# MCP tool census, 2026-10-24 (issue #228)

A dated record of the docs against the tools the MCP server registers. It
covers two census surfaces: this folder (one page per tool) and the tool
entries in [`docs/services-catalog.md`](../services-catalog.md). Run the
script at the end from the repository root to reproduce every count.

## Counts

Counted on main `dc077ef`, before the PR for #228, and on that PR's branch
after it:

| | Before | After |
| --- | --- | --- |
| Tools registered (`tool_definitions()` in `mcp_server/recall_mcp.py`) | 25 | 25 |
| Registered tools with a page in this folder | 15 | 18 |
| Registered tools named in the services catalog | 16 | 19 |
| Pages stating a route that differs from the server's dispatch | 0 | 0 |
| Pages without the 0.25 USDC shelf price line | 0 | 0 |
| Docs pages or catalog entries naming a tool that is not registered | 0 | 0 |
| Registered tools whose route is in `api/openapi.json` | 18 | 18 |

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

## Left open, on purpose

- **The seven original tools have no page in this folder:**
  `recall_check`, `carrier_check`, `litigation_screen`, `formd_check`,
  `nonprofit_check`, `awards_search` and `pagespeed_snapshot`. Six of them
  are also missing from the catalog; `recall_check` has catalog Part 4.
  Their pages, and an index for this folder, are the docs part of issue
  #147 (H2, branch `h2-mcpize-tool-shelf`), which also carries their
  pricing under the owner ruling on #147. They are not duplicated here.
- **Seven registered tools' routes are missing from `api/openapi.json`:**
  `/domain`, `/ofac`, `/github`, `/flood`, `/fda`, `/oig` and `/insider`.
  That file is not a docs file, and issue #228 limits fixes to docs, so
  this is reported for a separate task.

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
