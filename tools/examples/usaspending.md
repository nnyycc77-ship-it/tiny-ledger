# USAspending fetcher: captured live examples

Rendered from the complete live responses retained with request provenance in
`tools/tests/fixtures/usaspending/`. These are API search observations, not paid
deliveries. Exclusion is a reviewer-supplied agency-scope decision.

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

### Checked and excluded near match

- Award ID as shown: "NAS1510000"
- Recipient Name as shown: "THE BOEING COMPANY"
- Award Amount as shown: 22653589199\.84
- Awarding Agency as shown: "National Aeronautics and Space Administration"
- Description as shown: "INTERNATIONAL SPACE STATION"
- Start Date as shown: "1993\-11\-15"
- End Date as shown: "2031\-09\-30"
- NAICS as shown: \{"code": "336414", "description": "GUIDED MISSILE AND SPACE VEHICLE MANUFACTURING"\}
- generated_internal_id as shown: "CONT\_AWD\_NAS1510000\_8000\_\-NONE\-\_\-NONE\-"
- Reviewer-supplied exclusion reason: "Outside this brief’s Department of Defense scope; source Awarding Agency is National Aeronautics and Space Administration\."

API messages as returned: \["For searches, time period start and end dates are currently limited to an earliest date of 2007\-10\-01\.  For data going back to 2000\-10\-01, use either the Custom Award Download feature on the website or one of our download or bulk\_download API endpoints as listed on https://api\.usaspending\.gov/docs/endpoints\. "\]

Source: <https://api.usaspending.gov/api/v2/search/spending_by_award/>
```
{"spending_level":"awards","limit":2,"results":[{"internal_id":298557808,"Award ID":"FA862511C6600","Recipient Name":"THE BOEING COMPANY","Award Amount":31972918249.03,"Awarding Agency":"Department of Defense","Description":"KC-X MODERNIZATION PROGRAM","Start Date":"2011-02-24","End Date":"2027-07-31","NAICS":{"code":"336411","description":"AIRCRAFT MANUFACTURING"},"generated_internal_id":"CONT_AWD_FA862511C6600_9700_-NONE-_-NONE-","awarding_agency_id":1173,"agency_slug":"department-of-defense"},{"internal_id":311267295,"Award ID":"NAS1510000","Recipient Name":"THE BOEING COMPANY","Award Amount":22653589199.84,"Awarding Agency":"National Aeronautics and Space Administration","Description":"INTERNATIONAL SPACE STATION","Start Date":"1993-11-15","End Date":"2031-09-30","NAICS":{"code":"336414","description":"GUIDED MISSILE AND SPACE VEHICLE MANUFACTURING"},"generated_internal_id":"CONT_AWD_NAS1510000_8000_-NONE-_-NONE-","awarding_agency_id":862,"agency_slug":"national-aeronautics-and-space-administration"}],"page_metadata":{"page":1,"hasNext":true,"last_record_unique_id":311267295,"last_record_sort_value":"2265358919984"},"messages":["For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. "]}
```

## USAspending prime contract awards

Scope: one requested page; no assertion of an exhaustive recipient or award search.
Award Amount is the API field as returned, not a payment or revenue estimate.

Exact query: POST https://api.usaspending.gov/api/v2/search/spending_by_award/
Content-Type: application/json
Exact request body:
```
{"filters":{"award_type_codes":["A","B","C","D"],"recipient_search_text":["Instant Pot Smart WiFi"]},"fields":["Award ID","Recipient Name","Award Amount","Awarding Agency","Description","Start Date","End Date","NAICS","generated_internal_id"],"page":1,"limit":2,"sort":"Award Amount","order":"desc","subawards":false}
```
Retrieved (UTC): 2026-10-23T00:17:58Z

USAspending returned 0 record(s) on requested page 1.
API page_metadata.hasNext: false.
No records on this page; this does not establish that the recipient has no awards.

API messages as returned: \["For searches, time period start and end dates are currently limited to an earliest date of 2007\-10\-01\.  For data going back to 2000\-10\-01, use either the Custom Award Download feature on the website or one of our download or bulk\_download API endpoints as listed on https://api\.usaspending\.gov/docs/endpoints\. "\]

Source: <https://api.usaspending.gov/api/v2/search/spending_by_award/>
```
{"spending_level":"awards","limit":2,"results":[],"page_metadata":{"page":1,"hasNext":false,"last_record_unique_id":null,"last_record_sort_value":"None"},"messages":["For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. "]}
```

## USAspending prime contract awards

Scope: one requested page; no assertion of an exhaustive recipient or award search.
Award Amount is the API field as returned, not a payment or revenue estimate.

Exact query: POST https://api.usaspending.gov/api/v2/search/spending_by_award/
Content-Type: application/json
Exact request body:
```
{"filters":{"award_type_codes":["A","B","C","D"],"recipient_search_text":["Boeing"],"naics_codes":{"require":["336411"]}},"fields":["Award ID","Recipient Name","Award Amount","Awarding Agency","Description","Start Date","End Date","NAICS","generated_internal_id"],"page":1,"limit":2,"sort":"Award Amount","order":"desc","subawards":false}
```
Retrieved (UTC): 2026-10-23T00:18:02Z

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

- Award ID as shown: "N0001914C0067"
- Recipient Name as shown: "THE BOEING COMPANY"
- Award Amount as shown: 18111838529\.78
- Awarding Agency as shown: "Department of Defense"
- Description as shown: "USN P\-8A FRP II LONG LEAD MATERIAL"
- Start Date as shown: "2014\-08\-14"
- End Date as shown: "2027\-04\-30"
- NAICS as shown: \{"code": "336411", "description": "AIRCRAFT MANUFACTURING"\}
- generated_internal_id as shown: "CONT\_AWD\_N0001914C0067\_9700\_\-NONE\-\_\-NONE\-"

API messages as returned: \["For searches, time period start and end dates are currently limited to an earliest date of 2007\-10\-01\.  For data going back to 2000\-10\-01, use either the Custom Award Download feature on the website or one of our download or bulk\_download API endpoints as listed on https://api\.usaspending\.gov/docs/endpoints\. "\]

Source: <https://api.usaspending.gov/api/v2/search/spending_by_award/>
```
{"spending_level":"awards","limit":2,"results":[{"internal_id":298557808,"Award ID":"FA862511C6600","Recipient Name":"THE BOEING COMPANY","Award Amount":31972918249.03,"Awarding Agency":"Department of Defense","Description":"KC-X MODERNIZATION PROGRAM","Start Date":"2011-02-24","End Date":"2027-07-31","NAICS":{"code":"336411","description":"AIRCRAFT MANUFACTURING"},"generated_internal_id":"CONT_AWD_FA862511C6600_9700_-NONE-_-NONE-","awarding_agency_id":1173,"agency_slug":"department-of-defense"},{"internal_id":309494374,"Award ID":"N0001914C0067","Recipient Name":"THE BOEING COMPANY","Award Amount":18111838529.78,"Awarding Agency":"Department of Defense","Description":"USN P-8A FRP II LONG LEAD MATERIAL","Start Date":"2014-08-14","End Date":"2027-04-30","NAICS":{"code":"336411","description":"AIRCRAFT MANUFACTURING"},"generated_internal_id":"CONT_AWD_N0001914C0067_9700_-NONE-_-NONE-","awarding_agency_id":1173,"agency_slug":"department-of-defense"}],"page_metadata":{"page":1,"hasNext":true,"last_record_unique_id":309494374,"last_record_sort_value":"1811183852978"},"messages":["For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. "]}
```
