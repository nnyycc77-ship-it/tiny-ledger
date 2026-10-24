# MCPize redeploy runbook: recall check server

The runbook for issue
[#123](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/123). One
owner action carries three changes that have merged to `main` but are not live
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
3. **The wave tool registration** (issue
   [#204](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/204)).
   The seventeen tool factory wave tools whose fetchers and API
   endpoints are already on `main` are registered on the same server
   surface, so the server lists twenty five tools: the seven above plus
   `domain_trust_check`, `ofac_sanctions_check`, `vin_decode_check`,
   `clinical_trial_check`, `fda_drug_check`, `broken_link_check`,
   `meta_tag_check`, `github_repo_check`, `app_lookup_check`,
   `exchange_rate_check`, `flood_check`, `safety_file`,
   `fda_recall_check`, `epa_screen`, `csl_screen`, `oig_screen`,
   `insider_check` and `faa_lookup` (registered in the follow up change
   for issue #210, after its own pull request merged).

This file is repo work only. Nothing here was done on the dashboard,
deployed, or paid for. Every dashboard step is the owner's, taken when the
owner chooses.

**Where the facts come from.** Facts the repo record does not hold were
asked on #123 (comment 6371817865). The coordinator answered them in
[comment 6372123142](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/123#issuecomment-6372123142),
including a live probe of the gateway at about 18:36 UTC on 2026-10-23.
The few that only the dashboard can show stay marked **TO CONFIRM AT THE
DASHBOARD**, or are left as a blank the owner fills in. None of them is
guessed.

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

- [ ] **The local server lists twenty five tools** on that commit:

  ```sh
  printf '%s\n' \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"precheck","version":"0"}}}' \
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
    | python3 -m mcp_server 2>/dev/null \
    | python3 -c 'import json,sys; r=[json.loads(l) for l in sys.stdin]; print([t["name"] for t in r[1]["result"]["tools"]])'
  ```

  Expected, in this order: `['recall_check', 'carrier_check',
  'litigation_screen', 'formd_check', 'nonprofit_check', 'awards_search',
  'pagespeed_snapshot', 'domain_trust_check', 'ofac_sanctions_check',
  'vin_decode_check', 'clinical_trial_check', 'fda_drug_check',
  'broken_link_check', 'meta_tag_check', 'github_repo_check',
  'app_lookup_check', 'exchange_rate_check', 'flood_check', 'safety_file',
  'fda_recall_check', 'epa_screen', 'csl_screen', 'oig_screen', 'insider_check',
  'faa_lookup']`.

- [ ] **The live server lists one tool** before the redeploy. The
  coordinator's probe on 2026-10-23 at about 18:36 UTC (#123, comment
  6372123142) showed `serverInfo` version `0.1.0` and one tool,
  `recall_check`. Version 0.1.0 is the server version from PR #41, before
  PRs #80 and #102 added tools. Running the outside verification below once
  before the redeploy records this baseline, so the difference is visible.

- [ ] **`mcpize.yaml` is unchanged** since the pricing commit `f6fc36c`.
  The redeploy changes code, not the price, network or recipient:

  ```sh
  git diff --stat f6fc36c77a6993f8915d20056fd50124437cc1fa origin/main -- mcpize.yaml   # expect no output
  ```

- [ ] **The owner has the environment values the new tools read ready**
  for step 3 of the owner steps. This runbook names them; their values
  are never written in this repo.
  - `EDGAR_CONTACT`: without it, `formd_check` and `insider_check`
    answer an error and fetch nothing.
  - `PAGESPEED_API_KEY`: without it, `pagespeed_snapshot` reports the
    API's 429 with quota 0.
  - `COURTLISTENER_TOKEN`: optional; without it, CourtListener applies
    its anonymous rate limit.

- [ ] **Pricing stays as it is** (coordinator, #123). `mcpize.yaml` is
  untouched, and `recall_check` stays the one priced tool at 0.05 USDC per
  call. The other tools go live unpriced unless the owner prices them as
  a separate decision. Per tool prices live in the dashboard's Payments
  tab, which is the runtime source of truth.

## Owner steps on the MCPize dashboard

The owner deployed this server from the MCPize dashboard, with auto deploy
on push off. Neither the repo record nor the MCPize publish page names the
dashboard's redeploy control or its progress screens for this server, so
those labels stay **TO CONFIRM AT THE DASHBOARD**. The owner can write
them in at the time.

| # | Owner action | Expected result |
| --- | --- | --- |
| 1 | Open the server `recallcheck` (the slug in `mcpize.yaml`) in the MCPize dashboard. | The server's page. |
| 2 | Write down the deployment shown as current, in the Rollback section below: **date or id as shown: ______**. | The deployment live before this redeploy, which serves version 0.1.0 with one tool. Whether the dashboard lists earlier deployments is TO CONFIRM AT THE DASHBOARD. |
| 3 | In the server's environment or secrets settings, set `EDGAR_CONTACT` and `PAGESPEED_API_KEY`. | Both names present. Their values are entered on the dashboard only, never in this repo or in any issue. |
| 4 | Use the server's redeploy or deploy-latest control (**label: TO CONFIRM AT THE DASHBOARD**) to deploy from the deploy commit recorded in Preconditions. | A build that finishes with a healthy status. The screen wording is TO CONFIRM AT THE DASHBOARD. |
| 5 | Leave the Payments tab as it is. | `recall_check` still priced at 0.05 USDC per call, matching `mcpize.yaml`. The other tools unpriced. |

This is one owner action, with the environment values set in the same
sitting. The coordinator then runs the outside verification below.

**The CLI route, for reference only.** This is not the recorded flow for
this server. The MCPize publish page
(https://mcpize.com/developers/publish-mcp-server, as the coordinator read
it for PR #44 and rechecked on 2026-10-23) documents `mcpize deploy`. It
prints Building server package, Uploading to MCPize cloud, Provisioning
infrastructure, Configuring HTTPS endpoint, Running health checks, then
"Deployment successful!" with the server URL and "Status: healthy".
Version bumps are `mcpize version patch|minor|major` or
`mcpize deploy --bump patch`.

## Outside verification (coordinator, from a network that reaches MCPize)

**No paid call happens here.** Every request below is unpaid. A second
paid proof call is a separate owner spend decision, made on its own and
never bundled into this verification.

**Endpoint:** `https://recallcheck.mcpize.run/mcp`, the client gateway
pinned in the program record (coordinator, #123).
`https://mcpize.com/mcp/recallcheck`, named in PR #45, is the
marketplace listing page, not the client endpoint.

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

What each step must show. The "before" column is the coordinator's live
probe on 2026-10-23 at about 18:36 UTC (#123, comment 6372123142):

| Step | Before the redeploy (observed) | After the redeploy (expected) | Fails when |
| --- | --- | --- | --- |
| `initialize` (anonymous) | HTTP 200; `serverInfo` name "hojo-recall-check via MCPize", version "0.1.0", title "Tiny Ledger"; instructions name one tool, `recall_check` | HTTP 200; `serverInfo` version "0.3.0", the server version on `main` since PR #102, under the gateway's name form | It is not 200, or the version is still 0.1.0, which means the old build is live. |
| `tools/list` | One tool, `recall_check` | Twenty five tools, in the order listed under Preconditions | Any other count or order. |
| `tools/call recall_check`, unpaid | HTTP 402 with a JSON body, not a JSON-RPC error: `x402Version` 1, one `accepts` entry with `scheme` "exact", `network` "base", `maxAmountRequired` "50000" (0.05 USDC at 6 decimals), and `payTo` equal to the `recipient` in `mcpize.yaml` | The same 402 with the same values | Any status other than 402, a different amount or network, or a `payTo` that differs from `mcpize.yaml`. |

The observed 402 body is quoted verbatim in the coordinator's comment. It
is not repeated here, because the payout address appears in one place in
this repo, `mcpize.yaml`, and the check above compares against that file.

Record the full output of the run on issue #123, and on issue #38 as
DEPLOYMENT.md asks, with the time of the run and the deploy commit.

If the owner later makes a second paid proof call, as a separate
decision, its tool result text is recorded verbatim. It is either the
Vornado report (recalls 18-136 and 18-199 for `{"product": "VH101"}`, as
the coordinator's local run on PR #121 showed) or a named failure under
the new format. Either answers the open question on #118.

## Listing copy for the twenty five tools

This copy is pasted where the dashboard takes it after the outside
verification passes, replacing the one-tool copy in
[`packaging/mcpize/LISTING.md`](../packaging/mcpize/LISTING.md). Shorten
it by cutting, never by adding. Each line paraphrases that tool's own
`tools/list` description on `main`. The server's description is the
authority, and nothing here goes beyond it.

**Title:** Hojo public records checks: sourced recall, carrier, litigation,
Form D, nonprofit, contract award, PageSpeed and public records screening
lookups

**Short description:** Twenty five tools that each return a Markdown report in
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
- `domain_trust_check`: a domain's A and MX records, its SPF and DMARC
  records and policies, and its HTTPS answer over up to five hops. No
  certificate check is made.
- `ofac_sanctions_check`: an OFAC SDN list name check, against the list
  and its aliases. A name with no match is not a clearance.
- `vin_decode_check`: the NHTSA vPIC decode of a VIN, with vPIC's own
  error text where it gives it. A decode describes the vehicle as
  manufactured, not its current condition.
- `clinical_trial_check`: a ClinicalTrials.gov study search by company,
  drug or condition, with the total count as shown. Not medical advice.
- `fda_drug_check`: openFDA drug label facts for a brand or generic
  name, read from the first returned record. Not medical advice.
- `broken_link_check`: the link targets of one page, each checked once;
  a link is dead on a final status of 400 or above, and a failed request
  is a check failure, never a dead link.
- `meta_tag_check`: one page's title, meta description and Open Graph
  tags, present with their values or missing, as shown in the page.
- `github_repo_check`: a GitHub repository's stars, license, last push
  date and archived state, keyless, as the API shows them.
- `app_lookup_check`: an App Store lookup by app name, with seller,
  rating and store link per result, and exact name matches marked.
- `exchange_rate_check`: a Frankfurter exchange rate for a currency
  pair, latest or dated, with an optional converted amount. Not a quote
  to trade at.
- `flood_check`: a FEMA flood zone screen for coordinates or a US
  street address. Screening only, not a Standard Flood Hazard
  Determination.
- `safety_file`: one vehicle's NHTSA safety ratings, recalls and
  complaints for a model year, make and model, in one file.
- `fda_recall_check`: an openFDA enforcement recall search by product,
  device or firm name, across food, device or both. An empty result is
  not a clearance.
- `epa_screen`: EPA ECHO facility compliance records by facility name
  and state. An empty search is not a finding of no violations.
- `csl_screen`: a Consolidated Screening List name screen, stating the
  list publication date and the rows screened. No match is not a
  clearance.
- `oig_screen`: an HHS OIG LEIE exclusion screen by name, against the
  complete current file. No match is not a clearance.
- `insider_check`: SEC EDGAR insider filings (Forms 3, 4 and 5) for a
  company, by CIK or by company name search. It works only when the
  server has `EDGAR_CONTACT` set; until then it answers an error.
- `faa_lookup`: an FAA aircraft registry lookup by N number, showing
  the make, model, year and registrant name as registered, from the
  daily registry archive, whose Last-Modified every report states.

`recall_check` is the one priced tool. The other twenty four are unpriced at this
redeploy (coordinator, #123), and the listing names no price for them
until the owner sets one in the Payments tab.

## Rollback

**The deployment to return to** is the one live immediately before this
redeploy. On 2026-10-23 at about 18:36 UTC it served `serverInfo` version
0.1.0 with one tool, `recall_check` (coordinator probe, #123).

- **Deployment date or id, as the dashboard shows it** (the owner fills
  this in at step 2): **______**
- **No MCPize deployment id or build commit is on record in this repo.**
  The record narrows it down:
  - the manifest arrived with PR #45 (merged 2026-10-23T03:00:23Z, merge
    commit `7ee4fef648d50468cbe6f1f846a73959273883e5`);
  - the pricing commit is `f6fc36c77a6993f8915d20056fd50124437cc1fa`;
  - version 0.1.0 predates PR #80 (`f6a3e0c`).

  So the live build is consistent with a commit between those points.
  That is consistent, not proven.
- **Whether the dashboard keeps earlier deployments and offers a
  rollback control is TO CONFIRM AT THE DASHBOARD.** If it does not, the
  way back is a redeploy of the last commit before `f6a3e0c` that carries
  the pricing block, which is `f6fc36c` or a later commit from before
  PR #80. That is the owner's choice at the time.

**When to roll back:** the outside verification shows the paid tool worse
than before. For example, `initialize` fails, or the unpaid call returns
no 402, or a 402 with a different amount or `payTo`. The coordinator then
reruns the outside verification, expecting version 0.1.0, one tool and
the 402.

**When not to roll back:** a `recall_check` fetch failure that names its
cause is the expected evidence, not a reason to roll back. The old build
failed the same call with a bare error.
