"""The per-tool MCPize docs pages stay true to the server and the manifest (issue #147). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcpize_tool_pages.py' -v

docs/mcpize-tools/ holds one page per tool the MCP server lists. This test
fails when a page drifts from its sources:

- a tool in `recall_mcp.TOOL_NAMES` has no page, or a page names no tool;
- a page's quoted description is not the server's current `tools/list`
  description, verbatim;
- a page's price line disagrees with the `pricing` block of `mcpize.yaml`
  (a priced tool must show that price, an unpriced tool must say so);
- the redeploy runbook or the index stops linking a page.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp_server import recall_mcp  # noqa: E402

PAGES = ROOT / "docs" / "mcpize-tools"
RUNBOOK = ROOT / "docs" / "mcpize-redeploy-runbook.md"
MANIFEST = ROOT / "mcpize.yaml"


def manifest_prices():
    """{tool name: price string} from the pricing block of mcpize.yaml."""
    pricing = MANIFEST.read_text(encoding="utf-8").partition("\npricing:\n")[2]
    lines = pricing.splitlines()
    prices = {}
    for i, line in enumerate(lines):
        m = re.match(r"^\s+- name: (\S+)$", line)
        if m:
            price = re.match(r'^\s+price: "([^"]+)"$', lines[i + 1])
            prices[m.group(1)] = price.group(1) if price else None
    return prices


class ToolPagesTests(unittest.TestCase):
    def setUp(self):
        self.definitions = {d["name"]: d for d in recall_mcp.tool_definitions(None)}

    def test_one_page_per_tool_and_no_other(self):
        pages = sorted(p.stem for p in PAGES.glob("*.md") if p.name != "README.md")
        self.assertEqual(pages, sorted(recall_mcp.TOOL_NAMES))
        self.assertEqual(list(self.definitions), list(recall_mcp.TOOL_NAMES))

    def test_each_page_quotes_the_servers_description_verbatim(self):
        for name, definition in self.definitions.items():
            with self.subTest(tool=name):
                text = (PAGES / (name + ".md")).read_text(encoding="utf-8")
                self.assertIn("```text\n" + definition["description"] + "\n```", text)
                for argument in definition["inputSchema"]["properties"]:
                    self.assertIn("`%s`" % argument, text)

    def test_each_price_line_matches_the_manifest(self):
        prices = manifest_prices()
        self.assertTrue(set(prices) <= set(recall_mcp.TOOL_NAMES), "the manifest prices a tool the server does not list")
        for name in recall_mcp.TOOL_NAMES:
            with self.subTest(tool=name):
                text = (PAGES / (name + ".md")).read_text(encoding="utf-8")
                line = re.search(r"^- \*\*Price:\*\* (.*)$", text, re.M)
                self.assertIsNotNone(line, "no price line")
                if name in prices:
                    self.assertTrue(line.group(1).startswith("%s USDC per call" % prices[name]), line.group(1))
                else:
                    self.assertTrue(line.group(1).startswith("Not priced."), line.group(1))

    def test_tools_that_sell_an_error_without_their_setting_say_so(self):
        # Coordinator ruling on #147: formd_check without EDGAR_CONTACT and
        # pagespeed_snapshot without PAGESPEED_API_KEY are flagged plainly, not
        # given different prices or terms.
        for name, setting in (("formd_check", "EDGAR_CONTACT"), ("pagespeed_snapshot", "PAGESPEED_API_KEY")):
            with self.subTest(tool=name):
                text = (PAGES / (name + ".md")).read_text(encoding="utf-8")
                line = re.search(r"^- \*\*Before you pay for a call:\*\* (.*)$", text, re.M)
                self.assertIsNotNone(line, "no paid call warning")
                self.assertIn("`%s`" % setting, line.group(1))
                self.assertIn("a paid call in that state pays for", line.group(1))

    def test_runbook_and_index_link_every_page(self):
        runbook = RUNBOOK.read_text(encoding="utf-8")
        index = (PAGES / "README.md").read_text(encoding="utf-8")
        for name in recall_mcp.TOOL_NAMES:
            with self.subTest(tool=name):
                self.assertIn("(mcpize-tools/%s.md)" % name, runbook)
                self.assertIn("(%s.md)" % name, index)
        self.assertIn("(mcpize-tools/README.md)", runbook)

    def test_pages_link_to_targets_that_exist(self):
        for page in PAGES.glob("*.md"):
            text = page.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", text):
                if target.startswith("http"):
                    continue
                with self.subTest(page=page.name, target=target):
                    self.assertTrue((page.parent / target).resolve().exists(), target)


if __name__ == "__main__":
    unittest.main()
