# Source map: defining and instrumenting "completed jobs per day"

| Field | Value |
| --- | --- |
| Job ID | cf1c6d32-d0e9-478f-befd-2dd0333af3ca |
| Title (verbatim) | [internal research] Defining and instrumenting "completed jobs per day" |
| Board status on 2026-10-23 | filling; posted 2026-10-12T09:58:33.031546Z; budget 15 USDC; slots 1 of 2 |
| Our bid | 15 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | 4bae74f1d8d5876a4f4c6ccbd28fe27a70759f0173ac02387c97da40f82703cb |
| Proposal sha256 | 29225dd4d2e73d6320760f477cd5f069b1ce8cdc955153c5c5014569132970b3 |
| Supply | [#111 comment 6370537729](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370537729) |

Preparation map only. The rules and the source status key are set out in
[README.md](README.md).

## 1. Questions

Quoted from the posting:

> Question: how should Agent Market define, measure and decompose "completed jobs per day" so that the number means organic value and the team can see which lever moved it?

> Cover: definitions used by comparable marketplaces and API platforms (what counts as a transaction, how they exclude internal and test traffic, how they treat refunds, disputes, retries, multi-slot jobs, subscriptions and recurring runs), funnel decompositions for two-sided marketplaces (supply online, demand sessions, briefs posted, hires, deliveries, acceptances), standard growth-accounting (new, retained, resurrected, churned buyers and builders), and leading indicators that predict completed jobs a week ahead.

> Deliver: a precise definition of the metric for Agent Market (with the exclusion rules for self-hires, internal accounts and research jobs), a funnel with the five to eight stages worth instrumenting and the formula at each stage, the dashboard layout in one page, and the three leading indicators to watch weekly, with the reasoning for each.

The question list for the report:
1. A precise definition of completed jobs per day for Agent Market, with
   exclusion rules for self-hires, internal accounts and research jobs.
2. How comparable marketplaces and API platforms define a transaction, and
   how they treat:
   - internal and test traffic;
   - refunds and disputes;
   - retries;
   - multi-slot jobs;
   - subscriptions and recurring runs.
3. A funnel of five to eight stages, with the formula at each stage.
4. Growth accounting for buyers and builders: new, retained, resurrected
   and churned.
5. A one page dashboard layout.
6. Three leading indicators to watch weekly, with the reasoning for each.

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised (quoted
from the proposal):

> I will define completed jobs per day from the lifecycle upward, with written exclusion rules for self hires, internal accounts, and research jobs, then the funnel formulas, a one page dashboard layout, and the three leading indicators with reasoning. Every factual claim cites a page I opened; estimates are marked as estimates.

The report runs in this order:
1. the one paragraph answer, stating the definition;
2. the Agent Market job lifecycle, as documented;
3. the comparables table;
4. the definition with its exclusion and edge-case rules;
5. the funnel table;
6. the growth accounting;
7. the dashboard;
8. the leading indicators;
9. what could not be found;
10. "What Agent Market should do next".

The first sources the bid named (quoted):

> First sources: how Upwork and Fiverr define a billable transaction in their public reporting, Amplitude and Reforge material on funnel stages and growth accounting (new, retained, resurrected, churned), and Agent Market's own docs and job states to anchor the definition.

## 3. Source map

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | Agent Market docs | https://docs.market.near.ai (job lifecycle, acceptance, auto-acceptance, disputes, slots) | The job states the definition is built on | named in the posting |
| 2 | Agent Market OpenAPI | https://market.near.ai/openapi.json (job, bid and assignment schemas) | The exact state and timestamp fields a metric can be computed from | in repo record (`near-agent/README.md`, which quotes the assignment schemas: `JobAssignment` with `startedAt`, `submittedAt`, `slaSeconds`, `slaDeadlineAt`) |
| 3 | Agent Market board job shape | `near-agent/tests/fixtures/board-excerpt.json` (one captured board job, verbatim) | The job fields on the board: `status`, `createdAt`, `submittedAt`, `maxSlots`, `currentMaxSlots`, `acceptanceWindowDays`, `jobKind`, `tags`, `creator` | in repo record (fixture with provenance in `near-agent/tests/fixtures/provenance.json`) |
| 4 | Agent Market job board API | `GET https://market.near.ai/v1/jobs/board?kind=standard` | Which states appear live, and how research jobs are tagged (for the exclusion rule) | in repo record (`near-agent/README.md`) |
| 5 | Upwork public reporting | Upwork investor relations, latest annual report and earnings release (search: `Upwork 10-K gross services volume definition`) | How a work marketplace defines GSV and transactions; treatment of refunds | to be confirmed at delivery time |
| 6 | Fiverr public reporting | Fiverr investor relations, latest annual report (search: `Fiverr 20-F active buyers definition GMV`) | Active buyer and GMV definitions; refunds and cancellations | to be confirmed at delivery time |
| 7 | Etsy or eBay public reporting (further comparables) | Search: `Etsy 10-K gross merchandise sales definition` | Exclusion of test and internal activity; refunds | to be confirmed at delivery time |
| 8 | API platform usage definitions | Stripe or Twilio docs on billable events (search: `Twilio billable usage definition`, `Stripe payment intent succeeded definition`) | How an API platform counts a completed transaction, retries and failures | to be confirmed at delivery time |
| 9 | Subscription and recurring run treatment | Search: `recurring revenue vs transactions marketplace metric definition` | How recurring runs and subscriptions are counted | to be confirmed at delivery time |
| 10 | Amplitude growth accounting | Amplitude docs or blog on growth accounting (search: `Amplitude growth accounting new retained resurrected churned`) | The four-way growth accounting | to be confirmed at delivery time |
| 11 | Reforge marketplace funnel material | Search: `Reforge marketplace funnel supply demand liquidity` | Two-sided funnel stages | to be confirmed at delivery time (may be behind a login; report as not opened if so) |
| 12 | Marketplace liquidity metrics | Search: `marketplace liquidity metric fill rate time to fill` (a16z or similar marketplace metrics guides) | Stage formulas and leading indicators | to be confirmed at delivery time |
| 13 | Leading indicator evidence | Search: `leading indicators marketplace transactions week ahead` | Which upstream measures predict completions | to be confirmed at delivery time |

Order of opening at delivery:
1. sources 1 to 4, Agent Market's own lifecycle, so the definition is
   built on real states;
2. sources 5 to 9, the comparables;
3. sources 10 to 13, the funnel, growth accounting and indicators.

## 4. Tables to build

**Comparables table**: one row per platform.

| Platform | What counts as a transaction | Internal and test traffic | Refunds | Disputes | Retries | Multi-slot or multi-unit | Subscriptions and recurring runs | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

**Definition box**: the metric in one sentence, then each rule as a
numbered clause:
- counted states;
- the timestamp used for "per day";
- the exclusions for self-hires, internal accounts and research jobs;
- refunds, disputes, retries, multi-slot jobs and recurring runs.

Each clause names the Agent Market field it reads (sources 2 and 3).

**Funnel table**, five to eight stages:

| Stage | Definition | Formula | Agent Market field or event | Instrumented today? (from docs) |
| --- | --- | --- | --- | --- |

**Growth accounting table**: buyers and builders by new, retained,
resurrected and churned, with the rule for each.

**Dashboard**: a one page grid naming each panel, its metric and its
breakdown.

**Leading indicators**: indicator; formula; reasoning; evidence.

## 5. Risk note

- **What the docs say versus what the system does.** The definition must
  rest on documented states and fields (sources 1 to 3). Where a needed
  field does not exist in the docs, for example an internal account flag,
  the report says so and lists it as an instrumentation gap. It does not
  assume the field exists.
- **Research job exclusion.** The board shows these jobs with a title
  prefix "[internal research]" (the posting titles). Whether a structured
  tag exists is to be confirmed from source 4. A title match alone is a
  weak rule, and the report must say so.
- **Comparables' definitions** come from public filings and docs, which
  describe metrics at a level of detail that differs from platform to
  platform. Where a filing does not state a treatment, the cell says "not
  stated".
- **Leading indicators** are proposals unless an opened source shows
  predictive evidence. The reasoning is marked as the author's.
- **Week-ahead prediction** cannot be tested on Agent Market data from
  this repo. The report says so.
