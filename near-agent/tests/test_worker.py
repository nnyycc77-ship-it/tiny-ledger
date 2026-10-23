"""Tests for near-agent/worker.py. No network, no live marketplace call.

Run from the repository root:

    python3 -m unittest discover -s near-agent/tests -v

The CI job discovers these through tools/tests/test_near_agent.py, which
loads this directory, so no workflow change is needed.

Nothing here talks to market.near.ai. Every request goes to FakeTransport,
which records what it was given and answers from a table; the token is the
placeholder string FAKE_TOKEN. The job tables used by the state tests are
synthetic (labelled as such where they appear): they exercise the diff
logic only and do not claim to be the marketplace's response shape. The
response shape itself is exercised by the captured fixture tests, which
name their fixture and its provenance where they appear.
"""

import inspect
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import worker  # noqa: E402

FAKE_TOKEN = "fake-token-for-tests-only-not-a-real-credential"
ENV = {worker.TOKEN_ENV: FAKE_TOKEN, "HOME": "/nonexistent-home-for-tests"}


class FakeTransport:
    """Answers from a table keyed by (method, url); records every request."""

    def __init__(self, answers=None, error=None):
        self.answers = answers or {}
        self.error = error
        self.sent = []

    def send(self, request):
        self.sent.append(request)
        if self.error is not None:
            raise self.error
        key = (request.method, request.url)
        if key not in self.answers:
            raise AssertionError("unexpected request %s %s" % key)
        status, headers, body = self.answers[key]
        return worker.Response(status, headers, body)


def run(argv, transport, env=ENV):
    out, err = io.StringIO(), io.StringIO()
    code = worker.main(argv, env=env, transport=transport, stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


class TokenTests(unittest.TestCase):
    def test_token_comes_from_the_one_environment_variable(self):
        self.assertEqual(worker.read_token({worker.TOKEN_ENV: "  " + FAKE_TOKEN + "\n"}), FAKE_TOKEN)

    def test_missing_or_empty_token_is_a_config_error(self):
        for env in ({}, {worker.TOKEN_ENV: ""}, {worker.TOKEN_ENV: "   "}):
            with self.assertRaises(worker.ConfigError):
                worker.read_token(env)

    def test_main_refuses_to_run_without_a_token_and_sends_nothing(self):
        transport = FakeTransport()
        code, out, err = run(["poll"], transport, env={})
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn(worker.TOKEN_ENV, err)
        self.assertEqual(transport.sent, [])

    def test_token_reader_touches_no_file(self):
        source = inspect.getsource(worker.read_token)
        for forbidden in ("open(", "read_text", "read_bytes", "Path(", '".env"', "dotenv", "configparser"):
            self.assertNotIn(forbidden, source)
        whole = (PACKAGE / "worker.py").read_text(encoding="utf-8")
        for forbidden in ('".env"', "'.env'", "dotenv", "configparser", "netrc", "keyring"):
            self.assertNotIn(forbidden, whole)


class RedactionTests(unittest.TestCase):
    def test_redactor_replaces_the_token_everywhere_in_a_line(self):
        red = worker.Redactor(FAKE_TOKEN)
        text = "Authorization: Bearer %s and again %s" % (FAKE_TOKEN, FAKE_TOKEN)
        self.assertNotIn(FAKE_TOKEN, red.clean(text))
        self.assertEqual(red.clean(text).count(worker.REDACTED), 2)

    def test_described_request_never_contains_the_token(self):
        req = worker.build_request(FAKE_TOKEN, "GET", worker.BOARD_PATH, worker.BOARD_QUERY)
        text = req.describe()
        self.assertNotIn(FAKE_TOKEN, text)
        self.assertIn("Authorization: Bearer " + worker.REDACTED, text)
        self.assertEqual(text.splitlines()[0], "GET https://market.near.ai/v1/jobs/board?kind=standard")
        # The real header still carries the token, so the request itself is sendable.
        self.assertIn(("Authorization", "Bearer " + FAKE_TOKEN), req.headers)

    def test_error_paths_are_redacted(self):
        # A failing transport whose message echoes the token must not leak it.
        transport = FakeTransport(error=worker.FetchError("boom " + FAKE_TOKEN))
        code, out, err = run(["bid", "job-1", "--amount", "1"], transport)
        self.assertEqual(code, 2)
        self.assertNotIn(FAKE_TOKEN, out + err)


class RequestBuildingTests(unittest.TestCase):
    def test_read_requests_match_the_task_paths(self):
        self.assertEqual(worker.build_url(worker.ASSIGNMENTS_PATH), "https://market.near.ai/v1/agents/me/assignments")
        self.assertEqual(worker.build_url(worker.BOARD_PATH, worker.BOARD_QUERY), "https://market.near.ai/v1/jobs/board?kind=standard")

    def test_json_body_is_compact_sorted_and_typed(self):
        req = worker.build_request(FAKE_TOKEN, "POST", "/v1/x", body={"b": 1, "a": "two"})
        self.assertEqual(req.body, b'{"a":"two","b":1}')
        self.assertIn(("Content-Type", "application/json"), req.headers)
        self.assertEqual(req.describe().splitlines()[-1], '{"a":"two","b":1}')

    def test_transport_refuses_any_host_but_the_marketplace_over_https(self):
        transport = worker.UrllibTransport()
        for url in ("http://market.near.ai/v1/jobs/board", "https://example.org/v1/jobs/board", "https://market.near.ai.evil.example/"):
            # Example hosts above are synthetic test inputs, not sources.
            with self.assertRaises(worker.FetchError):
                transport.send(worker.Request("GET", url, []))

    def test_fetch_json_fails_closed_on_status_and_on_non_json(self):
        req = worker.build_request(FAKE_TOKEN, "GET", worker.BOARD_PATH, worker.BOARD_QUERY)
        key = ("GET", req.url)
        for status, body in ((401, b'{"error":"unauthorized"}'), (500, b"nope"), (200, b"<html>")):
            transport = FakeTransport({key: (status, [], body)})
            with self.assertRaises(worker.FetchError):
                worker.fetch_json(transport, req)
        transport = FakeTransport({key: (200, [], b'{"ok":true}')})
        self.assertEqual(worker.fetch_json(transport, req), {"ok": True})


class StateTests(unittest.TestCase):
    # The job tables below are synthetic: ids and budgets chosen to exercise
    # the diff logic, not records from the marketplace.
    def test_changed_jobs_reports_new_and_changed_budget_only(self):
        previous = {"job-a": "10", "job-b": "5", "job-gone": "1"}
        current = {"job-a": "10", "job-b": "6", "job-c": "1"}
        self.assertEqual(worker.changed_jobs(previous, current),
                         [("job-b", "5", "6"), ("job-c", None, "1")])
        self.assertEqual(worker.changed_jobs({}, {}), [])

    def test_state_round_trip_and_default_path_is_outside_the_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "state.json"
            self.assertEqual(worker.load_state(path), {})
            worker.save_state(path, {"job-a": "10"}, "2026-10-23T00:00:00Z")
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved, {"polled_utc": "2026-10-23T00:00:00Z", "jobs": {"job-a": "10"}})
            self.assertEqual(worker.load_state(path), {"job-a": "10"})
            path.write_text("not json", encoding="utf-8")
            with self.assertRaises(worker.ConfigError):
                worker.load_state(path)
        default = worker.default_state_path({"HOME": "/home/operator"})
        self.assertEqual(str(default), "/home/operator/.local/state/near-agent/state.json")
        repo = Path(__file__).resolve().parents[2]
        self.assertNotIn(str(repo), str(default))
        self.assertEqual(str(worker.default_state_path({"HOME": "/h", "XDG_STATE_HOME": "/var/state"})),
                         "/var/state/near-agent/state.json")

    def test_state_file_never_holds_the_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            worker.save_state(path, {"job-a": "10"}, "2026-10-23T00:00:00Z")
            self.assertNotIn(FAKE_TOKEN, path.read_text(encoding="utf-8"))


class ActGateTests(unittest.TestCase):
    def test_undocumented_action_sends_nothing_even_with_execute(self):
        for action in ("start", "message", "submit", "bid"):
            if worker.ACTIONS.get(action) is not None:
                continue
            transport = FakeTransport()
            code, out, err = run([action, "id-1", "--text", "x", "--amount", "1", "--execute"], transport)
            self.assertEqual(code, 2)
            self.assertEqual(transport.sent, [])
            self.assertIn("not recorded in this repo", err)


if __name__ == "__main__":
    unittest.main()
