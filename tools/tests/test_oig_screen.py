"""Tests for tools/oig_screen.py and its GET /oig route (issue #180). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_oig_screen.py' -v

Fixture (fixtures/oig/, recorded in provenance.json): an EXCERPT of the
complete LEIE database file, every line byte verbatim from the
coordinator's captures on issue #180 (Capture B, comment 6380711049, and
its correction, comment 6380713028); the complete file's size, line count
and SHA-256 are in the provenance. Variants built here from those lines say
DERIVED where they are built, and stand-ins say SYNTHETIC. Every test runs
with urlopen replaced by a function that fails the test, except the fetch
tests, which replace it with a fake.
"""

import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import oig_screen as o  # noqa: E402
from api import endpoints, recall_api  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "oig"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
LEIE = (FIX / "leie-excerpt.csv").read_bytes()
# The headers the coordinator's capture stated for the complete file (issue #180, Capture B).
CAPTURED_HEADERS = [("Content-Type", "text/csv"), ("Content-Disposition", 'attachment; filename="UPDATED.csv"'),
                    ("Last-Modified", "Fri, 09 Oct 2026 12:51:03 GMT"), ("Content-Length", "10802977")]


def replay(data=LEIE, headers=CAPTURED_HEADERS, module=o):
    def fetcher(url):
        if url != module.LEIE_URL:
            raise AssertionError("unexpected url %s" % url)
        return module.Download(url, "2026-10-24T06:20:00Z", list(headers), data)
    return fetcher


def no_network(*args, **kwargs):
    raise AssertionError("oig_screen tried to reach the network")


def run(argv, fetcher=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("urllib.request.urlopen", no_network):
        code = o.main(argv, fetcher=fetcher or replay(), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class FixtureTests(unittest.TestCase):
    def test_excerpt_matches_provenance_and_names_the_complete_file(self):
        entry = PROV["leie-excerpt.csv"]
        self.assertEqual(hashlib.sha256(LEIE).hexdigest(), entry["sha256"])
        self.assertTrue(entry["contents"].startswith("EXCERPT"))
        self.assertEqual(entry["complete_file_as_retrieved"]["sha256"],
                         "7483d47bc48734f7955095d51d13dd1111b11cc8a60f54ebe894806e6c293c03")
        self.assertEqual(entry["complete_file_as_retrieved"]["zqxflorp_occurrences"], 0)
        self.assertEqual(LEIE.decode().split("\n")[0], ",".join(o.HEADER))
        self.assertEqual(len(LEIE.decode().splitlines()), 23)


class MatchingTests(unittest.TestCase):
    def row(self, n):
        return o.rows(replay()(o.LEIE_URL))[0][n][2]

    def test_name_forms_and_rule(self):
        aaron = self.row(11)  # SMITH,AARON,JEFFREY
        self.assertEqual(o.name_forms(aaron), [("first last", "AARON SMITH"), ("first middle last", "AARON JEFFREY SMITH"),
                                               ("last first", "SMITH AARON"), ("last first middle", "SMITH AARON JEFFREY")])
        self.assertEqual(o.best_match("aaron smith", aaron)[:2], ("exact", "first last"))
        self.assertEqual(o.best_match("Smith, Aaron Jeffrey", aaron)[:2], ("exact", "last first middle"))
        self.assertEqual(o.best_match("Jeffrey Smith", aaron)[:2], ("contains", "first middle last"))
        # An exact match wins over a contains match found in an earlier form.
        self.assertEqual(o.best_match("Smith Aaron", aaron)[:2], ("exact", "last first"))
        self.assertIsNone(o.best_match("Aar Smith", aaron))  # whole words only
        entity = self.row(1)  # "1 BEST CARE, INC"
        self.assertEqual(o.name_forms(entity), [("BUSNAME", "1 BEST CARE, INC")])
        self.assertEqual(o.best_match("1 Best Care Inc", entity)[0], "exact")
        self.assertEqual(o.best_match("best care", entity)[0], "contains")


class ReportTests(unittest.TestCase):
    def test_individual_hit_answer_first_with_type_date_and_raw_row(self):
        code, out, err = run(["Aaron Smith"])
        self.assertEqual((code, err), (0, ""))
        self.assertLess(out.index("## Answer"), out.index("## Database read"))
        self.assertIn("1 LEIE row matched Aaron Smith: 1 with an exact match, 0 by contains match only.", out)
        self.assertIn("Screened: 22 data rows of the LEIE database dated Fri, 09 Oct 2026 12:51:03 GMT", out)
        self.assertIn("file SHA-256 %s" % hashlib.sha256(LEIE).hexdigest(), out)
        self.assertIn("### Line 13: SMITH, AARON JEFFREY", out)
        self.assertIn("- Exclusion type (EXCLTYPE) as published: 1128a1", out)
        self.assertIn("- Exclusion date (EXCLDATE) as published: 20190718", out)
        self.assertIn("- Matched: exact match on AARON SMITH (first last)", out)
        self.assertIn("- WAIVERDATE as published: 0; WVRSTATE as published: (empty)", out)
        self.assertIn("Source: <%s>, line 13 of the file as read\n```\n%s\n```" % (o.LEIE_URL, LEIE.decode().split("\n")[12]),
                      out)
        self.assertIn("does not define the codes", out)

    def test_entity_hit(self):
        _, out, _ = run(["#1 Marketing Service"])
        self.assertIn("### Line 2: #1 MARKETING SERVICE, INC", out)
        self.assertIn("- Row has a LASTNAME: no (BUSNAME row)", out)
        self.assertIn("- Exclusion type (EXCLTYPE) as published: 1128a1", out)
        self.assertIn("- Exclusion date (EXCLDATE) as published: 20200319", out)
        self.assertIn('Matched: contains match on #1 MARKETING SERVICE, INC (BUSNAME)', out)

    def test_waiver_row_shows_waiver_date_and_state_as_published(self):
        _, out, _ = run(["Samir Wahib"])
        self.assertIn("- WAIVERDATE as published: 20240227; WVRSTATE as published: IN", out)
        self.assertIn("- REINDATE as published: 0", out)

    def test_surname_search_counts_contains_matches(self):
        _, out, _ = run(["Smith"])
        self.assertIn("10 LEIE rows matched Smith: 0 with an exact match, 10 by contains match only.", out)
        self.assertNotIn("14 LAWRENCE AVE PHARMACY", out)  # its CITY is SMITHTOWN: only names are compared
        self.assertEqual(out.count("\n### Line "), 10)

    def test_crlf_line_endings_read_the_same(self):
        # DERIVED: the excerpt with CRLF line endings (the captures do not state the complete file's terminator).
        code, out, _ = run(["Aaron Smith"], replay(LEIE.replace(b"\n", b"\r\n")))
        self.assertEqual(code, 0)
        self.assertIn("### Line 13: SMITH, AARON JEFFREY", out)
        self.assertNotIn("\r", out)  # the raw row is printed without its CR

    def test_long_result_lists_are_capped_and_counted(self):
        # DERIVED: 60 copies of a captured SMITH row.
        lines = LEIE.decode().split("\n")
        data = ("\n".join([lines[0]] + [lines[12]] * 60) + "\n").encode()
        _, out, _ = run(["Smith"], replay(data))
        self.assertIn("60 LEIE rows matched Smith", out)
        self.assertIn("The first 50, in file order, are listed; 10 more matched and are not listed.", out)
        self.assertEqual(out.count("\n### Line "), 50)

    def test_no_match_is_proven_by_the_file_as_read_never_a_clearance(self):
        code, out, _ = run(["zqxflorp"])
        self.assertEqual(code, 0)
        self.assertIn("No row of the LEIE database matched zqxflorp under the matching rule below. Screened: 22 data "
                      "rows of the LEIE database dated Fri, 09 Oct 2026 12:51:03 GMT (the file's Last-Modified header "
                      "as returned), file SHA-256 %s. No match is not a clearance." % hashlib.sha256(LEIE).hexdigest(),
                      out)
        self.assertIn("File as read: %d bytes, SHA-256 %s, 23 lines, decoded as UTF-8; 22 data rows"
                      % (len(LEIE), hashlib.sha256(LEIE).hexdigest()), out)
        self.assertIn("Last-Modified: Fri, 09 Oct 2026 12:51:03 GMT", out)
        self.assertIn(o.RULE, out)


class FailClosedTests(unittest.TestCase):
    def test_a_file_not_in_the_captured_shape_is_refused(self):
        lines = LEIE.decode().split("\n")
        bad = [b"<html>SYNTHETIC maintenance</html>\n", b"",
               ("\n".join([lines[0].replace("WVRSTATE", "WAIVERSTATE")] + lines[1:])).encode(),  # DERIVED
               ("\n".join(lines[:5] + [lines[5] + ",EXTRA"] + lines[6:])).encode(),  # DERIVED
               (lines[0] + "\n").encode()]  # DERIVED: header only
        for data in bad:
            code, out, err = run(["Aaron Smith"], replay(data))
            self.assertEqual((code, out), (2, ""), data[:40])
            self.assertIn("no report", err)

    def test_no_last_modified_means_no_database_date_and_no_report(self):
        headers = [h for h in CAPTURED_HEADERS if h[0] != "Last-Modified"]
        code, out, err = run(["Aaron Smith"], replay(headers=headers))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("database date cannot be stated", err)

    def test_a_failed_download_is_never_no_match(self):
        def broken(url):
            raise o.FetchError("the LEIE database download %s failed: SYNTHETIC connection reset; no report" % url)
        code, out, err = run(["zqxflorp"], broken)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("SYNTHETIC connection reset", err)

    def test_fetch_maps_http_errors_non_200_and_redirects(self):
        class Answer:  # SYNTHETIC response object
            def __init__(self, status, url):
                self.status, self._url, self.headers = status, url, {"Last-Modified": "SYNTHETIC"}

            def read(self):
                return LEIE

            def geturl(self):
                return self._url

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def http_error(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 503, "Service Unavailable", {}, io.BytesIO(b""))
        for fake in (http_error, lambda request, timeout=None: Answer(206, o.LEIE_URL),
                     lambda request, timeout=None: Answer(200, "https://example.invalid/UPDATED.csv")):
            with mock.patch("urllib.request.urlopen", fake):
                with self.assertRaises(o.FetchError):
                    o.fetch(o.LEIE_URL)
        with mock.patch("urllib.request.urlopen", lambda request, timeout=None: Answer(200, o.LEIE_URL)):
            got = o.fetch(o.LEIE_URL)
        self.assertEqual((got.data, got.header("last-modified")), (LEIE, "SYNTHETIC"))

    def test_short_names_are_refused_before_any_fetch(self):
        def must_not(url):
            raise AssertionError("no fetch expected")
        for name in ("", "ab", "a.b", "  "):
            self.assertEqual(run([name], must_not)[0], 2, name)


class RouteTests(unittest.TestCase):
    def get(self, qs):
        # api/endpoints.py imports the tool as tools.oig_screen, its own module object.
        with mock.patch.object(endpoints.oig, "fetch", replay(module=endpoints.oig)), \
                mock.patch("urllib.request.urlopen", no_network):
            return recall_api.handle("GET", "/oig", qs, None)

    def test_route_serves_the_report_and_refuses_bad_queries(self):
        status, _, body = self.get("name=Aaron+Smith")
        self.assertEqual(status, "200 OK")
        text = body.decode() if isinstance(body, bytes) else body
        self.assertIn("### Line 13: SMITH, AARON JEFFREY", text)
        self.assertEqual(self.get("name=zqxflorp")[0], "200 OK")
        for qs in ("", "name=ab", "name=a.b"):
            self.assertEqual(self.get(qs)[0], "400 Bad Request", qs)
        self.assertEqual(endpoints.describe()["/oig"]["sources"], [o.LEIE_URL])

    def test_route_maps_a_failed_download_to_502(self):
        def broken(url):
            raise endpoints.oig.FetchError("SYNTHETIC failure; no report")
        with mock.patch.object(endpoints.oig, "fetch", broken):
            self.assertEqual(recall_api.handle("GET", "/oig", "name=Smith", None)[0], "502 Bad Gateway")


if __name__ == "__main__":
    unittest.main()
