"""Tests for tools/propublica_nonprofits.py. Standard library only, no network
unless PROPUBLICA_LIVE=1.

Run:  python3 -m unittest discover -s tools/tests -p 'test_propublica_nonprofits.py' -v

Fixtures:

* fixtures/propublica/search-american-red-cross.json and
  fixtures/propublica/organization-530196605.json are REAL CAPTURES: the
  response bodies of two live GETs to the ProPublica Nonprofit Explorer API
  v2, taken by the coordinator and posted verbatim on issue #47 (H3's own
  environment could not reach the host). The request URLs, retrieval times,
  HTTP status and SHA-256 of each body are in fixtures/propublica/
  provenance.json, and the hashes are checked here. Only the bodies were
  captured: no status line or headers.
* When these tests serve the captures from a local HTTP server on
  127.0.0.1, the status line and headers in the transcript come from that
  local test server, not from ProPublica. The body is the capture, unchanged.
* DERIVED data is built in the test that uses it from a real capture with
  one stated change (an array reordered, a block removed), and is labelled
  DERIVED there. SYNTHETIC data (an empty search body, error bodies) is
  hand written and labelled SYNTHETIC where it appears. None of it is
  presented as a response anyone received.
"""

import contextlib
import hashlib
import http.server
import io
import json
import os
import re
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import propublica_nonprofits as pp  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "propublica"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
SEARCH = (FIXTURES / "search-american-red-cross.json").read_text(encoding="utf-8")
ORG = (FIXTURES / "organization-530196605.json").read_text(encoding="utf-8")
SEARCH_URL = PROVENANCE["search-american-red-cross.json"]["url"]
ORG_URL = PROVENANCE["organization-530196605.json"]["url"]


def capture(url, body):
    return pp.Capture(url, "2026-10-23T03:35:58Z", "HTTP/1.1 200 OK", 200, ["Content-Type: application/json"], body)


def fake_fetcher(bodies):
    def fetcher(url):
        if url not in bodies:
            raise AssertionError("unexpected fetch: %s" % url)
        return capture(url, bodies[url])
    return fetcher


REAL = {SEARCH_URL: SEARCH, ORG_URL: ORG}


def fences(text):
    return re.findall(r"^```\n(.*?)\n```$", text, re.S | re.M)


class Fixtures(unittest.TestCase):
    def test_hashes_match_provenance(self):
        for name, entry in PROVENANCE.items():
            with self.subTest(name=name):
                digest = hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
                self.assertEqual(digest, entry["sha256"])

    def test_urls_reproduce_the_captured_requests(self):
        self.assertEqual(pp.search_url("American Red Cross"), SEARCH_URL)
        self.assertEqual(pp.organization_url(pp.normalize_ein("53-0196605")), ORG_URL)


class Organization(unittest.TestCase):
    def setUp(self):
        self.out = pp.report(None, ["530196605"], {}, "EIN 530196605", fetcher=fake_fetcher(REAL))

    def test_identity_and_figures_from_the_real_capture(self):
        data = json.loads(ORG)
        latest = max(data["filings_with_data"], key=lambda f: f["tax_prd"])
        for key in ("name", "city", "state"):
            self.assertIn("(%s) as shown: `%s`" % (key, json.dumps(data["organization"][key])), self.out)
        self.assertIn("EIN (ein) as shown: `530196605`", self.out)
        for key in ("tax_prd", "totrevenue", "totfuncexpns", "totassetsend", "totliabend"):
            self.assertIn("(%s) as shown: `%s`" % (key, latest[key]), self.out)
        self.assertIn("Total revenue (totrevenue) as shown: `3217077611`", self.out)
        self.assertIn("highest tax_prd (202306 of 13 entries)", self.out)

    def test_every_excerpt_is_cut_verbatim_from_the_body(self):
        blocks = fences(self.out)
        self.assertGreater(len(blocks), 10)
        for block in blocks[:-1]:
            self.assertIn(block, ORG, block[:80])
        self.assertTrue(blocks[-1].endswith("\n\n" + ORG), "full transcript body is not the capture")

    def test_each_claim_has_its_source_link_then_its_excerpt(self):
        for m in re.finditer(r"^- (?:Legal name|Total revenue).*\n  Source: <(.*?)>\n\n```\n(.*?)\n```", self.out, re.M):
            self.assertEqual(m.group(1), ORG_URL)
            self.assertIn(m.group(2), ORG)
        self.assertEqual(len(re.findall(r"^- (?:Legal name|Total revenue).*\n  Source: <", self.out, re.M)), 2)

    def test_later_filing_without_figures_is_disclosed(self):
        self.assertIn("A later filing is listed without extracted figures (filings_without_data), "
                      "tax_prd as shown: `202406`", self.out)
        self.assertIn('"tax_prd":202406', self.out)

    def test_organization_tax_period_is_labelled_not_used(self):
        self.assertIn('Organization record tax_period as shown: `"2025-06-01"`. This is the organization '
                      "block's field, not the period of the figures above.", self.out)

    def test_highest_tax_prd_is_chosen_whatever_the_order(self):
        # DERIVED from the real capture: filings_with_data reversed, every
        # entry's bytes unchanged.
        node = pp.Node(ORG, 0)
        _, vs, ve = node.spans["filings_with_data"]
        items = [ORG[s:e] for s, e in pp.elements(ORG, vs)]
        derived = ORG[:vs] + "[" + ",".join(reversed(items)) + "]" + ORG[ve:]
        out = pp.report(None, ["530196605"], {}, "x", fetcher=fake_fetcher({ORG_URL: derived}))
        self.assertIn("Tax period of the filing (tax_prd) as shown: `202306`", out)
        self.assertIn("Total revenue (totrevenue) as shown: `3217077611`", out)

    def test_no_filings_with_data_is_stated_not_filled(self):
        # DERIVED from the real capture: filings_with_data emptied.
        node = pp.Node(ORG, 0)
        _, vs, ve = node.spans["filings_with_data"]
        derived = ORG[:vs] + "[]" + ORG[ve:]
        out = pp.report(None, ["530196605"], {}, "x", fetcher=fake_fetcher({ORG_URL: derived}))
        self.assertIn("No filing with extracted figures is listed", out)
        self.assertNotIn("totrevenue) as shown", out)

    def test_missing_blocks_fail_closed(self):
        # DERIVED from the real capture: the filings_with_data member removed.
        node = pp.Node(ORG, 0)
        ks, _, ve = node.spans["filings_with_data"]
        derived = ORG[:ks] + ORG[ve + 1:]
        json.loads(derived)
        with self.assertRaises(pp.FetchError):
            pp.report(None, ["530196605"], {}, "x", fetcher=fake_fetcher({ORG_URL: derived}))


class Search(unittest.TestCase):
    def test_results_listed_and_only_given_ein_examined(self):
        out = pp.report("American Red Cross", ["530196605"], {"204801016": "separate local club"},
                        "American Red Cross", fetcher=fake_fetcher(REAL))
        self.assertIn("total_results as shown: 11. Organizations on this page: 11. num_pages as shown: 1.", out)
        self.assertIn('- Result `530196605`: strein `"53-0196605"`, name `"American National Red Cross"`, '
                      'city `"Washington"`, state `"DC"`. Status: examined below.', out)
        self.assertIn("Status: checked and excluded by the operator: separate local club.", out)
        self.assertEqual(out.count("Status: not examined."), 9)
        self.assertIn("#### Checked and excluded", out)
        self.assertIn('{"ein":204801016,"strein":"20-4801016","name":"881458 American Red Cross Club"', out)
        for block in fences(out):
            self.assertTrue(block in SEARCH or block in ORG or block.endswith(SEARCH) or block.endswith(ORG))

    def test_name_only_without_exact_match_fetches_nothing_more(self):
        out = pp.report("American Red Cross", [], {}, "x", fetcher=fake_fetcher({SEARCH_URL: SEARCH}))
        self.assertIn("No search result's name equals the search text exactly", out)
        self.assertNotIn("### Organization", out)

    def test_exact_name_match_ignores_case_and_spacing_only(self):
        found = pp.search_results(capture(SEARCH_URL, SEARCH), {})[2]
        self.assertEqual(pp.exact_name_matches(found, "american  national RED cross"), ["530196605"])
        self.assertEqual(pp.exact_name_matches(found, "American Red Cross"), [])

    def test_exclusion_not_in_response_is_refused(self):
        with self.assertRaises(ValueError):
            pp.report("American Red Cross", [], {"123456789": "not fetched"}, "x", fetcher=fake_fetcher(REAL))

    def test_empty_search_prints_the_full_raw_response(self):
        # SYNTHETIC: an empty-result body in the shape of the real search
        # response. The live empty shape was not observed.
        body = '{"total_results":0,"organizations":[],"num_pages":0}'
        url = pp.search_url("No Such Org Xq")
        out = pp.report("No Such Org Xq", [], {}, "x", fetcher=fake_fetcher({url: body}))
        self.assertIn("The search returned no organizations. The complete raw response is below", out)
        self.assertTrue(fences(out)[-1].endswith("\n\n" + body))


class Handler(http.server.BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        status, body, ctype = self.routes.get(self.path, (404, '{"error":"SYNTHETIC not found"}', "application/json"))
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class EndToEnd(unittest.TestCase):
    """main() against a local server on 127.0.0.1 serving the real bodies."""

    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d/nonprofits/api/v2" % cls.server.server_port
        Handler.routes = {
            "/nonprofits/api/v2/search.json?q=American+Red+Cross": (200, SEARCH, "application/json"),
            "/nonprofits/api/v2/organizations/530196605.json": (200, ORG, "application/json"),
            # SYNTHETIC failure answers:
            "/nonprofits/api/v2/organizations/000000001.json": (500, "SYNTHETIC server error", "text/plain"),
            "/nonprofits/api/v2/organizations/000000002.json": (200, "SYNTHETIC <html>not json</html>", "text/html"),
        }

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def run_main(self, argv, base=None):
        saved = pp.API
        pp.API = base or self.base
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = pp.main(argv)
        finally:
            pp.API = saved
        return code, out.getvalue(), err.getvalue()

    def test_full_run_prints_transcripts_with_the_capture_bodies(self):
        code, out, err = self.run_main(["--name", "American Red Cross", "--ein", "53-0196605"])
        self.assertEqual(code, 0, err)
        self.assertIn("HTTP status: HTTP/1.0 200 OK", out)
        self.assertIn("Retrieved (UTC): ", out)
        self.assertTrue(re.search(r"^Retrieved \(UTC\): \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$", out, re.M))
        tails = [b for b in fences(out) if b.startswith("HTTP/")]
        self.assertEqual(len(tails), 2)
        self.assertTrue(tails[0].endswith("\n\n" + SEARCH))
        self.assertTrue(tails[1].endswith("\n\n" + ORG))

    def test_http_error_fails_closed(self):
        code, out, err = self.run_main(["--ein", "000000001"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("HTTP 500", err)

    def test_404_is_a_failure_not_an_empty_result(self):
        code, out, err = self.run_main(["--name", "Unrouted Name"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("HTTP 404", err)

    def test_non_json_body_fails_closed(self):
        code, out, err = self.run_main(["--ein", "000000002"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("not a JSON object", err)

    def test_transport_failure_fails_closed(self):
        code, out, err = self.run_main(["--ein", "530196605"], base="http://127.0.0.1:9/nonprofits/api/v2")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("could not be fetched", err)

    def test_bad_inputs_are_refused(self):
        for argv in (["--ein", "12345"], [], ["--ein", "530196605", "--exclude", "204801016=x"],
                     ["--name", "x", "--ein", "530196605", "--exclude", "530196605=x"]):
            with self.subTest(argv=argv):
                code, out, _ = self.run_main(argv)
                self.assertEqual((code, out), (2, ""))


@unittest.skipUnless(os.environ.get("PROPUBLICA_LIVE") == "1", "set PROPUBLICA_LIVE=1 to query the live API")
class Live(unittest.TestCase):
    def test_live_organization_matches_capture_identity(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = pp.main(["--name", "American Red Cross", "--ein", "530196605"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn('Legal name (name) as shown: `"American National Red Cross"`', text)
        self.assertIn("Total revenue (totrevenue) as shown: `", text)


if __name__ == "__main__":
    unittest.main()
