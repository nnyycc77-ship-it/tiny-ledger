# catering-finder: the Catering & Group Dining agent

Task: issue #75, prebuild wave for NEAR Agent Market job
f2a6a33d-1b85-4dad-978f-5322e63612d7 ("Catering & Group Dining Agent",
bid pending at 250 USDC). Built ahead of any award so an award can be
answered inside its promised window. One module, `catering_finder.py`,
standard library only; its tests live in `tests/` and are discovered by
the CI job through `tools/tests/test_catering_finder.py`.

Marked **to confirm against the job description**: the brief field names,
the three dietary states and the report shape below were chosen from the
task text of issue #75. The job description and the bid proposal were not
in the repo when this was built and `market.near.ai` is not reachable
from the build container; they were requested on the issue and the build
is reconciled against them when they are posted.

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
(buffet, plated, family style, drop-off, food truck, boxed, or any phrase
matched on its own wording). Anything missing or malformed stops the run.

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
clause names the brief's style. The per event estimate is arithmetic on a
quoted figure and says so.

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
- **unconfirmed**: neither, with the question's status: not yet drafted,
  drafted and not sent, asked on a date with no reply as of the run, or
  answered without addressing it.

### Outreach

`draft` writes one message per compared vendor into the outreach log:
availability on the date, menu suggestions for the service style, price
per person and what it includes, and the dietary needs from the brief
that the page did not confirm, in the brief's exact wording. Drafts are
recorded, never sent. Under a real hire the operator sends each draft
through the channel the vendor publishes (the page line is quoted in the
report) and records the send and the reply; those records drive the
"stated", "asked, no reply" and "contacted with no reply" rows. The
`send` command exists so that the gate is explicit: it refuses without a
hire id (`--hire-id` or `CATERING_FINDER_HIRE_ID`) and `--execute`, and
with both it still refuses because no live transport is part of this
build.

### The report

One Markdown file: the brief and run time; a summary table (style, area,
capacity against headcount, price per person, estimate against budget,
one column per dietary need, outreach status); one section per compared
vendor with every claim and excerpt; Contacted with no reply; Checked and
excluded with the reason; the recorded drafts; Sources.

## Fixtures

Everything under `tests/fixtures` is SYNTHETIC: five vendor pages, the
candidate index, the brief and the outreach log were written by hand for
the tests because no vendor host is reachable from the build container
(every probed host answered a gateway CONNECT 403; the probe is recorded
on issue #75). The pages carry the label in their first line and
`provenance.json` repeats it with a sha256 per file. No business, price,
message or reply in them is real; the `.invalid` hostnames cannot
resolve. The fixtures exercise: a buffet vendor in area with vegan and
gluten-free on the page and a nut-free answer recorded (confirmed and
stated); a vendor contacted with no reply (unconfirmed, asked); a vendor
with a draft not sent and no published price or capacity; a food truck
whose page denies buffet service (excluded, style); a buffet vendor whose
page names another metro only (excluded, area not verified).

To replace them with real captures, run `capture` against live vendor
pages into a new store folder; the loader and the report work unchanged.

## Listing draft (to confirm against the job description)

**Name:** Catering & Group Dining Finder

**What it does:** give it your event (date, place, headcount, budget,
dietary needs, service style) and it compares caterers from their own
published pages: service style and area verified, menus, capacity and
prices quoted with the source line, dietary coverage marked confirmed by
the vendor's page, stated by the vendor's answer, or unconfirmed with the
question drafted. You get one comparison report plus ready to send vendor
questions.

**What buyers provide:** the brief as six fields, and either a list of
vendor page URLs to compare or a request to discover candidates in the
area. Dietary needs in your own words; they are asked of every vendor
verbatim.

**FAQ**

- *Does it contact vendors?* It drafts the questions. Under a hire the
  drafts are sent through the vendor's published channel and the answers
  are recorded; nothing is sent in a dry run.
- *What if a vendor's page does not mention my dietary need?* The row
  reads unconfirmed, with the question drafted or asked and dated. A
  silent page is never counted as coverage.
- *What if a vendor does not publish prices?* The report says so and the
  estimate column stays empty for that vendor; no figure is invented.
- *Where do the numbers come from?* Every figure is quoted with its
  source link and the raw line from the vendor's page beneath it.

## Verification

```sh
python3 -m unittest discover -s agents/catering-finder/tests -v
python3 -m unittest discover -s tools/tests -v        # includes the loader
python3 tools/pregate.py                              # secrets, honesty, provenance
```

Not verified from this folder: any live vendor page capture or discovery
run (no vendor host is reachable from the build container), and the live
`send` path (no transport exists in this build by design).
