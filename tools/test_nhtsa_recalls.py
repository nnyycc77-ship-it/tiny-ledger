"""Tests for tools/nhtsa_recalls.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools -v

The fixtures are not invented. Every response text below is copied
verbatim from the published delivery
deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md,
source S24, which records the source, the exact query URL
(https://api.nhtsa.gov/recalls/recallsByVehicle?make=Hyundai&model=Elantra&modelYear=2021)
and the UTC retrieval time (2026-10-22T11:48:10Z). S24_HEAD is the
published head excerpt: the opening of the response object through the
first campaign, exactly as printed there; the tests close it
syntactically where the excerpt ends. CAMPAIGN_21V302000 is the
published excerpt for campaign 3 of 6. The response envelope shape
("Count", "Message", "results") comes from that same excerpt. No HTTP
headers from api.nhtsa.gov were recorded in the delivery, so the
transcripts used here carry a plain test status line and header, and
the fetch test uses a local HTTP server on 127.0.0.1 and nothing else.
"""

import http.server
import io
import json
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nhtsa_recalls as nr  # noqa: E402

# Delivery source S24, "Excerpt (Response head and campaign 1 of 6, in
# response order)", verbatim: delivery lines 1194 to 1213.
S24_HEAD = r"""{
  "Count": 6,
  "Message": "Results returned successfully",
  "results": [
    {
      "Manufacturer": "Hyundai Motor America",
      "NHTSACampaignNumber": "21V796000",
      "parkIt": false,
      "parkOutSide": false,
      "overTheAirUpdate": false,
      "ReportReceivedDate": "13/10/2021",
      "Component": "SEAT BELTS:FRONT",
      "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2021 Elantra, Elantra HEV, Venue, Genesis GV80 and 2022 Genesis GV70 vehicles.  In the event of a crash, the front driver-side and/or passenger-side seat belt pretensioner(s) may explode upon deployment.",
      "Consequence": "An exploding seat belt pretensioner could project metal fragments into the vehicle, striking vehicle occupants and resulting in injury.",
      "Remedy": "Dealers will replace the seat belt pretensioners, free of charge.  Owner notification letters were mailed February 10, 2022. Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's numbers for this recall are 211 and 009G.  This recall is replaced by NHTSA recall numbers 22V-354 for Elantra and Elantra HEV vehicles, 22V-458 for Venue vehicles, and 23V-094 for Genesis vehicles.  Elantra, Elantra HEV, Venue, and Genesis vehicles already repaired under this recall will need to have the new remedies completed.",
      "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.nhtsa.gov.",
      "ModelYear": "2021",
      "Make": "HYUNDAI",
      "Model": "ELANTRA"
    },"""

# Delivery source S24, "Excerpt (Campaign 3 of 6, in response order)",
# verbatim: delivery lines 1236 to 1251.
CAMPAIGN_21V302000_TEXT = r"""{
  "Manufacturer": "Hyundai Motor America",
  "NHTSACampaignNumber": "21V302000",
  "parkIt": false,
  "parkOutSide": false,
  "overTheAirUpdate": false,
  "ReportReceivedDate": "28/04/2021",
  "Component": "SEATS:FRONT ASSEMBLY:RECLINER",
  "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2021 Elantra vehicles.  The driver and front passenger seat back recliners may have been improperly welded.",
  "Consequence": "An improperly welded seat back recliner could separate from the seat back frame during a crash, increasing the risk of injury.",
  "Remedy": "Dealers will inspect and if necessary, replace the seat back frame assembly, free of charge.  Owner notification letters were mailed on June 21, 2021.  Owners may contact Hyundai customer service at 1-888-371-9460.  Hyundai's number for this recall is 204.",
  "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.safercar.gov.",
  "ModelYear": "2021",
  "Make": "HYUNDAI",
  "Model": "ELANTRA"
},"""

# The head excerpt closed where it ends: one campaign inside the
# recorded envelope. Its "Count" of 6 is the recorded value and differs
# from the one entry that the excerpt holds, which the tests use to
# check that the tool reports such a difference instead of hiding it.
S24_HEAD_CLOSED = S24_HEAD[:-1] + "\n  ]\n}"
S24_HEAD_DATA = json.loads(S24_HEAD_CLOSED)
CAMPAIGN_21V796000 = S24_HEAD_DATA["results"][0]
CAMPAIGN_21V302000 = json.loads(CAMPAIGN_21V302000_TEXT.rstrip(","))

ELANTRA_PARAMS = [("make", "Hyundai"), ("model", "Elantra"), ("modelYear", "2021")]
ELANTRA_URL = "https://api.nhtsa.gov/recalls/recallsByVehicle?make=Hyundai&model=Elantra&modelYear=2021"
RETRIEVED = "2026-10-22T11:48:10Z"


def envelope(records, count=None):
    """A body in the recorded envelope shape holding the given records.
    Count defaults to the number of records."""
    return json.dumps({
        "Count": len(records) if count is None else count,
        "Message": "Results returned successfully",
        "results": records,
    }, ensure_ascii=False)


def transcript_for(body, status="HTTP/1.1 200 OK"):
    """A test transcript: status line, one header, blank line, body.
    The headers are not a recording of api.nhtsa.gov."""
    return status + "\nContent-Type: application/json\n\n" + body


class FixtureTests(unittest.TestCase):
    def test_fixtures_are_the_recorded_campaigns(self):
        self.assertEqual(S24_HEAD_DATA["Count"], 6)
        self.assertEqual(S24_HEAD_DATA["Message"], "Results returned successfully")
        self.assertEqual(CAMPAIGN_21V796000["NHTSACampaignNumber"], "21V796000")
        self.assertEqual(CAMPAIGN_21V796000["ReportReceivedDate"], "13/10/2021")
        self.assertEqual(CAMPAIGN_21V302000["NHTSACampaignNumber"], "21V302000")
        self.assertEqual(CAMPAIGN_21V302000["Component"], "SEATS:FRONT ASSEMBLY:RECLINER")
        self.assertEqual(
            list(CAMPAIGN_21V302000),
            ["Manufacturer", "NHTSACampaignNumber", "parkIt", "parkOutSide",
             "overTheAirUpdate", "ReportReceivedDate", "Component", "Summary",
             "Consequence", "Remedy", "Notes", "ModelYear", "Make", "Model"],
        )


class QueryBuildingTests(unittest.TestCase):
    def test_url_matches_published_delivery_url(self):
        self.assertEqual(nr.build_url("recallsByVehicle", ELANTRA_PARAMS), ELANTRA_URL)

    def test_spaces_are_percent_encoded(self):
        self.assertEqual(
            nr.build_url("recallsByVehicle", [("make", "Land Rover"), ("model", "Range Rover"), ("modelYear", "2020")]),
            "https://api.nhtsa.gov/recalls/recallsByVehicle?make=Land%20Rover&model=Range%20Rover&modelYear=2020",
        )

    def test_describe_query_matches_delivery_phrasing(self):
        self.assertEqual(nr.describe_query(ELANTRA_PARAMS), "make = Hyundai, model = Elantra, modelYear = 2021")

    def test_database_line_matches_delivery(self):
        self.assertEqual(
            nr.database_line("recallsByVehicle", ELANTRA_PARAMS),
            "Database: NHTSA public recall data (recallsByVehicle API), queried by make, model, and model year.",
        )

    def _args(self, **kw):
        base = dict(make=None, model=None, model_year=None, endpoint=None, param=None)
        base.update(kw)
        return nr.argparse.Namespace(**base)

    def test_build_query_default_endpoint(self):
        endpoint, params = nr.build_query(self._args(make="Hyundai", model="Elantra", model_year="2021"))
        self.assertEqual(endpoint, "recallsByVehicle")
        self.assertEqual(params, ELANTRA_PARAMS)

    def test_build_query_needs_all_three_vehicle_fields(self):
        with self.assertRaises(ValueError):
            nr.build_query(self._args(make="Hyundai", model="Elantra"))
        with self.assertRaises(ValueError):
            nr.build_query(self._args())

    def test_build_query_vehicle_fields_via_param(self):
        endpoint, params = nr.build_query(self._args(param=["make=Hyundai", "model=Elantra", "modelYear=2021"]))
        self.assertEqual((endpoint, params), ("recallsByVehicle", ELANTRA_PARAMS))

    def test_build_query_other_endpoint(self):
        endpoint, params = nr.build_query(self._args(endpoint="other", param=["a=b"]))
        self.assertEqual((endpoint, params), ("other", [("a", "b")]))
        with self.assertRaises(ValueError):
            nr.build_query(self._args(endpoint="other"))
        with self.assertRaises(ValueError):
            nr.build_query(self._args(endpoint="x/y", param=["a=b"]))
        with self.assertRaises(ValueError):
            nr.build_query(self._args(endpoint="other", param=["novalue"]))


class ValueFormattingTests(unittest.TestCase):
    def test_long_date_keeps_shown_value_and_adds_long_form(self):
        self.assertEqual(nr.long_date("28/04/2021"), "28/04/2021 (April 28, 2021)")
        self.assertEqual(nr.long_date("13/10/2021"), "13/10/2021 (October 13, 2021)")
        self.assertEqual(nr.long_date("2021-04-28"), "2021-04-28")
        self.assertEqual(nr.long_date(""), "")

    def test_campaign_key(self):
        self.assertEqual(nr.campaign_key("22v-354000"), "22V354000")
        self.assertEqual(nr.campaign_key(None), "")

    def test_parse_exclusions(self):
        self.assertEqual(
            nr.parse_exclusions(['21V796000="replaced by 22V354000"', "22v-354000=other"]),
            {"21V796000": "replaced by 22V354000", "22V354000": "other"},
        )
        with self.assertRaises(ValueError):
            nr.parse_exclusions(["21V796000"])
        with self.assertRaises(ValueError):
            nr.parse_exclusions(["21V796000="])


class RecordRenderingTests(unittest.TestCase):
    def test_record_block_matches_delivery_subject_lines(self):
        block = nr.render_record(CAMPAIGN_21V302000)
        # These lines appear word for word under Subject 6 of the delivery.
        for expected in [
            "#### Campaign 21V302000",
            "- NHTSA campaign number: 21V302000",
            "- Date as shown (ReportReceivedDate): 28/04/2021 (April 28, 2021)",
            "- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: SEATS:FRONT ASSEMBLY:RECLINER",
            "- Hazard as shown (Consequence): An improperly welded seat back recliner could separate from the seat back frame during a crash, increasing the risk of injury.",
            "- Remedy as shown: " + CAMPAIGN_21V302000["Remedy"],
            "- Units: not shown",
        ]:
            self.assertIn(expected, block)
        self.assertIn("- Manufacturer as shown: Hyundai Motor America", block)
        self.assertIn("- Summary as shown: " + CAMPAIGN_21V302000["Summary"], block)
        self.assertIn("- Flags as shown: parkIt = false; parkOutSide = false; overTheAirUpdate = false", block)
        self.assertEqual(block[0], "#### Campaign 21V302000")

    def test_missing_fields_are_marked_not_invented(self):
        block = nr.render_record({"NHTSACampaignNumber": "99V999000"})
        self.assertIn("- Manufacturer as shown: (not present in the API record)", block)
        self.assertIn("- Date as shown (ReportReceivedDate): (not present in the API record)", block)
        self.assertIn("- Product as shown: (not present in the API record)", block)
        self.assertIn("- Hazard as shown (Consequence): (not present in the API record)", block)
        self.assertIn("- Units: not shown", block)
        self.assertFalse(any(line.startswith("- Flags") for line in block))

    def test_a_unit_field_would_be_shown_not_dropped(self):
        record = dict(CAMPAIGN_21V302000)
        record["PotentialUnitsAffected"] = "1,234"
        block = nr.render_record(record)
        self.assertIn("- Units as shown (PotentialUnitsAffected): 1,234", block)
        self.assertNotIn("- Units: not shown", block)


class EmptyResultTests(unittest.TestCase):
    def setUp(self):
        self.params = [("make", "Zzz"), ("model", "Qqq"), ("modelYear", "2021")]
        self.url = nr.build_url("recallsByVehicle", self.params)
        self.body = envelope([])
        self.transcript = transcript_for(self.body)
        self.lines = nr.render_section("Zzz Qqq 2021", "recallsByVehicle", self.params,
                                       self.url, RETRIEVED, self.transcript, self.body)
        self.text = "\n".join(self.lines)

    def test_query_line_and_none_found(self):
        self.assertIn("QUERY: make = Zzz, model = Qqq, modelYear = 2021 returned 0 campaigns (retrieved %s)." % RETRIEVED, self.text)
        self.assertIn("The results array in the response was empty", self.text)
        self.assertIn("RECALLS: none found for Zzz Qqq 2021.", self.text)
        self.assertNotIn("#### Campaign", self.text)

    def test_full_transcript_printed_directly_beneath_source_link(self):
        link_index = self.lines.index("- Query URL: " + self.url)
        self.assertEqual(self.lines[link_index + 1], "- Retrieved (UTC): " + RETRIEVED)
        self.assertTrue(self.lines[link_index + 2].startswith("Excerpt ("))
        self.assertEqual(self.lines[link_index + 3], "```")
        fence_start = link_index + 3
        fence_end = self.lines.index("```", fence_start + 1)
        self.assertEqual("\n".join(self.lines[fence_start + 1:fence_end]), self.transcript)
        self.assertEqual(self.lines[fence_end - 1], self.body)


class SectionTests(unittest.TestCase):
    def test_two_campaign_section(self):
        body = envelope([CAMPAIGN_21V796000, CAMPAIGN_21V302000])
        lines = nr.render_section("Hyundai Elantra 2021", "recallsByVehicle", ELANTRA_PARAMS,
                                  ELANTRA_URL, RETRIEVED, transcript_for(body), body)
        text = "\n".join(lines)
        self.assertEqual(lines[0], "## Subject: Hyundai Elantra 2021")
        self.assertIn(
            "QUERY: make = Hyundai, model = Elantra, modelYear = 2021 returned 2 campaigns (retrieved %s). "
            "The API shows no unit counts for these campaigns, so units are stated as not shown." % RETRIEVED,
            text,
        )
        self.assertIn("RECALLS: 2 matching campaigns found.", text)
        self.assertIn("### Source. NHTSA recalls API (api.nhtsa.gov recallsByVehicle)", text)
        self.assertIn("- Query URL: " + ELANTRA_URL, text)
        # Response order is kept: 21V796000 before 21V302000, as recorded.
        self.assertLess(lines.index("#### Campaign 21V796000"), lines.index("#### Campaign 21V302000"))
        # Claims come before the source link, the link before the excerpt,
        # and the raw body is the last line inside the transcript fence.
        self.assertLess(lines.index("#### Campaign 21V302000"), lines.index("- Query URL: " + ELANTRA_URL))
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], body)

    def test_recorded_head_excerpt_reports_count_difference(self):
        lines = nr.render_section("Hyundai Elantra 2021", "recallsByVehicle", ELANTRA_PARAMS,
                                  ELANTRA_URL, RETRIEVED, transcript_for(S24_HEAD_CLOSED), S24_HEAD_CLOSED)
        text = "\n".join(lines)
        self.assertIn("returned 1 campaign (retrieved", text)
        self.assertIn('The response\'s own "Count" field shows 6, which differs from the 1 entries', text)
        self.assertIn("#### Campaign 21V796000", text)
        self.assertIn("- Date as shown (ReportReceivedDate): 13/10/2021 (October 13, 2021)", text)

    def test_exclusion_is_listed_with_reason(self):
        body = envelope([CAMPAIGN_21V796000, CAMPAIGN_21V302000])
        reason = "replaced by 22V354000 according to its own remedy text"
        lines = nr.render_section(
            "Hyundai Elantra 2021", "recallsByVehicle", ELANTRA_PARAMS, ELANTRA_URL, RETRIEVED,
            transcript_for(body), body, exclusions={"21V796000": reason},
        )
        text = "\n".join(lines)
        self.assertIn("returned 2 campaigns", text)
        self.assertIn("RECALLS: 1 matching campaign found.", text)
        self.assertIn("Checked and excluded: 1 campaign in the same response is listed below", text)
        self.assertIn("- Checked and excluded because: " + reason, text)
        exclusion_line = [i for i, l in enumerate(lines) if l.startswith("Checked and excluded:")][0]
        self.assertLess(lines.index("#### Campaign 21V302000"), exclusion_line)
        self.assertLess(exclusion_line, lines.index("#### Campaign 21V796000"))
        self.assertLess(lines.index("#### Campaign 21V796000"),
                        lines.index("- Checked and excluded because: " + reason))

    def test_exclusion_not_in_response_is_refused(self):
        body = envelope([CAMPAIGN_21V302000])
        with self.assertRaises(ValueError):
            nr.render_section("x", "recallsByVehicle", ELANTRA_PARAMS, ELANTRA_URL, RETRIEVED,
                              transcript_for(body), body, exclusions={"24V879000": "not here"})

    def test_pretty_excerpts_keep_values_unchanged_in_response_order(self):
        body = envelope([CAMPAIGN_21V796000, CAMPAIGN_21V302000])
        lines = nr.render_section("x", "recallsByVehicle", ELANTRA_PARAMS, ELANTRA_URL, RETRIEVED,
                                  transcript_for(body), body, pretty=True)
        starts = [i for i, l in enumerate(lines) if l.startswith(
            "Excerpt (make = Hyundai, model = Elantra, modelYear = 2021 response, campaign ")]
        self.assertEqual(len(starts), 2)
        self.assertIn("campaign 1 of 2 in response order", lines[starts[0]])
        first_end = lines.index("```", starts[0] + 2)
        second_end = lines.index("```", starts[1] + 2)
        self.assertEqual(json.loads("\n".join(lines[starts[0] + 2:first_end])), CAMPAIGN_21V796000)
        self.assertEqual(json.loads("\n".join(lines[starts[1] + 2:second_end])), CAMPAIGN_21V302000)

    def test_non_json_body_still_prints_transcript(self):
        transcript = "HTTP/1.1 503 Service Unavailable\nContent-Type: text/html\n\n<html>busy</html>"
        lines = nr.render_section("Hyundai Elantra 2021", "recallsByVehicle", ELANTRA_PARAMS, ELANTRA_URL,
                                  "2026-10-22T00:00:00Z", transcript, "<html>busy</html>")
        text = "\n".join(lines)
        self.assertIn("did not return the expected JSON object", text)
        self.assertIn("RECALLS: not determinable from this response.", text)
        self.assertIn("HTTP/1.1 503 Service Unavailable", text)
        self.assertIn("<html>busy</html>", text)

    def test_json_array_body_is_not_treated_as_results(self):
        body = "[]"
        lines = nr.render_section("x", "recallsByVehicle", ELANTRA_PARAMS, ELANTRA_URL, RETRIEVED,
                                  transcript_for(body), body)
        text = "\n".join(lines)
        self.assertIn("did not return the expected JSON object", text)
        self.assertIn("RECALLS: not determinable from this response.", text)


class _Handler(http.server.BaseHTTPRequestHandler):
    body = b"{}"
    status = 200

    def do_GET(self):
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Test-Order", "second")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


class FetchTests(unittest.TestCase):
    """fetch() against a local server: proves the transcript holds the
    status line, every header in order, a blank line, then the body."""

    @classmethod
    def setUpClass(cls):
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%d/" % cls.server.server_port
        os.environ["no_proxy"] = "127.0.0.1,localhost"
        os.environ["NO_PROXY"] = "127.0.0.1,localhost"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_transcript_shape_for_empty_results(self):
        _Handler.body, _Handler.status = envelope([]).encode("utf-8"), 200
        retrieved, transcript, body = nr.fetch(self.base + "recallsByVehicle?make=x&model=y&modelYear=1")
        self.assertRegex(retrieved, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(body, envelope([]))
        lines = transcript.split("\n")
        self.assertEqual(lines[0], "HTTP/1.0 200 OK")
        self.assertTrue(lines[1].startswith("Server: "))
        self.assertIn("Content-Type: application/json", lines)
        self.assertLess(lines.index("Content-Type: application/json"), lines.index("X-Test-Order: second"))
        self.assertEqual(lines[-2], "")
        self.assertEqual(lines[-1], envelope([]))

    def test_http_error_is_captured_not_raised(self):
        _Handler.body, _Handler.status = b"{}", 500
        _, transcript, body = nr.fetch(self.base)
        self.assertTrue(transcript.startswith("HTTP/1.0 500 Internal Server Error"))
        self.assertEqual(body, "{}")

    def test_main_end_to_end_prints_section(self):
        _Handler.body = envelope([CAMPAIGN_21V302000]).encode("utf-8")
        _Handler.status = 200
        original = nr.BASE_URL
        nr.BASE_URL = self.base
        try:
            out = io.StringIO()
            stdout = sys.stdout
            sys.stdout = out
            try:
                code = nr.main(["--subject", "Hyundai Elantra 2021", "--make", "Hyundai",
                                "--model", "Elantra", "--model-year", "2021"])
            finally:
                sys.stdout = stdout
        finally:
            nr.BASE_URL = original
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("## Subject: Hyundai Elantra 2021", text)
        self.assertIn("RECALLS: 1 matching campaign found.", text)
        self.assertIn("#### Campaign 21V302000", text)
        self.assertIn("- Query URL: " + self.base + "recallsByVehicle?make=Hyundai&model=Elantra&modelYear=2021", text)
        self.assertIn("HTTP/1.0 200 OK", text)

    def test_main_refuses_unknown_exclusion(self):
        _Handler.body = envelope([CAMPAIGN_21V302000]).encode("utf-8")
        _Handler.status = 200
        original = nr.BASE_URL
        nr.BASE_URL = self.base
        try:
            err = io.StringIO()
            stderr = sys.stderr
            sys.stderr = err
            try:
                code = nr.main(["--make", "Hyundai", "--model", "Elantra", "--model-year", "2021",
                                "--exclude", "24V879000=not in this response"])
            finally:
                sys.stderr = stderr
        finally:
            nr.BASE_URL = original
        self.assertEqual(code, 2)
        self.assertIn("excluded campaign number(s) not in the response: 24V879000", err.getvalue())


if __name__ == "__main__":
    unittest.main()
