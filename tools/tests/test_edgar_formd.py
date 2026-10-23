"""Tests for tools/edgar_formd.py. No network unless EDGAR_LIVE=1.

Every fixture under tests/fixtures/edgar/ is a complete raw HTTP response
transcript captured by the tool's own fetch() on 2026-10-23, saved
unmodified; provenance.json records each URL, UTC retrieval time, status
line and SHA-256 digest. The 403 fixture is a deliberate capture of
EDGAR's answer to a User-Agent whose contact carried a URL, kept as the
real fail-closed case. No response here was written by hand; the few
tests that corrupt a capture say so where they do it.
"""

from contextlib import redirect_stderr, redirect_stdout
import email.message
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from tools import edgar_formd as ef

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "edgar"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text())
CONTACT = "Test Operator operator@example.com"


def captured(name):
    meta = PROVENANCE[name]
    transcript = (FIXTURES / name).read_bytes().decode("utf-8")
    body = transcript.partition("\n\n")[2]
    return ef.Capture(meta["url"], meta["retrieved_utc"], transcript, body)


class FakeFetcher:
    """Serves the recorded capture for a URL; any other URL is a failure."""

    def __init__(self, *names):
        self.by_url = {PROVENANCE[n]["url"]: captured(n) for n in names}
        self.calls = []

    def __call__(self, url, contact):
        self.calls.append((url, contact))
        if url not in self.by_url:
            raise ef.FetchError("no recorded capture for %s" % url)
        return self.by_url[url]


class ProvenanceTests(unittest.TestCase):
    def test_every_fixture_matches_its_recorded_hash_and_status(self):
        for name, meta in PROVENANCE.items():
            with self.subTest(name=name):
                data = (FIXTURES / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), meta["sha256"])
                self.assertEqual(len(data), meta["bytes"])
                self.assertTrue(data.decode("utf-8").startswith(meta["status_line"] + "\n"))
                host = urlsplit(meta["url"]).netloc
                self.assertIn(host, ("data.sec.gov", "www.sec.gov"))
                self.assertRegex(meta["retrieved_utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")


class FairAccessTests(unittest.TestCase):
    def test_contact_is_required_and_plain(self):
        self.assertEqual(ef.contact_from(CONTACT, env={}), CONTACT)
        self.assertEqual(ef.contact_from(None, env={ef.CONTACT_ENV: " " + CONTACT + " "}), CONTACT)
        for bad in ["", "   ", "no address here", "@", "x@", "@x",
                    "Name a@b.c (github.com/x/y)", "https://x a@b.c", "a@b.c <tag>"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ef.contact_from(bad, env={})
        with self.assertRaises(ValueError):
            ef.contact_from(None, env={})

    def test_user_agent_names_tool_and_contact(self):
        self.assertEqual(ef.user_agent(CONTACT), "tiny-ledger edgar_formd.py " + CONTACT)

    def test_fetch_sends_declared_user_agent_and_identity_encoding(self):
        seen = {}

        class FakeResponse:
            status, reason, version = 200, "OK", 11
            headers = email.message.Message()
            headers["Content-Type"] = "application/json"

            def read(self):
                return b'{"ok": true}'

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake_urlopen(request, timeout=None):
            seen["ua"] = request.get_header("User-agent")
            seen["enc"] = request.get_header("Accept-encoding")
            seen["url"] = request.full_url
            return FakeResponse()

        with patch.object(ef.urllib.request, "urlopen", side_effect=fake_urlopen), \
                patch.object(ef, "pace"):
            cap = ef.fetch("https://data.sec.gov/submissions/CIK0000000001.json", CONTACT)
        self.assertEqual(seen["ua"], ef.user_agent(CONTACT))
        self.assertEqual(seen["enc"], "identity")
        self.assertEqual(cap.transcript, "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"ok\": true}")
        self.assertEqual(cap.body, '{"ok": true}')

    def test_pace_keeps_requests_at_least_the_interval_apart(self):
        clock = [100.0]
        slept = []

        def now():
            return clock[0]

        def sleep(seconds):
            slept.append(seconds)
            clock[0] += seconds

        ef._last_request_at[0] = 0.0
        ef.pace(now=now, sleep=sleep)          # first request, no wait
        ef.pace(now=now, sleep=sleep)          # immediately after: must wait the full interval
        clock[0] += 10
        ef.pace(now=now, sleep=sleep)          # long after: no wait
        self.assertEqual(len(slept), 1)
        self.assertAlmostEqual(slept[0], ef.MIN_INTERVAL_SECONDS, places=6)
        self.assertGreaterEqual(ef.MIN_INTERVAL_SECONDS, 0.1)


class UrlTests(unittest.TestCase):
    def test_urls_match_the_recorded_captures(self):
        self.assertEqual(ef.submissions_url("2156237"), PROVENANCE["submissions-2156237.http"]["url"])
        self.assertEqual(ef.submissions_url("0000320193"), PROVENANCE["submissions-320193.http"]["url"])
        self.assertEqual(ef.company_search_url("8VC DSS"), PROVENANCE["lookup-many.http"]["url"])
        self.assertEqual(ef.primary_doc_url("2156237", "0002156237-26-000001", "xslFormDX01/primary_doc.xml"),
                         PROVENANCE["formd-0002156237-26-000001.http"]["url"])
        self.assertEqual(ef.filing_index_url("2156237", "0002156237-26-000001"),
                         "https://www.sec.gov/Archives/edgar/data/2156237/000215623726000001/0002156237-26-000001-index.htm")
        self.assertEqual(parse_qs(urlsplit(ef.company_search_url("a b")).query)["type"], ["D"])

    def test_identifier_validation(self):
        self.assertEqual(ef.cik10("320193"), "0000320193")
        for bad in ["", "abc", "0", "12345678901"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ef.cik10(bad)
        with self.assertRaises(ValueError):
            ef.accession_nodash("0002156237-26-1")
        with self.assertRaises(ValueError):
            ef.company_search_url("  ")
        self.assertIsNone(ef.primary_doc_url("1", "0000000001-26-000001", ""))


class ParsingTests(unittest.TestCase):
    def test_company_search_three_shapes(self):
        kind, rows = ef.parse_company_search(captured("lookup-many.http").body)
        self.assertEqual(kind, "many")
        self.assertIn(("0002156237", "8VC DSS III, L.P.", "TX"), rows)
        self.assertEqual(len(rows), 3)
        kind, one = ef.parse_company_search(captured("lookup-one.http").body)
        self.assertEqual((kind, one), ("one", ("0002156237", "8VC DSS III, L.P.")))
        self.assertEqual(ef.parse_company_search(captured("lookup-none.http").body), ("none", []))
        with self.assertRaises(ef.FetchError):
            ef.parse_company_search("<html><body>something else</body></html>")

    def test_submissions_index(self):
        name, cik, filings, older = ef.parse_submissions(captured("submissions-2156237.http").body)
        self.assertEqual((name, cik, older), ("8VC DSS III, L.P.", "0002156237", []))
        self.assertEqual([f["form"] for f in filings], ["D"])
        self.assertEqual(filings[0]["accessionNumber"], "0002156237-26-000001")
        self.assertEqual(filings[0]["primaryDocument"], "xslFormDX01/primary_doc.xml")

        name, cik, filings, older = ef.parse_submissions(captured("submissions-320193.http").body)
        self.assertEqual((name, cik), ("Apple Inc.", "0000320193"))
        self.assertEqual(len(filings), 1002)
        self.assertEqual(ef.form_d_filings(filings), [])
        self.assertEqual(older, ["CIK0000320193-submissions-001.json"])

        name, cik, filings, older = ef.parse_submissions(captured("submissions-1801756.http").body)
        formd = ef.form_d_filings(filings)
        self.assertEqual([f["form"] for f in formd], ["D/A", "D/A", "D/A", "D/A", "D"])
        self.assertEqual(formd[0]["accessionNumber"], "0000929638-26-003990")

        for bad in ["not json", "[]", '{"filings": {}}', '{"filings": {"recent": {"form": ["D"], "filingDate": []}}}']:
            with self.subTest(bad=bad), self.assertRaises(ef.FetchError):
                ef.parse_submissions(bad)

    def test_form_d_values_as_shown(self):
        parsed = ef.parse_form_d(captured("formd-0002156237-26-000001.http").body)
        self.assertEqual(parsed["issuerName"], ["8VC DSS III, L.P."])
        self.assertEqual(parsed["issuerCik"], ["0002156237"])
        self.assertEqual(parsed["submissionType"], ["D"])
        self.assertEqual(parsed["isAmendment"], ["false"])
        self.assertEqual(parsed["dateOfFirstSale"], ["yetToOccur: true"])
        self.assertEqual(parsed["totalOfferingAmount"], ["400000000"])
        self.assertEqual(parsed["totalAmountSold"], ["0"])
        self.assertEqual(parsed["totalRemaining"], ["400000000"])
        self.assertEqual(parsed["investorsAlreadyInvested"], ["0"])
        self.assertEqual(parsed["industryGroup"], ["Pooled Investment Fund"])
        self.assertEqual(parsed["exemptions"], ["06b", "3C", "3C.7"])

        amended = ef.parse_form_d(captured("formd-0000929638-26-003990.http").body)
        self.assertEqual(amended["submissionType"], ["D/A"])
        self.assertEqual(amended["isAmendment"], ["true"])
        self.assertEqual(amended["dateOfFirstSale"], ["2020-01-22"])
        self.assertEqual(amended["totalOfferingAmount"], ["Indefinite"])
        self.assertEqual(amended["totalAmountSold"], ["243290624"])
        self.assertEqual(amended["amountsClarification"],
                         ["The Total Amount Sold includes investments by the Feeder Fund"])

        for bad in ["<not xml", "<other/>"]:
            with self.subTest(bad=bad), self.assertRaises(ef.FetchError):
                ef.parse_form_d(bad)


class RunTests(unittest.TestCase):
    def test_single_filing_report(self):
        fetcher = FakeFetcher("submissions-2156237.http", "formd-0002156237-26-000001.http")
        lines = ef.run(CONTACT, cik="2156237", fetcher=fetcher)
        text = "\n".join(lines)
        self.assertEqual(lines[0], "## SEC EDGAR Form D filings: 8VC DSS III, L.P. (CIK 0002156237)")
        self.assertIn("EDGAR lists 1 Form D filings (form D or D/A) among the 1 filings", text)
        self.assertIn("#### Form D 0002156237-26-000001", text)
        self.assertIn('- Issuer name as shown: "8VC DSS III, L.P."', text)
        self.assertIn('- Filing date as shown (submissions index): "2026-10-22"', text)
        self.assertIn('- Total offering amount as shown: "400000000"', text)
        self.assertIn('- Total amount sold as shown: "0"', text)
        self.assertIn('- Date of first sale as shown: "yetToOccur: true"', text)
        self.assertIn("- Filing index page: https://www.sec.gov/Archives/edgar/data/2156237/000215623726000001/0002156237-26-000001-index.htm", text)
        self.assertIn("- Listed as: Form D filing", text)
        # Every transcript sits directly beneath its own source link, verbatim.
        for name in ("submissions-2156237.http", "formd-0002156237-26-000001.http"):
            cap = captured(name)
            self.assertIn("\nSource: <%s>\n```\n%s\n```" % (cap.url, cap.transcript), text)
        self.assertEqual([u for u, _ in fetcher.calls], [captured("submissions-2156237.http").url,
                                                         captured("formd-0002156237-26-000001.http").url])
        self.assertTrue(all(c == CONTACT for _, c in fetcher.calls))
        self.assertNotIn(ef.NOT_PRESENT, text)

    def test_empty_result_is_proven_and_older_index_is_named(self):
        fetcher = FakeFetcher("submissions-320193.http")
        lines = ef.run(CONTACT, cik="320193", fetcher=fetcher)
        text = "\n".join(lines)
        self.assertIn("EDGAR lists 0 Form D filings (form D or D/A) among the 1002 filings", text)
        self.assertIn('older index file(s) outside the recent window, not queried by this tool: "CIK0000320193-submissions-001.json"', text)
        self.assertIn("No Form D filing is listed in the recent window; the complete raw response is beneath the source link.", text)
        cap = captured("submissions-320193.http")
        self.assertIn("\nSource: <%s>\n```\n%s\n```" % (cap.url, cap.transcript), text)
        self.assertNotIn("#### Form D", text)
        self.assertEqual(len(fetcher.calls), 1)

    def test_issuer_lookup_many_stops_for_the_operator(self):
        fetcher = FakeFetcher("lookup-many.http")
        lines = ef.run(CONTACT, issuer="8VC DSS", fetcher=fetcher)
        text = "\n".join(lines)
        self.assertIn("returned 3 matching companies. The tool does not choose", text)
        self.assertIn('- Candidate as shown: CIK "0002156237", "8VC DSS III, L.P.", state "TX"', text)
        self.assertIn(captured("lookup-many.http").transcript, text)
        self.assertEqual(len(fetcher.calls), 1)

    def test_issuer_lookup_one_proceeds_to_filings(self):
        fetcher = FakeFetcher("lookup-one.http", "submissions-2156237.http", "formd-0002156237-26-000001.http")
        lines = ef.run(CONTACT, issuer="8VC DSS III", fetcher=fetcher)
        text = "\n".join(lines)
        self.assertIn('matched exactly one company: "8VC DSS III, L.P.", CIK "0002156237"', text)
        self.assertIn("#### Form D 0002156237-26-000001", text)
        self.assertEqual(len(fetcher.calls), 3)

    def test_issuer_lookup_none_is_proven(self):
        fetcher = FakeFetcher("lookup-none.http")
        text = "\n".join(ef.run(CONTACT, issuer="zzqx nonexistent issuer name", fetcher=fetcher))
        self.assertIn("returned no matching companies for this name", text)
        self.assertIn(captured("lookup-none.http").transcript, text)
        self.assertEqual(len(fetcher.calls), 1)

    def test_exclusions_and_max_filings(self):
        fetcher = FakeFetcher("submissions-1801756.http", "formd-0000929638-26-003990.http",
                              "formd-0001801756-23-000001.http")
        lines = ef.run(CONTACT, cik="1801756", max_filings=2,
                       exclusions={"0001801756-23-000001": "older amendment superseded by the newer one"},
                       fetcher=fetcher)
        text = "\n".join(lines)
        self.assertIn("EDGAR lists 5 Form D filings", text)
        self.assertIn("#### Form D 0000929638-26-003990", text)
        self.assertIn('- Total offering amount as shown: "Indefinite"', text)
        self.assertIn("- Listed as: Checked and excluded: older amendment superseded by the newer one", text)
        self.assertIn("3 further Form D filing(s) listed above were not fetched because --max-filings is 2.", text)
        self.assertEqual(len(fetcher.calls), 3)
        with self.assertRaises(ValueError):
            ef.run(CONTACT, cik="1801756", max_filings=0, exclusions={"0000000000-00-000000": "x"},
                   fetcher=FakeFetcher("submissions-1801756.http"))
        lines = ef.run(CONTACT, cik="1801756", max_filings=0, fetcher=FakeFetcher("submissions-1801756.http"))
        self.assertIn("5 further Form D filing(s) listed above were not fetched", "\n".join(lines))

    def test_fail_closed(self):
        # The real 403 EDGAR returned to an undeclared user agent, as the submissions answer.
        fetcher = FakeFetcher("undeclared-403.http")
        fetcher.by_url[ef.submissions_url("2156237")] = captured("undeclared-403.http")
        with self.assertRaises(ef.FetchError) as ctx:
            ef.run(CONTACT, cik="2156237", fetcher=fetcher)
        self.assertIn("403 Forbidden", str(ctx.exception))
        # A corrupted capture, deliberately: the XML truncated so it no longer parses.
        good = captured("formd-0002156237-26-000001.http")
        broken = ef.Capture(good.url, good.retrieved, good.transcript[:-200], good.body[:-200])
        fetcher = FakeFetcher("submissions-2156237.http")
        fetcher.by_url[good.url] = broken
        with self.assertRaises(ef.FetchError):
            ef.run(CONTACT, cik="2156237", fetcher=fetcher)


class CliTests(unittest.TestCase):
    def test_contact_and_exactly_one_target_are_required(self):
        for argv in (["--cik", "2156237"], ["--contact", CONTACT], ["--contact", CONTACT, "--cik", "1", "--issuer", "x"],
                     ["--contact", "no address", "--cik", "1"], ["--contact", CONTACT, "--cik", "abc"]):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()), \
                    patch.dict(os.environ, {}, clear=False), self.assertRaises(SystemExit) as exit_info:
                os.environ.pop(ef.CONTACT_ENV, None)
                ef.main(argv)
            self.assertEqual(exit_info.exception.code, 2)

    def test_cli_prints_report_and_fails_closed(self):
        fetcher = FakeFetcher("submissions-2156237.http", "formd-0002156237-26-000001.http")
        out, err = io.StringIO(), io.StringIO()
        with patch.object(ef, "fetch", side_effect=fetcher), redirect_stdout(out), redirect_stderr(err), \
                patch.dict(os.environ, {ef.CONTACT_ENV: CONTACT}):
            status = ef.main(["--cik", "2156237"])
        self.assertEqual(status, 0)
        self.assertIn("#### Form D 0002156237-26-000001", out.getvalue())
        self.assertEqual(err.getvalue(), "")

        failing = FakeFetcher("undeclared-403.http")
        failing.by_url[ef.submissions_url("2156237")] = captured("undeclared-403.http")
        out, err = io.StringIO(), io.StringIO()
        with patch.object(ef, "fetch", side_effect=failing), redirect_stdout(out), redirect_stderr(err):
            status = ef.main(["--contact", CONTACT, "--cik", "2156237"])
        self.assertEqual(status, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("No report emitted", err.getvalue())


@unittest.skipUnless(os.environ.get("EDGAR_LIVE") == "1" and os.environ.get(ef.CONTACT_ENV),
                     "set EDGAR_LIVE=1 and EDGAR_CONTACT for a live EDGAR check")
class LiveTests(unittest.TestCase):
    def test_cli_against_edgar(self):
        result = subprocess.run([sys.executable, "tools/edgar_formd.py", "--cik", "2156237", "--max-filings", "1"],
                                cwd=ROOT, capture_output=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        output = result.stdout.decode()
        self.assertIn("### Submissions index", output)
        self.assertIn("HTTP/1.1 200 OK", output)
        self.assertIn("#### Form D ", output)
        self.assertIn("- Total offering amount", output)


if __name__ == "__main__":
    unittest.main()
