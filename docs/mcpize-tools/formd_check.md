# `formd_check`: SEC Form D filings

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** The Form D filings a company has made, by CIK or by an EDGAR company name search, as EDGAR indexes them.
- **Source:** SEC EDGAR submissions API and EDGAR company search.
- **Arguments:** `cik`, `issuer`, `max_filings`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `data.sec.gov` and `www.sec.gov`, and `EDGAR_CONTACT` set on the server. Without `EDGAR_CONTACT` the tool answers an error and fetches nothing.
- **What it is not:** A listing of filings as indexed, not an analysis of any offering.
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
Sourced SEC EDGAR Form D filing listing for a company, in the fixed evidence format: each claim with its source link and the raw response directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. Give `cik` (the company's Central Index Key, fetched from the EDGAR submissions API, https://data.sec.gov/submissions/CIK{cik10}.json) or `issuer` (an EDGAR company name search, https://www.sec.gov/cgi-bin/browse-edgar), not both. Optional `max_filings` (default 10) limits how many Form D filings are read; optional `exclude` entries of the form ACCESSION=reason list a filing as checked and excluded with the operator's reason, and an exclusion naming a filing the response does not contain is refused. The server must have EDGAR_CONTACT set (EDGAR fair access needs the operator's contact in the User-Agent); while it is unset the tool answers an error and fetches nothing. A listing of filings as indexed, not an analysis of any offering. The response is the fetcher's own Markdown, the same text GET /formd of the pay per call API returns for the same query; nothing is summarised, estimated, or added. A failed fetch is an error, never an empty result.
```
