# `nonprofit_check`: Nonprofit diligence

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** A nonprofit's record and the Form 990 figures the ProPublica Nonprofit Explorer API extracts, by name search or EIN.
- **Source:** ProPublica Nonprofit Explorer API v2.
- **Arguments:** `name`, `ein`, `subject`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `projects.propublica.org`. No key.
- **What it is not:** The figures are the API's extracted values as shown, not an audit.
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
Sourced nonprofit diligence from the ProPublica Nonprofit Explorer API (https://projects.propublica.org/nonprofits/api/v2), in the fixed evidence format: each claim with its source link and the raw response directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. Give `name` (an organization search), `ein` (one or more EINs, each organization's record and Form 990 figures as the API extracts them), or both. Optional `subject` is the heading; optional `exclude` entries of the form EIN=reason (with `name`) list a search result as checked and excluded with the operator's reason, and an exclusion naming an organization the search did not return is refused. The figures are the API's extracted Form 990 values as shown, not an audit. The response is the fetcher's own Markdown, the same text GET /nonprofit of the pay per call API returns for the same query; nothing is summarised, estimated, or added. A failed fetch is an error, never an empty result.
```
