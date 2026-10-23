# Field Service Route Planner & Schedule Backfill (agent build, issue #73)

Built ahead of any award for the NEAR Agent Market job "Field Service Route
Planner & Schedule Backfill" (job `5b3baff9-bb38-4a0f-9c52-89cf54af95b6`),
so that an award can be answered inside its promised window and the agent
is a portfolio asset either way. Nothing in this folder lists, bids,
submits or contacts anyone; it plans one day from three CSV files and
writes one Markdown report.

Standard library only: `planner.py` (the agent), `routing.py` (geocoding
and drive times behind one interface), `tests/` (offline, synthetic
fixtures). No key, token, wallet or buyer data exists in this folder.

**Spec.** The job description is quoted verbatim by the coordinator on
issue #73 (comment 6365291384; 8847 characters, SHA-256
`0f588e9fef17a40b36f450b4884b6979146e6a5ee424f39fe5cc7a14dfc95b99`,
checked against the comment body by this build). Its acceptance criteria
are mapped to the report in "How the acceptance criteria are met" below.
The description leaves the spreadsheet columns to the listing ("The
listing shows the expected columns"), so the column names, formats and
defaults below are this build's choice, stated in the listing draft. The
bid proposal's text was requested on the issue and is not in this
repository; item 4 of issue #73 is the record of its backfill rules used
here.

## What the buyer provides

Three CSV files with a header row (UTF-8; a BOM is tolerated). Column names
are exact; column order does not matter; extra columns are ignored.

### `jobs.csv`, one row per job booked for the planning day

| Column | Format | Notes |
| --- | --- | --- |
| `job_id` | text | unique in the file |
| `customer` | text | matched (name plus address) against the customer list to skip already booked customers |
| `address` | text | sent to the geocoder as written |
| `duration_minutes` | positive integer | on site time |
| `window_start`, `window_end` | `HH:MM`, 24 hour | the job may start anywhere in the window |
| `skills` | `a;b;c` | every listed skill must be held by the crew member |
| `date` | `YYYY-MM-DD`, optional | required when the run covers more than one day (`--date-to`); a row outside the period, or blank when the column exists, is dropped and listed |

### `crew.csv`, one row per crew member working that day

| Column | Format | Notes |
| --- | --- | --- |
| `crew_id` | text | unique |
| `name` | text | used in the report and the drafts |
| `start_address` | text | where the day starts |
| `shift_start`, `shift_end` | `HH:MM` | working hours; the last job must end by `shift_end`; the return drive is not required inside the shift and is not counted |
| `skills` | `a;b;c` | |

### `customers.csv`, the service plan list used for backfill

| Column | Format | Notes |
| --- | --- | --- |
| `customer_id` | text | unique |
| `name` | text | |
| `address` | text | |
| `last_service_date` | `YYYY-MM-DD` or blank | blank means the due date rests on the plan interval (assumption based) |
| `service_plan` | `weekly`, `biweekly`, `monthly`, `bimonthly`, `quarterly`, `semiannual`, `annual`, `yearly`, or `every N days` | the interval between visits |
| `do_not_contact` | `yes` / `no` (also `true`/`false`, `1`/`0`; blank is no) | a `yes` is a hard exclusion |
| `open_quote` | text, optional | a non blank value means the customer is due now (an open quote), with the text carried into the reason and the draft |

A row with an unusable field is dropped from planning and listed under
"Data problems" in the report with its row number and the field. A file
with a missing column, a missing file, or a provider failure stops the run
(exit 2, reason on stderr, nothing written).

## Run

From the repository root, offline on the synthetic fixtures:

```sh
python3 agents/field-service-planner/planner.py plan --date 2026-11-03 \
  --jobs agents/field-service-planner/tests/fixtures/jobs.csv \
  --crew agents/field-service-planner/tests/fixtures/crew.csv \
  --customers agents/field-service-planner/tests/fixtures/customers.csv \
  --places agents/field-service-planner/tests/fixtures/places.json \
  --out /tmp/plan.report.md
```

`--places FILE` is the offline fixture provider (places and a drive time
rule from a JSON file, no network). `--live` uses the open routing services
instead and needs `FIELD_PLANNER_CONTACT` in the environment (the
operator's contact for the User-Agent, which the Nominatim usage policy
requires); without it the run refuses before any request. Settings:
`--date-to` extends the period to a range of days (at most 31; the jobs
file then needs the `date` column). Settings: `--min-gap-minutes` (default
30), `--visit-minutes` (assumed backfill visit, default 60),
`--lookahead-days` (default 0: only customers due on or before the last
day are suggested; a larger value also admits customers due within that
many days, and every such suggestion is marked not yet due),
`--suggestions-per-gap` (default 3). Every setting is printed in the
report.

## What the report contains

1. **Brief and inputs**: the period, the three files with row counts and
   SHA-256 digests, the crew with hours and skills, the provider used and
   the UTC time of geocoding, the settings.
2. **Data problems**: dropped rows and every address the geocoder did not
   place. An unplaced address is never guessed: the job is not scheduled,
   the crew member gets no route, the customer is not suggested.
3. Per day:
   - **Schedule per crew member**: start, stops in order with drive,
     arrival, start, end and window, total drive time; then the total over
     all crew against the drive time of visiting the same jobs in the order
     the file gave them, with the difference or the reason it is not lower.
   - **Unassigned jobs**, each with the reason (unplaced address, no crew
     member with the skills, no feasible slot).
   - **Gaps**: idle stretches of at least the minimum, with the crew
     member, the time and the area (where they are before and after).
   - **Ranked backfill suggestions** per gap, each with its reason (due
     date arithmetic or open quote, added drive time, the check that the
     next job's planned start still holds, address confidence) and a
     certainty label (`high`, `medium`, `low`); assumption based and not
     yet due suggestions are marked.
4. **Checked and excluded customers** with the exclusion reason.
5. **Outreach drafts**, one per suggestion, marked drafts only. The agent
   sends nothing; the buyer decides. Do not contact customers never appear.
6. **Method**: the heuristic, the exclusion order, the ranking formula.

### How the acceptance criteria are met

| Job description criterion | Where |
| --- | --- |
| 1. Every job assigned or listed as unassigned with the reason | schedule tables plus "Unassigned jobs" per day; the tests assert the two sets cover every job row |
| 2. No work outside hours, windows or skills | the insertion only accepts feasible timelines; asserted stop by stop in the tests |
| 3. Drive times from a routing service, named | "Brief and inputs" names the provider and the time of geocoding; offline runs name the fixture file |
| 4. Total drive time lower than the given order, or explained | the total line per day compares with the file order and explains when not lower |
| 5. Every gap of at least the minimum, with crew, time and area | "Gaps" per day; the minimum is `--min-gap-minutes`, default 30 |
| 6. A suggested customer keeps every later job on time | a suggestion is made only when drive, visit and the drive on fit before the next job's planned start; the reason says so |
| 7. Every suggested customer is due, and the report says why | default lookahead 0; the reason gives the due arithmetic or the open quote |
| 8. No do not contact customer in suggestions | hard exclusion before ranking; listed under excluded with that reason |
| 9. A draft per suggestion, nothing sent | "Outreach drafts"; the agent has no sending code at all |

Sample scenarios from the description: the unassignable job and the do
not contact customer near a gap are in the fixtures; the one week plan
with light days is `tests/fixtures/jobs-week.csv` run with `--date-to`.

### The rules, as built

- Sequencing: cheapest feasible insertion. Jobs are taken in order of
  window end; each goes to the eligible crew member and position that adds
  the least drive time while every window and shift stays feasible. Greedy,
  so feasible rather than proven optimal; a solver can replace the
  `Planner.sequence` method without changing the report.
- Dedupe: customers are keyed on normalized name plus address (lower case,
  punctuation removed, whitespace collapsed); later duplicates are excluded
  and name the kept row.
- Hard exclusions, in order, before ranking: duplicate; do not contact;
  address not placed; already has a job in the period (name plus address
  match against `jobs.csv`); not due (within the lookahead window when one
  is set).
- Due: last service date plus the plan interval is on or before the day,
  or an open quote is on record. Due strength: (day minus next due date)
  divided by the interval. No last service date and no quote: treated as
  one full interval elapsed, labelled assumption based, certainty `low`.
- Ranking: `due_strength - added_drive_hours * 0.5 + confidence bonus`
  (high 0.2, medium 0.1, low 0), scored for every gap in the period the
  customer fits with the assumed visit; the pairs are taken best first
  (ties by less added drive time, then customer id, then the earlier gap),
  each customer once in the whole period and at most the configured number
  per gap, so light days with nearby due customers get filled.
- Fit: the drive to the customer, the visit and the drive on to the next
  job must fit before that job's planned start (or the shift end), so no
  later job moves.
- Certainty: `high` with a recorded last service date and a high confidence
  placement; `medium` with a recorded date and medium or low placement;
  `low` when assumption based.

## Geocoding and drive times (`routing.py`)

One interface, two methods: `geocode(address) -> Place or None` and
`matrix(places) -> seconds table`. `FixtureProvider` reads a JSON file and
makes no request. `LiveProvider` uses Nominatim (`/search`, `format=jsonv2`,
`limit=1`, one request per second, the operator contact in the User-Agent)
for geocoding and the public OSRM demo table service
(`/table/v1/driving/{lon,lat;...}?annotations=duration`) for drive times,
HTTPS only, hosts pinned, redirects refused; a non 2xx status, a non JSON
body, an unexpected shape or a pair with no route stops the run. A keyed
provider replaces `LiveProvider` by implementing the two methods.

**To confirm before a live run:** the two request shapes above were
written from the public documentation of those services as known when this
was built, not from a call made here (both hosts are refused from the build
environment, probe recorded on issue #73). The live provider returns
placement confidence `medium` for every result because a single best match
is unverified; a keyed provider can report `high`.

## Where this sits in the NEAR worker loop

The marketplace side is `near-agent/worker.py` (issue #48): `poll` shows
assignments, `start`, `message` and `submit` are dry runs until
`--execute`. On an award the operator runs this planner on the buyer's
three files and submits the report text through `worker.py submit` after
reading the dry run. This folder itself never talks to the marketplace.

## Listing draft (for the owner, at award; not created by this task)

**Name:** Field Service Route Planner & Schedule Backfill

**What it does:** Give it your day's jobs, your crew and your customer
list as three spreadsheets. You get back a route per technician that
respects working hours, time windows and skills, the drive time it costs,
the gaps left in the day, and a ranked list of service plan customers who
could fill each gap, each with the reason, a confidence label and a
message draft you can send or not. Nothing is sent by the agent.

**What you provide:** `jobs.csv`, `crew.csv`, `customers.csv` in the
formats above, and the date.

**FAQ**

- *Does the agent contact my customers?* No. It writes drafts; you decide.
- *What about customers who asked not to be contacted?* A `yes` in
  `do_not_contact` removes them before anything is ranked; they appear only
  in the excluded list with that reason.
- *What if an address cannot be found?* It is reported as a data problem
  and left out. The agent never guesses a location.
- *What if a customer has no last service date?* They can still be
  suggested, marked assumption based with low certainty, using the plan
  interval alone.
- *Is the route optimal?* It is feasible and built to add the least drive
  time at each step; it is not a proven optimum. The method is printed in
  every report, with the drive time of the given order for comparison.
- *How long must a gap be to count?* 30 minutes by default; set
  `--min-gap-minutes` to your own minimum.
- *Can it plan a week?* Yes: give the jobs a `date` column and run with
  `--date-to`. Each customer is suggested once across the period.
- *Which maps does it use?* Open services (Nominatim, OSRM) by default; a
  commercial provider can be swapped in.

## Verification

```sh
python3 -m unittest discover -s agents/field-service-planner/tests -v
python3 -m unittest discover -s tools/tests -v      # includes this suite through tools/tests/test_field_service_planner.py
```

The tests make no network request (the live transport is patched to fail
if touched). The fixtures under `tests/fixtures/` are SYNTHETIC sample
data, labelled in `tests/fixtures/provenance.json` and in the places file
itself; no buyer, geocoder or routing data was used.

## Sources

- Task text: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/73>
  (the column summaries, the rules that bind the build, the acceptance).
- Job description, quoted verbatim by the coordinator from the NEAR Agent
  Market board on 2026-10-23:
  <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/73#issuecomment-6365291384>
  (8847 characters, SHA-256
  `0f588e9fef17a40b36f450b4884b6979146e6a5ee424f39fe5cc7a14dfc95b99`).
- Marketplace loop: `near-agent/README.md` and its sources on issue #48.
- The bid proposal text: requested on issue #73; not in this repository.
