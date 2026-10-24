# `epa_screen`: EPA facility compliance screen

A tool factory wave 2 tool (issue #178). The fetcher is
[`tools/epa_screen.py`](../../tools/epa_screen.py), and it is served as
`GET /epa` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is registered on the MCP server: the server on main lists it
(`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
PR #208 (issue #204), the shared surface step the #158 ruling called for.
Going live still waits on the owner redeploy step.

- **What it answers:** Does this facility show EPA violations or significant noncompliance? It answers as the EPA ECHO facility search states it, quoting three fields of each facility row as shown: `FacComplianceStatus`, `FacSNCFlg` (significant noncompliance flag) and `FacQtrsWithNC`.
- **Source:** the EPA ECHO facility search web service on `echodata.epa.gov`, keyless, in two steps:
  - `echo_rest_services.get_facilities?output=JSON&p_fn=<name>[&p_cty=<city>]&p_st=<state>` answers a summary with QueryRows and a QueryID;
  - `echo_rest_services.get_qid?output=JSON&qid=<QueryID>` answers the facility rows.

  These are the calls the coordinator ran live on #178. ECHO's web services index page (`https://echo.epa.gov/tools/web-services`) lists the Facility Search service by name. Its parameter tables load separately and could not be captured, so no parameter is documented from them.
- **Arguments:** `name` and `state` (two letters), optional `city`, and optional `registry_id`. A RegistryID selects that facility's row from the search results; it does not replace the search, because no single-facility route is verified (see below).
- **Needs on the server:** Outbound HTTPS to `echodata.epa.gov`. No key, no environment value.
- **What it is not:** A compliance finding of this service. The status fields are ECHO's, as shown, and the tool does not total, score or judge them. A search can return several facility records with similar names. Which one is meant is the caller's call.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

Every report uses the repo's fixed evidence format. The answer comes
first, then each call's source link with its complete raw response
directly beneath it, with the exact query and retrieval time recorded.

## Empty results and failures

- **Zero rows is not "clean".** A summary with QueryRows `"0"` is an empty result, proven by its transcript. It shows only that the service answered zero rows for those parameters. The coordinator's captures show an invalid state code (`p_st=ZZ`) answering with the same zero-row shape, so the report never calls an empty result a finding that a facility is free of violations.
- **Failures are checked by status first, then the body.** Any status other than 200 is a source failure. So is a body whose `Results` carries an `Error`: the captures show ECHO answering HTTP 200 with an Error body ("Queryset Limit would be exceeded…"). A source failure prints no report. The CLI exits 2, the API answers 502, and the failure names the step, the query, the status and the body.
- **No single-facility route is verified.** In the captures, the Detailed Facility Report service (`get_dfr`) answered HTTP 500 for a real RegistryID. `get_facilities` with `p_id` behaved as an unfiltered search and answered that Error body. Neither is used.

## What a report shows, on a recorded response

The tool's answer for the recorded Baytown search, filtered to one
RegistryID. The claims are the tool's own lines for those responses (the
offline tests check these exact lines), with the recorded facility rows
printed directly beneath the source link.

- `rows filtered to RegistryID 110000463178`
- `- BAYTOWN OLEFINS PLANT (RegistryID 110000463178, BAYTOWN, TX): FacComplianceStatus "Significant Violation"; FacSNCFlg "Y"; FacQtrsWithNC "12"`

Source: https://echodata.epa.gov/echo/echo_rest_services.get_qid?output=JSON&qid=126, captured keyless by the coordinator under Option B on issue #178 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/178#issuecomment-6380456438)), retrieved 2026-10-24, about 05:10 to 05:11 UTC (response Date header: Sat, 24 Oct 2026 05:10:32 GMT); transcript 7430 bytes, sha256 `1e08020c9302c6fc88789f9739b8b7565081ae3c9c96a065355f3249c74623eb`; saved byte for byte as [`tools/tests/fixtures/epa-echo/qid-baytown-olefins.http`](../../tools/tests/fixtures/epa-echo/qid-baytown-olefins.http), with the search summary that named QueryID 126 beside it (`search-baytown-olefins.http`, sha256 `dbfe83067e4cadcf9d2e746b4becfdb66cf74a22f2380bf4249561cfbe4b51da`). The transcript is curl output with CRLF line ends and the proxy's CONNECT reply first. It is linked rather than pasted here, so its line ends stay as recorded.

All eight recorded responses are in [`tools/tests/fixtures/epa-echo/`](../../tools/tests/fixtures/epa-echo/), with their provenance:
- the Baytown search and rows (four records, one shown with a significant violation);
- the Bissonnet search and rows ("No Violation Identified");
- an empty search;
- the `p_st=ZZ` search;
- the `get_dfr` 500;
- the HTTP 200 Error answer.

## Not verified here

This container cannot reach `echodata.epa.gov` (the proxy refuses the
connection), so no live run was made from it. The tool's behaviour is
tested offline on the recorded responses above. The coordinator's live
smoke run at review is the live check.
