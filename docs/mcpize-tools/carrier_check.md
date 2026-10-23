# `carrier_check`: FMCSA carrier check

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** The public FMCSA records for one motor carrier by USDOT number, or a Census File name search.
- **Source:** FMCSA Company Census File on DOT open data; the SAFER company snapshot; the Licensing and Insurance carrier list.
- **Arguments:** `usdot`, `name`, `subject`, `source`, `limit`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `data.transportation.gov`, `safer.fmcsa.dot.gov` and `li-public.fmcsa.dot.gov`. No key.
- **What it is not:** An empty result is not a clearance.
- **Price:** Not priced. The `pricing` block of [`mcpize.yaml`](../../mcpize.yaml) does not name this tool, and pricing it is the owner's decision (issue #147).

Every report uses the repo's fixed evidence format. Each claim has its
source link with the raw response directly beneath it, the exact query
and retrieval time are recorded, and an empty result is proven by the
complete raw response. A failed fetch is an error that names the
source, never an empty result.

## The tool's own description

This is the text the server returns for this tool in `tools/list`,
copied verbatim. The lines above are a summary of it. Where they
differ, this text is the authority.

Source: [`mcp_server/recall_mcp.py`](../../mcp_server/recall_mcp.py), `tools/list` at main `7a902e4`
```text
Sourced FMCSA carrier vetting from public United States motor carrier records, in the fixed evidence format: each claim with its source link and the raw response directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. USDOT form: `usdot` fetches the carrier's record from the FMCSA Company Census File on DOT open data (https://data.transportation.gov/resource/az4n-8mr2.json), the SAFER company snapshot (https://safer.fmcsa.dot.gov/query.asp) and the Licensing and Insurance carrier list (https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist); optional `source` limits the run to some of census, safer, li, in the order given. Name form: `name` runs a Census name search (`limit` rows, default 50); optional `exclude` entries of the form USDOT=reason list a returned carrier as checked and excluded with the operator's reason, and an exclusion naming a carrier the response does not contain is refused. Give one form, not both. Optional `subject` is the heading. The response is the fetcher's own Markdown, the same text GET /carrier of the pay per call API returns for the same query; nothing is summarised, estimated, or added. An empty result is not a clearance. A failed fetch is an error, never an empty result.
```
