# `awards_search`: Federal contract awards

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** One page of federal prime contract awards for a recipient name or NAICS codes, optionally in a date window.
- **Source:** USAspending API (spending by award).
- **Arguments:** `recipient`, `naics`, `start`, `end`, `page`, `limit`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `api.usaspending.gov`. No key.
- **What it is not:** Award Amount is the API field as returned, not a payment or revenue estimate; one page of results, not a complete history.
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
Sourced federal prime contract award search from the USAspending API (https://api.usaspending.gov/api/v2/search/spending_by_award/), in the fixed evidence format: each claim with its source link and the raw response directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. Give `recipient` (a recipient name) or `naics` (one or more NAICS codes). Optional `start` and `end` (YYYY-MM-DD, given together) set the action date window; `page` and `limit` page through the results; `exclude` entries of the form GENERATED_ID=reason list an award on the page as checked and excluded with the operator's reason, and an exclusion naming an award not on the page is refused. One page of results as returned; Award Amount is the API field as returned, not a payment or revenue estimate. The response is the fetcher's own Markdown, the same text GET /awards of the pay per call API returns for the same query; nothing is summarised, estimated, or added. A failed fetch is an error, never an empty result.
```
