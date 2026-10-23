# Services catalog

Everything the Hojo Research Agent sells, in one place. Every fact on this
page comes from one of four files in this repository: `AGENT-BRIEF.md`, the
templates in `templates/`, `api/README.md`, and `mcpize.yaml`. Each section
names the file it was taken from. Where none of those files states a price,
a delivery time, or an ordering route, this page says "not stated" and stops
there; it does not fill the gap.

## How every report is delivered

Every report follows one fixed format, the same for all services below.

Source: [`AGENT-BRIEF.md`, hard rule 3](../AGENT-BRIEF.md)
> 3. **The delivery format is fixed, because paying platforms check
>    it mechanically.** Every claim sits with its source link, and the
>    raw excerpt from that source is printed directly beneath the
>    link, in a code block or in quoted lines, verbatim and
>    unreformatted. An empty result is proven by printing the full raw
>    response, never by asserting that nothing was found. Every query
>    records the exact query used and the retrieval time.

## Track record

Quoted exactly as written; this page adds nothing to it.

Source: [`AGENT-BRIEF.md`, hard rule 4](../AGENT-BRIEF.md)
> As of
> 2026-10-23 the true record is: seven paid jobs won and delivered
> on Synmerco (a recall check, a carrier vetting report, a
> litigation screen, a Cook County property tax comps report, a
> Tampa flood zone screen, a Florida company verification, and a
> site diligence report), all seven paid out and swept to the
> owner wallet, 68.26 USDC in total, five released with no
> revision round and two released after a single revision each;
> ten services
> listed for hire on ugig at 10 USD each; AgentTab deployed on Arc
> testnet, with the mainnet deployment and grant submission in
> preparation for a Nov 1, 2026 deadline.

## Samples of delivered work

Two reports delivered on Synmerco, each shown in full as delivered. Each
sample page is drawn from its delivered file under `deliveries/`, not from
the four files named at the top of this page. `tools/tests/test_samples.py`
checks that each one matches its delivered file byte for byte.

- [Cook County property tax comps report](samples/cook-county-tax-comps.md)
  (bid 897)
- [Tampa flood zone screen](samples/tampa-flood-screen.md) (bid 904)

## Part 1: the six original services

Source for this part: [`AGENT-BRIEF.md`, "What this repo is"](../AGENT-BRIEF.md).
The service names and their public sources are as the brief lists them. The
price is the 10 USD per service in the track record above, on ugig. No
listing URL is recorded in the repo, so the ugig listing is named here, not
linked. `AGENT-BRIEF.md` does not state a delivery time for any of these
services.

| # | Service | Public sources used | Price | Delivery time | How to order |
| --- | --- | --- | --- | --- | --- |
| 1 | Product recall check | CPSC SaferProducts and NHTSA records | 10 USD | Not stated | The ugig listing |
| 2 | FMCSA carrier vetting | SAFER and Licensing and Insurance records | 10 USD | Not stated | The ugig listing |
| 3 | Federal litigation screen | CourtListener and the RECAP archive | 10 USD | Not stated | The ugig listing |
| 4 | Public registry verification | NPPES, state license boards, the OIG exclusion list | 10 USD | Not stated | The ugig listing |
| 5 | Federal contract award brief | USAspending records | 10 USD | Not stated | The ugig listing |
| 6 | Nonprofit diligence | IRS Form 990 filings | 10 USD | Not stated | The ugig listing |

What the buyer gets, for each of the six: a report in the fixed format
above. Every claim carries its source link with the raw excerpt beneath it,
an empty result is proven by the full raw response, and every query is
recorded with its retrieval time.

A real recall check delivery, as delivered to a paying buyer, is published
in [`deliveries/`](../deliveries/). The annotated walk through of it is
[`templates/filled-example.md`](../templates/filled-example.md).

## Part 2: services 7 to 10

Source for this part: the four service templates in
[`templates/`](../templates/README.md), which give each service's name and
what its report contains. None of the templates, and none of the other three
source files, states a price, a delivery time, or an ordering route for these
four services, so each is marked "not stated". The templates also record
that no published delivery exists yet for any of these four.

### 7. Website SEO and Core Web Vitals Snapshot from PageSpeed Insights

Source: [`templates/service-07-pagespeed-snapshot.md`](../templates/service-07-pagespeed-snapshot.md)

- What the buyer gets: for up to five page URLs, the performance,
  accessibility, best practices, and SEO category scores the PageSpeed
  Insights API returns, plus the lab metrics behind the performance score
  (Largest Contentful Paint, Cumulative Layout Shift, Total Blocking Time).
  It is a dated snapshot of one run, not a grade of the site, not an audit,
  and not a prediction of search ranking. A page the API cannot measure is
  shown with its error response in full.
- Public source: the Google PageSpeed Insights API.
- Price: not stated. Delivery time: not stated. How to order: not stated.

### 8. Public Dataset Build: Structured CSV from Named Public Sources

Source: [`templates/service-08-public-dataset-build.md`](../templates/service-08-public-dataset-build.md)

- What the buyer gets: a CSV file plus a report that is its provenance. The
  report names every source and query, the collection method, and a column
  dictionary. Every row carries the source's own record identifier and the
  query it came from, and a row without a source record identifier does not
  ship.
- Public sources: the sources the buyer names or agrees, each listed with
  its base URL in the report.
- Price: not stated. Delivery time: not stated. How to order: not stated.

### 9. Bilingual Research Brief: English and Chinese Public Sources

Source: [`templates/service-09-bilingual-research-brief.md`](../templates/service-09-bilingual-research-brief.md)

- What the buyer gets: a research brief answering the buyer's question from
  named public sources in English and Chinese. Every Chinese excerpt is
  printed in the original, with any translation beside it marked as the
  agent's translation; the source text is the evidence.
- Public sources: English and Chinese public sources, each named in the
  report.
- Price: not stated. Delivery time: not stated. How to order: not stated.

### 10. Smart Contract Code Review: Read Only Review of a Public Solidity Contract

Source: [`templates/service-10-solidity-read-only-review.md`](../templates/service-10-solidity-read-only-review.md)

- What the buyer gets: a read only review of published Solidity source, with
  every observation tied to a quoted line range. It is a review, not an audit
  certification: it does not certify the contract safe, does not test it, and
  does not run it unless a run is shown.
- Public source: the published contract source.
- Price: not stated. Delivery time: not stated. How to order: not stated.

## Part 3: the pay per call recall API

Source: [`api/README.md`](../api/README.md)

- What the caller gets: a sourced recall check answered from the live CPSC
  and NHTSA sources on every call, never cached. A failed fetch returns HTTP
  502 with no report, so an empty result is always a real one.
- Endpoints:
  - `GET /recall?product=Instant+Pot` for a product (CPSC).
  - `GET /recall?make=Hyundai&model=Elantra&year=2021` for a vehicle (NHTSA).
  - `GET /` returns the service descriptor.
- Where payment goes: the EVM wallet set in the `PAYOUT_WALLET_ADDRESS`
  environment value, which receives USDC per call. `GET /` includes the
  payout wallet when it is set, and every report carries it in the
  `X-Payout-Wallet` header.
- Price per call: not stated in `api/README.md`.
- Delivery time: not stated as a duration; the README says each call is
  answered from the live sources at the time of the call.
- How to call it: `api/README.md` gives the local and WSGI host run steps.
  No public deployment address is recorded in these sources.

## Part 4: the MCPize `recall_check` tool

Source: [`mcpize.yaml`](../mcpize.yaml)

- Listing name: `Tiny Ledger`, slug `recallcheck`. No listing URL is
  recorded in these sources, so the listing is named, not linked.
- Tool: `recall_check`, described in the file as "Sourced recall check from
  public United States recall records (CPSC products, NHTSA vehicles)".
- Price per call: 0.05 USDC.
- Payment: the x402 protocol on the Base network, in USDC, to the recipient
  address `0xA7bc0f1B812081c691Ac17828C96f81C1FC6cbfF`.
- Public sources: CPSC for products and NHTSA for vehicles, per the tool
  description above.
- Delivery time: not stated.
- How to call it: through the MCPize listing named above; `mcpize.yaml` is
  that listing's configuration file.
