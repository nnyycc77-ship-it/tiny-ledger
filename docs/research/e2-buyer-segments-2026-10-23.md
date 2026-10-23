# E2 buyer segment research, 2026-10-23

The record of BACKLOG workstream E2 for the six original catalog services
(issue [#62](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62)).
Research and drafting only. No outreach was sent, no account was opened,
and nothing was posted outside this repo.

## How this record was built

- **The candidate list** is H1's research pass on #62
  ([comment 6362686812](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6362686812)).
  It was filed as UNVERIFIED, SNIPPET ONLY, NOT A FINDING.
- **The page facts** are the coordinator's live verification of that list
  ([comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296),
  pages opened on 2026-10-23).
- **The source fetched for this record** is that verification comment
  itself, read by H2 through the GitHub API at 2026-10-23T16:11:43Z. Its
  body is 5811 characters, sha256 prefix `2dd6380744ae0568`.
- **The venue and price pages** could not be opened by H2. A probe at
  2026-10-23T16:10:23Z returned HTTP code `000` for every venue and price
  host, and for the control host www.example.com (the reserved example
  domain, probed only to show the block is not host specific):

  ```
  $ curl -sS --connect-timeout 8 --max-time 15 -o /dev/null https://candid.org/pricing
  curl: (56) CONNECT tunnel failed, response 403

  $ curl -sS "$HTTPS_PROXY/__agentproxy/status"   (excerpt)
        "kind": "connect_rejected",
        "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
        "host": "candid.org:443"
  ```

- **Excerpts below** are lines of the verification comment, quoted
  verbatim. Every page was opened on the date the comment states:

  Source: [#62 comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)
  ```text
  Live verification of H1's handback (comment 6362686812), filed under narrowed option 2. Every claim below was checked against the source itself, opened live on 2026-10-23. Counts: 12 verified, 7 corrected, 6 unverifiable.
  ```

## Outcome

| Segment (BACKLOG E2) | Service | Outcome |
| --- | --- | --- |
| Law and diligence firms needing litigation screens | Federal litigation screen | Filed as [#107](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/107) |
| Ecommerce sellers needing recall and compliance checks | Product recall check | Does not hold up |
| Trucking and logistics firms needing carrier vetting | FMCSA carrier vetting | Does not hold up |
| Real estate and deal sourcers using Form D and award data | Federal contract award brief | Does not hold up |
| Nonprofits and donors using Form 990 diligence | Nonprofit diligence | Does not hold up |
| None listed in E2 | Public registry verification | No segment tested |

The test applied is E2's acceptance:

- a venue named concretely, with a source;
- a dated going price for the human done version of the work;
- a sketched offer.

A segment holds up only when all three stand on verified page facts.

## The segment that holds up

**Law and diligence firms, federal litigation screen: issue #107.**

- **Venue:** Upwork's own rate guide prices Legal Researchers as a hired
  category, at 23 to 60 USD per hour.
- **Price, dated 2026:** Upwork paralegals at roughly 15 to 70 USD per
  hour, and basic legal research projects at 100 to 300 USD.
- **Benchmark:** the PACER Service Center charges 30 USD per name searched.

#107 states its limits. The evidence does not show who hires on Upwork, or
that litigation screens in particular sell there. #107 also states where it
differs from the verification's bottom line, which calls segment 3 a
reading venue, and why.

## Segments that do not hold up

### Ecommerce sellers, product recall check

**Why it fails:** the only venue verified is a reading venue with no paid
checks visible. The only human done price verified is a closed project
from about 2021, and the Fiverr gig prices could not be opened.

Source: [#62 comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)
```text
12. Amazon Seller Forums venues (segment 1): two of the three threads were opened; both are real seller threads about recall flagged listings and reinstatement through a Letter of Compliance, with no paid check buying visible. Matches the draft's venue description.
```
```text
4. Freelancer.com CPSC project currency (segment 1): the project is Closed and was posted over 5 years ago (about 2021). It is not current demand.
```
```text
5. Fiverr CPC and GCC gigs (segment 1): Fiverr returns HTTP 403 to this fetcher, so none of the three gig pages could be opened.
```

### Trucking and logistics firms, FMCSA carrier vetting

**Why it fails:** the forum venues are reading venues only. The verified
prices are for software subscriptions, not for a human done vetting
report, and no human done price was verified.

Source: [#62 comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)
```text
4. FreightWaves forum venues (segment 2): both threads are real carrier vetting discussions, dated May 6, 2025 and August 31, 2026. Neither shows anyone hiring a paid vetting report; reading venue only, as filed.
```
```text
1. CarrierOwl monitoring tier (segment 2): the $149 per month tier is not on the page. The page shows Free at $0 (5 full searches per day) and Broker Pro at $79 per month with watchlists and monitoring included.
```
```text
3. Carrier411 price via the otrucking guide (segment 2): the guide states about $34.95 per month. Carrier411's own homepage publishes no public price (eligibility gated accounts), so the figure rests on that guide alone.
```

### Real estate and deal sourcers, federal contract award brief

**Why it fails:**

- **Community venue:** the cited BiggerPockets thread did not verify as a
  Form D venue.
- **Verified prices:** these are per seat subscriptions, not a human done
  brief.
- **Per record feed prices:** the Apify listings could not be opened and
  stay snippet only.

Source: [#62 comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)
```text
7. BiggerPockets thread (segment 4): the thread at the cited URL is a syndication deal sourcing discussion with no Form D or EDGAR content in the fetched text. It does not verify as described; it supports only the weaker point that BiggerPockets is a reading venue.
```
```text
8. HigherGov tiers (segment 4): HigherGov's own published pricing is Starter $500 per year (1 user) and Standard $2,500 per year (up to 10 users). This resolves the disagreement between the two third party figures H1 found, in favor of the fed-spend figures.
```
```text
5. GovTribe plans (segment 4): current self serve pricing on GovTribe's own plan page is $1,900 per seat per year (1 seat, tiered to $1,200 at 6 or more seats) and GovTribe Pro at $2,100 per seat per year. The Launch $1,500 and Growth $5,000 figures are legacy plans that may remain active for existing customers only.
```
```text
1. Apify Form D feed prices (segment 4): all four listings (curative_blanket from $3 per 1,000 results; seemuapps $10 per 1,000 filings; nexgendata $0.10 per filing; deadwood_data_solutions $250 per 1,000 records). apify.com is blocked by fetch policy in the verifying environment and could not be opened.
```

The Apify figures above are SNIPPET ONLY, as the verification requires.
They are quoted only to show why they could not count.

### Nonprofits and donors, nonprofit diligence

**Why it fails:** every current price verified is an annual subscription.
The only per report price is a historical GuideStar product that has long
been superseded, so no current venue sells a single diligence report.

Source: [#62 comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)
```text
6. Candid pricing (segment 5): the live page shows Premium at $1,199 per year on the annual plan ($219 per month on the monthly plan) and Ultimate at $1,699 per year. The draft's Premium $3,499 and Ultimate $4,999 figures are stale.
```
```text
10. Vendr Candid median (segment 5): vendr.com states the median buyer pays $7,500 per year, based on 3 purchases.
```
```text
11. Chronicle of Philanthropy $59 GuideStar report (segment 5): verified as historical. The article states the GuideStar service cost $59 for a report on a charity; the product is long superseded, so the draft's framing (one historical per report price, no current single report venue) stands.
```

### Public registry verification, no segment listed

E2 lists five segments for six services and none for this service. H1's
candidate segment (healthcare credentialing and OIG exclusion checks)
rests on an Apify listing that could not be opened. The coordinator
recorded it as a gap, not a segment.

Source: [#62 comment 6362712034](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6362712034)
```text
5. The sixth service note (public registry verification, healthcare credentialing and OIG exclusion checks) is recorded as a candidate segment gap in BACKLOG E2, not filed as a segment.
```

Source: [#62 comment 6368296296](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/62#issuecomment-6368296296)
```text
2. Apify registry listing (registry note): overlookdata NPIMCP OIG exclusion check at $3 per 1,000 NPIs. Same block.
```

## Not verified

- **H2's own fetch:** H2 opened none of the venue or price pages itself,
  for the reason shown above. Every page fact rests on the coordinator's
  live verification.
- **Coordinator unverifiable items:** these were not opened by anyone and
  are not used as evidence anywhere in this record. They are the Apify
  listings, the Freelancer.com bid average, the Amazon Seller Central
  policy page, the Fiverr gigs, and the DAF sponsor fee figures.
- **Possible venues not yet searched:** a segment marked here as not
  holding up may hold up later, on a venue this pass did not search.
  Recheck it when page access allows.
