"""Contract test for the MCP server's tool surface (issue #138). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcp_tool_surface.py' -v

The outside verification in docs/mcpize-redeploy-runbook.md (PR #126)
expects the hosted server, once redeployed, to list a fixed set of tools by
name. This test boots the real entry point (`python -m mcp_server`) over
stdio pipes and checks the same surface locally:

- `tools/list` names exactly the seven tools, in order, and that list
  equals both `recall_mcp.TOOL_NAMES` in the server code and the list the
  runbook's outside verification expects;
- `initialize` reports the server name and the version the runbook expects;
- a `recall_check` whose source fails in a controlled offline way answers
  a tool error naming the source, the exact query and the reason (the
  failure naming merged in PR #121), with no report.

The two controlled failures need no network. The CPSC product form runs
with a PATH that holds no curl, so the fetcher cannot start. The NHTSA
vehicle form runs with HTTPS_PROXY pointing at a local port that was bound
and then closed, so the connection is refused on this machine.
"""

import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import recall_api  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402
from tools import cpsc_recalls, nhtsa_recalls  # noqa: E402

RUNBOOK = ROOT / "docs" / "mcpize-redeploy-runbook.md"

# The surface, written out by hand from the server code so that a renamed,
# dropped or added tool fails this test instead of passing silently.
EXPECTED_TOOLS = ["recall_check", "carrier_check", "litigation_screen",
                  "formd_check", "nonprofit_check", "awards_search", "pagespeed_snapshot"]

INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "contract-test", "version": "0"}}}
INITIALIZED = {"jsonrpc": "2.0", "method": "notifications/initialized"}
LIST = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}


def call(req_id, arguments):
    return {"jsonrpc": "2.0", "id": req_id, "method": "tools/call",
            "params": {"name": "recall_check", "arguments": arguments}}


def closed_local_port():
    """A port on 127.0.0.1 that nothing listens on: bound, then released."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(messages, **env_changes):
    """Run the real entry point over stdio; return {id: response} and stderr."""
    env = dict(os.environ)
    env.pop(recall_api.PAYOUT_ENV, None)
    for key, value in env_changes.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    proc = subprocess.run([sys.executable, "-m", "mcp_server"], cwd=str(ROOT), env=env,
                          input="".join(json.dumps(m) + "\n" for m in messages),
                          capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise AssertionError("server exited %d: %s" % (proc.returncode, proc.stderr))
    responses = {}
    for line in proc.stdout.splitlines():
        message = json.loads(line)  # stdout carries protocol lines only
        responses[message.get("id")] = message
    return responses, proc.stderr


class ToolSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.responses, cls.stderr = serve([INIT, INITIALIZED, LIST])
        cls.tools = cls.responses[2]["result"]["tools"]

    def test_tools_list_names_exactly_the_seven_tools_in_order(self):
        self.assertEqual([t["name"] for t in self.tools], EXPECTED_TOOLS)

    def test_the_list_is_the_server_codes_own(self):
        self.assertEqual(list(recall_mcp.TOOL_NAMES), EXPECTED_TOOLS)

    def test_the_list_is_the_one_the_redeploy_runbook_expects(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        found = re.search(r"Expected, in this order: `(\[.*?\])`", text, re.S)
        self.assertIsNotNone(found, "the runbook's expected tool list line is missing")
        runbook_tools = re.findall(r"'([a-z_]+)'", found.group(1))
        self.assertEqual(runbook_tools, EXPECTED_TOOLS)

    def test_initialize_reports_the_name_and_version_the_runbook_expects(self):
        info = self.responses[1]["result"]["serverInfo"]
        self.assertEqual(info, {"name": recall_mcp.SERVER_NAME, "version": recall_mcp.SERVER_VERSION})
        self.assertEqual(info["version"], "0.3.0")
        self.assertIn('version "0.3.0"', RUNBOOK.read_text(encoding="utf-8"))

    def test_every_tool_has_a_description_and_an_object_schema(self):
        for tool in self.tools:
            with self.subTest(tool=tool["name"]):
                self.assertTrue(tool["description"].strip())
                self.assertEqual(tool["inputSchema"]["type"], "object")
                self.assertFalse(tool["inputSchema"].get("additionalProperties", True))
                self.assertTrue(tool["inputSchema"]["properties"])


class FailureNamingTests(unittest.TestCase):
    """recall_check over the real stdio entry point, sources failed offline."""

    def assert_named_failure(self, result, source, url, reason):
        self.assertTrue(result["isError"])
        text = result["content"][0]["text"]
        self.assertEqual(text, "Fetch failed, no report emitted: the %s could not be read (%s). Query: GET %s"
                         % (source, reason, url))
        self.assertNotIn("# Recall check", text)

    def test_cpsc_source_failure_names_source_query_and_reason(self):
        with tempfile.TemporaryDirectory() as empty_path:
            responses, _ = serve([INIT, INITIALIZED, call(3, {"product": "VH101"})], PATH=empty_path)
        self.assert_named_failure(
            responses[3]["result"], recall_api.CPSC_SOURCE, cpsc_recalls.query_url("VH101"),
            "curl is not installed on this host (not found on PATH); no recall conclusion")

    def test_nhtsa_source_failure_names_source_query_and_reason(self):
        proxy = "http://127.0.0.1:%d" % closed_local_port()
        responses, _ = serve([INIT, INITIALIZED, call(3, {"make": "Honda", "model": "Accord", "year": "2018"})],
                             HTTPS_PROXY=proxy, https_proxy=proxy, NO_PROXY="", no_proxy="")
        result = responses[3]["result"]
        url = nhtsa_recalls.build_url(nhtsa_recalls.DEFAULT_ENDPOINT,
                                      [("make", "Honda"), ("model", "Accord"), ("modelYear", "2018")])
        self.assertTrue(result["isError"])
        text = result["content"][0]["text"]
        self.assertTrue(text.startswith("Fetch failed, no report emitted: the %s could not be read ("
                                        % recall_api.NHTSA_SOURCE), text)
        self.assertTrue(text.endswith("). Query: GET " + url), text)
        reason = text[len("Fetch failed, no report emitted: the %s could not be read (" % recall_api.NHTSA_SOURCE):
                      -len("). Query: GET " + url)]
        self.assertIn("refused", reason.lower())
        self.assertNotIn("# Recall check", text)


if __name__ == "__main__":
    unittest.main()
