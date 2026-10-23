# Call-for-Me offline runner

Issue #109. `call_runner.py` plays the call flows in `DESIGN.md` through a fake telephony provider, so the design is tested behaviour before any award, account or real call exists. It is fully offline. It uses no provider account, no number, no key, and no real provider configuration, and every script is SYNTHETIC.

```
python3 agents/call-for-me/call_runner.py agents/call-for-me/scenarios/provider/*.json [--dialogue] [--json]
python3 -m unittest discover -s agents/call-for-me/tests
```

The runner exits 0 when every scenario passes, 1 on any failed expectation or invariant, and 2 when a scenario cannot run.

## What it adds to the merged harness

PR #92 already ships the policy (`CallSession`) and a scripted line (`ScriptedLine` and `run_job`) with eight scenarios. This runner keeps `CallSession` as it is, so every rule still lives in one place, and adds two things:

- **`FakeProvider`**, a provider-shaped fake. `dial(number, at, record=False, store_transcript=False, ring_timeout_s, time_limit_s)` returns a `FakeCall`, which emits call events and business turns:
  - call events: `initiated`, `ringing`, then `answered`, `busy`, `no answer`, `voicemail` or `phone menu`, then `completed`;
  - turns within a call: speech, hold, transfer, transfer to voicemail, and hang-up.

  DESIGN.md section 2 specifies the line as `dial(number, at)`. The keyword settings are the live-stage settings named in DESIGN.md section 9 and PROVIDERS.md: recording off, ring timeout and call time limit. The fake refuses any dial that asks for recording or a stored transcript, and it logs every dial's settings.
- **`run_provider_job`**, the attempt loop of `run_job` played through the provider. It reaches the business, states the party and window (`OPENING`), handles hold and transfer, confirms or takes a pre-approved alternative, and closes with the summary line. Its outcome record is the merged `outcome_record`, so the report is unchanged.

## Scenarios and the design rule each assertion traces to

| Scenario | Flow | Asserted | DESIGN.md |
| --- | --- | --- | --- |
| p1-transfer-to-reservations | front desk transfers to reservations | booked 7:15 pm with the confirmation code; OPENING said twice, once to each person; events end `transfer:reservations`, `completed:agent` | sections 3 and 4 (disclosure on every answered call), 5 (read-back and confirmation), 8 (confirmation number) |
| p2-hold-then-answer | 90 s hold within the limit, then an offer | booked 8:00 pm, code `H8` | 3, 5, 8 |
| p3-busy-then-answer | busy, then a retry after the gap | booked; both attempts listed | 7 (retries), 8 (every attempt) |
| p4-refusal-polite-stop | "Is this a robot?", then a refusal | AI_ANSWER, then POLITE_END; not booked, reason `declined_ai_caller`; no retry | 4 (AI answer), 7 (refusals not retried), criterion 3 |
| p5-counter-offer-inside-window | first choice gone, 8:15 pm offered | booked 8:15 pm; no alternatives | 5, criterion 1 |
| p6-counter-offer-outside-window | only 9:45 pm Friday or 6 pm Saturday offered | ASK_IN_WINDOW, then NOT_BOOKED_END; nothing booked; both offers reported with their words | 5, criterion 2 |
| p7-transfer-to-voicemail | transfer lands on voicemail | the agent says nothing after the transfer and hangs up; retried to the limit; status `no answer` | 7 (voicemail retried), 9 (keep only report fields) |
| p8-hold-too-long | 240 s of hold in one call, then a later attempt | HOLD_END, ended `held_too_long`, retried, then booked | 7, plus the provisional hold limit below |

Every scenario is also checked against two sets of invariants:
- **The merged `check_invariants`:**
  - attempts stay within the limit and inside opening and calling hours;
  - every AI question is answered yes;
  - no denial of being an AI, no card-like number, no agreement to a payment term, and no unapproved number shared;
  - a booking only inside the window or a pre-approved alternative, and no offered alternative booked;
  - no business speech in the outcome.
- **The runner's provider-boundary checks:**
  - every dial asks for no recording and no stored transcript, and carries the `POLICY` ring timeout and time limit;
  - no more dials than the attempt limit;
  - the agent's first line to each new person is the AI disclosure naming the customer;
  - the agent never speaks into voicemail.

## Open design questions

DESIGN.md does not settle these. The runner needs a behaviour to run at all, so it uses the provisional values below. They live in `PROVISIONAL` in `call_runner.py` and are not design decisions; each needs an owner or coordinator answer before the live stage.

| Question | Provisional value | Why this value |
| --- | --- | --- |
| After a transfer, does the agent repeat the AI disclosure to the new person? | `redisclose_after_transfer = True` | The design says OPENING is the first line of every answered call but is silent on a new person mid call. Repeating it is the more conservative reading of the disclosure rule. |
| How long may the agent stay on hold in one call? | `hold_limit_s = 180` | The design sets a call time limit (600 s) but no hold limit. |
| Does a transfer count as a new attempt? | `transfer_counts_as_attempt = False` | The design counts dials; a transfer happens inside one dial. |
| How many transfers before the agent gives up? | `max_transfers = 2` | Not in the design; this stops a transfer loop. |
| Should the agent leave a voicemail? | no message, hang up | DESIGN.md section 7 retries voicemail, and section 9 keeps only report fields. A message would put the customer's name on a recording the agent does not control. |
| Lines the runner itself speaks | `HOLD_END`, `TRANSFER_END` in `RUNNER_TEMPLATES` | The design's template table has no line for ending a hold or a transfer loop. These are fixed text, like the other templates, and should move into DESIGN.md section 4 once agreed. |

## Found while building, and fixed

The merged understanding rules read a confirmation code only when it had at least three characters, so a code like `H8` was dropped and the report said "none given". The same rule is case-insensitive, so ordinary words after "confirmation number is" could be read as codes ("is in your email" gave `in`; "is your phone number" gave `your`). The rule now takes codes of two or more characters, and only when the code holds a digit or is written in capitals. Tests cover all four cases. No other change was made to `call_for_me.py`.

## Not covered

- No real provider. The fake's events are modelled on the Twilio and Telnyx facts in PROVIDERS.md, but no provider API, webhook or audio is exercised.
- Speech recognition. Business turns arrive as clean text, so the understanding rules are tested on scripted wording only.
- Phone menus that need key presses. `phone menu` exists as a call result that is retried; navigating a menu is not built.
