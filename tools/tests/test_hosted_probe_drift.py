"""Drift check for the hosted probe's expected values (issue #237).

Offline only: no network, no live probe run. The hosted MCP probe
(tools/hosted_mcp_probe.py, issue #218) carries its expected values as
constants. Those constants have two sources in this repo, and this test
pins all three sides together so a drift in any one fails here and names
the disagreeing source:

- the probe itself (tools/hosted_mcp_probe.py): EXPECTED_TOOLS,
  EXPECTED_VERSION, EXPECTED_X402_VERSION, EXPECTED_SCHEME,
  EXPECTED_NETWORK, EXPECTED_MAX_AMOUNT, and the recipient it reads from
  mcpize.yaml;
- the server surface (mcp_server/recall_mcp.py): tool_definitions()
  names in order and SERVER_VERSION;
- the runbook (docs/mcpize-redeploy-runbook.md): the "Expected, in this
  order" tool list and the Outside verification table's after column
  (server version, x402Version, scheme, network, maxAmountRequired, and
  payTo equal to the mcpize.yaml recipient).

The comparison lives in disagreements() so the mutation tests below can
feed it drifted inputs: every drift case is SYNTHETIC, built in this
file, and each asserts the returned message names the source pair that
disagrees.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import hosted_mcp_probe as probe  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402

RUNBOOK = ROOT / "docs" / "mcpize-redeploy-runbook.md"


def runbook_values(text):
    """The expected values the runbook states, parsed from its own text.
    A missing value parses as None, which disagrees with everything."""
    order = re.search(r"Expected, in this order: `(\[.*?\])`", text, re.S)
    tools = re.findall(r"'([a-z_]+)'", order.group(1)) if order else None
    section_match = re.search(r"## Outside verification(.*?)## Listing copy",
                              text, re.S)
    section = section_match.group(1) if section_match else ""
    version = re.search(r'`serverInfo` version "([0-9.]+)"', section)
    x402 = re.search(r"`x402Version` (\d+)", section)
    scheme = re.search(r"`scheme` \"([a-z]+)\"", section)
    network = re.search(r"`network` \"([a-z]+)\"", section)
    amount = re.search(r"`maxAmountRequired` \"(\d+)\"", section)
    return {
        "tools": tools,
        "version": version.group(1) if version else None,
        "x402_version": int(x402.group(1)) if x402 else None,
        "scheme": scheme.group(1) if scheme else None,
        "network": network.group(1) if network else None,
        "max_amount": amount.group(1) if amount else None,
        "payto_is_yaml_recipient": "payTo` equal to the `recipient` in `mcpize.yaml`" in section,
    }


def disagreements(probe_values, server_tools, server_version, book):
    """One message per drift, each naming the disagreeing sources.
    probe_values mirrors the probe's constants; book is runbook_values()."""
    out = []
    if probe_values["tools"] != server_tools:
        out.append("probe vs server: EXPECTED_TOOLS %r != tool_definitions() %r"
                   % (probe_values["tools"], server_tools))
    if probe_values["tools"] != book["tools"]:
        out.append("probe vs runbook: EXPECTED_TOOLS %r != the runbook's "
                   "expected order %r" % (probe_values["tools"], book["tools"]))
    if server_tools != book["tools"]:
        out.append("server vs runbook: tool_definitions() %r != the runbook's "
                   "expected order %r" % (server_tools, book["tools"]))
    if probe_values["version"] != server_version:
        out.append("probe vs server: EXPECTED_VERSION %r != SERVER_VERSION %r"
                   % (probe_values["version"], server_version))
    if probe_values["version"] != book["version"]:
        out.append("probe vs runbook: EXPECTED_VERSION %r != the table's "
                   "expected version %r" % (probe_values["version"], book["version"]))
    if server_version != book["version"]:
        out.append("server vs runbook: SERVER_VERSION %r != the table's "
                   "expected version %r" % (server_version, book["version"]))
    for key, label in (("x402_version", "x402Version"), ("scheme", "scheme"),
                       ("network", "network"), ("max_amount", "maxAmountRequired")):
        if probe_values[key] != book[key]:
            out.append("probe vs runbook: the probe's %s %r != the table's %r"
                       % (label, probe_values[key], book[key]))
    if not book["payto_is_yaml_recipient"]:
        out.append("runbook vs mcpize.yaml: the table no longer states payTo "
                   "equal to the recipient in mcpize.yaml, which is the value "
                   "the probe compares against")
    return out


def real_probe_values():
    return {"tools": probe.EXPECTED_TOOLS, "version": probe.EXPECTED_VERSION,
            "x402_version": probe.EXPECTED_X402_VERSION,
            "scheme": probe.EXPECTED_SCHEME, "network": probe.EXPECTED_NETWORK,
            "max_amount": probe.EXPECTED_MAX_AMOUNT}


def real_server_tools():
    return [d["name"] for d in recall_mcp.tool_definitions(None)]


class RealSourcesAgreeTests(unittest.TestCase):
    def test_probe_server_and_runbook_agree(self):
        book = runbook_values(RUNBOOK.read_text(encoding="utf-8"))
        found = disagreements(real_probe_values(), real_server_tools(),
                              recall_mcp.SERVER_VERSION, book)
        self.assertEqual(found, [],
                         "drift detected: " + "; ".join(found))

    def test_probe_recipient_is_the_yaml_recipient(self):
        # The probe compares payTo against the value it reads from
        # mcpize.yaml; pin that the read still lands on the file's
        # recipient line (an independent parse, not the probe's regex).
        text = (ROOT / "mcpize.yaml").read_text(encoding="utf-8")
        line = [l for l in text.splitlines() if "recipient:" in l][0]
        yaml_recipient = line.split("recipient:")[1].strip().strip('"')
        self.assertEqual(probe.read_recipient(), yaml_recipient)


class MutationTests(unittest.TestCase):
    """SYNTHETIC drift, fed to the same comparison the real test uses.
    Each case must be caught and must name the disagreeing source."""

    def setUp(self):
        self.book = runbook_values(RUNBOOK.read_text(encoding="utf-8"))
        self.probe_values = real_probe_values()
        self.server_tools = real_server_tools()

    def check(self, probe_values=None, server_tools=None,
              server_version=None, book=None):
        return disagreements(probe_values or self.probe_values,
                             server_tools or self.server_tools,
                             server_version or recall_mcp.SERVER_VERSION,
                             book or self.book)

    def test_probe_tool_order_mutation_names_probe_vs_server_and_runbook(self):
        drifted = dict(self.probe_values)
        tools = list(drifted["tools"])
        tools[0], tools[1] = tools[1], tools[0]  # synthetic swap
        drifted["tools"] = tools
        found = self.check(probe_values=drifted)
        self.assertTrue(any(m.startswith("probe vs server") for m in found), found)
        self.assertTrue(any(m.startswith("probe vs runbook") for m in found), found)

    def test_server_tool_drop_mutation_names_server(self):
        found = self.check(server_tools=self.server_tools[:-1])
        self.assertTrue(any(m.startswith("probe vs server") for m in found), found)
        self.assertTrue(any(m.startswith("server vs runbook") for m in found), found)

    def test_runbook_amount_mutation_names_probe_vs_runbook(self):
        book = dict(self.book)
        book["max_amount"] = "250000"  # synthetic drift in the table's value
        found = self.check(book=book)
        self.assertTrue(any("probe vs runbook" in m and "maxAmountRequired" in m
                            for m in found), found)

    def test_version_mutation_names_the_version_sources(self):
        drifted = dict(self.probe_values)
        drifted["version"] = "0.4.0"  # synthetic
        found = self.check(probe_values=drifted)
        self.assertTrue(any(m.startswith("probe vs server") for m in found), found)
        self.assertTrue(any(m.startswith("probe vs runbook") for m in found), found)


if __name__ == "__main__":
    unittest.main()
