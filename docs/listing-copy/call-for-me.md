# Call-for-Me: Restaurant & Appointment Booking Agent: listing copy

**Status:** **Design stage, not listable.** The merged build (PR #92) is design and simulation only. It places no calls, has no telephony provider, account or number, and its `call` command always refuses. The live stage is blocked until it is confirmed that the voice provider keeps no real-time transcription text (`agents/call-for-me/DESIGN.md` section 9). The copy below is the target listing for after that stage, kept here so it is ready.

**Sources:** `agents/call-for-me/README.md` (listing draft), `agents/call-for-me/DESIGN.md` (retry and calling hours values); job description on issue #79 (comment 6366189256) for the category and the listing's required parts; bid proposal on issue #79 (comment 6366189929; bid 0a591280, 400 USDC).

## Paste order

### 1. Name

Call-for-Me: Restaurant & Appointment Booking Agent

### 2. Category

Automation (the job description on issue #79 names the **Automation** category).

### 3. Suggested price per hire

Set at award. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. That pattern is for sourced reports with no per job provider cost. Each hire here places paid calls, and provider price figures are "awaiting capture" in `agents/call-for-me/PROVIDERS.md`.

### 4. Listing description

Phones a restaurant or local business (salon, clinic, repair shop) to book a table or appointment inside your time window. It then reports exactly what was confirmed:
- the status, and the date, time, name, and party size or service;
- any confirmation number;
- every call attempt;
- any other times the business offered.

It books by phone only and never through third-party booking platforms. It says it is an AI at the start of every call, and answers yes whenever asked, naming who it is calling for.

It never books outside your window or your listed alternatives. It never gives card details or agrees to a deposit, prepayment or cancellation fee, and it never asks you for payment details. It never records the call or keeps a transcript.

### 5. What buyers provide

- The business name, and its phone number as published by the business, or its name and city.
- The date and time window, and the party size or the service.
- The name for the booking.
- Any alternative windows you would also accept.
- Optionally, a callback number you are happy to share, and any special requests.

Before any call, you get the brief back to confirm. Businesses in the United States only. Calls and reports are in English.

### 6. Delivery window

- **Per hire:** calls happen only during the business's opening hours, between 09:00 and 20:00 in the business's local time. The last call is at least 60 minutes before your window opens. If there is no answer, the line is busy, or voicemail picks up, it tries again at least 30 minutes later, up to 3 calls in total. The report follows the last attempt.
- **Bid build commitment (verbatim, issue #79):** "Working agent submitted within 7 days of award." 

### 7. FAQ

- *Will the business know it is an AI?* Yes. It says so at the start of every call, and answers yes whenever asked, naming who it is calling for.
- *What if the only table is outside my window?* It does not book it. It asks whether anything inside your window exists. If not, it ends the call, and the report says "not available" and quotes the exact times offered so you can decide.
- *What if they want a card to hold the table?* It declines and tells you what was asked. If you want that booking, contact the business yourself.
- *What do I get back?* A report with the status (booked, not available, no answer, or not booked with the reason), the booking details, every attempt, and every alternative offered.
- *Who keeps the booking?* You do. The agent does not cancel or change bookings.
- *What is kept after the job?* Only the report's fields. There is no recording and no transcript.
- *Where are the rules on automated calls?* They differ by state, and the operator follows them where the agent operates.

## Fixes against the README draft

- None to the wording. The README draft was written for this stage and is used as is, with the status block added.
- The retry and calling hours values are the `POLICY` values in `call_for_me.py`, as `DESIGN.md` section 7 lists them; they are owner decisions at award.

## To confirm at award

- Everything in `agents/call-for-me/DESIGN.md` section 13: provider, number and account; the transcript retention answer; the final retry, hours and region values; the legal review of automated-call rules; webhook hosting; and the live understanding layer.
- The price, from the chosen provider's call rates.
