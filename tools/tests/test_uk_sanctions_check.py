"""Offline tests for tools/uk_sanctions_check.py (issue #342).

Run:  python3 -m unittest discover -s tools/tests -p 'test_uk_sanctions_check.py' -v

The fixture is an excerpt assembled from four verbatim lines of the
coordinator's Option B capture of ConList.csv on issue #342 (date line,
header row, one Individual row, one Entity row), with its provenance in
tools/tests/fixtures/uk-sanctions/provenance.json. Cases that need a shape
the captures do not show (an alias row, a changed header) are built from
those lines and labelled SYNTHETIC. No network is used: urllib's urlopen is
replaced for every test by a function that fails the test.
"""

import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (str(ROOT / "tools"), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import uk_sanctions_check as uk  # noqa: E402

FIX = HERE / "fixtures" / "uk-sanctions"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
EXCERPT = (FIX / "conlist-excerpt.csv").read_bytes()
LINES = EXCERPT.decode("utf-8").split("\n")[:4]  # date line, header, Individual row, Entity row
RETRIEVED = "2026-10-24T13:20:00Z"  # test value; the capture's own time is in provenance.json


def download(data=EXCERPT, headers=()):
    return uk.Download(uk.LIST_URL, RETRIEVED, list(headers), data, False)


def replay(data=EXCERPT):
    def fetcher(url):
        if url != uk.LIST_URL:
            raise AssertionError("unexpected url %s" % url)
        return download(data)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("the UK sanctions tests tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    code = uk.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)


class FixtureTests(Base):
    def test_the_excerpt_matches_its_recorded_hash(self):
        meta = PROV["conlist-excerpt.csv"]
        self.assertEqual(hashlib.sha256(EXCERPT).hexdigest(), meta["sha256"])
        self.assertEqual(len(EXCERPT), meta["bytes"])
        self.assertEqual(meta["source_url"], uk.LIST_URL)

    def test_the_excerpt_carries_the_captured_header_and_rows(self):
        self.assertEqual(LINES[0], "Last Updated,03/06/2026")
        self.assertEqual(tuple(LINES[1].split(",")), uk.HEADER)
        self.assertTrue(LINES[2].startswith("MITHOO,Mian,"))
        self.assertTrue(LINES[3].startswith("GAZPROM NEFT,"))


class ReportTests(Base):
    def test_exact_entity_match_prints_the_entry_rows_verbatim(self):
        code, out, err = run(["Gazprom Neft"])
        self.assertEqual(code, 0, err)
        self.assertIn("1 list entry matched Gazprom Neft: 1 with an exact match, 0 by contains match only.", out)
        self.assertIn("### Group ID 16736: Entity, regime Russia", out)
        self.assertIn("- exact match on GAZPROM NEFT (Alias Type as shown: Primary name)", out)
        self.assertIn("All 1 record of this entry in the file, verbatim:\n```\n%s\n```" % LINES[3], out)

    def test_both_name_orders_are_checked(self):
        _, out, _ = run(["Mian Mithoo"])
        self.assertIn("- exact match on Mian MITHOO (Alias Type as shown: Primary name variation)", out)
        _, out, _ = run(["Mithoo Mian"])
        self.assertIn("- exact match on MITHOO Mian", out)

    def test_contains_is_whole_words_and_accents_fold(self):
        _, out, _ = run(["neft"])
        self.assertIn("0 with an exact match, 1 by contains match only", out)
        _, out, _ = run(["Gazprom Néft"])
        self.assertIn("1 with an exact match", out)
        _, out, _ = run(["Gazpro"])
        self.assertIn("No name matched Gazpro", out)

    def test_no_match_is_proven_by_the_file_as_read(self):
        code, out, _ = run(["Nosuch Holdings"])
        self.assertEqual(code, 0)
        sha = hashlib.sha256(EXCERPT).hexdigest()
        self.assertIn("No name matched Nosuch Holdings under the rule above. Checked: 2 records in 2 list entries "
                      "of the file exactly as read above (%d bytes, SHA-256 %s, list date line Last "
                      "Updated,03/06/2026)." % (len(EXCERPT), sha), out)
        self.assertIn("List date line, as read (line 1): Last Updated,03/06/2026", out)
        self.assertIn("Records by Group Type, as read: Entity 1, Individual 1.", out)
        self.assertNotIn("### Group ID", out)

    def test_the_non_latin_name_is_not_matched(self):
        # The captured Non-Latin Script value: under the rule its letters fold to
        # separators, so it is refused as too short rather than searched.
        code, out, err = run(["ГАЗПРОМ НЕФТЬ"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("error: the name must have at least 3 letters or digits", err)

    def test_alias_rows_are_grouped_with_their_entry(self):
        # SYNTHETIC: a second row for Group ID 16736, the captured Entity row with its
        # name and Alias Type changed, to show grouping; not a list record.
        alias = LINES[3].replace("GAZPROM NEFT,", "SYNTHETIC ALIAS NAME,", 1).replace(
            ",Entity,Primary name,", ",Entity,AKA (SYNTHETIC),", 1)
        data = "\n".join(LINES + [alias]).encode("utf-8") + b"\n"
        _, out, _ = run(["Synthetic Alias Name"], replay(data))
        self.assertIn("### Group ID 16736: Entity, regime Russia", out)
        self.assertIn("- exact match on SYNTHETIC ALIAS NAME (Alias Type as shown: AKA (SYNTHETIC))", out)
        self.assertIn("All 2 records of this entry in the file, verbatim:", out)
        self.assertIn("in 2 list entries (distinct Group ID values)", out)

    def test_response_headers_are_printed_as_returned(self):
        # SYNTHETIC headers: none were captured on issue #342.
        report = uk.render("Gazprom Neft", download(headers=[("Content-Type", "text/csv (SYNTHETIC)")]))
        self.assertIn("Response headers as returned (the ones listed in the tool):\n```\nContent-Type: text/csv "
                      "(SYNTHETIC)\n```", report)


class FailClosedTests(Base):
    def test_a_short_name_is_refused_with_no_fetch(self):
        def never(url):
            raise AssertionError("no fetch expected")
        for name in ("ab", "a.b", "  "):
            with self.subTest(name=name):
                code, out, err = run([name], never)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err.startswith("error: "), err)

    def test_a_file_not_in_the_captured_shape_is_a_source_failure(self):
        shapes = {
            "no date line": "\n".join(LINES[1:]),
            "changed header (SYNTHETIC)": "\n".join([LINES[0], LINES[1].replace("Group ID", "GroupID")] + LINES[2:]),
            "short row (SYNTHETIC)": "\n".join(LINES[:2] + ["MITHOO,Mian"]),
            "header only": "\n".join(LINES[:2]),
            "not csv": "<html>not the list</html>",
        }
        for label, text in shapes.items():
            with self.subTest(shape=label):
                code, out, err = run(["Gazprom Neft"], replay(text.encode("utf-8")))
                self.assertEqual((code, out), (2, ""))
                self.assertIn("source failure, nothing printed", err)

    def test_a_failed_fetch_is_a_source_failure(self):
        def refused(url):
            raise uk.FetchError("request to %s failed: test failure, connection refused; no report" % url)
        code, out, err = run(["Gazprom Neft"], refused)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("connection refused", err)


class FetchTests(Base):
    class Response(io.BytesIO):
        def __init__(self, data, status=200, url=uk.LIST_URL):
            super().__init__(data)
            self.status, self._url = status, url
            self.headers = {"Content-Type": "text/csv (SYNTHETIC)", "X-Other": "not shown"}

        def geturl(self):
            return self._url

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def test_a_200_returns_the_bytes_and_the_listed_headers_only(self):
        seen = {}

        def opener(request, timeout):
            seen["ua"] = request.get_header("User-agent")
            return self.Response(EXCERPT)
        with mock.patch("urllib.request.urlopen", opener):
            got = uk.fetch()
        self.assertEqual(got.data, EXCERPT)
        self.assertEqual(got.headers, [("Content-Type", "text/csv (SYNTHETIC)")])
        self.assertFalse(got.redirected)
        self.assertEqual(seen["ua"], uk.USER_AGENT)

    def test_an_http_error_raises_fetch_error(self):
        def opener(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, io.BytesIO(b""))
        with mock.patch("urllib.request.urlopen", opener), self.assertRaises(uk.FetchError) as ctx:
            uk.fetch()
        self.assertIn("HTTP 404", str(ctx.exception))

    def test_a_transport_error_raises_fetch_error(self):
        def opener(request, timeout):
            raise urllib.error.URLError("test failure: timed out")
        with mock.patch("urllib.request.urlopen", opener), self.assertRaises(uk.FetchError):
            uk.fetch()


class DocsPage(Base):
    def test_the_docs_page_names_the_question_the_source_and_the_price(self):
        page = (ROOT / "docs" / "mcpize-tools" / "uk_sanctions_check.md").read_text(encoding="utf-8")
        self.assertIn("0.25 USDC", page)
        self.assertIn(uk.LIST_URL, page)
        self.assertIn("tools/uk_sanctions_check.py", page)


if __name__ == "__main__":
    unittest.main()
