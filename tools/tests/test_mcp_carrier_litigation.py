"""Tests for the carrier_check and litigation_screen tools of
mcp_server/recall_mcp.py (issue #67). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcp_carrier_litigation.py' -v

The fetchers are patched at their module `fetch` to serve recorded
material that already lives in this repo with its provenance: the FMCSA
Company Census record for USDOT 2046 and the CourtListener search
excerpts carried by test_fmcsa_carrier.py and test_courtlistener_recap.py
(copied from the published deliveries, with the test harness parts
labelled there). Where a recorded body is served in answer to a
differently shaped query to exercise a code path, the test says so where
it happens. No source figure is invented here. For each sample call the
test asserts the tool's text equals the pay per call API's body for the
same query, since both go through api.endpoints.
"""

import io
import json
import os
import subprocess
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from api import endpoints, recall_api  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402
from tools import courtlistener_recap as cl  # noqa: E402
from tools import fmcsa_carrier as fc  # noqa: E402
import test_courtlistener_recap as cl_fixtures  # noqa: E402
import test_fmcsa_carrier as fc_fixtures  # noqa: E402

WALLET = "0x" + "ab" * 20  # synthetic test value, not a real wallet
# Placeholder credential for the test only; not a real token.
FAKE_TOKEN = "fake-token-for-tests-only-not-a-real-credential"


def rpc(messages, wallet=None):
    stdin = io.StringIO("".join(json.dumps(m) + "\n" for m in messages))
    stdout, stderr = io.StringIO(), io.StringIO()
    recall_mcp.serve(stdin, stdout, wallet, stderr)
    return [json.loads(line) for line in stdout.getvalue().splitlines() if line.strip()], stderr.getvalue()


def call(name, arguments, req_id=2):
    return {"jsonrpc": "2.0", "id": req_id, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


def tool_result(name, arguments):
    responses, err = rpc([call(name, arguments)])
    assert err == "", err
    return responses[0]["result"]


def api_body(path, query_string):
    status, _, body = recall_api.handle("GET", path, query_string, None)
    assert status == "200 OK", (status, body[:200])
    return body.decode("utf-8")


def fc_capture(url, body, status_line="HTTP/1.1 200 OK"):
    # Plain test headers; not a recording of any FMCSA header.
    return fc.Capture(url, "2026-10-22T21:37:45Z", status_line, ["Content-Type: application/json"], body, "utf-8")


# ----------------------------------------------------------------------
# Listing
# ----------------------------------------------------------------------

class ListingTests(unittest.TestCase):
    def test_three_tools_listed_recall_check_first_and_unchanged(self):
        responses, _ = rpc([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}], wallet=WALLET)
        tools = responses[0]["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["recall_check", "carrier_check", "litigation_screen"])
        self.assertEqual(tools[0], recall_mcp.tool_definition(WALLET))
        for tool in tools:
            self.assertFalse(tool["inputSchema"]["additionalProperties"])
            self.assertIn("A failed fetch is an error, never an empty result.", tool["description"])
        carrier, litigation = tools[1], tools[2]
        self.assertEqual(sorted(carrier["inputSchema"]["properties"]), ["exclude", "limit", "name", "source", "subject", "usdot"])
        self.assertEqual(carrier["inputSchema"]["properties"]["source"]["items"]["enum"], ["census", "safer", "li"])
        for url in (fc.CENSUS_URL, fc.SAFER_URL, fc.LI_URL):
            self.assertIn(url, carrier["description"])
        self.assertEqual(sorted(litigation["inputSchema"]["properties"]),
                         ["docket_details", "exclude", "filed_after", "list", "order_by", "party", "subject"])
        self.assertEqual(litigation["inputSchema"]["required"], ["party"])
        self.assertIn(cl.SEARCH_URL, litigation["description"])
        self.assertIn(cl.SCOPE_LINE, litigation["description"])
        # Only recall_check carries a recorded price (mcpize.yaml), so only its
        # description names the payout wallet.
        self.assertIn(WALLET, tools[0]["description"])
        self.assertNotIn("0x", carrier["description"])
        self.assertNotIn("0x", litigation["description"])
        self.assertIn("Payment", tools[0]["description"])
        self.assertNotIn("Payment", carrier["description"] + litigation["description"])

    def test_instructions_name_all_three_tools(self):
        responses, _ = rpc([{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {"protocolVersion": "2025-06-18"}}])
        text = responses[0]["result"]["instructions"]
        for name in recall_mcp.TOOL_NAMES:
            self.assertIn(name, text)
        self.assertNotIn("0x", text)


# ----------------------------------------------------------------------
# carrier_check
# ----------------------------------------------------------------------

class CarrierCheckTests(unittest.TestCase):
    def test_usdot_census_report_equals_the_api_body(self):
        url = fc.census_record_url("2046")
        cap = fc_capture(url, fc_fixtures.CENSUS_BODY_2046)

        def fake_fetch(u):
            if u != url:
                raise AssertionError("unexpected url " + u)
            return cap
        args = {"usdot": "2046", "source": ["census"], "subject": "GARDA CL CENTRAL INC"}
        with patch.object(fc, "fetch", side_effect=fake_fetch) as fetch:
            result = tool_result("carrier_check", args)
            expected = api_body("/carrier", "usdot=2046&source=census&subject=GARDA+CL+CENTRAL+INC")
        self.assertEqual(fetch.call_count, 2)  # one per surface
        self.assertFalse(result["isError"])
        self.assertEqual(result["content"][0]["type"], "text")
        text = result["content"][0]["text"]
        self.assertEqual(text, expected)
        self.assertTrue(text.startswith("# Carrier vetting: GARDA CL CENTRAL INC\n"))
        self.assertIn("## Carrier: GARDA CL CENTRAL INC", text)
        self.assertIn("- legal_name as shown: GARDA CL CENTRAL INC", text)
        self.assertIn("- Query URL: " + url + "\n- Retrieved (UTC): 2026-10-22T21:37:45Z", text)
        self.assertIn(cap.transcript, text)

    def test_source_order_and_default_sources(self):
        urls = {fc.census_record_url("2046"): "census", fc.safer_url("2046"): "safer", fc.li_url("2046"): "li"}
        seen = []

        def fake_fetch(u):
            seen.append(urls[u])
            # The recorded Census body is served for every source here to
            # exercise the ordering only; this pairing of query and body is a
            # test arrangement, not a recording of SAFER or L&I.
            return fc_capture(u, fc_fixtures.CENSUS_BODY_2046)
        with patch.object(fc, "fetch", side_effect=fake_fetch):
            tool_result("carrier_check", {"usdot": "2046", "source": ["li", "census"]})
            self.assertEqual(seen, ["li", "census"])
            seen.clear()
            tool_result("carrier_check", {"usdot": "2046"})
            self.assertEqual(seen, ["census", "safer", "li"])

    def test_name_search_exclusion_rule(self):
        # The recorded USDOT 2046 Census record is served here as the body of a
        # name search response, to exercise the exclusion rule; this pairing of
        # query and body is a test arrangement, not a recording.
        url = fc.census_name_url("GARDA", 50)
        cap = fc_capture(url, fc_fixtures.CENSUS_BODY_2046)
        with patch.object(fc, "fetch", return_value=cap):
            result = tool_result("carrier_check", {"name": "GARDA", "exclude": ["999999=not the subject"]})
            self.assertTrue(result["isError"])
            self.assertIn("Bad request:", result["content"][0]["text"])
            self.assertNotIn("## Carrier", result["content"][0]["text"])
            args = {"name": "GARDA", "exclude": ["2046=a different carrier with a similar name"]}
            result = tool_result("carrier_check", args)
            expected = api_body("/carrier", "name=GARDA&exclude=2046%3Da+different+carrier+with+a+similar+name")
        self.assertFalse(result["isError"])
        self.assertEqual(result["content"][0]["text"], expected)
        self.assertIn("## Carrier search: GARDA", result["content"][0]["text"])
        self.assertIn("a different carrier with a similar name", result["content"][0]["text"])

    def test_limit_is_passed_as_the_fetchers_own_input(self):
        seen = []

        def fake_fetch(u):
            seen.append(u)
            return fc_capture(u, "[]")
        with patch.object(fc, "fetch", side_effect=fake_fetch):
            result = tool_result("carrier_check", {"name": "GARDA", "limit": 5})
        self.assertFalse(result["isError"])
        self.assertEqual(seen, [fc.census_name_url("GARDA", 5)])

    def test_bad_arguments_are_tool_errors_with_no_fetch(self):
        cases = [
            ({}, "exactly one of usdot or name"),
            ({"usdot": "2046", "name": "GARDA"}, "exactly one of usdot or name"),
            ({"usdot": "abc"}, "Bad request:"),
            ({"usdot": "2046", "source": ["bogus"]}, "source must be one of census, safer, li"),
            ({"usdot": "2046", "source": "census"}, "source must be an array of strings"),
            ({"name": "GARDA", "limit": "5"}, "limit must be an integer"),
            ({"name": "GARDA", "limit": True}, "limit must be an integer"),
            ({"name": "GARDA", "limit": 0}, "limit must be at least 1"),
            ({"usdot": "2046", "exclude": ["1=x"]}, "exclude applies to a name search"),
            ({"name": "GARDA", "source": ["census"]}, "source applies to a usdot run"),
            ({"name": "GARDA", "exclude": ["no reason"]}, "exclude needs the form USDOT=reason"),
            ({"usdot": 2046}, "usdot must be a string"),
            ({"usdot": "2046", "colour": "red"}, "unknown argument(s): colour"),
        ]
        with patch.object(fc, "fetch", side_effect=AssertionError("no fetch may happen")):
            for args, needle in cases:
                with self.subTest(args=args):
                    result = tool_result("carrier_check", args)
                    self.assertTrue(result["isError"])
                    text = result["content"][0]["text"]
                    self.assertTrue(text.startswith("Bad request: "), text)
                    self.assertIn(needle, text)
                    self.assertNotIn("--", text)  # no command line flags leak into the error
                    self.assertNotIn("## Carrier", text)

    def test_fetch_failure_is_a_tool_error_with_no_report(self):
        for exc in (OSError("connection refused"), urllib.error.URLError("blocked")):
            with self.subTest(exc=exc), patch.object(fc, "fetch", side_effect=exc):
                result = tool_result("carrier_check", {"usdot": "2046", "source": ["census"]})
            self.assertTrue(result["isError"])
            self.assertIn("no report emitted", result["content"][0]["text"])
            self.assertNotIn("## Carrier", result["content"][0]["text"])
            self.assertNotIn("Query URL", result["content"][0]["text"])


# ----------------------------------------------------------------------
# litigation_screen
# ----------------------------------------------------------------------

class LitigationScreenTests(unittest.TestCase):
    def setUp(self):
        self.body = cl_fixtures.envelope([cl_fixtures.RECORD_D1, cl_fixtures.RECORD_D5, cl_fixtures.RECORD_D9], count=15)
        self.calls = []

        def fake_fetch(url, token=None):
            self.calls.append((url, token))
            if url != cl_fixtures.Q1_URL:
                raise AssertionError("unexpected url " + url)
            return cl.Capture(url, cl_fixtures.RETRIEVED, "HTTP/1.1 200 OK", ["Content-Type: application/json"], self.body)
        patcher = patch.object(cl, "fetch", side_effect=fake_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)
        env = patch.dict(os.environ, {}, clear=False)
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop(cl.TOKEN_ENV, None)

    def test_party_search_equals_the_api_body(self):
        result = tool_result("litigation_screen", {"party": ["Jabil Inc."], "filed_after": "2021-10-22"})
        expected = api_body("/litigation", "party=Jabil+Inc.&filed_after=2021-10-22")
        self.assertFalse(result["isError"])
        text = result["content"][0]["text"]
        self.assertEqual(text, expected)
        self.assertEqual(self.calls[0], (cl_fixtures.Q1_URL, None))
        self.assertTrue(text.startswith("# Litigation screen: Jabil Inc.\n"))
        self.assertIn(cl.SCOPE_LINE, text)
        self.assertIn("| 1 | 0:26-cv-03269 | District Court, D. Minnesota | Andresen v. Jabil, Inc. |", text)
        self.assertIn("- Query URL: " + cl_fixtures.Q1_URL + "\n- Retrieved (UTC): " + cl_fixtures.RETRIEVED, text)
        self.assertIn("\n" + self.body + "\n```", text)

    def test_token_from_the_environment_is_sent_and_never_printed(self):
        with patch.dict(os.environ, {cl.TOKEN_ENV: FAKE_TOKEN}):
            result = tool_result("litigation_screen", {"party": ["Jabil Inc."], "filed_after": "2021-10-22", "list": 2})
        self.assertFalse(result["isError"])
        self.assertEqual(self.calls[0][1], FAKE_TOKEN)
        text = json.dumps(result)
        self.assertNotIn(FAKE_TOKEN, text)
        self.assertNotIn("| 3 |", text)  # list=2 limits the rows

    def test_docket_details_false_fetches_no_docket(self):
        result = tool_result("litigation_screen", {"party": ["Jabil Inc."], "filed_after": "2021-10-22",
                                                   "docket_details": False, "subject": "Jabil"})
        self.assertFalse(result["isError"])
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(result["content"][0]["text"].startswith("# Litigation screen: Jabil\n"))

    def test_exclusion_not_listed_is_a_tool_error(self):
        result = tool_result("litigation_screen", {"party": ["Jabil Inc."], "filed_after": "2021-10-22", "exclude": ["1=not listed"]})
        self.assertTrue(result["isError"])
        self.assertTrue(result["content"][0]["text"].startswith("Bad request: "))
        self.assertNotIn("## Subject", result["content"][0]["text"])

    def test_bad_arguments_are_tool_errors_with_no_fetch(self):
        cases = [
            ({}, "at least one party"),
            ({"party": []}, "at least one party"),
            ({"party": "Jabil Inc."}, "party must be an array of strings"),
            ({"party": ["Jabil Inc."], "filed_after": "nope"}, "filed-after needs YYYY-MM-DD"),
            ({"party": ["Jabil Inc."], "list": -1}, "list must be at least 0"),
            ({"party": ["Jabil Inc."], "list": "2"}, "list must be an integer"),
            ({"party": ["Jabil Inc."], "docket_details": "yes"}, "docket_details must be true or false"),
            ({"party": ["Jabil Inc."], "exclude": ["x"]}, "exclude needs the form DOCKET_ID=reason"),
            ({"party": ['Ja"bil']}, "must not contain a double quote"),
            ({"party": ["Jabil Inc."], "colour": "red"}, "unknown argument(s): colour"),
        ]
        for args, needle in cases:
            with self.subTest(args=args):
                result = tool_result("litigation_screen", args)
                self.assertTrue(result["isError"])
                text = result["content"][0]["text"]
                self.assertTrue(text.startswith("Bad request: "), text)
                self.assertIn(needle, text)
                self.assertNotIn("--", text)
        self.assertEqual(self.calls, [])

    def test_transport_failure_is_a_tool_error_with_no_report(self):
        with patch.object(cl, "fetch", side_effect=urllib.error.URLError("name resolution failed")):
            result = tool_result("litigation_screen", {"party": ["Jabil Inc."]})
        self.assertTrue(result["isError"])
        self.assertIn("no report emitted", result["content"][0]["text"])
        self.assertNotIn("## Subject", result["content"][0]["text"])
        self.assertNotIn("Query URL", result["content"][0]["text"])


# ----------------------------------------------------------------------
# The real entry point over stdio, for the methods that need no fetch
# ----------------------------------------------------------------------

class StdioListingTests(unittest.TestCase):
    def test_tools_list_over_stdio_names_all_three(self):
        env = dict(os.environ)
        env.pop(recall_api.PAYOUT_ENV, None)
        messages = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        proc = subprocess.run([sys.executable, "-m", "mcp_server"], cwd=str(ROOT), env=env,
                              input="".join(json.dumps(m) + "\n" for m in messages),
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
        self.assertEqual([l["id"] for l in lines], [1, 2])
        self.assertEqual([t["name"] for t in lines[1]["result"]["tools"]], list(recall_mcp.TOOL_NAMES))


if __name__ == "__main__":
    unittest.main()
