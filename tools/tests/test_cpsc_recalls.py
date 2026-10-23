"""Regression tests use captured public responses, never invented recall data.

Set CPSC_LIVE=1 to also run the real CLI against the public CPSC endpoint.
Malformed-response tests deliberately corrupt captures to test failure handling.
"""

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from tools import cpsc_recalls as cpsc


FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[2]
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text())


def captured(name):
    metadata = PROVENANCE[name]
    return cpsc.Capture(metadata["url"], metadata["retrieved_utc"],
                        (FIXTURES / name).read_bytes().decode("utf-8"))


class ReportTests(unittest.TestCase):
    def test_capture_integrity_and_provenance(self):
        for name, metadata in PROVENANCE.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest(),
                                 metadata["sha256"])
                self.assertTrue(metadata["url"].startswith(cpsc.ENDPOINT + "?"))
                self.assertRegex(metadata["retrieved_utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_nonempty_claim_and_names_are_from_source(self):
        capture = captured("instant-pot.http")
        rows = cpsc.records(capture)
        self.assertTrue(rows)
        output = cpsc.render_query(capture)
        self.assertIn(f"CPSC returned {len(rows)} record(s)", output)
        for row in rows:
            self.assertIn(cpsc.inline(row["RecallNumber"]), output)
            for product in row["Products"]:
                self.assertIn(cpsc.inline(product["Name"]), output)
        self.assertNotIn("Checked and excluded:", output)

    def test_complete_empty_response_under_source_without_reformatting(self):
        capture = captured("smart-wifi.http")
        self.assertEqual(cpsc.records(capture), [])
        output = cpsc.render_query(capture)
        self.assertIn(f"Source: <{capture.url}>\n```\n{capture.raw}\n```", output)
        self.assertIn(f"Exact query: GET {capture.url}", output)
        self.assertIn(f"Retrieved (UTC): {capture.retrieved}", output)

    def test_nonempty_response_preserved_byte_for_byte(self):
        capture = captured("instant-pot.http")
        output = cpsc.render_query(capture)
        self.assertIn(f"Source: <{capture.url}>\n```\n{capture.raw}\n```", output)

    def test_near_match_has_source_names_and_explicit_exclusion_reason(self):
        target = parse_qs(urlsplit(captured("smart-wifi.http").url).query)["ProductName"][0]
        capture = captured("instant-pot.http")
        output = cpsc.render_query(capture, exact_name=target, near=True)
        self.assertIn("Checked and excluded:", output)
        self.assertIn("Reason: none of the returned product names equals", output)
        self.assertIn(cpsc.inline(target), output)
        self.assertIn("model applicability still requires review", output)
        self.assertIn(capture.raw, output)

    def test_exact_name_ignores_case_and_whitespace(self):
        capture = captured("instant-pot.http")
        name = cpsc.records(capture)[0]["Products"][0]["Name"]
        output = cpsc.render_query(capture, exact_name="  " + name.upper() + "  ")
        self.assertIn("Returned candidate:", output)
        self.assertNotIn("Checked and excluded:", output)

    def test_query_encodes_source_product_names(self):
        name = cpsc.records(captured("instant-pot.http"))[0]["Products"][0]["Name"]
        query = parse_qs(urlsplit(cpsc.query_url(name)).query)
        self.assertEqual(query, {"format": ["json"], "ProductName": [name]})

    def test_blank_query_rejected(self):
        with self.assertRaises(ValueError):
            cpsc.query_url(" \t")

    def test_bad_responses_cannot_be_reported_as_zero_results(self):
        capture = captured("instant-pot.http")
        headers, _, body = capture.raw.partition("\r\n\r\n")
        bad = [capture.raw.replace("200", "500", 1),
               headers + "\r\n\r\n" + body[:-1],
               headers + "\r\n\r\n{}",
               headers + "\r\n\r\n[{}]",
               capture.raw.replace("application/json", "text/html"),
               capture.raw.replace("\r\n", "\n")]
        for raw in bad:
            with self.subTest(raw=raw[:40]), self.assertRaises(cpsc.FetchError):
                cpsc.render_query(cpsc.Capture(capture.url, capture.retrieved, raw))

    def test_missing_names_are_not_silently_excluded(self):
        capture = captured("instant-pot.http")
        rows = cpsc.records(capture)
        rows[0]["Products"] = []  # Deliberate schema fault, not a factual fixture.
        headers = capture.raw.partition("\r\n\r\n")[0]
        with self.assertRaises(cpsc.FetchError):
            cpsc.records(cpsc.Capture(capture.url, capture.retrieved,
                                      headers + "\r\n\r\n" + json.dumps(rows)))

    def test_markdown_cannot_close_raw_evidence_fence(self):
        capture = captured("instant-pot.http")
        # Inject delimiter in an HTTP header only, without inventing recall values.
        raw = capture.raw.replace("\r\n", "\r\nX-Test: ```\r\n", 1)
        output = cpsc.render_query(cpsc.Capture(capture.url, capture.retrieved, raw))
        self.assertIn(f"Source: <{capture.url}>\n````\n{raw}\n````", output)

    def test_curl_bypasses_config_and_preserves_capture(self):
        capture = captured("instant-pot.http")
        result = subprocess.CompletedProcess([], 0, capture.raw.encode(), b"")
        with patch.object(cpsc.subprocess, "run", return_value=result) as run:
            fetched = cpsc.fetch("Instant Pot")
        command = run.call_args.args[0]
        self.assertEqual(command[:2], ["curl", "--disable"])
        self.assertIn("--suppress-connect-headers", command)
        self.assertNotIn("--location", command)
        self.assertEqual(fetched.raw, capture.raw)
        self.assertTrue(fetched.retrieved.endswith("Z"))

    def test_transport_failure_and_timeout_raise(self):
        result = subprocess.CompletedProcess([], 28, b"", b"")
        with patch.object(cpsc.subprocess, "run", return_value=result):
            with self.assertRaises(cpsc.FetchError):
                cpsc.fetch("Instant Pot")
        with patch.object(cpsc.subprocess, "run", side_effect=subprocess.TimeoutExpired("curl", 35)):
            with self.assertRaises(cpsc.FetchError):
                cpsc.fetch("Instant Pot")

    def test_late_failure_emits_no_partial_report(self):
        with patch.object(cpsc, "fetch", side_effect=[captured("smart-wifi.http"), cpsc.FetchError("failed")]):
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = cpsc.main(["Instant Pot Smart WiFi", "--exact-name", "Instant Pot Smart WiFi",
                                    "--near-product", "Instant Pot"])
        self.assertEqual(status, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("No report emitted", err.getvalue())

    def test_near_query_requires_explicit_rule(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_info:
            cpsc.main(["Instant Pot Smart WiFi", "--near-product", "Instant Pot"])
        self.assertEqual(exit_info.exception.code, 2)

    # --- claim blocks and the two added query shapes (task #26) ---

    def test_query_url_supports_three_fields_and_rejects_others(self):
        self.assertEqual(parse_qs(urlsplit(cpsc.query_url("Peloton", "RecallTitle")).query),
                         {"format": ["json"], "RecallTitle": ["Peloton"]})
        self.assertEqual(parse_qs(urlsplit(cpsc.query_url("21-128", "RecallNumber")).query),
                         {"format": ["json"], "RecallNumber": ["21-128"]})
        self.assertEqual(cpsc.query_url("Instant Pot"), cpsc.query_url("Instant Pot", "ProductName"))
        with self.assertRaises(ValueError):
            cpsc.query_url("Peloton", "Title")
        with self.assertRaises(ValueError):
            cpsc.query_url(" ", "RecallNumber")
        for field in cpsc.FIELDS:
            self.assertEqual(cpsc.query_field(cpsc.query_url("x", field)), field)
        with self.assertRaises(cpsc.FetchError):
            cpsc.query_field(cpsc.ENDPOINT + "?format=json")

    def test_claim_block_values_are_from_the_captured_record(self):
        capture = captured("instant-pot.http")
        row = cpsc.records(capture)[0]
        output = cpsc.render_query(capture)
        self.assertIn("#### Recall 15-741", output)
        self.assertIn(f"- Recall number as shown: {cpsc.inline(row['RecallNumber'])}", output)
        self.assertIn(f"- Announcement date as shown: {cpsc.inline(row['RecallDate'])} (July 15, 2015)", output)
        self.assertIn(f"- Title as shown: {cpsc.inline(row['Title'])}", output)
        self.assertIn(f"- Product as shown: {cpsc.inline(row['Products'][0]['Name'])}", output)
        self.assertIn(f"- Hazard as shown: {cpsc.inline(row['Hazards'][0]['Name'])}", output)
        self.assertIn(f"- Remedy as shown: {cpsc.inline(row['Remedies'][0]['Name'])}", output)
        self.assertIn(f"- Units as shown: {cpsc.inline(row['Products'][0]['NumberOfUnits'])}", output)
        self.assertIn(f"- Remedy options as shown: {cpsc.inline(row['RemedyOptions'][0]['Option'])}", output)
        self.assertIn(f"- CPSC recall page as shown: {cpsc.inline(row['URL'])}", output)
        self.assertIn("- Listed above as: Returned candidate", output)
        self.assertNotIn("- Note: the remedy text", output)
        # The block sits above the source link, and the raw capture still follows it.
        self.assertLess(output.index("#### Recall 15-741"), output.index(f"Source: <{capture.url}>"))
        self.assertIn(f"Source: <{capture.url}>\n```\n{capture.raw}\n```", output)

    def test_excluded_record_block_is_labelled(self):
        target = parse_qs(urlsplit(captured("smart-wifi.http").url).query)["ProductName"][0]
        output = cpsc.render_query(captured("instant-pot.http"), exact_name=target, near=True)
        self.assertIn("#### Recall 15-741", output)
        self.assertIn("- Listed above as: Checked and excluded", output)

    def test_missing_block_fields_are_marked_not_invented(self):
        capture = captured("instant-pot.http")
        rows = cpsc.records(capture)
        # Deliberate schema variation of the captured record, not a factual fixture:
        # the optional fields are removed to check that nothing is filled in for them.
        for key in ("RecallDate", "Title", "Hazards", "Remedies", "RemedyOptions", "URL"):
            rows[0].pop(key, None)
        rows[0]["Products"][0]["NumberOfUnits"] = ""
        headers = capture.raw.partition("\r\n\r\n")[0]
        output = cpsc.render_query(cpsc.Capture(capture.url, capture.retrieved,
                                                headers + "\r\n\r\n" + json.dumps(rows)))
        for label in ("Announcement date", "Title", "Hazard", "Remedy", "Units",
                      "Remedy options", "CPSC recall page"):
            self.assertIn(f"- {label}: {cpsc.NOT_PRESENT}", output)
        self.assertIn("#### Recall 15-741", output)

    def test_remedy_repeating_hazard_is_noted(self):
        capture = captured("instant-pot.http")
        rows = cpsc.records(capture)
        # Deliberate variation of the captured record, not a factual fixture: the
        # remedy text is set equal to the hazard text to exercise the note, which the
        # published delivery needed for recall 21-128.
        rows[0]["Remedies"] = [{"Name": rows[0]["Hazards"][0]["Name"]}]
        headers = capture.raw.partition("\r\n\r\n")[0]
        output = cpsc.render_query(cpsc.Capture(capture.url, capture.retrieved,
                                                headers + "\r\n\r\n" + json.dumps(rows)))
        self.assertIn("- Note: the remedy text in this API record repeats the hazard text", output)

    def test_dashed_and_long_date_keep_unparseable_values_as_shown(self):
        self.assertEqual(cpsc.dashed("15741"), "15-741")
        self.assertEqual(cpsc.dashed(" 21128 "), "21-128")
        self.assertEqual(cpsc.dashed("abc"), "abc")
        self.assertEqual(cpsc.long_date("2015-07-15T00:00:00"), "July 15, 2015")
        self.assertIsNone(cpsc.long_date("not a date"))
        self.assertIsNone(cpsc.long_date(None))

    def test_title_and_number_query_headings_and_links(self):
        # Reconstructed captures, labelled as such: the URL is the RecallTitle or
        # RecallNumber query shape, while the body is the verbatim instant-pot.http
        # capture reused only to exercise the heading and the source link. This does
        # not claim that CPSC returned that body for those queries.
        real = captured("instant-pot.http")
        for value, field, heading in (("Instant Pot", "RecallTitle", "### Recall title query"),
                                      ("15-741", "RecallNumber", "### Recall number query")):
            with self.subTest(field=field):
                url = cpsc.query_url(value, field)
                output = cpsc.render_query(cpsc.Capture(url, real.retrieved, real.raw))
                self.assertTrue(output.startswith(heading + "\n"))
                self.assertIn(f"Exact query: GET {url}", output)
                self.assertIn(f"Source: <{url}>\n```\n{real.raw}\n```", output)
                self.assertIn("#### Recall 15-741", output)
        near = cpsc.render_query(cpsc.Capture(cpsc.query_url("Instant Pot", "RecallTitle"),
                                              real.retrieved, real.raw), exact_name="x", near=True)
        self.assertTrue(near.startswith("### Checked near-match query\n"))

    def test_cli_sends_the_chosen_query_shape(self):
        calls = []

        def fake_fetch(value, field="ProductName"):
            calls.append((value, field))
            return captured("instant-pot.http")

        for argv, expected in ((["--recall-title", "Peloton"], ("Peloton", "RecallTitle")),
                               (["--recall-number", "21-128"], ("21-128", "RecallNumber")),
                               (["Instant Pot"], ("Instant Pot", "ProductName"))):
            with self.subTest(argv=argv):
                calls.clear()
                with patch.object(cpsc, "fetch", side_effect=fake_fetch), \
                        patch.object(sys, "stdout", new=io.TextIOWrapper(io.BytesIO(), encoding="utf-8")) as out:
                    status = cpsc.main(argv)
                    out.flush()
                    text = out.buffer.getvalue().decode("utf-8")
                self.assertEqual(status, 0)
                self.assertEqual(calls, [expected])
                self.assertIn("## CPSC recall search", text)
                self.assertIn("#### Recall 15-741", text)

    def test_cli_requires_exactly_one_query_shape(self):
        for argv in ([], ["Instant Pot", "--recall-title", "Peloton"],
                     ["--recall-title", "Peloton", "--recall-number", "21-128"]):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit) as exit_info:
                cpsc.main(argv)
            self.assertEqual(exit_info.exception.code, 2)


@unittest.skipUnless(os.environ.get("CPSC_LIVE") == "1", "set CPSC_LIVE=1 for public API checks")
class LiveTests(unittest.TestCase):
    def test_cli_nonempty_and_empty_with_excluded_near_match(self):
        result = subprocess.run(
            [sys.executable, "tools/cpsc_recalls.py", "Instant Pot Smart WiFi",
             "--exact-name", "Instant Pot Smart WiFi", "--near-product", "Instant Pot"],
            cwd=ROOT, capture_output=True, timeout=80,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        output = result.stdout.decode()
        self.assertIn("CPSC returned 0 record(s)", output)
        self.assertIn("\r\n\r\n[]\n```", output)
        self.assertIn("Checked and excluded:", output)
        self.assertIn("Reason:", output)
        self.assertEqual(output.count("Retrieved (UTC):"), 2)
        self.assertEqual(output.count("Source: <"), 2)

    def test_cli_title_and_number_query_shapes(self):
        # The delivery's Peloton query was RecallTitle = Peloton, and its detail
        # queries were RecallNumber = NN-NNN; both shapes are run live here.
        title = subprocess.run([sys.executable, "tools/cpsc_recalls.py", "--recall-title", "Peloton"],
                               cwd=ROOT, capture_output=True, timeout=80)
        self.assertEqual(title.returncode, 0, title.stderr.decode())
        title_out = title.stdout.decode()
        self.assertIn("### Recall title query", title_out)
        self.assertIn("RecallTitle=Peloton", title_out)
        self.assertIn("#### Recall ", title_out)
        self.assertIn("- Announcement date as shown:", title_out)
        number = subprocess.run([sys.executable, "tools/cpsc_recalls.py", "--recall-number", "21-128"],
                                cwd=ROOT, capture_output=True, timeout=80)
        self.assertEqual(number.returncode, 0, number.stderr.decode())
        number_out = number.stdout.decode()
        self.assertIn("### Recall number query", number_out)
        self.assertIn("RecallNumber=21-128", number_out)
        self.assertIn("#### Recall 21-128", number_out)
        self.assertIn("- Hazard as shown:", number_out)


if __name__ == "__main__":
    unittest.main()
