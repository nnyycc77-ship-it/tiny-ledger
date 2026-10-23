"""Tests for mcp_server/recall_mcp.py. No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_recall_mcp.py' -v

The fetchers are patched to return recorded public responses that
already live in this repo with their provenance: the CPSC captures in
tools/tests/fixtures (verbatim HTTP captures; URLs, retrieval times and
SHA-256 digests in provenance.json) and the NHTSA S24 excerpt from the
published recall delivery, carried by test_nhtsa_recalls.py. No recall
data is invented here. The in-process tests drive the server loop over
JSON-RPC through StringIO streams; the subprocess test runs the real
entry point over stdio pipes for the methods that need no fetch.
"""

import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api import recall_api  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402
from tools import cpsc_recalls, nhtsa_recalls  # noqa: E402
import test_nhtsa_recalls as nhtsa_fixtures  # noqa: E402

FIXTURES = ROOT / "tools" / "tests" / "fixtures"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))
WALLET = "0x" + "ab" * 20


def captured(name):
    meta = PROVENANCE[name]
    return cpsc_recalls.Capture(meta["url"], meta["retrieved_utc"],
                                (FIXTURES / name).read_bytes().decode("utf-8"))


def fake_cpsc_fetch(product):
    for name, meta in PROVENANCE.items():
        if meta["url"] == cpsc_recalls.query_url(product):
            return captured(name)
    raise cpsc_recalls.FetchError("no recorded capture for %r" % product)


def fake_nhtsa_fetch(url):
    body = nhtsa_fixtures.S24_HEAD_CLOSED
    return nhtsa_fixtures.RETRIEVED, nhtsa_fixtures.transcript_for(body), body


def rpc(messages, wallet=None):
    """Run the server loop over the given messages; return the responses."""
    stdin = io.StringIO("".join(json.dumps(m) + "\n" if not isinstance(m, str) else m + "\n" for m in messages))
    stdout, stderr = io.StringIO(), io.StringIO()
    recall_mcp.serve(stdin, stdout, wallet, stderr)
    return [json.loads(line) for line in stdout.getvalue().splitlines() if line.strip()], stderr.getvalue()


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}}}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}


def call(req_id, arguments):
    return {"jsonrpc": "2.0", "id": req_id, "method": "tools/call", "params": {"name": "recall_check", "arguments": arguments}}


class ProtocolTests(unittest.TestCase):
    def test_initialize_echoes_known_version_and_lists_the_tool(self):
        responses, err = rpc([INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                              {"jsonrpc": "2.0", "id": 3, "method": "ping"}])
        self.assertEqual(err, "")
        self.assertEqual([r["id"] for r in responses], [1, 2, 3])  # the notification got no answer
        init = responses[0]["result"]
        self.assertEqual(init["protocolVersion"], "2025-06-18")
        self.assertEqual(init["serverInfo"]["name"], recall_mcp.SERVER_NAME)
        self.assertIn("tools", init["capabilities"])
        tools = responses[1]["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["recall_check"])
        schema = tools[0]["inputSchema"]
        self.assertEqual(sorted(schema["properties"]), ["exact_name", "exclude", "make", "model", "near", "product", "year"])
        self.assertFalse(schema["additionalProperties"])
        self.assertIn(cpsc_recalls.ENDPOINT, tools[0]["description"])
        self.assertEqual(responses[2]["result"], {})

    def test_unknown_version_gets_newest_known(self):
        responses, _ = rpc([{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}}])
        self.assertEqual(responses[0]["result"]["protocolVersion"], recall_mcp.PROTOCOL_VERSIONS[0])

    def test_wallet_appears_only_when_set(self):
        responses, _ = rpc([INIT, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}], wallet=WALLET)
        self.assertIn(WALLET, responses[0]["result"]["instructions"])
        self.assertIn(WALLET, responses[1]["result"]["tools"][0]["description"])
        responses, _ = rpc([INIT, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}])
        self.assertNotIn("0x", responses[0]["result"]["instructions"])
        self.assertNotIn("Payment", responses[1]["result"]["tools"][0]["description"])

    def test_errors_follow_jsonrpc(self):
        responses, _ = rpc([{"jsonrpc": "2.0", "id": 5, "method": "resources/list"},
                            "this is not json",
                            {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "other_tool"}},
                            {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {}},
                            {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 1}},
                            {"jsonrpc": "2.0", "id": 8, "method": "ping"}])
        self.assertEqual(responses[0]["error"]["code"], recall_mcp.JSONRPC_METHOD_NOT_FOUND)
        self.assertEqual(responses[1]["error"]["code"], recall_mcp.JSONRPC_PARSE_ERROR)
        self.assertIsNone(responses[1]["id"])
        self.assertEqual(responses[2]["error"]["code"], recall_mcp.JSONRPC_INVALID_PARAMS)
        self.assertEqual(responses[3]["error"]["code"], recall_mcp.JSONRPC_INVALID_PARAMS)
        self.assertEqual(responses[4], {"jsonrpc": "2.0", "id": 8, "result": {}})
        self.assertEqual(len(responses), 5)


class ProductFormTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(cpsc_recalls, "fetch", side_effect=fake_cpsc_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_empty_result_is_proven_and_matches_the_api_text(self):
        args = {"product": "Instant Pot Smart WiFi"}
        responses, _ = rpc([INIT, INITIALIZED, call(2, args)])
        result = responses[1]["result"]
        self.assertFalse(result["isError"])
        text = result["content"][0]["text"]
        self.assertEqual(result["content"][0]["type"], "text")
        # Same dispatcher, same text as the API for the same query.
        self.assertEqual(text, recall_api.recall({"product": ["Instant Pot Smart WiFi"]}))
        cap = captured("smart-wifi.http")
        self.assertIn("Exact query: GET " + cap.url, text)
        self.assertIn("Retrieved (UTC): " + cap.retrieved, text)
        self.assertIn("CPSC returned 0 record(s) for this query.", text)
        marker = "Source: <%s>\n```\n" % cap.url
        self.assertIn(marker, text)
        self.assertTrue(text.split(marker, 1)[1].startswith(cap.raw))
        self.assertTrue(cap.raw.endswith("\r\n\r\n[]"))

    def test_near_match_checked_and_excluded_matches_the_api_text(self):
        args = {"product": "Instant Pot Smart WiFi", "exact_name": "Instant Pot Smart WiFi", "near": ["Instant Pot"]}
        responses, _ = rpc([call(2, args)])
        text = responses[0]["result"]["content"][0]["text"]
        self.assertEqual(text, recall_api.recall({"product": ["Instant Pot Smart WiFi"],
                                                  "exact_name": ["Instant Pot Smart WiFi"], "near": ["Instant Pot"]}))
        self.assertIn("### Checked near-match query", text)
        self.assertIn("- Checked and excluded: recall ", text)
        self.assertIn("Reason: none of the returned product names equals", text)

    def test_bad_requests_are_tool_errors_not_reports(self):
        for args, needle in [
            ({"product": "Instant Pot", "near": ["Instant Pot"]}, "near requires exact_name"),
            ({"product": "Instant Pot", "make": "Hyundai"}, "either product, or make+model+year"),
            ({}, "give product=<name>"),
            ({"product": 5}, "product must be a string"),
            ({"near": "x", "product": "Instant Pot", "exact_name": "Instant Pot"}, "near must be an array of strings"),
            ({"product": "Instant Pot", "colour": "red"}, "unknown argument(s): colour"),
        ]:
            with self.subTest(args=args):
                responses, _ = rpc([call(2, args)])
                result = responses[0]["result"]
                self.assertTrue(result["isError"])
                self.assertIn(needle, result["content"][0]["text"])
                self.assertNotIn("CPSC returned", result["content"][0]["text"])

    def test_fetch_failure_is_a_tool_error_with_no_report(self):
        with patch.object(cpsc_recalls, "fetch", side_effect=cpsc_recalls.FetchError("curl failed (exit 6); no recall conclusion")):
            responses, _ = rpc([call(2, {"product": "Instant Pot"})])
        result = responses[0]["result"]
        self.assertTrue(result["isError"])
        self.assertIn("Fetch failed, no report emitted", result["content"][0]["text"])
        self.assertNotIn("CPSC returned", result["content"][0]["text"])


class VehicleFormTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(nhtsa_recalls, "fetch", side_effect=fake_nhtsa_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_vehicle_report_matches_the_api_text(self):
        args = {"make": "Hyundai", "model": "Elantra", "year": "2021"}
        responses, _ = rpc([call(2, args)])
        result = responses[0]["result"]
        self.assertFalse(result["isError"])
        text = result["content"][0]["text"]
        self.assertEqual(text, recall_api.recall({"make": ["Hyundai"], "model": ["Elantra"], "year": ["2021"]}))
        self.assertIn("- Query URL: " + nhtsa_fixtures.ELANTRA_URL, text)
        self.assertIn("- Retrieved (UTC): " + nhtsa_fixtures.RETRIEVED, text)
        self.assertIn("#### Campaign 21V796000", text)

    def test_exclusion_with_reason_and_refusal(self):
        responses, _ = rpc([call(2, {"make": "Hyundai", "model": "Elantra", "year": "2021",
                                     "exclude": ["21V796000=replaced by 22V354000, which is listed"]})])
        text = responses[0]["result"]["content"][0]["text"]
        self.assertFalse(responses[0]["result"]["isError"])
        self.assertIn("- Checked and excluded because: replaced by 22V354000, which is listed", text)
        responses, _ = rpc([call(3, {"make": "Hyundai", "model": "Elantra", "year": "2021", "exclude": ["24V879000=not here"]})])
        self.assertTrue(responses[0]["result"]["isError"])
        self.assertIn("excluded campaign number(s) not in the response", responses[0]["result"]["content"][0]["text"])

    def test_incomplete_vehicle_is_a_tool_error(self):
        responses, _ = rpc([call(2, {"make": "Hyundai", "model": "Elantra"})])
        self.assertTrue(responses[0]["result"]["isError"])
        self.assertIn("missing: year", responses[0]["result"]["content"][0]["text"])

    def test_transport_failure_is_a_tool_error(self):
        import urllib.error
        with patch.object(nhtsa_recalls, "fetch", side_effect=urllib.error.URLError("blocked")):
            responses, _ = rpc([call(2, {"make": "Hyundai", "model": "Elantra", "year": "2021"})])
        self.assertTrue(responses[0]["result"]["isError"])
        self.assertIn("Fetch failed, no report emitted", responses[0]["result"]["content"][0]["text"])


class StdioEntryPointTests(unittest.TestCase):
    """The real entry point over pipes, for the methods that need no fetch."""

    def _run(self, messages, env_extra=None):
        env = dict(os.environ)
        env.pop(recall_api.PAYOUT_ENV, None)
        env.update(env_extra or {})
        proc = subprocess.run([sys.executable, "-m", "mcp_server"], cwd=str(ROOT), env=env,
                              input="".join(json.dumps(m) + "\n" for m in messages),
                              capture_output=True, text=True, timeout=60)
        return proc

    def test_initialize_and_list_over_stdio(self):
        proc = self._run([INIT, INITIALIZED, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
        self.assertEqual([l["id"] for l in lines], [1, 2])
        self.assertEqual(lines[1]["result"]["tools"][0]["name"], "recall_check")
        self.assertIn("payout wallet: (not set)", proc.stderr)
        # stdout carries protocol lines only
        for line in proc.stdout.splitlines():
            json.loads(line)

    def test_wallet_from_environment_and_refusal_of_a_malformed_one(self):
        proc = self._run([INIT], {recall_api.PAYOUT_ENV: WALLET})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(WALLET, json.loads(proc.stdout.splitlines()[0])["result"]["instructions"])
        proc = self._run([INIT], {recall_api.PAYOUT_ENV: "0x1234"})
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")
        self.assertIn("refusing to start", proc.stderr)


if __name__ == "__main__":
    unittest.main()
