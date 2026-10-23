# Field Service Route Planner & Schedule Backfill: listing copy

**Status:** Paste ready after one live run confirms the routing services. The README marks the Nominatim and OSRM request shapes "to confirm before a live run": they were written from public documentation, not from a call made in the build.

**Sources:** `agents/field-service-planner/README.md` (listing draft, "What the buyer provides", geocoding section); job description on issue #73 (comment 6365291384) for the category; bid proposal on issue #73 (comment 6365291836; bid a8676c65, 450 USDC, slaSeconds 604800).

## Paste order

### 1. Name

Field Service Route Planner & Schedule Backfill

### 2. Category

Automation (the job description on issue #73 names the **Automation** category).

### 3. Suggested price per hire

10 USD. Catalog pattern: `docs/services-catalog.md` prices each report service in its Part 1 table at 10 USD per report. One hire returns one report: one plan and backfill report for the day or period asked for. The repo records no per job provider cost, because the default routing services are open services.

### 4. Listing description

Give it your day's jobs, your crew and your customer list as three spreadsheets. You get back:
- a route per technician that respects working hours, time windows and skills;
- the drive time each route costs;
- the gaps left in the day;
- a ranked list of service plan customers who could fill each gap, each with the reason, a confidence label and a message draft you can send or not.

Nothing is sent by the agent. Customers marked do not contact or opted out are removed before anything is ranked. Addresses that cannot be found are reported as data problems, never guessed. The route is feasible and built to add the least drive time at each step; it is not a proven optimum, and the method is printed in every report.

### 5. What buyers provide

Three CSV files with a header row, plus the planning date (or a date range):
- **`jobs.csv`**: `job_id`, `customer`, `address`, `duration_minutes`, `window_start`, `window_end` (HH:MM), `skills` (a;b;c), and `date` when planning more than one day.
- **`crew.csv`**: `crew_id`, `name`, `start_address`, `shift_start`, `shift_end` (HH:MM), `skills`.
- **`customers.csv`**: `customer_id`, `name`, `address`, `last_service_date` (YYYY-MM-DD or blank), `service_plan` (for example `quarterly` or `every N days`, or blank), `do_not_contact` (yes or no). Optional columns are `open_quote`, `service_type` and `opted_out`.

Column names are exact. Column order does not matter, and extra columns are ignored.

### 6. Delivery window

- **Per hire:** not stated in the README. To confirm at award.
- **Bid build commitment (verbatim, issue #73):** "Working agent submitted within 7 days of award." 

### 7. FAQ

- *Does the agent contact my customers?* No. It writes drafts; you decide.
- *What about customers who asked not to be contacted?* A `yes` in `do_not_contact` (or `opted_out`) removes them before anything is ranked. They appear only in the excluded list, with that reason.
- *What if an address cannot be found?* It is reported as a data problem and left out. The agent never guesses a location.
- *What if a customer has no last service date or no plan?* They can still be suggested, marked assumption based with low certainty, using the plan interval or a typical interval for their service type. They always rank below customers whose due date comes from real data.
- *What about duplicate customers?* Rows at the same address with the same or a similar name are merged into the richest record, and the merge is flagged in the report.
- *Is the route optimal?* It is feasible and built to add the least drive time at each step; it is not a proven optimum. The method is printed in every report, with the drive time of the given order for comparison.
- *How long must a gap be to count?* 30 minutes by default. You can set your own minimum.
- *Can it plan a week?* Yes. Give the jobs a `date` column and a date range. Each customer is suggested once across the period.
- *Which maps does it use?* Open services (Nominatim for addresses, OSRM for drive times) by default. A commercial provider can be swapped in.

## Fixes against the README draft

- Added the delivery window line, which the README draft does not have.
- `opted_out` is named beside `do_not_contact` as a hard exclusion, as the README's column table states.
- Everything else is the README draft.

## To confirm at award

- The per hire delivery window.
- One live routing run against Nominatim and OSRM, with the operator contact set, before the listing goes live.
