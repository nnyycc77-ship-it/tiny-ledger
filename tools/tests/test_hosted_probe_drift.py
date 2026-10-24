"""Drift check for the hosted probe's expected values (issue #237).

Pinned tree: refreshed for issue #392 on merged main
`3c13f2e56dccd9cadce02b1981bfbcd5d8591ba1` (the merge of PR #390), by
rerunning this suite on a clean checkout of that exact tree
unmodified first: all eight tests green and the pricing state
unchanged (mcpize.yaml prices recall_check only, at 0.05 USDC, 50000
atomic units, pending issue #147's 0.25 repricing), so only this pin
moved. Previous pins: issue #383 on merged main
`9ad0a24b04e1f99e814113eee1ef04da9a3be5b9`, issue #378 on merged main
`74d67d266530708e7925cb4fadeb7d43eda9d710`, issue #376 on merged main
`96ab9af06813088a88a585948baec7ef604a6b3f`, issue #309 on merged main
`44507b55d1b65d260471c6180689194f5cf40d46`, issue #302 on merged main
`65dde3693bf3aeb601e783c78dcfc36472b895d8`, issue #294 on merged main
`2b86c90199ede1fbf3b31a0d39d6f9a4d3293e65`, issue #287 on merged main
`96a347f8b26dde768d020fcf1c2d65264e1a5fae`, issue #278 on merged main
`530f6dae61770cf5be9dacad6e3a7a6806c3595f`, issue #271 on merged main
`e5035f36a116feddc6243787cfacf951705b9067`. The pin records the tree
the suite was last verified against; the comparisons below read the
live files, so a later drift fails on its own merits wherever it
lands.

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

Issue #244 adds a fourth side for the amount: the pricing block in
mcpize.yaml is the pricing source of record, so its recall_check price,
parsed independently of the probe's own reader and converted to atomic
units (USDC has 6 decimals, as the runbook's table states), is pinned
against both the probe's EXPECTED_MAX_AMOUNT and the runbook's
maxAmountRequired.

The comparison lives in disagreements() so the mutation tests below can
feed it drifted inputs: every drift case is SYNTHETIC, built in this
file, and each asserts the returned message names the source pair that
disagrees.
"""

import re
import sys
import unittest
from decimal import Decimal
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


def yaml_pricing_amount(text, tool="recall_check"):
    """The pricing block's price for `tool` in mcpize.yaml, as atomic
    units, parsed independently of the probe's reader: the tools list
    entry naming the tool, then its price line, converted at USDC's 6
    decimals. A missing entry or a price that is not a whole number of
    atomic units parses as None, which disagrees with everything."""
    entry = re.search(r"-\s*name:\s*%s\s*\n\s*price:\s*\"?([0-9]+(?:\.[0-9]+)?)\"?"
                      % re.escape(tool), text)
    if not entry:
        return None
    atomic = Decimal(entry.group(1)) * (10 ** 6)
    if atomic != atomic.to_integral_value():
        return None
    return str(int(atomic))


def disagreements(probe_values, server_tools, server_version, book, yaml_amount):
    """One message per drift, each naming the disagreeing sources.
    probe_values mirrors the probe's constants; book is runbook_values();
    yaml_amount is yaml_pricing_amount() on mcpize.yaml."""
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
    if probe_values["max_amount"] != yaml_amount:
        out.append("probe vs mcpize.yaml: EXPECTED_MAX_AMOUNT %r != the pricing "
                   "block's recall_check amount %r (atomic units)"
                   % (probe_values["max_amount"], yaml_amount))
    if book["max_amount"] != yaml_amount:
        out.append("runbook vs mcpize.yaml: the table's maxAmountRequired %r != "
                   "the pricing block's recall_check amount %r (atomic units)"
                   % (book["max_amount"], yaml_amount))
    return out


def real_probe_values():
    return {"tools": probe.EXPECTED_TOOLS, "version": probe.EXPECTED_VERSION,
            "x402_version": probe.EXPECTED_X402_VERSION,
            "scheme": probe.EXPECTED_SCHEME, "network": probe.EXPECTED_NETWORK,
            "max_amount": probe.EXPECTED_MAX_AMOUNT}


def real_server_tools():
    return [d["name"] for d in recall_mcp.tool_definitions(None)]


def real_yaml_amount():
    return yaml_pricing_amount((ROOT / "mcpize.yaml").read_text(encoding="utf-8"))


class RealSourcesAgreeTests(unittest.TestCase):
    def test_probe_server_and_runbook_agree(self):
        book = runbook_values(RUNBOOK.read_text(encoding="utf-8"))
        found = disagreements(real_probe_values(), real_server_tools(),
                              recall_mcp.SERVER_VERSION, book, real_yaml_amount())
        self.assertEqual(found, [],
                         "drift detected: " + "; ".join(found))

    def test_yaml_pricing_amount_is_parsed_and_agrees(self):
        # The pricing block is the pricing source of record: its
        # recall_check price must parse (a whole number of atomic units)
        # and land on the same amount the probe and the runbook carry.
        amount = real_yaml_amount()
        self.assertIsNotNone(amount, "the pricing block's recall_check price did not parse")
        self.assertEqual(amount, probe.EXPECTED_MAX_AMOUNT)
        book = runbook_values(RUNBOOK.read_text(encoding="utf-8"))
        self.assertEqual(amount, book["max_amount"])

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
        self.yaml_amount = real_yaml_amount()

    def check(self, probe_values=None, server_tools=None,
              server_version=None, book=None, yaml_amount=None):
        return disagreements(probe_values or self.probe_values,
                             server_tools or self.server_tools,
                             server_version or recall_mcp.SERVER_VERSION,
                             book or self.book,
                             self.yaml_amount if yaml_amount is None else yaml_amount)

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

    def test_yaml_price_mutation_names_mcpize_yaml(self):
        text = (ROOT / "mcpize.yaml").read_text(encoding="utf-8")
        drifted = text.replace('price: "0.05"', 'price: "0.25"')  # synthetic drift in the pricing block
        self.assertNotEqual(drifted, text)
        found = self.check(yaml_amount=yaml_pricing_amount(drifted))
        self.assertTrue(any(m.startswith("probe vs mcpize.yaml") for m in found), found)
        self.assertTrue(any(m.startswith("runbook vs mcpize.yaml")
                            and "maxAmountRequired" in m for m in found), found)

    def test_version_mutation_names_the_version_sources(self):
        drifted = dict(self.probe_values)
        drifted["version"] = "0.4.0"  # synthetic
        found = self.check(probe_values=drifted)
        self.assertTrue(any(m.startswith("probe vs server") for m in found), found)
        self.assertTrue(any(m.startswith("probe vs runbook") for m in found), found)


if __name__ == "__main__":
    unittest.main()
