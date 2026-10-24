# `pagespeed_snapshot`: PageSpeed snapshot

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** PageSpeed Insights scores and lab metrics for up to five pages, measured at that moment.
- **Source:** Google PageSpeed Insights API v5.
- **Arguments:** `url`, `strategy`, `subject`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `www.googleapis.com`, and `PAGESPEED_API_KEY` set on the server. Without it the API answers 429 with quota 0, and that transcript is the report.
- **What it is not:** A measurement of that moment, not a permanent grade.
- **Price:** Not priced. The `pricing` block of [`mcpize.yaml`](../../mcpize.yaml) does not name this tool, and pricing it is the owner's decision (issue #147).
- **Before you pay for a call:** while the server has no `PAGESPEED_API_KEY` set, the API answers 429 with quota 0 and that transcript is the whole report, so a paid call in that state pays for the 429 transcript and no scores.

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
Sourced PageSpeed Insights snapshot from the public API (https://www.googleapis.com/pagespeedonline/v5/runPagespeed), in the fixed evidence format: each claim with its source link and the raw response directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. `url` lists the pages to measure (up to 5); optional `strategy` is mobile (default) or desktop; optional `subject` is the heading; optional `exclude` entries of the form URL=reason list a page as checked and excluded with the operator's reason. The server uses PAGESPEED_API_KEY when set; without it the API answers 429 with quota 0 and that transcript is the report. The key is never printed. A measurement of that moment, not a permanent grade. The response is the fetcher's own Markdown, the same text GET /pagespeed of the pay per call API returns for the same query; nothing is summarised, estimated, or added. A failed fetch is an error, never an empty result.
```
