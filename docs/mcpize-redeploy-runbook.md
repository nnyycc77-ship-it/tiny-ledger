# MCPize redeploy runbook: recall check server

The runbook for issue
[#123](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/123). One
owner action carries two changes that have merged to `main` but are not live
on MCPize, because auto deploy is off by design:

1. **The failure naming fix** (PR
   [#121](https://github.com/nnyycc77-ship-it/tiny-ledger/pull/121), merge
   commit `9ec53ea1c94c8dd31c81edb12f02c195a528e7fc`). A `recall_check` whose
   source cannot be read now answers with the source, the exact query and
   the reason, instead of a bare fetch error.
2. **The expanded tool set.** The six tools alongside `recall_check` are
   `carrier_check` and `litigation_screen` (PR
   [#80](https://github.com/nnyycc77-ship-it/tiny-ledger/pull/80), merge
   commit `f6a3e0c253a41ae11412676cbb76377aa54a051d`), and `formd_check`,
   `nonprofit_check`, `awards_search` and `pagespeed_snapshot` (PR
   [#102](https://github.com/nnyycc77-ship-it/tiny-ledger/pull/102), merge
   commit `6c31a3444485fe7eada6f764ea7d0fe0f76a22b8`).

This file is repo work only. Nothing here was done on the dashboard,
deployed, or paid for. Every dashboard step is the owner's, taken when the
owner chooses.

**Items marked TO CONFIRM** are facts the repo record does not hold. They
are asked on #123 (comment 6371817865) and are filled in here only from
an answer on that issue, never guessed.

## What this redeploy does not claim

The hosted fetch error from the 2026-10-23 paid proof call is **not
claimed fixed** by this redeploy.

- **What PR #121 changes:** the error names its cause, and the fetch path
  is unchanged.
- **The cause is still only probable:** most likely no `curl` binary in
  the MCPize Python runtime, with blocked outbound fetch the other live
  candidate. That stays so until a live call shows which. The diagnosis is
  in the PR #121 description.
- **What a failing call returns after the redeploy:** if the cause is
  still present, a `recall_check` product call fails as before. Its error
  text then names the cause, for example
  `... (curl is not installed on this host (not found on PATH); no recall conclusion) ...`.
  That is the evidence the fix was built to produce.
- **What the next fix depends on:** the coordinator ruled on #118
  (comment 6370988907) that the next fix waits on that evidence.

## Preconditions

Every box is checked before the owner acts.

- [ ] **The commit to deploy from** is the tip of `main`, and it contains
  all three merge commits above. Check from a clone:

  ```sh
  git fetch origin main
  for c in 9ec53ea1c94c8dd31c81edb12f02c195a528e7fc \
           f6a3e0c253a41ae11412676cbb76377aa54a051d \
           6c31a3444485fe7eada6f764ea7d0fe0f76a22b8; do
    git merge-base --is-ancestor "$c" origin/main && echo "contains $c" || echo "MISSING $c"
  done
  git rev-parse origin/main      # record this SHA as the deploy commit
  ```

- [ ] **The suites are green on that commit,** on a clean checkout:

  ```sh
  python3 -m unittest discover -s tools/tests -v     # expect OK; it includes the MCP server suites
  python3 -m unittest discover -s api -v             # expect OK
  python3 tools/pregate.py                           # expect PASS on secrets, honesty, provenance
  ```

  CI on that commit is green too: the `test` and `USAspending fetcher
  tests` workflows.

- [ ] **The local server lists seven tools** on that commit:

  ```sh
  printf '%s\n' \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"precheck","version":"0"}}}' \
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
    | python3 -m mcp_server 2>/dev/null \
    | python3 -c 'import json,sys; r=[json.loads(l) for l in sys.stdin]; print([t["name"] for t in r[1]["result"]["tools"]])'
  ```

  Expected, in this order: `['recall_check', 'carrier_check',
  'litigation_screen', 'formd_check', 'nonprofit_check', 'awards_search',
  'pagespeed_snapshot']`.

- [ ] **The live server lists one tool** before the redeploy:
  `recall_check`, as issue #123 records. The outside verification below
  starts by recording that count, so the difference is visible.

- [ ] **`mcpize.yaml` is unchanged** since the pricing commit `f6fc36c`.
  The redeploy changes code, not the price, network or recipient:

  ```sh
  git diff --stat f6fc36c77a6993f8915d20056fd50124437cc1fa origin/main -- mcpize.yaml   # expect no output
  ```

- [ ] **The owner has decided what happens to the environment values the
  new tools read.** Names only; values are never written in this repo.
  TO CONFIRM (#123, question 4).
  - `EDGAR_CONTACT`: without it, `formd_check` answers an error and
    fetches nothing.
  - `PAGESPEED_API_KEY`: without it, `pagespeed_snapshot` reports the
    API's 429 with quota 0.
  - `COURTLISTENER_TOKEN`: optional; without it, CourtListener applies
    its anonymous rate limit.

- [ ] **The owner has decided pricing for the six new tools.** The
  manifest prices `recall_check` only, at 0.05 USDC per call, so the
  six new tools go live unpriced unless the owner prices them as a
  separate decision. TO CONFIRM (#123, question 5).

## Owner steps on the MCPize dashboard

**These steps are TO CONFIRM (#123, question 1).** The repo record
(`packaging/mcpize/DEPLOYMENT.md`) quotes the MCPize GitHub app's PR #45
and the coordinator's reading of the publish and monetization pages. It
does not describe the dashboard's screens, so no button label or screen
result is written here until it is confirmed.

| # | Owner action | Expected result on screen |
| --- | --- | --- |
| 1 | Open the server `recallcheck` (the slug in `mcpize.yaml`) in the MCPize dashboard. | TO CONFIRM |
| 2 | Note the deployment shown as current (commit or deployment id) and copy it into the Rollback section below. | TO CONFIRM |
| 3 | Start one redeploy from the deploy commit recorded in Preconditions. | TO CONFIRM |
| 4 | Wait for the build to finish and confirm that the deployment now shown as current is the deploy commit. | TO CONFIRM |
| 5 | Leave pricing as it is, unless the owner decided otherwise in Preconditions. | Price for `recall_check` still 0.05 USDC (dashboard and `mcpize.yaml` agree) |

The owner takes this action once, and the coordinator runs the outside
verification below.

## Outside verification (coordinator, from a network that reaches MCPize)

**No paid call happens here.** Every request below is unpaid. A second
paid proof call is a separate owner spend decision, made on its own and
never bundled into this verification.

**Endpoint:** TO CONFIRM (#123, question 3). Issue #118 names
`https://recallcheck.mcpize.run/mcp`; PR #45 names
`https://mcpize.com/mcp/recallcheck`.

The script below speaks MCP's streamable HTTP transport:
- one JSON-RPC message per POST;
- an `Accept: application/json, text/event-stream` header;
- the `Mcp-Session-Id` the server returns, echoed back on later requests.

It uses the standard library only. It prints each status line and body
as received and pays nothing.

```python
# verify_mcpize.py: run as  python3 verify_mcpize.py <endpoint URL>
import json, sys, urllib.error, urllib.request

URL = sys.argv[1]
session = {}

def post(message):
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream",
               "MCP-Protocol-Version": "2025-06-18"}
    if "id" in session:
        headers["Mcp-Session-Id"] = session["id"]
    request = urllib.request.Request(URL, json.dumps(message).encode(), headers, method="POST")
    try:
        response = urllib.request.urlopen(request, timeout=60)
    except urllib.error.HTTPError as err:
        response = err
    with response:
        if response.headers.get("Mcp-Session-Id"):
            session["id"] = response.headers["Mcp-Session-Id"]
        body = response.read().decode("utf-8", "replace")
        print("==", message.get("method"), "->", response.status, response.reason)
        print(body)
        return response.status, body

post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                 "clientInfo": {"name": "outside-verification", "version": "0"}}})
post({"jsonrpc": "2.0", "method": "notifications/initialized"})
post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
post({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
      "params": {"name": "recall_check", "arguments": {"product": "VH101"}}})
```

What each step must show:

| Step | Expected | Fails when |
| --- | --- | --- |
| `initialize` (anonymous) | A JSON-RPC result whose `serverInfo` is `{"name": "hojo-recall-check", "version": "0.3.0"}` (the version on `main` since PR #102). | An error, or an older `serverInfo` version, which means the redeploy did not take. |
| `tools/list` | The seven tool names, in the order listed under Preconditions. | Any other count. One tool means the old build is still live. |
| `tools/call recall_check`, unpaid | A 402 payment demand for 0.05 USDC on Base to the manifest's recipient. The HTTP status and where the x402 requirements appear (HTTP body or JSON-RPC error) are TO CONFIRM (#123, question 3). | A report or a tool error with no payment demand, which means the price is not enforced. |

Record the full output of the run on issue #123, and on issue #38 as
DEPLOYMENT.md asks, with the time of the run and the deploy commit.

If the owner later makes a second paid proof call, as a separate
decision, its tool result text is recorded verbatim. It is either the
Vornado report (recalls 18-136 and 18-199 for `{"product": "VH101"}`, as
the coordinator's local run on PR #121 showed) or a named failure under
the new format. Either answers the open question on #118.

## Listing copy for the seven tools

This copy is pasted where the dashboard takes it after the outside
verification passes, replacing the one-tool copy in
[`packaging/mcpize/LISTING.md`](../packaging/mcpize/LISTING.md). Shorten
it by cutting, never by adding. Each line paraphrases that tool's own
`tools/list` description on `main`. The server's description is the
authority, and nothing here goes beyond it.

**Title:** Hojo public records checks: sourced recall, carrier, litigation,
Form D, nonprofit, contract award and PageSpeed lookups

**Short description:** Seven tools that each return a Markdown report in
one fixed evidence format: the exact query, the UTC retrieval time, the
source link, and the complete raw response beneath the link. An empty
result is proven by that raw response, never asserted. A failed fetch is
an error that names the source, never an empty result.

**Tools:**

- `recall_check`: CPSC SaferProducts recalls for a product, or NHTSA
  recalls for a vehicle by make, model and year. An empty result is not
  a safety clearance. Priced at 0.05 USDC per call (`mcpize.yaml`).
- `carrier_check`: FMCSA carrier records by USDOT number (Company Census
  File, SAFER snapshot, Licensing and Insurance) or a Census name search.
  An empty result is not a clearance.
- `litigation_screen`: an index-level federal docket screen of the
  CourtListener RECAP archive by party name. It is not a legal opinion,
  and an empty result is not proof of no litigation.
- `formd_check`: SEC EDGAR Form D filings for a company, by CIK or by
  company name search. It is a listing of filings as indexed, not an
  analysis of any offering. It works only when the server has
  `EDGAR_CONTACT` set; until then it answers an error.
- `nonprofit_check`: ProPublica Nonprofit Explorer records and the Form
  990 figures that API extracts, by name or EIN. The figures are as
  shown, not an audit.
- `awards_search`: one page of USAspending federal prime contract awards
  by recipient or NAICS code. Award Amount is the API field as returned,
  not a payment or revenue estimate.
- `pagespeed_snapshot`: PageSpeed Insights scores and lab metrics for up
  to five pages, measured at that moment. Without `PAGESPEED_API_KEY` on
  the server, the API answers 429 and that answer is the report.

The pricing of the six tools after `recall_check` is TO CONFIRM (#123,
question 5). Until the owner prices them, the listing names no price for
them.

## Rollback

**The deployment to return to** is the one live before this redeploy,
with one tool, `recall_check`.

- **Its exact commit or MCPize deployment id is TO CONFIRM** (#123,
  question 2). The owner records it at step 2 above before redeploying.
- **What the repo record narrows down:**
  - the manifest arrived with PR #45 (merged 2026-10-23T03:00:23Z, merge
    commit `7ee4fef648d50468cbe6f1f846a73959273883e5`);
  - the pricing commit is `f6fc36c77a6993f8915d20056fd50124437cc1fa`;
  - the first added tools merged at `f6a3e0c` (PR #80).

  So a one-tool live build is consistent with a commit from before
  `f6a3e0c`. That is consistent, not proven.

**When to roll back:** if the outside verification fails in a way that
leaves the paid tool worse than before, for example `initialize` fails
or the unpaid call returns no 402. The owner then redeploys that recorded
deployment by the dashboard's own rollback or redeploy control (TO
CONFIRM, #123, question 2), and the coordinator reruns the outside
verification, expecting one tool and the 402.

**When not to roll back:** a `recall_check` fetch failure that names its
cause is the expected evidence, not a reason to roll back. The old build
failed the same call with a bare error.
