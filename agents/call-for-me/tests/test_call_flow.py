"""Tests for the Call-for-Me Booking agent (issue #79).

Every brief, business and dialogue here is SYNTHETIC: written by hand for
these tests. No call was placed and no business named here exists.
"""
import copy
import datetime as dt
import glob
import io
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import call_for_me as c  # noqa: E402
import call_sources as sources  # noqa: E402

SCENARIOS = sorted(glob.glob(os.path.join(ROOT, "scenarios", "*.json")))


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(obj, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def brief_raw(**over):
    """SYNTHETIC restaurant brief used across the tests."""
    raw = copy.deepcopy(load_json(os.path.join(ROOT, "scenarios", "01-standard-booking.json"))["brief"])
    raw["callback_number"] = None
    for k, v in over.items():
        raw[k] = v
    return raw


def utc(text):
    return dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


class BriefTests(unittest.TestCase):
    def test_valid_brief_is_confirmed_before_any_call(self):
        b = c.validate_brief(brief_raw())
        text = c.confirmed_brief_text(b)
        self.assertIn("Confirmed brief", text)
        self.assertIn("a table for 4 on Friday November 13, 2026 between 7:00 pm and 8:30 pm", text)
        self.assertIn("Pre-approved alternatives: none", text)
        self.assertIn("will not share one", text)

    def test_rejects_payment_fields_anywhere(self):
        for key in ("card_number", "deposit_ok", "payment"):
            raw = brief_raw()
            raw["booking"][key] = "x"
            with self.assertRaisesRegex(c.BriefError, "payment"):
                c.validate_brief(raw)

    def test_business_numbers_only_and_operating_country(self):
        raw = brief_raw(); raw["business"]["phone_source"] = ""
        with self.assertRaisesRegex(c.BriefError, "phone_source"):
            c.validate_brief(raw)
        raw = brief_raw(); raw["business"]["country"] = "CA"
        with self.assertRaisesRegex(c.BriefError, "country"):
            c.validate_brief(raw)
        raw = brief_raw(); raw["business"]["phone"] = "+442071234567"
        with self.assertRaisesRegex(c.BriefError, r"\+1"):
            c.validate_brief(raw)

    def test_needs_exactly_one_of_party_size_or_service(self):
        raw = brief_raw(); raw["booking"]["service"] = "haircut"
        with self.assertRaisesRegex(c.BriefError, "exactly one"):
            c.validate_brief(raw)
        raw = brief_raw(); del raw["booking"]["party_size"]
        with self.assertRaisesRegex(c.BriefError, "exactly one"):
            c.validate_brief(raw)

    def test_opening_hours_timezone_language_window(self):
        raw = brief_raw(); del raw["business"]["opening_hours"]
        with self.assertRaisesRegex(c.BriefError, "opening_hours"):
            c.validate_brief(raw)
        raw = brief_raw(); raw["business"]["timezone"] = "Mars/Olympus"
        with self.assertRaisesRegex(c.BriefError, "timezone"):
            c.validate_brief(raw)
        with self.assertRaisesRegex(c.BriefError, "English only"):
            c.validate_brief(brief_raw(report_language="fr"))
        raw = brief_raw(); raw["booking"]["end"] = "18:00"
        with self.assertRaisesRegex(c.BriefError, "after"):
            c.validate_brief(raw)


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.b = c.validate_brief(brief_raw())

    def test_calls_only_inside_opening_and_calling_hours_with_gap_and_limit(self):
        times = c.plan_attempts(self.b, utc("2026-11-12T15:00:00Z"))   # Thu 09:00 CST, opens 11:30
        local = [t.astimezone(self.b["business"]["tz"]).strftime("%a %H:%M") for t in times]
        self.assertEqual(local, ["Thu 11:30", "Thu 12:00", "Thu 12:30"])
        self.assertEqual(len(times), c.POLICY["max_attempts"])

    def test_evening_rolls_to_next_open_day_and_respects_calling_hours(self):
        times = c.plan_attempts(self.b, utc("2026-11-11T01:50:00Z"))   # Tue 19:50 CST
        local = [t.astimezone(self.b["business"]["tz"]).strftime("%a %H:%M") for t in times]
        self.assertEqual(local, ["Tue 19:50", "Wed 11:30", "Wed 12:00"])

    def test_closed_day_skipped(self):
        times = c.plan_attempts(self.b, utc("2026-11-09T15:00:00Z"))   # Mon, closed
        self.assertEqual(times[0].astimezone(self.b["business"]["tz"]).strftime("%a %H:%M"), "Tue 11:30")

    def test_no_call_after_deadline(self):
        deadline = c.call_deadline(self.b)
        self.assertEqual(deadline.astimezone(self.b["business"]["tz"]).strftime("%a %H:%M"), "Fri 18:00")
        self.assertIsNone(c.next_allowed(self.b, deadline))
        out = c.run_job(self.b, c.ScriptedLine([]), deadline)
        self.assertEqual((out["status"], out["reason"], out["attempts"]), ("not booked", "no_call_window", []))


class UnderstandTests(unittest.TestCase):
    FRI = dt.date(2026, 11, 13)

    THU = dt.date(2026, 11, 12)   # the day of the call

    def slots(self, text):
        return [(s.date, s.readings) for s in c.understand(text, self.FRI, self.FRI, self.THU).slots]

    def test_day_after_or_before_the_time_binds(self):
        self.assertEqual(self.slots("I can do 7:30 Saturday."), [(dt.date(2026, 11, 14), [450, 1170])])
        self.assertEqual(self.slots("Saturday at 2:30 pm or Tuesday at 10 am"),
                         [(dt.date(2026, 11, 14), [870]), (dt.date(2026, 11, 17), [600])])
        self.assertEqual(self.slots("We have 8:15."), [(self.FRI, [495, 1215])])
        # nearest to the requested day, never before the day of the call
        self.assertEqual(c.understand("Thursday at 6 pm", self.FRI, self.FRI, self.THU).slots[0].date, self.THU)
        self.assertEqual(c.understand("Tuesday at 6 pm", self.FRI, self.FRI).slots[0].date, dt.date(2026, 11, 10))

    def test_non_offers_are_not_slots(self):
        for text in ("We have nothing between 7 and 8:30.", "We close at 10 pm on Fridays.",
                     "Is that for 4 people?", "Your confirmation number is BN4471.", "We open at 11:30."):
            self.assertEqual(self.slots(text), [], text)

    def test_intents(self):
        def i(t):
            return c.understand(t, self.FRI, self.FRI).intents
        for t in ("Is this a robot?", "Am I talking to a real person?", "Is this a recording?", "Are you human?",
                  "is this a robot", "are you a bot or something", "wait am i talking to an AI", "is this automated"):
            self.assertIn("ask_ai", i(t), t)
        for t in ("It's 40 dollars a person.", "I can do 7:30 on Friday.", "How many people?"):
            self.assertNotIn("ask_ai", i(t), t)
        self.assertIn("refuse_ai", i("We don't take bookings from robots."))
        self.assertNotIn("ask_ai", i("We don't take bookings from robots."))
        self.assertIn("ask_payment", i("We need a credit card to hold the table."))
        self.assertIn("payment_required", i("We can't hold it without a card."))
        self.assertIn("do_not_call", i("Please don't call here again."))
        self.assertEqual(c.understand("Your confirmation number is BN4471.", self.FRI, self.FRI).confirmation, "BN4471")
        self.assertEqual(c.payment_kinds("a deposit and a no-show fee, paid upfront"), ["deposit", "prepayment", "cancellation fee"])


def session(raw=None):
    b = c.validate_brief(raw or brief_raw())
    s = c.CallSession(b)
    s.start()
    return s


class PolicyTests(unittest.TestCase):
    def test_books_only_inside_window_or_pre_approved_alternative(self):
        raw = brief_raw(alternatives=[{"date": "2026-11-14", "start": "18:30", "end": "19:00"}])
        b = c.validate_brief(raw)
        allowed = {(b["window"]["date"], m) for m in range(b["window"]["start"], b["window"]["end"] + 1)}
        allowed |= {(dt.date(2026, 11, 14), m) for m in range(18 * 60 + 30, 19 * 60 + 1)}
        checked = 0
        for day, word in ((dt.date(2026, 11, 12), "Thursday"), (dt.date(2026, 11, 13), "Friday"),
                          (dt.date(2026, 11, 14), "Saturday")):
            for minute in range(0, 24 * 60, 15):
                for spoken in (c.fmt_time(minute), "%d:%02d" % ((minute // 60) % 12 or 12, minute % 60)):
                    s = session(raw)
                    s.hear("We could do %s on %s." % (spoken, word))
                    s.hear("You're all set.")
                    checked += 1
                    if s.end == "booked":
                        self.assertIn(s.booked[:2], allowed, (spoken, word))
                        self.assertEqual(s.booked[2], day != b["window"]["date"])
                    elif (day, minute) in allowed and spoken == c.fmt_time(minute):
                        self.fail("refused an explicit in-window time %s %s" % (spoken, word))
        self.assertGreater(checked, 500)

    def test_booking_needs_the_business_to_confirm(self):
        s = session()
        s.hear("I can do 7:45 on Friday.")
        self.assertIsNone(s.booked)
        self.assertEqual(s.said[-1], "ACCEPT")
        s.hear("You're all set, confirmation number is ZX12.")
        self.assertEqual((s.end, s.confirmation), ("booked", "ZX12"))

    def test_confirmation_of_a_different_out_of_window_time_does_not_book(self):
        s = session()
        s.hear("I can do 7:45 on Friday.")
        s.hear("Actually I've put you down for 9:30 pm Friday, you're all set.")
        self.assertNotEqual(s.end, "booked")
        self.assertIn({"date": "2026-11-13", "time": "9:30 pm", "stated": "9:30 pm Friday"}, s.alternatives)

    def test_payment_is_always_declined_and_blocks_acceptance(self):
        for ask in ("We need a credit card to hold the table.", "There's a 20 dollar deposit.",
                    "We ask guests to prepay.", "Is a cancellation fee of 30 dollars okay?"):
            s = session()
            s.hear("I have 7:30 Friday. " + ask)
            self.assertEqual(s.said[-1], "PAYMENT_DECLINE", ask)
            self.assertNotIn("ACCEPT", s.said, ask)
            s.hear("Sorry, we can't hold it without that.")
            self.assertEqual(s.end, "payment_required", ask)
            self.assertEqual(s.conditional[:2], (dt.date(2026, 11, 13), 19 * 60 + 30))

    def test_payment_waived_then_booked(self):
        s = session()
        s.hear("8 pm Friday works, but we need a card.")
        s.hear("No problem, we can do it without a card.")
        self.assertEqual(s.said[-1], "ACCEPT")
        s.hear("You're booked.")
        self.assertEqual(s.end, "booked")

    def test_ai_question_always_answered_yes_with_who_it_calls_for(self):
        s = session()
        out = s.hear("Hold on, am I talking to a real person?")
        self.assertTrue(out[0].startswith("Yes, I am an AI."))
        self.assertIn("on behalf of Jordan Rivera", out[0])
        self.assertTrue(c.TEMPLATES["OPENING"].startswith("Hello, this is an automated booking assistant, an AI, calling on behalf of"))

    def test_callback_only_when_buyer_approved(self):
        s = session()
        self.assertEqual(s.hear("What's a good callback number?")[0][:30], c.TEMPLATES["NO_CALLBACK"][:30])
        self.assertFalse(s.callback_shared)
        # SYNTHETIC callback number from the reserved 555-01xx example range
        s = session(brief_raw(callback_number="+15125550142"))
        self.assertEqual(s.hear("What's a good callback number?"), ["The callback number is 512 555 0142."])

    def test_unclear_ends_after_limit(self):
        s = session()
        for _ in range(c.POLICY["max_unclear"]):
            self.assertEqual(s.hear("Mmm hmm."), [c.TEMPLATES["REPEAT"]])
        s.hear("Mmm hmm.")
        self.assertEqual(s.end, "unclear")

    def test_session_stores_no_business_speech(self):
        s = session()
        said = "I can do 7:45 on Friday, and we love our new patio heaters this season."
        s.hear(said)
        blob = json.dumps({k: v for k, v in vars(s).items() if k != "brief"}, default=str)
        self.assertNotIn("patio heaters", blob)


class JobTests(unittest.TestCase):
    def setUp(self):
        self.b = c.validate_brief(brief_raw())

    def run_lines(self, attempts):
        line = c.ScriptedLine(attempts)
        return c.run_job(self.b, line, utc("2026-11-12T15:00:00Z")), line

    def test_hang_up_and_stop_requests_are_not_retried(self):
        out, _ = self.run_lines([{"result": "answered", "turns": ["Bella Notte.", {"hangup": True}]}, {"result": "busy"}])
        self.assertEqual((out["status"], out["reason"], len(out["attempts"])), ("not booked", "hung_up", 1))
        out, _ = self.run_lines([{"result": "answered", "turns": ["Hello.", "Stop calling us."]}, {"result": "busy"}])
        self.assertEqual((out["reason"], len(out["attempts"])), ("asked_not_to_call", 1))

    def test_dropped_call_is_retried_and_alternatives_kept_across_attempts(self):
        out, _ = self.run_lines([
            {"result": "answered", "turns": ["Hello.", "We're full Friday but have 9:45 pm."]},
            {"result": "answered", "turns": ["Hello again.", "Yes, 7 pm Friday opened up.", "You're all set."]}])
        self.assertEqual(out["status"], "booked")
        self.assertEqual([a["result"] for a in out["attempts"]], ["answered", "answered"])
        self.assertEqual(out["attempts"][0]["ended"], "dropped")
        self.assertEqual([(a["date"], a["time"]) for a in out["alternatives_offered"]], [("2026-11-13", "9:45 pm")])

    def test_unclear_on_every_attempt_reports_unclear(self):
        mumble = {"result": "answered", "turns": ["Hello.", "Mmm.", "Mmm.", "Mmm."]}
        out, _ = self.run_lines([mumble, {"result": "no answer"}, mumble])
        self.assertEqual((out["status"], out["reason"]), ("not booked", "unclear"))
        self.assertEqual(len(out["attempts"]), 3)

    def test_unknown_attempt_result_fails_closed(self):
        with self.assertRaises(c.ScenarioError):
            self.run_lines([{"result": "maybe"}])


class ScenarioTests(unittest.TestCase):
    def test_every_scenario_passes_with_invariants(self):
        self.assertGreaterEqual(len(SCENARIOS), 4)
        for path in SCENARIOS:
            scn = load_json(path)
            self.assertIn("SYNTHETIC", scn["_label"], path)
            self.assertIn("SYNTHETIC", scn["brief"]["_label"], path)
            _, outcome, dialogue, fails = c.run_scenario(scn, os.path.dirname(path))
            self.assertEqual(fails, [], path)

    def test_the_four_job_samples_are_present(self):
        labels = [load_json(p)["label"] for p in SCENARIOS]
        for n in range(1, 5):
            self.assertTrue(any(l.startswith("Job sample %d:" % n) for l in labels), n)

    def test_invariants_catch_a_bad_outcome(self):
        scn = load_json(SCENARIOS[0])
        b, outcome, dialogue, _ = c.run_scenario(scn)
        bad = copy.deepcopy(outcome)
        bad["booking"]["time"] = "10:30 pm"
        bad["alternatives_offered"] = [{"date": None, "time": "x", "stated": "x", "booked": True}]
        bad["note"] = scn["attempts"][0]["turns"][4]
        dialogue = dialogue + [{"attempt": 9, "result": "answered", "turns": [("agent", "No, I'm a real person."),
                                                                              ("agent", "My card is 4111 1111 1111 1111.")]}]
        fails = c.check_invariants(b, bad, dialogue, [t for t in scn["attempts"][0]["turns"]])
        joined = "\n".join(fails)
        for needle in ("outside the window", "marked booked", "business speech", "denied being an AI", "card-like"):
            self.assertIn(needle, joined)

    def test_report_has_status_details_attempts_alternatives(self):
        for path in SCENARIOS:
            _, outcome, _, _ = c.run_scenario(load_json(path))
            text = c.render_report(outcome)
            for heading in ("**Status:", "## Booking details", "## Alternatives the business offered", "## Every attempt", "## What was kept"):
                self.assertIn(heading, text, path)
            self.assertNotRegex(text, r"(?i)please (send|provide|give) (us |me )?(your )?(card|payment)")


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        code = c.main(argv, out, err)
        return code, out.getvalue(), err.getvalue()

    def test_call_always_refuses(self):
        code, out, err = self.run_cli(["call", "--execute", "--to", "+15125550134"])
        self.assertEqual(code, 2)
        self.assertIn("No call was placed", err)

    def test_simulate_check_and_plan(self):
        code, out, _ = self.run_cli(["simulate"] + SCENARIOS)
        self.assertEqual(code, 0)
        self.assertEqual(out.count("\nPASS "), len(SCENARIOS))
        path = os.path.join(ROOT, "scenarios", "01-standard-booking.json")
        tmp = os.path.join(HERE, "_brief.tmp.json")
        try:
            write_json(load_json(path)["brief"], tmp)
            code, out, _ = self.run_cli(["check", "--brief", tmp])
            self.assertEqual(code, 0); self.assertIn("Confirmed brief", out)
            code, out, _ = self.run_cli(["plan", "--brief", tmp, "--start", "2026-11-12T15:00:00Z"])
            self.assertEqual(code, 0); self.assertIn("attempt 3:", out)
        finally:
            os.remove(tmp)

    def test_failed_expectation_exits_1_and_bad_brief_exits_2(self):
        scn = load_json(SCENARIOS[0])
        scn["expect"]["status"] = "no answer"
        tmp = os.path.join(HERE, "_scn.tmp.json")
        try:
            write_json(scn, tmp)
            code, out, _ = self.run_cli(["simulate", tmp])
            self.assertEqual(code, 1); self.assertIn("FAIL", out)
            scn["brief"]["business"]["country"] = "GB"
            write_json(scn, tmp)
            code, out, err = self.run_cli(["simulate", tmp])
            self.assertEqual(code, 2); self.assertIn("No report emitted", err)
        finally:
            os.remove(tmp)


class DocsAndSourcesTests(unittest.TestCase):
    def test_design_names_every_acceptance_criterion_and_fail_signal(self):
        text = read_text(os.path.join(ROOT, "DESIGN.md"))
        for n in range(1, 8):
            self.assertIn("Criterion %d" % n, text)
        for signal in ("Books a time outside the buyer's window or alternatives",
                       "Denies being an AI when asked",
                       "Gives, or asks the buyer for, payment information",
                       "Keeps a recording or transcript after the job"):
            self.assertIn(signal, text)
        for key in ("OPENING", "AI_ANSWER", "PAYMENT_DECLINE"):
            self.assertIn(c.TEMPLATES[key].split("{")[0][:40], text, key)

    def test_provenance_is_complete_and_every_excerpt_is_in_the_evaluation(self):
        prov = sources.load_provenance()
        self.assertEqual(set(prov["captures"]), set(sources.CAPTURES))
        for name, meta in prov["captures"].items():
            self.assertRegex(meta["sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(meta["retrieved_utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
            self.assertIn(sources.TWILIO_COMMIT if meta["provider"] == "Twilio" else sources.TELNYX_COMMIT, meta["url"])
        self.assertEqual([x["id"] for x in prov["claims"]], [x[0] for x in sources.CLAIMS])
        doc = read_text(os.path.join(ROOT, "PROVIDERS.md"))
        for claim in prov["claims"]:
            link = sources.source_link(prov, claim)
            self.assertIn(link, doc, claim["id"])
            block = "\n".join(claim["raw"])
            self.assertIn(block, doc, claim["id"])
            self.assertLess(doc.index(link), doc.index(block), claim["id"])

    @unittest.skipUnless(os.environ.get("CALL_FOR_ME_CAPTURES"), "set CALL_FOR_ME_CAPTURES to a folder of fetched captures")
    def test_captures_verify(self):
        self.assertEqual(sources.verify(os.environ["CALL_FOR_ME_CAPTURES"]), [])

    def test_verify_detects_a_changed_capture(self):
        import tempfile
        prov = sources.load_provenance()
        with tempfile.TemporaryDirectory() as d:
            for name in prov["captures"]:
                with open(os.path.join(d, name), "w") as fh:
                    fh.write("not the capture\n")
            problems = sources.verify(d, prov)
        self.assertEqual(len(problems), len(prov["captures"]))
        self.assertTrue(all("sha256 mismatch" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
