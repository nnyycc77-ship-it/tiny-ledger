# catering-finder: the Catering & Group Dining agent

Task: issue #75, prebuild wave for NEAR Agent Market job
f2a6a33d-1b85-4dad-978f-5322e63612d7 ("Catering & Group Dining Agent",
bid pending at 250 USDC). Built ahead of any award so an award can be
answered inside its promised window. One module, `catering_finder.py`,
standard library only; its tests live in `tests/` and are discovered by
the CI job through `tools/tests/test_catering_finder.py`.

Reconciled against the job description and the bid proposal as posted
verbatim by the coordinator on issue #75 (comments 6365588905 and
6365589501, read live from the market on 2026-10-23): the brief fields,
the three dietary states and the "not confirmed" wording (acceptance
criterion 3), availability separated into confirmed, declined and not
confirmed (criterion 4), non responders and decliners kept in the report
(criterion 5), prices, minimums and deposits printed only as stated with
no totals or estimates (criterion 2), the on behalf of a customer and
automated assistant disclosure in every draft, no booking and no buyer
contact details (criterion 6), and a stop request honoured. `market.near.ai`
itself is not reachable from the build container.

## What it does

Given an event brief, the agent reads each candidate vendor's published
page, keeps the vendors whose own page verifies the service style and the
area, extracts menus, capacity and pricing from what the page says,
drafts the vendor questions, and renders one comparison report.

| Command | Does | Sends anything |
| --- | --- | --- |
| `run --brief B --store S [--log L] [--out FILE]` | render the comparison report | no |
| `draft --brief B --store S --log L` | record a question draft for every compared vendor without one | no |
| `record-sent VENDOR --log L --when UTC` | record that the operator sent a draft through the published channel | no |
| `record-reply VENDOR --log L --when UTC --text "..."` | record the vendor's answer verbatim | no |
| `send VENDOR --log L [--hire-id ID] [--execute]` | refused: live sending needs a hire id and `--execute`, and no transport is part of this build | no |
| `capture URL --store S --id ID --name "..."` | fetch one live vendor page into a store with provenance (status, headers, sha256) | GET only |

Run from the repository root; the dry run on the fixture store:

```sh
python3 agents/catering-finder/catering_finder.py run \
  --brief agents/catering-finder/tests/fixtures/brief.json \
  --store agents/catering-finder/tests/fixtures \
  --log agents/catering-finder/tests/fixtures/outreach-log.json
```

### The brief

A JSON object with `date` (YYYY-MM-DD), `location` ("Austin, TX"),
`headcount` (positive integer), `budget_usd` (positive number),
`dietary_needs` (list of strings, may be empty) and `service_style`
(buffet, plated, family style, drop-off, private dining room, food truck,
boxed, or any phrase matched on its own wording), plus optional `time`
(HH:MM) and `response_deadline_utc` (the end of the collection window,
printed in the report). Anything missing or malformed stops the run. The
budget per head printed in the report is the brief's budget divided by
its headcount, the buyer's own number, and is labelled so.

### The store

A folder with `index.json` (the candidate list: `{"vendors": [{"id",
"name", "url"}]}` plus an optional `source` note), `vendors/<id>.html`
(each page as captured) and `provenance.json` (url, retrieval time, sha256
per page). The loader checks every page against its recorded sha256 and
refuses an edited page rather than quote it. `capture` builds a real store
one page at a time; the fixture store under `tests/fixtures` is SYNTHETIC
(see Fixtures).

### Evidence

Every extracted value is printed as a claim with its source link and the
raw page line directly beneath, verbatim, in the fixed format from
`AGENT-BRIEF.md`. A value the page does not state is reported as "not
published on the vendor page", never filled in. Prices are read with the
clause they sit in, so a page that prices buffet and plated service on
one line is not reported as one price; the summary uses only prices whose
clause names the brief's style, and a clause that says "from" or
"starting at" is marked a starting point. Lines stating a minimum, a
deposit or cancellation terms are quoted as shown. Nothing is totalled or
estimated: the only comparison made is the vendor's stated price per
person against the brief's budget per head, and an over budget vendor is
marked as such with both figures.

### Service style and area

A vendor is compared only when its own page states the service style and
names the brief's place. A line that mentions the style only to deny it
("No buffet or table service") is not a match. A page silent on the area
is listed under Checked and excluded as "not verified, not inferred": the
finder does not conclude the vendor is out of area, only that the page
does not say.

### Dietary rule

Coverage is never inferred from silence. For each need in the brief a
vendor row shows one of three states:

- **confirmed**: the vendor's own page says it covers the need (the line
  is quoted beneath the claim);
- **stated**: the vendor's recorded answer addresses the need (the answer
  is quoted, with the date it was received);
- **not confirmed**: neither, with the question's status: not yet
  drafted, drafted and not sent, asked on a date with no reply as of the
  run, or answered without addressing it.

Availability works the same way: a vendor is **confirmed** for the date
only when its recorded answer says so, **declined** when the answer says
it cannot, and **not confirmed** otherwise. The answer's own words decide
(`--available yes|no` on `record-reply` overrides an ambiguous reply),
and the answer is quoted in the report. A price per person stated in the
answer is quoted from it too.

### Outreach

`draft` writes one message per compared vendor into the outreach log.
Every draft says it is sent on behalf of a customer by an automated
assistant, invites the vendor to ask us to stop, asks for availability on
the date (and time, when given), menu suggestions for the service style,
the price per person and total and what it includes, any minimum spend,
deposit or cancellation terms, and the dietary needs from the brief that
the page did not confirm, in the brief's exact wording. It asks for a
quote only, carries no buyer contact details, and says the customer
decides on any booking. Drafts are recorded, never sent. Under a real
hire the operator sends each draft through the channel the vendor
publishes (the page line is quoted in the report) and records the send
and the reply (`record-reply --stop` records a vendor who asked not to be
contacted again; no further draft is made for them). Those records drive
the "stated", "asked, no reply", "declined" and "contacted with no reply"
rows. If a vendor asks whether they are talking to an AI, the operator
answers yes. The `send` command exists so that the gate is explicit: it
refuses without a hire id (`--hire-id` or `CATERING_FINDER_HIRE_ID`) and
`--execute`, and with both it still refuses because no live transport is
part of this build. The agent never books, accepts a quote or pays a
deposit.

### The report

One Markdown file: the brief, run time and collection window; a summary
table (style, area, capacity against headcount, price per person as
stated, against budget per head, availability for the date, one column
per dietary need, outreach status); a counts line (compared, with
capacity for the headcount, contacted, replied, confirmed, declined,
stopped) so thin coverage is stated rather than padded; availability
lists; one section per compared vendor with every claim and excerpt,
the terms lines, and the quoted answer; Contacted with no reply;
Declined; Checked and excluded with the reason; the recorded drafts;
Sources.

## Fixtures

Everything under `tests/fixtures` is SYNTHETIC: six vendor pages, the
candidate index, the brief and the outreach log were written by hand for
the tests because no vendor host is reachable from the build container
(every probed host answered a gateway CONNECT 403; the probe is recorded
on issue #75, and the coordinator's ruling there allows labelled
synthetic pages for the offline tests). The pages carry the label in
their first line and `provenance.json` repeats it with a sha256 per
file. No business, price, message or reply in them is real; the
`.invalid` hostnames cannot resolve. The fixtures exercise: a buffet
vendor in area with vegan and gluten-free on the page, a nut-free answer
recorded and availability confirmed (confirmed and stated); a vendor
contacted with no reply (not confirmed, asked); a vendor with a draft not
sent and no published price or capacity; a vendor with minimum, deposit
and cancellation lines whose answer declines the date; a food truck
whose page denies buffet service (excluded, style); a buffet vendor whose
page names another metro only (excluded, area not verified).

To replace them with real captures, run `capture` against live vendor
pages into a new store folder; the loader and the report work unchanged.

## Listing draft (category: Events, per the job description)

**Name:** Catering & Group Dining Finder

**What it does:** give it your event (date and time, place, headcount,
budget, dietary needs, service style) and it compares caterers and
restaurants from their own published pages and their own answers:
service style and area verified, menus, capacity, prices, minimums,
deposits and cancellation terms quoted with the source, availability for
your date marked confirmed, declined or not confirmed, and each dietary
need marked confirmed by the vendor's page, stated by the vendor's
answer, or not confirmed with the question asked and dated. You get one
side by side comparison, including the vendors who did not reply or
declined, plus the vendor questions ready to send.

**What buyers provide:** the brief (date and time, location, headcount,
budget, dietary needs in your own words, service style) and either a
list of vendor pages to compare or a request to find candidates in the
area. Your contact details are never shared with vendors unless you
approve it.

**Locations covered:** any area where vendors publish a page with their
service style, area and contact channel; the buyer names the place.

**Collection window:** three days from the first message by default (a
different window can be set in the brief); the comparison is delivered
at the end of the window even if some vendors have not replied, with
those vendors listed as contacted with no reply.

**FAQ**

- *Does it contact vendors?* It drafts the questions. Under a hire the
  drafts are sent through each vendor's published channel, every message
  says it is on behalf of a customer and sent by an automated assistant,
  and the answers are recorded and quoted; nothing is sent in a dry run.
- *Does it book or pay anything?* No. It collects quotes only; the buyer
  decides on any booking, deposit or tasting.
- *What if a vendor's page does not mention my dietary need?* The row
  reads not confirmed, with the question drafted or asked and dated. A
  silent page is never counted as coverage.
- *What if a vendor does not publish prices?* The report says so; no
  figure is invented, and prices are shown as stated, with "starting
  point" where the vendor says so. Final totals depend on menu choices,
  taxes and service charges.
- *Where do the numbers come from?* Every figure is quoted with its
  source link and the raw line from the vendor's page or answer beneath
  it.

## Verification

```sh
python3 -m unittest discover -s agents/catering-finder/tests -v
python3 -m unittest discover -s tools/tests -v        # includes the loader
python3 tools/pregate.py                              # secrets, honesty, provenance
```

Not verified from this folder: any live vendor page capture or discovery
run (no vendor host is reachable from the build container), and the live
`send` path (no transport exists in this build by design).
