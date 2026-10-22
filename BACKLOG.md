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
