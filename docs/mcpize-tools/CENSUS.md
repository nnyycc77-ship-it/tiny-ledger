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
`530f6dae61770cf5be9dacad6e3a7a6806c3595f`, by the same method:

| | Before #228 | After #228 | Refresh #252 | Refresh #265 | Refresh #272 | Refresh #280 |
| --- | --- | --- | --- | --- | --- | --- |
| Tools registered (`tool_definitions()` in `mcp_server/recall_mcp.py`) | 25 | 25 | 25 | 25 | 25 | 25 |
| Registered tools with a page in this folder | 15 | 18 | 18 | 18 | 18 | 18 |
| Registered tools named in the services catalog | 16 | 19 | 19 | 19 | 19 | 19 |
| Pages stating a route that differs from the server's dispatch | 0 | 0 | 0 | 0 | 0 | 0 |
| Pages without the 0.25 USDC shelf price line | 0 | 0 | 0 | 0 | 0 | 0 |
| Docs pages or catalog entries naming a tool that is not registered | 0 | 0 | 0 | 0 | 0 | 0 |
| Registered tools whose route is in `api/openapi.json` | 18 | 18 | 18 | 25 | 25 | 25 |

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
