"""Honesty checks for packaging/mcpize/. Standard library only, no network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcpize_listing.py' -v

The listing copy may only state what the merged server does. These tests
tie it to the code: the example in LISTING.md must equal, byte for byte,
what the real server renders from the recorded CPSC capture (fetcher
patched, no network); the tool name and every argument the listing names
must match the server's live tools/list schema; the track record paragraph
must match AGENT-BRIEF.md byte for byte; the manifest must name the entry
command and the tool and carry no pricing or wallet field; and no file in
the folder may claim that a deployment or listing has happened.
"""

import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp_server import recall_mcp  # noqa: E402
from tools import cpsc_recalls  # noqa: E402
import test_recall_mcp as mcp_tests  # noqa: E402

FOLDER = ROOT / "packaging" / "mcpize"
LISTING = (FOLDER / "LISTING.md").read_bytes().decode("utf-8")
DEPLOYMENT = (FOLDER / "DEPLOYMENT.md").read_text(encoding="utf-8")
README = (FOLDER / "README.md").read_text(encoding="utf-8")


def live_tools_list():
    out = io.StringIO()
    recall_mcp.serve(io.StringIO('{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n'), out, None, io.StringIO())
    return json.loads(out.getvalue())["result"]["tools"][0]


def rendered_example():
    with patch.object(cpsc_recalls, "fetch", side_effect=mcp_tests.fake_cpsc_fetch):
        out = io.StringIO()
        recall_mcp.serve(io.StringIO(json.dumps(mcp_tests.call(1, {"product": "Instant Pot Smart WiFi"})) + "\n"),
                         out, None, io.StringIO())
    return json.loads(out.getvalue())["result"]["content"][0]["text"]


class ListingTests(unittest.TestCase):
    def test_example_equals_the_server_output_for_the_recorded_capture(self):
        text = rendered_example()
        start = LISTING.index("````markdown\n") + len("````markdown\n")
        end = LISTING.index("````", start)
        self.assertEqual(LISTING[start:end], text)
        self.assertIn("\r\n", text)  # the capture's own line endings survive into the listing

    def test_example_provenance_matches_the_fixture_record(self):
        prov = json.loads((ROOT / "tools" / "tests" / "fixtures" / "provenance.json").read_text())["smart-wifi.http"]
        for key in ("url", "retrieved_utc", "sha256"):
            self.assertIn('"%s": "%s"' % (key, prov[key]), LISTING)

    def test_tool_name_and_schema_match_the_live_server(self):
        tool = live_tools_list()
        self.assertIn("`%s`" % tool["name"], LISTING)
        self.assertIn(json.dumps(tool["inputSchema"], indent=2), LISTING)
        for prop in tool["inputSchema"]["properties"]:
            self.assertIn("`%s`" % prop, LISTING, prop)
            self.assertIn("`%s`" % prop, DEPLOYMENT, prop)

    def test_track_record_paragraph_is_quoted_verbatim(self):
        brief = (ROOT / "AGENT-BRIEF.md").read_text(encoding="utf-8")
        start = brief.index("4. **Track record claims stay honest and current.**")
        end = brief.index("## Boundaries")
        quoted = "\n".join("> " + l if l else ">" for l in brief[start:end].rstrip("\n").split("\n"))
        self.assertIn(quoted, LISTING)

    def test_price_arithmetic_inputs_are_sourced_in_the_text(self):
        self.assertIn("six named consumer products", LISTING)
        self.assertIn("10 USD / 6 = 1.67 USD", LISTING)
        self.assertIn("not yet verified on the", LISTING)

    def test_entry_point_and_env_value_named_in_deployment_notes(self):
        self.assertIn("python3 -m mcp_server", DEPLOYMENT)
        self.assertIn("PAYOUT_WALLET_ADDRESS", DEPLOYMENT)
        self.assertIn("To confirm from the MCPize docs", DEPLOYMENT)

    def test_no_file_claims_a_deployment_or_listing_happened(self):
        for name, text in (("LISTING.md", LISTING), ("DEPLOYMENT.md", DEPLOYMENT), ("README.md", README)):
            self.assertIsNone(re.search(r"\b(is|was|has been|now) (deployed|live|listed|published) on MCPize\b", text), name)
            self.assertNotIn("0x" + "0" * 40, text, name)

    def test_manifest_names_entry_command_and_tool_and_holds_no_payout_fields(self):
        manifest = (FOLDER / "mcpize.yaml").read_text(encoding="utf-8")
        self.assertIn("command: python3 -m mcp_server", manifest)
        self.assertIn("entry: mcp_server/__main__.py", manifest)
        self.assertIn("type: stdio", manifest)
        self.assertIn("name: recall_check", manifest)
        self.assertIn("name: hojo-recall-check", manifest)
        self.assertIn("runtime: python3.12", manifest)
        # Pricing and the recipient wallet live in the MCPize dashboard, never here.
        for forbidden in ("pricing", "recipient", "wallet:", "price:", "0x"):
            self.assertNotIn(forbidden, manifest.lower() if forbidden == "pricing" else manifest, forbidden)
        self.assertEqual(sorted(p.name for p in FOLDER.iterdir()),
                         [".gitattributes", "DEPLOYMENT.md", "LISTING.md", "README.md", "mcpize.yaml"])

    def test_deployment_notes_quote_the_coordinator_reading_with_sources(self):
        self.assertIn("pull/44#issuecomment-6356274881", DEPLOYMENT)
        self.assertIn("https://mcpize.com/developers/publish-mcp-server", DEPLOYMENT)
        self.assertIn("https://mcpize.com/docs/monetization", DEPLOYMENT)
        self.assertIn("between 0.01 and 100 USDC", DEPLOYMENT)
        self.assertIn("dashboard route", DEPLOYMENT)

if __name__ == "__main__":
    unittest.main()
