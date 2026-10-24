"""Tests for tools/bank_check.py and its GET /bank route (issue #320). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_bank_check.py' -v

Fixtures (fixtures/bank-check/, recorded in provenance.json): three live
keyless captures made by H8 with the tool's own fetch on issue #320, each
response as its header block and its body, verbatim, with SHA-256 hashes:
a two match page (JPMorgan), a 29 match page (Wells Fargo) and a page
whose total is 0 (Zebra). Variants built here from those responses say
DERIVED where they are built. Every test runs with urlopen replaced by a
function that fails the test, except the fetch tests, which replace it
with a recorder.
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
import bank_check as b  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "bank-check"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
CASES = {"JPMorgan Chase Bank": "jpmorgan-chase", "Wells Fargo Bank": "wells-fargo",
         "Zebra National Bank": "zebra-none"}


def captured(name, module=b):
    block = (FIX / ("%s.headers" % name)).read_text(encoding="utf-8").split("\n")
    status_line, headers = block[0], [tuple(line.split(": ", 1)) for line in block[1:] if line]
    status = int(re.findall(r" (\d{3}) ", status_line + " ")[0])
    url = PROV["%s.body" % name]["url"]
    final = "https://api.fdic.gov/banks/" + url.split("banks.data.fdic.gov/api/", 1)[1]
    return module.Capture(url, final, "2026-10-24T12:20:00Z", status, status_line, headers,
                          (FIX / ("%s.body" % name)).read_text(encoding="utf-8"))


def replay(module=b):
    def fetcher(url):
        for typed, name in CASES.items():
            if url == module.search_url(typed):
                return captured(name, module)
        raise AssertionError("unexpected url %s" % url)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("bank_check tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = b.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for slug in CASES.values():
            for ext in ("headers", "body"):
                data = (FIX / ("%s.%s" % (slug, ext))).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), PROV["%s.%s" % (slug, ext)]["sha256"])


class ReportTests(unittest.TestCase):
    def test_jpmorgan_report(self):
        code, out, _ = run(["JPMorgan Chase Bank"])
        self.assertEqual(code, 0)
        self.assertIn("## JPMorgan Chase Bank, National Association", out)
        self.assertIn("## JPMorgan Chase Bank, Dearborn", out)
        self.assertIn("- FDIC certificate number (CERT) as shown: 628", out)
        self.assertIn("- City (CITY) as shown: Columbus", out)
        self.assertIn("- State (STNAME) as shown: Ohio", out)
        self.assertIn("- Active status (ACTIVE) as shown: 1 (active)", out)
        self.assertIn("The prefix page holds 3 institution(s); 2 match", out)
        self.assertIn("Source: <https://banks.data.fdic.gov/api/Institutions?", out)
        self.assertIn("institutions_", out)  # the index snapshot name, inside the transcript

    def test_wells_fargo_report_counts_every_prefix_match(self):
        code, out, _ = run(["Wells Fargo Bank"])
        self.assertEqual(code, 0)
        self.assertIn("The prefix page holds 38 institution(s); 29 match", out)
        self.assertEqual(out.count("\n## "), 29)

    def test_no_match_is_a_report_proven_by_the_raw_response(self):
        code, out, _ = run(["Zebra National Bank"])
        self.assertEqual(code, 0)
        self.assertIn("No institution in this FDIC index snapshot has a name beginning with", out)
        self.assertIn('"total":0', out.replace(" ", ""))  # the empty page itself, in the transcript

    def test_typed_name_must_be_the_listed_start(self):
        # DERIVED case set: the JPMorgan page keyed on "Chase" cannot exist; the tool
        # keys the request on the typed first word, so "Chase Bank" asks a Chase page.
        # Offline, the replay refuses that URL, which is the point: no cross page claims.
        with self.assertRaises(AssertionError):
            run(["Chase Bank"])

    def test_normalise_and_prefix_rule(self):
        self.assertEqual(b.normalise("JPMorgan Chase Bank, National Association"),
                         "jpmorgan chase bank national association")
        rows = [{"NAME": "Bank of America, National Association"},
                {"NAME": "Bank of Ann Arbor"},
                {"NAME": "BankUnited, National Association"}]
        kept = b.matches("Bank of", rows)
        self.assertEqual([r["NAME"] for r in kept],
                         ["Bank of America, National Association", "Bank of Ann Arbor"])

    def test_page_shorter_than_total_is_unknown_not_a_report(self):
        # DERIVED from the zebra capture: claim a total the page does not carry.
        cap = captured("zebra-none")
        body = cap.body.replace('"total":0', '"total":7', 1).replace('"count":0', '"count":7', 1)
        self.assertNotEqual(body, cap.body)
        cap2 = b.Capture(cap.url, cap.final_url, cap.retrieved, 200, cap.status_line, cap.headers, body)
        out, err = io.StringIO(), io.StringIO()
        code = b.main(["Zebra National Bank"], fetcher=lambda url: cap2, stdout=out, stderr=err)
        self.assertEqual(code, 2)
        self.assertIn("not the whole candidate set", err.getvalue())
        self.assertEqual(out.getvalue(), "")

    def test_malformed_body_is_unknown(self):
        cap = captured("zebra-none")
        cap2 = b.Capture(cap.url, cap.final_url, cap.retrieved, 200, cap.status_line, cap.headers,
                         '{"meta": {}}')
        out, err = io.StringIO(), io.StringIO()
        code = b.main(["Zebra National Bank"], fetcher=lambda url: cap2, stdout=out, stderr=err)
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")

    def test_short_and_filter_character_names_are_refused_before_any_fetch(self):
        for bad in ("Ab", "A Bank", "* Bank", "Ba: Bank"):
            code, out, err = run([bad], fetcher=lambda url: (_ for _ in ()).throw(AssertionError("fetched")))
            self.assertEqual(code, 2, bad)
            self.assertEqual(out, "")


class FetchTests(unittest.TestCase):
    def test_fetch_refuses_non_200_and_off_host_redirect(self):
        class Resp:
            status = 403
            code = 403
            reason = "Forbidden"
            version = 11
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def geturl(self):
                return "https://banks.data.fdic.gov/api/Institutions"

            def read(self):
                return b'{"error": {"code": "API_KEY_INVALID"}}'

        with mock.patch("urllib.request.urlopen", lambda req, timeout=0: Resp()):
            with self.assertRaises(b.FetchError):
                b.fetch(b.search_url("Wells Fargo Bank"))


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.bank_check, its own module object.
        with mock.patch.object(endpoints.bk, "fetch", replay(module=endpoints.bk)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/bank", qs, None)

    def test_route_serves_the_report_and_rejects_bad_names(self):
        status, _, body = self.get("name=JPMorgan+Chase+Bank")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("JPMorgan Chase Bank, National Association", text)
        self.assertTrue(self.get("name=Ab")[0].startswith("400"))
        self.assertTrue(self.get("")[0].startswith("400"))


if __name__ == "__main__":
    unittest.main()
