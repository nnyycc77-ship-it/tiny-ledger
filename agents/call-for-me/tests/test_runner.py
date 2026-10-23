"""Tests for the offline Call-for-Me runner over a fake provider (issue #109).

Every script here is SYNTHETIC: written by hand for these tests. No call was
placed, no provider account exists, and no business named here exists.
"""
import datetime as dt
import glob
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import call_for_me as cfm  # noqa: E402
import call_runner as runner  # noqa: E402

PROVIDER_SCENARIOS = sorted(glob.glob(os.path.join(ROOT, "scenarios", "provider", "*.json")))


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def scenario(name):
    return load(os.path.join(ROOT, "scenarios", "provider", name + ".json"))


def utc(text):
    return dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


class ScenarioSuite(unittest.TestCase):
    def test_every_provider_scenario_passes(self):
        self.assertGreaterEqual(len(PROVIDER_SCENARIOS), 6)
        for path in PROVIDER_SCENARIOS:
            scn = load(path)
            self.assertIn("SYNTHETIC", scn["_label"], path)
            _, _, _, fails = runner.run_scenario(scn)
            self.assertEqual(fails, [], path)

    def test_refusal_is_a_polite_stop_and_a_report(self):
        _, outcome, provider, _ = runner.run_scenario(scenario("p4-refusal-polite-stop"))
        self.assertEqual((outcome["status"], outcome["reason"], outcome["booking"]), ("not booked", "declined_ai_caller", None))
        self.assertEqual(len(provider.calls), 1)   # not retried
        self.assertEqual(provider.calls[0].log["turns"][-1], ("agent", cfm.TEMPLATES["POLITE_END"]))
        self.assertIn("declined to take a booking from an AI caller", cfm.render_report(outcome))

    def test_outside_window_counter_offer_books_nothing_and_reports(self):
        _, outcome, provider, _ = runner.run_scenario(scenario("p6-counter-offer-outside-window"))
        self.assertEqual(outcome["status"], "not available")
        self.assertIsNone(outcome["booking"])
        self.assertTrue(all(not a["booked"] for a in outcome["alternatives_offered"]))
        agent = [t for w, t in provider.calls[0].log["turns"] if w == "agent"]
        self.assertFalse(any(t.startswith("That works. Please book") for t in agent))
        self.assertTrue(agent[-1].startswith("Thank you. I won't book anything now"))
        report = cfm.render_report(outcome)
        self.assertIn('as stated: "9:45 pm Friday"', report)

    def test_inside_window_counter_offer_books_that_time(self):
        _, outcome, _, _ = runner.run_scenario(scenario("p5-counter-offer-inside-window"))
        self.assertEqual((outcome["booking"]["date"], outcome["booking"]["time"]), ("2026-11-13", "8:15 pm"))

    def test_transfer_redisclosure_and_booking(self):
        _, outcome, provider, _ = runner.run_scenario(scenario("p1-transfer-to-reservations"))
        openings = [t for w, t in provider.calls[0].log["turns"] if w == "agent" and t.startswith("Hello, this is an automated booking assistant, an AI")]
        self.assertEqual(len(openings), 2)
        self.assertEqual(outcome["attempts"][0]["transfers"], ["reservations"])
        self.assertEqual(outcome["booking"]["confirmation"], "RS715")

    def test_voicemail_gets_no_message_and_is_retried(self):
        _, outcome, provider, _ = runner.run_scenario(scenario("p7-transfer-to-voicemail"))
        turns = provider.calls[0].log["turns"]
        self.assertEqual(turns[-1], ("business", "[transfers the call to voicemail]"))
        self.assertEqual(len(outcome["attempts"]), cfm.POLICY["max_attempts"])
        self.assertEqual(outcome["status"], "no answer")

    def test_hold_limit_ends_the_call_and_retries(self):
        _, outcome, provider, _ = runner.run_scenario(scenario("p8-hold-too-long"))
        first = outcome["attempts"][0]
        self.assertEqual(first["ended"], "held_too_long")
        self.assertGreater(first["hold_seconds"], runner.PROVISIONAL["hold_limit_s"])
        self.assertEqual(provider.calls[0].log["turns"][-1], ("agent", runner.RUNNER_TEMPLATES["HOLD_END"]))
        self.assertEqual(outcome["status"], "booked")


class ProviderBoundary(unittest.TestCase):
    def test_dial_refuses_recording_and_stored_transcripts(self):
        p = runner.FakeProvider([{"result": "answered", "turns": ["hi"]}] * 2)
        with self.assertRaises(runner.DialRefused):
            p.dial("+15125550134", utc("2026-11-12T17:30:00Z"), record=True)
        with self.assertRaises(runner.DialRefused):
            p.dial("+15125550134", utc("2026-11-12T17:30:00Z"), store_transcript=True)
        self.assertEqual(len(p.calls), 0)

    def test_every_dial_carries_policy_settings_and_no_recording(self):
        for path in PROVIDER_SCENARIOS:
            _, _, provider, _ = runner.run_scenario(load(path))
            for d in provider.dial_log:
                self.assertEqual((d["record"], d["store_transcript"]), (False, False), path)
                self.assertEqual(d["ring_timeout_s"], cfm.POLICY["ring_timeout_s"], path)
                self.assertEqual(d["time_limit_s"], cfm.POLICY["call_time_limit_s"], path)

    def test_outcome_keeps_no_business_speech(self):
        scn = scenario("p1-transfer-to-reservations")
        _, outcome, _, _ = runner.run_scenario(scn)
        blob = json.dumps(outcome)
        for said in ("Reservations, this is Sam.", "Bella Notte front desk."):
            self.assertNotIn(said, blob)

    def test_runner_invariants_catch_missing_disclosure_and_voicemail_message(self):
        brief = cfm.validate_brief(scenario("p1-transfer-to-reservations")["brief"])
        p = runner.FakeProvider([{"result": "answered", "turns": []}])
        call = p.dial("+15125550134", utc("2026-11-12T17:30:00Z"))
        call.log["turns"] = [("business", "Hello."), ("agent", "Hi, I'd like a table."),
                             ("business", "[transfers the call to voicemail]"), ("agent", "Please call back.")]
        call.events.append("transfer:voicemail")
        fails = "\n".join(runner.check_runner_invariants(brief, {}, p))
        self.assertIn("not the AI disclosure", fails)
        self.assertIn("spoke into voicemail", fails)

    def test_unknown_call_result_fails_closed(self):
        p = runner.FakeProvider([{"result": "maybe"}])
        with self.assertRaises(cfm.ScenarioError):
            p.dial("+15125550134", utc("2026-11-12T17:30:00Z"))


class ConfirmationCodes(unittest.TestCase):
    FRI = dt.date(2026, 11, 13)

    def code(self, text):
        return cfm.understand(text, self.FRI, self.FRI).confirmation

    def test_short_codes_kept_words_rejected(self):
        self.assertEqual(self.code("Your confirmation number is H8."), "H8")
        self.assertEqual(self.code("The confirmation code is RSVP."), "RSVP")
        self.assertIsNone(self.code("Confirmation number is in your email."))
        self.assertIsNone(self.code("The confirmation code is your phone number."))


class Cli(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        return runner.main(argv, out, err), out.getvalue(), err.getvalue()

    def test_exit_codes(self):
        code, out, _ = self.run_cli(PROVIDER_SCENARIOS)
        self.assertEqual(code, 0)
        self.assertEqual(out.count("\nPASS "), len(PROVIDER_SCENARIOS))
        scn = scenario("p3-busy-then-answer")
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.json")
            scn["expect"]["status"] = "no answer"
            with open(bad, "w") as fh:
                json.dump(scn, fh)
            code, out, _ = self.run_cli([bad])
            self.assertEqual(code, 1)
            scn["calls"] = []
            with open(bad, "w") as fh:
                json.dump(scn, fh)
            code, _, err = self.run_cli([bad])
            self.assertEqual(code, 2)
            self.assertIn("No report emitted", err)


if __name__ == "__main__":
    unittest.main()
