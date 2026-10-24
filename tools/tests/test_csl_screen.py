"""Tests for tools/csl_screen.py and its GET /csl route (issue #179). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_csl_screen.py' -v

Fixtures (fixtures/csl/, recorded in provenance.json): an EXCERPT of the
real consolidated.csv, the header line plus seven data lines verbatim
from the complete file as retrieved on 2026-10-24; the complete file's
size, line count, row count and SHA-256 are in the provenance (the
complete file is about 16 MB and is not committed). Variants built here
from those lines say DERIVED where they are built. Every test runs with
urlopen replaced by a function that fails the test, and with the list
cache pointed at a fresh temporary directory.
"""

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import csl_screen as c  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "csl"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
EXCERPT = (FIX / "consolidated-excerpt.csv").read_bytes()
# The headers the live GET of the complete file returned on 2026-10-24, as recorded in provenance.
CAPTURED_HEADERS = [("Content-Type", "text/csv"), ("Content-Length", "16832471"),
                    ("Last-Modified", "Sat, 24 Oct 2026 04:30:32 GMT"), ("ETag", "0x8DF31878A87768F")]


def download(data=EXCERPT, headers=CAPTURED_HEADERS, retrieved="2026-10-24T05:15:38Z"):
    return c.Download(c.CSL_URL, retrieved, list(headers), data)


def replay(data=EXCERPT):
    def fetcher(url):
        if url != c.CSL_URL:
            raise AssertionError("unexpected url %s" % url)
        return download(data)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("csl_screen tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.dict(os.environ, {"CSL_CACHE_DIR": tmp}), \
            mock.patch("urllib.request.urlopen", no_network):
        code = c.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_excerpt_matches_provenance_and_names_the_complete_file(self):
        entry = PROV["consolidated-excerpt.csv"]
        self.assertEqual(hashlib.sha256(EXCERPT).hexdigest(), entry["sha256"])
        self.assertEqual(len(EXCERPT), entry["bytes"])
        self.assertTrue(entry["contents"].startswith("EXCERPT"))
        complete = entry["complete_file_as_retrieved"]
        self.assertEqual(complete["sha256"],
                         "1091be6f588e5a3cc67a88cf748724a9621dff849d56a1f5a3c58d701af5a325")
        self.assertEqual(complete["data_rows"], 26173)
        self.assertEqual(complete["last_modified_header"], "Sat, 24 Oct 2026 04:30:32 GMT")
        self.assertEqual(len(EXCERPT.decode("utf-8").splitlines()), 8)  # header plus seven rows


class MatchingTests(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(c.match_kind("mohammed abu teir", "Mohammed ABU TEIR"), "exact")
        self.assertEqual(c.match_kind("Huawei Technologies", "HUAWEI TECHNOLOGIES CO., LTD."), "contains")
        self.assertIsNone(c.match_kind("Huawei Tech", "HUAWEI TECHNOLOGIES CO., LTD."))  # whole words only
        self.assertEqual(c.match_kind("Aero Caribbean", "AERO-CARIBBEAN"), "exact")
        self.assertIsNone(c.match_kind("", "ANY"))


class ReportTests(unittest.TestCase):
    def test_primary_exact_match_prints_the_raw_row_in_full(self):
        code, out, err = run(["Mohammed Abu Teir"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("1 list entry matched Mohammed Abu Teir: 1 with an exact match", out)
        self.assertIn("- List as shown (source): Palestinian Legislative Council List (PLC) - "
                      "Treasury Department", out)
        self.assertIn("- Program as shown: NS-PLC", out)
        self.assertIn("- Matched: exact match on the name Mohammed ABU TEIR", out)
        self.assertIn('"9640","Palestinian Legislative Council List (PLC) - Treasury Department","9640",'
                      '"Individual","NS-PLC","Mohammed ABU TEIR"', out)
        self.assertIn("line 2 of the file as read", out)
        self.assertIn("List publication date as published (the file's Last-Modified header): "
                      "Sat, 24 Oct 2026 04:30:32 GMT", out)
        self.assertIn("7 rows screened", out)

    def test_alias_match_is_told_apart(self):
        _, out, _ = run(["Mohammad Mahmoud Abou Tayr"])
        self.assertIn("- Matched: exact match on the alias Mohammad Mahmoud ABOU TAYR", out)
        self.assertIn("### Mohammed ABU TEIR", out)

    def test_contains_matches_across_lists(self):
        _, out, _ = run(["Huawei Technologies"])
        self.assertIn("2 list entries matched Huawei Technologies: 0 with an exact match, "
                      "2 by contains match only.", out)
        self.assertIn("Entity List (EL) - Bureau of Industry and Security", out)
        self.assertIn("Non-SDN Chinese Military-Industrial Complex Companies List (CMIC) - "
                      "Treasury Department", out)
        _, out, _ = run(["Aeroflot"])
        self.assertIn("Denied Persons List (DPL) - Bureau of Industry and Security", out)
        self.assertIn("- Program as shown: not shown", out)

    def test_no_match_states_the_list_date_and_rows_screened(self):
        code, out, _ = run(["zqxflorp holdings"])
        self.assertEqual(code, 0)
        self.assertIn("No name or alias matched zqxflorp holdings under the rule above. Screened: 7 rows "
                      "of the Consolidated Screening List as published on Sat, 24 Oct 2026 04:30:32 GMT "
                      "(file SHA-256 %s)" % hashlib.sha256(EXCERPT).hexdigest(), out)
        self.assertIn("no match is not a screening clearance", out)
        self.assertIn(c.RULE, out)

    def test_a_file_not_in_the_published_shape_is_refused(self):
        # DERIVED: the excerpt with its header renamed, so it is no longer the published header.
        bad = EXCERPT.replace(b"_id,source", b"id,source", 1)
        code, out, err = run(["Aeroflot"], replay(bad))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("not the published CSL header", err)

    def test_short_names_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        self.assertEqual(run(["ab"], must_not)[0], 2)
        self.assertEqual(run(["  "], must_not)[0], 2)


class FetchAndCacheTests(unittest.TestCase):
    def test_fetch_failures_fail_closed(self):
        # SYNTHETIC answers: an HTTP error and a transport failure.
        def http_error(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 503, "Unavailable", {}, io.BytesIO(b"{}"))
        def transport(request, timeout=None):
            raise urllib.error.URLError("SYNTHETIC no route")
        for fake in (http_error, transport):
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(c.FetchError):
                    c.fetch(c.CSL_URL)

    def test_main_maps_a_source_failure_to_exit_2_with_no_report(self):
        def refused(url):
            raise c.FetchError("SYNTHETIC 503; no report")
        code, out, err = run(["Aeroflot"], refused)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC 503; no report", err)

    def test_cache_round_trip_and_refresh(self):
        calls = []
        def counting(url):
            calls.append(url)
            return download()
        with tempfile.TemporaryDirectory() as tmp:
            first = c.load(fetcher=counting, directory=tmp)
            self.assertIsNone(first.from_cache)
            second = c.load(fetcher=counting, directory=tmp)
            self.assertIsNotNone(second.from_cache)
            self.assertEqual(second.retrieved, first.retrieved)
            self.assertEqual(len(calls), 1)
            report = c.render("Aeroflot", second)
            self.assertIn("Read from the local cache", report)
            third = c.load(fetcher=counting, refresh=True, directory=tmp)
            self.assertIsNone(third.from_cache)
            self.assertEqual(len(calls), 2)

    def test_a_corrupt_cache_is_downloaded_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            c.load(fetcher=replay(), directory=tmp)
            (Path(tmp) / "consolidated.csv").write_bytes(b"tampered")
            again = c.load(fetcher=replay(), directory=tmp)
            self.assertIsNone(again.from_cache)
            self.assertEqual(again.data, EXCERPT)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.csl_screen, its own module object.
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.dict(os.environ, {"CSL_CACHE_DIR": tmp}), \
                mock.patch.object(endpoints.cs, "fetch", replay()), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/csl", qs, None)

    def test_route(self):
        status, _, body = self.get("name=Mohammed%20Abu%20Teir")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("Palestinian Legislative Council List (PLC)", text)
        self.assertEqual(self.get("name=zqxflorp%20holdings")[0], "200 OK")
        self.assertEqual(self.get("")[0], "400 Bad Request")
        self.assertEqual(self.get("name=ab")[0], "400 Bad Request")
        self.assertEqual(endpoints.describe()["/csl"]["sources"], [c.CSL_URL])

    def test_route_maps_a_source_failure_to_502(self):
        def refused(url):
            raise endpoints.cs.FetchError("SYNTHETIC 503; no report")
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.dict(os.environ, {"CSL_CACHE_DIR": tmp}), \
                mock.patch.object(endpoints.cs, "fetch", refused):
            self.assertEqual(recall_api.handle("GET", "/csl", "name=Aeroflot", None)[0],
                             "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
