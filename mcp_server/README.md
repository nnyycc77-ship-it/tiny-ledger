# Recall check MCP server (core)

Part 1 (B1, issue #37) of the MCP server for the recall check. This folder
is the server itself: the protocol, the one tool, and the wiring to the
merged fetchers. Platform packaging, deployment notes and listing copy are
part 2 (B2, issue #38) and attach around the entry point below without
changing the core. Nothing here is deployed anywhere, and nothing here
assumes a hosting platform.

## What it does

`python3 -m mcp_server` (from the repository root) speaks the Model
Context Protocol over stdio: JSON-RPC 2.0, one message per line. It serves
`initialize`, `ping`, `tools/list` and `tools/call`, accepts the
`notifications/initialized` notification, and answers any other method
with the JSON-RPC "method not found" error. Stdout carries protocol
messages only; diagnostics go to stderr.

One tool, `recall_check`:

| Form | Arguments | Source |
| --- | --- | --- |
| product | `product`; optional `exact_name`; optional `near` (array, needs `exact_name`) | CPSC SaferProducts recall API, via `tools/cpsc_recalls.py` |
| vehicle | `make`, `model`, `year`; optional `exclude` (array of `CAMPAIGN=reason`) | NHTSA recalls API, via `tools/nhtsa_recalls.py` |

The tool result is the recall check as Markdown in the fixed delivery
format from `AGENT-BRIEF.md`: claim lines, the exact query, the UTC
retrieval time, the source link, and the complete raw response directly
beneath the link, with an empty result proven by that raw response. The
text comes from `api.recall_api.recall()`, the same host-free dispatcher
the pay per call API uses, so for the same query the MCP tool and the API
return the same report byte for byte; the server adds nothing, summarises
nothing, and estimates nothing. A bad request, a failed fetch, or a
response the fetcher cannot read comes back as a tool error (`isError`
true) with only the error message, never as an empty result.

## Configuration

One optional environment value, the same one the API reads:
`PAYOUT_WALLET_ADDRESS`, the EVM address that receives USDC per call. It is
read through `api.recall_api.payout_wallet()`, which refuses a malformed
value at start. When set it is stated in the `initialize` instructions and
the tool description; payment collection is the listing platform's job, not
the server's. Nothing else is read from the environment, and no key or
secret exists in this folder.

Needs Python 3.10+ and `curl` on PATH (the CPSC fetcher captures responses
with curl, see `tools/README.md`). No packages.

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
text.

## Where part 2 attaches

The entry point is `python3 -m mcp_server` (module `mcp_server.recall_mcp`,
function `main()`); `serve(stdin, stdout, wallet)` is the transport-free
loop for a host that provides its own streams. Packaging adds a manifest and
metadata beside this folder and points at that entry point; the core stays
as it is.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_recall_mcp.py' -v
```

The tests need no network. They drive the server in process over JSON-RPC
and over a real stdio subprocess, with the fetchers patched to return the
recorded public captures already in this repo with their provenance: the
CPSC captures in `tools/tests/fixtures/` and the NHTSA S24 excerpt from the
published recall delivery, carried by `tools/tests/test_nhtsa_recalls.py`.
For each sample query the test asserts the tool's text equals
`api.recall_api.recall()` for the same query. No recall data is invented.
