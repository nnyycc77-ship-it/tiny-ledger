# Federal awards check (USAspending prime contract awards): Boeing

Produced by `tools/delivery_packager.py`. Every claim below sits under its source link with the complete raw response printed beneath it, and every summary line names the section that carries its evidence. Values are as the sources returned them at the stated retrieval times.

## Scope and inputs

- Service: Federal awards check (USAspending prime contract awards)
- Subject: Boeing
- Buyer ask, as given: Show the largest federal prime contract awards to this recipient on USAspending.
- Inputs: `{"limit": 2, "recipient": "Boeing"}`
- Sources: replay of captures already committed in this repository; no request was made for this package
- Packaged (UTC): 2026-10-23T23:52:49Z
- Scope: only the queries listed in the sections below, as each source answered them. A section that finds nothing is a search observation, not a clearance.

## Summary

- USAspending awards returned on requested page 1: 2. (Section S1)

## Section S1: USAspending prime contract awards, Boeing

## USAspending prime contract awards

Scope: one requested page; no assertion of an exhaustive recipient or award search.
Award Amount is the API field as returned, not a payment or revenue estimate.

Exact query: POST https://api.usaspending.gov/api/v2/search/spending_by_award/
Content-Type: application/json
Exact request body:
```
{"filters":{"award_type_codes":["A","B","C","D"],"recipient_search_text":["Boeing"]},"fields":["Award ID","Recipient Name","Award Amount","Awarding Agency","Description","Start Date","End Date","NAICS","generated_internal_id"],"page":1,"limit":2,"sort":"Award Amount","order":"desc","subawards":false}
```
Retrieved (UTC): 2026-10-23T00:17:52Z

USAspending returned 2 record(s) on requested page 1.
API page_metadata.hasNext: true.
More pages are reported by the API; this section does not include them.

### Returned award

- Award ID as shown: "FA862511C6600"
- Recipient Name as shown: "THE BOEING COMPANY"
- Award Amount as shown: 31972918249\.03
- Awarding Agency as shown: "Department of Defense"
- Description as shown: "KC\-X MODERNIZATION PROGRAM"
- Start Date as shown: "2011\-02\-24"
- End Date as shown: "2027\-07\-31"
- NAICS as shown: \{"code": "336411", "description": "AIRCRAFT MANUFACTURING"\}
- generated_internal_id as shown: "CONT\_AWD\_FA862511C6600\_9700\_\-NONE\-\_\-NONE\-"

### Returned award

- Award ID as shown: "NAS1510000"
- Recipient Name as shown: "THE BOEING COMPANY"
- Award Amount as shown: 22653589199\.84
- Awarding Agency as shown: "National Aeronautics and Space Administration"
- Description as shown: "INTERNATIONAL SPACE STATION"
- Start Date as shown: "1993\-11\-15"
- End Date as shown: "2031\-09\-30"
- NAICS as shown: \{"code": "336414", "description": "GUIDED MISSILE AND SPACE VEHICLE MANUFACTURING"\}
- generated_internal_id as shown: "CONT\_AWD\_NAS1510000\_8000\_\-NONE\-\_\-NONE\-"

API messages as returned: \["For searches, time period start and end dates are currently limited to an earliest date of 2007\-10\-01\.  For data going back to 2000\-10\-01, use either the Custom Award Download feature on the website or one of our download or bulk\_download API endpoints as listed on https://api\.usaspending\.gov/docs/endpoints\. "\]

Source: <https://api.usaspending.gov/api/v2/search/spending_by_award/>
```
{"spending_level":"awards","limit":2,"results":[{"internal_id":298557808,"Award ID":"FA862511C6600","Recipient Name":"THE BOEING COMPANY","Award Amount":31972918249.03,"Awarding Agency":"Department of Defense","Description":"KC-X MODERNIZATION PROGRAM","Start Date":"2011-02-24","End Date":"2027-07-31","NAICS":{"code":"336411","description":"AIRCRAFT MANUFACTURING"},"generated_internal_id":"CONT_AWD_FA862511C6600_9700_-NONE-_-NONE-","awarding_agency_id":1173,"agency_slug":"department-of-defense"},{"internal_id":311267295,"Award ID":"NAS1510000","Recipient Name":"THE BOEING COMPANY","Award Amount":22653589199.84,"Awarding Agency":"National Aeronautics and Space Administration","Description":"INTERNATIONAL SPACE STATION","Start Date":"1993-11-15","End Date":"2031-09-30","NAICS":{"code":"336414","description":"GUIDED MISSILE AND SPACE VEHICLE MANUFACTURING"},"generated_internal_id":"CONT_AWD_NAS1510000_8000_-NONE-_-NONE-","awarding_agency_id":862,"agency_slug":"national-aeronautics-and-space-administration"}],"page_metadata":{"page":1,"hasNext":true,"last_record_unique_id":311267295,"last_record_sort_value":"2265358919984"},"messages":["For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. "]}
```

## Package checked and excluded

- None: no result in any section was set aside as a near match for this job.

## Package sources

- S1: https://api.usaspending.gov/api/v2/search/spending_by_award/, retrieved 2026-10-23T00:17:52Z; replayed from tools/tests/fixtures/usaspending/recipient.json with the request and retrieval time in tools/tests/fixtures/usaspending/recipient.meta.json (SHA-256 b77571eca7ef51670b4a1e8eeb0a1fa76ce11b933cad747b829d2e56830edff2).
