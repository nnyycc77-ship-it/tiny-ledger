# `recall_check`: Recall check

One tool of the recall check MCP server (`mcp_server/`). Its listing for
the MCPize redeploy is in the
[redeploy runbook](../mcpize-redeploy-runbook.md#listing-copy-for-the-seven-tools).

- **What it answers:** Whether a consumer product (by name) or a vehicle (by make, model and year) appears in the public United States recall records, with every record shown as returned.
- **Source:** CPSC SaferProducts recall API (product form); NHTSA recalls API (vehicle form).
- **Arguments:** `product`, `exact_name`, `near`, `make`, `model`, `year`, `exclude`.
- **Needs on the server:** Outbound HTTPS to `www.saferproducts.gov` and `api.nhtsa.gov`, and `curl` on the host for the product form. No key.
- **What it is not:** An empty result is not a safety clearance. No product or vehicle is inspected.
- **Price:** 0.05 USDC per call, x402 on Base, from the `pricing` block of [`mcpize.yaml`](../../mcpize.yaml), which the owner set.

Every report uses the repo's fixed evidence format. Each claim has its
source link with the raw response directly beneath it, the exact query
and retrieval time are recorded, and an empty result is proven by the
complete raw response. A failed fetch is an error that names the
source, never an empty result.

## The tool's own description

This is the text the server returns for this tool in `tools/list`,
copied verbatim. The lines above are a summary of it. Where they
differ, this text is the authority. It is shown with no payout wallet configured, and a configured wallet adds one sentence naming it.

Source: [`mcp_server/recall_mcp.py`](../../mcp_server/recall_mcp.py), `tools/list` at main `7a902e4`
```text
Sourced recall check from public United States recall records, in the fixed evidence format: each claim with its source link and the raw excerpt directly beneath it, the exact query and UTC retrieval time recorded, and an empty result proven by the complete raw response. Product form: `product` searches the CPSC SaferProducts recall API (https://www.saferproducts.gov/RestWebServices/Recall); optional `exact_name` marks records whose product names do not equal it as checked and excluded, and `near` (needs `exact_name`) adds broader searches checked the same way. Vehicle form: `make`, `model` and `year` search the NHTSA recalls API (https://api.nhtsa.gov/recalls/recallsByVehicle); optional `exclude` entries of the form CAMPAIGN=reason list a returned campaign as checked and excluded with the operator's reason. Give one form, not both. The response is the fetchers' own Markdown; nothing is summarised, estimated, or added. An empty result is not a safety clearance. A failed fetch is an error, never an empty result.
```
