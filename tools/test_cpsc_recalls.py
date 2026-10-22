"""Tests for tools/cpsc_recalls.py. Standard library only, no network.

Run:  python3 -m unittest discover -s tools -v

The fixtures are not invented. Every response text below is copied
verbatim from the published delivery
deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md,
which records the source, the exact query URL, and the UTC retrieval
time for each. Where a fixture is a record whose published excerpt ends
at RemedyOptions, the fixture is closed syntactically at that point and
holds no fields past the excerpt. The fetch test uses a local HTTP
server on 127.0.0.1 and nothing else.
"""

import http.server
import json
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cpsc_recalls as cr  # noqa: E402

# Delivery source S10: the complete raw HTTP response transcript for
# https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant%20Pot%20Smart%20WiFi
# retrieved 2026-10-22T11:48:05Z. Verbatim.
S10_TRANSCRIPT = """HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Cache-Control: no-cache
Expires: Thu, 22 Oct 2026 11:48:07 GMT
Date: Thu, 22 Oct 2026 11:48:07 GMT
Alt-Svc: h3=":443"; ma=93600
Connection: close
Content-Length: 2

[]"""

# Delivery source S25: the record for recall 13-087 from
# https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=13-087
# retrieved 2026-10-22T11:48:09Z, parts 1 and 2 verbatim, closed after
# RemedyOptions where the published excerpt ends.
RECORD_13_087 = json.loads(r"""
  {
    "RecallID": 1285,
    "RecallNumber": "13087",
    "RecallDate": "2013-01-08T00:00:00",
    "Description": "This recall to inspect includes all Fisher-Price Rock N' Play infant recliner seats called sleepers. The sleeper is designed for babies up to 25 pounds and is composed of a soft plastic seat held by a metal rocking frame. The product has a removable, fabric cover that is sold in 14 patterns and color palettes.",
    "URL": "https://www.cpsc.gov/Recalls/2013/Fisher-Price-Recalls-to-Inspect-Rock-N-Play-Infant-Sleepers-Due-to-Risk-of-Exposure-to-Mold",
    "Title": "Fisher-Price Recalls to Inspect Rock 'N Play Infant Sleepers Due to Risk of Exposure to Mold",
    "ConsumerContact": "Fisher-Price; at (800) 432-5437, from 9 a.m. to 6 p.m. ET Monday through Friday, or online at www.service.mattel.com for more information.",
    "LastPublishDate": "2015-01-13T00:00:00",
    "Products": [
      {
        "Name": "Newborn Rock 'n Play Sleeper™",
        "Description": "",
        "Model": "",
        "Type": "Bassinets and Cradles",
        "CategoryID": "67558",
        "NumberOfUnits": "About 800,000 units"
      }
    ],
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "Mold can develop between the removable seat cushion and the hard plastic frame of the sleeper when it remains wet/moist or is infrequently cleaned, posing a risk of exposure to mold to infants sleeping in the product. The CPSC advises that mold has been associated with respiratory illnesses and other infections. Although mold is not present at the time of purchase, mold growth can occur after use of the product.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately check for mold under the removable seat cushion. Dark brown, gray or black spots can indicate the presence of mold. If mold is found, consumers should immediately stop using the product. Consumers can contact Fisher-Price for cleaning instructions or further assistance. Cleaning and care instructions can also be found at www.service.mattel.com or by contacting the firm."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "New Instructions"
      },
      {
        "Option": "Repair"
      }
    ]
  }
""")

# Delivery source S2: the record for recall 21-128 from
# https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128
# retrieved 2026-10-22T03:28:32Z, parts 1 and 2 verbatim, closed after
# RemedyOptions where the published excerpt ends. In this record the
# remedy text repeats the hazard text, which the delivery notes.
RECORD_21_128 = json.loads(r"""
  {
    "RecallID": 9057,
    "RecallNumber": "21128",
    "RecallDate": "2021-05-05T00:00:00",
    "Description": "This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.",
    "URL": "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported",
    "Title": "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported",
    "ConsumerContact": "Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.",
    "LastPublishDate": "2021-05-05T00:00:00",
    "Products": [
      {
        "Name": "Tread+",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 125,000"
      }
    ],
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Refund"
      },
      {
        "Option": "Repair"
      }
    ]
  }
""")


def transcript_for(records):
    """A transcript with the S10 status line and headers and a body that
    is the given records serialised. Only the body differs from S10."""
    body = json.dumps(records, ensure_ascii=False)
    head = S10_TRANSCRIPT.rsplit("\n\n", 1)[0]
    return head + "\n\n" + body, body


class QueryBuildingTests(unittest.TestCase):
    def test_url_matches_published_delivery_urls(self):
        # Delivery S4 and S22 query URLs, verbatim.
        self.assertEqual(
            cr.build_url([("ProductName", "Rock 'n Play")]),
            "https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Rock%20%27n%20Play",
        )
        self.assertEqual(
            cr.build_url([
                ("ProductName", "Top-Load Washing Machines"),
                ("RecallDateStart", "2018-01-01"),
                ("RecallDateEnd", "2023-12-31"),
            ]),
            "https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Top-Load%20Washing%20Machines&RecallDateStart=2018-01-01&RecallDateEnd=2023-12-31",
        )

    def test_describe_query_matches_delivery_phrasing(self):
        self.assertEqual(cr.describe_query([("ProductName", "VH101")]), 'ProductName = "VH101"')
        self.assertEqual(
            cr.describe_query([
                ("ProductName", "Top-Load Washing Machines"),
                ("RecallDateStart", "2018-01-01"),
                ("RecallDateEnd", "2023-12-31"),
            ]),
            'ProductName = "Top-Load Washing Machines" with RecallDateStart = 2018-01-01 and RecallDateEnd = 2023-12-31',
        )

    def test_build_params_needs_a_field(self):
        parser_args = cr.argparse.Namespace(
            recall_number=None, recall_title=None, product_name=None,
            date_start=None, date_end=None, param=None,
        )
        with self.assertRaises(ValueError):
            cr.build_params(parser_args)


class ValueFormattingTests(unittest.TestCase):
    def test_recall_number_dash(self):
        self.assertEqual(cr.dash_recall_number("18136"), "18-136")
        self.assertEqual(cr.dash_recall_number("13087"), "13-087")
        self.assertEqual(cr.dash_recall_number("oddity"), "oddity")

    def test_long_date(self):
        self.assertEqual(cr.long_date("2018-04-04T00:00:00"), "April 4, 2018")
        self.assertEqual(cr.long_date("2013-01-08T00:00:00"), "January 8, 2013")
        self.assertEqual(cr.long_date("not a date"), "not a date")

    def test_parse_exclusions(self):
        self.assertEqual(
            cr.parse_exclusions(['18-199="names a different model"', "15741=other model"]),
            {"18-199": "names a different model", "15-741": "other model"},
        )
        with self.assertRaises(ValueError):
            cr.parse_exclusions(["18-199"])
        with self.assertRaises(ValueError):
            cr.parse_exclusions(["18-199="])


class EmptyResultTests(unittest.TestCase):
    def setUp(self):
        self.params = [("ProductName", "Instant Pot Smart WiFi")]
        self.url = cr.build_url(self.params)
        self.lines = cr.render_section(
            "Instant Pot Smart WiFi 6 Qt", self.params, self.url,
            "2026-10-22T11:48:05Z", S10_TRANSCRIPT, "[]",
        )
        self.text = "\n".join(self.lines)

    def test_query_line_and_none_found(self):
        self.assertIn(
            'QUERY: ProductName = "Instant Pot Smart WiFi" returned 0 records (retrieved 2026-10-22T11:48:05Z).',
            self.text,
        )
        self.assertIn("RECALLS: none found for Instant Pot Smart WiFi 6 Qt.", self.text)
        self.assertNotIn("#### Recall", self.text)

    def test_full_transcript_printed_directly_beneath_source_link(self):
        link_index = self.lines.index("- Query URL: " + self.url)
        self.assertEqual(self.lines[link_index + 1], "- Retrieved (UTC): 2026-10-22T11:48:05Z")
        self.assertTrue(self.lines[link_index + 2].startswith("Excerpt ("))
        self.assertEqual(self.lines[link_index + 3], "```")
        fence_start = link_index + 3
        fence_end = self.lines.index("```", fence_start + 1)
        self.assertEqual("\n".join(self.lines[fence_start + 1:fence_end]), S10_TRANSCRIPT)
        self.assertEqual(self.lines[fence_end - 1], "[]")

    def test_query_url_is_the_exact_query(self):
        self.assertEqual(
            self.url,
            "https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant%20Pot%20Smart%20WiFi",
        )


class RecordRenderingTests(unittest.TestCase):
    def test_record_block_matches_delivery_subject_lines(self):
        block = cr.render_record(RECORD_13_087)
        # These lines appear word for word under Subject 2 of the delivery.
        for expected in [
            "#### Recall 13-087",
            "- Recall number: 13-087",
            "- Announcement date: January 8, 2013",
            "- Product as shown: Newborn Rock 'n Play Sleeper™",
            "- Hazard as shown: " + RECORD_13_087["Hazards"][0]["Name"],
            "- Remedy as shown: " + RECORD_13_087["Remedies"][0]["Name"],
            "- Units as shown: About 800,000 units",
            "- Remedy options as shown in the API record: New Instructions; Repair",
            "- CPSC recall page as shown: " + RECORD_13_087["URL"],
        ]:
            self.assertIn(expected, block)
        self.assertFalse(any("Note:" in line for line in block))

    def test_remedy_repeating_hazard_is_noted(self):
        block = cr.render_record(RECORD_21_128)
        self.assertIn("- Units as shown: About 125,000", block)
        self.assertIn("- Remedy options as shown in the API record: Refund; Repair", block)
        notes = [line for line in block if line.startswith("- Note: in the API record for 21-128")]
        self.assertEqual(len(notes), 1)
        self.assertIn("repeats the hazard text word for word", notes[0])

    def test_missing_fields_are_marked_not_invented(self):
        block = cr.render_record({"RecallNumber": "99999", "RecallDate": "", "Title": ""})
        self.assertIn("- Product as shown: (not present in the API record)", block)
        self.assertIn("- Hazard as shown: (not present in the API record)", block)
        self.assertIn("- Units as shown: (not present in the API record)", block)


class SectionTests(unittest.TestCase):
    def test_one_record_section(self):
        params = [("RecallNumber", "13-087")]
        url = cr.build_url(params)
        transcript, body = transcript_for([RECORD_13_087])
        lines = cr.render_section("Fisher-Price Rock 'n Play Sleeper", params, url,
                                  "2026-10-22T11:48:09Z", transcript, body)
        text = "\n".join(lines)
        self.assertIn('QUERY: RecallNumber = "13-087" returned 1 record (retrieved 2026-10-22T11:48:09Z).', text)
        self.assertIn("RECALLS: 1 matching recall found.", text)
        self.assertIn("#### Recall 13-087", text)
        self.assertIn("- Query URL: " + url, text)
        # The raw body is the last line inside the transcript fence.
        fence_end = len(lines) - 1 - lines[::-1].index("```")
        self.assertEqual(lines[fence_end - 1], body)
        # Claims come before the source link, the link before the excerpt.
        self.assertLess(lines.index("#### Recall 13-087"), lines.index("- Query URL: " + url))

    def test_exclusion_is_listed_with_reason(self):
        params = [("RecallTitle", "Peloton")]
        url = cr.build_url(params)
        transcript, body = transcript_for([RECORD_21_128, RECORD_13_087])
        lines = cr.render_section(
            "Peloton Tread+ treadmill", params, url, "2026-10-22T03:30:55Z",
            transcript, body, exclusions={"13-087": "names a Fisher-Price sleeper, not a Peloton product"},
        )
        text = "\n".join(lines)
        self.assertIn('returned 2 records', text)
        self.assertIn("RECALLS: 1 matching recall found.", text)
        self.assertIn("Checked and excluded: 1 record in the same response is listed below", text)
        self.assertIn("- Checked and excluded because: names a Fisher-Price sleeper, not a Peloton product", text)
        # The kept record comes first, then the exclusion line, then the
        # excluded record with its reason.
        exclusion_line = [i for i, l in enumerate(lines) if l.startswith("Checked and excluded:")][0]
        self.assertLess(lines.index("#### Recall 21-128"), exclusion_line)
        self.assertLess(exclusion_line, lines.index("#### Recall 13-087"))
        self.assertLess(
            lines.index("#### Recall 13-087"),
            lines.index("- Checked and excluded because: names a Fisher-Price sleeper, not a Peloton product"),
        )

    def test_exclusion_not_in_response_is_refused(self):
        params = [("RecallNumber", "13-087")]
        transcript, body = transcript_for([RECORD_13_087])
        with self.assertRaises(ValueError):
            cr.render_section("x", params, cr.build_url(params), "2026-10-22T11:48:09Z",
                              transcript, body, exclusions={"18-199": "not here"})

    def test_pretty_excerpts_keep_values_unchanged(self):
        params = [("RecallNumber", "13-087")]
        transcript, body = transcript_for([RECORD_13_087])
        lines = cr.render_section("x", params, cr.build_url(params), "2026-10-22T11:48:09Z",
                                  transcript, body, pretty=True)
        start = [i for i, l in enumerate(lines) if l.startswith("Excerpt (RecallNumber = \"13-087\" response, record 1 of 1")][0]
        end = lines.index("```", start + 2)
        self.assertEqual(json.loads("\n".join(lines[start + 2:end])), RECORD_13_087)

    def test_non_json_body_still_prints_transcript(self):
        params = [("ProductName", "VH101")]
        transcript = "HTTP/1.1 503 Service Unavailable\nContent-Type: text/html\n\n<html>busy</html>"
        lines = cr.render_section("Vornado VH101 heater", params, cr.build_url(params),
                                  "2026-10-22T00:00:00Z", transcript, "<html>busy</html>")
        text = "\n".join(lines)
        self.assertIn("did not return a JSON array", text)
        self.assertIn("RECALLS: not determinable from this response.", text)
        self.assertIn("HTTP/1.1 503 Service Unavailable", text)
        self.assertIn("<html>busy</html>", text)


class _Handler(http.server.BaseHTTPRequestHandler):
    body = b"[]"
    status = 200

    def do_GET(self):
        self.send_response(self.status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
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

    def test_transcript_shape_for_empty_array(self):
        _Handler.body, _Handler.status = b"[]", 200
        retrieved, transcript, body = cr.fetch(self.base + "?format=json&ProductName=x")
        self.assertRegex(retrieved, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(body, "[]")
        lines = transcript.split("\n")
        self.assertEqual(lines[0], "HTTP/1.0 200 OK")
        self.assertTrue(lines[1].startswith("Server: "))
        self.assertIn("Content-Type: application/json; charset=utf-8", lines)
        self.assertLess(lines.index("Content-Type: application/json; charset=utf-8"),
                        lines.index("X-Test-Order: second"))
        self.assertEqual(lines[-2], "")
        self.assertEqual(lines[-1], "[]")

    def test_http_error_is_captured_not_raised(self):
        _Handler.body, _Handler.status = b"[]", 500
        _, transcript, body = cr.fetch(self.base)
        self.assertTrue(transcript.startswith("HTTP/1.0 500 Internal Server Error"))
        self.assertEqual(body, "[]")

    def test_main_end_to_end_prints_section(self):
        _Handler.body, _Handler.status = json.dumps([RECORD_13_087], ensure_ascii=False).encode("utf-8"), 200
        original = cr.BASE_URL
        cr.BASE_URL = self.base
        try:
            import io
            out = io.StringIO()
            stdout = sys.stdout
            sys.stdout = out
            try:
                code = cr.main(["--subject", "Fisher-Price Rock 'n Play Sleeper", "--recall-number", "13-087"])
            finally:
                sys.stdout = stdout
        finally:
            cr.BASE_URL = original
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("## Subject: Fisher-Price Rock 'n Play Sleeper", text)
        self.assertIn("RECALLS: 1 matching recall found.", text)
        self.assertIn("- Query URL: " + self.base + "?format=json&RecallNumber=13-087", text)
        self.assertIn("HTTP/1.0 200 OK", text)


if __name__ == "__main__":
    unittest.main()
