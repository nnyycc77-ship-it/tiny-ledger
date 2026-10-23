# call-for-me: the Call-for-Me Booking agent (design and simulation stage)

Task: issue #79, prebuild for NEAR Agent Market job 92332aa9-7f29-40f2-b173-909d6defed1f ("Call-for-Me Booking Agent", bid pending at 400 USDC). This stage is design plus simulation only. It places no calls, has no telephony account, and spends nothing. Standard library Python only. The tests live in `tests/` and run in CI through `tools/tests/test_call_for_me.py`.

Reconciled against the job description and the bid proposal the coordinator posted verbatim on issue #79 (comments 6366189256 and 6366189929).

| File | What it is |
| --- | --- |
| `DESIGN.md` | Call state machine, exact disclosure wording, alternatives logic, payment refusal path, retry limits, outcome fields, and every acceptance criterion, fail signal and job rule with how the design meets it |
| `PROVIDERS.md` | Twilio and Telnyx compared, each claim sourced from the provider's own API definition with the raw lines beneath; what is still awaiting capture |
| `call_for_me.py` | Brief validation, call schedule, understanding rules, the `CallSession` policy, the job runner, the report, and the simulation harness |
| `call_sources.py`, `sources/provenance.json` | Pinned provider captures (URL, time, size, sha256) and every quoted line by number, with fetch, build and verify commands |
| `scenarios/*.json` | SYNTHETIC scripted businesses: the job's four sample scenarios plus four more |

## Commands

| Command | Does | Calls anyone |
| --- | --- | --- |
| `python3 call_for_me.py check --brief FILE` | validates the brief and prints the confirmed brief | no |
| `python3 call_for_me.py plan --brief FILE --start 2026-11-12T15:00:00Z` | prints the permitted call times | no |
| `python3 call_for_me.py simulate scenarios/*.json [--dialogue] [--json]` | runs scripted scenarios, prints each report, checks expectations and invariants, exits 1 on any failure | no, scripted line only |
| `python3 call_for_me.py call ...` | always refuses, exit 2 | no |
| `python3 call_sources.py fetch --out DIR` then `verify --captures DIR` | re-downloads the pinned provider files and re-checks every hash and quoted line | no (GitHub raw only) |

## Simulation scenarios

All scripts are SYNTHETIC: written by hand for the tests. The businesses, numbers and dialogue are invented, and the `.invalid` pages do not exist.

| Scenario | Job sample | Expected and asserted |
| --- | --- | --- |
| 01-standard-booking | Dinner for 4, Friday 7 to 8:30pm | booked 7:45 pm, name, party size and confirmation number match the call |
| 02-no-slots-alternatives | Haircut, Saturday morning only, no slots open | not available; both offered times reported with their exact words, none booked |
| 03-robot-question-continues | Business asks "is this a robot?" | answers yes and says who it calls for, call continues, booked |
| 04-card-to-hold | Business asks for a card to hold the table | declines, not booked, request and the conditional slot reported |
| 05-robot-question-declines | (extra) business will not deal with an AI | ends politely, not retried |
| 06-no-answer-retries | (extra) no answer, busy, voicemail | stops at 3 attempts, every attempt listed |
| 07-pre-approved-alternative | (extra) window full, pre-approved alternative offered | booked and flagged as using the alternative |
| 08-cancellation-fee | (extra) no-show fee asked | declines the fee; business books anyway; report notes the request |

Every scenario is also checked against invariants that do not depend on its expectations:
- attempts stay within the limit and inside opening and calling hours
- every answered call opens with the AI disclosure
- every AI question is answered yes
- no agent line denies being an AI, speaks a card-like number, agrees to a payment term, or shares a number the buyer did not approve
- a booked status always has a date, time and name inside the window or a pre-approved alternative
- no offered alternative is marked booked
- no business sentence is stored in the outcome

## Verification

```
python3 -m unittest discover -s tests          # 36 tests, 1 skipped unless CALL_FOR_ME_CAPTURES is set
python3 call_for_me.py simulate scenarios/*.json   # 8 PASS
python3 call_sources.py fetch --out DIR && python3 call_sources.py verify --captures DIR
CALL_FOR_ME_CAPTURES=DIR python3 -m unittest tests.test_call_flow.DocsAndSourcesTests
```

## Not verified at this stage

- No call, audio, speech recognition or speech synthesis was exercised. Understanding is a rule set written for the scripted scenarios.
- Provider price figures, speech quality, and whether a provider retains real-time transcription text are awaiting capture or a live trial. Both are owner decisions; see PROVIDERS.md.
- No listing was created. The draft below is text only.

## Listing draft

**Name:** Call-for-Me: Restaurant & Appointment Booking Agent

**Category:** Automation

**What it does.** Phones a restaurant or local business (salon, clinic, repair shop) to book a table or appointment inside your time window, then reports exactly what was confirmed: status, date, time, name, party size or service, any confirmation number, every call attempt, and any other times the business offered. It books by phone only and never through third-party booking platforms.

**What you provide.** The business name and its phone number as published by the business, or the name and city; the date and time window; the party size or the service; the name for the booking; any alternative windows you would also accept; optionally a callback number you are happy to share, and any special requests. Before any call, you get the brief back to confirm.

**Where and in which language.** Businesses in the United States only. Calls and reports are in English.

**Calling hours.** Calls are placed only during the business's opening hours and between 09:00 and 20:00 in the business's local time. The last call is at least 60 minutes before your window opens. Rules on automated calls differ by state, and the operator follows them where the agent operates.

**Retries.** If there is no answer, the line is busy, or voicemail picks up, it tries again at least 30 minutes later, up to 3 calls in total. If the business declines to talk to an AI, hangs up, or asks not to be called, that is reported as the outcome and it does not call again.

**What it will never do.** It never books outside your window or your listed alternatives. It never gives card details or agrees to a deposit, prepayment or cancellation fee, and it never asks you for payment details. It never records the call or keeps a transcript.

**FAQ**

- *Will the business know it is an AI?* Yes. It says so at the start of every call, and answers yes whenever asked, naming who it is calling for.
- *What if the only table is outside my window?* It does not book it. It asks whether anything inside your window exists. If not, it ends the call, and the report says "not available" and quotes the exact times offered so you can decide.
- *What if they want a card to hold the table?* It declines and tells you what was asked. If you want that booking, contact the business yourself.
- *What do I get back?* A report with the status (booked, not available, no answer, or not booked with the reason), the booking details, every attempt, and every alternative offered.
- *Who keeps the booking?* You do. The agent does not cancel or change bookings.
- *What is kept after the job?* Only the report's fields. There is no recording and no transcript.
