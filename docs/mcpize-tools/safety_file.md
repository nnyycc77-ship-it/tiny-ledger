# `safety_file`: NHTSA model safety file

A tool factory wave 2 tool (issue #176). The fetcher is
[`tools/safety_file.py`](../../tools/safety_file.py), and it is served as
`GET /safety` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is not on the MCP server yet. Wave tools that pass review are
registered on the server in one shared surface PR (coordinator rulings on
issues #158 and #175), and going live is one owner redeploy step after that.

- **What it answers:** For one make, model and model year, the NHTSA crash test ratings of each rated variant, the recall campaigns, and the consumer complaints, in one file. Each figure is stated only where the raw response beneath it shows it.
- **Sources:** Three keyless NHTSA APIs on `api.nhtsa.gov`, called as the coordinator's live captures on #176 show them:
  - `SafetyRatings/modelyear/<year>/make/<make>/model/<model>` lists the rated variants;
  - `SafetyRatings/VehicleId/<id>` gives each variant's ratings;
  - `recalls/recallsByVehicle?make=&model=&modelYear=` gives the recalls;
  - `complaints/complaintsByVehicle?make=&model=&modelYear=` gives the complaints.
- **No NHTSA documentation is cited.** NHTSA's documentation page refused the coordinator's capture (HTTP 403), so none is quoted here.
- **Arguments:** `make`, `model`, `year` (four digits).
- **Needs on the server:** Outbound HTTPS to `api.nhtsa.gov`. No key, no environment value.
- **What it is not:** An inspection or a judgement of any vehicle. Ratings, recalls and complaints are NHTSA's records as shown. Complaints are consumer reports, not findings.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

Every report uses the repo's fixed evidence format. Each section has its
own source link with its complete raw response directly beneath it, the
exact query and retrieval time are recorded, and an empty result is
proven by the complete raw response.

## Source failures are never empty results

The coordinator's captures on #176 show these endpoints answering HTTP
400 or 500 while the body still reads "Results returned successfully".
An unknown model gets HTTP 400 from both recalls and complaints, with a
body of `{"Count":0,"Message":"Results returned successfully","results":[]}`
(recalls; complaints spells `count` and `message` in lower case). So the
tool checks the HTTP status first. Any status other than 200, or a body
without the results array the endpoint returns, is a source failure. The
call then prints no report: the CLI exits 2, and the API answers 502. The
failure names each failed source, its exact query, its status and its
body. The one genuine empty case on record is safety ratings for an
unknown model: HTTP 200, Count 0, Results [].

## What a report shows, on a recorded response

The tool's ratings lines for the recorded 2021 Hyundai Elantra
(VehicleId 15697). The claims are the tool's own lines for that response
(the offline tests check these exact lines), with the recorded response
printed directly beneath the source link.

- `- OverallRating as shown: 5`
- `- OverallFrontCrashRating as shown: 4`
- `- RolloverPossibility as shown: 0.101`
- `- RecallsCount as shown in the ratings record for VehicleId 15697: 6; records in the recalls response: 6.`

Source: https://api.nhtsa.gov/SafetyRatings/VehicleId/15697, captured keyless by the coordinator under Option B on issue #176 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/176#issuecomment-6379528154)), retrieved 2026-10-24, about 03:51 to 03:53 UTC (response Date header: Sat, 24 Oct 2026 03:51:46 GMT); body 1360 bytes, sha256 `73882ec247d8cba40f081fdbcfb4ff393cde306dfe987f6f49737156550c1e84`; saved as [`tools/tests/fixtures/nhtsa-safety/ratings-vehicle-15697.http`](../../tools/tests/fixtures/nhtsa-safety/ratings-vehicle-15697.http). Headers as posted, with Set-Cookie omitted by the coordinator.
```text
HTTP/1.1 200 OK
Content-Type: application/json;charset=utf-8
x-amzn-RequestId: 27b6d6cb-11a0-481c-8f04-4ef1523cda8b
x-amzn-Remapped-Connection: keep-alive
x-amz-apigw-id: FtacwHwBoAMFeuQ=
x-amzn-Remapped-Date: Fri, 23 Oct 2026 18:15:45 GMT
X-Application-Context: application:production
Date: Sat, 24 Oct 2026 03:51:46 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Content-Length: 1360

{"Count":1,"Message":"Results returned successfully","Results":[{"OverallRating":"5","OverallFrontCrashRating":"4","FrontCrashDriversideRating":"5","FrontCrashPassengersideRating":"4","FrontCrashPicture":"https://static.nhtsa.gov/crashTest/images/2021/v11574P085.jpg","FrontCrashVideo":"https://static.nhtsa.gov/crashTest/videos/2021/v11574C019.wmv","OverallSideCrashRating":"5","SideCrashDriversideRating":"5","SideCrashPassengersideRating":"5","SideCrashPicture":"https://static.nhtsa.gov/crashTest/images/2021/v11576P105.JPG","SideCrashVideo":"https://static.nhtsa.gov/crashTest/videos/2021/v11576C013.wmv","combinedSideBarrierAndPoleRating-Front":"5","combinedSideBarrierAndPoleRating-Rear":"5","sideBarrierRating-Overall":"5","RolloverRating":"5","RolloverRating2":"Not Rated","RolloverPossibility":0.101,"RolloverPossibility2":0.0,"dynamicTipResult":"No Tip","SidePoleCrashRating":"5","SidePolePicture":"https://static.nhtsa.gov/crashTest/images/2021/v11577P075.jpg","SidePoleVideo":"https://static.nhtsa.gov/crashTest/videos/2021/v11577C013.wmv","NHTSAElectronicStabilityControl":"Standard","NHTSAForwardCollisionWarning":"No","NHTSALaneDepartureWarning":"Standard","ComplaintsCount":132,"RecallsCount":6,"InvestigationCount":2,"ModelYear":2021,"Make":"HYUNDAI","Model":"ELANTRA","VehicleDescription":"2021 Hyundai Elantra 4 DR FWD","VehicleId":15697}]}
```

All recorded responses are in [`tools/tests/fixtures/nhtsa-safety/`](../../tools/tests/fixtures/nhtsa-safety/), with their provenance:
- the Elantra variants list, ratings, recalls and complaints;
- the unknown model's ratings (HTTP 200, empty), recalls and complaints (HTTP 400);
- complaints for a non-numeric year (HTTP 500).

## Not verified here

This container cannot reach `api.nhtsa.gov` (the proxy refuses the
connection), so no live run was made from it. The tool's behaviour is
tested offline on the recorded responses above. The coordinator's live
smoke run at review is the live check.
