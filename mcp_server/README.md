# Recall check MCP server (core)

Part 1 (B1, issue #37) of the MCP server for the recall check, extended by
issue #67 with two more tools and by issue #97 with four more. This folder is the server itself: the
protocol, the tools, and the wiring to the merged fetchers. Platform
packaging, deployment notes and listing copy are part 2 (B2, issue #38) and
attach around the entry point below without changing the core. Nothing in
this folder deploys anything, and nothing here assumes a hosting platform;
the record of what is live is in `packaging/mcpize/DEPLOYMENT.md`.

## What it does

`python3 -m mcp_server` (from the repository root) speaks the Model
Context Protocol over stdio: JSON-RPC 2.0, one message per line. It serves
`initialize`, `ping`, `tools/list` and `tools/call`, accepts the
`notifications/initialized` notification, and answers any other method
with the JSON-RPC "method not found" error. Stdout carries protocol
messages only; diagnostics go to stderr.

Seven tools, `recall_check` first in the listing:

| Tool | Form | Arguments | Source |
| --- | --- | --- | --- |
| `recall_check` | product | `product`; optional `exact_name`; optional `near` (array, needs `exact_name`) | CPSC SaferProducts recall API, via `tools/cpsc_recalls.py` |
| `recall_check` | vehicle | `make`, `model`, `year`; optional `exclude` (array of `CAMPAIGN=reason`) | NHTSA recalls API, via `tools/nhtsa_recalls.py` |
| `carrier_check` | USDOT | `usdot`; optional `source` (array, any of `census`, `safer`, `li`, in order; default all three); optional `subject` | FMCSA Company Census File (DOT open data), SAFER company snapshot, Licensing and Insurance carrier list, via `tools/fmcsa_carrier.py` |
| `carrier_check` | name | `name`; optional `limit` (integer, default 50); optional `exclude` (array of `USDOT=reason`); optional `subject` | FMCSA Company Census File name search, via `tools/fmcsa_carrier.py` |
| `litigation_screen` | party | `party` (array; the first is the exact name whose results are listed); optional `subject`, `filed_after` (YYYY-MM-DD), `order_by`, `list` (integer, default 10), `docket_details` (boolean), `exclude` (array of `DOCKET_ID=reason`) | CourtListener RECAP docket search API, via `tools/courtlistener_recap.py` |
| `formd_check` | cik or issuer | `cik` or `issuer`, not both; optional `max_filings` (integer, default 10); optional `exclude` (array of `ACCESSION=reason`). Needs `EDGAR_CONTACT` on the server | SEC EDGAR submissions API and company search, via `tools/edgar_formd.py` |
| `nonprofit_check` | name and/or ein | `name`, `ein` (array), or both; optional `subject`; optional `exclude` (array of `EIN=reason`, with `name`) | ProPublica Nonprofit Explorer API, via `tools/propublica_nonprofits.py` |
| `awards_search` | recipient or naics | `recipient` or `naics` (array); optional `start` and `end` (YYYY-MM-DD, together), `page`, `limit` (integers), `exclude` (array of `GENERATED_ID=reason`) | USAspending spending by award API, via `tools/usaspending_awards.py` |
| `pagespeed_snapshot` | url | `url` (array, up to 5); optional `strategy` (`mobile` or `desktop`), `subject`, `exclude` (array of `URL=reason`) | PageSpeed Insights API, via `tools/pagespeed_snapshot.py` |

A tool result is the check as Markdown in the fixed delivery format from
`AGENT-BRIEF.md`: claim lines, the exact query, the UTC retrieval time, the
source link, and the complete raw response directly beneath the link, with
an empty result proven by that raw response. The text comes from the same
host-free dispatchers the pay per call API uses: `api.recall_api.recall()`
for `recall_check` (`GET /recall`), and the matching `api.endpoints`
function for every other tool (`carrier()` for `GET /carrier`,
`litigation()`, `formd()`, `nonprofit()`, `awards()` and `pagespeed()` for
their paths), so for the same inputs the MCP
tool and the API return the same report byte for byte; the server adds
nothing, summarises nothing, and estimates nothing. The arguments are the
fetchers' own command line inputs under the same names (hyphens as
underscores), typed as the schema says (arrays, integers and booleans
rather than repeated flags). A bad request, an operator exclusion naming a
record the response does not contain, a failed fetch, or a response the
fetcher cannot read comes back as a tool error (`isError` true) with only
the error message, never as an empty result.

## Configuration

Environment values, the same ones the API reads:

- `PAYOUT_WALLET_ADDRESS`, the EVM address that receives USDC per call. It
  is read through `api.recall_api.payout_wallet()`, which refuses a
  malformed value at start. When set it is stated in the `initialize`
  instructions and in the `recall_check` tool description, the one tool
  with a recorded price (the root `mcpize.yaml`); payment collection is
  the listing platform's job, not the server's.
- `COURTLISTENER_TOKEN`, optional, read by `tools/courtlistener_recap.py`
  at call time for `litigation_screen` and sent as the Authorization
  header; it lifts CourtListener's anonymous rate limit and is never
  printed.
- `EDGAR_CONTACT`, required for `formd_check` by SEC EDGAR fair access:
  the operator's "Name address" contact for the User-Agent. While it is
  unset, `formd_check` answers a tool error and fetches nothing. Never
  printed.
- `PAGESPEED_API_KEY`, optional, read at call time for
  `pagespeed_snapshot`. Without it the API answers 429 with quota 0 and
  that transcript is the report. The key is never printed; the recorded
  request URL shows a redaction marker.

Nothing else is read from the environment, and no key or secret exists in
this folder.

Needs Python 3.10+ and `curl` on PATH (the CPSC fetcher captures responses
with curl, see `tools/README.md`); outbound HTTPS to the sources named in
the table above. No packages.

## Try it locally

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"local","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"recall_check","arguments":{"product":"Instant Pot Smart WiFi","exact_name":"Instant Pot Smart WiFi","near":["Instant Pot"]}}}' \
  | python3 -m mcp_server
```

The third response carries the Markdown report in `result.content[0].text`,
fetched live from CPSC at that moment. The same arguments as a query string
to the API (`GET /recall?product=...&exact_name=...&near=...`) give the same
text. Likewise:

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"carrier_check","arguments":{"usdot":"2046","source":["census"]}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"litigation_screen","arguments":{"party":["Jabil Inc."],"filed_after":"2021-10-22","list":2}}}' \
  | python3 -m mcp_server
```

gives the same text as `GET /carrier?usdot=2046&source=census` and
`GET /litigation?party=Jabil+Inc.&filed_after=2021-10-22&list=2`.

## Where part 2 attaches

The entry point is `python3 -m mcp_server` (module `mcp_server.recall_mcp`,
function `main()`); `serve(stdin, stdout, wallet)` is the transport-free
loop for a host that provides its own streams. Packaging adds a manifest and
metadata beside this folder and points at that entry point; the core stays
as it is.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_recall_mcp.py' -v
python3 -m unittest discover -s tools/tests -p 'test_mcp_carrier_litigation.py' -v
python3 -m unittest discover -s tools/tests -p 'test_mcp_remaining_fetchers.py' -v
```

The tests need no network. They drive the server in process over JSON-RPC
and over a real stdio subprocess, with the fetchers patched to return the
recorded public material already in this repo with its provenance: the
CPSC captures in `tools/tests/fixtures/`, the NHTSA S24 excerpt from the
published recall delivery (carried by `tools/tests/test_nhtsa_recalls.py`),
the FMCSA Census record for USDOT 2046 (`test_fmcsa_carrier.py`) and the
CourtListener search excerpts (`test_courtlistener_recap.py`), and the
USAspending, ProPublica, EDGAR and PageSpeed captures under
`tools/tests/fixtures/` with their provenance. For each
sample call the tests assert the tool's text equals what the API returns
for the same query. No source data is invented.
