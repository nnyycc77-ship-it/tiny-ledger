"""Offline tests for tools/disaster_history_check.py (issue #312).

Run:  python3 -m unittest discover -s tools/tests -p 'test_disaster_history_check.py' -v

Every response body here is a coordinator Option B capture on issue #312,
in tools/tests/fixtures/openfema/ with its URL, byte count, sha256 and
comment link in provenance.json. The captures carry bodies only, so the
status and header lines in the transcripts below are a test harness
(labelled as such), not a recording. No network is used: urllib's
urlopen is replaced for every test by a function that fails the test.
"""

import contextlib
import hashlib
import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (str(ROOT / "tools"), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

import disaster_history_check as dh  # noqa: E402

FIX = HERE / "fixtures" / "openfema"
PROV = json.loads((FIX / "provenance.json").read_text(encoding="utf-8"))
STATE = "state-RI-top5.json"
STATE_COUNT = "state-RI-top5-count.json"
KENT = "county-RI-Kent-top5.json"
NOSUCH = "county-RI-Nosuch-top5.json"
BAD = "bad-field-400.json"
RETRIEVED = "2026-10-24T12:10:00Z"  # test value; the captures' own times are in provenance.json


def body(name):
    return (FIX / name).read_bytes().decode("utf-8")


def transcript(name):
    """A harness transcript around a recorded body: the status line is the
    one the capture comment states, and no headers were captured."""
    return "%s (test harness line; status as stated in the capture)\n\n%s" % (PROV[name]["status"], body(name))


def capture(name):
    status = int(PROV[name]["status"].split()[1])
    return RETRIEVED, status, transcript(name), body(name)


def served(name, url=None):
    """A fetcher that answers one URL with one capture and fails the test on any other."""
    want = url or PROV[name]["url"]

    def fetch(asked):
        if asked != want:
            raise AssertionError("unexpected url %s" % asked)
        return capture(name)
    return fetch


def never(url):
    raise AssertionError("no fetch expected for a refused input")


def no_network(*args, **kwargs):
    raise AssertionError("the disaster history tests tried to reach the network")


def cli(argv, fetcher):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(dh, "fetch", fetcher), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = dh.main(argv)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        guard = mock.patch("urllib.request.urlopen", no_network)
        guard.start()
        self.addCleanup(guard.stop)


class Fixtures(Base):
    def test_every_capture_matches_its_recorded_hash_and_size(self):
        self.assertEqual(sorted(PROV), sorted([STATE, STATE_COUNT, KENT, NOSUCH, BAD]))
        for name, meta in PROV.items():
            raw = (FIX / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"], name)
            self.assertEqual(len(raw), meta["body_bytes"], name)

    def test_recorded_urls_are_the_responses_own_metadata_url(self):
        for name in (STATE, STATE_COUNT, KENT, NOSUCH):
            self.assertEqual(PROV[name]["url"], "https://www.fema.gov" + json.loads(body(name))["metadata"]["url"])


class Query(Base):
    def test_state_url_is_the_recorded_count_query(self):
        self.assertEqual(dh.build_url("RI", None, 5), PROV[STATE_COUNT]["url"])

    def test_county_url_is_the_recorded_county_query_plus_count(self):
        self.assertEqual(dh.build_url("RI", "Kent (County)", 5), PROV[KENT]["url"] + "&$count=true")

    def test_inputs_are_normalised(self):
        self.assertEqual(dh.check_state(" ri "), "RI")
        self.assertEqual(dh.check_area("  Kent   (County) "), "Kent (County)")
        self.assertIsNone(dh.check_area(""))
        self.assertEqual(dh.check_limit(None), dh.DEFAULT_LIMIT)
        self.assertEqual(dh.check_limit("10"), 10)

    def test_bad_inputs_are_refused(self):
        for bad in ("", "R", "RIX", "R1", None):
            with self.subTest(state=bad), self.assertRaises(ValueError):
                dh.check_state(bad)
        for bad in ("Prince George's (County)", "K", "Kent;drop", "x" * 121):
            with self.subTest(area=bad), self.assertRaises(ValueError):
                dh.check_area(bad)
        for bad in ("0", "1001", "x", "-1"):
            with self.subTest(limit=bad), self.assertRaises(ValueError):
                dh.check_limit(bad)

    def test_a_refused_input_makes_no_fetch(self):
        for argv in (["RIX"], ["RI", "--county", "Prince George's (County)"], ["RI", "--limit", "0"]):
            with self.subTest(argv=argv):
                code, out, err = cli(argv, never)
                self.assertEqual(code, 2)
                self.assertEqual(out, "")
                self.assertTrue(err.startswith("error: "), err)


class Render(Base):
    def section(self, name, area=None, limit=5):
        return "\n".join(dh.render_section("RI", area, limit, PROV[name]["url"], RETRIEVED, transcript(name),
                                           body(name)))

    def test_state_with_count_states_the_total_and_counts_distinct_disasters(self):
        text = self.section(STATE_COUNT)
        self.assertIn("5 rows returned (retrieved %s). FEMA's total of matching rows (metadata count, "
                      "$count=true) as shown: 123. More rows match than this response returns" % RETRIEVED, text)
        self.assertIn("DISASTERS: 2 distinct disasterNumber values among the 5 rows returned", text)
        self.assertIn("- disasterNumber 4766 (femaDeclarationString as shown: DR-4766-RI): declarationType DR, "
                      "incidentType \"Severe Storm\", declarationDate 2024-03-20T00:00:00.000Z, declarationTitle "
                      "\"SEVERE STORMS AND FLOODING\"", text)
        self.assertIn("  - designatedArea in the 4 rows returned: Kent (County); Newport (County)(in PMSA 2480,6480); "
                      "Providence (County)(in PMSA 6060,6480); Washington (County)(in (P)MSA 5520,6480)", text)
        self.assertIn("- disasterNumber 4765 (femaDeclarationString as shown: DR-4765-RI)", text)
        self.assertEqual(text.count("\n- disasterNumber "), 2)

    def test_without_count_no_total_is_stated(self):
        text = self.section(STATE)
        self.assertIn("FEMA's total was not requested for this response", text)
        self.assertNotIn("total of matching rows", text)
        self.assertNotIn("as shown: 0", text)
        self.assertIn("DISASTERS: 2 distinct disasterNumber values among the 5 rows returned", text)

    def test_county_lists_each_disaster_once_newest_first(self):
        text = self.section(KENT, "Kent (County)")
        self.assertIn('designatedArea "Kent (County)" in state RI', text)
        numbers = [line.split()[2] for line in text.split("\n") if line.startswith("- disasterNumber ")]
        self.assertEqual(numbers, ["4765", "4766", "4653", "3563", "4505"])

    def test_empty_result_is_proven_by_the_raw_response_and_worded_narrowly(self):
        text = self.section(NOSUCH, "Nosuch (County)")
        self.assertIn("0 rows returned", text)
        self.assertIn('NO ROWS: the DisasterDeclarationsSummaries array in the response is empty for this exact '
                      'filter. This says only that no declaration row has state RI and designatedArea exactly '
                      '"Nosuch (County)"', text)
        self.assertNotIn("DISASTERS:", text)
        self.assertNotIn("no disasters", text.lower())
        self.assertIn('"DisasterDeclarationsSummaries": []}', text)

    def test_the_transcript_is_printed_verbatim_beneath_the_source_link(self):
        text = self.section(STATE_COUNT)
        link = text.index("- Query URL: %s" % PROV[STATE_COUNT]["url"])
        self.assertGreater(text.index(body(STATE_COUNT)), link)
        self.assertTrue(text.endswith(body(STATE_COUNT) + "\n```"))


class FailClosed(Base):
    def test_a_400_answer_is_a_source_failure_with_nothing_printed(self):
        url = dh.build_url("RI", None, 5)
        with self.assertRaises(dh.SourceFailed) as ctx:
            dh.run("RI", limit=5, fetcher=lambda u: (RETRIEVED, 400, transcript(BAD), body(BAD)))
        self.assertIn(url, str(ctx.exception))
        self.assertIn("HTTP/1.1 400 Bad Request", str(ctx.exception))
        self.assertIn("the answer is unknown", str(ctx.exception))
        code, out, err = cli(["RI", "--limit", "5"], lambda u: (RETRIEVED, 400, transcript(BAD), body(BAD)))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("source failure, nothing printed", err)

    def test_a_body_not_in_the_recorded_shape_is_a_source_failure(self):
        for text in ("not json", "[]", '{"metadata": {}}', body(BAD)):
            with self.subTest(body=text[:40]), self.assertRaises(dh.SourceFailed):
                dh.run("RI", limit=5, fetcher=lambda u, t=text: (RETRIEVED, 200, "HTTP/1.1 200 OK\n\n" + t, t))

    def test_a_transport_failure_is_a_source_failure(self):
        def refused(url):
            raise dh.SourceFailed("%s: fetch failed: test failure, connection refused" % url)
        code, out, err = cli(["RI"], refused)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("fetch failed", err)


class CommandLine(Base):
    def test_the_report_is_the_rendered_section(self):
        code, out, err = cli(["ri", "--limit", "5"], served(STATE_COUNT))
        self.assertEqual(code, 0, err)
        expected = dh.render_section("RI", None, 5, PROV[STATE_COUNT]["url"], *capture(STATE_COUNT)[:1],
                                     transcript(STATE_COUNT), body(STATE_COUNT))
        self.assertEqual(out, "\n".join(expected) + "\n")


class Fetch(Base):
    """fetch() itself, with urlopen replaced by recorded bodies."""

    class Response(io.BytesIO):
        def __init__(self, status, reason, data):
            super().__init__(data)
            self.status, self.reason, self.version = status, reason, 11
            self.headers = {"Content-Type": "application/json"}

    def test_a_200_is_returned_with_its_transcript_and_the_tool_user_agent(self):
        seen = {}

        def opener(request, timeout):
            seen["ua"], seen["timeout"] = request.get_header("User-agent"), timeout
            return self.Response(200, "OK", (FIX / STATE_COUNT).read_bytes())
        with mock.patch("urllib.request.urlopen", opener):
            retrieved, status, text, got = dh.fetch(PROV[STATE_COUNT]["url"])
        self.assertEqual((status, got), (200, body(STATE_COUNT)))
        self.assertEqual(text, "HTTP/1.1 200 OK\nContent-Type: application/json\n\n" + body(STATE_COUNT))
        self.assertEqual(seen, {"ua": dh.USER_AGENT, "timeout": dh.TIMEOUT_SECONDS})

    def test_an_http_error_is_returned_not_raised(self):
        def opener(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {"Content-Type": "application/json"},
                                         io.BytesIO((FIX / BAD).read_bytes()))
        with mock.patch("urllib.request.urlopen", opener):
            _, status, text, got = dh.fetch("https://www.fema.gov/x")
        self.assertEqual((status, got), (400, body(BAD)))
        self.assertTrue(text.startswith("HTTP/1.1 400 Bad Request\n"))

    def test_a_transport_error_raises_source_failed(self):
        def opener(request, timeout):
            raise urllib.error.URLError("test failure: timed out")
        with mock.patch("urllib.request.urlopen", opener), self.assertRaises(dh.SourceFailed):
            dh.fetch("https://www.fema.gov/x")


class DocsPage(Base):
    def test_the_docs_page_names_the_question_the_source_and_the_price(self):
        page = (ROOT / "docs" / "mcpize-tools" / "disaster_history_check.md").read_text(encoding="utf-8")
        self.assertIn("0.25 USDC", page)
        self.assertIn(dh.BASE_URL, page)
        self.assertIn("tools/disaster_history_check.py", page)


if __name__ == "__main__":
    unittest.main()
