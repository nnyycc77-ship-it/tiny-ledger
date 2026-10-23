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

import hashlib
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

FIXTURES = HERE / "fixtures"
PROVENANCE = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))

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


def fixture_bytes(name):
    return (FIXTURES / name).read_bytes()


def answers_from_fixtures():
    """Fake transport table: the two read URLs answer with the captured bodies."""
    return {
        ("GET", worker.build_url(worker.ASSIGNMENTS_PATH)): (200, [("Content-Type", "application/json")], fixture_bytes("assignments-empty.json")),
        ("GET", worker.build_url(worker.BOARD_PATH, worker.BOARD_QUERY)): (200, [("Content-Type", "application/json")], fixture_bytes("board-excerpt.json")),
    }


class FixtureTests(unittest.TestCase):
    """The captured bodies: provenance recorded, hashes match, shapes as documented."""

    def test_fixture_hashes_match_their_provenance(self):
        for name in ("assignments-empty.json", "board-excerpt.json"):
            meta = PROVENANCE[name]
            self.assertEqual(hashlib.sha256(fixture_bytes(name)).hexdigest(), meta["sha256"], name)
            self.assertTrue(meta["url"].startswith("https://market.near.ai/v1/"))
            self.assertIn("issues/48", meta["source"])
        self.assertIn("ONE JOB EXCERPT", PROVENANCE["board-excerpt.json"]["note"])
        self.assertEqual(PROVENANCE["board-excerpt.json"]["full_capture_job_count"], 32)

    def test_board_excerpt_reads_as_one_job_with_its_budget(self):
        payload = json.loads(fixture_bytes("board-excerpt.json"))
        self.assertEqual(worker.board_jobs(payload), {"52778aa1-7e1b-4d4e-85f9-3a1fa3fe8b7e": "0.1100 USDC"})
        self.assertEqual(worker.job_titles(payload)["52778aa1-7e1b-4d4e-85f9-3a1fa3fe8b7e"],
                         "WURK agent onboarding \u2014 round 2: 100 additional agents")

    def test_empty_assignments_read_as_none(self):
        self.assertEqual(worker.assignment_rows(json.loads(fixture_bytes("assignments-empty.json"))), [])

    def test_unrecognised_shapes_are_refused(self):
        for bad in ({}, {"jobs": "x"}, {"jobs": [{}]}, {"jobs": [{"jobId": "a"}]},
                    {"jobs": [{"jobId": "a", "budgetAmount": 1, "budgetToken": "USDC"}]},
                    {"jobs": [{"jobId": "a", "budgetAmount": "1", "budgetToken": "USDC"}] * 2}):
            with self.assertRaises(worker.FetchError):
                worker.board_jobs(bad)
        for bad in ({}, {"assignments": {}}, {"assignments": [{}]}, {"assignments": [{"assignment": {}}]}):
            with self.assertRaises(worker.FetchError):
                worker.assignment_rows(bad)
        # A documented wrapper with the inner JobAssignment is read; this row is a
        # synthetic shape check using the documented field names, not a capture.
        rows = worker.assignment_rows({"assignments": [{"assignment": {"assignmentId": "as-1", "status": "started"}, "job": {}, "latestMessage": None, "autoAcceptAt": None}]})
        self.assertEqual(rows, [("as-1", "started")])


class PollTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "state.json"

    def test_first_poll_over_the_captures_reports_the_job_as_new_and_saves_state(self):
        transport = FakeTransport(answers_from_fixtures())
        code, out, err = run(["poll", "--state", str(self.state)], transport)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([r.method for r in transport.sent], ["GET", "GET"])
        self.assertEqual([r.url for r in transport.sent],
                         ["https://market.near.ai/v1/agents/me/assignments", "https://market.near.ai/v1/jobs/board?kind=standard"])
        for req in transport.sent:
            self.assertIn(("Authorization", "Bearer " + FAKE_TOKEN), req.headers)
        self.assertIn("Assignments: 0", out)
        self.assertIn("Board jobs (kind=standard): 1", out)
        self.assertIn("Changed since the previous poll: 1", out)
        self.assertIn("- 52778aa1-7e1b-4d4e-85f9-3a1fa3fe8b7e: new; budget 0.1100 USDC;", out)
        self.assertNotIn(FAKE_TOKEN, out)
        self.assertEqual(worker.load_state(self.state), {"52778aa1-7e1b-4d4e-85f9-3a1fa3fe8b7e": "0.1100 USDC"})

    def test_second_poll_reports_no_change_and_a_budget_change_when_it_happens(self):
        transport = FakeTransport(answers_from_fixtures())
        run(["poll", "--state", str(self.state)], transport)
        code, out, _ = run(["poll", "--state", str(self.state)], transport)
        self.assertEqual(code, 0)
        self.assertIn("Changed since the previous poll: 0", out)
        # Synthetic variation of the captured job: budget edited to exercise the diff.
        payload = json.loads(fixture_bytes("board-excerpt.json"))
        payload["jobs"][0]["budgetAmount"] = "0.1200"
        answers = answers_from_fixtures()
        key = ("GET", worker.build_url(worker.BOARD_PATH, worker.BOARD_QUERY))
        answers[key] = (200, [], json.dumps(payload).encode("utf-8"))
        code, out, _ = run(["poll", "--state", str(self.state)], FakeTransport(answers))
        self.assertEqual(code, 0)
        self.assertIn("Changed since the previous poll: 1", out)
        self.assertIn("budget 0.1100 USDC -> 0.1200 USDC", out)

    def test_poll_fails_closed_and_leaves_state_untouched(self):
        answers = answers_from_fixtures()
        key = ("GET", worker.build_url(worker.BOARD_PATH, worker.BOARD_QUERY))
        for status, body in ((401, b'{"detail":"unauthorized"}'), (429, b""), (500, b"x"), (200, b"not json"), (200, b'{"items": []}')):
            answers[key] = (status, [], body)
            code, out, err = run(["poll", "--state", str(self.state)], FakeTransport(answers))
            self.assertEqual(code, 2, (status, body))
            self.assertEqual(out, "")
            self.assertTrue(err.startswith("error: "), err)
            self.assertFalse(self.state.exists())
        code, out, err = run(["poll", "--state", str(self.state)], FakeTransport(error=worker.FetchError("connection reset")))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("connection reset", err)

    def test_replay_from_the_fixture_files_sends_nothing(self):
        transport = FakeTransport()
        code, out, err = run(["poll", "--state", str(self.state),
                              "--replay-assignments", str(FIXTURES / "assignments-empty.json"),
                              "--replay-board", str(FIXTURES / "board-excerpt.json")], transport)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(transport.sent, [])
        self.assertIn("replayed from a file, nothing sent", out)
        self.assertIn("Board jobs (kind=standard): 1", out)
        code, _, err = run(["poll", "--state", str(self.state), "--replay-board", str(FIXTURES / "board-excerpt.json")], transport)
        self.assertEqual(code, 2)
        self.assertIn("go together", err)

    def test_repeat_and_interval_rules(self):
        transport = FakeTransport(answers_from_fixtures())
        code, _, err = run(["poll", "--state", str(self.state), "--repeat", "2", "--interval", "5"], transport)
        self.assertEqual(code, 2)
        self.assertIn("at least 30", err)
        self.assertEqual(transport.sent, [])


class ActTests(unittest.TestCase):
    def test_every_action_is_a_dry_run_without_execute(self):
        cases = {
            "start": (["start", "as-1"], "POST https://market.near.ai/v1/assignments/as-1/start", "(no body)"),
            "message": (["message", "as-1", "--text", "hello"], "POST https://market.near.ai/v1/assignments/as-1/messages", '{"body":"hello"}'),
            "submit": (["submit", "as-1", "--text", "# Report"], "POST https://market.near.ai/v1/assignments/as-1/submit", '{"deliverableMarkdown":"# Report"}'),
            "bid": (["bid", "52778aa1-7e1b-4d4e-85f9-3a1fa3fe8b7e", "--amount", "0.11", "--note", "Delivery in 2 days."],
                    "POST https://market.near.ai/v1/jobs/52778aa1-7e1b-4d4e-85f9-3a1fa3fe8b7e/bids",
                    '{"amount":"0.11","proposal":"Delivery in 2 days."}'),
        }
        for action, (argv, first_line, body_line) in cases.items():
            transport = FakeTransport()
            code, out, err = run(argv, transport)
            self.assertEqual((code, err), (0, ""), action)
            self.assertEqual(transport.sent, [], action)
            self.assertTrue(out.startswith("DRY RUN: nothing sent."), out)
            lines = out.splitlines()
            self.assertIn(first_line, lines)
            self.assertEqual(lines[-1], body_line)
            self.assertIn("Authorization: Bearer " + worker.REDACTED, lines)
            self.assertNotIn(FAKE_TOKEN, out)

    def test_execute_sends_exactly_the_described_request(self):
        url = "https://market.near.ai/v1/jobs/job-9/bids"
        transport = FakeTransport({("POST", url): (201, [], b'{"bidId":"b-1"}')})
        code, out, err = run(["bid", "job-9", "--amount", "0.11", "--note", "p", "--execute"], transport)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(len(transport.sent), 1)
        sent = transport.sent[0]
        self.assertEqual((sent.method, sent.url, sent.body), ("POST", url, b'{"amount":"0.11","proposal":"p"}'))
        self.assertIn(("Authorization", "Bearer " + FAKE_TOKEN), sent.headers)
        self.assertIn("SENT POST " + url, out)
        self.assertNotIn(FAKE_TOKEN, out)
        # A non 2xx answer is reported and exits 2.
        transport = FakeTransport({("POST", url): (403, [], b'{"detail":"forbidden"}')})
        code, out, err = run(["bid", "job-9", "--amount", "0.11", "--note", "p", "--execute"], transport)
        self.assertEqual(code, 2)
        self.assertIn("HTTP 403", out + err)

    def test_required_fields_are_enforced_and_nothing_is_sent(self):
        for argv in (["bid", "job-9", "--amount", "0.11"], ["bid", "job-9", "--note", "p"],
                     ["message", "as-1"], ["submit", "as-1"]):
            transport = FakeTransport()
            code, out, err = run(argv + ["--execute"], transport)
            self.assertEqual(code, 2, argv)
            self.assertEqual(transport.sent, [])
            self.assertIn("required field", err)

    def test_act_request_refuses_undocumented_fields_and_actions(self):
        with self.assertRaises(worker.ConfigError):
            worker.act_request(FAKE_TOKEN, "bid", "job-9", {"amount": "1", "proposal": "p", "agentId": "x"})
        with self.assertRaises(worker.NotDocumented):
            worker.act_request(FAKE_TOKEN, "cancel", "job-9", {})
        req = worker.act_request(FAKE_TOKEN, "bid", "job 9/x", {"amount": "1", "proposal": "p"})
        self.assertEqual(req.url, "https://market.near.ai/v1/jobs/job%209%2Fx/bids")

    def test_action_table_matches_the_quoted_openapi_excerpt(self):
        gives = PROVENANCE["_sources"]["openapi"]["gives"]
        for action, (method, path, required, optional) in worker.ACTIONS.items():
            self.assertEqual(method, "POST")
            self.assertIn("%s %s" % (method, path), gives, action)
            for name in required + optional:
                self.assertIn(name, gives, (action, name))



if __name__ == "__main__":
    unittest.main()
