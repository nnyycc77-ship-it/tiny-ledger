# Backlog

The work that would most improve this operation, in value order.
Read `AGENT-BRIEF.md` first; its hard rules govern every task here.
Each workstream lists its tasks and the acceptance bar a reviewer
will check before the work is used.

## A. Delivery tooling

**Why first:** every paid delivery is currently built by hand.
Small fetchers that pull a source and emit a correctly formatted
report section would cut delivery time and, more than that, cut the
revision rounds that slow payment.

Build one small command line fetcher per source, in a `tools/`
folder, one file or one small package per source:

1. CPSC SaferProducts API — product recall checks.
2. NHTSA recalls API — vehicle and equipment recalls.
3. FMCSA SAFER and FMCSA Licensing and Insurance — carrier vetting.
4. CourtListener RECAP search — federal litigation screens.
5. USAspending API — federal contract award briefs.
6. IRS Form 990 data — nonprofit diligence files.

Each fetcher takes simple inputs (product names, carrier names or
USDOT numbers, company names, NAICS codes, NPIs, nonprofit names)
and emits one Markdown section in the delivery format from
`AGENT-BRIEF.md`: the claim lines, the source link, and the raw
excerpt from the source printed directly beneath the link, verbatim.
Where a source needs a free public demo key, the fetcher reads it
from the environment and says so in its header comment; no key is
ever stored in the repo.

**Acceptance:**

* Runs against the live public source, not a fixture or a mock.
* Output matches the delivery format exactly, including the raw
  excerpt directly beneath each source link.
* An empty result prints the full raw response, the exact query
  used, and the retrieval timestamp in UTC.
* A checked and excluded near match is listed with the reason, the
  way the published deliveries in `deliveries/` do it.

## B. Pay per call recall API

**Why:** the recall check is the proven service. Sold per call
through an agent payment registry, it can earn without a bidding
round, at a small price per call in USDC.

Build a small HTTP service in an `api/` folder, framework light and
deployable to a free serverless host:

* One endpoint that takes a product name (and a vehicle form where
  the source split needs it) and returns a sourced recall check in
  the same delivery format as workstream A.
* Configuration reads a payout wallet address from the environment.
  No keys or secrets appear in code, and the service runs locally
  with no environment set beyond that one optional value.
* A README inside the `api/` folder explains deployment in ten
  lines or fewer.

**Acceptance:**

* A local run answers a sample product query with sourced output in
  the delivery format, excerpts and timestamps included.
* Nothing secret in the folder, verified by reading it, not by
  assumption.
* The deployment README is ten lines or fewer and names the one
  environment value.

**Pricing completion note (adopted 2026-10-24):** the nine
priority routes (`/carrier`, `/litigation`, `/awards`, `/nonprofit`,
`/formd`, `/pagespeed`, `/domain`, `/app`, `/vin`) are part of the
pricing work already claimed under issue #147 at the ruled
0.25 USDC per call. Issue #147 is the home of this work; this note
records it and creates no duplicate pricing task. Pricing
completion is judged under #147: every tool the hosted server
exposes is priced at 0.25; tools built in the repo but not yet
hosted are wired into the server or explicitly listed as not yet
hosted; no price other than 0.25 appears.

**Payment gate extension.** `api/README.md` records that the x402
payment gate wraps `GET /recall` only; the other routes are served
without payment. Extend the gate to the whole API.

**Acceptance:**

* The gate wraps every route in the `api/README.md` table with the
  same 402 shape as `/recall`.
* Offline tests cover a paid, unpaid, and malformed payment call on
  at least three non recall routes.
* `api/README.md` is updated in the same PR to state the new
  coverage.
* No price is set by the follow on build task; prices live in the
  deployment configuration the owner controls.

## C. AgentTab support

**Why:** AgentTab is being submitted for a grant with a Nov 1, 2026
deadline, and judges verify claims by reading this repo.

Tasks:

1. Keep `app/proof.html` accurate against the contract ABI. The
   proof page reads live contract events and lists tabs, amounts
   settled, and explorer links; every event name, field, and figure
   it shows must match `contracts/AgentTab.sol`. If the page is
   missing, build it to that description.
2. Write a walkthrough storyboard at `docs/walkthrough-storyboard.md`:
   the shot by shot plan for a 60 to 90 second walkthrough video of
   a tab being opened, released, and claimed after a grace window,
   with the narration line for each shot.
3. Verify every claim in `README.md` against the contract and the
   test suite, and fix any claim the code does not back.

**Acceptance:**

* `forge test` still passes in full (26 tests).
* No claim in any doc or page that the code does not back, checked
  claim by claim, not skimmed.
* The storyboard covers release, refund inside the grace window,
  and claim after it, because those three paths are the product.

## D. Templates

**Why:** the format rules and the revision lessons currently live
in the reviewer its head. Written down once, every future delivery
starts right.

Create a `templates/` folder with:

1. A delivery checklist encoding the format rules from
   `AGENT-BRIEF.md` and the lessons paid for in revision rounds:
   empty results proven with the full raw response; excerpts
   verbatim, never reformatted or reordered; each excerpt printed
   directly under its own source link; every query and retrieval
   time recorded; near matches listed as checked and excluded with
   reasons.
2. A report skeleton: title, scope and inputs, per subject sections
   in the delivery format, a checked and excluded section, and a
   sources list.
3. One filled example, built from one of the real published
   deliveries in `deliveries/`, showing the checklist applied.

**Acceptance:**

* The filled example matches its source delivery in `deliveries/`
  figure for figure.
* A new delivery could be produced from the skeleton and the
  checklist alone, with no other instructions.

## E. Sourcing

**Why:** building capacity only pays when there is paid work in
front of it. Sourcing keeps the pipeline full: new places to sell,
the buyers who already pay for this kind of work, prices checked
against the market, and a calendar of programs worth entering
before their deadlines arrive.

**Rules for all sourcing work:** research and drafting only. No
outreach is sent, no accounts are created, and no messages are
posted anywhere. Every claim carries its source link. A lead is a
lead until the coordinating agent verifies it on the platform
itself; search snippets alone are never evidence.

### E1. Board scouting

Continuously look for new agent paying boards, job marketplaces,
grant and hackathon programs, and paid API registries that pass
the program filters: payout arrives in a crypto wallet with no
KYC; the work is something an agent can fully and honestly produce
from public sources; no promotional posting, no vendor signups,
and no faked human activity.

File each lead as a GitHub issue in this repo with:

* Platform name and link.
* Evidence it is live: a dated page or a terms link, opened and
  read.
* The payout method and any KYC mention, quoted from the platform
  itself.
* What fitting work exists there now.
* An estimated owner effort in minutes.

**Acceptance:**

* The platform page or terms were opened and read, and the
  evidence is dated.
* The payout and KYC wording is quoted from the platform, not
  paraphrased from a search snippet.
* Fitting work that exists now is named concretely.
* Owner effort is estimated in minutes.

### E2. Buyer segment research

For each of the six services in `AGENT-BRIEF.md`, find the buyer
segments who already pay for this work outside agent boards.
Segments to test, not assume: ecommerce sellers needing recall
and compliance checks; trucking and logistics firms needing
carrier vetting; law and diligence firms needing litigation
screens; real estate and deal sourcers using SEC Form D and
contract award data; nonprofits and donors using Form 990
diligence.

File one issue per segment. Each segment note names where those
buyers congregate or buy today, the going price for the human done
version of the work with a source, and what a listing or offer in
that venue would look like.

**Acceptance:**

* The segment is tied to one named service.
* Where the buyers are is named concretely (a venue, a
  marketplace, a community), with a source.
* The going price for the human done version is stated with a
  dated source.
* The shape of an offer in that venue is sketched. No outreach
  is sent.

**Segment queue (adopted 2026-10-24):** the segments run in this
order. First, sanctions and exclusion screening (OFAC, OIG, CSL),
filed as its own issue. Second, freight broker carrier monitoring,
filed as its own issue. Third, grantmaker diligence: nonprofit
diligence buyers (grantmakers), resting on `tools/nonprofit_pack.py`
and `tools/propublica_nonprofits.py`. The third segment is queued
here only; no E2 issue for it is filed until its turn comes.

### E3. Pricing and competitor scans

Once a month, scan what comparable research and verification
services charge on freelance platforms and agent boards, and file
the scan as an issue with dated sources. The scan ends with a
recommended price for the 10 USD catalog rate: hold, raise, or
lower, with the evidence behind the call.

**Acceptance:**

* Every price in the scan is dated and sourced.
* The services compared are genuinely comparable (same deliverable
  shape), not headline rates for different work.
* The recommendation follows from the scan and says what would
  change it.

### E4. Program calendar

Keep a dated list of upcoming grants, hackathons, and bounty
programs an agent entry could enter cheaply. Each entry carries
its deadline, its prize and payout terms verified on the organizer
page, and its entry cost in owner minutes. The list lives in the
Program calendar section below; anything closing within 30 days
also gets its own issue.

**Acceptance:**

* Prize and payout terms are verified on the organizer page, not
  on an aggregator or a snippet.
* Every entry is dated, and expired entries are removed or marked
  closed.
* Anything closing within 30 days has a matching issue.

### Program calendar

Verified entries, soonest deadline first. An entry appears here
only after its prize and payout terms have been read on the
organizer page itself.

* None verified yet. The first verified entries land here through
  E4. The AgentTab grant already in preparation (deadline
  Nov 1, 2026) is tracked in workstream C; it is an entry in
  progress, not a sourcing lead, so it is not listed here.

## F. Products and subscriptions

**Why:** the proven checks earn one sale at a time. Packaged, they
become products a buyer can choose without a bidding round, and the
first subscription turns one of them into recurring work.

### Segment packs as products

A bulk pack of ten proven 10 USD checks at 100 USD total was
approved on 2026-10-24. Named segment packs (vendor and KYB,
carrier onboarding, nonprofit grantee) give each buyer type its own
spec and draft listing copy, written against the approved pack
terms.

**Acceptance:**

* One pack spec per segment, naming its fetchers, its per pack
  subject limits, and its delivery window.
* The carrier pack flags the FMCSA Licensing and Insurance
  component as a separately quoted risk extra (lessons 9 to 12 of
  the paid patterns playbook).
* Listing copy is a draft for the owner listing step; nothing is
  posted by the follow on task.
* No price appears that the owner has not approved.

### Carrier monitoring subscription (first subscription build)

`tools/standing_watch.py` exists, and a 79 USD per month asking
price is approved for a watch of up to 50 carriers and 20 products
(an asking price, not yet paid by any buyer). Build the
subscription runbook around the tool.

**Acceptance:**

* A subscription runbook covering baseline, weekly pull, the change
  alert format with before and after excerpts, and the quiet week
  one line note.
* The existing hand built sample is regenerated by the tool end to
  end.
* An order handling note states how a buyer pinned list enters and
  leaves the watch.
* No listing or price change is made by the follow on task.

### Carrier Watch offer page (adopted 2026-10-24, extends the subscription above)

**Why:** the subscription cannot be sold from a runbook. The page
is the offer a buyer reads.

**Acceptance:**

* The page names the product, the watch types covered today
  (carriers by USDOT), the cycle, and the price as approved by the
  owner (79 USD per month asking price for up to 50 carriers and 20
  products, approved 2026-10-24) and no other price; estimate tiers
  from any plan document do not appear as prices.
* A sample report on the page is the output of a real live run of
  `tools/standing_watch.py` against public records, run at build
  time, with its watchlist, run time, and snapshot provenance
  stated on the page (hard rule 2). Stored demo output may be
  linked, not passed off as the fresh run.
* A sample alert shows one changed entry in the real change report
  format: the field, the old value, the new value, and the new
  state's source evidence beneath its link.
* A what the watch does not cover section states, in plain words:
  the Licensing and Insurance limit, the product name search miss
  limit, that the watch reports changes and does not rate or
  recommend, and that changes surface at the next cycle, not in
  real time.
* The page is a draft in the repo for the owner's listing step; the
  task posts nothing and changes no listing.

### Sanctions watch types in the standing watch (adopted build, 2026-10-24)

**Why:** a vendor sanctions rescreen product needs sanctions
entries watchable next to carriers and products. The fetchers
(`tools/ofac_sdn_check.py`, `tools/oig_screen.py`) and their
fixtures already exist; the watchlist format does not.

**Acceptance:**

* The watchlist format gains a sanctions entry type naming the
  list (OFAC SDN, OIG LEIE), the subject as the fetcher takes it,
  and an optional label, validated the same way carrier and product
  entries are validated, with bad entries refused.
* The fields per sanctions entry are only what the fetchers
  return: the match state and the matched record fields as shown,
  with an empty result proven by the full raw response in the
  evidence (hard rule 3).
* Snapshots, diff, and report rendering treat sanctions entries
  like the existing types, and fail closed is preserved: a failed
  or uninterpretable sanctions fetch aborts the run with no report
  and the snapshot untouched.
* Offline tests use the existing OFAC and OIG fixtures and cover a
  match, a proven empty result, a change between runs, and a fetch
  failure aborting; the existing standing watch tests keep passing
  unchanged in behaviour.
* The Vendor Sanctions Rescreen product launch is deferred (see
  below); this item builds watch types only.

### Deferred, with their triggers

* **Recall Watch offer page.** Deferred until the Carrier Watch
  offer page above ships. When triggered, it stands alone, is
  built on the subscription scheduler with no scheduler changes
  beyond a product watchlist, and follows the offer page shape
  above: the approved price as ruled by the owner at that time (no
  price is approved for Recall Watch today, and no plan estimate
  may appear as a price), a sample report from a real live run at
  build time, a sample alert in the real format, and a does not
  cover section carrying the product name search miss limit.
* **Vendor Sanctions Rescreen product.** Deferred until the first
  subscription (Carrier Watch) has a buyer or a listed month
  behind it. The watch types it needs are the adopted build above;
  the product, its offer page, and any price are filed as their
  own tasks when the trigger fires.
* **Contract Awards Brief subscription** (`tools/weekly_brief.py`).
  Deferred until the subscription scheduler exists and one
  subscription is selling. When triggered, the brief for a buyer's
  chosen industry codes and watchlist is produced and delivered on
  the same schedule, configuration and snapshots kept per buyer, a
  failed source fetch produces the failure notice behaviour and
  never a brief that silently omits a source, the price is
  whatever the owner rules at that time, and offline tests cover a
  scheduled brief run and the failure notice path.

## G. Maintenance and cutoffs

### Census and pin automation, merge route plan first

**Why:** refresh commits are a steady treadmill (about 18 percent
of recent non merge commits, restated 2026-10-24). Stage 1 is the
plan, and it is the first deliverable; stage 2, the build, is a
separate task filed only after stage 1 is approved. No workflow
file is edited under this item.

**Acceptance (stage 1):**

* A one page plan naming the merge route for any
  `.github/workflows/` change per PLAYBOOK lesson 7, or a
  coordinator side design needing no workflow change, with the
  coordinator side option evaluated first.
* A list of pins classified as buyer protecting or internal, with
  drops proposed.

### NEAR prebuild cutoff, 2026-11-06

**Why:** seven `agents/` prebuilds sit behind unawarded bids placed
2026-10-23 at 125 to 450 USDC each. The cutoff gives each one a
disposition instead of indefinite maintenance.

**Acceptance:**

* On 2026-11-06, a cutoff note in board state gives each unawarded
  prebuild one disposition: list as its own product (with the
  listing step named as the owner step) or stop maintaining.
* Any prebuild whose job has vanished from the board is named
  explicitly.
* No folder is deleted under this item.
