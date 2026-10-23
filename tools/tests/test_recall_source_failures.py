"""Source failures in recall_check fail honestly (issue #118). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_recall_source_failures.py' -v

A recall_check whose source cannot be fetched or read must answer an
error that names the source, the exact query and the real reason, never
a bare error and never a report. Each failure mode is produced offline:

- curl missing from the host (FileNotFoundError from subprocess.run),
- curl past its 35 second limit (subprocess.TimeoutExpired),
- curl exiting non zero, with curl's own --show-error line on stderr,
- a CPSC response the fetcher cannot read (a non 200 capture),
- NHTSA refused, timed out at connect or at read, or cut off mid response.

The curl stderr line and the proxy refusal text below are the messages
curl and urllib printed in the #118 diagnosis run from the build
environment (2026-10-23T17:29:48Z), copied as printed. The CPSC capture
used for the unreadable case is the recorded instant-pot.http fixture
with its status line replaced, labelled as a synthetic edit.
"""

import http.client
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import recall_api  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402
from tools import cpsc_recalls, nhtsa_recalls  # noqa: E402

FIXTURES = ROOT / "tools" / "tests" / "fixtures"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))

VORNADO_URL = cpsc_recalls.query_url("Vornado VH101")
CURL_56 = b"curl: (56) CONNECT tunnel failed, response 403\n"
PROXY_REFUSAL = "Tunnel connection failed: 403 Forbidden"
VEHICLE = {"make": ["Honda"], "model": ["Accord"], "year": ["2018"]}
VEHICLE_URL = nhtsa_recalls.build_url(
    nhtsa_recalls.DEFAULT_ENDPOINT, [("make", "Honda"), ("model", "Accord"), ("modelYear", "2018")])


def curl_result(code, stderr=b""):
    return subprocess.CompletedProcess([], code, b"", stderr)


def rpc_call(arguments):
    """One recall_check tools/call through the server loop; returns the result."""
    message = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
               "params": {"name": "recall_check", "arguments": arguments}}
    stdout = io.StringIO()
    recall_mcp.serve(io.StringIO(json.dumps(message) + "\n"), stdout, None, io.StringIO())
    return json.loads(stdout.getvalue().splitlines()[0])["result"]


class CurlReasonTests(unittest.TestCase):
    """tools/cpsc_recalls.fetch says which way curl failed."""

    def assert_fetch_error(self, needle, **run):
        with patch.object(cpsc_recalls.subprocess, "run", **run):
            with self.assertRaises(cpsc_recalls.FetchError) as caught:
                cpsc_recalls.fetch("Vornado VH101")
        self.assertIn(needle, str(caught.exception))
        self.assertIn("no recall conclusion", str(caught.exception))
        return str(caught.exception)

    def test_missing_curl_is_named_as_missing(self):
        text = self.assert_fetch_error("curl is not installed on this host (not found on PATH)",
                                       side_effect=FileNotFoundError(2, "No such file or directory", "curl"))
        self.assertNotIn("timed out", text)

    def test_timeout_is_named_as_a_timeout(self):
        text = self.assert_fetch_error("curl did not finish within 35 seconds",
                                       side_effect=subprocess.TimeoutExpired("curl", 35))
        self.assertNotIn("not installed", text)

    def test_other_start_failure_keeps_its_reason(self):
        self.assert_fetch_error("curl could not be started", side_effect=PermissionError(13, "Permission denied"))

    def test_exit_code_carries_curls_own_error_line(self):
        self.assert_fetch_error("curl failed (exit 56: curl: (56) CONNECT tunnel failed, response 403)",
                                return_value=curl_result(56, CURL_56))

    def test_exit_code_without_stderr_still_names_the_code(self):
        self.assert_fetch_error("curl failed (exit 28)", return_value=curl_result(28))

    def test_long_stderr_is_cut_to_one_short_line(self):
        text = self.assert_fetch_error("curl failed (exit 6: ",
                                       return_value=curl_result(6, b"curl: (6) " + b"x" * 1000 + b"\nsecond\n"))
        self.assertNotIn("\n", text)
        self.assertLess(len(text), 400)


class ProductSourceFailureTests(unittest.TestCase):
    """The product form names CPSC, the query and the reason; no report."""

    def test_recall_raises_source_failed_naming_cpsc_and_the_query(self):
        with patch.object(cpsc_recalls.subprocess, "run", return_value=curl_result(56, CURL_56)):
            with self.assertRaises(recall_api.SourceFailed) as caught:
                recall_api.recall({"product": ["Vornado VH101"]})
        err = caught.exception
        self.assertEqual(err.source, "CPSC SaferProducts recall API")
        self.assertEqual(err.url, VORNADO_URL)
        self.assertEqual(
            str(err),
            "Fetch failed, no report emitted: the CPSC SaferProducts recall API could not be read "
            "(curl failed (exit 56: curl: (56) CONNECT tunnel failed, response 403); no recall conclusion). "
            "Query: GET " + VORNADO_URL)

    def test_unreadable_response_is_a_source_failure_too(self):
        meta = PROVENANCE["instant-pot.http"]
        raw = (FIXTURES / "instant-pot.http").read_bytes().decode("utf-8")
        # SYNTHETIC edit of the recorded capture: only the status line changes.
        edited = "HTTP/1.1 503 Service Unavailable" + raw[raw.index("\r\n"):]
        capture = cpsc_recalls.Capture(meta["url"], meta["retrieved_utc"], edited)
        with patch.object(cpsc_recalls, "fetch", return_value=capture):
            with self.assertRaises(recall_api.SourceFailed) as caught:
                recall_api.recall({"product": ["Instant Pot"]})
        self.assertIn("Expected HTTP 200", str(caught.exception))
        self.assertIn("Query: GET " + meta["url"], str(caught.exception))

    def test_a_failed_near_search_names_its_own_query(self):
        meta = PROVENANCE["instant-pot.http"]
        good = cpsc_recalls.Capture(meta["url"], meta["retrieved_utc"],
                                    (FIXTURES / "instant-pot.http").read_bytes().decode("utf-8"))
        failure = cpsc_recalls.FetchError("curl failed (exit 7); no recall conclusion")
        with patch.object(cpsc_recalls, "fetch", side_effect=[good, failure]):
            with self.assertRaises(recall_api.SourceFailed) as caught:
                recall_api.recall({"product": ["Instant Pot"], "exact_name": ["Instant Pot"],
                                   "near": ["Instant Pot Duo"]})
        self.assertEqual(caught.exception.url, cpsc_recalls.query_url("Instant Pot Duo"))

    def test_mcp_tool_error_is_the_named_message_and_no_report(self):
        with patch.object(cpsc_recalls.subprocess, "run", return_value=curl_result(56, CURL_56)):
            result = rpc_call({"product": "Vornado VH101"})
        self.assertTrue(result["isError"])
        text = result["content"][0]["text"]
        self.assertTrue(text.startswith("Fetch failed, no report emitted: the CPSC SaferProducts recall API"))
        self.assertIn("Query: GET " + VORNADO_URL, text)
        self.assertNotIn("# Recall check", text)

    def test_http_api_answers_502_with_the_same_message(self):
        with patch.object(cpsc_recalls.subprocess, "run",
                          side_effect=FileNotFoundError(2, "No such file or directory", "curl")):
            status, _, body = recall_api.handle("GET", "/recall", "product=Vornado+VH101", None)
        self.assertEqual(status, "502 Bad Gateway")
        self.assertIn("the CPSC SaferProducts recall API could not be read "
                      "(curl is not installed on this host (not found on PATH)", body.decode("utf-8"))


class VehicleSourceFailureTests(unittest.TestCase):
    """The vehicle form names NHTSA, the query and the reason; no report."""

    def failure(self, exc):
        with patch.object(nhtsa_recalls, "fetch", side_effect=exc):
            with self.assertRaises(recall_api.SourceFailed) as caught:
                recall_api.recall(VEHICLE)
        self.assertEqual(caught.exception.source, "NHTSA recalls API")
        self.assertEqual(caught.exception.url, VEHICLE_URL)
        return str(caught.exception)

    def test_refused_connection_names_nhtsa_and_the_reason(self):
        text = self.failure(urllib.error.URLError(PROXY_REFUSAL))
        self.assertEqual(text, "Fetch failed, no report emitted: the NHTSA recalls API could not be read "
                               "(Tunnel connection failed: 403 Forbidden). Query: GET " + VEHICLE_URL)

    def test_connect_timeout_and_read_timeout_say_timed_out(self):
        expected = "no answer within %d seconds" % nhtsa_recalls.TIMEOUT_SECONDS
        self.assertIn(expected, self.failure(urllib.error.URLError(TimeoutError("timed out"))))
        self.assertIn(expected, self.failure(TimeoutError("The read operation timed out")))

    def test_response_cut_off_names_the_exception(self):
        text = self.failure(http.client.RemoteDisconnected("Remote end closed connection without response"))
        self.assertIn("RemoteDisconnected: Remote end closed connection without response", text)

    def test_mcp_vehicle_tool_error_names_nhtsa(self):
        with patch.object(nhtsa_recalls, "fetch", side_effect=urllib.error.URLError(PROXY_REFUSAL)):
            result = rpc_call({"make": "Honda", "model": "Accord", "year": "2018"})
        self.assertTrue(result["isError"])
        self.assertIn("the NHTSA recalls API could not be read (Tunnel connection failed: 403 Forbidden)",
                      result["content"][0]["text"])
        self.assertIn("Query: GET " + VEHICLE_URL, result["content"][0]["text"])


class StdioWithoutCurlTests(unittest.TestCase):
    """The real entry point on a host with no curl on PATH: the tool names
    the missing binary. Nothing is fetched, because curl cannot start."""

    def test_stdio_recall_check_without_curl_names_the_cause(self):
        with tempfile.TemporaryDirectory() as empty_path:
            env = dict(os.environ, PATH=empty_path)
            env.pop(recall_api.PAYOUT_ENV, None)
            message = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                       "params": {"name": "recall_check", "arguments": {"product": "Vornado VH101"}}}
            proc = subprocess.run([sys.executable, "-m", "mcp_server"], cwd=str(ROOT), env=env,
                                  input=json.dumps(message) + "\n", capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout.splitlines()[0])["result"]
        self.assertTrue(result["isError"])
        self.assertEqual(
            result["content"][0]["text"],
            "Fetch failed, no report emitted: the CPSC SaferProducts recall API could not be read "
            "(curl is not installed on this host (not found on PATH); no recall conclusion). "
            "Query: GET " + VORNADO_URL)


if __name__ == "__main__":
    unittest.main()
