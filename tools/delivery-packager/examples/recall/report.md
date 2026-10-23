# Product recall check (CPSC Recalls API): Peloton Tread+

Produced by `tools/delivery_packager.py`. Every claim below sits under its source link with the complete raw response printed beneath it, and every summary line names the section that carries its evidence. Values are as the sources returned them at the stated retrieval times.

## Scope and inputs

- Service: Product recall check (CPSC Recalls API)
- Subject: Peloton Tread+
- Buyer ask, as given: Is there a CPSC recall on record for the Peloton Tread+? Show the recall and its source.
- Inputs: `{"exact_name": "Tread+", "queries": [{"field": "ProductName", "value": "Tread+"}, {"field": "RecallNumber", "value": "21-128"}]}`
- Sources: replay of captures already committed in this repository; no request was made for this package
- Packaged (UTC): 2026-10-23T23:52:48Z
- Scope: only the queries listed in the sections below, as each source answered them. A section that finds nothing is a search observation, not a clearance.

## Summary

- CPSC records returned for the ProductName query "Tread+": 1. (Section S1)
- CPSC records returned for the RecallNumber query "21-128": 1. (Section S2)

## Section S1: CPSC ProductName query "Tread+"

### Product query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Tread%2B
Retrieved (UTC): 2026-10-23T21:57:25Z

CPSC returned 1 record(s) for this query.

- Returned candidate: recall "21128"; product name(s) as shown: "Tread+".

#### Recall 21-128
- Recall number as shown: "21128"
- Announcement date as shown: "2021-05-05T00:00:00" (May 5, 2021)
- Title as shown: "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported"
- Product as shown: "Tread+"
- Hazard as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Remedy as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Units as shown: "About 125,000"
- Remedy options as shown: "Refund"; "Repair"
- CPSC recall page as shown: "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported"
- Note: the remedy text in this API record repeats the hazard text word for word. Read the remedy from the CPSC recall page above and quote that page as its own source.
- Listed above as: Returned candidate

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Tread%2B>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Vary: Accept-Encoding
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:26 GMT
Date: Fri, 23 Oct 2026 21:57:26 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Alt-Svc: h3=":443"; ma=93600
Content-Length: 2735

[{"RecallID":9057,"RecallNumber":"21128","RecallDate":"2021-05-05T00:00:00","Description":"This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.","URL":"https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported","Title":"Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported","ConsumerContact":"Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.","LastPublishDate":"2021-05-05T00:00:00","Products":[{"Name":"Tread+","Description":"","Model":"","Type":"","CategoryID":"","NumberOfUnits":"About 125,000"}],"Inconjunctions":[],"Images":[{"URL":"https://www.cpsc.gov/s3fs-public/Peloton Tread Plus Recall Picture_0.png","Caption":"Recalled Peloton Tread+ Treadmill"}],"Injuries":[{"Name":"A 6-year-old child recently died after being pulled under the rear of the treadmill. In addition, Peloton has received 72 reports of adult users, children, pets and/or objects being pulled under the rear of the treadmill, including 29 reports of injuries to children such as second- and third-degree abrasions, broken bones, and lacerations."}],"Manufacturers":[],"Retailers":[{"Name":"Online at onepeloton.com and at Peloton showrooms from September 2018 through April 2021 for about $4,295.","CompanyID":""}],"Importers":[{"Name":"Peloton Interactive, Inc., of New York","CompanyID":""}],"Distributors":[],"SoldAtLabel":null,"ManufacturerCountries":[{"Country":"Taiwan"}],"ProductUPCs":[],"Hazards":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.","HazardType":"","HazardTypeID":""}],"Remedies":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."}],"RemedyOptions":[{"Option":"Refund"},{"Option":"Repair"}]}]
```

## Section S2: CPSC RecallNumber query "21-128"

### Recall number query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128
Retrieved (UTC): 2026-10-23T21:57:24Z

CPSC returned 1 record(s) for this query.

- Returned candidate: recall "21128"; product name(s) as shown: "Tread+".

#### Recall 21-128
- Recall number as shown: "21128"
- Announcement date as shown: "2021-05-05T00:00:00" (May 5, 2021)
- Title as shown: "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported"
- Product as shown: "Tread+"
- Hazard as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Remedy as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Units as shown: "About 125,000"
- Remedy options as shown: "Refund"; "Repair"
- CPSC recall page as shown: "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported"
- Note: the remedy text in this API record repeats the hazard text word for word. Read the remedy from the CPSC recall page above and quote that page as its own source.
- Listed above as: Returned candidate

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Vary: Accept-Encoding
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:25 GMT
Date: Fri, 23 Oct 2026 21:57:25 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Alt-Svc: h3=":443"; ma=93600
Content-Length: 2735

[{"RecallID":9057,"RecallNumber":"21128","RecallDate":"2021-05-05T00:00:00","Description":"This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.","URL":"https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported","Title":"Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported","ConsumerContact":"Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.","LastPublishDate":"2021-05-05T00:00:00","Products":[{"Name":"Tread+","Description":"","Model":"","Type":"","CategoryID":"","NumberOfUnits":"About 125,000"}],"Inconjunctions":[],"Images":[{"URL":"https://www.cpsc.gov/s3fs-public/Peloton Tread Plus Recall Picture_0.png","Caption":"Recalled Peloton Tread+ Treadmill"}],"Injuries":[{"Name":"A 6-year-old child recently died after being pulled under the rear of the treadmill. In addition, Peloton has received 72 reports of adult users, children, pets and/or objects being pulled under the rear of the treadmill, including 29 reports of injuries to children such as second- and third-degree abrasions, broken bones, and lacerations."}],"Manufacturers":[],"Retailers":[{"Name":"Online at onepeloton.com and at Peloton showrooms from September 2018 through April 2021 for about $4,295.","CompanyID":""}],"Importers":[{"Name":"Peloton Interactive, Inc., of New York","CompanyID":""}],"Distributors":[],"SoldAtLabel":null,"ManufacturerCountries":[{"Country":"Taiwan"}],"ProductUPCs":[],"Hazards":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.","HazardType":"","HazardTypeID":""}],"Remedies":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."}],"RemedyOptions":[{"Option":"Refund"},{"Option":"Repair"}]}]
```

## Package checked and excluded

- None: no result in any section was set aside as a near match for this job.

## Package sources

- S1: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Tread%2B, retrieved 2026-10-23T21:57:25Z; replayed from tools/examples/standing-watch/snapshot-run1-2026-10-23.json, entry product:peloton-tread, response 1 (live run 2026-10-23T21:57:11Z; SHA-256 4a9b73ccee6dc0e957bbafe310f41aaff91464bbe293e922c27ba72ffe63900c as recorded).
- S2: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128, retrieved 2026-10-23T21:57:24Z; replayed from tools/examples/standing-watch/snapshot-run1-2026-10-23.json, entry product:peloton-tread, response 0 (live run 2026-10-23T21:57:11Z; SHA-256 3df43c84a1bc24258dc64ff6eca01985b40bef4e8961301225fd47d5116d1706 as recorded).
