# `litigation_screen`: Federal litigation screen

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** Federal court dockets that name a party, from the public CourtListener RECAP docket index.
- **Source:** CourtListener RECAP docket search API.
- **Arguments:** `party`, `subject`, `filed_after`, `order_by`, `list`, `docket_details`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `www.courtlistener.com`. `COURTLISTENER_TOKEN` is optional (it lifts the anonymous rate limit).
- **What it is not:** Index level only and not a legal opinion; an empty result is not proof of no litigation.
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
Sourced federal litigation screen from the public CourtListener RECAP docket index (https://www.courtlistener.com/api/rest/v4/search/), in the fixed evidence format: each claim with its source link and the raw response directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. `party` lists the party name variants to search as party:("variant") docket queries; the first is the exact name whose first page results are listed (`list` rows, default 10), the others are counted. Optional `filed_after` (YYYY-MM-DD, default five years before today) and `order_by` (default dateFiled desc) set the window and order; `docket_details` true also fetches each listed docket's record; `exclude` entries of the form DOCKET_ID=reason list a returned docket as checked and excluded with the operator's reason, and an exclusion naming a docket the response does not contain is refused. Optional `subject` is the heading. Index-level only; not a legal opinion. The response is the fetcher's own Markdown, the same text GET /litigation of the pay per call API returns for the same query; nothing is summarised, estimated, or added. An empty result is not proof of no litigation. A failed fetch is an error, never an empty result.
```
