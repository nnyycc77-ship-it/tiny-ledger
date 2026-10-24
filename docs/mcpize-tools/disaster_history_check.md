# `disaster_history_check`: FEMA disaster declarations

A tool factory wave 3 tool (issue #312, parent #305). The fetcher is
[`tools/disaster_history_check.py`](../../tools/disaster_history_check.py),
and it is served as `GET /disaster` by the pay per call API
([`api/endpoints.py`](../../api/endpoints.py)). Following the #175 ruling
for wave tools, as the coordinator ruled on #312, this PR does not
register it on the MCP server. That is a later shared surface step, and
going live waits on the owner redeploy step.

- **What it answers:** Which FEMA disaster declarations the public OpenFEMA API records for one US state, or for one designated area (county) in it, newest first. For each disaster it gives the disaster number, the declaration type, the incident type and the declaration date, all as shown, with the designated areas named in the rows returned.
- **Source:** OpenFEMA API v2, `DisasterDeclarationsSummaries`, `https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=state eq '<ST>'[ and designatedArea eq '<area>']&$orderby=declarationDate desc&$top=<limit>&$count=true`, form encoded. Keyless. The dataset page is https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2 and the API page is https://www.fema.gov/about/openfema/api.
- **Arguments:** `state`, the two letter code as FEMA records it. Optional `county`, the exact `designatedArea` as FEMA writes it, for example `Kent (County)`. Optional `limit`, the rows to ask for, 1 to 1000, default 50.
- **Needs on the server:** Outbound HTTPS to `www.fema.gov`. No key, no environment value.
- **What it is not:** A risk assessment of any place. The declarations are FEMA's records as shown.
  - **Rows are not disasters.** One disaster appears once per designated area, so the report counts distinct `disasterNumber` values.
  - **Totals are stated only when requested.** FEMA's total of matching rows is stated only when the response shows `$count=true` was requested; without it the API reports a count of 0.
  - **Counties match exactly.** A county is matched as the exact `designatedArea` string. Some carry suffixes, for example `Newport (County)(in PMSA 2480,6480)`. An empty county result says only that no row has that exact string, never that the county had no disasters.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price, and `mcpize.yaml` is untouched.

Every report uses the repo's fixed evidence format. Each claim has its
source link with the raw response directly beneath it, the exact query
and retrieval time are recorded, and an empty result is proven by the
complete raw response.

**Fail closed.** These all stop with no report, and the answer is unknown, never a negative claim:
- a failed or timed out fetch;
- any status other than 200 (the recorded malformed query answers 400);
- a body not in the recorded shape.

## What a report shows, on a recorded response

The claims are the tool's own lines for this body (the offline tests check these exact lines), with the recorded body printed directly beneath the source link.

- `QUERY: $filter "state eq 'RI'", $top 5: 5 rows returned (...). FEMA's total of matching rows (metadata count, $count=true) as shown: 123. More rows match than this response returns; the disasters below are those in the 5 rows returned, not the full history.`
- `DISASTERS: 2 distinct disasterNumber values among the 5 rows returned (one disaster appears once per designated area, so rows are not disasters):`
- `- disasterNumber 4766 (femaDeclarationString as shown: DR-4766-RI): declarationType DR, incidentType "Severe Storm", declarationDate 2024-03-20T00:00:00.000Z, declarationTitle "SEVERE STORMS AND FLOODING"`
- `- disasterNumber 4765 (femaDeclarationString as shown: DR-4765-RI): declarationType DR, incidentType "Severe Storm", declarationDate 2024-03-20T00:00:00.000Z, declarationTitle "SEVERE STORM AND FLOODING"`

Source: https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=state+eq+%27RI%27&$orderby=declarationDate+desc&$top=5&$count=true, captured by the coordinator under Option B on issue #312 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/312#issuecomment-6384043847)), retrieved 2026-10-24, about 12:09 to 12:11 UTC, HTTP 200, 5050 bytes, sha256 `753b858b0046f7ee94d3894b9b861a065add47956ab9eba5719ed8a69248603c`; saved unmodified as [`tools/tests/fixtures/openfema/state-RI-top5-count.json`](../../tools/tests/fixtures/openfema/state-RI-top5-count.json)
```json
{"metadata": {"skip":0,"select":null,"rundate":"2026-10-24T12:10:33.213Z","top":5,"filter":"state eq 'RI'","format":"json","metadata":true,"orderby":"declarationDate DESC","entityname":"DisasterDeclarationsSummaries","version":"v2","url":"/api/open/v2/DisasterDeclarationsSummaries?$filter=state+eq+%27RI%27&$orderby=declarationDate+desc&$top=5&$count=true","count":123}, "DisasterDeclarationsSummaries": [{"femaDeclarationString":"DR-4766-RI","disasterNumber":4766,"state":"RI","declarationType":"DR","declarationDate":"2024-03-20T00:00:00.000Z","fyDeclared":2024,"incidentType":"Severe Storm","declarationTitle":"SEVERE STORMS AND FLOODING","ihProgramDeclared":true,"iaProgramDeclared":false,"paProgramDeclared":true,"hmProgramDeclared":true,"incidentBeginDate":"2024-01-09T00:00:00.000Z","incidentEndDate":"2024-01-13T00:00:00.000Z","disasterCloseoutDate":null,"tribalRequest":false,"fipsStateCode":"44","fipsCountyCode":"003","placeCode":"99003","designatedArea":"Kent (County)","declarationRequestNumber":"24021","declarationRequestDate":"2024-03-06T00:00:00.000Z","lastIAFilingDate":"2024-05-20T00:00:00.000Z","incidentId":"2024010901","region":1,"designatedIncidentTypes":"W","lastRefresh":"2026-10-05T11:26:24.661Z","hash":"aaca930b5b42beeab035ea411d844457bf064fa1","id":"63a40101-46c2-43ab-8da9-4fb9f3ce1fb8"},{"femaDeclarationString":"DR-4766-RI","disasterNumber":4766,"state":"RI","declarationType":"DR","declarationDate":"2024-03-20T00:00:00.000Z","fyDeclared":2024,"incidentType":"Severe Storm","declarationTitle":"SEVERE STORMS AND FLOODING","ihProgramDeclared":false,"iaProgramDeclared":false,"paProgramDeclared":true,"hmProgramDeclared":true,"incidentBeginDate":"2024-01-09T00:00:00.000Z","incidentEndDate":"2024-01-13T00:00:00.000Z","disasterCloseoutDate":null,"tribalRequest":false,"fipsStateCode":"44","fipsCountyCode":"005","placeCode":"99005","designatedArea":"Newport (County)(in PMSA 2480,6480)","declarationRequestNumber":"24021","declarationRequestDate":"2024-03-06T00:00:00.000Z","lastIAFilingDate":"2024-05-20T00:00:00.000Z","incidentId":"2024010901","region":1,"designatedIncidentTypes":"W","lastRefresh":"2026-10-05T11:26:24.661Z","hash":"2654f373b8a035c6102d8d5b72e7d4318ba64ef7","id":"a68b22f9-282f-4574-a1e1-43b89559ea3b"},{"femaDeclarationString":"DR-4766-RI","disasterNumber":4766,"state":"RI","declarationType":"DR","declarationDate":"2024-03-20T00:00:00.000Z","fyDeclared":2024,"incidentType":"Severe Storm","declarationTitle":"SEVERE STORMS AND FLOODING","ihProgramDeclared":true,"iaProgramDeclared":false,"paProgramDeclared":false,"hmProgramDeclared":true,"incidentBeginDate":"2024-01-09T00:00:00.000Z","incidentEndDate":"2024-01-13T00:00:00.000Z","disasterCloseoutDate":null,"tribalRequest":false,"fipsStateCode":"44","fipsCountyCode":"007","placeCode":"99007","designatedArea":"Providence (County)(in PMSA 6060,6480)","declarationRequestNumber":"24021","declarationRequestDate":"2024-03-06T00:00:00.000Z","lastIAFilingDate":"2024-05-20T00:00:00.000Z","incidentId":"2024010901","region":1,"designatedIncidentTypes":"W","lastRefresh":"2026-10-05T11:26:24.661Z","hash":"05402e22209bb14f314f55f3fe158cd9120beac6","id":"a58272b3-f746-4aaf-b7ab-03db11718dc4"},{"femaDeclarationString":"DR-4766-RI","disasterNumber":4766,"state":"RI","declarationType":"DR","declarationDate":"2024-03-20T00:00:00.000Z","fyDeclared":2024,"incidentType":"Severe Storm","declarationTitle":"SEVERE STORMS AND FLOODING","ihProgramDeclared":true,"iaProgramDeclared":false,"paProgramDeclared":true,"hmProgramDeclared":true,"incidentBeginDate":"2024-01-09T00:00:00.000Z","incidentEndDate":"2024-01-13T00:00:00.000Z","disasterCloseoutDate":null,"tribalRequest":false,"fipsStateCode":"44","fipsCountyCode":"009","placeCode":"99009","designatedArea":"Washington (County)(in (P)MSA 5520,6480)","declarationRequestNumber":"24021","declarationRequestDate":"2024-03-06T00:00:00.000Z","lastIAFilingDate":"2024-05-20T00:00:00.000Z","incidentId":"2024010901","region":1,"designatedIncidentTypes":"W","lastRefresh":"2026-10-05T11:26:24.661Z","hash":"439140e6d6c4bd56950563493ba7701d892e17fe","id":"ecaff529-69cb-4343-a246-35183b07740d"},{"femaDeclarationString":"DR-4765-RI","disasterNumber":4765,"state":"RI","declarationType":"DR","declarationDate":"2024-03-20T00:00:00.000Z","fyDeclared":2024,"incidentType":"Severe Storm","declarationTitle":"SEVERE STORM AND FLOODING","ihProgramDeclared":true,"iaProgramDeclared":false,"paProgramDeclared":false,"hmProgramDeclared":true,"incidentBeginDate":"2023-12-17T00:00:00.000Z","incidentEndDate":"2023-12-19T00:00:00.000Z","disasterCloseoutDate":null,"tribalRequest":false,"fipsStateCode":"44","fipsCountyCode":"003","placeCode":"99003","designatedArea":"Kent (County)","declarationRequestNumber":"24020","declarationRequestDate":"2024-03-07T00:00:00.000Z","lastIAFilingDate":"2024-05-20T00:00:00.000Z","incidentId":"2023121901","region":1,"designatedIncidentTypes":"F,W","lastRefresh":"2026-10-05T11:26:24.661Z","hash":"8678840480c475070ee68dccfa2b5547d777db59","id":"1cf7d35b-42e7-4581-ac2f-621f8f4d7365"}]}
```

## An empty result, on a recorded response

- `NO ROWS: the DisasterDeclarationsSummaries array in the response is empty for this exact filter. This says only that no declaration row has state RI and designatedArea exactly "Nosuch (County)"; ...`

Source: https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$filter=state+eq+%27RI%27+and+designatedArea+eq+%27Nosuch+%28County%29%27&$top=5, captured by the coordinator under Option B on issue #312 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/312#issuecomment-6384044365)), retrieved 2026-10-24, about 12:09 to 12:11 UTC, HTTP 200, 434 bytes, sha256 `06d17ee862ea601526b2def37d1d4db170d1c9a3986e23ad5bf6b2f61140b60c`; saved unmodified as [`tools/tests/fixtures/openfema/county-RI-Nosuch-top5.json`](../../tools/tests/fixtures/openfema/county-RI-Nosuch-top5.json)
```json
{"metadata": {"skip":0,"select":null,"rundate":"2026-10-24T12:09:56.770Z","top":5,"filter":"state eq 'RI' and designatedArea eq 'Nosuch%20(County)'","format":"json","metadata":true,"orderby":"","entityname":"DisasterDeclarationsSummaries","version":"v2","url":"/api/open/v2/DisasterDeclarationsSummaries?$filter=state+eq+%27RI%27+and+designatedArea+eq+%27Nosuch+%28County%29%27&$top=5","count":0}, "DisasterDeclarationsSummaries": []}
```

## A failed query, on a recorded response

A malformed filter answers HTTP 400 with an OData Query Parser Error.
The tool stops with exit 2 and prints no report, and `GET /disaster`
answers 502. The answer is unknown, never "no declarations".

Source: the query `$filter=nosuchfield eq 'RI'&$top=5` on the same endpoint, captured by the coordinator under Option B on issue #312 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/312#issuecomment-6384044613)), retrieved 2026-10-24, about 12:09 to 12:11 UTC, HTTP/1.1 400 Bad Request, 233 bytes, sha256 `1a9ea451ba877fbeb2631bbb359d0779e2eb03513640f75181a0f1c1aad55686`; saved unmodified as [`tools/tests/fixtures/openfema/bad-field-400.json`](../../tools/tests/fixtures/openfema/bad-field-400.json)
```json
{"error":[{"name":"OData Query Parser Error","code":"OF_OQP_002","type":"$filter criteria error","message":"Field \"nosuchfield\" not found in the model path DisasterDeclarationsSummaries.  Please check that the fields are valid."}]}
```

## Not verified here

This container cannot reach `www.fema.gov`, because the proxy refuses the connection. No live run was made from it. The tool is tested offline on the five recorded bodies in [`tools/tests/fixtures/openfema/`](../../tools/tests/fixtures/openfema/). The coordinator's live smoke run at review is the live check.

- **No headers on record.** The recorded bodies carry no response headers, so the header part of a live transcript is not on record here.
- **County filter with `$count=true`.** It was not captured together. The count rule is the API page's, and the tool states a total only when the response's own metadata.url shows it.
- **Rate limits and timeouts.** No rate limit or timeout statement was found on the API page as read on 2026-10-24.
- **Apostrophes.** County names with an apostrophe are refused, because their OData quoting has not been verified against the API.
