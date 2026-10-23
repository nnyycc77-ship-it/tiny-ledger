# Draft listing copy: recall check MCP server

Status: **draft copy inside the repo.** This repo has not submitted it
anywhere; the owner pastes it into the MCPize dashboard when setting the
listing (see `DEPLOYMENT.md`, which also records that MCPize's app reports
the server itself live). Every claim below traces to behaviour the merged
server has (its README and tests in `mcp_server/` and
`tools/tests/test_recall_mcp.py`, and the coordinator's live runs recorded
on PR #41). The example is rendered from a recorded source response with
its provenance. Nothing here is a track record claim beyond the paragraph
quoted from `AGENT-BRIEF.md`.

## Title

Hojo recall check: sourced CPSC and NHTSA recall lookups

## Short description

One tool, `recall_check`, returns a recall check for a consumer product
(CPSC SaferProducts) or a vehicle (NHTSA, by make, model and year) as a
Markdown report in a fixed evidence format: the exact query, the UTC
retrieval time, the source link, and the complete raw response printed
beneath the link. An empty result is proven by that raw response, never
asserted. A failed fetch is an error, never an empty result.

## Long description

The server fetches live from the two public United States recall sources
on every call and caches nothing. Its report is the same text the
operator's own fetchers produce, unchanged: no summary, estimate, or value
from anywhere else is added. For a product, it searches the CPSC
SaferProducts recall API by product name; optional arguments let the caller
mark records whose product names do not equal an exact name as checked and
excluded, and run broader searches that are checked the same way. For a
vehicle, it searches the NHTSA recalls API by make, model and model year;
optional entries list a returned campaign as checked and excluded with the
caller's reason, and a campaign that is not in the response is refused.

Observation only. The report records what the public databases returned at
the stated time. No product or vehicle is inspected, and an empty result is
not a safety clearance.

## Tool summary (as the server lists it)

Tool name: `recall_check`. Input schema as returned by the server's
`tools/list`:

```json
{
  "type": "object",
  "properties": {
    "product": {
      "type": "string",
      "description": "Product name for the CPSC SaferProducts search (product form)."
    },
    "exact_name": {
      "type": "string",
      "description": "Product form, optional: records whose product names do not equal this are listed as checked and excluded."
    },
    "near": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Product form, optional, needs exact_name: broader product searches to run and check the same way."
    },
    "make": {
      "type": "string",
      "description": "Vehicle make (vehicle form)."
    },
    "model": {
      "type": "string",
      "description": "Vehicle model (vehicle form)."
    },
    "year": {
      "type": "string",
      "description": "Vehicle model year (vehicle form)."
    },
    "exclude": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Vehicle form, optional: CAMPAIGN=reason entries listing a returned NHTSA campaign as checked and excluded, with the operator's reason."
    }
  },
  "additionalProperties": false
}
```

Give one form per call: `product` (with optional `exact_name` and `near`),
or `make` + `model` + `year` (with optional `exclude`). The result is one
text content item holding the Markdown report, or `isError: true` with the
reason.

## Example

Rendered by the server from a recorded CPSC response, with the fetcher
replaced by that capture; no network. Capture provenance:

Source: [`tools/tests/fixtures/smart-wifi.http`](../../tools/tests/fixtures/smart-wifi.http), [`provenance.json`](../../tools/tests/fixtures/provenance.json)
```text
"url": "https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant+Pot+Smart+WiFi",
"retrieved_utc": "2026-10-23T00:05:58Z",
"sha256": "e50cbc096ac645dbe81f3efa7327e7585286be9d75efc6e0c5679abab35e3409"
```

Tool call: `{"product": "Instant Pot Smart WiFi"}`. Tool result text,
byte for byte (the raw response inside keeps its CRLF line endings):

````markdown
# Recall check: Instant Pot Smart WiFi

Observation only: this report records what the public CPSC recall database returned at the retrieval time stated below; no product was bought, sold, handled, or tested, and an empty result is not a safety clearance.

Produced by the Hojo Research Agent recall check API from tools/cpsc_recalls.py. The query, the retrieval time, the source link, and the complete raw response are below.

## CPSC recall search
### Product query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant+Pot+Smart+WiFi
Retrieved (UTC): 2026-10-23T00:05:58Z

CPSC returned 0 record(s) for this query.
No records returned for this query; this is not a product safety clearance.

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant+Pot+Smart+WiFi>
```
HTTP/1.1 200 OK
content-type: application/json; charset=utf-8
content-length: 2
pragma: no-cache
server: envoy
x-aspnet-version: 4.0.30319
x-powered-by: ASP.NET
access-control-allow-origin: *
access-control-allow-headers: Content-Type
access-control-allow-methods: POST, GET, PUT, DELETE, OPTIONS
cache-control: no-cache
expires: Fri, 23 Oct 2026 00:05:58 GMT
date: Fri, 23 Oct 2026 00:05:58 GMT
alt-svc: h3=":443"; ma=93600
strict-transport-security: max-age=31536000 ; includeSubDomains ; preload
x-envoy-upstream-service-time: 153

[]
```
````

## Per call price

Set by the owner: **0.05 USDC per call.** Source: the `pricing` block of the
root [`mcpize.yaml`](../../mcpize.yaml), added in commit
[f6fc36c](https://github.com/nnyycc77-ship-it/tiny-ledger/commit/f6fc36c77a6993f8915d20056fd50124437cc1fa)
("Sync mcpize.yaml pricing with dashboard: x402 on Base, recipient owner
wallet, recall_check 0.05 USDC"): protocol `x402`, network `base`, asset
`usdc`, tool `recall_check`, price `"0.05"`. The price is the owner's; this
folder records it and does not set it. It is inside the documented range of
0.01 to 100 USDC (item 4 below).

### The earlier suggestion, kept for its arithmetic

Before the owner set the price, this folder suggested **1.00 USDC per
call.** The suggestion is superseded; the arithmetic and its sources stay
as the record of how it was reached:

1. The operator's catalog rate for a full research job is 10 USD.
   Source: [AGENT-BRIEF.md, hard rule 4](../../AGENT-BRIEF.md)
   > 4. **Track record claims stay honest and current.** As of
   >    2026-10-23 the true record is: five paid jobs won and delivered
   >    on Synmerco (a recall check, a carrier vetting report, a
   >    litigation screen, a Cook County property tax comps report, and
   >    a Tampa flood zone screen), all five paid out and swept to the
   >    owner wallet, 48.43 USDC in total, and all five released with no
   >    revision round; ten services
   >    listed for hire on ugig at 10 USD each; AgentTab deployed on Arc
   >    testnet, with the mainnet deployment and grant submission in
   >    preparation for a Nov 1, 2026 deadline. Do not write any claim
   >    stronger than this. When the record changes, the reviewer updates
   >    this paragraph.
2. The published recall delivery, one such 10 USD job, covered six subjects.
   Source: [deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md](../../deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md)
   ```text
   # Recall check: six named consumer products in the CPSC and NHTSA recall databases
   ```
   Per subject that is 10 USD / 6 = 1.67 USD, rounded to two places.
3. One tool call answers one subject with no revision round and no human
   arrangement, so a price below per subject parity fits: 1.00 USDC.
4. The coordinator's reading of MCPize's monetization page on 2026-10-23
   (quoted in [`DEPLOYMENT.md`](DEPLOYMENT.md) beneath its link) gives a
   per tool price range of 0.01 to 100 USDC, so 1.00 USDC is inside the
   range, and a default revenue share of 80 percent, so the seller receives
   0.80 USDC per call. The page itself was not read from the build
   environment; the task text in issue #33 states the same share.

What would change it: MCPize's fee schedule or minimum once the page is
read directly; the going per call rate for comparable sourced lookups from
the workstream E3 pricing scan when it exists; and the cost of the live
fetch, which is currently zero (no keys, public sources). The price in
force is the one the owner recorded in the root `mcpize.yaml` pricing
block, 0.05 USDC per call, not this suggestion.

## What the server does not do

- It does not interpret, rank, or score results, and does not say a product
  or vehicle is safe.
- It does not search any source other than the two named above.
- It does not collect payment. Payment is collected by the platform that
  lists the server; the server only states the payout wallet when one is
  configured.

## Track record the operator may state, exactly as written

Source: [AGENT-BRIEF.md, hard rule 4](../../AGENT-BRIEF.md)
> 4. **Track record claims stay honest and current.** As of
>    2026-10-23 the true record is: five paid jobs won and delivered
>    on Synmerco (a recall check, a carrier vetting report, a
>    litigation screen, a Cook County property tax comps report, and
>    a Tampa flood zone screen), all five paid out and swept to the
>    owner wallet, 48.43 USDC in total, and all five released with no
>    revision round; ten services
>    listed for hire on ugig at 10 USD each; AgentTab deployed on Arc
>    testnet, with the mainnet deployment and grant submission in
>    preparation for a Nov 1, 2026 deadline. Do not write any claim
>    stronger than this. When the record changes, the reviewer updates
>    this paragraph.
