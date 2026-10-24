"""Tests for tools/vin_decode.py (issue #161). Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_vin_decode.py' -v

Fixtures: fixtures/vpic/*.json are five real response bodies from the live
vPIC DecodeVinValues endpoint, captured by the coordinator under Option B
on issue #161 (this container cannot reach vpic.nhtsa.dot.gov) and saved
unmodified. Each one's URL, status, size, SHA-256 and the comment it was
posted in are in fixtures/vpic/provenance.json, and the hash is checked
here. The captures carry the bodies only, so where a test needs a full
transcript it puts a plainly labelled test status line above the recorded
body; that line is not a recording of any vPIC header.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vin_decode as vd  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "vpic"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
HARNESS_STATUS = "HTTP/1.1 200 OK"  # test harness line, not a recorded header
RETRIEVED = "2026-10-24T01:38:00Z"  # test value; the captures' own times are in provenance.json

CLEAN = "clean-1HGCM82633A004352.json"
CHECK_DIGIT = "check-digit-1HGCM82643A004352.json"
PARTIAL = "example-partial-5UXWX7C5-BA.json"
PARTIAL_9TH = "example-partial-5UXWX7C55BA.json"
ZEROS = "all-zeros-00000000000000000.json"


def body(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def capture(name):
    """(retrieved, transcript, body) for a fixture, as fetch() returns them."""
    b = body(name)
    return RETRIEVED, "\n".join([HARNESS_STATUS, "Content-Type: application/json", "", b]), b


def section(name, vin, year=None, pretty=False):
    retrieved, transcript, b = capture(name)
    return "\n".join(vd.render_section(vin, year, vd.build_url(vin, year), retrieved, transcript, b, pretty))


class Fixtures(unittest.TestCase):
    def test_hashes_and_urls_match_provenance(self):
        self.assertEqual(sorted(PROVENANCE), sorted(p.name for p in FIXTURES.glob("*.json") if p.name != "provenance.json"))
        for name, entry in PROVENANCE.items():
            raw = (FIXTURES / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"], name)
            self.assertEqual(len(raw), entry["body_bytes"], name)
            criteria = json.loads(raw)["SearchCriteria"]
            vin = criteria.split("VIN(s): ", 1)[1]
            year = entry["url"].split("modelyear=")[1] if "modelyear=" in entry["url"] else None
            # The tool builds the exact URL each capture was made with.
            self.assertEqual(vd.build_url(vd.check_vin(vin), year), entry["url"], name)


class Query(unittest.TestCase):
    def test_vin_is_normalised_and_checked(self):
        self.assertEqual(vd.check_vin(" 1hgcm8 2633a004352 "), "1HGCM82633A004352")
        self.assertEqual(vd.check_vin("5uxwx7c5*ba"), "5UXWX7C5*BA")
        for bad in ("", "   ", "1HGCM82633A0043521", "1HGCM/2633A004352", "1HGCM?2633A004352", "ÄBC"):
            with self.assertRaises(ValueError, msg=bad):
                vd.check_vin(bad)

    def test_model_year(self):
        self.assertIsNone(vd.check_year(None))
        self.assertIsNone(vd.check_year(" "))
        self.assertEqual(vd.check_year("2011"), "2011")
        for bad in ("11", "20111", "year"):
            with self.assertRaises(ValueError, msg=bad):
                vd.check_year(bad)


class Render(unittest.TestCase):
    def test_clean_decode(self):
        text = section(CLEAN, "1HGCM82633A004352")
        self.assertIn("QUERY: VIN = 1HGCM82633A004352 returned 1 result (retrieved %s)." % RETRIEVED, text)
        self.assertIn('VPIC STATUS: ErrorCode as shown: "0"; ErrorText as shown: '
                      '"0 - VIN decoded clean. Check Digit (9th position) is correct"', text)
        self.assertIn("DECODE: vehicle as shown: 2003 HONDA Accord EX-V6", text)
        self.assertIn("- Manufacturer: AMERICAN HONDA MOTOR CO., INC.", text)
        self.assertIn("- PlantCity: MARYSVILLE", text)
        self.assertNotIn("- ErrorCode:", text)
        self.assertNotIn("no vehicle decoded", text)

    def test_every_value_listed_is_in_the_record_in_order(self):
        record = json.loads(body(CLEAN))["Results"][0]
        text = section(CLEAN, "1HGCM82633A004352")
        listed = text.split("Fields with a value, in response order (", 1)[1]
        count = int(listed.split(")", 1)[0])
        rows = [l[2:].split(": ", 1) for l in listed.split("\n")[1:count + 1]]
        self.assertEqual(len(rows), count)
        for key, value in rows:
            self.assertEqual(record[key], value, key)
        keys = [k for k, _ in rows]
        self.assertEqual(keys, [k for k in record if k in keys])
        expected = [k for k, v in record.items()
                    if v.strip() and k not in ("ErrorCode", "ErrorText", "AdditionalErrorText")]
        self.assertEqual(keys, expected)
        empty = sum(1 for v in record.values() if not v.strip())
        self.assertIn("%d other fields came back empty. The response's own Message says: " % empty, text)

    def test_check_digit_error_is_quoted_and_vehicle_still_shown(self):
        text = section(CHECK_DIGIT, "1HGCM82643A004352")
        self.assertIn('ErrorCode as shown: "1"; ErrorText as shown: '
                      '"1 - Check Digit (9th position) does not calculate properly"', text)
        self.assertIn("DECODE: vehicle as shown: 2003 HONDA Accord EX-V6", text)

    def test_partial_vin_is_incomplete_per_vpic(self):
        for name, vin in ((PARTIAL, "5UXWX7C5*BA"), (PARTIAL_9TH, "5UXWX7C55BA")):
            text = section(name, vin, "2011")
            self.assertIn("QUERY: VIN = %s, modelyear = 2011 returned 1 result" % vin, text)
            self.assertIn('ErrorCode as shown: "6"; ErrorText as shown: "6 - Incomplete VIN"', text)
            self.assertIn("DECODE: vehicle as shown: 2011 BMW X3 xDrive35i", text)
            self.assertIn("queried by VIN and model year.", text)

    def test_empty_decode_is_proven_by_the_transcript(self):
        text = section(ZEROS, "00000000000000000")
        self.assertIn("DECODE: no vehicle decoded. Make, Model and ModelYear are empty in the response", text)
        self.assertIn('ErrorCode as shown: "1,7,11,400"', text)
        self.assertIn("- AdditionalErrorText as shown: Invalid character(s): 10:0.", text)
        self.assertNotIn("vehicle as shown:", text)
        _, transcript, _ = capture(ZEROS)
        self.assertIn("```\n" + transcript + "\n```", text)

    def test_source_block_sits_directly_above_the_transcript(self):
        _, transcript, _ = capture(CLEAN)
        text = section(CLEAN, "1HGCM82633A004352")
        self.assertIn("### Source. NHTSA vPIC API (vpic.nhtsa.dot.gov DecodeVinValues)\n"
                      "- Query URL: https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/1HGCM82633A004352?format=json\n"
                      "- Retrieved (UTC): %s\nExcerpt (complete raw HTTP response transcript" % RETRIEVED, text)
        self.assertTrue(text.endswith("```\n" + transcript + "\n```"))

    def test_pretty_excerpt_has_values_unchanged(self):
        text = section(CLEAN, "1HGCM82633A004352", pretty=True)
        pretty = text.rsplit("values unchanged):\n```\n", 1)[1].rsplit("\n```", 1)[0]
        self.assertEqual(json.loads(pretty), json.loads(body(CLEAN))["Results"][0])

    def test_empty_results_array_is_reported_not_crashed(self):
        # A test variant of the recorded body with its Results emptied, to
        # exercise the branch; vPIC returned no such response in the captures.
        data = json.loads(body(ZEROS))
        data["Results"] = []
        b = json.dumps(data)
        text = "\n".join(vd.render_section("X", None, vd.build_url("X"), RETRIEVED, HARNESS_STATUS + "\n\n" + b, b))
        self.assertIn("returned 0 results", text)
        self.assertIn('own "Count" field shows 1, which differs from the 0 entries', text)
        self.assertIn("DECODE: no vehicle decoded. The Results array in the response was empty", text)

    def test_unreadable_body_keeps_the_transcript(self):
        b = "<html>not json</html>"  # test body, not a recording
        text = "\n".join(vd.render_section("X", None, vd.build_url("X"), RETRIEVED, "HTTP/1.1 500 Internal Server Error\n\n" + b, b))
        self.assertIn("did not return the expected JSON object", text)
        self.assertIn("DECODE: not determinable from this response.", text)
        self.assertIn(b, text)


class DocsPage(unittest.TestCase):
    PAGE = Path(__file__).resolve().parents[2] / "docs" / "mcpize-tools" / "vin_decode_check.md"

    def test_page_quotes_the_tool_and_the_recorded_body(self):
        page = self.PAGE.read_text(encoding="utf-8")
        text = section(CLEAN, "1HGCM82633A004352")
        claims = page.split("## What a report shows", 1)[1].split("Source: ", 1)[0]
        quoted = [q for line in claims.splitlines() if line.startswith("- `") for q in line[2:].split("`")[1::2]]
        self.assertGreaterEqual(len(quoted), 5)
        for q in quoted:
            self.assertIn(q, text)
        entry = PROVENANCE[CLEAN]
        self.assertIn("Source: %s," % entry["url"], page)
        self.assertIn("sha256 `%s`" % entry["sha256"], page)
        self.assertIn("```json\n%s\n```" % body(CLEAN), page)

    def test_page_states_the_shelf_price_and_its_ruling(self):
        page = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("**Price:** 0.25 USDC per call", page)
        self.assertIn("issues/147#issuecomment-6377953191", page)


class CommandLine(unittest.TestCase):
    def run_main(self, argv, fetch):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(vd, "fetch", fetch), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = vd.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_one_fetch_of_the_exact_url(self):
        urls = []

        def fake(url):
            urls.append(url)
            return capture(PARTIAL)
        code, out, _ = self.run_main(["5uxwx7c5*ba", "--model-year", "2011"], fake)
        self.assertEqual(code, 0)
        self.assertEqual(urls, [PROVENANCE[PARTIAL]["url"]])
        self.assertTrue(out.startswith("## Subject: VIN 5UXWX7C5*BA\n"))

    def test_bad_input_fetches_nothing(self):
        def never(url):
            raise AssertionError("no fetch expected")
        for argv in (["1HGCM/2633A004352"], ["1HGCM82633A004352", "--model-year", "03"]):
            code, out, _ = self.run_main(argv, never)
            self.assertEqual(code, 2, argv)
            self.assertEqual(out, "")

    def test_failed_fetch_prints_no_report(self):
        def broken(url):
            raise urllib.error.URLError("connection refused (test)")
        code, out, err = self.run_main(["1HGCM82633A004352"], broken)
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("fetch failed, nothing printed", err)


if __name__ == "__main__":
    unittest.main()
