#!/usr/bin/env python3
"""Offline simulation runner for the Call-for-Me Booking agent (issue #109).

Plays the DESIGN.md call flows through a fake telephony provider, so the
design is tested behaviour before any award, account or real call exists:
reach the business, state the party and window, handle hold and transfer,
confirm or take a pre-approved alternative, close with a summary.

Fully offline. FakeProvider holds no real provider configuration, account,
number or key; it plays SYNTHETIC scripts. The policy is CallSession from
call_for_me.py, used unchanged: every line the agent speaks is a template,
and booking, disclosure, payment and retry rules live there.

  python3 call_runner.py scenarios/provider/*.json [--dialogue] [--json]

Exit 0 when every scenario passes its expectations and the invariants, 1 on
any failure, 2 when a scenario cannot run.
"""
import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import call_for_me as cfm  # noqa: E402

# Provisional choices for questions DESIGN.md leaves open. Each is listed in
# RUNNER.md under "Open design questions"; none is a design decision.
PROVISIONAL = {
    "redisclose_after_transfer": True,   # say OPENING again to the new person
    "hold_limit_s": 180,                 # end the call after this much hold in one call
    "transfer_counts_as_attempt": False, # a transfer stays inside the same attempt
    "max_transfers": 2,                  # end the call after this many transfers
}

# Lines the runner itself may speak. Fixed text, like the policy's templates.
RUNNER_TEMPLATES = {
    "HOLD_END": "I'm sorry, I can't hold any longer. I'll call back later. Goodbye.",
    "TRANSFER_END": "I'm sorry, I'll call back later. Goodbye.",
}

CALL_RESULTS = ("answered", "busy", "no answer", "voicemail", "phone menu", "failed")


class ProviderError(Exception):
    pass


class DialRefused(ProviderError):
    """The fake refuses any dial that would record or keep a transcript."""


class FakeCall(object):
    """One simulated call. Business turns come from the script, in order.

    Script turn forms (SYNTHETIC):
      "text"                          the business says this
      {"say": "text"}                 the same
      {"hold": seconds}               the business puts the call on hold
      {"transfer": "name", "then": [turns]}   transfer; "then" is the new party
      {"transfer": "voicemail"}       transfer lands on voicemail
      {"hangup": true}                the business hangs up
    """

    def __init__(self, provider, n, script):
        self.provider, self.n = provider, n
        self.status = script.get("result", "answered")
        if self.status not in CALL_RESULTS:
            raise cfm.ScenarioError("unknown call result %r" % self.status)
        self.turns = [t if isinstance(t, dict) else {"say": t} for t in script.get("turns", [])]
        self.events = ["initiated", "ringing", self.status if self.status != "answered" else "answered"]
        self.log = {"attempt": n, "result": self.status, "turns": []}
        self.ended = self.status != "answered"
        if self.ended:
            self.events.append("completed")

    def say(self, text):
        """The agent speaks. Kept only in the simulation log, never by the agent."""
        if self.ended:
            raise ProviderError("say on an ended call")
        self.log["turns"].append(("agent", text))

    def next_event(self):
        """Return the next business event: ("say", text), ("hold", s),
        ("transfer", name), ("voicemail", None), ("hangup", None) or ("silence", None)."""
        if self.ended or not self.turns:
            return ("silence", None)
        t = self.turns.pop(0)
        if "transfer" in t:
            target = t["transfer"]
            self.events.append("transfer:%s" % target)
            self.log["turns"].append(("business", "[transfers the call to %s]" % target))
            if target == "voicemail":
                return ("voicemail", None)
            self.turns = [x if isinstance(x, dict) else {"say": x} for x in t.get("then", [])]
            return ("transfer", target)
        if "hold" in t:
            self.events.append("hold:%d" % t["hold"])
            self.log["turns"].append(("business", "[puts the call on hold for %d s]" % t["hold"]))
            return ("hold", int(t["hold"]))
        if t.get("hangup"):
            self.log["turns"].append(("business", "[hangs up]"))
            self.hangup(by="business")
            return ("hangup", None)
        self.log["turns"].append(("business", t["say"]))
        return ("say", t["say"])

    def hangup(self, by="agent"):
        if not self.ended:
            self.ended = True
            self.events.append("completed:%s" % by)


class FakeProvider(object):
    """A provider-shaped fake: dial(number, at, ...) returns a FakeCall.

    DESIGN.md section 2 specifies the line as one method, dial(number, at).
    The keyword settings are the live-stage settings DESIGN.md section 9 and
    PROVIDERS.md name (recording off, ring timeout, call time limit). The fake
    refuses a dial that asks for recording or a stored transcript, and keeps
    every dial's settings in dial_log so tests can assert them.
    """

    def __init__(self, scripts):
        self.scripts = list(scripts)
        self.dial_log = []
        self.calls = []

    @property
    def dialogue(self):
        return [c.log for c in self.calls]

    def dial(self, number, at_utc, record=False, store_transcript=False,
             ring_timeout_s=None, time_limit_s=None):
        settings = {"number": number, "at_utc": at_utc.strftime("%Y-%m-%dT%H:%M:%SZ"), "record": record,
                    "store_transcript": store_transcript, "ring_timeout_s": ring_timeout_s,
                    "time_limit_s": time_limit_s}
        self.dial_log.append(settings)
        if record or store_transcript:
            raise DialRefused("dial refused: recording and stored transcripts are not allowed (DESIGN.md section 9)")
        if not self.scripts:
            raise cfm.ScenarioError("the scenario has no scripted call for attempt %d" % (len(self.calls) + 1))
        call = FakeCall(self, len(self.calls) + 1, self.scripts.pop(0))
        self.calls.append(call)
        return call


def play_call(brief, call, today):
    """Run one answered call through CallSession. Returns (session, ended_how, extras)."""
    session = cfm.CallSession(brief, today=today)
    extras = {"transfers": [], "hold_seconds": 0, "disclosures": 0}
    first = True
    while True:
        kind, value = call.next_event()
        if kind == "say":
            if first:
                lines = session.start()
                extras["disclosures"] += 1
                first = False
            else:
                lines = session.hear(value)
            for line in lines:
                call.say(line)
            if session.done:
                call.hangup()
                return session, session.end, extras
        elif kind == "hold":
            extras["hold_seconds"] += value
            if extras["hold_seconds"] > PROVISIONAL["hold_limit_s"]:
                call.say(RUNNER_TEMPLATES["HOLD_END"])
                call.hangup()
                return session, "held_too_long", extras
        elif kind == "transfer":
            extras["transfers"].append(value)
            if len(extras["transfers"]) > PROVISIONAL["max_transfers"]:
                call.say(RUNNER_TEMPLATES["TRANSFER_END"])
                call.hangup()
                return session, "too_many_transfers", extras
            if PROVISIONAL["redisclose_after_transfer"]:
                first = True   # the new person hears OPENING with their first turn
        elif kind == "voicemail":
            call.hangup()      # never leave a message: no buyer details on a recording
            return session, "voicemail", extras
        elif kind == "hangup":
            session.hung_up()
            return session, session.end, extras
        else:  # silence: the script ran out
            call.hangup()
            if not session.done:
                session.end, session.done = "dropped", True
            return session, session.end, extras


RETRYABLE = set(cfm.RETRYABLE) | {"held_too_long", "too_many_transfers"}


def run_provider_job(brief, provider, start_utc):
    """run_job's attempt loop, played through a provider. Returns the outcome record."""
    attempts, sessions, final = [], [], None
    t = cfm.next_allowed(brief, start_utc)
    if t is None:
        return cfm.outcome_record(brief, attempts, sessions, None, "no_call_window")
    while t is not None and len(attempts) < cfm.POLICY["max_attempts"]:
        call = provider.dial(brief["business"]["phone"], t, record=False, store_transcript=False,
                             ring_timeout_s=cfm.POLICY["ring_timeout_s"], time_limit_s=cfm.POLICY["call_time_limit_s"])
        rec = {"n": len(attempts) + 1, "at_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "at_local": cfm._local(brief, t).strftime("%Y-%m-%d %H:%M %Z"), "result": call.status,
               "provider_events": call.events}
        attempts.append(rec)
        if call.status == "answered":
            session, ended, extras = play_call(brief, call, cfm._local(brief, t).date())
            sessions.append(session)
            rec.update({"ended": ended, "disclosed_ai_at_start": bool(session.said) and session.said[0] == "OPENING",
                        "asked_if_ai": session.asked_if_ai, "answered_ai_yes": session.said.count("AI_ANSWER"),
                        "said": list(session.said), "transfers": extras["transfers"],
                        "hold_seconds": extras["hold_seconds"], "disclosures": extras["disclosures"]})
            if ended not in RETRYABLE:
                final = session
                break
        t = cfm.next_allowed(brief, t + dt.timedelta(minutes=cfm.POLICY["retry_gap_minutes"]))
    return cfm.outcome_record(brief, attempts, sessions, final, None)


def check_runner_invariants(brief, outcome, provider):
    """Rules from DESIGN.md checked at the provider boundary, on top of check_invariants."""
    fails = []
    for d in provider.dial_log:
        if d["record"] or d["store_transcript"]:
            fails.append("a dial asked for recording or a stored transcript: %r" % d)
        if d["ring_timeout_s"] != cfm.POLICY["ring_timeout_s"] or d["time_limit_s"] != cfm.POLICY["call_time_limit_s"]:
            fails.append("a dial did not carry the POLICY ring timeout and time limit: %r" % d)
    if len(provider.dial_log) > cfm.POLICY["max_attempts"]:
        fails.append("more dials than the attempt limit")
    name = brief["name"]
    for call in provider.calls:
        turns = call.log["turns"]
        # disclosure: the agent's first line to each new person (the business,
        # and after a transfer the new party) is OPENING, naming the customer
        expect_opening = True
        for who, text in turns:
            if who == "business" and text.startswith("[transfers the call to") and PROVISIONAL["redisclose_after_transfer"]:
                expect_opening = True
            elif who == "agent" and expect_opening:
                if not (text.startswith("Hello, this is an automated booking assistant, an AI") and ("on behalf of %s" % name) in text):
                    fails.append("call %d: first agent line to a new person is not the AI disclosure: %r" % (call.n, text))
                expect_opening = False
        if any(e.startswith("transfer:voicemail") for e in call.events):
            after = turns[[i for i, t in enumerate(turns) if t[1].startswith("[transfers the call to voicemail")][0] + 1:]
            if any(who == "agent" for who, _ in after):
                fails.append("call %d: the agent spoke into voicemail" % call.n)
    return fails


def run_scenario(scn):
    brief = cfm.validate_brief(scn["brief"])
    start = dt.datetime.strptime(scn["start_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    provider = FakeProvider(scn["calls"])
    outcome = run_provider_job(brief, provider, start)
    texts = []
    for c in scn["calls"]:
        stack = list(c.get("turns", []))
        while stack:
            t = stack.pop(0)
            if isinstance(t, str):
                texts.append(t)
            elif isinstance(t, dict):
                if t.get("say"):
                    texts.append(t["say"])
                stack.extend(t.get("then", []))
    fails = cfm.check_invariants(brief, outcome, provider.dialogue, texts)
    fails += check_runner_invariants(brief, outcome, provider)
    fails += cfm.check_expect(outcome, scn.get("expect", {}), provider.dialogue)
    exp = scn.get("expect", {})
    if "provider_events" in exp:
        got = [c.events for c in provider.calls]
        if got != exp["provider_events"]:
            fails.append("expected provider events %r, got %r" % (exp["provider_events"], got))
    if "disclosures" in exp:
        got = [a.get("disclosures") for a in outcome["attempts"] if "disclosures" in a]
        if got != exp["disclosures"]:
            fails.append("expected disclosures per answered call %r, got %r" % (exp["disclosures"], got))
    if "ended" in exp:
        got = [a.get("ended", a["result"]) for a in outcome["attempts"]]
        if got != exp["ended"]:
            fails.append("expected attempt endings %r, got %r" % (exp["ended"], got))
    return brief, outcome, provider, fails


def main(argv=None, stdout=sys.stdout, stderr=sys.stderr):
    ap = argparse.ArgumentParser(prog="call_runner.py", description="Offline Call-for-Me runner over a fake provider")
    ap.add_argument("scenarios", nargs="+")
    ap.add_argument("--dialogue", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    failed = 0
    try:
        for path in args.scenarios:
            scn = cfm.load_json(path)
            brief, outcome, provider, fails = run_scenario(scn)
            name = os.path.basename(path)
            print("<!-- scenario: %s (%s) -->" % (name, scn.get("label", "")), file=stdout)
            print(json.dumps(outcome, indent=2) if args.json else cfm.render_report(outcome), file=stdout)
            if args.dialogue:
                print(cfm.render_dialogue(provider.dialogue), file=stdout)
                print("Provider events: %s" % json.dumps([c.events for c in provider.calls]), file=stdout)
            for f in fails:
                print("FAIL %s: %s" % (name, f), file=stdout)
            print("%s %s" % ("FAIL" if fails else "PASS", name), file=stdout)
            failed += bool(fails)
    except (cfm.BriefError, cfm.ScenarioError, ProviderError, OSError, ValueError, KeyError) as exc:
        print("error: %s. No report emitted." % exc, file=stderr)
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
