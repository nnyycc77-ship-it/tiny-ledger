"""Offline MCP byte equality pass for faa_lookup (issue #234).

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcp_faa_integration.py' -v

In the pattern of the merged wave 1 and wave 2 MCP passes
(tools/tests/test_wave1_mcp_integration.py and
tools/tests/test_mcp_wave2_integration.py), for faa_lookup, the twenty
fifth tool, registered on the MCP surface after those passes landed
(issue #210). The wave 2 MCP pass covers faa_lookup among its nine
tools through call_tool; this module is its dedicated pass, driving the
stdio transport itself in the wave 1 pass's pattern, so the text checked
is the text an MCP client receives.

Every call goes through mcp_server.recall_mcp.serve: a JSON-RPC
tools/call line is written in and the response line is read back and
parsed. The fixture serving, the command line run and the dispatcher's
title block are the Faa route's from tools/tests/test_wave2_integration.py
(issue #212), so the capture, its provenance and the CLI inputs are the
ones that pass already uses: the FAA archive assembled from the recorded
captures in tools/tests/test_faa_lookup.py, downloaded into a fresh
cache by the route's own hand.

For faa_lookup:

1. Same text. The tool's text is byte for byte the dispatcher's title
   block followed by what the fetcher's command line prints for the
   same fixture input (N100ZT), with isError false.
2. Bad arguments. Arguments the tool must refuse answer isError true
   with a "Bad request: " message, and no fetch is made: the route's
   download is replaced by one that fails the test if it is called.
3. Unavailable source. A source failure (the route's refused download)
   answers isError true with no report.

Not driven offline: none. NOT_DRIVEN below is the named, counted list
of tools this pass could not serve from the existing fixtures; it is
empty, a test pins its count, and the coverage test accounts for the
one tool of this pass exactly once, so the tool can only leave the
equality pass by being named there.

No network is used: urllib.request.urlopen is replaced, for every test,
by a function that fails the test, and the archive download is the
route's fixture hand.
"""

import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
for path in (str(ROOT), str(ROOT / "tools" / "tests")):
    if path not in sys.path:
        sys.path.insert(0, path)

from mcp_server import recall_mcp  # noqa: E402
import test_wave2_integration as api_pass  # noqa: E402

ROUTE = {r.path: r for r in api_pass.ROUTES}["/faa"]

# tool name: (the arguments matching the route's query and CLI inputs,
# arguments the tool must refuse)
TOOLS = {
    "faa_lookup": ({"n_number": "N100ZT"},
                   [{}, {"n_number": "N"}, {"n_number": "N10-0Z"}, {"n_number": "N1234567"},
                    {"n_number": 100}, {"n_number": "N100ZT", "extra": "x"}]),
}

# Tools this pass could not drive offline from the existing fixtures,
# each with the reason. Their equality is not asserted. Empty: it runs.
NOT_DRIVEN = {}


def no_network(*args, **kwargs):
    raise AssertionError("the faa MCP pass tried to reach the network")


def call(name, arguments, req_id=1):
    """One tools/call over the stdio transport; returns the parsed result."""
    line = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": "tools/call",
                       "params": {"name": name, "arguments": arguments}})
    out, err = io.StringIO(), io.StringIO()
    recall_mcp.serve(io.StringIO(line + "\n"), out, stderr=err)
    response = json.loads(out.getvalue())
    assert response["id"] == req_id and "result" in response, out.getvalue()
    return response["result"]


def tool_list():
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    out, err = io.StringIO(), io.StringIO()
    recall_mcp.serve(io.StringIO(line + "\n"), out, stderr=err)
    return json.loads(out.getvalue())["result"]["tools"]


def text_of(result):
    return result["content"][0]["text"]


class FaaMcpIntegration(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_the_pass_covers_faa_lookup_and_counts_what_it_does_not_drive(self):
        self.assertEqual(sorted(list(TOOLS) + sorted(NOT_DRIVEN)), ["faa_lookup"])
        self.assertEqual(len(NOT_DRIVEN), 0)
        self.assertIn("faa_lookup", recall_mcp.TOOL_NAMES)
        self.assertIn("faa_lookup", [t["name"] for t in tool_list()])

    def test_tool_text_is_the_fetchers_own_markdown(self):
        code, own, err = ROUTE.own()
        self.assertEqual(code, 0, err)
        with ROUTE.serve():
            result = call("faa_lookup", TOOLS["faa_lookup"][0])
        self.assertFalse(result["isError"], text_of(result)[:300])
        expected = "\n".join(ROUTE.head) + "\n" + own
        self.assertEqual(text_of(result), expected)

    def test_refused_arguments_are_tool_errors_with_no_fetch(self):
        for arguments in TOOLS["faa_lookup"][1]:
            with self.subTest(arguments=arguments), ROUTE.block_fetch():
                result = call("faa_lookup", arguments)
            self.assertTrue(result["isError"], text_of(result)[:300])
            self.assertTrue(text_of(result).startswith("Bad request: "), text_of(result)[:300])

    def test_source_failure_is_a_tool_error_with_no_report(self):
        with ROUTE.break_source():
            result = call("faa_lookup", TOOLS["faa_lookup"][0])
        self.assertTrue(result["isError"], text_of(result)[:300])
        self.assertNotIn("\n## ", text_of(result))
        self.assertFalse(text_of(result).startswith("#"), text_of(result)[:300])


if __name__ == "__main__":
    unittest.main()
