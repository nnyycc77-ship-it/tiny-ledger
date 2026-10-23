"""Tests for the config validation pass and the deadline guard (issue #110).

Run from the repository root:

    python3 -m unittest discover -s near-agent/tests -v

No network: polls replay saved bodies or answer from FakeTransport. The
clock is injected, never read from the system, so every alarm fires at a
known offset. The assignment rows are SYNTHETIC
(fixtures/assignments-deadline-SYNTHETIC.json, recorded in provenance.json):
invented ids and times under the OpenAPI field names quoted on issue #48.
The token and handle are placeholder strings, not credentials.
"""

import datetime
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))

import worker  # noqa: E402

FIXTURES = HERE / "fixtures"
SYNTHETIC = FIXTURES / "assignments-deadline-SYNTHETIC.json"
BOARD = FIXTURES / "board-excerpt.json"
PAYLOAD = json.loads(SYNTHETIC.read_text(encoding="utf-8"))

FAKE_TOKEN = "aat_fake-token-for-tests-only-not-a-real-credential"
HANDLE = "test-agent-handle"
ENV = {worker.TOKEN_ENV: FAKE_TOKEN, worker.HANDLE_ENV: HANDLE, "HOME": "/nonexistent-home-for-tests"}

START = datetime.datetime(2026, 11, 1, tzinfo=datetime.timezone.utc)  # SYNTHETIC: the fixture's start time


def at(**offset):
    """A clock fixed at START plus the offset."""
    moment = START + datetime.timedelta(**offset)
    return lambda: moment


def rows(*ids):
    return [item["assignment"] for item in PAYLOAD["assignments"] if item["assignment"]["assignmentId"] in ids]


def log_lines(folder):
    path = Path(folder) / worker.ALARM_LOG
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def run(argv, env=ENV, clock=None, transport=None):
    out, err = io.StringIO(), io.StringIO()
    code = worker.main(argv, env=env, transport=transport, stdout=out, stderr=err, clock=clock)
    return code, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.alarms = self.root / "alarms"


class FixtureTests(unittest.TestCase):
    def test_synthetic_fixture_is_labelled_and_hashed(self):
        meta = json.loads((FIXTURES / "provenance.json").read_text(encoding="utf-8"))[SYNTHETIC.name]
        self.assertEqual(hashlib.sha256(SYNTHETIC.read_bytes()).hexdigest(), meta["sha256"])
        self.assertTrue(meta["note"].startswith("SYNTHETIC."))
        self.assertIn("SYNTHETIC", SYNTHETIC.name)

    def test_fixture_passes_the_worker_shape_check(self):
        self.assertEqual(len(worker.assignment_rows(PAYLOAD)), 5)
        open_ids = [a["assignmentId"] for a in worker.open_assignments(PAYLOAD)]
        self.assertNotIn("syn-submitted", open_ids)
        self.assertEqual(len(open_ids), 4)


class ParsingTests(unittest.TestCase):
    def test_marketplace_timestamp_forms(self):
        self.assertEqual(worker.parse_utc("2026-10-21T22:52:27.676765Z"),
                         datetime.datetime(2026, 10, 21, 22, 52, 27, 676765, tzinfo=datetime.timezone.utc))
        self.assertEqual(worker.parse_utc("2026-11-02T00:00:00.5Z").microsecond, 500000)
        self.assertEqual(worker.parse_utc("2026-11-02T00:00:00Z"), START + datetime.timedelta(days=1))
        for bad in (None, 5, "", "next tuesday", "2026-11-02 00:00:00Z", "2026-11-02T00:00:00+00:00",
                    "2026-11-02T00:00:00", "2026-13-02T00:00:00Z"):
            self.assertIsNone(worker.parse_utc(bad), bad)

    def test_window_from_sla_seconds_then_from_started_at(self):
        week, = rows("syn-week")
        self.assertEqual(worker.deadline_window(week)[1], 604800)
        day, = rows("syn-day-no-sla")
        self.assertEqual(worker.deadline_window(day)[1], 86400)
        fresh, = rows("syn-fresh")  # startedAt null: the window comes from slaSeconds
        self.assertEqual(worker.deadline_window(fresh)[1], 86400)
        for change in ({"slaDeadlineAt": None}, {"slaSeconds": True, "startedAt": None},
                       {"slaSeconds": 0, "startedAt": "2026-11-09T00:00:00Z"}):
            with self.assertRaises(ValueError):
                worker.deadline_window(dict(week, **change))

    def test_alarm_levels_at_the_thresholds(self):
        day = 86400
        self.assertIsNone(worker.alarm_level(day // 2 + 1, day))
        self.assertEqual(worker.alarm_level(day // 2, day), "half")
        self.assertEqual(worker.alarm_level(day // 4, day), "quarter")
        self.assertEqual(worker.alarm_level(worker.FINAL_SECONDS - 1, day), "final")
        self.assertEqual(worker.alarm_level(-60, day), "final")  # past the deadline
        # A window shorter than two hours is final from the start.
        self.assertEqual(worker.alarm_level(3000, 3600), "final")


class GuardTests(Base):
    def guard(self, clock):
        return worker.DeadlineGuard(self.alarms, HANDLE, clock)

    def test_escalates_half_quarter_final_once_each(self):
        week, = rows("syn-week")
        steps = [({"days": 1}, None), ({"days": 3, "hours": 12}, "half"), ({"days": 4}, None),
                 ({"days": 5, "hours": 6}, "quarter"), ({"days": 5, "hours": 7}, None),
                 ({"days": 6, "hours": 22, "minutes": 1}, "final"), ({"days": 7, "hours": 1}, None)]
        expected = []
        for offset, fired in steps:
            guard = self.guard(at(**offset))
            guard.check([week])
            if fired:
                expected.append(fired)
            self.assertEqual([r["alarm"] for r in log_lines(self.alarms)], expected, offset)
            self.assertEqual(len(guard.take_emitted()), 1 if fired else 0, offset)
        final = log_lines(self.alarms)[-1]
        self.assertEqual(final["remainingSeconds"], 7140)
        self.assertEqual(final["windowSeconds"], 604800)
        self.assertEqual((final["agent"], final["assignmentId"], final["reason"]),
                         (HANDLE, "syn-week", "no submit recorded"))
        marker = json.loads((self.alarms / "syn-week.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["level"], "final")

    def test_a_late_first_poll_jumps_straight_to_the_highest_level(self):
        self.guard(at(days=6, hours=23)).check(rows("syn-week"))
        self.assertEqual([r["alarm"] for r in log_lines(self.alarms)], ["final"])

    def test_submitted_assignments_never_alarm(self):
        submitted = [item["assignment"] for item in PAYLOAD["assignments"]
                     if item["assignment"]["assignmentId"] == "syn-submitted"]
        self.assertEqual(worker.open_assignments({"assignments": [{"assignment": submitted[0]}]}), [])
        self.guard(at(hours=1)).check(worker.open_assignments(PAYLOAD))
        self.assertNotIn("syn-submitted", [r["assignmentId"] for r in log_lines(self.alarms)])

    def test_unreadable_deadline_alarms_instead_of_being_skipped(self):
        guard = self.guard(at(hours=1))
        guard.check(rows("syn-unreadable"))
        guard.check(rows("syn-unreadable"))  # once only
        records = log_lines(self.alarms)
        self.assertEqual([r["alarm"] for r in records], ["unreadable"])
        self.assertIn("slaDeadlineAt is missing or not a UTC timestamp", records[0]["reason"])

    def test_corrupt_marker_fails_closed(self):
        self.alarms.mkdir()
        (self.alarms / "syn-week.json").write_text("{not json", encoding="utf-8")
        with self.assertRaises(worker.ConfigError):
            self.guard(at(days=6, hours=23)).check(rows("syn-week"))

    def test_marker_names_are_escaped_ids(self):
        week, = rows("syn-week")
        self.guard(at(days=6, hours=23)).check([dict(week, assignmentId="../escape/id")])
        self.assertEqual(sorted(p.name for p in self.alarms.iterdir()), ["..%2Fescape%2Fid.json", worker.ALARM_LOG])


class PollHookTests(Base):
    def poll(self, clock, extra=(), env=ENV):
        state = self.root / "state" / "state.json"
        return run(["poll", "--state", str(state), "--alarm-dir", str(self.alarms),
                    "--replay-assignments", str(SYNTHETIC), "--replay-board", str(BOARD)] + list(extra),
                   env=env, clock=clock), state

    def test_poll_runs_the_guard_and_writes_only_its_log_markers_and_the_state(self):
        (code, out, err), state = self.poll(at(hours=22, minutes=30))
        self.assertEqual(code, 0, err)
        self.assertIn("Assignments: 5", out)
        self.assertNotIn("ALARM", out)
        alarm_lines = [line for line in err.splitlines() if line.startswith("ALARM ")]
        fired = sorted((json.loads(line[6:])["assignmentId"], json.loads(line[6:])["alarm"]) for line in alarm_lines)
        self.assertEqual(fired, [("syn-day-no-sla", "final"), ("syn-fresh", "final"), ("syn-unreadable", "unreadable")])
        written = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(written, ["alarms/alarms.log", "alarms/syn-day-no-sla.json", "alarms/syn-fresh.json",
                                   "alarms/syn-unreadable.json", "state/state.json"])
        self.assertNotIn(FAKE_TOKEN, out + err + (self.alarms / worker.ALARM_LOG).read_text(encoding="utf-8"))

    def test_quiet_poll_writes_no_alarm_files(self):
        (code, _, err), _ = self.poll(at(minutes=1))
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(p.name for p in self.alarms.iterdir()), [worker.ALARM_LOG, "syn-unreadable.json"])
        quiet = self.root / "quiet"
        state = self.root / "state2.json"
        code, _, err = run(["poll", "--state", str(state), "--alarm-dir", str(quiet),
                            "--replay-assignments", str(FIXTURES / "assignments-empty.json"),
                            "--replay-board", str(BOARD)], clock=at(minutes=1))
        self.assertEqual((code, err), (0, ""))
        self.assertFalse(quiet.exists())

    def test_default_alarm_dir_sits_beside_the_state_file(self):
        state = self.root / "s" / "state.json"
        code, _, err = run(["poll", "--state", str(state), "--replay-assignments", str(SYNTHETIC),
                            "--replay-board", str(BOARD)], clock=at(minutes=1))
        self.assertEqual(code, 0, err)
        self.assertTrue((self.root / "s" / "alarms" / worker.ALARM_LOG).is_file())

    def test_corrupt_marker_stops_the_poll_before_the_state_is_saved(self):
        self.alarms.mkdir()
        (self.alarms / "syn-fresh.json").write_text('{"level": "panic"}', encoding="utf-8")
        (code, out, err), state = self.poll(at(hours=23))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("unknown level", err)
        self.assertFalse(state.exists())


class ConfigValidationTests(Base):
    def poll(self, env, extra=()):
        transport = FakeTransportNever()
        code, out, err = run(["poll", "--state", str(self.root / "state.json")] + list(extra),
                             env=env, transport=transport, clock=at(minutes=1))
        self.assertEqual(transport.sent, 0)
        return code, out, err

    def test_every_problem_is_named_at_once_and_nothing_is_sent(self):
        env = {worker.TOKEN_ENV: "not-an-agent-token-placeholder", worker.HANDLE_ENV: "Bad Handle!",
               worker.SUBMIT_MAX_ENV: "lots", "HOME": "/nonexistent-home-for-tests"}
        code, out, err = self.poll(env, ["--repeat", "0"])
        self.assertEqual((code, out), (2, ""))
        for reason in ("NEAR_AGENT_TOKEN: not the per agent token shape", "NEAR_AGENT_HANDLE: 'Bad Handle!'",
                       "--repeat: must be at least 1", "NEAR_AGENT_SUBMIT_MAX_BYTES: 'lots' is not a whole number"):
            self.assertIn(reason, err)
        self.assertNotIn("not-an-agent-token-placeholder", err)

    def test_token_shape(self):
        for bad in ("aat_", "fake-token-for-tests-only", "aat_has space-inside", "aat_tab\tinside"):
            code, _, err = self.poll(dict(ENV, **{worker.TOKEN_ENV: bad}))
            self.assertEqual(code, 2, bad)
            self.assertIn("NEAR_AGENT_TOKEN:", err)
            self.assertNotIn(bad.strip(), err.replace(worker.TOKEN_PREFIX + " prefix", ""))

    def test_handle(self):
        env = dict(ENV)
        del env[worker.HANDLE_ENV]
        code, _, err = self.poll(env)
        self.assertEqual(code, 2)
        self.assertIn("NEAR_AGENT_HANDLE: not set", err)
        for bad in ("Hojo", "hojo--agent", "-hojo", "hojo_agent", "hojo/agent"):
            self.assertEqual(self.poll(dict(ENV, **{worker.HANDLE_ENV: bad}))[0], 2, bad)

    def test_submit_limit_must_sit_inside_the_marketplace_rule(self):
        for bad in ("0", "262145", "-1", "1.5"):
            code, _, err = self.poll(dict(ENV, **{worker.SUBMIT_MAX_ENV: bad}))
            self.assertEqual(code, 2, bad)
            self.assertIn("NEAR_AGENT_SUBMIT_MAX_BYTES", err)
        args = worker.build_parser().parse_args(["poll"])
        self.assertEqual(worker.validate_config(args, FAKE_TOKEN, ENV)["submit_max_bytes"], 262144)
        for good in ("1", "262144", "4096"):
            config = worker.validate_config(args, FAKE_TOKEN, dict(ENV, **{worker.SUBMIT_MAX_ENV: good}))
            self.assertEqual(config, {"handle": HANDLE, "submit_max_bytes": int(good)})

    def test_interval_rule_kept(self):
        code, _, err = self.poll(ENV, ["--repeat", "2", "--interval", "5"])
        self.assertEqual(code, 2)
        self.assertIn("--interval: must be at least 30 seconds", err)

    def test_act_commands_are_unchanged_and_need_no_handle(self):
        env = {worker.TOKEN_ENV: "placeholder-without-the-prefix", "HOME": "/nonexistent-home-for-tests"}
        for argv in (["start", "a-1"], ["message", "a-1", "--text", "hi"], ["submit", "a-1", "--text", "x"],
                     ["bid", "j-1", "--amount", "1.00", "--note", "n"]):
            code, out, err = run(argv, env=env, transport=FakeTransportNever())
            self.assertEqual((code, err), (0, ""), argv)
            self.assertIn("DRY RUN: nothing sent.", out)


class FakeTransportNever:
    """Counts requests; any send is a test failure path for the callers above."""

    def __init__(self):
        self.sent = 0

    def send(self, request):
        self.sent += 1
        raise worker.FetchError("test transport: no request may be sent here")


if __name__ == "__main__":
    unittest.main()
