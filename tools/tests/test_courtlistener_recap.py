"""Tests for tools/courtlistener_recap.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_courtlistener_recap.py' -v

The fixtures are not invented. Every response text below is copied
verbatim from the published litigation screen
deliveries/litigation-screen-5c567ad5-77c5-4ccc-a207-a1acc743b3bd.md,
which records for each source the exact query URL and the UTC retrieval
time; the delivery line range of each excerpt is given beside it. The
delivery prints contiguous slices of each JSON response, so the tests
close each slice syntactically where it ends (a trailing comma removed,
the open objects and arrays closed) to make it parse; no value is
changed, and the closings are labelled below. The docket record
excerpts are two slices of one response (fields before and after the
part the delivery did not print), joined into one object the same way.
The fetch tests use a local HTTP server on 127.0.0.1 and nothing else.
"""

import http.server
import io
import json
import os
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import courtlistener_recap as cl  # noqa: E402

# Delivery source Q1, search for party:("Jabil Inc."), delivery lines 197 to
# 220 verbatim. Recorded URL (percent signs written out):
# https://www.courtlistener.com/api/rest/v4/search/?type=d&q=party%3A%28%22Jabil+Inc.%22%29&filed_after=2021-10-22&order_by=dateFiled+desc
# Recorded retrieval: 2026-10-22T23:08:14Z
Q1_TEXT = """{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "assignedTo": null,
      "assigned_to_id": null,
      "attorney": [],
      "attorney_id": [],
      "caseName": "Andresen v. Jabil, Inc.",
      "case_name_full": "",
      "cause": "",
      "chapter": null,
      "court": "District Court, D. Minnesota",
      "court_citation_string": "D. Minnesota",
      "court_id": "mnd",
      "dateArgued": null,
      "dateFiled": "2026-07-10",
      "dateTerminated": null,
      "docketNumber": "0:26-cv-03269",
      "docket_absolute_url": "/docket/73603835/andresen-v-jabil-inc/",
      "docket_id": 73603835,
      "firm": [],"""

# Delivery source Q5, search for party:("Raymond James Financial"), a
# response that carries a next page cursor, delivery lines 321 to 344 verbatim.
# Recorded retrieval: 2026-10-22T23:08:53Z
Q5_TEXT = """{
  "count": 27,
  "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=cz0xMzM1MzIwNjAwMDAwMC4wJnM9Njc5ODE3OTAmdD1kJmQ9MjAyNi0xMC0yMiZwPTI%3D&filed_after=2021-10-22&order_by=dateFiled+desc&q=party%3A%28%22Raymond+James+Financial%22%29&type=d",
  "previous": null,
  "results": [
    {
      "assignedTo": "Edmund G LaCour, Jr",
      "assigned_to_id": null,
      "attorney": [],
      "attorney_id": [],
      "caseName": "Norris v. Raymond James Financial Services, Inc.",
      "case_name_full": "",
      "cause": "",
      "chapter": null,
      "court": "District Court, N.D. Alabama",
      "court_citation_string": "N.D. Ala.",
      "court_id": "alnd",
      "dateArgued": null,
      "dateFiled": "2026-05-15",
      "dateTerminated": null,
      "docketNumber": "7:26-cv-00830",
      "docket_absolute_url": "/docket/73354392/norris-v-raymond-james-financial-services-inc/",
      "docket_id": 73354392,
      "firm": [],"""

# Delivery source D1, docket record 73603835, two slices of one response,
# delivery lines 662 to 674 and 678 to 695 verbatim. Recorded retrieval:
# 2026-10-22T23:08:23Z
D1_A = """      "caseName": "Andresen v. Jabil, Inc.",
      "case_name_full": "",
      "cause": "",
      "chapter": null,
      "court": "District Court, D. Minnesota",
      "court_citation_string": "D. Minnesota",
      "court_id": "mnd",
      "dateArgued": null,
      "dateFiled": "2026-07-10",
      "dateTerminated": null,
      "docketNumber": "0:26-cv-03269",
      "docket_absolute_url": "/docket/73603835/andresen-v-jabil-inc/",
      "docket_id": 73603835,"""
D1_B = """      "jurisdictionType": "",
      "juryDemand": "",
      "meta": {
        "timestamp": "2026-07-12T15:30:38.685251Z",
        "date_created": "2026-07-10T23:03:55.783294Z",
        "score": {
          "bm25": 4.0
        }
      },
      "pacer_case_id": "235009",
      "party": [
        "Andresen",
        "Jabil, Inc."
      ],
      "party_id": [],
      "referredTo": null,
      "referred_to_id": null,
      "suitNature": "","""

# Delivery source D5, docket record 69574962 (the subject is a listed party
# on neither side of the caption), delivery lines 835 to 847 and 851 to 873.
# Recorded retrieval: 2026-10-22T23:08:34Z
D5_A = """      "caseName": "Allstate Vehicle and Property Insurance Company v. Whirlpool Corporation",
      "case_name_full": "",
      "cause": "28:1332 Diversity-Product Liability",
      "chapter": null,
      "court": "District Court, D. Colorado",
      "court_citation_string": "D. Colo.",
      "court_id": "cod",
      "dateArgued": null,
      "dateFiled": "2025-01-24",
      "dateTerminated": null,
      "docketNumber": "1:25-cv-00242",
      "docket_absolute_url": "/docket/69574962/allstate-vehicle-and-property-insurance-company-v-whirlpool-corporation/",
      "docket_id": 69574962,"""
D5_B = """      "jurisdictionType": "Diversity",
      "juryDemand": "Both",
      "meta": {
        "timestamp": "2025-06-08T10:45:25.468822Z",
        "date_created": "2025-01-24T18:33:40.964948Z",
        "score": {
          "bm25": 4.0
        }
      },
      "pacer_case_id": "240738",
      "party": [
        "Whirlpool Corporation",
        "Jabil Inc.",
        "Allstate Vehicle and Property Insurance Company"
      ],
      "party_id": [
        15033058,
        15033059,
        15033060
      ],
      "referredTo": "Cyrus Y. Chung",
      "referred_to_id": null,
      "suitNature": "110 Insurance","""

# Delivery source D9, docket record 68113338 (the subject is the plaintiff),
# delivery lines 1010 to 1022 and 1026 to 1046. Recorded retrieval:
# 2026-10-22T23:08:45Z
D9_A = """      "caseName": "Jabil, Inc. v. GE",
      "case_name_full": "",
      "cause": "",
      "chapter": null,
      "court": "Court of Appeals for the Eleventh Circuit",
      "court_citation_string": "11th Cir.",
      "court_id": "ca11",
      "dateArgued": null,
      "dateFiled": "2023-10-12",
      "dateTerminated": null,
      "docketNumber": "23-13436",
      "docket_absolute_url": "/docket/68113338/jabil-inc-v-ge/",
      "docket_id": 68113338,"""
D9_B = """      "jurisdictionType": "",
      "juryDemand": "",
      "meta": {
        "timestamp": "2025-03-02T13:58:01.372940Z",
        "date_created": "2023-12-22T20:30:13.540383Z",
        "score": {
          "bm25": 4.0
        }
      },
      "pacer_case_id": "84655",
      "party": [
        "JABIL, INC.",
        "GENERAL ELECTRIC COMPANY"
      ],
      "party_id": [
        13239068,
        13239069
      ],
      "referredTo": null,
      "referred_to_id": null,
      "suitNature": "4190 Other Contract Actions","""


def close_search_head(text):
    """A search head excerpt ends inside its first result at '"firm": [],'.
    Closing: drop that trailing comma, close the result object and the
    results array and the envelope. Not a recording of the closing."""
    return text.rstrip().rstrip(",") + "\n    }\n  ]\n}"


def docket_record(part_a, part_b):
    """Two recorded slices of one docket record joined into one object:
    '{' + first slice + second slice without its trailing comma + '}'.
    Not a recording of the braces."""
    return json.loads("{" + part_a.rstrip() + "\n" + part_b.rstrip().rstrip(",") + "\n}")


def envelope(records, count=None, next_url=None):
    """A search envelope in the recorded shape (count, next, previous,
    results) around the given records. Count defaults to their number."""
    return json.dumps({"count": len(records) if count is None else count, "next": next_url,
                       "previous": None, "results": records}, ensure_ascii=False)


Q1_DATA = json.loads(close_search_head(Q1_TEXT))
Q5_DATA = json.loads(close_search_head(Q5_TEXT))
RECORD_D1 = docket_record(D1_A, D1_B)
RECORD_D5 = docket_record(D5_A, D5_B)
RECORD_D9 = docket_record(D9_A, D9_B)
FILED_AFTER = "2021-10-22"
Q1_URL = "https://www.courtlistener.com/api/rest/v4/search/?type=d&q=party%3A%28%22Jabil+Inc.%22%29&filed_after=2021-10-22&order_by=dateFiled+desc"
RETRIEVED = "2026-10-22T23:08:14Z"


def capture(url, body, status_line="HTTP/1.1 200 OK", retrieved=RETRIEVED):
    """A Capture with a plain test header; the headers are not a recording."""
    return cl.Capture(url, retrieved, status_line, ["Content-Type: application/json"], body)


class FixtureTests(unittest.TestCase):
    def test_recorded_values(self):
        self.assertEqual(Q1_DATA["count"], 15)
        self.assertIsNone(Q1_DATA["next"])
        self.assertEqual(Q1_DATA["results"][0]["caseName"], "Andresen v. Jabil, Inc.")
        self.assertEqual(Q1_DATA["results"][0]["docket_id"], 73603835)
        self.assertEqual(Q5_DATA["count"], 27)
        self.assertTrue(Q5_DATA["next"].startswith("https://www.courtlistener.com/api/rest/v4/search/?cursor="))
        self.assertEqual(RECORD_D1["party"], ["Andresen", "Jabil, Inc."])
        self.assertEqual(RECORD_D5["suitNature"], "110 Insurance")
        self.assertEqual(RECORD_D5["cause"], "28:1332 Diversity-Product Liability")
        self.assertEqual(RECORD_D9["caseName"], "Jabil, Inc. v. GE")


class QueryBuildingTests(unittest.TestCase):
    def test_search_url_matches_recorded_delivery_urls(self):
        self.assertEqual(cl.search_url("Jabil Inc.", FILED_AFTER), Q1_URL)
        self.assertEqual(
            cl.search_url("Raymond James Financial, Inc.", FILED_AFTER),
            "https://www.courtlistener.com/api/rest/v4/search/?type=d&q=party%3A%28%22Raymond+James+Financial%2C+Inc.%22%29&filed_after=2021-10-22&order_by=dateFiled+desc",
        )

    def test_docket_url_matches_recorded_delivery_url(self):
        self.assertEqual(cl.docket_url("73603835"), "https://www.courtlistener.com/api/rest/v4/search/?type=d&q=docket_id%3A73603835")
        with self.assertRaises(ValueError):
            cl.docket_url("73603835 OR 1")

    def test_describe_query_matches_delivery_phrasing(self):
        self.assertEqual(cl.describe_query("Jabil Inc.", FILED_AFTER),
                         'type=d, q=party:("Jabil Inc."), filed_after=2021-10-22, order_by=dateFiled desc')

    def test_party_variant_rules(self):
        with self.assertRaises(ValueError):
            cl.party_query("")
        with self.assertRaises(ValueError):
            cl.party_query('Jabil") OR party:("x')

    def test_default_window_is_five_years_before_today(self):
        import datetime
        self.assertEqual(cl.default_filed_after(datetime.date(2026, 10, 22)), "2021-10-22")
        self.assertEqual(cl.default_filed_after(datetime.date(2028, 2, 29)), "2023-02-28")
        with self.assertRaises(ValueError):
            cl.check_date("22/10/2021")


class CaptionRuleTests(unittest.TestCase):
    def test_delivery_rows_reproduce(self):
        # Delivery Subject 1 table: row 1 defendant, row 5 other, row 9 plaintiff.
        self.assertEqual(cl.caption_role(RECORD_D1["caseName"], "Jabil Inc."), ("defendant", ""))
        self.assertEqual(cl.caption_role(RECORD_D5["caseName"], "Jabil Inc."),
                         ("other", "a listed party on neither side of the caption"))
        self.assertEqual(cl.caption_role(RECORD_D9["caseName"], "Jabil Inc."), ("plaintiff", ""))

    def test_no_versus_in_caption(self):
        self.assertEqual(cl.caption_role("In re Jabil Inc.", "Jabil Inc."), ("other", "no ' v. ' in the caption"))

    def test_status_and_shown(self):
        self.assertEqual(cl.status_text(RECORD_D1), "open")
        self.assertEqual(cl.status_text({"dateTerminated": "2024-08-19"}), "2024-08-19")
        self.assertEqual(cl.shown(""), "not shown")
        self.assertEqual(cl.shown(None), "not shown")
        self.assertEqual(cl.shown("110 Insurance"), "110 Insurance")


class SectionTests(unittest.TestCase):
    def setUp(self):
        self.body = envelope([RECORD_D1, RECORD_D5, RECORD_D9], count=15)
        self.searches = [("Jabil Inc.", "exact name", capture(Q1_URL, self.body))]

    def test_searches_cases_totals_then_sources(self):
        lines = cl.render_section("Jabil Inc.", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, self.searches, 10)
        text = "\n".join(lines)
        self.assertEqual(lines[0], "## Subject: Jabil Inc.")
        self.assertIn(cl.SCOPE_LINE, text)
        self.assertIn('- Variant (exact name): "Jabil Inc." — query: type=d, q=party:("Jabil Inc."), filed_after=2021-10-22, order_by=dateFiled desc — result count in the window: 15 — first page holds 3 results — retrieved ' + RETRIEVED, text)
        self.assertIn("| 1 | 0:26-cv-03269 | District Court, D. Minnesota | Andresen v. Jabil, Inc. | 2026-07-10 | not shown | not shown | defendant | open | 73603835 |", text)
        self.assertIn("| 2 | 1:25-cv-00242 | District Court, D. Colorado | Allstate Vehicle and Property Insurance Company v. Whirlpool Corporation | 2025-01-24 | 110 Insurance | 28:1332 Diversity-Product Liability | other (a listed party on neither side of the caption) | open | 69574962 |", text)
        self.assertIn("| 3 | 23-13436 | Court of Appeals for the Eleventh Circuit | Jabil, Inc. v. GE | 2023-10-12 | 4190 Other Contract Actions | not shown | plaintiff | open | 68113338 |", text)
        self.assertIn("- As plaintiff: rows 3 = 1.", text)
        self.assertIn("- As defendant: rows 1 = 1.", text)
        self.assertIn("- As other: rows 2 = 1.", text)
        self.assertIn("- Role arithmetic: 1 + 1 + 1 = 3 listed cases.", text)
        self.assertIn("- Status arithmetic: 3 + 0 = 3 listed cases.", text)
        self.assertIn("- Total count found in the window (first variant's party search, as returned by the API): 15.", text)
        link = lines.index("- Query URL: " + Q1_URL)
        self.assertLess(lines.index("### Totals"), link)
        self.assertEqual(lines[link + 1], "- Retrieved (UTC): " + RETRIEVED)
        self.assertTrue(lines[link + 2].startswith("Excerpt ("))
        self.assertEqual(lines[link + 3], "```")
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], self.body)

    def test_list_count_limits_rows(self):
        lines = cl.render_section("Jabil Inc.", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, self.searches, 2)
        text = "\n".join(lines)
        self.assertIn("The first 2 of 3 results on the first page", text)
        self.assertIn("| 2 | 1:25-cv-00242", text)
        self.assertNotIn("| 3 | 23-13436", text)
        self.assertIn("- Listed cases: 2.", text)

    def test_exclusion_listed_with_reason_and_refused_when_absent(self):
        reason = "the subject is a listed party but on neither side of the caption"
        lines = cl.render_section("Jabil Inc.", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, self.searches, 10,
                                  exclusions={"69574962": reason})
        text = "\n".join(lines)
        self.assertIn("- Listed cases: 2.", text)
        self.assertIn("Checked and excluded: 1 result among the listed results is shown below", text)
        self.assertIn("- Docket ID 69574962 checked and excluded because: " + reason, text)
        self.assertLess(text.index("| 2 | 23-13436"), text.index("Checked and excluded:"))
        with self.assertRaises(ValueError):
            cl.render_section("x", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, self.searches, 10, exclusions={"1": "no"})

    def test_recorded_head_with_cursor_is_reported(self):
        body = close_search_head(Q5_TEXT)
        searches = [("Raymond James Financial", "name without suffix", capture(cl.search_url("Raymond James Financial", FILED_AFTER), body, retrieved="2026-10-22T23:08:53Z"))]
        text = "\n".join(cl.render_section("Raymond James Financial, Inc.", ["Raymond James Financial"], FILED_AFTER, cl.DEFAULT_ORDER, searches, 10))
        self.assertIn("result count in the window: 27 — first page holds 1 result; a next page cursor was returned and not followed — retrieved 2026-10-22T23:08:53Z", text)
        self.assertIn("| 1 | 7:26-cv-00830 | District Court, N.D. Alabama | Norris v. Raymond James Financial Services, Inc. | 2026-05-15 | not shown | not shown | defendant | open | 73354392 |", text)

    def test_empty_result_is_proven_by_transcript(self):
        body = envelope([], count=0)
        searches = [("Zzz Qqq", "exact name", capture(cl.search_url("Zzz Qqq", FILED_AFTER), body))]
        lines = cl.render_section("Zzz Qqq", ["Zzz Qqq"], FILED_AFTER, cl.DEFAULT_ORDER, searches, 10)
        text = "\n".join(lines)
        self.assertIn("result count in the window: 0 — first page holds 0 results; the results array is empty and the complete raw transcript is in the Sources section", text)
        self.assertIn("No cases listed.", text)
        self.assertIn("- Listed cases: 0.", text)
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], body)

    def test_http_error_and_non_json_are_not_empty_results(self):
        searches = [("Jabil Inc.", "exact name", capture(Q1_URL, "<html>throttled</html>", status_line="HTTP/1.1 429 Too Many Requests"))]
        text = "\n".join(cl.render_section("Jabil Inc.", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, searches, 10))
        self.assertIn("HTTP status 429 Too Many Requests, not 200; the count is not determinable from this response", text)
        self.assertIn("No cases are listed: the first variant's search did not return a usable response", text)
        self.assertIn("<html>throttled</html>", text)
        self.assertNotIn("result count in the window: 0", text)
        searches = [("Jabil Inc.", "exact name", capture(Q1_URL, "[]"))]
        text = "\n".join(cl.render_section("Jabil Inc.", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, searches, 10))
        self.assertIn("the response is not the expected JSON object", text)
        self.assertNotIn("result count in the window: 0", text)

    def test_docket_detail_sources_follow_search_sources(self):
        dockets = [("73603835", capture(cl.docket_url("73603835"), envelope([RECORD_D1], count=1), retrieved="2026-10-22T23:08:23Z"))]
        lines = cl.render_section("Jabil Inc.", ["Jabil Inc."], FILED_AFTER, cl.DEFAULT_ORDER, self.searches, 10, docket_captures=dockets)
        text = "\n".join(lines)
        self.assertIn('### Source. Q1. CourtListener RECAP docket search, Jabil Inc., exact name variant "Jabil Inc."', text)
        self.assertIn("### Source. D1. CourtListener RECAP docket record, Jabil Inc., docket ID 73603835", text)
        self.assertLess(text.index("### Source. Q1."), text.index("### Source. D1."))
        self.assertIn("- Query URL: " + cl.docket_url("73603835"), text)


class _Handler(http.server.BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        status, body = self.routes.get(self.path, (404, b"not found"))
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Test-Order", "second")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


LIVE_SEARCH_URL = "https://www.courtlistener.com/api/rest/v4/search/"


class FetchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%d/search/" % cls.server.server_port
        os.environ["no_proxy"] = "127.0.0.1,localhost"
        os.environ["NO_PROXY"] = "127.0.0.1,localhost"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _path(self, url):
        return url[url.index("/search/"):]

    def test_transcript_shape_and_header_order(self):
        body = envelope([RECORD_D1], count=1)
        _Handler.routes = {"/search/?a=1": (200, body.encode("utf-8"))}
        cap = cl.fetch(self.base + "?a=1")
        self.assertRegex(cap.retrieved, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertTrue(cap.status_ok)
        lines = cap.transcript.split("\n")
        self.assertEqual(lines[0], "HTTP/1.0 200 OK")
        self.assertTrue(lines[1].startswith("Server: "))
        self.assertLess(lines.index("Content-Type: application/json"), lines.index("X-Test-Order: second"))
        self.assertEqual(lines[-2], "")
        self.assertEqual(lines[-1], body)

    def test_http_error_is_captured_not_raised(self):
        _Handler.routes = {"/search/?e=1": (500, b"{}")}
        cap = cl.fetch(self.base + "?e=1")
        self.assertFalse(cap.status_ok)
        self.assertTrue(cap.transcript.startswith("HTTP/1.0 500 Internal Server Error"))

    def test_token_never_appears_in_transcript(self):
        _Handler.routes = {"/search/?t=1": (200, b"{}")}
        cap = cl.fetch(self.base + "?t=1", token="not-a-real-token-value")
        self.assertNotIn("not-a-real-token-value", cap.transcript)

    def _run_main(self, argv, env_token=None):
        cl.SEARCH_URL = self.base
        saved = os.environ.pop(cl.TOKEN_ENV, None)
        if env_token:
            os.environ[cl.TOKEN_ENV] = env_token
        out, err = io.StringIO(), io.StringIO()
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            code = cl.main(argv)
        finally:
            sys.stdout, sys.stderr = stdout, stderr
            cl.SEARCH_URL = LIVE_SEARCH_URL
            os.environ.pop(cl.TOKEN_ENV, None)
            if saved is not None:
                os.environ[cl.TOKEN_ENV] = saved
        return code, out.getvalue(), err.getvalue()

    def test_main_end_to_end_two_variants_and_docket_details(self):
        cl.SEARCH_URL = self.base
        try:
            u1 = self._path(cl.search_url("Jabil Inc.", FILED_AFTER))
            u2 = self._path(cl.search_url("Jabil", FILED_AFTER))
            d1 = self._path(cl.docket_url("73603835"))
        finally:
            cl.SEARCH_URL = LIVE_SEARCH_URL
        _Handler.routes = {
            u1: (200, envelope([RECORD_D1], count=15).encode("utf-8")),
            u2: (200, envelope([RECORD_D1, RECORD_D5], count=18).encode("utf-8")),
            d1: (200, envelope([RECORD_D1], count=1).encode("utf-8")),
        }
        code, out, err = self._run_main(["--subject", "Jabil Inc.", "--party", "Jabil Inc.", "--party", "Jabil",
                                         "--filed-after", FILED_AFTER, "--docket-details"], env_token="not-a-real-token-value")
        self.assertEqual(code, 0, err)
        self.assertTrue(out.startswith("## Subject: Jabil Inc.\n"))
        self.assertIn('- Variant (exact name): "Jabil Inc."', out)
        self.assertIn('- Variant (name without suffix): "Jabil"', out)
        self.assertIn("result count in the window: 15", out)
        self.assertIn("result count in the window: 18", out)
        self.assertIn("| 1 | 0:26-cv-03269 |", out)
        self.assertIn("### Source. D1. CourtListener RECAP docket record, Jabil Inc., docket ID 73603835", out)
        self.assertEqual(out.count("HTTP/1.0 200 OK"), 3)
        self.assertNotIn("not-a-real-token-value", out)

    def test_main_transport_failure_prints_nothing(self):
        self.server.shutdown()
        self.server.server_close()
        try:
            code, out, err = self._run_main(["--party", "Jabil Inc.", "--filed-after", FILED_AFTER])
        finally:
            type(self).server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
            type(self).thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            type(self).base = "http://127.0.0.1:%d/search/" % self.server.server_port
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("fetch failed, nothing printed", err)

    def test_main_argument_rules(self):
        from contextlib import redirect_stderr
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                cl.main([])
            with self.assertRaises(SystemExit):
                cl.main(["--party", "Jabil Inc.", "--filed-after", "22/10/2021"])
            with self.assertRaises(SystemExit):
                cl.main(["--party", "Jabil Inc.", "--exclude", "abc=reason"])


if __name__ == "__main__":
    unittest.main()
