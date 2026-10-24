"""Tests for tools/domain_trust_check.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_domain_trust_check.py' -v

The fixtures in fixtures/domain-trust/ are real captures: the coordinator
retrieved every response live on 2026-10-24 and posted it verbatim on
issue #159 (Option B); URLs, retrieval times and hashes are in
fixtures/domain-trust/provenance.json. Three inputs below are not
recordings and are labelled where they appear: a TXT data string split
into two quoted strings (no capture holds one), a transport error raised
by a test stub, and two malformed DNS answers built to prove the tool
fails closed.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import domain_trust_check as dt  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "domain-trust"
PROVENANCE = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))


def captured(name):
    meta = PROVENANCE[name]
    with open(FIX / name, encoding="utf-8", newline="") as fh:
        transcript = fh.read()
    head, _, body = transcript.partition("\n\n")
    lines = head.split("\n")
    return dt.Capture(meta["url"], meta["retrieved_utc"], lines[0], lines[1:], body)


def by_url(*names):
    table = {PROVENANCE[n]["url"]: captured(n) for n in names}

    def fetch(url):
        if url not in table:
            raise AssertionError("no recorded capture for %s" % url)
        return table[url]
    return fetch


EXAMPLE_DNS = ("doh-example.com-A.http", "doh-example.com-MX.http", "doh-example.com-TXT.http",  # example domain fixture
               "doh-_dmarc.example.com-TXT.http")  # example domain fixture


class Captures(unittest.TestCase):
    def test_every_fixture_matches_its_recorded_hashes_and_body_size(self):
        names = [n for n in PROVENANCE if not n.startswith("_")]
        self.assertEqual(len(names), 11)
        for name in names:
            meta = PROVENANCE[name]
            raw = (FIX / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"], name)
            body = raw.decode("utf-8").partition("\n\n")[2].encode("utf-8")
            self.assertEqual(hashlib.sha256(body).hexdigest(), meta["body_sha256_as_posted"], name)
            self.assertEqual(len(body), meta["body_bytes"], name)

    def test_request_urls_reproduce_the_captured_requests(self):
        self.assertEqual([dt.doh_url(n, t) for _, n, t in dt.queries("example.com")],  # example domain fixture
                         [PROVENANCE[n]["url"] for n in EXAMPLE_DNS])
        self.assertEqual(dt.doh_url("does-not-exist.invalid", "A"), PROVENANCE["doh-does-not-exist.invalid-A.http"]["url"])
        self.assertEqual(dt.doh_url("_dmarc.neverssl.com", "TXT"), PROVENANCE["doh-_dmarc.neverssl.com-TXT.http"]["url"])


class ExampleComReport(unittest.TestCase):
    def setUp(self):
        self.lines = dt.run("example.com", by_url(*EXAMPLE_DNS), by_url("site-example.com.http"))  # example domain fixture
        self.text = "\n".join(self.lines)

    def test_a_and_mx_records_as_shown(self):
        self.assertIn("- A record as shown: `104.20.23.154` (TTL 39).", self.lines)
        self.assertIn("- A record as shown: `172.66.147.243` (TTL 39).", self.lines)
        self.assertIn("- MX record as shown: `0 .` (TTL 285).", self.lines)

    def test_spf_record_and_ending_policy(self):
        self.assertIn("- TXT records in the answer: 2, of which 1 begin v=spf1.", self.lines)
        self.assertIn('- SPF record as shown (data `"v=spf1 -all"`): `v=spf1 -all`', self.lines)
        self.assertIn("- SPF ending policy: `-all`, the final all mechanism of the record (source S3).", self.lines)

    def test_dmarc_record_and_policy(self):
        self.assertIn("- DMARC policy (p= tag as shown): `reject` (source S4).", self.lines)

    def test_https_answer(self):
        self.assertIn("- Hop 1: GET https://example.com/ answered 200 OK (retrieved 2026-10-24T01:51:49Z; source S5).", self.lines)  # example domain fixture
        self.assertIn("- HTTPS: the final hop answered 200 OK at https://example.com/.", self.lines)  # example domain fixture

    def test_every_source_prints_its_complete_transcript_under_its_url(self):
        for i, name in enumerate(EXAMPLE_DNS + ("site-example.com.http",)):  # example domain fixture
            cap = captured(name)
            start = self.lines.index("- Request URL: %s" % cap.url)
            self.assertEqual(self.lines[start - 1][:len("### Source. S%d." % (i + 1))], "### Source. S%d." % (i + 1))
            self.assertEqual(self.lines[start + 1], "- Retrieved (UTC): %s" % cap.retrieved)
            fence = self.lines[start + 3]
            end = self.lines.index(fence, start + 4)
            self.assertEqual("\n".join(self.lines[start + 4:end]), cap.transcript)


class SecondDomains(unittest.TestCase):
    def section(self, name, rr_name, label="TXT records (SPF)"):
        cap = captured(name)
        lines, status, found = dt.dns_section(label, rr_name, "TXT", 3, cap)
        return dt.spf_lines(rr_name, status, found, 3) if label.startswith("TXT") else dt.dmarc_lines(rr_name, status, found, 4)

    def test_iana_org_spf_ends_with_a_redirect_not_an_all(self):
        lines = self.section("doh-iana.org-TXT.http", "iana.org")
        self.assertIn("- TXT records in the answer: 12, of which 1 begin v=spf1.", lines)
        self.assertIn("- SPF ending policy: the record has no all mechanism and ends with the modifier "
                      "`redirect=icann.org`, so its policy is the redirected record's, which this tool does not "
                      "fetch (source S3).", lines)

    def test_iana_org_dmarc_policy_none_with_spaces_after_semicolons(self):
        lines = self.section("doh-_dmarc.iana.org-TXT.http", "_dmarc.iana.org", label="DMARC record")
        self.assertIn("- DMARC policy (p= tag as shown): `none` (source S4).", lines)

    def test_wikipedia_org_spf_ends_softfail(self):
        lines = self.section("doh-wikipedia.org-TXT.http", "wikipedia.org")
        self.assertIn("- TXT records in the answer: 3, of which 1 begin v=spf1.", lines)
        self.assertIn("- SPF ending policy: `~all`, the final all mechanism of the record (source S3).", lines)


class EmptyResults(unittest.TestCase):
    def test_name_that_does_not_exist_is_an_empty_result_with_its_status(self):
        cap = captured("doh-does-not-exist.invalid-A.http")
        lines, status, found = dt.dns_section("A records", "does-not-exist.invalid", "A", 1, cap)
        self.assertEqual((status, found), (3, []))
        self.assertIn("DNS Status as shown: 3.", lines[2])
        self.assertTrue(lines[-1].startswith("The answer holds no A record for does-not-exist.invalid: the DNS "
                                             "Status field is 3, not 0"), lines[-1])

    def test_domain_without_dmarc_is_an_empty_result_not_a_failure(self):
        cap = captured("doh-_dmarc.neverssl.com-TXT.http")
        lines, status, found = dt.dns_section("DMARC record", "_dmarc.neverssl.com", "TXT", 4, cap)
        out = dt.dmarc_lines("_dmarc.neverssl.com", status, found, 4)
        self.assertEqual((status, found), (0, []))
        self.assertIn("The answer holds no TXT record for _dmarc.neverssl.com (DNS Status 0 with no TXT record "
                      "in the Answer). The complete raw response is in source S4.", out)
        self.assertIn("- DMARC: no TXT record for _dmarc.neverssl.com begins v=DMARC1 in this answer, so no DMARC "
                      "policy is shown (source S4).", out)


class HttpsLeg(unittest.TestCase):
    def test_redirect_reports_status_and_location_then_follows_it(self):
        google = captured("site-google.com.http")
        calls = []

        def fetch(url):
            calls.append(url)
            if url == "https://google.com/":
                return google
            # Test stub, not a recording: the second hop is not in the captures.
            raise urllib.error.URLError("test stub: no capture for this hop")
        hops = dt.walk_site("google.com", fetch)
        self.assertEqual(calls, ["https://google.com/", "https://www.google.com/"])
        lines = dt.https_lines(hops, 5)
        self.assertEqual(lines[0], "- Hop 1: GET https://google.com/ answered 301 Moved Permanently (retrieved "
                                   "2026-10-24T01:51:50Z; source S5), Location header as shown: `https://www.google.com/`.")
        self.assertTrue(lines[1].startswith("- Hop 2: GET https://www.google.com/ did not return an HTTP response"))
        self.assertIn("is not determinable from this run", lines[-1])

    def test_google_body_keeps_its_crlf_bytes(self):
        self.assertTrue(captured("site-google.com.http").body.endswith("</BODY></HTML>\r\n"))

    def test_hops_stop_at_the_limit(self):
        google = captured("site-google.com.http")
        # The same recorded 301 served for every hop, only to exercise the limit.
        hops = dt.walk_site("google.com", lambda url: google)
        self.assertEqual(len(hops), dt.MAX_HOPS)
        self.assertIn("still redirecting after %d hops" % dt.MAX_HOPS, dt.https_lines(hops, 5)[-1])


class Parsing(unittest.TestCase):
    def test_split_txt_strings_are_joined(self):
        # SYNTHETIC data string: two quoted strings, the shape a long TXT record takes; no capture holds one.
        self.assertEqual(dt.txt_text('"v=spf1 include:a.example " "~all"'), "v=spf1 include:a.example ~all")
        self.assertEqual(dt.txt_text('"say \\"hi\\""'), 'say "hi"')

    def test_ending_policy_rules(self):
        self.assertEqual(dt.spf_ending("v=spf1 -all"), ("all", "-all"))
        self.assertEqual(dt.spf_ending("v=spf1 include:_cidrs.wikimedia.org ~all"), ("all", "~all"))
        self.assertEqual(dt.spf_ending("v=spf1 redirect=icann.org"), ("redirect", "redirect=icann.org"))
        self.assertEqual(dt.spf_ending("v=spf1 mx"), ("none", None))

    def test_domain_input_rules(self):
        self.assertEqual(dt.check_domain(" Example.COM. "), "example.com")  # example domain fixture
        for bad in ("", "https://example.com/", "example", "a..example.com", "-bad.example.com", "x@example.com"):
            with self.assertRaises(ValueError, msg=bad):
                dt.check_domain(bad)


class FailClosed(unittest.TestCase):
    def test_non_200_and_non_json_answers_raise_and_print_nothing(self):
        good = captured("doh-example.com-A.http")  # example domain fixture
        # Built inputs, not recordings: the recorded answer with its status changed, and a body that is not JSON.
        bad_status = dt.Capture(good.url, good.retrieved, "HTTP/1.1 503 Service Unavailable", good.headers, good.body)
        bad_body = dt.Capture(good.url, good.retrieved, good.status_line, good.headers, "<html>not json</html>")
        for bad in (bad_status, bad_body):
            with self.assertRaises(dt.FetchError):
                dt.parse_doh(bad)
            out, err = io.StringIO(), io.StringIO()
            fetch = by_url(*EXAMPLE_DNS[1:])
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                original = dt.fetch_doh
                dt.fetch_doh = lambda url, bad=bad, fetch=fetch: bad if url == good.url else fetch(url)
                try:
                    code = dt.main(["example.com"])  # the example domain of the fixtures
                finally:
                    dt.fetch_doh = original
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertIn("fetch failed, nothing printed", err.getvalue())

    def test_cli_prints_the_report(self):
        # The reserved example domain, served from its recorded fixtures.
        out = io.StringIO()
        original = (dt.fetch_doh, dt.fetch_site)
        dt.fetch_doh, dt.fetch_site = by_url(*EXAMPLE_DNS), by_url("site-example.com.http")
        try:
            with contextlib.redirect_stdout(out):
                code = dt.main(["example.com"])  # the example domain of the fixtures
        finally:
            dt.fetch_doh, dt.fetch_site = original
        self.assertEqual(code, 0)
        # Heading for the example domain, as in the fixtures.
        self.assertTrue(out.getvalue().startswith("## Domain: example.com\n"))


if __name__ == "__main__":
    unittest.main()
