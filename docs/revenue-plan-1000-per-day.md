# Revenue plan: toward 1,000 USD per day

Status: **plan, not adopted.** Written 2026-10-24 as a follow-on to
`docs/growth-proposal.md`. The only revenue fact in it is the track
record in `AGENT-BRIEF.md`, hard rule 4. **Every price, conversion rate,
customer count and timeline below is an estimate for planning, not
data.** Each one is a hypothesis for workstreams E2 and E3 to confirm or
replace.

## 1. The size of the gap

- **Today:** 68.26 USDC from seven paid jobs (`AGENT-BRIEF.md`, hard
  rule 4), about 9.75 USDC per job.
- **Target:** 1,000 USD per day is about 30,000 USD per month, or
  365,000 USD per year.
- **What that means:** the operation has to grow by a factor of
  several thousand. Doing more of the same 10 USD board jobs can't close
  that gap. It would take 100 jobs a day, every day, each built and
  reviewed. The way the money is earned has to change.

**Honest outlook (estimate):** 1,000 USD per day is a 9 to 12 month
stretch goal, and it is only reachable through recurring business
customers. A realistic 6-month goal is 200 to 300 USD per day. Most small
data products never reach 1,000 USD per day, so the plan sets checkpoints
and conditions for switching course rather than assuming success.

## 2. What 1,000 USD per day can be made of

There are four revenue engines, each one already partly built in the
repo. All prices are estimates.

| Engine | Unit price | Volume needed alone for 1,000 USD/day | Realistic share at month 12 |
| --- | --- | --- | --- |
| A. Monitoring subscriptions (carrier, OFAC/vendor, awards brief) | 99 to 299 USD/month | about 300 subscribers at 100 USD | 55 to 65 % |
| B. Diligence packs (KYB, carrier onboarding, grantee) | 25 to 75 USD each | 20 packs/day at 50 USD | 20 to 25 % |
| C. Pay-per-call API and MCP tools | 0.05 to 1 USD/call | 4,000 calls/day at 0.25 USD | 5 to 10 % |
| D. Larger custom jobs (NEAR market, dataset builds) | 250 to 400 USD each | 3 jobs/day | 5 to 10 % |

**Target mix at month 12 (estimate):**

| Engine | Count | Price | USD/day |
| --- | --- | --- | --- |
| A. Subscriptions | 200 subscribers | 100 USD/month blended | about 660 |
| B. Packs | 5 per day | 45 USD | about 225 |
| C. API calls | 400 per day | 0.20 USD | about 80 |
| D. Custom jobs | 2 per month | 300 USD | about 20 |
| **Total** | | | **about 985** |

Subscriptions carry the plan because they compound: each month's
customers keep paying while new ones are added. Packs and API calls are
both how buyers find the operation and how it learns what they will pay
for.

## 3. Decisions needed before scaling (owner)

These sit outside the repo and only the owner can make them.

1. **Payment rails.** The current program filter is "payout arrives in a
   crypto wallet with no KYC" (`BACKLOG.md`, E1). Most of the businesses
   that pay for subscriptions (freight brokers, compliance teams,
   contractors) pay by card or invoice, which means a processor and KYC.
   Keeping crypto-only likely caps the market well below 1,000 USD per
   day. This is the single biggest decision in the plan.
2. **Sales and outreach.** Repo helpers never send outreach
   (`AGENT-BRIEF.md`, Boundaries). Selling subscriptions needs someone
   to contact buyers, run demos and handle support. The owner has to do
   this, or allow it in a new, reviewed workstream.
3. **Legal check on screening products.** Screens of *people* (for
   example, litigation screens used to decide on employment or tenancy)
   may fall under the US Fair Credit Reporting Act. Before scaling, keep
   products to business entities, or get legal advice. Carrier, vendor,
   nonprofit and contractor screens on businesses are lower risk.
4. **Owner time budget.** The plan assumes about 1 to 2 owner hours a
   day, mostly on sales and support. Less than that means slower phases.

## 4. Phased plan

Each phase has a goal, the work to do, and a checkpoint. If a phase misses
its checkpoint, change course before starting the next one.

### Phase 0: now to Nov 1, 2026: protect the grant

- Finish the AgentTab mainnet deployment and the grant submission
  (workstream C). Nothing below displaces this.

### Phase 1: weeks 1 to 4: 10 to 30 USD per day

Goal: turn the existing tools into products people can buy, and find out
what buyers pay.

- Price every endpoint per call in `mcpize.yaml` (`growth-proposal.md`,
  item 2.1) and list in the MCP registry (`packaging/mcp-registry/`).
- Run the E3 price scan for carrier vetting, litigation and KYB.
- Build the KYB and carrier onboarding packs from existing fetchers, each
  with a filled example in `templates/`.
- Make `tools/pregate.py` catch the failure types behind past revision
  rounds, so most deliveries need no revision.
- Automate the census and pin refreshes so build time goes to products.

**Checkpoint:** at least 10 paid packs or 500 paid API calls in the
phase, and at least one buyer who comes back to buy again.

### Phase 2: months 2 to 3: about 100 USD per day

Goal: one subscription product that works in one niche.

- Choose one niche based on Phase 1 and E2 evidence. The default pick is
  **freight broker carrier monitoring**: `tools/fmcsa_carrier.py` plus
  `tools/standing_watch.py`, with alerts on authority, insurance or
  safety status changes for a broker's carrier list.
- Ship it as a subscription: list upload, daily or weekly change report
  in the fixed evidence format, and an alert only when a source record
  actually changed.
- Owner runs sales in that niche.

**Checkpoint:** 30 paying subscribers at about 99 USD per month, which is
about 100 USD per day. Change course: if there are fewer than 10 after 6
weeks of selling, switch to the second niche below instead of building
more features.

### Phase 3: months 4 to 6: 200 to 300 USD per day

Goal: a second subscription and more ways for buyers to find the
operation.

- Second niche: **vendor and sanctions re-screening** (OFAC, OIG,
  litigation, registry) for marketplaces, healthcare staffing or small
  fintechs.
- Turn the weekly brief (`tools/weekly_brief.py`) into a paid sector
  brief for government contractors or deal sourcers.
- Publish sample reports built from real public records (rule 2: no
  invented data) as the main marketing material.
- Offer a team tier at a higher price for list size or frequency.

**Checkpoint:** 80 to 100 subscribers across two products, plus steady
pack and API sales, for 200 to 300 USD per day.

### Phase 4: months 7 to 12: toward 1,000 USD per day

Goal: grow what already works; build nothing speculative.

- Put more effort into whichever niche has the best retention and the
  lowest support load per subscriber.
- Annual plans with a discount, to bring cash in sooner and keep
  customers longer.
- Partner and reseller listings (freight load boards, compliance tool
  directories, contractor associations), approved by the owner.
- Bring in AgentTab as an optional rail for agent-to-agent buyers.

**Checkpoint:** about 200 subscribers plus packs and API, for about
1,000 USD per day. If growth stalls around 300 to 500 USD per day, the
usual cause is too little sales time or the wrong payment rails, not a
missing feature.

## 5. What to stop doing

- **Speculative prebuilds.** Seven NEAR agents were built ahead of bids
  that have not been awarded (`agents/*/README.md`). Build new agents
  only after an award, or when the agent is a product in this plan.
- **Overhead that doesn't protect a buyer.** 30 of 84 non-merge commits
  are census, pin or drift refreshes (`git log --no-merges`). Automate
  them or remove them.
- **10 USD jobs that need revisions.** Raise the price, bundle them, or
  stop taking them once packs and subscriptions are selling.

## 6. Weekly scorecard

Track these every week, in a sourced issue (no invented figures):

| Metric | Why it matters |
| --- | --- |
| Revenue per day (7-day average) | The target |
| Paying subscribers, new and lost | Engine A health; cancellations above about 5 % a month need fixing first |
| Packs sold, and revision rate | Engine B, and delivery quality |
| Paid API calls | Engine C demand |
| Owner hours on sales and support | The real bottleneck |
| Buyer conversations held | Leading signal for next month's revenue |

## 7. Costs and risks

- **Costs** stay low: public data sources are free, hosting is small,
  and the main cost is compute for agent runs. 1,000 USD per day is
  revenue, not profit; track costs alongside it.
- **Source risk:** a public API can change or rate-limit. Fail-closed
  fetchers (`PLAYBOOK.md`, lesson 3) protect correctness, but a
  subscription needs monitoring for outages and a status note to
  customers.
- **Concentration risk:** one niche or one platform should not be more
  than half of revenue by month 12.
- **Reputation:** the evidence format is the product. Never ship a
  report that breaks hard rule 3 just to hit a volume target.
