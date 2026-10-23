"""Tests for tools/nonprofit_pack.py. Standard library only, no network
unless PROPUBLICA_LIVE=1.

Run:  python3 -m unittest discover -s tools/tests -p 'test_nonprofit_pack.py' -v

Fixtures (all in fixtures/propublica/, hashes in provenance.json):

* search-american-red-cross.json and organization-530196605.json are the
  REAL CAPTURES the coordinator took live and posted on issue #47.
* search-feeding-america.json, organization-363673599.json and
  search-empty-zxqv.json are REAL CAPTURES taken live by H5 on
  2026-10-23 for issue #149. The empty search capture is the body of the
  HTTP 404 answer the search endpoint gives a search with no results;
  its status is recorded in provenance.json. Only bodies were captured,
  for these as for the earlier fixtures: the Capture objects in these
  tests carry the recorded status and a single Content-Type header as
  test scaffolding, and the graded content is the body.
* DERIVED data is built in the test that uses it from a real capture
  with one stated change, and is labelled DERIVED there. SYNTHETIC data
  (small parser inputs, error bodies) is hand written and labelled
  SYNTHETIC where it appears.
"""

import contextlib
import http.server
import io
import json
import os
import re
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nonprofit_pack as pk  # noqa: E402
import propublica_nonprofits as pp  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "propublica"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
RC_SEARCH = (FIXTURES / "search-american-red-cross.json").read_text(encoding="utf-8")
RC_ORG = (FIXTURES / "organization-530196605.json").read_text(encoding="utf-8")
FA_SEARCH = (FIXTURES / "search-feeding-america.json").read_text(encoding="utf-8")
FA_ORG = (FIXTURES / "organization-363673599.json").read_text(encoding="utf-8")
EMPTY_SEARCH = (FIXTURES / "search-empty-zxqv.json").read_text(encoding="utf-8")

RC_SEARCH_URL = PROVENANCE["search-american-red-cross.json"]["url"]
RC_ORG_URL = PROVENANCE["organization-530196605.json"]["url"]
FA_SEARCH_URL = PROVENANCE["search-feeding-america.json"]["url"]
FA_ORG_URL = PROVENANCE["organization-363673599.json"]["url"]
EMPTY_URL = PROVENANCE["search-empty-zxqv.json"]["url"]


def capture(url, body, status=200):
    line = "HTTP/1.1 200 OK" if status == 200 else "HTTP/1.1 404 Not Found"
    return pp.Capture(url, "2026-10-23T21:48:29Z", line, status, ["Content-Type: application/json"], body)


def fake_fetcher(bodies, calls=None):
    def fetcher(url):
        if calls is not None:
            calls.append(url)
        if url not in bodies:
            raise AssertionError("unexpected fetch: %s" % url)
        return bodies[url]
    return fetcher


BODIES = {
    RC_SEARCH_URL: capture(RC_SEARCH_URL, RC_SEARCH),
    RC_ORG_URL: capture(RC_ORG_URL, RC_ORG),
    FA_SEARCH_URL: capture(FA_SEARCH_URL, FA_SEARCH),
    FA_ORG_URL: capture(FA_ORG_URL, FA_ORG),
    EMPTY_URL: capture(EMPTY_URL, EMPTY_SEARCH, status=404),
}

ENTRIES = [pk.Entry("53-0196605", "ein", "530196605"),
           pk.Entry("Feeding America", "name", None),
           pk.Entry("Zxqv Memorial Pancake Foundation", "name", None)]


def fences(text):
    return re.findall(r"^```\n(.*?)\n```$", text, re.S | re.M)


def summary_rows(pack):
    rows = []
    for line in pack.splitlines():
        if re.match(r"\| \d+ \|", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


class PackAssembly(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.pack = pk.assemble(ENTRIES, "test batch", fetcher=fake_fetcher(BODIES, self.calls))

    def test_summary_rows_match_the_sections(self):
        rows = summary_rows(self.pack)
        self.assertEqual(len(rows), 3)
        # Row 1: the Red Cross by EIN. Row 2: Feeding America by name.
        for row, org_body, count in ((rows[0], RC_ORG, 13), (rows[1], FA_ORG, 12)):
            data = json.loads(org_body)
            latest = max(data["filings_with_data"], key=lambda f: f["tax_prd"])
            self.assertEqual(row[2], "Found")
            self.assertEqual(row[3], str(count))
            self.assertEqual(row[4], "`%d`" % latest["tax_prd"])
            self.assertEqual(row[5], "`%d`" % latest["totrevenue"])
            section_no = int(row[6])
            section = self.pack.split("## Section %d:" % section_no)[1]
            # The section states the same count and period in its figures
            # line, and the revenue figure inside a verbatim excerpt.
            self.assertIn("highest tax_prd (%d of %d entries)" % (latest["tax_prd"], count), section)
            self.assertIn('"totrevenue":%d' % latest["totrevenue"], section)
            self.assertIn("Total revenue (totrevenue) as shown: `%d`" % latest["totrevenue"], section)
        self.assertEqual(rows[0][1], "53-0196605")
        self.assertEqual(rows[1][1], "Feeding America")

    def test_not_found_row_and_closing_list_are_proven(self):
        rows = summary_rows(self.pack)
        self.assertEqual(rows[2][2], "Not found")
        self.assertEqual(rows[2][3:], ["n/a", "n/a", "n/a", "3"])
        self.assertIn("## Entities that could not be found", self.pack)
        self.assertIn('- Entry 3, "Zxqv Memorial Pancake Foundation": the search returned no '
                      "organizations.", self.pack)
        section = self.pack.split("## Section 3:")[1]
        self.assertIn("HTTP status: HTTP/1.1 404 Not Found", section)
        self.assertIn("The search returned no organizations. The complete raw response is below", section)
        self.assertTrue(fences(section)[-1].endswith("\n\n" + EMPTY_SEARCH))

    def test_every_fenced_excerpt_is_verbatim_from_a_capture(self):
        bodies = (RC_SEARCH, RC_ORG, FA_SEARCH, FA_ORG, EMPTY_SEARCH)
        for block in fences(self.pack):
            self.assertTrue(any(block in b or block.endswith("\n\n" + b) or b in block for b in bodies),
                            block[:80])

    def test_dedupe_by_ein_and_by_name(self):
        calls = []
        entries = [pk.Entry("Feeding America", "name", None), pk.Entry("363673599", "ein", "363673599"),
                   pk.Entry("53-0196605", "ein", "530196605"), pk.Entry("American National Red Cross", "name", None)]
        bodies = dict(BODIES)
        bodies[pp.search_url("American National Red Cross")] = capture(
            pp.search_url("American National Red Cross"), RC_SEARCH)
        # The Red Cross search capture answers the "American Red Cross" query;
        # for this entry the search text differs, but the fake fetcher keys on
        # URL only, and the capture's results carry the exact legal name.
        pack = pk.assemble(entries, "dupes", fetcher=fake_fetcher(bodies, calls))
        rows = summary_rows(pack)
        self.assertEqual(rows[1][2], "Found (same organization as entry 1)")
        self.assertEqual(calls.count(FA_ORG_URL), 1, "organization fetched twice for a duplicate")
        self.assertEqual(rows[3][2], "Found (same organization as entry 3)")
        self.assertIn("Resolved to EIN 530196605, examined in full at section 2.", pack)
        self.assertEqual(calls.count(RC_ORG_URL), 1)

    def test_no_exact_match_is_not_resolved_not_invented(self):
        entries = [pk.Entry("American Red Cross", "name", None)]
        pack = pk.assemble(entries, "x", fetcher=fake_fetcher(BODIES))
        rows = summary_rows(pack)
        self.assertEqual(rows[0][2], "Not resolved: no exact name match")
        self.assertIn("No search result's name equals the entry exactly", pack)
        self.assertNotIn("### Organization", pack)
        self.assertIn("None: no listed entity came back with an empty search.", pack)

    def test_multiple_exact_matches_are_not_resolved(self):
        # DERIVED from the real Feeding America search capture: its exact
        # match element is duplicated with only the EIN and strein changed,
        # so two results carry the exact name.
        node = pp.Node(FA_SEARCH, 0)
        _, vs, _ = node.spans["organizations"]
        spans = pp.elements(FA_SEARCH, vs)
        first = FA_SEARCH[spans[0][0]:spans[0][1]]
        self.assertIn('"ein":363673599', first)
        twin = first.replace('"ein":363673599', '"ein":999999999').replace(
            '"strein":"36-3673599"', '"strein":"99-9999999"')
        derived = FA_SEARCH[:spans[0][1]] + "," + twin + FA_SEARCH[spans[0][1]:]
        json.loads(derived)
        bodies = {FA_SEARCH_URL: capture(FA_SEARCH_URL, derived)}
        pack = pk.assemble([pk.Entry("Feeding America", "name", None)], "x", fetcher=fake_fetcher(bodies))
        rows = summary_rows(pack)
        self.assertEqual(rows[0][2], "Not resolved: 2 exact name matches")
        self.assertIn("the runner does not choose", pack)

    def test_fetch_failure_fails_the_whole_pack_closed(self):
        def boom(url):
            raise pp.FetchError("SYNTHETIC failure")
        with self.assertRaises(pp.FetchError):
            pk.assemble(ENTRIES, "x", fetcher=boom)


class EmptyShape(unittest.TestCase):
    def test_observed_empty_shape_is_recognized(self):
        self.assertTrue(pk.is_empty_search(capture(EMPTY_URL, EMPTY_SEARCH, status=404)))

    def test_other_bodies_are_not_empty(self):
        self.assertFalse(pk.is_empty_search(capture(FA_SEARCH_URL, FA_SEARCH)))
        # SYNTHETIC parser inputs, not captures:
        self.assertFalse(pk.is_empty_search(capture("u", '{"total_results":0,"organizations":[{"ein":1}]}')))
        self.assertFalse(pk.is_empty_search(capture("u", '{"total_results":3,"organizations":[]}')))
        self.assertFalse(pk.is_empty_search(capture("u", "not json")))


class Inputs(unittest.TestCase):
    def test_parse_entry(self):
        self.assertEqual(pk.parse_entry("53-0196605").kind, "ein")
        self.assertEqual(pk.parse_entry("530196605").ein, "530196605")
        self.assertEqual(pk.parse_entry("  Feeding America ").kind, "name")

    def test_read_list_skips_blanks_and_comments(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("# a comment\n\nFeeding America\n53-0196605\n")
            path = fh.name
        try:
            entries = pk.read_list(path)
        finally:
            os.unlink(path)
        self.assertEqual([(e.kind, e.text) for e in entries],
                         [("name", "Feeding America"), ("ein", "53-0196605")])

    def test_no_entries_is_refused(self):
        code = pk.main([])
        self.assertEqual(code, 2)


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
    """main() and the pack fetch against a local server on 127.0.0.1
    serving the real capture bodies, the empty one at its real 404."""

    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d/nonprofits/api/v2" % cls.server.server_port
        Handler.routes = {
            "/nonprofits/api/v2/search.json?q=Feeding+America": (200, FA_SEARCH, "application/json"),
            "/nonprofits/api/v2/organizations/363673599.json": (200, FA_ORG, "application/json"),
            "/nonprofits/api/v2/organizations/530196605.json": (200, RC_ORG, "application/json"),
            "/nonprofits/api/v2/search.json?q=Zxqv+Memorial+Pancake+Foundation": (404, EMPTY_SEARCH, "application/json"),
            # SYNTHETIC failure answers:
            "/nonprofits/api/v2/organizations/000000001.json": (500, "SYNTHETIC server error", "text/plain"),
            "/nonprofits/api/v2/search.json?q=Bogus+Shape": (404, '{"error":"SYNTHETIC not the empty shape"}', "application/json"),
        }

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def run_main(self, argv):
        saved = pp.API
        pp.API = self.base
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = pk.main(argv)
        finally:
            pp.API = saved
        return code, out.getvalue(), err.getvalue()

    def test_full_pack_from_a_list_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("Feeding America\n53-0196605\nZxqv Memorial Pancake Foundation\n")
            path = fh.name
        try:
            code, out, err = self.run_main(["--list", path])
        finally:
            os.unlink(path)
        self.assertEqual(code, 0, err)
        rows = summary_rows(out)
        self.assertEqual([r[2] for r in rows], ["Found", "Found", "Not found"])
        self.assertIn("HTTP status: HTTP/1.0 404 Not Found", out)
        self.assertTrue(fences(out)[-1].endswith("\n\n" + EMPTY_SEARCH) or
                        any(b.endswith("\n\n" + EMPTY_SEARCH) for b in fences(out)))

    def test_http_500_fails_closed(self):
        code, out, err = self.run_main(["--ein", "000000001"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("HTTP 500", err)

    def test_404_that_is_not_the_empty_shape_fails_closed(self):
        code, out, err = self.run_main(["--name", "Bogus Shape"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("HTTP 404", err)


@unittest.skipUnless(os.environ.get("PROPUBLICA_LIVE") == "1", "set PROPUBLICA_LIVE=1 to query the live API")
class Live(unittest.TestCase):
    def test_live_demo_list(self):
        lst = Path(__file__).resolve().parents[1] / "examples" / "nonprofit-pack-list.txt"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = pk.main(["--list", str(lst)])
        self.assertEqual(code, 0)
        rows = summary_rows(out.getvalue())
        self.assertEqual([r[2] for r in rows], ["Found"] * 5 + ["Not found"])


if __name__ == "__main__":
    unittest.main()
