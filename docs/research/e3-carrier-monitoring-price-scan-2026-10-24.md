# E3 price scan: carrier monitoring services, 2026-10-24

The price scan for issue
[#330](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/330),
testing the Carrier Watch figures in section 2 of the recurring
revenue plan against what carrier monitoring sells for today.
Research and drafting only. No outreach was sent, no account was
opened, and no price is changed by this scan; pricing stays with the
owner.

## The figures under test

- **79 USD per month, the only approved asking price** (approved
  2026-10-24 as an asking price, not yet paid by any buyer): up to 50
  carriers and 20 products, baseline then weekly pulls with change
  alerts, from the standing watch in `tools/standing_watch.py` over
  `tools/fmcsa_carrier.py`.
- **The plan's tier estimates, unapproved and under test here:** 49
  USD per month up to 25 carriers, 149 up to 150, 399 up to 500.

## How this scan was built

- Vendor pages were opened live by H5 on 2026-10-24, and the excerpt
  under each price is the page's own wording. Four prices rest on
  secondary sources and are labelled where they appear: CarrierTrail
  (an aggregator product page), Carrier Assure and RMIS (a
  competitor's buyer guide), and CarrierOwl (verified on its own page
  on 2026-10-23 in the earlier E2 record; this pass could not re-open
  its pricing page, and the figure is carried with its date).
- Comparability rule, from the issue: only monitoring of a pinned
  carrier list counts. One off carrier vetting prices are excluded
  (the separate catalog E3 covers them). Products that bundle
  monitoring inside a wider workflow are included but their wider
  scope is stated, so the comparison stays honest.
- Per carrier figures are derived by dividing the published monthly
  price by the published list size, and are labelled derived wherever
  they appear. They are a comparison device, not a vendor price.

## The scan

### Pinned list monitoring, published prices (the clean comparables)

**VerifyCarrier, Carrier Watch.** The closest comparable in the
market: the same product name, the same 50 carrier size.

Source: [VerifyCarrier](https://verifycarrier.com/)
```text
Watch 50 carriers. $49 /month. Monitor up to 50 carriers. Email when FMCSA posts an insurance cancellation, with the effective date. Email when FMCSA posts an involuntary suspension notice, with the effective date. Email when the FMCSA census file shows an out-of-service or safety-rating change. API included, 1,000 calls a month.
```
- Monitors: authority (suspension notices), insurance filings and
  cancellations, safety rating and out of service changes.
- Derived: 0.98 USD per carrier per month at the 50 carrier size.

**AuthorityWatch.** Pure monitoring of federal filings, flat pricing
by list size.

Source: [AuthorityWatch](https://authoritywatch.io/)
```text
Founding: $49/mo, locked for life. 250 monitored carriers. Instant alerts + Monday digest.
Starter: $59/mo. 250 monitored carriers. Instant alerts + Monday digest. 14-day free trial, no card.
Pro: $109/mo. 1,000 monitored carriers. CSV export & API (coming). 14-day free trial, no card.
```
```text
Authority status, insurance filings and cancellations, safety ratings, out-of-service orders, registration changes - checked against official FMCSA data around the clock, every few hours.
```
- Derived: 0.24 USD per carrier per month at 250 (Starter), 0.11 at
  1,000 (Pro).

**CarrierOwl.** Carrier vetting with watchlists and monitoring, the
incumbent named in the earlier E2 record.

Source: the coordinator's live verification of CarrierOwl's own page
on 2026-10-23, quoted in the E2 record (issue #62, comment
6368296296). This pass could not re-open the page, so the figure is
dated 2026-10-23 and marked for re-verification.
```text
CarrierOwl monitoring tier: the page shows Free at $0 (5 full searches per day) and Broker Pro at $79 per month with watchlists and monitoring included.
```
- The page as verified does not state a watchlist size cap, so no
  per carrier figure is derived.

**CarrierTrail.** Browser based vetting and monitoring, daily checks
with email notifications. Secondary source (aggregator product page,
read 2026-10-24):

Source: [SourceForge, freight broker software listing](https://sourceforge.net/software/freight-broker/usa/)
```text
CarrierTrail is browser-based carrier vetting and monitoring software for freight brokers. Watchlists help teams follow carrier changes through scheduled daily checks and email notifications. Paid monitoring starts at $49 per month for 500 active carriers and two workspace members; the $99 Team plan supports 5,000 carriers and five members.
```
- Derived: 0.10 USD per carrier per month at 500, 0.02 at 5,000.

### Monitoring bundled in a wider product, published prices

**DOTScreener.** Carrier selection documentation; continuous
monitoring is included in the single plan rather than sold by list
size.

Source: [DOTScreener pricing](https://www.dotscreener.com/pricing)
```text
$99 /month + $14.99/month per additional user. Unlimited carrier reviews — no cap, no overage. Continuous carrier monitoring with change alerts.
```
```text
Does DOTScreener monitor carriers after I screen them? Yes — continuous monitoring is included with every account. Every day we re-check them against live FMCSA data and alert you — in the app and by email — when something material changes: authority status, safety rating, insurance filings, or a new out-of-service order.
```
- No list size is published, so no per carrier figure is derived.
  The relevant fact is the shape: at 99 USD the monitoring is
  unlimited, which caps what a size capped plan can charge a buyer
  who compares the two.

**Carrier411.** The established broker monitoring platform
(authority, insurance, safety, plus its FreightGuard community
reports, which are not monitoring and are noted so the comparison
stays clean). Its own homepage publishes no price and gates accounts
by eligibility:

Source: [Carrier411](https://carrier411.com/)
```text
Account Eligibility Required. Carrier411 is not a service for trucking companies. Accounts and user access to the site are allowed at our discretion.
```

Its price is widely reported at 99 USD per month, by a competitor's
comparison page citing carrier411.com (2026) and by trade press
coverage:

Source: [CarrierOk, CarrierOk vs Carrier411](https://www.carrierok.com/compare-carrier411)
```text
Its published price is $99 a month, with its Web Services Interface and CSV downloads sold as add-ons (carrier411.com, 2026).
```

**Carrier Assure.** Daily recalculated carrier performance grades
with monitoring; a scoring product rather than a filings tripwire.
Secondary source (a competitor's buyer guide, read 2026-10-24):

Source: [DOTScreener, Carrier Vetting Software 2026 buyer's guide](https://dotscreener.com/blog/carrier-vetting-software-buyers-guide-2026)
```text
Carrier Assure grades carriers A through F against similar-sized peers, recalculated daily, using FMCSA data, tracking data and related-entity checks. It has a free Individual plan and lists Premium at $149/month after an offer period. Its own FAQ says it doesn't yet vet insurance policies (it analyzes FMCSA insurance data).
```

AuthorityWatch's own page states the same figure as a per seat
price ("Carrier Assure publishes $149/seat",
[authoritywatch.io](https://authoritywatch.io/)).

**WeighStation, Broker Subscription.** Screening at volume with
monthly monitoring alerts, priced flat per account. Published but
marked coming soon, so it is evidence of intended pricing, not of a
selling product:

Source: [WeighStation, Broker Subscription](https://www.weighstation.io/reports/broker-subscription.html)
```text
Unlimited WeighStation Quick Screens, API access to integrate into your TMS, batch screening, team seats, and monthly carrier monitoring alerts — all for a flat monthly rate. COMING SOON. $499 /mo. Per account. Annual plan available at $449/mo.
```

### No published price (itself evidence)

- **Truckstop RMIS**, the established onboarding and compliance
  platform with continuous monitoring: the competitor guide above
  reports "Truckstop lists RMIS Lite starting at $340/month, with
  RMIS Pro by quote" (secondary, read 2026-10-24). The Lite figure
  could not be verified on Truckstop's own page in this pass; the Pro
  tier is quote only either way.
- **Highway**, the carrier identity platform: the same guide states
  "Pricing isn't published; brokers book a demo" (secondary, read
  2026-10-24).
- **Descartes MyCarrierPortal**: aggregator comparisons consistently
  record "Pricing: No information available" for it (SourceForge
  comparison pages, read 2026-10-24), a demo and quote motion.
- **Carrier411** also belongs in this section in part: whatever its
  reported price, its own homepage sells eligibility and discretion,
  not a price.

The pattern across the established end of the market (RMIS, Highway,
MyCarrierPortal, Carrier411) is quote or gate first, price second.
Published prices live at the newer, smaller end: VerifyCarrier,
AuthorityWatch, CarrierTrail, DOTScreener, CarrierOwl.

## What the evidence says about the figures under test

Headline prices for pinned list monitoring cluster tightly:

| Shape | Published figures (USD per month) |
| --- | --- |
| Entry monitoring plans | 49 (VerifyCarrier, 50 carriers), 49 to 59 (AuthorityWatch, 250), 49 (CarrierTrail, 500), 79 (CarrierOwl Broker Pro), 99 flat unlimited (DOTScreener), 99 reported (Carrier411) |
| Larger lists | 109 (AuthorityWatch, 1,000), 99 (CarrierTrail Team, 5,000) |
| Wider platforms | 149 (Carrier Assure Premium), 340 reported starting (RMIS Lite), 499 coming soon (WeighStation account) |

Derived per carrier prices fall steeply with list size everywhere:
0.98 at 50 carriers, 0.24 at 250, 0.11 at 1,000, 0.02 at 5,000, and
unlimited at a 99 USD flat plan. No incumbent's per carrier price
rises as the list grows.

Against that:

- **The approved 79 USD anchor sits inside the observed band.** It
  matches CarrierOwl's Broker Pro headline exactly, and sits between
  the 49 to 59 entry plans and the 99 flat plans. At 50 carriers its
  derived per carrier price is 1.58 USD, above VerifyCarrier's 0.98
  at the identical size. The anchor is defensible only on scope:
  Carrier Watch as approved also covers 20 products and delivers a
  weekly evidence report, which none of the 49 USD comparables do.
  As a pure carrier monitoring price at 50 carriers, the market says
  49.
- **The tier estimates invert the market's size curve.** The 49 USD
  estimate buys only 25 carriers, a derived 1.96 per carrier, the
  highest per carrier figure anywhere in this scan, at the smallest
  list, where every incumbent gives 250 to 500 carriers for the same
  money. The 149 USD estimate at 150 carriers (0.99 derived) charges
  Carrier411's reported headline for a tenth of AuthorityWatch's Pro
  list. The 399 USD estimate at 500 carriers (0.80 derived) is eight
  times AuthorityWatch's per carrier price at 1,000 and forty times
  CarrierTrail's at 5,000, and it prices a 500 carrier list above
  DOTScreener's unlimited plan by a factor of four. The direction of
  the tiers (more money, more carriers) is right; the size steps are
  roughly ten times tighter than the market's at every rung.

## Recommendation

**Hold the approved 79 USD anchor, and do not adopt the 49, 149 and
399 tier estimates as drawn.** The anchor needs no defence beyond
scope, and a single anchor matches how the closest comparables sell
(VerifyCarrier sells exactly one size; DOTScreener exactly one
plan).

If the owner later wants a tiered shape, the evidence supports
tracking the market's per carrier curve instead of the estimates'
steps, for example 49 USD up to 250 carriers, 99 USD up to 1,000,
and 199 USD up to 5,000 (each step at or slightly above the cheapest
comparable's derived per carrier price, leaving room for the wider
Carrier Watch scope). These are candidate figures for an owner
decision, stated because the acceptance asks for stated figures;
this scan changes no price, and the 79 USD anchor remains the only
approved asking price unless the owner rules otherwise.

**What would change the call:**

- A first paying buyer at 79 USD validates the anchor as drawn; a
  pattern of losses to VerifyCarrier or AuthorityWatch on price in
  real sales conversations would argue for meeting the 49 USD entry
  point at a larger list size instead.
- A re-verification of CarrierOwl's page, if its 79 USD tier has
  moved or gained a size cap, changes the anchor's closest headline
  match.
- Any published price from the quote only end (RMIS Pro, Highway,
  MyCarrierPortal) would test whether the established platforms
  really transact above the published band or merely gate access to
  similar figures.
- Evidence that buyers pay for the product side of the watch (the 20
  products in the approved scope) as part of the same subscription,
  which no comparable in this scan bundles, would support holding a
  premium over the pure monitoring band.

## Not verified

- **CarrierOwl's price was not re-opened in this pass.** The 79 USD
  figure is dated 2026-10-23 and rests on the earlier E2 record's
  live verification; search did not surface the pricing page today.
- **CarrierTrail, Carrier Assure, RMIS Lite, and Highway** rest on
  the secondary sources labelled above, not on the vendors' own
  pricing pages.
- **Carrier411's 99 USD** is reported by a competitor page and trade
  press; its own homepage publishes no price, as quoted.
- **WeighStation's 499 USD** is a coming soon price for a product not
  yet on sale.
- **No buyer was contacted** and no transaction was observed; the
  scan compares published asking prices, which is what the issue
  asks for, and asking prices are not paid prices.
