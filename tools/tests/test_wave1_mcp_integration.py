"""Offline MCP byte equality pass over the wave 1 tools (issue #227).

Run:  python3 -m unittest discover -s tools/tests -p 'test_wave1_mcp_integration.py' -v

The MCP side of tools/tests/test_wave1_integration.py (issue #219), which
does the same for the API routes. Every call goes through
mcp_server.recall_mcp.serve, the stdio transport itself: a JSON-RPC
tools/call line is written in and the response line is read back and parsed,
so the text checked is the text an MCP client receives. The ten wave 1 tools,
by the names registered in mcp_server/recall_mcp.py:

    domain_trust_check ofac_sanctions_check vin_decode_check
    clinical_trial_check fda_drug_check broken_link_check meta_tag_check
    github_repo_check app_lookup_check exchange_rate_check

Each tool reuses its route's fixture serving and command line run from
test_wave1_integration.py, so the capture, its provenance, the CLI inputs and
the dispatcher's title block are the ones that pass already uses. For each
tool:

1. Same text (one test per tool). The tool's text is byte for byte what the
   fetcher's command line prints for the same fixture input, after the
   dispatcher's title block where the API route adds one (the MCP tool calls
   the same dispatcher), with isError false.
2. Bad arguments. Arguments the tool must refuse answer isError true with a
   "Bad request: " message, and no fetch is made.
3. Unavailable source. A source failure answers isError true with no report.

A coverage test fails if a wave 1 tool is missing from the pass, from the
server's TOOL_NAMES, or from tools/list.

Not driven offline: none. NOT_DRIVEN below is the named, counted list of
wave 1 tools this pass could not serve from the existing fixtures; it is
empty, and a test pins its count, so a tool can only leave the equality
pass by being named there.

No network is used: urllib.request.urlopen is replaced, for every test, by a
function that fails the test, and each tool's fetch functions are replaced
by the recorded captures.
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
import test_wave1_integration as api_pass  # noqa: E402

ROUTE = {r.path: r for r in api_pass.ROUTES}

# tool name: (the route whose dispatcher it calls, the arguments matching the
# route's query and CLI inputs, arguments the tool must refuse)
TOOLS = {
    "domain_trust_check": ("/domain", {"domain": "example.com"},  # example domain fixture
                           [{}, {"domain": "https://example.com/"}, {"domain": "example"},  # example domain fixture
                            {"domain": 7}, {"domain": "example.com", "extra": "x"}]),  # example domain fixture
    "ofac_sanctions_check": ("/ofac", {"name": "National Bank of Cuba"},
                             [{}, {"name": "ab"}, {"name": "a.b"}, {"name": ["National Bank of Cuba"]}]),
    "vin_decode_check": ("/vin", {"vin": "1HGCM82633A004352"},
                         [{}, {"vin": "1HGCM/2633A004352"}, {"vin": "1HGCM82633A0043521"},
                          {"vin": "1HGCM82633A004352", "model_year": "03"},
                          {"vin": "1HGCM82633A004352", "model_year": 2003}]),
    "clinical_trial_check": ("/trials", {"term": "elivaldogene", "limit": 5},
                             [{}, {"term": "Zolgensma", "limit": 0}, {"term": "Zolgensma", "limit": 101},
                              {"term": "Zolgensma", "limit": "5"}, {"term": "Zolgensma", "limit": True}]),
    "fda_drug_check": ("/drug", {"name": "Tylenol"},
                       [{}, {"name": ""}, {"name": 'say "cheese"'}, {"name": None}]),
    "broken_link_check": ("/links", {"url": api_pass.t_links.PAGE_URL},
                          [{}, {"url": "notaurl"}, {"url": "ftp://example.com/"},  # example URL fixtures
                           {"url": ["https://a.example/"]}]),
    "meta_tag_check": ("/meta", {"url": "https://ogp.me/"},
                       [{}, {"url": "notaurl"}, {"url": "https://ogp.me/", "page": "x"}]),
    "github_repo_check": ("/github", {"owner": "psf", "repo": "requests"},
                          [{}, {"owner": "psf"}, {"owner": "psf/x", "repo": "y"}]),
    "app_lookup_check": ("/app", {"name": "Nike", "limit": 5},
                         [{}, {"name": "Nike", "country": "usa"}, {"name": "Nike", "limit": 0},
                          {"name": "Nike", "limit": 201}, {"name": "Nike", "limit": "5"}]),
    "exchange_rate_check": ("/fx", {"base": "USD", "target": "EUR"},
                            [{}, {"base": "USD"}, {"target": "EUR"}, {"base": "US", "target": "EUR"},
                             {"base": "USD", "target": "usd"}, {"base": "USD", "target": "EUR", "amount": "0"},
                             {"base": "USD", "target": "EUR", "date": "2024-13-01"},
                             {"base": "USD", "target": "EUR", "amount": 100}]),
}

WAVE1 = tuple(TOOLS)

# Wave 1 tools this pass could not drive offline from the existing fixtures,
# each with the reason. Their equality is not asserted. Empty: all ten run.
NOT_DRIVEN = {}


def no_network(*args, **kwargs):
    raise AssertionError("the wave 1 MCP pass tried to reach the network")


def call(name, arguments, req_id=1):
    """One tools/call over the stdio transport; returns the parsed result."""
    line = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": "tools/call",
                       "params": {"name": name, "arguments": arguments}})
    out, err = io.StringIO(), io.StringIO()
    recall_mcp.serve(io.StringIO(line + "\n"), out, stderr=err)
    response = json.loads(out.getvalue())
    if "result" not in response:
        raise AssertionError("no result for %s: %r (stderr %r)" % (name, response, err.getvalue()))
    return response["result"]


def text_of(result):
    content = result["content"]
    if len(content) != 1 or content[0]["type"] != "text":
        raise AssertionError("expected one text block, got %r" % content)
    return content[0]["text"]


class Wave1McpIntegration(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)

    def test_the_pass_covers_every_wave1_tool_on_main(self):
        self.assertEqual(sorted(path for path, _, _ in TOOLS.values()), sorted(api_pass.WAVE1))
        listed = recall_mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, None)
        names = [tool["name"] for tool in listed["result"]["tools"]]
        for name in WAVE1:
            self.assertIn(name, recall_mcp.TOOL_NAMES)
            self.assertIn(name, names)

    def test_the_not_driven_list_is_named_and_counted(self):
        self.assertEqual(len(NOT_DRIVEN), 0)
        self.assertTrue(set(NOT_DRIVEN) <= set(TOOLS))

    def test_each_refused_argument_set_is_bad_request_with_no_fetch(self):
        for name, (path, _, bad) in TOOLS.items():
            for arguments in bad:
                with self.subTest(tool=name, arguments=arguments), ROUTE[path].block_fetch():
                    result = call(name, arguments)
                    self.assertTrue(result["isError"], text_of(result)[:300])
                    self.assertTrue(text_of(result).startswith("Bad request: "), text_of(result)[:300])

    def test_each_source_failure_is_an_error_with_no_report(self):
        for name, (path, good, _) in TOOLS.items():
            with self.subTest(tool=name), ROUTE[path].break_source():
                result = call(name, good)
            text = text_of(result)
            self.assertTrue(result["isError"], text[:300])
            self.assertNotIn("\n## ", text)
            self.assertFalse(text.startswith("#"), text[:300])


def same_text(name):
    path, arguments, _ = TOOLS[name]
    route = ROUTE[path]

    def test(self):
        code, own, err = route.own()
        self.assertEqual(code, 0, err)
        with route.serve():
            result = call(name, arguments)
        self.assertFalse(result["isError"], text_of(result)[:300])
        expected = own if route.head is None else "\n".join(route.head) + "\n" + own
        self.assertEqual(text_of(result), expected)
    test.__doc__ = "%s: the tool text is the fetcher's own Markdown" % name
    return test


for _name in WAVE1:
    if _name not in NOT_DRIVEN:
        setattr(Wave1McpIntegration, "test_text_is_the_fetchers_own_markdown_%s" % _name, same_text(_name))


if __name__ == "__main__":
    unittest.main()
