# MCP tool census, 2026-10-24 (issue #228)

A dated record of the docs against the tools the MCP server registers. It
covers two census surfaces: this folder (one page per tool) and the tool
entries in [`docs/services-catalog.md`](../services-catalog.md). Run the
script at the end from the repository root to reproduce every count.

## Counts

Counted on main `dc077ef`, before the PR for #228, and on that PR's branch
after it. Refreshed for issue #252 on main
`80e646427a625346c0dce4480412fa41c12549a7`, after the `faa_lookup`
registration (issue #210, PR #213) and the registry listing drift check
(issue #246), by running the script at the end of this file, unchanged,
from the repository root of that tree. Refreshed again for issue #265 on
main `af30eb423ef090bfd2adaff7db44ae4bfb4d50e5`, after PR #253 added the
seven missing routes to `api/openapi.json`, by the same method.
Refreshed again for issue #272 on main
`e5035f36a116feddc6243787cfacf951705b9067`, by the same method.
Refreshed again for issue #280 on main
`530f6dae61770cf5be9dacad6e3a7a6806c3595f`, by the same method.
Refreshed again for issue #289 on main
`96a347f8b26dde768d020fcf1c2d65264e1a5fae`, by the same method.
Refreshed again for issue #297 on main
`2b86c90199ede1fbf3b31a0d39d6f9a4d3293e65`, by the same method.
Refreshed again for issue #304 on main
`65dde3693bf3aeb601e783c78dcfc36472b895d8`, by the same method.
Refreshed again for issue #311 on main
`44507b55d1b65d260471c6180689194f5cf40d46`, by the same method:
Refreshed again for issue #384 on main
`9ad0a24b04e1f99e814113eee1ef04da9a3be5b9`, by the same method:

| | Before #228 | After #228 | Refresh #252 | Refresh #265 | Refresh #272 | Refresh #280 | Refresh #289 | Refresh #297 | Refresh #304 | Refresh #311 | Refresh #384 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tools registered (`tool_definitions()` in `mcp_server/recall_mcp.py`) | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |
| Registered tools with a page in this folder | 15 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 |
| Registered tools named in the services catalog | 16 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 |
| Pages stating a route that differs from the server's dispatch | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Pages without the 0.25 USDC shelf price line | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Docs pages or catalog entries naming a tool that is not registered | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 |
| Registered tools whose route is in `api/openapi.json` | 18 | 18 | 18 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |

One count moved at the #265 refresh: the `api/openapi.json` row, from
18 to 25. PR #253 (issue #243) added the seven routes the earlier
censuses reported missing, `/domain`, `/ofac`, `/github`, `/flood`,
`/fda`, `/oig` and `/insider`, so every registered tool's route now
stands in `api/openapi.json`, which carries 26 paths in all (the twenty
five tool routes plus `/`).

No count moved at the #272 refresh. Between the #265 pin and this one
the merges were PR #261 (api smoke coverage census), PR #266 (suite
census), PR #267 (the #265 census refresh itself) and PR #268 (OFAC
normalise test coverage, issue #264); none of them touched a census
surface, and the recomputation on the pinned commit, not the merge
history, is the proof.

No count moved at the #280 refresh either. Between the #272 pin and
this one the merges were PR #273 (api smoke census pin), PR #274
(pricing drift pin), PR #275 (the #272 census refresh itself) and
PR #276 (an offline OpenAPI alignment test for the seven routes, issue
#263, which reads `api/openapi.json` and changes nothing in it); none
of them touched a census surface.

No count moved at the #289 refresh either. Between the #280 pin and
this one the merges were PR #281 (pricing drift pin, issue #278),
PR #282 (api smoke census pin, issue #279), PR #283 (suite census) and
PR #284 (the #280 census refresh itself); none of them touched a
census surface.

No count moved at the #297 refresh either. Between the #289 pin and
this one the merges were PR #290 (pricing drift pin, issue #287),
PR #291 (api smoke census pin, issue #288), PR #292 (the #289 census
refresh itself) and PR #293 (suite census); none of them touched a
census surface.

No count moved at the #304 refresh either. Between the #297 pin and
this one the merges were PR #285 (suite census), PR #298 (api smoke
census pin, issue #295), PR #299 (pricing drift pin, issue #294) and
PR #300 (the #297 census refresh itself); none of them touched a
census surface.

One count moved at the #384 refresh: the row for docs pages or
catalog entries naming a tool that is not registered, from 0 to 10.
The ten wave 3 tools (`disaster_history_check`, `earthquake_check`,
`weather_alert_check`, `address_geocode_check`, `bank_check`,
`npi_check`, `wallet_check`, `email_check`, `uk_sanctions_check` and
`upc_lookup`) each merged with a page in this folder (PRs #333,
#339, #325, #336, #328, #335, #340, #341, #346 and #345, in the
order the tools are listed in parent issue #305) but none of them is
registered in `mcp_server/recall_mcp.py`, because MCP registration
is the shared wave end step and is still outstanding, the same
state the wave 3 completion audit on issue #355 recorded. Every
other count stands: no tool was registered or dropped, no
registered tool gained or lost a page or a catalog entry, and
`api/openapi.json` still names every registered route (25 of 25)
while carrying 36 paths in all, the 25 registered routes, the ten
wave 3 routes and `/`; PR #374, the merge this refresh is pinned
to, added the last three wave 3 entries (`/weather`, `/npi`,
`/wallet`) without moving the registered route row. The remaining
merges between the #311 pin and this one (PRs #313, #314, #315,
#316, #347, #348, #349, #352, #353, #356, #367, #372, #373, #377
and #379: suite censuses, smoke and pricing pins, research and the
census guard test) touched no census surface beyond the wave 3
pages named above, and the recomputation on the pinned commit, not
the merge history, is the proof.

No count moved at the #311 refresh either. Between the #304 pin and
this one the merges were PR #306 (api smoke census pin, issue #303),
PR #307 (pricing drift pin, issue #302) and PR #308 (the #304 census
refresh itself); none of them touched a census surface.

## Drift found and fixed by the PR for #228

- **Stale registration status, 17 places.** The places were all 15 wave
  pages in this folder, [`docs/ofac-sdn-check.md`](../ofac-sdn-check.md),
  and the catalog's Part 5 introduction (with its "How to order" line).
  They said the tools were "not on the MCP server yet". The server on
  main registers all of them: PR #208 (issue #204) added the wave tools,
  and PR #213 (issue #210) added `faa_lookup`. Each place now says the
  tool is registered and that going live still waits on the owner
  redeploy step.
- **Three registered wave 1 tools had no page in this folder and no
  catalog entry:** `domain_trust_check` (#159), `ofac_sanctions_check`
  (#160, whose full page stays at `docs/ofac-sdn-check.md`) and
  `app_lookup_check` (#167). Each now has a page here and an entry in
  catalog Part 5, Wave 1.

## Refresh notes (issue #384)

- One count moved; the Refresh #384 column is the #311 column with
  the unregistered in docs row at 10, proven by the reproduce
  script's output on the pinned commit.
- The ten names the script reports are the wave 3 tools listed in
  the counts section: each has a page in this folder and a route in
  `api/openapi.json`, and none is registered on the MCP server yet.
  Registration is the wave end step that closes the row back to 0;
  it is recorded under Left open below.
- The left open item from before stands as it was left: the seven
  original tools still have no page in this folder.

## Refresh notes (issue #311)

- No count moved; the Refresh #311 column repeats the #304 figures,
  proven by the reproduce script's output on the pinned commit.
- The left open items stand as they were left: the seven original
  tools still have no page in this folder.

## Refresh notes (issue #304)

- No count moved; the Refresh #304 column repeats the #297 figures,
  proven by the reproduce script's output on the pinned commit.
- The left open items stand as they were left: the seven original
  tools still have no page in this folder.

## Refresh notes (issue #297)

- No count moved; the Refresh #297 column repeats the #289 figures,
  proven by the reproduce script's output on the pinned commit.
- The left open items stand as they were left: the seven original
  tools still have no page in this folder.

## Refresh notes (issue #289)

- No count moved; the Refresh #289 column repeats the #280 figures,
  proven by the reproduce script's output on the pinned commit.
- The left open items stand as they were left: the seven original
  tools still have no page in this folder.

## Refresh notes (issue #280)

- No count moved; the Refresh #280 column repeats the #272 figures,
  proven by the reproduce script's output on the pinned commit.
- The seven original tools listed under Left open still have no page
  in this folder; that is the only item left open on this census.

## Refresh notes (issue #272)

- No count moved; the Refresh #272 column repeats the #265 figures
  because the tree's census surfaces are byte identical in effect, as
  the reproduce script's output on the pinned commit shows.
- The seven original tools listed under Left open still have no page
  in this folder; that is the only item left open on this census.

## Refresh notes (issue #265)

- The only accounting change since the #252 refresh is the seven
  OpenAPI routes named above. No tool was registered or dropped, no
  page or catalog entry was added or removed, and the seven original
  tools listed under Left open still have no page in this folder.
- The `api/openapi.json` item under Left open is closed by PR #253 and
  is struck from that list below; the earlier census text that reported
  it stays in the #228 section, as the dated record it is.

## Refresh notes (issue #252)

- The census file itself stands where the PR for #228 put it, in this
  folder; the path named in issue #252 (`docs/mcp-tool-census-2026-10-24.md`)
  does not exist in the tree, and no file was moved for this refresh.
- `faa_lookup` is inside every count above: it is registered (the last
  of the twenty five, in `tool_definitions()` order), it has a page in
  this folder, it is named in the services catalog, and its route
  `/faa` is in `api/openapi.json`.
- Nothing in this refresh is taken from outside the tree: every line
  reproduces from the script below on the pinned commit.

## Left open, on purpose

- **The seven original tools have no page in this folder:**
  `recall_check`, `carrier_check`, `litigation_screen`, `formd_check`,
  `nonprofit_check`, `awards_search` and `pagespeed_snapshot`. Six of them
  are also missing from the catalog; `recall_check` has catalog Part 4.
  Their pages, and an index for this folder, are the docs part of issue
  #147 (H2, branch `h2-mcpize-tool-shelf`), which also carries their
  pricing under the owner ruling on #147. They are not duplicated here.
- **Ten wave 3 tools have a page in this folder and a route in
  `api/openapi.json` but are not registered on the MCP server:**
  `disaster_history_check`, `earthquake_check`,
  `weather_alert_check`, `address_geocode_check`, `bank_check`,
  `npi_check`, `wallet_check`, `email_check`, `uk_sanctions_check`
  and `upc_lookup`. Registration is the shared wave end step; the
  audit on issue #355 recorded the same outstanding step. When it
  lands, the unregistered in docs row above returns to 0 and the
  registered count rises to 35. Recorded at the #384 refresh.
- **Seven registered tools' routes were missing from `api/openapi.json`:**
  `/domain`, `/ofac`, `/github`, `/flood`, `/fda`, `/oig` and `/insider`.
  That file is not a docs file, and issue #228 limits fixes to docs, so
  this was reported for a separate task. Closed since: PR #253 (issue
  #243) added all seven routes, as the Refresh #265 column above shows.
  **Follow-up:** issue #243 added all seven, so `api/openapi.json` now
  names every registered route; the reproduce script below reports 25.

## Reproduce

```sh
python3 - <<'EOF'
import json, re, sys
from pathlib import Path
sys.path[:0] = ["mcp_server", "."]
import recall_mcp as m
from api import endpoints
names = [t["name"] for t in m.tool_definitions("0x" + "0" * 40)]  # placeholder wallet: descriptions only
src = Path("mcp_server/recall_mcp.py").read_text(encoding="utf-8")
dispatch = {getattr(m, c): f for c, f in
            re.findall(r"if name == ([A-Z_]+):\s*\n\s*return call_endpoint\(endpoints\.([a-z_]+),", src)}
route = {f.__name__: p for p, f in endpoints.ROUTES.items()}
openapi = set(json.loads(Path("api/openapi.json").read_text(encoding="utf-8"))["paths"])
catalog = Path("docs/services-catalog.md").read_text(encoding="utf-8")
pages = {p.stem: p.read_text(encoding="utf-8") for p in Path("docs/mcpize-tools").glob("*.md")
         if p.stem != "CENSUS"}
rows = [(n, "/recall" if n == "recall_check" else route.get(dispatch.get(n))) for n in names]
print("registered", len(names))
print("with a page", sum(n in pages for n, _ in rows))
print("in the catalog", sum(("`%s`" % n) in catalog for n, _ in rows))
print("page route differs", [n for n, r in rows if n in pages and ("`GET %s" % r) not in pages[n]])
print("page without 0.25 USDC", [n for n, _ in rows if n in pages and "0.25 USDC" not in pages[n]])
print("unregistered in docs", sorted((set(pages) | set(re.findall(r"^#### `([a-z_]+)`", catalog, re.M)))
                                     - set(names)))
print("route in openapi.json", sum(r in openapi for _, r in rows), [r for _, r in rows if r not in openapi])
print("no page", [n for n, _ in rows if n not in pages])
EOF
```
