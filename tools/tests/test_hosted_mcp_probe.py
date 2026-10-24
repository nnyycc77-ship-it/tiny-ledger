"""Offline tests for tools/hosted_mcp_probe.py (issue #218).

Every transcript below is SYNTHETIC: written for these tests, labelled as
such, and shaped like the hosted gateway's answers as the redeploy
runbook records them. No transcript here is a live capture, and no test
touches the network: a fake session answers from the synthetic
transcripts. The recipient used in the pass case is the public value in
mcpize.yaml, read through the probe itself; the mismatched payTo case
uses the all-zero address as an obviously synthetic wrong value.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import hosted_mcp_probe as probe  # noqa: E402

RECIPIENT = probe.read_recipient()
ENDPOINT = "https://synthetic.invalid/mcp"


def exchange(label, status, payload):
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return probe.Exchange(label, ENDPOINT, "{}", "2026-01-01T00:00:00Z",
                          status, [("Content-Type", "application/json")], body)


# SYNTHETIC transcripts: a hosted server in the post redeploy state.
def init_ok(version="0.3.0"):
    return exchange("initialize", 200,
                    {"jsonrpc": "2.0", "id": 1,
                     "result": {"protocolVersion": "2025-06-18",
                                "serverInfo": {"name": "hojo-recall-check via MCPize",
                                               "version": version}}})


def list_ok(names=None):
    names = probe.EXPECTED_TOOLS if names is None else names
    return exchange("tools/list", 200,
                    {"jsonrpc": "2.0", "id": 2,
                     "result": {"tools": [{"name": n} for n in names]}})


def call_402(pay_to=RECIPIENT, status=402, amount="50000"):
    return exchange("tools/call", status,
                    {"x402Version": 1,
                     "accepts": [{"scheme": "exact", "network": "base",
                                  "maxAmountRequired": amount,
                                  "payTo": pay_to}]})


class FakeSession:
    """Answers the probe's three steps from synthetic transcripts."""

    def __init__(self, init, listing, call):
        self.answers = {"initialize": init, "tools/list": listing,
                        "tools/call": call}
        self.sent = []

    def post(self, label, message):
        self.sent.append(message)
        if label == "notifications/initialized":
            return None
        return self.answers[label]


def run(session):
    return probe.run_probe(ENDPOINT, RECIPIENT, session=session)


class ProbePassTests(unittest.TestCase):
    def test_pass_case_all_checks_hold(self):
        lines, failed = run(FakeSession(init_ok(), list_ok(), call_402()))
        self.assertEqual(failed, 0)
        self.assertIn("Result: PASS, every check held.", lines)

    def test_probe_never_sends_a_payment_header(self):
        session = FakeSession(init_ok(), list_ok(), call_402())
        run(session)
        for message in session.sent:
            self.assertNotIn("X-PAYMENT", json.dumps(message))
            self.assertNotIn("payment", json.dumps(message).lower())


class ProbeFailureShapeTests(unittest.TestCase):
    def test_wrong_version_fails_that_check_only(self):
        lines, failed = run(FakeSession(init_ok(version="0.1.0"), list_ok(), call_402()))
        self.assertEqual(failed, 1)
        self.assertTrue(any("FAIL: serverInfo version is '0.1.0'" in line
                            for line in lines))

    def test_wrong_tool_count_fails_count_and_order(self):
        lines, failed = run(FakeSession(init_ok(), list_ok(["recall_check"]), call_402()))
        self.assertEqual(failed, 2)
        self.assertTrue(any("FAIL: tool count is 1" in line for line in lines))

    def test_non_402_call_fails_the_status_check(self):
        lines, failed = run(FakeSession(init_ok(), list_ok(),
                                        call_402(status=200)))
        self.assertTrue(any("FAIL: unpaid recall_check call answered HTTP 200"
                            in line for line in lines))
        self.assertGreaterEqual(failed, 1)

    def test_mismatched_pay_to_fails_that_check_only(self):
        wrong = "0x0000000000000000000000000000000000000000"  # synthetic
        lines, failed = run(FakeSession(init_ok(), list_ok(),
                                        call_402(pay_to=wrong)))
        self.assertEqual(failed, 1)
        self.assertTrue(any("FAIL: payTo is" in line for line in lines))

    def test_wrong_amount_is_reported_not_rewritten(self):
        lines, failed = run(FakeSession(init_ok(), list_ok(),
                                        call_402(amount="250000")))
        self.assertEqual(failed, 1)
        self.assertTrue(any("'250000'" in line for line in lines))

    def test_402_body_that_is_a_json_rpc_error_fails(self):
        body = {"jsonrpc": "2.0", "id": 3, "error": {"code": -32000,
                                                     "message": "synthetic"}}
        lines, failed = run(FakeSession(init_ok(), list_ok(),
                                        exchange("tools/call", 402, body)))
        self.assertTrue(any("not an x402 demand" in line for line in lines))
        self.assertGreaterEqual(failed, 1)


class ProbeCannotRunTests(unittest.TestCase):
    def test_transport_failure_raises_probe_error(self):
        class DeadSession:
            def post(self, label, message):
                raise probe.ProbeError("transport failure on initialize: synthetic")

        with self.assertRaises(probe.ProbeError):
            run(DeadSession())

    def test_main_returns_2_when_the_probe_cannot_run(self):
        original = probe.Session

        class DeadSession:
            def __init__(self, endpoint):
                pass

            def post(self, label, message):
                raise probe.ProbeError("transport failure: synthetic")

        probe.Session = DeadSession
        try:
            self.assertEqual(probe.main([ENDPOINT]), 2)
        finally:
            probe.Session = original


class ExpectedValuesTests(unittest.TestCase):
    def test_expected_tools_match_the_server_on_main(self):
        root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(root))
        from mcp_server import recall_mcp
        names = [d["name"] for d in recall_mcp.tool_definitions(None)]
        self.assertEqual(probe.EXPECTED_TOOLS, names)
        self.assertEqual(probe.EXPECTED_VERSION, recall_mcp.SERVER_VERSION)


if __name__ == "__main__":
    unittest.main()
