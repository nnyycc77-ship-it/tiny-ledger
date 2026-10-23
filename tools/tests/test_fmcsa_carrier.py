"""Tests for tools/fmcsa_carrier.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_fmcsa_carrier.py' -v

The fixtures are not invented. Every source text below is copied
verbatim from the published carrier vetting delivery
deliveries/carrier-vetting-3b4e7143-c7e2-4fda-92f4-c19a99bbd98f.md,
which records for each source the exact query URL (or form fields) and
the UTC retrieval time. The delivery line range of each excerpt is given
beside it. Two things in these tests are not recordings and are labelled
as such: (1) the delivery prints the Census JSON excerpt without the
object braces, so CENSUS_BODY_2046 adds "{" and "}" around the recorded
key/value lines to make the recorded response parse, values unchanged;
(2) no HTML of the SAFER or Licensing and Insurance pages was recorded,
only their text, so the HTML parser is exercised on a test harness that
wraps each recorded text line in a table row. The fetch tests use a
local HTTP server on 127.0.0.1 and nothing else.
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
import fmcsa_carrier as fc  # noqa: E402

RETRIEVED = "2026-10-22T21:34:25Z"  # SAFER retrieval time recorded for USDOT 2046 (S2 to S8)

# Delivery source S1, FMCSA Company Census File record, USDOT 2046,
# delivery lines 447 to 467 verbatim. Recorded URL:
# https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=2046&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef
# Recorded: Retrieved: 2026-10-22T21:37:45Z
CENSUS_EXCERPT_2046 = """[
  "dot_number": "2046",
  "legal_name": "GARDA CL CENTRAL INC",
  "phy_city": "BOCA RATON",
  "phy_state": "FL",
  "power_units": "137",
  "total_drivers": "84",
  "docket1prefix": "MC",
  "docket1": "65419",
  "docket1_status_code": "A",
  "safety_rating": "S",
  "safety_rating_date": "20220817",
  "mcs150_mileage": "1420000",
  "mcs150_mileage_year": "2026",
  "mcs150_date": "20260601",
  "business_org_desc": "CORPORATION",
  "carship": "C",
  "carrier_operation": "A",
  "status_code": "A",
  "classdef": "AUTHORIZED FOR HIRE"
]"""

# Delivery source S2, SAFER Company Snapshot, ID/Operations and operating
# authority, USDOT 2046, delivery lines 475 to 499 verbatim.
SAFER_S2_TEXT = """USDOT INFORMATION
Entity Type:
CARRIER
New Entrant Status:
(Active)
-->
USDOT Status:
ACTIVE
Out of Service Date:
None
USDOT Number:
2046
State Carrier ID Number:
MCS-150 Form Date:
06/01/2026
MCS-150 Mileage (Year):
1,420,000 (2026)
OPERATING AUTHORITY INFORMATION
Operating Authority Status:
AUTHORIZED FOR:
Motor Carrier of Property (Except Household Goods)
For Licensing and Insurance details
click here.
MC/MX/FF Number(s):
MC-65419"""

# Delivery source S3, SAFER Company Snapshot, company information,
# USDOT 2046, delivery lines 507 to 526 verbatim.
SAFER_S3_TEXT = """COMPANY INFORMATION
Legal Name:
GARDA CL CENTRAL INC
DBA Name:
Physical Address:
2000 NW CORPORATE BLVD
BOCA RATON, FL   33431-7304
Phone:
(561) 939-7000
Mailing Address:
2000 NW CORPORATE BLVD
BOCA RATON, FL   33431-7304
DUNS Number:
45-734-852
Power Units:
68
Non-CMV Units:
69
Drivers:
84"""

# Delivery source S8, SAFER Company Snapshot, safety rating, USDOT 2046,
# delivery lines 639 to 651 verbatim.
SAFER_S8_TEXT = """Carrier Safety Rating:
The rating below is current as of:
10/20/2026
Review Information:
Review Information
Rating Date:
08/17/2022
Review Date:
08/10/2022
Rating:
Satisfactory
Type:
Compliance Review"""

# Delivery source S35, SAFER Company Snapshot, safety rating, USDOT 89741
# (a carrier SAFER shows as not rated), delivery lines 1336 to 1348 verbatim.
SAFER_S35_TEXT = """Carrier Safety Rating:
The rating below is current as of:
10/20/2026
Review Information:
Review Information
Rating Date:
None
Review Date:
02/03/2010
Rating:
None
Type:
Non-Ratable"""

# Delivery source S9, FMCSA Licensing and Insurance record, USDOT 2046,
# delivery lines 659 to 672 verbatim.
LI_S9_TEXT = """US DOT: 2046
Docket Number: MC00065419
Legal Name: GARDA CL CENTRAL, INC
Authority Type | Authority Status | Application Pending
Common | ACTIVE | NO
Contract | ACTIVE | NO
Broker | NONE | NO
Insurance Type | Insurance Required | Insurance on File
BIPD | $750,000 | $5,000,000
Cargo | NO | YES
Bond | NO | NO
Form | Type | Insurance Carrier | Policy/Surety | Posted Date | Coverage From | Coverage To | Effective Date | Cancellation Date
91X | BIPD/Primary | NATIONAL UNION FIRE INS. CO. OF PITSBGH. PA | 2867428 | 03/16/2022 | $0 | $5,000,000 | 06/15/2021 | 
34 | CARGO | FIREMAN'S FUND INSURANCE CO. | MZI98309514 | 11/06/2008 | $0 | $5,000* | 05/31/2008 | """

# The recorded excerpt wrapped in the object braces the delivery omitted,
# so that it parses as the JSON array of one object the API returns.
# Values unchanged. This is a repair of the excerpt's punctuation, not
# a recording.
CENSUS_BODY_2046 = "[{" + CENSUS_EXCERPT_2046[1:-1].rstrip().rstrip(",") + "}]"
CENSUS_RECORD_2046 = json.loads(CENSUS_BODY_2046)[0]


def harness_html(text):
    """Test harness only: each recorded text line becomes one table row.
    Not a recording of any FMCSA page's HTML."""
    rows = "".join("<tr><td>%s</td></tr>" % line for line in text.split("\n"))
    return "<html><head><title>t</title><script>var x = 'skip me';</script></head><body><table>%s</table></body></html>" % rows


def capture(url, body, status_line="HTTP/1.1 200 OK", retrieved=RETRIEVED):
    """A Capture with a plain test header. The headers are not a recording."""
    return fc.Capture(url, retrieved, status_line, ["Content-Type: text/plain"], body, "utf-8")


def last_fenced(lines):
    """The text inside the last fenced block of a rendered section."""
    fence_end = len(lines) - 1 - lines[::-1].index("```")
    fence_start = len(lines) - 1 - lines[:fence_end][::-1].index("```") - (len(lines) - fence_end)
    return "\n".join(lines[fence_start + 1:fence_end])


class FixtureTests(unittest.TestCase):
    def test_census_fixture_is_the_recorded_record(self):
        self.assertEqual(CENSUS_RECORD_2046["dot_number"], "2046")
        self.assertEqual(CENSUS_RECORD_2046["legal_name"], "GARDA CL CENTRAL INC")
        self.assertEqual(CENSUS_RECORD_2046["power_units"], "137")
        self.assertEqual(CENSUS_RECORD_2046["classdef"], "AUTHORIZED FOR HIRE")
        self.assertNotIn("dba_name", CENSUS_RECORD_2046)
        # Every key is one the recorded $select asked for.
        self.assertTrue(set(CENSUS_RECORD_2046) <= set(fc.CENSUS_FIELDS))

    def test_safer_fixtures_hold_the_recorded_values(self):
        self.assertIn("USDOT Status:\nACTIVE", SAFER_S2_TEXT)
        self.assertIn("Power Units:\n68", SAFER_S3_TEXT)
        self.assertIn("Rating:\nSatisfactory", SAFER_S8_TEXT)
        self.assertIn("Rating:\nNone", SAFER_S35_TEXT)
        self.assertIn("US DOT: 2046", LI_S9_TEXT)


class QueryBuildingTests(unittest.TestCase):
    def test_census_url_matches_recorded_delivery_url(self):
        self.assertEqual(
            fc.census_record_url("2046"),
            "https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=2046&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef",
        )

    def test_safer_url_matches_recorded_delivery_url(self):
        self.assertEqual(
            fc.safer_url("2046"),
            "https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=2046",
        )

    def test_li_url_uses_recorded_form_fields(self):
        self.assertEqual(
            fc.li_url("2046"),
            "https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=2046&s_prefix=MC&pv_vpath=LIVIEW",
        )

    def test_name_url_encodes_spaces_and_keeps_dollar_and_commas(self):
        url = fc.census_name_url("CHENEY BROTHERS", 50)
        self.assertTrue(url.startswith("https://data.transportation.gov/resource/az4n-8mr2.json?$q=CHENEY%20BROTHERS&$select=dot_number,legal_name,"))
        self.assertTrue(url.endswith("&$limit=50"))

    def test_usdot_must_be_digits(self):
        with self.assertRaises(ValueError):
            fc.census_record_url("20 46")
        with self.assertRaises(ValueError):
            fc.safer_url("2046; drop")
        self.assertEqual(fc.check_usdot(" 2046 "), "2046")

    def test_parse_exclusions(self):
        self.assertEqual(fc.parse_exclusions(['123456="other state"', "7=x"]), {"123456": "other state", "7": "x"})
        with self.assertRaises(ValueError):
            fc.parse_exclusions(["123456"])
        with self.assertRaises(ValueError):
            fc.parse_exclusions(["abc=reason"])


class TextExtractionTests(unittest.TestCase):
    def test_text_lines_keep_recorded_lines_and_skip_script(self):
        lines = fc.text_lines(harness_html(SAFER_S3_TEXT))
        self.assertNotIn("var x = 'skip me';", lines)
        self.assertEqual(lines[0], "t")
        self.assertEqual(lines[1:], SAFER_S3_TEXT.split("\n"))

    def test_inline_markup_does_not_split_a_label(self):
        lines = fc.text_lines("<table><tr><th>USDOT <b>Status:</b></th><td>ACTIVE</td></tr></table>")
        self.assertEqual(lines, ["USDOT Status:", "ACTIVE"])

    def test_inner_spacing_is_kept_including_non_breaking_spaces(self):
        # The recorded SAFER address text carries non-breaking spaces (U+00A0); they are kept as shown.
        lines = fc.text_lines("<p>BOCA RATON, FL \xa0 33431-7304</p><p>A&nbsp;B</p>")
        self.assertEqual(lines, ["BOCA RATON, FL \xa0 33431-7304", "A\xa0B"])

    def test_labelled_values_from_recorded_safer_text(self):
        text = "\n".join([SAFER_S2_TEXT, SAFER_S3_TEXT, SAFER_S8_TEXT])
        found = fc.labelled_values(fc.text_lines(harness_html(text)), fc.SAFER_LABELS,
                                   fc.SAFER_MULTILINE, fc.SAFER_STOP_PREFIXES)
        self.assertEqual(found["Entity Type:"], ["CARRIER"])
        self.assertEqual(found["USDOT Status:"], ["ACTIVE"])
        self.assertEqual(found["Out of Service Date:"], ["None"])
        self.assertEqual(found["USDOT Number:"], ["2046"])
        self.assertEqual(found["MCS-150 Form Date:"], ["06/01/2026"])
        self.assertEqual(found["MCS-150 Mileage (Year):"], ["1,420,000 (2026)"])
        self.assertEqual(found["Operating Authority Status:"],
                         ["AUTHORIZED FOR:", "Motor Carrier of Property (Except Household Goods)"])
        self.assertEqual(found["MC/MX/FF Number(s):"], ["MC-65419"])
        self.assertEqual(found["Legal Name:"], ["GARDA CL CENTRAL INC"])
        self.assertEqual(found["DBA Name:"], [])  # blank in the source: next line is the next label
        self.assertEqual(found["Physical Address:"], ["2000 NW CORPORATE BLVD", "BOCA RATON, FL \xa0 33431-7304"])
        self.assertEqual(found["Phone:"], ["(561) 939-7000"])
        self.assertEqual(found["Power Units:"], ["68"])
        self.assertEqual(found["Non-CMV Units:"], ["69"])
        self.assertEqual(found["Drivers:"], ["84"])
        self.assertEqual(found["Rating Date:"], ["08/17/2022"])
        self.assertEqual(found["Review Date:"], ["08/10/2022"])
        self.assertEqual(found["Rating:"], ["Satisfactory"])
        self.assertIsNone(found["Total Inspections:"])  # S5 text not included in this harness

    def test_not_rated_carrier_shows_source_none_not_a_rating(self):
        found = fc.labelled_values(fc.text_lines(harness_html(SAFER_S35_TEXT)), fc.SAFER_LABELS,
                                   fc.SAFER_MULTILINE, fc.SAFER_STOP_PREFIXES)
        self.assertEqual(found["Rating:"], ["None"])
        self.assertEqual(found["Rating Date:"], ["None"])
        self.assertEqual(found["Review Date:"], ["02/03/2010"])

    def test_value_text(self):
        self.assertEqual(fc.value_text(None), "label not found in the response text")
        self.assertEqual(fc.value_text([]), "none shown (blank in the source)")
        self.assertEqual(fc.value_text(["AUTHORIZED FOR:", "Motor Carrier of Property (Except Household Goods)"]),
                         "AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods)")


class CensusSectionTests(unittest.TestCase):
    def test_record_fields_as_shown_and_absent_fields_marked(self):
        cap = capture(fc.census_record_url("2046"), CENSUS_BODY_2046, retrieved="2026-10-22T21:37:45Z")
        lines = fc.census_section("2046", cap)
        text = "\n".join(lines)
        self.assertIn("QUERY: dot_number = 2046 returned 1 record (retrieved 2026-10-22T21:37:45Z).", text)
        self.assertIn("- legal_name as shown: GARDA CL CENTRAL INC", text)
        self.assertIn("- power_units as shown: 137", text)
        self.assertIn("- dba_name: not present in the record", text)
        self.assertIn("- classdef as shown: AUTHORIZED FOR HIRE", text)
        # Field order follows the $select list.
        self.assertLess(text.index("- dot_number as shown"), text.index("- legal_name as shown"))
        # Source link, then the transcript directly beneath; the body is the last fenced line.
        link = lines.index("- Query URL: " + cap.url)
        self.assertEqual(lines[link + 1], "- Retrieved (UTC): 2026-10-22T21:37:45Z")
        self.assertTrue(lines[link + 2].startswith("Excerpt ("))
        self.assertEqual(lines[link + 3], "```")
        self.assertEqual(last_fenced(lines), cap.transcript)
        self.assertTrue(cap.transcript.endswith("\n\n" + CENSUS_BODY_2046))
        self.assertLess(lines.index("- legal_name as shown: GARDA CL CENTRAL INC"), link)

    def test_empty_array_is_proven_by_transcript(self):
        cap = capture(fc.census_record_url("1"), "[]")
        lines = fc.census_section("1", cap)
        text = "\n".join(lines)
        self.assertIn("QUERY: dot_number = 1 returned 0 records (retrieved %s). The response body was an empty array" % RETRIEVED, text)
        self.assertNotIn("as shown:", text)
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], "[]")

    def test_http_error_status_is_not_an_empty_result(self):
        cap = capture(fc.census_record_url("2046"), "<html>denied</html>", status_line="HTTP/1.1 403 Forbidden")
        text = "\n".join(fc.census_section("2046", cap))
        self.assertIn("returned HTTP status 403 Forbidden, not 200", text)
        self.assertIn("not determinable from this response", text)
        self.assertIn("<html>denied</html>", text)
        self.assertNotIn("returned 0 records", text)

    def test_non_json_body_is_not_an_empty_result(self):
        cap = capture(fc.census_record_url("2046"), "<html>maintenance</html>")
        text = "\n".join(fc.census_section("2046", cap))
        self.assertIn("did not return a JSON array of objects", text)
        self.assertNotIn("returned 0 records", text)


class SaferSectionTests(unittest.TestCase):
    def test_claim_lines_then_link_then_full_page(self):
        html = harness_html("\n".join([SAFER_S2_TEXT, SAFER_S3_TEXT, SAFER_S8_TEXT]))
        cap = capture(fc.safer_url("2046"), html)
        lines = fc.safer_section("2046", cap)
        text = "\n".join(lines)
        self.assertIn("QUERY: query_param = USDOT, query_string = 2046 (retrieved %s). 18 of 19 labelled fields were found" % RETRIEVED, text)
        self.assertIn("- USDOT Status: ACTIVE", text)
        self.assertIn("- DBA Name: none shown (blank in the source)", text)
        self.assertIn("- Operating Authority Status: AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods)", text)
        self.assertIn("- Physical Address: 2000 NW CORPORATE BLVD BOCA RATON, FL \xa0 33431-7304", text)
        self.assertIn("- Total Inspections: label not found in the response text", text)
        self.assertIn("- Rating: Satisfactory", text)
        link = lines.index("- Query URL: " + cap.url)
        self.assertLess(lines.index("- USDOT Status: ACTIVE"), link)
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], html)

    def test_page_without_labels_claims_nothing(self):
        cap = capture(fc.safer_url("2046"), "<html><body><p>Please wait</p></body></html>")
        text = "\n".join(fc.safer_section("2046", cap))
        self.assertIn("0 of 19 labelled fields were found", text)
        self.assertIn("no carrier field is claimed from it", text)
        self.assertIn("- Legal Name: label not found in the response text", text)


class LiSectionTests(unittest.TestCase):
    def test_record_lines_found(self):
        cap = capture(fc.li_url("2046"), harness_html(LI_S9_TEXT))
        text = "\n".join(fc.li_section("2046", cap))
        self.assertIn("QUERY: n_dotno = 2046, s_prefix = MC, pv_vpath = LIVIEW (retrieved %s). 3 record text lines found." % RETRIEVED, text)
        self.assertIn("- As shown: US DOT: 2046", text)
        self.assertIn("- As shown: Docket Number: MC00065419", text)
        self.assertIn("- As shown: Legal Name: GARDA CL CENTRAL, INC", text)
        self.assertIn("Common | ACTIVE | NO", text)  # in the raw excerpt

    def test_challenge_page_claims_nothing(self):
        cap = capture(fc.li_url("2046"), "<html><body><p>Checking your browser</p></body></html>")
        text = "\n".join(fc.li_section("2046", cap))
        self.assertIn("0 record text lines found.", text)
        self.assertIn("No Licensing and Insurance record fields were found in the response text.", text)
        self.assertIn("Nothing is claimed from this response.", text)
        self.assertIn("Checking your browser", text)


class NameSearchTests(unittest.TestCase):
    def test_candidates_and_exclusion(self):
        other = dict(CENSUS_RECORD_2046)
        other["dot_number"] = "999999"  # test construction: a second record to exclude; not a recording
        body = json.dumps([CENSUS_RECORD_2046, other])
        cap = capture(fc.census_name_url("GARDA", 50), body)
        lines = fc.name_search_section("GARDA", cap, {"999999": "test exclusion reason"})
        text = "\n".join(lines)
        self.assertIn('QUERY: $q = "GARDA" returned 2 records', text)
        self.assertIn("CANDIDATES: 1 record.", text)
        self.assertIn("Checked and excluded: 1 record in the same response is listed below", text)
        self.assertIn("- Checked and excluded because: test exclusion reason", text)
        self.assertLess(text.index("Candidate 1 of 1:"), text.index("Checked and excluded:"))
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], body)

    def test_exclusion_not_in_response_is_refused(self):
        cap = capture(fc.census_name_url("GARDA", 50), CENSUS_BODY_2046)
        with self.assertRaises(ValueError):
            fc.name_search_section("GARDA", cap, {"1": "not here"})

    def test_empty_search_is_proven(self):
        cap = capture(fc.census_name_url("ZZZ", 50), "[]")
        text = "\n".join(fc.name_search_section("ZZZ", cap))
        self.assertIn('QUERY: $q = "ZZZ" returned 0 records', text)
        self.assertIn("The response body was an empty array", text)


class _Handler(http.server.BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        status, body = self.routes.get(self.path.split("?")[0], (404, b"not found"))
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("X-Test-Order", "second")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class FetchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%d" % cls.server.server_port
        os.environ["no_proxy"] = "127.0.0.1,localhost"
        os.environ["NO_PROXY"] = "127.0.0.1,localhost"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_transcript_shape_and_header_order(self):
        _Handler.routes = {"/census": (200, CENSUS_BODY_2046.encode("utf-8"))}
        cap = fc.fetch(self.base + "/census?dot_number=2046")
        self.assertRegex(cap.retrieved, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertTrue(cap.status_ok)
        lines = cap.transcript.split("\n")
        self.assertEqual(lines[0], "HTTP/1.0 200 OK")
        self.assertTrue(lines[1].startswith("Server: "))
        self.assertLess(lines.index("Content-Type: text/plain"), lines.index("X-Test-Order: second"))
        self.assertTrue(cap.transcript.endswith("\n\n" + CENSUS_BODY_2046))
        self.assertEqual(cap.body, CENSUS_BODY_2046)
        self.assertEqual(cap.decoding, "utf-8")

    def test_http_error_is_captured_not_raised(self):
        _Handler.routes = {"/x": (500, b"[]")}
        cap = fc.fetch(self.base + "/x")
        self.assertFalse(cap.status_ok)
        self.assertTrue(cap.transcript.startswith("HTTP/1.0 500 Internal Server Error"))

    def test_non_utf8_body_falls_back_to_latin1_without_loss(self):
        _Handler.routes = {"/l": (200, b"carrier\x92s page")}
        cap = fc.fetch(self.base + "/l")
        self.assertEqual(cap.body, "carrier\x92s page")
        self.assertTrue(cap.decoding.startswith("latin-1"))

    def _run_main(self, argv):
        originals = (fc.CENSUS_URL, fc.SAFER_URL, fc.LI_URL)
        fc.CENSUS_URL, fc.SAFER_URL, fc.LI_URL = (self.base + "/census", self.base + "/safer", self.base + "/li")
        out, err = io.StringIO(), io.StringIO()
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            code = fc.main(argv)
        finally:
            sys.stdout, sys.stderr = stdout, stderr
            fc.CENSUS_URL, fc.SAFER_URL, fc.LI_URL = originals
        return code, out.getvalue(), err.getvalue()

    def test_main_end_to_end_three_sources(self):
        _Handler.routes = {
            "/census": (200, CENSUS_BODY_2046.encode("utf-8")),
            "/safer": (200, harness_html("\n".join([SAFER_S2_TEXT, SAFER_S3_TEXT, SAFER_S8_TEXT])).encode("utf-8")),
            "/li": (200, b"<html><body><p>Checking your browser</p></body></html>"),
        }
        code, out, err = self._run_main(["--subject", "GARDA CL CENTRAL INC", "--usdot", "2046"])
        self.assertEqual(code, 0, err)
        self.assertTrue(out.startswith("## Carrier: GARDA CL CENTRAL INC\n"))
        self.assertIn("### Census record", out)
        self.assertIn("### SAFER Company Snapshot", out)
        self.assertIn("### Licensing and Insurance", out)
        self.assertIn("- legal_name as shown: GARDA CL CENTRAL INC", out)
        self.assertIn("- Power Units: 68", out)
        self.assertIn("Nothing is claimed from this response.", out)
        self.assertIn("- Query URL: " + self.base + "/census?dot_number=2046&$select=", out)
        self.assertIn("- Query URL: " + self.base + "/safer?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=2046", out)
        self.assertIn("- Query URL: " + self.base + "/li?n_dotno=2046&s_prefix=MC&pv_vpath=LIVIEW", out)
        self.assertEqual(out.count("HTTP/1.0 200 OK"), 3)
        self.assertLess(out.index("### Census record"), out.index("### SAFER Company Snapshot"))
        self.assertLess(out.index("### SAFER Company Snapshot"), out.index("### Licensing and Insurance"))

    def test_main_source_selection_and_order(self):
        _Handler.routes = {"/census": (200, CENSUS_BODY_2046.encode("utf-8")),
                           "/safer": (200, b"<html></html>")}
        code, out, _ = self._run_main(["--usdot", "2046", "--source", "safer", "--source", "census"])
        self.assertEqual(code, 0)
        self.assertNotIn("### Licensing and Insurance", out)
        self.assertLess(out.index("### SAFER Company Snapshot"), out.index("### Census record"))

    def test_main_transport_failure_prints_nothing(self):
        self.server.shutdown()
        self.server.server_close()
        try:
            code, out, err = self._run_main(["--usdot", "2046"])
        finally:
            type(self).server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
            type(self).thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            type(self).base = "http://127.0.0.1:%d" % self.server.server_port
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("fetch failed, nothing printed", err)

    def test_main_argument_rules(self):
        with self.assertRaises(SystemExit):
            fc.main([])
        with self.assertRaises(SystemExit):
            fc.main(["--usdot", "1", "--name", "x"])
        with self.assertRaises(SystemExit):
            fc.main(["--usdot", "1", "--exclude", "2=reason"])
        with self.assertRaises(SystemExit):
            fc.main(["--usdot", "abc"])


if __name__ == "__main__":
    unittest.main()
