# E2 buyer segments for sanctions and exclusion screening, 2026-10-24

The record of BACKLOG workstream E2 for the three screening tools in
`tools/` (`ofac_sdn_check.py`, `oig_screen.py`, `csl_screen.py`), for
issue [#321](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/321).
Research and drafting only. No outreach was sent, no account was
opened, and nothing was posted outside this repo.

## How this record was built

- Every page fact below was opened live by H5 on 2026-10-24, and the
  excerpt under each claim is the page's own wording. Pages are cited
  by the URL that was opened.
- Two price points rest on secondary sources and are labelled where
  they appear: the enterprise tier estimates (a third party guide) and
  the RapidAPI tier table (the API maker's own post quoting its
  marketplace listing; the listing page itself was not opened).
- The x402 contrast figure is the program study finding the issue
  itself states (competing name screens at 0.001 to 0.01 USDC per call
  on the x402 Bazaar), corroborated by the published x402 price survey
  quoted in the price ladder below.
- The earlier E2 record (2026-10-23, removed from this repo in the
  quieting package) left healthcare credentialing and OIG exclusion
  checks as a recorded gap, because its only candidate source could
  not be opened. This pass opens the vendor pages directly, and the
  healthcare segment is tested properly here for the first time.

The test applied is E2's acceptance, the same as the earlier record:

- the segment is tied to the named screening service;
- where the buyers are is named concretely, with a source;
- the going price is stated, with a dated source;
- the shape of an offer in that venue is sketched.

A segment holds up only when all four stand on verified page facts.

## Outcome

| Segment (issue #321) | Service | Outcome |
| --- | --- | --- |
| Fintechs and payment firms with onboarding checks | OFAC SDN check, CSL screen | Holds up |
| Healthcare staffing firms screening against the OIG exclusion list | OIG screen | Holds up, in the wider employer and supply chain form stated below |
| Marketplaces screening sellers | OFAC SDN check, CSL screen | Does not hold up as a standalone segment on this pass |

## The price ladder the segments sit on

The issue asks what buyers pay for evidence grade screening rather
than a bare match flag. The opened pages give a four rung ladder,
retrieved 2026-10-24:

1. **Bare flag, agent rails:** 0.001 to 0.01 USDC per call (the
   program study figure stated in issue #321). A published survey of
   x402 OFAC address screening found the same band from the other
   side of the market:

   Source: [What AI agents pay per call, part 2 (dev.to, Tanod)](https://dev.to/tanod/what-ai-agents-pay-per-call-part-2-domains-whois-holidays-ibanvat-screenshots-and-sanctions-58lk)
   ```text
   41 distinct priced offers on 36 hosts, all of them screening a crypto address.
   Lowest listed price per call: USD 0.001
   Median: USD 0.005
   Highest listed price per call: USD 0.1
   ```

2. **Bare flag, developer marketplace:** SanctionRail sells an OFAC
   name screen through RapidAPI. The maker's own post quotes the
   listing tiers (the listing page itself was not opened, so this rung
   is labelled secondary): PRO $9 per month for 10,000 calls, ULTRA
   $49 for 100,000, MEGA $199 for 1,000,000. At full use that is
   0.0009 to 0.002 USD per call.

   Source: [Screen a name against the OFAC sanctions list (dev.to, SanctionRail maker)](https://dev.to/hudsonenterprises/screen-a-name-against-the-ofac-sanctions-list-in-3-lines-rest-api-free-tier-23gg)
   ```text
   | PRO | $9/mo | 10,000 |
   | ULTRA | $49/mo | 100,000 |
   | MEGA | $199/mo | 1,000,000 |
   No credit card on the free tier. Subscribe at the RapidAPI listing.
   ```

3. **Hosted match API with maintained data:** OpenSanctions, the
   hosted screening API built on the open sanctions dataset, moved to
   prepaid credit bundles effective 2026-09-24 at 0.10 EUR per
   screening query at the smallest bundle, falling to 0.03 EUR at the
   largest. That is roughly 6 to 30 times the x402 median, for the
   same nominal act of matching a name, with the difference buying
   maintained multi list data and a stable API.

   Source: [OpenSanctions changelog, entry 51](https://www.opensanctions.org/changelog/?category=yente&category=Hosted%20API)
   ```text
   | Bundle price | Credits | Price per screening query |
   | €50 | 500 | €0.10 |
   | €400 | 5,000 | €0.08 |
   | €2,000 | 30,000 | €0.067 |
   | €5,000 | 100,000 | €0.05 |
   | €15,000 | 500,000 | €0.03 |
   ```

4. **Evidence and review workflow:** SanctionsKit sells the screen
   together with retained evidence, source versions, and an analyst
   review dashboard, priced per completed subject:

   Source: [SanctionsKit, OFAC and sanctions screening API](https://www.sanctionskit.com/product/api)
   ```text
   | Starter | $59 USD | 5,000 | API + compliance dashboard + retained review workflow |
   | Growth | $239 USD | 25,000 | API + compliance dashboard + retained review workflow |
   | Scale | $719 USD | 100,000 | API + compliance dashboard + retained review workflow |
   ```
   ```text
   Production from $59/month USD for 5,000 completed screenings. API and dashboard included.
   ```
   ```text
   HTTP or transport error: A valid completed screening result was not obtained. Keep the check incomplete. Correct the cause or retry safely; never translate an error into no_match.
   ```

   At full allowance that is 0.0118 USD per completed subject on
   Starter, before the review workflow's value is counted at all.

**The test result, stated plainly:** evidence grade screening does
sell above the bare flag band, by a factor of about 6 to 30 at the
hosted API rung and by far more in healthcare (below). But every
published per call price found in this pass still sits under the
0.25 USDC shelf price the three tools carry under the issue #147
ruling. At 0.25 the offer cannot be the flag or the match; it has to
be the evidence pack itself (the source record, the list version,
the retrieval time, and the raw excerpt a reviewer can file), sold
where a buyer already pays for that pack, or bundled into a recurring
watch where the per call price stops being the comparison.

## Segment 1: fintechs and payment firms with onboarding checks

**Verdict: holds up.**

- **Service tie:** `ofac_sdn_check.py` and `csl_screen.py` screen a
  name against the OFAC SDN and Consolidated lists and the trade
  Consolidated Screening List, which is the onboarding check a payment
  firm runs on customers, payees, and suppliers before an account
  opens or a payment releases.
- **Where the buyers are, concretely:** they buy screening in three
  named places. Direct from hosted API vendors with published prices
  (OpenSanctions and SanctionsKit, both opened above). On developer
  marketplaces, RapidAPI named concretely by the SanctionRail listing
  above. And at the top of the market, through enterprise contracts
  with Dow Jones Risk and Compliance, Refinitiv World-Check, and
  ComplyAdvantage; a third party guide (labelled secondary, not a
  vendor page) puts those at roughly 10,000 to 100,000 USD per year,
  quote based:

  Source: [OFAC Screening: Avoid Costly Violations (terms.law guide)](https://terms.law/Trading-Legal/guides/ofac-sanctions-screening.html)
  ```text
  Dow Jones Risk & Compliance: Pricing: Enterprise (contact for quote); typically $10K-50K+ annually depending on volume
  Refinitiv World-Check: Pricing: Enterprise (contact for quote); typically $15K-100K+ annually
  ComplyAdvantage: Pricing: Starts around $12K annually; scales with volume and features
  ```

- **Going price, dated 2026-10-24:** the ladder above. A fintech
  onboarding screen costs the buyer 0.001 to 0.01 USD as a bare flag,
  0.03 to 0.10 EUR as a hosted match, and about 0.012 USD per
  completed subject inside an evidence and review plan at 59 USD per
  month.
- **Offer shape in the venue:** in the marketplace venue, a listing
  in the SanctionRail shape: a named single purpose API (screen one
  name against the OFAC lists), a free tier for evaluation, and paid
  tiers by monthly call volume, with list freshness stated on the
  listing. In the direct venue, an API plan page in the SanctionsKit
  shape: price per completed subject, the evidence retained and
  reviewable, and failures that never render as a clear result. Our
  tools already produce the evidence half of that shape (source link,
  verbatim excerpt, retrieval time, fail closed); the missing half is
  the retained, reviewable record.

## Segment 2: healthcare staffing firms screening against the OIG list

**Verdict: holds up, in a wider form.** The buyers who pay are
healthcare employers and the staffing and contractor supply chain
around them, and staffing firms sit inside that chain rather than in
a staffing only venue. The segment as the issue states it (staffing
firms screening against the OIG list) is reached through the same
vendor storefronts as every other healthcare buyer.

- **Service tie:** `oig_screen.py` screens a name against the OIG
  List of Excluded Individuals and Entities (LEIE), the exact check
  this segment buys monthly.
- **Why they pay, from the vendor page that sells to them:**
  screening is a standing monthly obligation in this market, not a
  one off purchase:

  Source: [Exclusion Screening, FAQ](https://exclusionscreening.com/faq/)
  ```text
  Providers should screen prior to employment or to the initiation of a business relationship and monthly thereafter. Monthly screening makes sense because a person's exclusion status is always subject to change. It is required by all Medicare Advantage Plans, all State Medicaid Programs, and all Medicaid Managed Care Organizations.
  ```
  ```text
  Providers are responsible for ensuring the exclusion status of all employees, vendors and contractors that provide items or services, directly or indirectly, in whole or in part, that are payable by federal health care programs.
  ```

  Vendors screen contractors and vendors as a named part of the same
  product, which is the door staffing firms come through: an agency's
  placed clinicians are the provider's contractors, and the screening
  duty covers them by name in the text above.

- **Where the buyers are, concretely:** self serve vendor storefronts
  for healthcare exclusion screening, two opened in this pass
  (Exclusion Screening and ExclusionSentry, below). Both sell by
  roster upload with public pricing and no sales call required at the
  entry tier:

  Source: [ExclusionSentry](https://exclusionsentry.com/)
  ```text
  You can sign up and run your first screening the same day, with no sales call. Pricing is public.
  ```
  ```text
  Home health and hospice agencies, behavioral health and ABA providers, dental and physician groups, FQHCs, pharmacies, and the billing companies and compliance consultants who support them: anyone who bills Medicare or Medicaid and needs a record of who was screened, against which lists, and when.
  ```

- **Going price, dated 2026-10-24:** published, and notably higher
  per screen than anything in the sanctions ladder, because the
  product is the audit record:

  Source: [Exclusion Screening, FAQ](https://exclusionscreening.com/faq/)
  ```text
  Our Basic plan starts at $30 per month and our Premium plan starts at $40 per month, each covering up to 100 screens. Pricing scales based on the size of your roster and the level of service you need.
  ```

  At the 100 screen cap that is 0.30 to 0.40 USD per screen. The
  flat roster shape prices the same way:

  Source: [ExclusionSentry](https://exclusionsentry.com/)
  ```text
  Plans start at $29 a month with no per-name fees.
  Starter: $29/month, up to 50 roster names. Growth: $49/month, up to 150 roster names. Scale: $99/month, up to 400 roster names.
  ```
  ```text
  Monthly exclusion screening, with an audit PDF for every run. Upload your roster once. Every month it is screened against the OIG LEIE, SAM.gov, and 43 state exclusion, debarment, and termination lists, and you get a timestamped audit PDF that records which source versions were checked and how each potential match was resolved.
  ```
  ```text
  Each run produces an audit PDF that cites the exact source versions used and records its own SHA-256 so the file can be verified later. If any source was not current, the PDF says so on page one.
  ```

- **Offer shape in the venue:** a monthly roster screening in the
  ExclusionSentry shape: the buyer uploads a roster once, each run
  returns one audit ready report per cycle naming the lists, their
  versions, every potential match with its evidence, and how each was
  resolved, at a flat price by roster size in the 29 to 99 USD per
  month band. Our `oig_screen.py` is the screening step inside that
  shape; the product a staffing firm or small agency pays for is the
  recurring report, not a per call screen. This is also the one
  segment where a per name price near the shelf price already exists
  in the wild (0.30 to 0.40 USD per screen at the Exclusion Screening
  cap), because the deliverable is evidence a surveyor can be handed.

## Segment 3: marketplaces screening sellers

**Verdict: does not hold up as a standalone segment on this pass.**

- **What was tested:** whether marketplaces buy seller screening as
  its own purchasable thing, with a venue and a price of its own.
- **What the pass found:** no marketplace specific venue, listing, or
  published price for seller screening was found. Screening vendors
  describe their buyers as compliance teams, law firms, and fintechs
  doing KYC and onboarding, with marketplaces absent from the buyer
  lists on the pages opened:

  Source: [Sanctions Screening, sanctionsscreening.io](https://sanctionsscreening.io/)
  ```text
  Trusted by Compliance teams, law firms and fintechs — for KYC, onboarding and ongoing monitoring.
  ```

- **Reading of the evidence:** seller screening is bought, but it is
  bought inside the Segment 1 purchase (the same onboarding screening
  APIs and enterprise KYC contracts), not as a separate line item a
  marketplace shops for on its own. A distinct marketplace offer
  would have to be a partnership or bundle motion, which is outreach
  design, not a listing in a venue this pass can name. The segment
  may hold up later on evidence this pass did not reach, for example
  inside marketplace seller tooling app stores; it is recorded as not
  holding up, not as disproven.

## Not verified

- **sanctions.io's own pricing page** was not opened in this pass; its
  prices appear only through third party pages, so no sanctions.io
  figure is used as evidence anywhere above.
- **The RapidAPI listing page itself** was not opened; the SanctionRail
  tiers rest on the maker's own post and are labelled secondary where
  used.
- **Enterprise tier prices** (Dow Jones, World-Check, ComplyAdvantage)
  are quote based; the figures quoted come from a third party guide
  and are labelled secondary. They establish the shape of the top of
  the market, not a transactable price.
- **No buyer was contacted** and no demand was observed directly; as
  in every E2 record, the evidence shows where screening is bought
  and at what published price, not that any named buyer will buy from
  a new listing.
