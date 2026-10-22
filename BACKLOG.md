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
