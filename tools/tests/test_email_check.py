"""Tests for tools/email_check.py and its GET /email route (issue #338). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_email_check.py' -v

Fixtures (fixtures/email-check/, recorded in provenance.json): three live
keyless capture sets made by H8 with the tool's own fetch on issue #338,
three queries each (MX and TXT on the domain, TXT on _dmarc.<domain>),
each response as its header block and its body, verbatim, with SHA-256
hashes: gmail.com (full records), example.com (null MX, SPF, DMARC) and
nonexistent.invalid (NXDOMAIN on all three). Variants built here from
those responses say DERIVED where they are built. Every test runs with
urlopen replaced by a function that fails the test, except the fetch
tests, which replace it with a recorder.
"""

import hashlib
import io
import json
import re
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import email_check as e  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "email-check"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
CASES = {"someone@gmail.com": "gmail", "someone@example.com": "example",
         "someone@nonexistent.invalid": "nxdomain"}
KEYS = ["mx", "spf", "dmarc"]


def captured(slug, key, module=e):
    name = "%s-%s" % (slug, key)
    block = (FIX / ("%s.headers" % name)).read_text(encoding="utf-8").split("\n")
    status_line, headers = block[0], [tuple(line.split(": ", 1)) for line in block[1:] if line]
    status = int(re.findall(r" (\d{3}) ", status_line + " ")[0])
    url = PROV["%s.body" % name]["url"]
    return module.Capture(url, url, "2026-10-24T12:50:00Z", status, status_line, headers,
                          (FIX / ("%s.body" % name)).read_text(encoding="utf-8"))


def replay(module=e):
    def fetcher(url):
        for address, slug in CASES.items():
            _local, domain = module.check_address(address)
            for (_label, qname, rr), key in zip(module.queries(domain), KEYS):
                if url == module.doh_url(qname, rr):
                    return captured(slug, key, module)
        raise AssertionError("unexpected url %s" % url)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("email_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = e.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for slug in CASES.values():
            for key in KEYS:
                for ext in ("headers", "body"):
                    fname = "%s-%s.%s" % (slug, key, ext)
                    data = (FIX / fname).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(), PROV[fname]["sha256"])


class ReportTests(unittest.TestCase):
    def test_gmail_report(self):
        code, out, _ = run(["someone@gmail.com"])
        self.assertEqual(code, 0)
        self.assertIn("Well formed: yes", out)
        self.assertIn("- MX: 5 record(s) as shown:", out)
        self.assertIn("5 gmail-smtp-in.l.google.com.", out)
        self.assertIn("- SPF record as shown:", out)
        self.assertIn("v=spf1 redirect=_spf.google.com", out)
        self.assertIn("- DMARC record as shown:", out)
        self.assertIn("v=DMARC1; p=none", out)
        self.assertEqual(out.count("## Source: "), 3)

    def test_example_report_reads_the_null_mx(self):
        # The example domain capture set: its single MX answer is the null MX.
        code, out, _ = run(["someone@example.com"])
        self.assertEqual(code, 0)
        self.assertIn("a null MX (RFC 7505)", out)
        self.assertIn("v=spf1 -all", out)
        self.assertIn("v=DMARC1;p=reject", out)

    def test_nxdomain_report_is_a_report_not_a_failure(self):
        code, out, _ = run(["someone@nonexistent.invalid"])
        self.assertEqual(code, 0)
        self.assertIn("does not exist (the resolver answered NXDOMAIN)", out)
        self.assertIn("the name does not exist (NXDOMAIN)", out)

    def test_malformed_addresses_are_refused_before_any_fetch(self):
        for bad in ("no-at-sign", "two@@signs.com", ".dot@gmail.com", "dot.@gmail.com",
                    "a@gmail", "a@-bad-.com", "a b@gmail.com"):
            code, out, err = run([bad], fetcher=lambda url: (_ for _ in ()).throw(AssertionError("fetched")))
            self.assertEqual(code, 2, bad)
            self.assertEqual(out, "")

    def test_failed_query_is_unknown_not_a_report(self):
        def broken(url):
            if "type=MX" in url:
                raise e.FetchError("request failed or timed out; no report")
            return replay()(url)
        code, out, err = run(["someone@gmail.com"], fetcher=broken)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")

    def test_txt_chunks_are_joined_before_selection(self):
        self.assertEqual(e.txt_text('"v=spf1 " "include:x -all"'), "v=spf1 include:x -all")
        self.assertEqual(e.txt_text("plain"), "plain")


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.email_check, its own module object.
        with mock.patch.object(endpoints.ec, "fetch", replay(module=endpoints.ec)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/email", qs, None)

    def test_route_serves_the_report_and_rejects_bad_addresses(self):
        status, _, body = self.get("address=someone%40gmail.com")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("# Email check: someone@gmail.com", text)
        self.assertTrue(self.get("address=nope")[0].startswith("400"))
        self.assertTrue(self.get("")[0].startswith("400"))


if __name__ == "__main__":
    unittest.main()
