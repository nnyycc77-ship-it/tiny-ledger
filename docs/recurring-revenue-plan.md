# Recurring revenue plan: watch subscriptions

Status: **plan, not adopted.** Written 2026-10-24 as a follow-on to
`docs/growth-proposal.md` and `docs/revenue-plan-1000-per-day.md`.
Repo facts are cited to their files. **Every price, subscriber count and
timeline below is an estimate for planning, not data**, to be confirmed
by workstreams E2 and E3 before it goes into any listing.

## 1. Why subscriptions, and why now

Recurring revenue is the only realistic path to the targets in
`docs/revenue-plan-1000-per-day.md`. Most of it is already built.
`tools/standing_watch.py` takes a buyer's list once, rechecks it on
each run, stores a dated snapshot, and reports only what changed:
alerts for changed entries with the new source evidence in the fixed
delivery format, and one line for each unchanged entry
(`docs/standing-watch.md`). It covers two watch types today: carriers by
USDOT number through `tools/fmcsa_carrier.py`, and products through
`tools/cpsc_recalls.py`.

## 2. The products

Prices are estimates to test.

| # | Product | Built on | Status | Price idea |
| --- | --- | --- | --- | --- |
| 1 | **Carrier Watch:** weekly alerts when a broker's carriers lose authority or insurance, or their safety rating changes | `standing_watch.py` + `fmcsa_carrier.py` | Works today, run by hand | 49 USD/mo up to 25 carriers, 149 USD/mo up to 150, 399 USD/mo up to 500 |
| 2 | **Recall Watch:** weekly recall alerts on a seller's product catalog | `standing_watch.py` + `cpsc_recalls.py` | Works today, run by hand | 29 USD/mo up to 50 products, 99 USD/mo up to 300 |
| 3 | **Vendor Sanctions Re-screen:** monthly OFAC and OIG re-checks of a vendor or contractor list | `ofac_sdn_check.py`, `oig_screen.py` | Fetchers exist; needs adding to the standing watch | 79 to 249 USD/mo |
| 4 | **Contract Awards Brief:** weekly federal awards for chosen industry codes, plus SEC Form D filings | `tools/weekly_brief.py` (`docs/weekly-brief.md`) | Works today, run by hand | 49 to 99 USD/mo |

**Lead product: Carrier Watch.** It is fully built, freight brokers
already pay for carrier monitoring (to be confirmed by E2), and a lapsed
insurance policy is an alert the buyer acts on right away.

## 3. What is missing before the first subscriber can pay

Repo work is items 1, 2 and 4. Item 3 is the owner's decision.

1. **Scheduler and delivery.** Run each watch on a timer, keep each
   buyer's snapshots, and deliver each report by email or webhook.
   Today the watch runs by hand. It must fail closed: a failed fetch
   sends a failure notice, never a "no change" report (`PLAYBOOK.md`,
   lesson 3).
2. **Sanctions watch types.** Add OFAC and OIG entries to the watchlist
   format next to carriers and products, with tests, for product 3.
3. **Recurring billing (owner decision).** Monthly crypto payments are
   awkward for business buyers. Card billing (Stripe or similar) means
   KYC, which conflicts with the current no-KYC filter (`BACKLOG.md`,
   E1). Without card billing, sell prepaid quarterly or annual plans in
   USDC.
4. **One offer page for each product.** Each page has a real sample
   report built from live public records (hard rule 2: no invented
   data), the tiers, what one alert looks like, and what the watch does
   not cover.

## 4. Revenue math

Estimates, at about 100 USD per subscriber per month blended:

| Target | Subscribers needed |
| --- | --- |
| 100 USD/day | about 30 |
| 500 USD/day | about 150 |
| 1,000 USD/day | about 300 |

Subscriptions take weeks to months to build up, not days. On the other
hand, each customer keeps paying, so revenue keeps growing as long as
cancellations stay low (aim for under about 5 % a month).

## 5. Where the first subscribers come from

This is owner work: repo helpers never send outreach (`AGENT-BRIEF.md`,
Boundaries). Buyer segments are hypotheses for E2.

- **Carrier Watch:** small freight brokers and dispatchers.
- **Recall Watch:** Amazon and Shopify sellers of children's products
  and home goods.
- **Vendor re-screening:** healthcare staffing agencies and small
  marketplaces.
- **For any of them:** offer the first 10 customers a founding price for
  paying a quarter up front. That gets cash in now and shows whether
  people will pay.

## 6. Order of work

1. Carrier Watch scheduler and delivery, with tests.
2. Carrier Watch offer page with a real sample report.
3. Owner decides billing and starts founding-customer sales.
4. Recall Watch offer page (the same scheduler serves it).
5. Sanctions watch types, then the Vendor Re-screen offer.
6. Contract Awards Brief as a subscription.

## 7. Checkpoints

- **Week 2:** Carrier Watch can run on its own schedule; offer page is
  live; first founding customers are being contacted.
- **Week 6:** 10 or more paying subscribers on any product. If there are
  fewer than 5, change the niche or the offer before building more.
- **Month 3:** about 30 subscribers, about 100 USD per day.

## 8. Rules that do not change

The watch reports are deliveries, so `AGENT-BRIEF.md` hard rules 2 and 3
apply to every edition: values as shown in the source, raw evidence
beneath each source link, empty results proven by the full raw response,
and a failed fetch never shown as "no change".
