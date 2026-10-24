#!/usr/bin/env python3
"""Hosted MCP verification probe for the redeploy check (issue #218).

Runs the outside verification from docs/mcpize-redeploy-runbook.md as one
script, against the hosted MCP endpoint: an anonymous initialize, a
tools/list, and one unpaid recall_check tools/call. It prints one
Markdown section per step in the delivery format from AGENT-BRIEF.md: a
claim line per check (PASS or FAIL, with the observed value), the source
(the endpoint URL and the exact request), the retrieval time in UTC, and
the complete raw response transcript directly beneath.

    python3 tools/hosted_mcp_probe.py
    python3 tools/hosted_mcp_probe.py https://recallcheck.mcpize.run/mcp

Expected values, all taken from the repo, never invented:

- serverInfo version "0.3.0": SERVER_VERSION in mcp_server/recall_mcp.py
  on main, the version the runbook's table expects after the redeploy.
- Twenty five tool names in the order tool_definitions() returns them on
  main, recall_check first (EXPECTED_TOOLS below mirrors that order).
- The unpaid call answers HTTP 402 with a JSON body (not a JSON-RPC
  error): x402Version 1, exactly one accepts entry with scheme "exact",
  network "base", maxAmountRequired "50000" (0.05 USDC at 6 decimals, the
  recall_check price the runbook keeps), and payTo equal to the recipient
  recorded in mcpize.yaml, which this script reads at run time.

The probe never sends an X-PAYMENT header and never pays; the unpaid call
is the whole point, because the 402 demand is the evidence. No private
key, token, or signing wallet is read or printed; the only wallet value
the probe handles is the public recipient recorded in mcpize.yaml, read
for the payTo comparison and printed as part of that check.

Exit 0 when every check passes, 1 when any check fails, 2 when the probe
cannot run (a transport failure, an unreadable mcpize.yaml, bad input).
A failed fetch is never reported as a pass or a fail of a check.
Standard library only.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ENDPOINT = "https://recallcheck.mcpize.run/mcp"
EXPECTED_VERSION = "0.3.0"
EXPECTED_TOOLS = ["recall_check", "carrier_check", "litigation_screen",
                  "formd_check", "nonprofit_check", "awards_search",
                  "pagespeed_snapshot", "domain_trust_check",
                  "ofac_sanctions_check", "vin_decode_check",
                  "clinical_trial_check", "fda_drug_check",
                  "broken_link_check", "meta_tag_check", "github_repo_check",
                  "app_lookup_check", "exchange_rate_check", "flood_check",
                  "safety_file", "fda_recall_check", "epa_screen",
                  "csl_screen", "oig_screen", "insider_check", "faa_lookup"]
EXPECTED_X402_VERSION = 1
EXPECTED_SCHEME = "exact"
EXPECTED_NETWORK = "base"
EXPECTED_MAX_AMOUNT = "50000"
TIMEOUT_SECONDS = 60
ROOT = Path(__file__).resolve().parent.parent

Exchange = namedtuple("Exchange", "label endpoint request retrieved status headers body")


class ProbeError(Exception):
    """The probe could not run. Never reported as a pass or a fail."""


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_recipient(root=ROOT):
    """The payout recipient from mcpize.yaml, the one place it appears."""
    path = root / "mcpize.yaml"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProbeError("cannot read %s: %s" % (path, exc))
    match = re.search(r'^\s*recipient:\s*"?([^"\s]+)"?', text, re.MULTILINE)
    if not match:
        raise ProbeError("no recipient line found in mcpize.yaml")
    return match.group(1)


# ----------------------------------------------------------------------
# Transport
# ----------------------------------------------------------------------

class Session:
    """One hosted MCP session. Sends JSON-RPC POSTs, tracks the session
    id the gateway returns, and never sets an X-PAYMENT header."""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.session_id = None

    def post(self, label, message):
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json, text/event-stream",
                   "MCP-Protocol-Version": "2025-06-18",
                   "User-Agent": "tiny-ledger-hosted-mcp-probe"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        retrieved = utc_now_iso()
        request = urllib.request.Request(self.endpoint,
                                         json.dumps(message).encode(),
                                         headers, method="POST")
        try:
            response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
        except urllib.error.HTTPError as err:
            response = err
        except Exception as exc:  # URLError, OSError, http.client errors
            raise ProbeError("transport failure on %s: %s" % (label, exc))
        with response:
            if response.headers.get("Mcp-Session-Id"):
                self.session_id = response.headers["Mcp-Session-Id"]
            body = read_body(response, label)
            return Exchange(label, self.endpoint, json.dumps(message),
                            retrieved, response.status,
                            list(response.headers.items()), body)


def read_body(response, label):
    """Read a response body. The gateway has been observed answering a
    step with a dropped body (zero bytes, connection closed) while other
    steps answer in full; the status and headers already arrived, so a
    body that cannot be read is the step's evidence (the checks on it
    fail), not a transport failure of the probe itself. An
    IncompleteRead's partial bytes are used when the gateway sent some."""
    try:
        return response.read().decode("utf-8", "replace")
    except Exception as exc:
        partial = getattr(exc, "partial", b"") or b""
        return partial.decode("utf-8", "replace")


def parse_rpc_body(body):
    """The JSON-RPC payload of a response body: plain JSON, or the data
    lines of a text/event-stream body. None when neither parses."""
    text = body.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    for line in text.splitlines():
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except ValueError:
                continue
    return None


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------

def check_initialize(exchange):
    results = []
    results.append((exchange.status == 200,
                    "initialize answered HTTP %s (expected 200)" % exchange.status))
    payload = parse_rpc_body(exchange.body)
    results.append((isinstance(payload, dict),
                    "initialize body parses as a JSON-RPC response"))
    info = {}
    if isinstance(payload, dict):
        info = (payload.get("result") or {}).get("serverInfo") or {}
    version = info.get("version")
    results.append((version == EXPECTED_VERSION,
                    "serverInfo version is %r (expected %r)" % (version, EXPECTED_VERSION)))
    results.append((bool(info.get("name")),
                    "serverInfo name is %r" % (info.get("name"),)))
    return results


def check_tools_list(exchange):
    results = []
    results.append((exchange.status == 200,
                    "tools/list answered HTTP %s (expected 200)" % exchange.status))
    payload = parse_rpc_body(exchange.body)
    results.append((isinstance(payload, dict),
                    "tools/list body parses as a JSON-RPC response "
                    "(%d bytes received)" % len(exchange.body)))
    tools = []
    if isinstance(payload, dict):
        tools = (payload.get("result") or {}).get("tools") or []
    names = [t.get("name") for t in tools if isinstance(t, dict)]
    results.append((len(names) == len(EXPECTED_TOOLS),
                    "tool count is %d (expected %d)" % (len(names), len(EXPECTED_TOOLS))))
    results.append((names == EXPECTED_TOOLS,
                    "tool names in order are %s" % (names,)))
    return results


def check_unpaid_call(exchange, recipient):
    results = []
    results.append((exchange.status == 402,
                    "unpaid recall_check call answered HTTP %s (expected 402)" % exchange.status))
    payload = parse_rpc_body(exchange.body)
    if not isinstance(payload, dict) or "accepts" not in payload:
        results.append((False, "402 body is not an x402 demand JSON object: %r"
                        % (exchange.body[:200],)))
        return results
    results.append((True, "402 body is an x402 demand JSON object, not a JSON-RPC error"))
    results.append((payload.get("x402Version") == EXPECTED_X402_VERSION,
                    "x402Version is %r (expected %r)"
                    % (payload.get("x402Version"), EXPECTED_X402_VERSION)))
    accepts = payload.get("accepts") or []
    results.append((len(accepts) == 1,
                    "accepts carries %d entries (expected 1)" % len(accepts)))
    entry = accepts[0] if accepts else {}
    results.append((entry.get("scheme") == EXPECTED_SCHEME,
                    "scheme is %r (expected %r)" % (entry.get("scheme"), EXPECTED_SCHEME)))
    results.append((entry.get("network") == EXPECTED_NETWORK,
                    "network is %r (expected %r)" % (entry.get("network"), EXPECTED_NETWORK)))
    results.append((str(entry.get("maxAmountRequired")) == EXPECTED_MAX_AMOUNT,
                    "maxAmountRequired is %r (expected %r, 0.05 USDC at 6 decimals); "
                    "the probe reports the observed amount and sets no price"
                    % (entry.get("maxAmountRequired"), EXPECTED_MAX_AMOUNT)))
    results.append((entry.get("payTo") == recipient,
                    "payTo is %r (expected the recipient in mcpize.yaml, %r)"
                    % (entry.get("payTo"), recipient)))
    return results


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------

def transcript(exchange):
    lines = ["HTTP %s" % exchange.status]
    lines += ["%s: %s" % pair for pair in exchange.headers]
    lines += ["", exchange.body]
    return "\n".join(lines)


def fenced(text):
    fence = "```"
    while fence in text:
        fence += "`"
    return "%s\n%s\n%s" % (fence, text, fence)


def section(title, exchange, results):
    lines = ["## %s" % title, "",
             "Source: POST %s" % exchange_label_url(exchange),
             "Request: `%s`" % exchange.request,
             "Retrieved: %s" % exchange.retrieved, ""]
    lines += ["- %s: %s" % ("PASS" if passed else "FAIL", text)
              for passed, text in results]
    lines += ["", "Raw response:", "", fenced(transcript(exchange)), ""]
    return lines


def exchange_label_url(exchange):
    return exchange.endpoint


def run_probe(endpoint, recipient, session=None):
    """Run the three steps and return (report_lines, failed_count).
    Raises ProbeError when a step cannot be performed at all."""
    session = session or Session(endpoint)
    steps = []
    init = session.post("initialize",
                        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                         "params": {"protocolVersion": "2025-06-18",
                                    "capabilities": {},
                                    "clientInfo": {"name": "hosted-mcp-probe",
                                                   "version": "0"}}})
    steps.append(("Step 1: initialize (anonymous)", init, check_initialize(init)))
    try:
        session.post("notifications/initialized",
                     {"jsonrpc": "2.0", "method": "notifications/initialized"})
    except ProbeError:
        pass  # a notification carries no checks; later steps judge the session
    listing = session.post("tools/list",
                           {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    steps.append(("Step 2: tools/list", listing, check_tools_list(listing)))
    call = session.post("tools/call",
                        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                         "params": {"name": "recall_check",
                                    "arguments": {"product": "VH101"}}})
    steps.append(("Step 3: tools/call recall_check (unpaid)", call,
                  check_unpaid_call(call, recipient)))
    lines = ["# Hosted MCP probe: %s" % endpoint, "",
             "Expected: server version %s, %d tools in the runbook order, "
             "and the unpaid call's 402 demand as recorded in "
             "docs/mcpize-redeploy-runbook.md. The probe never sends an "
             "X-PAYMENT header and never pays." % (EXPECTED_VERSION, len(EXPECTED_TOOLS)),
             ""]
    failed = 0
    for title, exchange, results in steps:
        lines += section(title, exchange, results)
        failed += sum(1 for passed, _ in results if not passed)
    if failed:
        lines.append("Result: FAIL, %d check(s) failed." % failed)
    else:
        lines.append("Result: PASS, every check held.")
    return lines, failed


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Probe the hosted MCP endpoint: initialize, tools/list, "
                    "and one unpaid recall_check call. Never pays.")
    parser.add_argument("endpoint", nargs="?", default=DEFAULT_ENDPOINT,
                        help="hosted MCP endpoint URL (default: %(default)s)")
    args = parser.parse_args(argv)
    try:
        recipient = read_recipient()
        lines, failed = run_probe(args.endpoint, recipient)
    except ProbeError as exc:
        print("ERROR: %s" % exc)
        return 2
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
