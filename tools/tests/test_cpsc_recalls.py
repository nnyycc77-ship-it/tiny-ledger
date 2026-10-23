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


if __name__ == "__main__":
    unittest.main()
