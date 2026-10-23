"""Tests for the formd_check, nonprofit_check, awards_search and
pagespeed_snapshot tools of mcp_server/recall_mcp.py (issue #97). No network.

Run:  python3 -m unittest discover -s tools/tests -p 'test_mcp_remaining_fetchers.py' -v

The fetchers are patched at their module `fetch` to serve recorded
material already in this repo with its provenance, the same material the
API endpoint tests use (api/test_endpoints.py): the USAspending, ProPublica,
EDGAR and PageSpeed captures under tools/tests/fixtures. No source figure
is invented here. For each sample call the test asserts the tool's text
equals the pay per call API's body for the same query, since both go
through api.endpoints.
"""

import hashlib
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

from api import recall_api  # noqa: E402
from mcp_server import recall_mcp  # noqa: E402
from tools import edgar_formd as ef  # noqa: E402
from tools import pagespeed_snapshot as ps  # noqa: E402
from tools import propublica_nonprofits as pp  # noqa: E402
from tools import usaspending_awards as ua  # noqa: E402

FIXTURES = ROOT / "tools" / "tests" / "fixtures"
WALLET = "0x" + "ab" * 20  # synthetic test value, not a real wallet
CONTACT = "Test Operator operator@example.com"  # placeholder contact for tests (example domain), not a real address
FAKE_KEY = "fake-key-for-tests-only-not-a-real-credential"  # placeholder, not a real key
NEW_TOOLS = ["formd_check", "nonprofit_check", "awards_search", "pagespeed_snapshot"]


def rpc(messages, wallet=None):
    stdin = io.StringIO("".join(json.dumps(m) + "\n" for m in messages))
    stdout, stderr = io.StringIO(), io.StringIO()
    recall_mcp.serve(stdin, stdout, wallet, stderr)
    return [json.loads(line) for line in stdout.getvalue().splitlines() if line.strip()], stderr.getvalue()


def tool_result(name, arguments):
    responses, err = rpc([{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}}])
    assert err == "", err
    return responses[0]["result"]


def api_body(path, query_string):
    status, _, body = recall_api.handle("GET", path, query_string, None)
    assert status == "200 OK", (status, body[:300])
    return body.decode("utf-8")


def text_of(result):
    return result["content"][0]["text"]


# ----------------------------------------------------------------------
# Listing
# ----------------------------------------------------------------------

class ListingTests(unittest.TestCase):
    def test_seven_tools_listed_first_three_unchanged(self):
        responses, _ = rpc([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}], wallet=WALLET)
        tools = responses[0]["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["recall_check", "carrier_check", "litigation_screen"] + NEW_TOOLS)
        self.assertEqual(tools[0], recall_mcp.tool_definition(WALLET))
        self.assertEqual(tools[1], recall_mcp.carrier_tool_definition())
        self.assertEqual(tools[2], recall_mcp.litigation_tool_definition())
        by_name = {t["name"]: t for t in tools}
        expected = {
            "formd_check": (["cik", "exclude", "issuer", "max_filings"], [ef.SUBMISSIONS_URL, ef.COMPANY_SEARCH_URL, ef.CONTACT_ENV]),
            "nonprofit_check": (["ein", "exclude", "name", "subject"], [pp.API]),
            "awards_search": (["end", "exclude", "limit", "naics", "page", "recipient", "start"], [ua.ENDPOINT]),
            "pagespeed_snapshot": (["exclude", "strategy", "subject", "url"], [ps.API_URL, ps.KEY_ENV]),
        }
        for name, (props, named) in expected.items():
            with self.subTest(tool=name):
                tool = by_name[name]
                self.assertEqual(sorted(tool["inputSchema"]["properties"]), props)
                self.assertFalse(tool["inputSchema"]["additionalProperties"])
                for n in named:
                    self.assertIn(n, tool["description"])
                self.assertIn("A failed fetch is an error, never an empty result.", tool["description"])
                # only recall_check carries a recorded price, so no other tool names the wallet
                self.assertNotIn("0x", tool["description"])
                self.assertNotIn("Payment", tool["description"])
        self.assertEqual(by_name["pagespeed_snapshot"]["inputSchema"]["required"], ["url"])
        self.assertEqual(by_name["pagespeed_snapshot"]["inputSchema"]["properties"]["strategy"]["enum"], ["mobile", "desktop"])

    def test_instructions_name_all_seven_tools(self):
        responses, _ = rpc([{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}])
        text = responses[0]["result"]["instructions"]
        self.assertTrue(text.startswith("Seven tools"))
        for name in recall_mcp.TOOL_NAMES:
            self.assertIn(name, text)
        self.assertEqual(len(recall_mcp.TOOL_NAMES), 7)


# ----------------------------------------------------------------------
# formd_check
# ----------------------------------------------------------------------

class FormdCheckTests(unittest.TestCase):
    PROVENANCE = json.loads((FIXTURES / "edgar" / "provenance.json").read_text(encoding="utf-8"))

    def captured(self, name):
        meta = self.PROVENANCE[name]
        transcript = (FIXTURES / "edgar" / name).read_bytes().decode("utf-8")
        return ef.Capture(meta["url"], meta["retrieved_utc"], transcript, transcript.partition("\n\n")[2])

    def fake_fetcher(self, *names):
        by_url = {self.PROVENANCE[n]["url"]: self.captured(n) for n in names}
        calls = []

        def fetch(url, contact):
            calls.append((url, contact))
            if url not in by_url:
                raise ef.FetchError("no recorded capture for %s" % url)
            return by_url[url]
        fetch.calls = calls
        return fetch

    def test_cik_report_equals_the_api_body_and_sends_the_contact(self):
        fetch = self.fake_fetcher("submissions-2156237.http", "formd-0002156237-26-000001.http")
        with patch.object(ef, "fetch", side_effect=fetch), patch.object(ef, "pace"), \
             patch.dict(os.environ, {ef.CONTACT_ENV: CONTACT}):
            result = tool_result("formd_check", {"cik": "2156237"})
            expected = api_body("/formd", "cik=2156237")
        self.assertFalse(result["isError"])
        text = text_of(result)
        self.assertEqual(text, expected)
        self.assertTrue(text.startswith("# Form D filings: CIK 2156237\n"))
        self.assertIn('- Total offering amount as shown: "400000000"', text)
        for name in ("submissions-2156237.http", "formd-0002156237-26-000001.http"):
            cap = self.captured(name)
            self.assertIn("\nSource: <%s>\n```\n%s\n```" % (cap.url, cap.transcript), text)
        self.assertTrue(fetch.calls)
        self.assertTrue(all(c == CONTACT for _, c in fetch.calls))
        self.assertNotIn(CONTACT, json.dumps(result))

    def test_unset_contact_is_a_tool_error_and_fetches_nothing(self):
        with patch.object(ef, "fetch", side_effect=AssertionError("no fetch expected")), patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ef.CONTACT_ENV, None)
            result = tool_result("formd_check", {"cik": "2156237"})
        self.assertTrue(result["isError"])
        self.assertTrue(text_of(result).startswith("Unavailable, no report emitted: "))
        self.assertIn(ef.CONTACT_ENV, text_of(result))

    def test_bad_arguments_and_fetch_failure(self):
        with patch.dict(os.environ, {ef.CONTACT_ENV: CONTACT}), \
             patch.object(ef, "fetch", side_effect=AssertionError("no fetch expected")):
            for args, needle in [({}, "give exactly one of cik or issuer"),
                                 ({"cik": "2156237", "issuer": "x"}, "give exactly one of cik or issuer"),
                                 ({"cik": "notdigits"}, "Bad request: "),
                                 ({"cik": "2156237", "max_filings": -1}, "max_filings must be at least 0"),
                                 ({"cik": "2156237", "max_filings": "3"}, "max_filings must be an integer"),
                                 ({"cik": "2156237", "colour": "red"}, "unknown argument(s): colour")]:
                with self.subTest(args=args):
                    result = tool_result("formd_check", args)
                    self.assertTrue(result["isError"])
                    self.assertTrue(text_of(result).startswith("Bad request: "), text_of(result))
                    self.assertIn(needle, text_of(result))
                    self.assertNotIn("--", text_of(result))
        with patch.dict(os.environ, {ef.CONTACT_ENV: CONTACT}), \
             patch.object(ef, "fetch", side_effect=ef.FetchError("HTTP 403")), patch.object(ef, "pace"):
            result = tool_result("formd_check", {"cik": "2156237"})
        self.assertTrue(result["isError"])
        self.assertIn("no report emitted", text_of(result))
        self.assertNotIn("## SEC EDGAR", text_of(result))


# ----------------------------------------------------------------------
# nonprofit_check
# ----------------------------------------------------------------------

class NonprofitCheckTests(unittest.TestCase):
    PROVENANCE = json.loads((FIXTURES / "propublica" / "provenance.json").read_text(encoding="utf-8"))
    ORG = (FIXTURES / "propublica" / "organization-530196605.json").read_text(encoding="utf-8")
    SEARCH = (FIXTURES / "propublica" / "search-american-red-cross.json").read_text(encoding="utf-8")

    def setUp(self):
        self.org_url = self.PROVENANCE["organization-530196605.json"]["url"]
        self.search_url = self.PROVENANCE["search-american-red-cross.json"]["url"]
        bodies = {self.org_url: self.ORG, self.search_url: self.SEARCH}
        self.calls = []

        def fake_fetch(url):
            self.calls.append(url)
            if url not in bodies:
                raise AssertionError("unexpected fetch " + url)
            # Plain test headers; the recorded bodies are the fixture files.
            return pp.Capture(url, "2026-10-23T03:35:58Z", "HTTP/1.1 200 OK", 200, ["Content-Type: application/json"], bodies[url])
        patcher = patch.object(pp, "fetch", side_effect=fake_fetch)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_ein_lookup_equals_the_api_body(self):
        self.assertEqual(hashlib.sha256(self.ORG.encode("utf-8")).hexdigest(), self.PROVENANCE["organization-530196605.json"]["sha256"])
        result = tool_result("nonprofit_check", {"ein": ["53-0196605"]})
        expected = api_body("/nonprofit", "ein=53-0196605")
        self.assertFalse(result["isError"])
        self.assertEqual(text_of(result), expected)
        self.assertTrue(text_of(result).startswith("# Nonprofit diligence: 530196605\n"))
        self.assertIn("Organization: EIN 530196605", text_of(result))
        self.assertIn(self.ORG.rstrip("\n"), text_of(result))

    def test_name_search_with_ein(self):
        result = tool_result("nonprofit_check", {"name": "American Red Cross", "ein": ["530196605"]})
        self.assertEqual(text_of(result), api_body("/nonprofit", "name=American+Red+Cross&ein=530196605"))
        self.assertIn(self.search_url, text_of(result))

    def test_bad_arguments_and_fetch_failure(self):
        for args, needle in [({}, "give name=<organization>, ein=<EIN>, or both"),
                             ({"ein": "530196605"}, "ein must be an array of strings"),
                             ({"ein": ["530196605"], "exclude": ["131624241=x"]}, "exclude needs name"),
                             ({"ein": ["1"]}, "EIN must be 9 digits"),
                             ({"name": "x", "colour": "red"}, "unknown argument(s): colour")]:
            with self.subTest(args=args):
                result = tool_result("nonprofit_check", args)
                self.assertTrue(result["isError"])
                self.assertIn(needle, text_of(result))
        self.assertEqual(self.calls, [])
        with patch.object(pp, "fetch", side_effect=pp.FetchError("connection refused")):
            result = tool_result("nonprofit_check", {"ein": ["530196605"]})
        self.assertTrue(result["isError"])
        self.assertIn("no report emitted", text_of(result))
        self.assertNotIn("## ProPublica", text_of(result))


# ----------------------------------------------------------------------
# awards_search
# ----------------------------------------------------------------------

class AwardsSearchTests(unittest.TestCase):
    META = json.loads((FIXTURES / "usaspending" / "recipient.meta.json").read_text(encoding="utf-8"))
    RAW = (FIXTURES / "usaspending" / "recipient.json").read_text(encoding="utf-8")

    def fake_fetch(self, request_body):
        self.assertEqual(request_body, self.META["request_body"])
        return ua.Capture(request_body, self.META["retrieved_utc"], self.RAW)

    def test_recipient_page_equals_the_api_body(self):
        with patch.object(ua, "fetch", side_effect=self.fake_fetch):
            result = tool_result("awards_search", {"recipient": "Boeing", "limit": 2})
            expected = api_body("/awards", "recipient=Boeing&limit=2")
        self.assertFalse(result["isError"])
        text = text_of(result)
        self.assertEqual(text, expected)
        self.assertTrue(text.startswith("# Contract awards: Boeing\n"))
        self.assertIn("Exact query: POST " + ua.ENDPOINT, text)
        self.assertIn(self.META["request_body"], text)
        self.assertIn("Retrieved (UTC): " + self.META["retrieved_utc"], text)
        self.assertIn(self.RAW.rstrip("\n"), text)

    def test_exclusion_not_on_the_page_and_fetch_failures(self):
        with patch.object(ua, "fetch", side_effect=self.fake_fetch):
            result = tool_result("awards_search", {"recipient": "Boeing", "limit": 2, "exclude": ["NOT_ON_PAGE=reason"]})
        self.assertTrue(result["isError"])
        self.assertTrue(text_of(result).startswith("Bad request: "))
        self.assertNotIn("--exclude", text_of(result))
        for failure in (ValueError("unexpected HTTP status 500"), OSError("timed out"), TimeoutError("slow")):
            with self.subTest(failure=failure), patch.object(ua, "fetch", side_effect=failure):
                result = tool_result("awards_search", {"recipient": "Boeing", "limit": 2})
            self.assertTrue(result["isError"])
            self.assertIn("no report emitted", text_of(result))
            self.assertNotIn("## USAspending", text_of(result))

    def test_bad_arguments_fetch_nothing(self):
        with patch.object(ua, "fetch", side_effect=AssertionError("no fetch expected")):
            for args, needle in [({"recipient": "Boeing", "naics": "336411"}, "naics must be an array of strings"),
                                 ({"recipient": "Boeing", "limit": True}, "limit must be an integer"),
                                 ({"recipient": "Boeing", "colour": "red"}, "unknown argument(s): colour")]:
                with self.subTest(args=args):
                    result = tool_result("awards_search", args)
                    self.assertTrue(result["isError"])
                    self.assertIn(needle, text_of(result))
            result = tool_result("awards_search", {})
            self.assertTrue(result["isError"])
            self.assertTrue(text_of(result).startswith("Bad request: "))
            self.assertNotIn("--", text_of(result))


# ----------------------------------------------------------------------
# pagespeed_snapshot
# ----------------------------------------------------------------------

class PageSpeedSnapshotTests(unittest.TestCase):
    PROVENANCE = json.loads((FIXTURES / "pagespeed" / "provenance.json").read_text(encoding="utf-8"))
    TRANSCRIPT = (FIXTURES / "pagespeed" / "keyless-429.http").read_text(encoding="utf-8")
    PAGE = "https://example.com/"  # the example domain page the recorded keyless capture was made for

    def setUp(self):
        self.calls = []

    def fake_fetch(self, url, key=None, recorded=None):
        self.calls.append((url, key, recorded))
        head, body = self.TRANSCRIPT.split("\n\n", 1)
        lines = head.split("\n")
        return ps.Capture(recorded or url, self.PROVENANCE["keyless-429.http"]["retrieved_utc"], lines[0], lines[1:], body)

    def test_keyless_429_capture_is_the_report_and_equals_the_api_body(self):
        with patch.object(ps, "fetch", side_effect=self.fake_fetch), patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ps.KEY_ENV, None)
            # example domain page, as in the recorded capture
            result = tool_result("pagespeed_snapshot", {"url": [self.PAGE]})
            expected = api_body("/pagespeed", "url=https://example.com/")  # example domain
        self.assertFalse(result["isError"])
        text = text_of(result)
        self.assertEqual(text, expected)
        self.assertTrue(text.startswith("# PageSpeed snapshot: example.com\n"))  # example domain
        self.assertIn("The API could not measure this page", text)
        self.assertIn("HTTP/1.1 429 Too Many Requests", text)
        self.assertIsNone(self.calls[0][1])

    def test_key_is_sent_and_never_printed(self):
        with patch.object(ps, "fetch", side_effect=self.fake_fetch), patch.dict(os.environ, {ps.KEY_ENV: FAKE_KEY}):
            # example domain page, as in the recorded capture
            result = tool_result("pagespeed_snapshot", {"url": [self.PAGE], "strategy": "desktop"})
        self.assertFalse(result["isError"])
        self.assertEqual(self.calls[0][1], FAKE_KEY)
        self.assertIn("key=" + ps.KEY_MARKER, self.calls[0][2])
        self.assertNotIn(FAKE_KEY, json.dumps(result))

    def test_bad_arguments_fetch_nothing_and_transport_failure(self):
        six = ["https://example.com/p%d" % i for i in range(6)]  # six example domain pages, one over the limit
        with patch.object(ps, "fetch", side_effect=AssertionError("no fetch expected")):
            for args, needle in [({}, "give at least one url"),
                                 ({"url": "https://example.com/"}, "url must be an array of strings"),  # example domain
                                 ({"url": six}, "at most 5 pages"),
                                 ({"url": [self.PAGE], "strategy": "tablet"}, "strategy must be one of mobile, desktop"),
                                 ({"url": [self.PAGE], "colour": "red"}, "unknown argument(s): colour")]:
                with self.subTest(args=args):
                    result = tool_result("pagespeed_snapshot", args)
                    self.assertTrue(result["isError"])
                    self.assertIn(needle, text_of(result))
        with patch.object(ps, "fetch", side_effect=urllib.error.URLError("connection refused")):
            result = tool_result("pagespeed_snapshot", {"url": [self.PAGE]})
        self.assertTrue(result["isError"])
        self.assertIn("no report emitted", text_of(result))
        self.assertNotIn("## Page", text_of(result))


# ----------------------------------------------------------------------
# the real entry point over stdio, for the methods that need no fetch
# ----------------------------------------------------------------------

class StdioListingTests(unittest.TestCase):
    def test_tools_list_over_stdio_names_all_seven(self):
        env = dict(os.environ)
        env.pop(recall_api.PAYOUT_ENV, None)
        env.pop(ef.CONTACT_ENV, None)
        messages = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "formd_check", "arguments": {"cik": "2156237"}}}]
        proc = subprocess.run([sys.executable, "-m", "mcp_server"], cwd=str(ROOT), env=env,
                              input="".join(json.dumps(m) + "\n" for m in messages),
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
        self.assertEqual([l["id"] for l in lines], [1, 2, 3])
        self.assertEqual([t["name"] for t in lines[1]["result"]["tools"]], list(recall_mcp.TOOL_NAMES))
        # with EDGAR_CONTACT unset the Form D tool refuses before any fetch, over the real transport too
        self.assertTrue(lines[2]["result"]["isError"])
        self.assertIn(ef.CONTACT_ENV, lines[2]["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
