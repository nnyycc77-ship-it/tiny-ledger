# `exchange_rate_check`: exchange rate

A tool factory wave 1 tool (issue #168, parent #158). The fetcher is
[`tools/exchange_rate_check.py`](../../tools/exchange_rate_check.py), and it is served as
`GET /fx` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #208 (issue #204), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

- **What it answers:** The exchange rate the public Frankfurter API gives for one currency pair, latest or for a date, with the rate's own date, and with the API's own converted figure when an amount is given.
- **Source:** Frankfurter API v1, `https://api.frankfurter.dev/v1/latest?base=<FROM>&symbols=<TO>` (plus `&amount=<N>` when given), or `/v1/<YYYY-MM-DD>?...` for a date. Keyless. The Frankfurter homepage says: "You don't need an API key." The v1 page describes v1 as serving European Central Bank data, with "the latest working day's rates, updated daily around 16:00 CET" (both quoted by the coordinator on #168).
- **Arguments:** `base` and `target` (three letter currency codes), optional `amount` (a positive number), optional `date` (YYYY-MM-DD).
- **Needs on the server:** Outbound HTTPS to `api.frankfurter.dev`. No key, no environment value.
- **What it is not:** A quote to trade at. The rate is the API's own figure for the date the response shows. For the recorded weekend date (Saturday 2024-01-06), the API answered with the rates dated 2024-01-05, and the report states the response's own date, not the one asked.
- **Version note:** The v1 documentation says: "The v1 API is deprecated in favor of v2, but will continue to work." Each recorded v1 response carries a `deprecation` header and a `link` to a v2 successor. This tool uses v1, the version whose responses are recorded. A move to v2 is a separate task.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

Every report uses the repo's fixed evidence format. Each claim has its
source link with the raw response directly beneath it, the exact query
and retrieval time are recorded, and a missing rate is proven by the
complete raw response. A failed fetch is an error that names the
source, never an empty result.

## What a report shows, on a recorded response

The tool's answer for one recorded response, USD to EUR with an amount
of 100. The claims are the tool's own lines for that response (the
offline tests check these exact lines), with the recorded response
printed directly beneath the source link.

- `RATE: 100.0 USD = 89.34 EUR, rate date 2026-10-23 (each as shown in the response).`
- `- rates.EUR as shown: 89.34`
- `- The figure for EUR is the API's own conversion of the amount sent; this tool does no arithmetic.`

Source: https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR&amount=100, captured keyless by the coordinator under Option B on issue #168 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/168#issuecomment-6379109049)), retrieved 2026-10-24, about 03:05 UTC (response Date header: Sat, 24 Oct 2026 03:06:03 GMT); body 71 bytes, sha256 `ad6617ee99350b619f5eccf4dee1b5bb9bee515e24592e74303038f5c0be347e`; saved as [`tools/tests/fixtures/frankfurter/latest-USD-EUR-amount-100.http`](../../tools/tests/fixtures/frankfurter/latest-USD-EUR-amount-100.http)
```text
HTTP/1.1 200 OK
Date: Sat, 24 Oct 2026 03:06:03 GMT
Content-Type: application/json; charset=utf-8
CF-RAY: a4f5c36a1c7f20ac-IAD
Server: cloudflare
cache-control: public, max-age=86400
etag: "ddb2c31ee37226cd131c19d7d87ace78"
vary: Origin
x-robots-tag: noindex
deprecation: @1779103800
link: <https://api.frankfurter.dev/v2/rates>; rel="successor-version"
Accept-Ranges: bytes
cf-cache-status: MISS
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=j3AwPupjCiOQXnLjh6JIUbeojVIP43PqQsz1Oi7l8%2FpO4xhuyftg%2BFO3dSKV%2F97jHEom2Apge8yPDMI7r4T7LAzfDZ07eEO6JuEFpI%2FkBLy%2FJoHvCTNxdQSDhbeHXCedEnsAVDD9ICPjmNl5Grhppgs%3D"}]}
Content-Length: 71

{"amount":100.0,"base":"USD","date":"2026-10-23","rates":{"EUR":89.34}}
```

## The other outcomes, on recorded responses

All recorded responses are in [`tools/tests/fixtures/frankfurter/`](../../tools/tests/fixtures/frankfurter/), with their provenance:

- **Latest, no amount** (USD to EUR): `RATE: 1.0 USD = 0.89342 EUR, rate date 2026-10-23`.
- **A weekend date** (2024-01-06): the API answers with date `2024-01-05`, and the report says the rate is for 2024-01-05, not the date asked.
- **An unknown code** (USD to XYZ): HTTP 404 with body `{"message":"not found"}`. The report says no rate was returned, quotes that message, and the complete raw response beneath the source link proves it.
- **The currencies list** (`/v1/currencies`): recorded as the reference for which codes the API knows. The tool does not fetch it; each call is one GET, and the API's own answer decides.

## Not verified here

This container cannot reach `api.frankfurter.dev` (the proxy refuses the
connection), so no live run was made from it. The tool's behaviour is
tested offline on the five recorded responses above. The coordinator's
live smoke run at review is the live check.
