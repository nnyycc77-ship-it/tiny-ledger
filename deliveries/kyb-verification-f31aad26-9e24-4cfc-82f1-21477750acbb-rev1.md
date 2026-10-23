# KYB entity verification, five Florida headquartered public companies, GLEIF and SEC EDGAR

Disclaimer: verification of public registry data only, not a sanctions screen, beneficial ownership certification or credit decision.
This work was unattended agent work and observation of public records only, with no contact with anyone (no emails, calls, messages or test sends).
Retrieval date for every query below: 2026-10-23 (UTC times in section 5). SEC EDGAR queries were sent with User-Agent: Hojo Research Agent nnyycc77@gmail.com

Revision 1 note (2026-10-23): this revision answers the two evaluator items on escrow esc_c81b3a2752d4478b8cd4bcf0, round 1 of 3, both about one field. Section 1 reports Entity status: ACTIVE for Jabil, Raymond James, Lennar and NextEra, but the single record excerpts in S8 to S11 stopped at the legalForm and associatedEntity blocks, before the entity status field that follows them in the same record. No figure, name, date or finding in sections 1 to 4 changes. New sources S35 to S38 at the end of section 5 reprint, for each of the four LEI records, a verbatim excerpt from a fresh pull of the same GLEIF single record URL, running from the registeredAt block through the entity status line, so the value ACTIVE now stands inside a quoted excerpt directly under its source link for every entity that has an LEI record. Publix Super Markets, Inc. has no LEI record found, so it has no entity status field to excerpt.

## 1. LEI (GLEIF)

### Jabil Inc.
Name search run: GLEIF filter[entity.legalName] with the name as written (Jabil Inc.); result count as returned in the response meta: 1.
LEI: 5493000CGCQY2OQU7669
Legal name: JABIL INC.
Legal address: C/O THE CORPORATION TRUST COMPANY, CORPORATION TRUST CENTER, 1209 ORANGE ST, WILMINGTON, US-DE, 19801, US
Headquarters address: 10800 ROOSEVELT BLVD N, ST. PETERSBURG, US-FL, 33716, US
Legal jurisdiction: US-DE
Entity status: ACTIVE
Registration status: ISSUED
Last update date: 2026-08-10T09:04:58Z
Next renewal date: 2027-08-12T00:00:00Z

### Raymond James Financial, Inc.
Name search run: GLEIF filter[entity.legalName] with the name as written (Raymond James Financial, Inc.); result count as returned in the response meta: 77254 (the filter returns a broad tokenised set; the record whose legal name matches the name as written, ignoring case and punctuation, is the first record returned).
LEI: RGUZHJ05YTITL6D76949
Legal name: RAYMOND JAMES FINANCIAL, INC.
Legal address: C/O CT CORPORATION SYSTEM, 1200 SOUTH PINE ISLAND ROAD, PLANTATION, US-FL, 33324, US
Headquarters address: 880 Carillon Parkway, St. Petersburg, US-FL, 33716, US
Legal jurisdiction: US-FL
Entity status: ACTIVE
Registration status: ISSUED
Last update date: 2025-12-30T16:32:06Z
Next renewal date: 2027-01-05T11:16:55Z

### Publix Super Markets, Inc.
Name search run: GLEIF filter[entity.legalName] with the name as written (Publix Super Markets, Inc.); result count as returned in the response meta: 77253 (the filter returns a broad tokenised set, and none of the 15 records on the first page is this entity). Fulltext follow up searches as prescribed: the exact phrase fulltext search returned 0 records, and the single token Publix fulltext search returned 5 records (Stiftung Gesunde Erde Gesunde Menschen gGmbH, Publix Employees Federal Credit Union, SOUTH END PARTNERS, LLC, and two more, none of them Publix Super Markets, Inc.; Publix Employees Federal Credit Union is a different legal entity).
no LEI record found

### Lennar Corporation
Name search run: GLEIF filter[entity.legalName] with the name as written (Lennar Corporation); result count as returned in the response meta: 1.
LEI: 529900G61XVRLX5TJX09
Legal name: LENNAR CORPORATION
Legal address: c/o THE CORPORATION TRUST COMPANY, CORPORATION TRUST CENTER 1209 ORANGE ST, WILMINGTON, US-DE, 19801, US
Headquarters address: 700 Northwest 107th Avenue, Miami, US-FL, 33172, US
Legal jurisdiction: US-DE
Entity status: ACTIVE
Registration status: LAPSED
Last update date: 2021-07-16T05:04:45Z
Next renewal date: 2020-01-02T11:24:40Z

### NextEra Energy, Inc.
Name search run: GLEIF filter[entity.legalName] with the name as written (NextEra Energy, Inc.); result count as returned in the response meta: 77278 (the filter returns a broad tokenised set; the record whose legal name matches the name as written, ignoring case and punctuation, is the first record returned).
LEI: 254900RHL9MEUS5NKX63
Legal name: NextEra Energy, Inc.
Legal address: C/O CORPORATION SERVICE COMPANY, 1201 HAYS STREET, TALLAHASSEE, US-FL, 32301, US
Headquarters address: 700 UNIVERSE BLVD, JUNO BEACH, US-FL, 33408, US
Legal jurisdiction: US-FL
Entity status: ACTIVE
Registration status: ISSUED
Last update date: 2026-02-13T15:36:14Z
Next renewal date: 2027-02-26T08:29:55Z

## 2. PARENTS (GLEIF)

### Jabil Inc.
Direct parent: the direct parent call returned 404 (related resource not found); the direct parent reporting exception gives reason NON_CONSOLIDATING. No parent LEI or name is reported.
Ultimate parent: the ultimate parent call returned 404 (related resource not found); the ultimate parent reporting exception gives reason NON_CONSOLIDATING. No parent LEI or name is reported.

### Raymond James Financial, Inc.
Direct parent: the direct parent call returned 404 (related resource not found); the direct parent reporting exception gives reason NON_CONSOLIDATING. No parent LEI or name is reported.
Ultimate parent: the ultimate parent call returned 404 (related resource not found); the ultimate parent reporting exception gives reason NON_CONSOLIDATING. No parent LEI or name is reported.

### Lennar Corporation
Direct parent: the direct parent call returned 404 (related resource not found); the direct parent reporting exception gives reason NO_KNOWN_PERSON. No parent LEI or name is reported.
Ultimate parent: the ultimate parent call returned 404 (related resource not found); the ultimate parent reporting exception gives reason NO_KNOWN_PERSON. No parent LEI or name is reported.

### NextEra Energy, Inc.
Direct parent: the direct parent call returned 404 (related resource not found); the direct parent reporting exception gives reason NO_KNOWN_PERSON. No parent LEI or name is reported.
Ultimate parent: the ultimate parent call returned 404 (related resource not found); the ultimate parent reporting exception gives reason NO_KNOWN_PERSON. No parent LEI or name is reported.

### Publix Super Markets, Inc.
No LEI record found (section 1), so no direct or ultimate parent call and no reporting exception call can be run for this entity; parent calls on GLEIF are addressed by LEI. No parent reported.

## 3. SEC (EDGAR)

### Jabil Inc.
CIK: 898293
Name: JABIL INC
SIC code: 3672
SIC description: Printed Circuit Boards
State of incorporation: DE
Fiscal year end: 0831
Former names: JABIL CIRCUIT INC (1996-07-15 to 2017-06-05)

### Raymond James Financial, Inc.
CIK: 720005
Name: RAYMOND JAMES FINANCIAL INC
SIC code: 6211
SIC description: Security Brokers, Dealers & Flotation Companies
State of incorporation: FL
Fiscal year end: 0930
Former names: none (the formerNames array is empty)

### Publix Super Markets, Inc.
CIK: 81061
Name: PUBLIX SUPER MARKETS INC
SIC code: 5411
SIC description: Retail-Grocery Stores
State of incorporation: FL
Fiscal year end: 1226
Former names: none (the formerNames array is empty). This entity has no entry in the SEC company tickers file (it is not exchange listed; its tickers and exchanges arrays in the submissions record are empty); its CIK was taken from the SEC EDGAR company name search result in section 5.

### Lennar Corporation
CIK: 920760
Name: LENNAR CORP /NEW/
SIC code: 1520
SIC description: General Bldg Contractors - Residential Bldgs
State of incorporation: DE
Fiscal year end: 1130
Former names: PACIFIC GREYSTONE CORP /DE/ (1996-06-27 to 1997-09-26)

### NextEra Energy, Inc.
CIK: 753308
Name: NEXTERA ENERGY INC
SIC code: 4911
SIC description: Electric Services
State of incorporation: FL
Fiscal year end: 1231
Former names: FPL GROUP INC (1994-02-28 to 2010-05-21)

## 4. CONSISTENCY

### Jabil Inc.
GLEIF legal name JABIL INC. and SEC name JABIL INC match, ignoring case and punctuation. Registration status is ISSUED and the next renewal date 2027-08-12T00:00:00Z is after the retrieval time. No flag.

### Raymond James Financial, Inc.
GLEIF legal name RAYMOND JAMES FINANCIAL, INC. and SEC name RAYMOND JAMES FINANCIAL INC match, ignoring case and punctuation. Registration status is ISSUED and the next renewal date 2027-01-05T11:16:55Z is after the retrieval time. No flag.

### Publix Super Markets, Inc.
FLAG: no LEI record found, so no GLEIF legal name exists to compare with the SEC name PUBLIX SUPER MARKETS INC, and no registration status or renewal date exists to check.

### Lennar Corporation
FLAG: GLEIF legal name LENNAR CORPORATION and SEC name LENNAR CORP /NEW/ do not match under the stated rule (ignoring case and punctuation only): CORPORATION is abbreviated to CORP and the SEC name carries a /NEW/ suffix. FLAG: registration status is LAPSED, not ISSUED, and the next renewal date 2020-01-02T11:24:40Z is before the retrieval time.

### NextEra Energy, Inc.
GLEIF legal name NextEra Energy, Inc. and SEC name NEXTERA ENERGY INC match, ignoring case and punctuation. Registration status is ISSUED and the next renewal date 2027-02-26T08:29:55Z is after the retrieval time. No flag.

## 5. SOURCES

### S1. GLEIF LEI search by legal name, Jabil Inc.
https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=Jabil Inc.
Retrieved: 2026-10-23T15:18:36Z
```
      "from": 1,
      "to": 1,
      "total": 1,
      "lastPage": 1
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Jabil+Inc.&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Jabil+Inc.&page%5Bnumber%5D=1&page%5Bsize%5D=15"
  },
  "data": [
    {
      "type": "lei-records",
      "id": "5493000CGCQY2OQU7669",
      "attributes": {
```
```
        "lei": "5493000CGCQY2OQU7669",
        "entity": {
          "legalName": {
            "name": "JABIL INC.",
            "language": "en"
          },
          "otherNames": [
            {
              "name": "JABIL CIRCUIT, INC.",
              "language": "en",
              "type": "PREVIOUS_LEGAL_NAME"
            }
          ],
```

### S2. GLEIF LEI search by legal name, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=Raymond James Financial, Inc.
Retrieved: 2026-10-23T15:18:46Z
```
      "from": 1,
      "to": 15,
      "total": 77254,
      "lastPage": 5151
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Raymond+James+Financial%2C+Inc.&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "next": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Raymond+James+Financial%2C+Inc.&page%5Bnumber%5D=2&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Raymond+James+Financial%2C+Inc.&page%5Bnumber%5D=5151&page%5Bsize%5D=15"
  },
  "data": [
    {
      "type": "lei-records",
      "id": "RGUZHJ05YTITL6D76949",
```
```
        "lei": "RGUZHJ05YTITL6D76949",
        "entity": {
          "legalName": {
            "name": "RAYMOND JAMES FINANCIAL, INC.",
            "language": "en"
          },
          "otherNames": [
            {
              "name": "RJ FINANCIAL CORPORATION",
              "language": "en",
              "type": "PREVIOUS_LEGAL_NAME"
            },
            {
```

### S3. GLEIF LEI search by legal name, Publix Super Markets, Inc.
https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=Publix Super Markets, Inc.
Retrieved: 2026-10-23T15:18:47Z
```
      "from": 1,
      "to": 15,
      "total": 77253,
      "lastPage": 5151
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Publix+Super+Markets%2C+Inc.&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "next": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Publix+Super+Markets%2C+Inc.&page%5Bnumber%5D=2&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Publix+Super+Markets%2C+Inc.&page%5Bnumber%5D=5151&page%5Bsize%5D=15"
  },
  "data": [
    {
      "type": "lei-records",
      "id": "549300I1AHR8KMMFIS52",
```
```
        "lei": "549300I1AHR8KMMFIS52",
        "entity": {
          "legalName": {
            "name": "INC Group Inc.",
            "language": "en"
          },
          "otherNames": [],
          "transliteratedOtherNames": [],
          "legalAddress": {
            "language": "en",
            "addressLines": [
              "1185 Caledonia Road"
            ],
```

### S4. GLEIF LEI search by legal name, Lennar Corporation
https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=Lennar Corporation
Retrieved: 2026-10-23T15:18:51Z
```
      "from": 1,
      "to": 1,
      "total": 1,
      "lastPage": 1
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Lennar+Corporation&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=Lennar+Corporation&page%5Bnumber%5D=1&page%5Bsize%5D=15"
  },
  "data": [
    {
      "type": "lei-records",
      "id": "529900G61XVRLX5TJX09",
      "attributes": {
```
```
        "lei": "529900G61XVRLX5TJX09",
        "entity": {
          "legalName": {
            "name": "LENNAR CORPORATION",
            "language": "en-US"
          },
          "otherNames": [],
          "transliteratedOtherNames": [],
          "legalAddress": {
            "language": "en-US",
            "addressLines": [
              "c/o THE CORPORATION TRUST COMPANY, CORPORATION TRUST CENTER 1209 ORANGE ST"
            ],
```

### S5. GLEIF LEI search by legal name, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=NextEra Energy, Inc.
Retrieved: 2026-10-23T15:18:55Z
```
      "from": 1,
      "to": 15,
      "total": 77278,
      "lastPage": 5152
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=NextEra+Energy%2C+Inc.&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "next": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=NextEra+Energy%2C+Inc.&page%5Bnumber%5D=2&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bentity.legalName%5D=NextEra+Energy%2C+Inc.&page%5Bnumber%5D=5152&page%5Bsize%5D=15"
  },
  "data": [
    {
      "type": "lei-records",
      "id": "254900RHL9MEUS5NKX63",
```
```
        "lei": "254900RHL9MEUS5NKX63",
        "entity": {
          "legalName": {
            "name": "NextEra Energy, Inc.",
            "language": "en"
          },
          "otherNames": [],
          "transliteratedOtherNames": [],
          "legalAddress": {
            "language": "en",
            "addressLines": [
              "C/O CORPORATION SERVICE COMPANY",
              "1201 HAYS STREET"
```

### S6. GLEIF fulltext search, exact phrase Publix Super Markets
https://api.gleif.org/api/v1/lei-records?filter[fulltext]="Publix Super Markets"
Retrieved: 2026-10-23T15:20:52Z
```
{
  "meta": {
    "goldenCopy": {
      "publishDate": "2026-10-23T08:00:00Z"
    },
    "pagination": {
      "currentPage": 1,
      "perPage": 15,
      "from": null,
      "to": null,
      "total": 0,
      "lastPage": 1
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bfulltext%5D=%22Publix+Super+Markets%22&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bfulltext%5D=%22Publix+Super+Markets%22&page%5Bnumber%5D=1&page%5Bsize%5D=15"
  },
  "data": []
}
```

### S7. GLEIF fulltext search, single token Publix
https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Publix
Retrieved: 2026-10-23T15:21:33Z
```
      "from": 1,
      "to": 5,
      "total": 5,
      "lastPage": 1
    }
  },
  "links": {
    "first": "https://api.gleif.org/api/v1/lei-records?filter%5Bfulltext%5D=Publix&page%5Bnumber%5D=1&page%5Bsize%5D=15",
    "last": "https://api.gleif.org/api/v1/lei-records?filter%5Bfulltext%5D=Publix&page%5Bnumber%5D=1&page%5Bsize%5D=15"
  },
  "data": [
    {
      "type": "lei-records",
      "id": "391200AC437GL7G45X64",
      "attributes": {
```
```
      "type": "lei-records",
      "id": "391200AC437GL7G45X64",
      "attributes": {
        "lei": "391200AC437GL7G45X64",
        "entity": {
          "legalName": {
            "name": "Stiftung Gesunde Erde Gesunde Menschen gGmbH",
            "language": "de"
          },
          "otherNames": [],
          "transliteratedOtherNames": [],
          "legalAddress": {
            "language": "de",
```
```
      "type": "lei-records",
      "id": "5493009KQ3D6Q5VM0B61",
      "attributes": {
        "lei": "5493009KQ3D6Q5VM0B61",
        "entity": {
          "legalName": {
            "name": "Publix Employees Federal Credit Union",
            "language": "en"
          },
          "otherNames": [
            {
              "name": "PUBLIX EMPLOYEES",
              "language": "en",
```
```
      "type": "lei-records",
      "id": "549300I5BT7N4DW1W320",
      "attributes": {
        "lei": "549300I5BT7N4DW1W320",
        "entity": {
          "legalName": {
            "name": "SOUTH END PARTNERS, LLC",
            "language": "en"
          },
          "otherNames": [],
          "transliteratedOtherNames": [],
          "legalAddress": {
            "language": "en",
```

### S8. GLEIF LEI record, Jabil Inc.
https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669
Retrieved: 2026-10-23T15:24:12Z
```
    "attributes": {
      "lei": "5493000CGCQY2OQU7669",
      "entity": {
        "legalName": {
          "name": "JABIL INC.",
          "language": "en"
        },
        "otherNames": [
          {
            "name": "JABIL CIRCUIT, INC.",
            "language": "en",
            "type": "PREVIOUS_LEGAL_NAME"
          }
        ],
```
```
        "legalAddress": {
          "language": "en",
          "addressLines": [
            "C/O THE CORPORATION TRUST COMPANY",
            "CORPORATION TRUST CENTER",
            "1209 ORANGE ST"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "WILMINGTON",
          "region": "US-DE",
          "country": "US",
          "postalCode": "19801"
        },
        "headquartersAddress": {
          "language": "en",
          "addressLines": [
            "10800 ROOSEVELT BLVD N"
          ],
          "addressNumber": null,
```
```
        "headquartersAddress": {
          "language": "en",
          "addressLines": [
            "10800 ROOSEVELT BLVD N"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "ST. PETERSBURG",
          "region": "US-FL",
          "country": "US",
          "postalCode": "33716"
        },
        "registeredAt": {
          "id": "RA000602",
          "other": null
        },
        "registeredAs": "2288884",
        "jurisdiction": "US-DE",
        "category": "GENERAL",
        "legalForm": {
```
```
        },
        "registeredAt": {
          "id": "RA000602",
          "other": null
        },
        "registeredAs": "2288884",
        "jurisdiction": "US-DE",
        "category": "GENERAL",
        "legalForm": {
          "id": "XTIQ",
          "other": null
        },
        "associatedEntity": {
```
```
      "registration": {
        "initialRegistrationDate": "2012-12-03T15:57:00Z",
        "lastUpdateDate": "2026-08-10T09:04:58Z",
        "status": "ISSUED",
        "nextRenewalDate": "2027-08-12T00:00:00Z",
        "managingLou": "5493001KJTIIGC8Y1R12",
        "corroborationLevel": "FULLY_CORROBORATED",
        "validatedAt": {
          "id": "RA000602",
          "other": null
        },
        "validatedAs": "2288884",
        "otherValidationAuthorities": []
```

### S9. GLEIF LEI record, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949
Retrieved: 2026-10-23T15:24:33Z
```
    "attributes": {
      "lei": "RGUZHJ05YTITL6D76949",
      "entity": {
        "legalName": {
          "name": "RAYMOND JAMES FINANCIAL, INC.",
          "language": "en"
        },
        "otherNames": [
          {
            "name": "RJ FINANCIAL CORPORATION",
            "language": "en",
            "type": "PREVIOUS_LEGAL_NAME"
          },
          {
```
```
        "legalAddress": {
          "language": "en",
          "addressLines": [
            "C/O CT CORPORATION SYSTEM",
            "1200 SOUTH PINE ISLAND ROAD"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "PLANTATION",
          "region": "US-FL",
          "country": "US",
          "postalCode": "33324"
        },
        "headquartersAddress": {
          "language": "en",
          "addressLines": [
            "880 Carillon Parkway"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
```
```
        "headquartersAddress": {
          "language": "en",
          "addressLines": [
            "880 Carillon Parkway"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "St. Petersburg",
          "region": "US-FL",
          "country": "US",
          "postalCode": "33716"
        },
        "registeredAt": {
          "id": "RA000603",
          "other": null
        },
        "registeredAs": "444750",
        "jurisdiction": "US-FL",
        "category": "GENERAL",
        "legalForm": {
```
```
        },
        "registeredAt": {
          "id": "RA000603",
          "other": null
        },
        "registeredAs": "444750",
        "jurisdiction": "US-FL",
        "category": "GENERAL",
        "legalForm": {
          "id": "TRI2",
          "other": null
        },
        "associatedEntity": {
```
```
      "registration": {
        "initialRegistrationDate": "2012-06-06T15:55:00Z",
        "lastUpdateDate": "2025-12-30T16:32:06Z",
        "status": "ISSUED",
        "nextRenewalDate": "2027-01-05T11:16:55Z",
        "managingLou": "5493001KJTIIGC8Y1R12",
        "corroborationLevel": "FULLY_CORROBORATED",
        "validatedAt": {
          "id": "RA000603",
          "other": null
        },
        "validatedAs": "444750",
        "otherValidationAuthorities": []
```

### S10. GLEIF LEI record, Lennar Corporation
https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09
Retrieved: 2026-10-23T15:24:53Z
```
    "attributes": {
      "lei": "529900G61XVRLX5TJX09",
      "entity": {
        "legalName": {
          "name": "LENNAR CORPORATION",
          "language": "en-US"
        },
        "otherNames": [],
        "transliteratedOtherNames": [],
        "legalAddress": {
          "language": "en-US",
          "addressLines": [
            "c/o THE CORPORATION TRUST COMPANY, CORPORATION TRUST CENTER 1209 ORANGE ST"
          ],
```
```
        "legalAddress": {
          "language": "en-US",
          "addressLines": [
            "c/o THE CORPORATION TRUST COMPANY, CORPORATION TRUST CENTER 1209 ORANGE ST"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "WILMINGTON",
          "region": "US-DE",
          "country": "US",
          "postalCode": "19801"
        },
        "headquartersAddress": {
          "language": "en-US",
          "addressLines": [
            "700 Northwest 107th Avenue"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
```
```
        "headquartersAddress": {
          "language": "en-US",
          "addressLines": [
            "700 Northwest 107th Avenue"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "Miami",
          "region": "US-FL",
          "country": "US",
          "postalCode": "33172"
        },
        "registeredAt": {
          "id": "RA000602",
          "other": null
        },
        "registeredAs": "2272968",
        "jurisdiction": "US-DE",
        "category": "GENERAL",
        "legalForm": {
```
```
        },
        "registeredAt": {
          "id": "RA000602",
          "other": null
        },
        "registeredAs": "2272968",
        "jurisdiction": "US-DE",
        "category": "GENERAL",
        "legalForm": {
          "id": "8888",
          "other": "Corporation"
        },
        "associatedEntity": {
```
```
      "registration": {
        "initialRegistrationDate": "2019-01-02T11:24:40Z",
        "lastUpdateDate": "2021-07-16T05:04:45Z",
        "status": "LAPSED",
        "nextRenewalDate": "2020-01-02T11:24:40Z",
        "managingLou": "5299000J2N45DDNE4Y28",
        "corroborationLevel": "FULLY_CORROBORATED",
        "validatedAt": {
          "id": "RA000602",
          "other": null
        },
        "validatedAs": "2272968",
        "otherValidationAuthorities": []
```

### S11. GLEIF LEI record, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63
Retrieved: 2026-10-23T15:25:14Z
```
    "attributes": {
      "lei": "254900RHL9MEUS5NKX63",
      "entity": {
        "legalName": {
          "name": "NextEra Energy, Inc.",
          "language": "en"
        },
        "otherNames": [],
        "transliteratedOtherNames": [],
        "legalAddress": {
          "language": "en",
          "addressLines": [
            "C/O CORPORATION SERVICE COMPANY",
            "1201 HAYS STREET"
```
```
        "legalAddress": {
          "language": "en",
          "addressLines": [
            "C/O CORPORATION SERVICE COMPANY",
            "1201 HAYS STREET"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "TALLAHASSEE",
          "region": "US-FL",
          "country": "US",
          "postalCode": "32301"
        },
        "headquartersAddress": {
          "language": "en",
          "addressLines": [
            "700 UNIVERSE BLVD"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
```
```
        "headquartersAddress": {
          "language": "en",
          "addressLines": [
            "700 UNIVERSE BLVD"
          ],
          "addressNumber": null,
          "addressNumberWithinBuilding": null,
          "mailRouting": null,
          "city": "JUNO BEACH",
          "region": "US-FL",
          "country": "US",
          "postalCode": "33408"
        },
        "registeredAt": {
          "id": "RA000603",
          "other": null
        },
        "registeredAs": "M04961",
        "jurisdiction": "US-FL",
        "category": "GENERAL",
        "legalForm": {
```
```
        },
        "registeredAt": {
          "id": "RA000603",
          "other": null
        },
        "registeredAs": "M04961",
        "jurisdiction": "US-FL",
        "category": "GENERAL",
        "legalForm": {
          "id": "TRI2",
          "other": null
        },
        "associatedEntity": {
```
```
      "registration": {
        "initialRegistrationDate": "2024-02-26T08:29:55Z",
        "lastUpdateDate": "2026-02-13T15:36:14Z",
        "status": "ISSUED",
        "nextRenewalDate": "2027-02-26T08:29:55Z",
        "managingLou": "5493001KJTIIGC8Y1R12",
        "corroborationLevel": "FULLY_CORROBORATED",
        "validatedAt": {
          "id": "RA000603",
          "other": null
        },
        "validatedAs": "M04961",
        "otherValidationAuthorities": []
```

### S12. GLEIF direct-parent call, Jabil Inc.
https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669/direct-parent
Retrieved: 2026-10-23T15:24:16Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S13. GLEIF direct-parent reporting exception, Jabil Inc.
https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669/direct-parent-reporting-exception
Retrieved: 2026-10-23T15:24:20Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "5493000CGCQY2OQU7669",
      "category": "DIRECT_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NON_CONSOLIDATING",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669"
        }
      }
    }
```

### S14. GLEIF ultimate-parent call, Jabil Inc.
https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669/ultimate-parent
Retrieved: 2026-10-23T15:24:25Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S15. GLEIF ultimate-parent reporting exception, Jabil Inc.
https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669/ultimate-parent-reporting-exception
Retrieved: 2026-10-23T15:24:29Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "5493000CGCQY2OQU7669",
      "category": "ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NON_CONSOLIDATING",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669"
        }
      }
    }
```

### S16. GLEIF direct-parent call, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949/direct-parent
Retrieved: 2026-10-23T15:24:37Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S17. GLEIF direct-parent reporting exception, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949/direct-parent-reporting-exception
Retrieved: 2026-10-23T15:24:41Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "RGUZHJ05YTITL6D76949",
      "category": "DIRECT_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NON_CONSOLIDATING",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949"
        }
      }
    }
```

### S18. GLEIF ultimate-parent call, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949/ultimate-parent
Retrieved: 2026-10-23T15:24:45Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S19. GLEIF ultimate-parent reporting exception, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949/ultimate-parent-reporting-exception
Retrieved: 2026-10-23T15:24:49Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "RGUZHJ05YTITL6D76949",
      "category": "ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NON_CONSOLIDATING",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949"
        }
      }
    }
```

### S20. GLEIF direct-parent call, Lennar Corporation
https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09/direct-parent
Retrieved: 2026-10-23T15:24:57Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S21. GLEIF direct-parent reporting exception, Lennar Corporation
https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09/direct-parent-reporting-exception
Retrieved: 2026-10-23T15:25:02Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "529900G61XVRLX5TJX09",
      "category": "DIRECT_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NO_KNOWN_PERSON",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09"
        }
      }
    }
```

### S22. GLEIF ultimate-parent call, Lennar Corporation
https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09/ultimate-parent
Retrieved: 2026-10-23T15:25:06Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S23. GLEIF ultimate-parent reporting exception, Lennar Corporation
https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09/ultimate-parent-reporting-exception
Retrieved: 2026-10-23T15:25:10Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "529900G61XVRLX5TJX09",
      "category": "ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NO_KNOWN_PERSON",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09"
        }
      }
    }
```

### S24. GLEIF direct-parent call, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63/direct-parent
Retrieved: 2026-10-23T15:25:18Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S25. GLEIF direct-parent reporting exception, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63/direct-parent-reporting-exception
Retrieved: 2026-10-23T15:25:22Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "254900RHL9MEUS5NKX63",
      "category": "DIRECT_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NO_KNOWN_PERSON",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63"
        }
      }
    }
```

### S26. GLEIF ultimate-parent call, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63/ultimate-parent
Retrieved: 2026-10-23T15:25:26Z
```
{
  "errors": [
    {
      "status": "404",
      "title": "Resource not found",
      "detail": "Related resource not found"
    }
  ]
}
```

### S27. GLEIF ultimate-parent reporting exception, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63/ultimate-parent-reporting-exception
Retrieved: 2026-10-23T15:25:30Z
```
    "attributes": {
      "validFrom": null,
      "validTo": null,
      "lei": "254900RHL9MEUS5NKX63",
      "category": "ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT",
      "reason": "NO_KNOWN_PERSON",
      "reference": null
    },
    "relationships": {
      "lei-record": {
        "links": {
          "related": "https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63"
        }
      }
    }
```

### S28. SEC EDGAR company tickers file
https://www.sec.gov/files/company_tickers.json
Retrieved: 2026-10-23T15:19:07Z
```
  "488": {
    "cik_str": 898293,
    "ticker": "JBL",
    "title": "JABIL INC"
  },
  "489": {
    "cik_str": 1002910,
    "ticker": "AEE",
    "title": "AMEREN CORP"
  },
```
```
  "482": {
    "cik_str": 720005,
    "ticker": "RJF",
    "title": "RAYMOND JAMES FINANCIAL INC"
  },
  "483": {
    "cik_str": 1097864,
    "ticker": "ON",
    "title": "ON SEMICONDUCTOR CORP"
  },
```
```
  "653": {
    "cik_str": 920760,
    "ticker": "LEN",
    "title": "LENNAR CORP /NEW/"
  },
  "654": {
    "cik_str": 718940,
    "ticker": "BCE",
    "title": "BCE INC"
  },
```
```
  "95": {
    "cik_str": 753308,
    "ticker": "NEE",
    "title": "NEXTERA ENERGY INC"
  },
  "96": {
    "cik_str": 313616,
    "ticker": "DHR",
    "title": "DANAHER CORP /DE/"
  },
```

### S29. SEC EDGAR company name search, publix
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=publix&type=&dateb=&owner=include&count=10
Retrieved: 2026-10-23T15:19:37Z
```
 <tr>
 <td valign="top" scope="row"><a href="/cgi-bin/browse-edgar?action=getcompany&amp;CIK=0000926048&amp;owner=include&amp;count=10&amp;hidefilings=0">0000926048</a></td>
 <td scope="row">PUBLIX SUPER MARKETS INC PROFIT SHARING PLAN</td>
 <td valign="top" scope="row"><a href="/cgi-bin/browse-edgar?action=getcompany&amp;State=FL&amp;owner=include&amp;count=10&amp;hidefilings=0">FL</a></td>
 </tr>
 <tr class="evenRow">
 <td valign="top" scope="row"><a href="/cgi-bin/browse-edgar?action=getcompany&amp;CIK=0001351715&amp;owner=include&amp;count=10&amp;hidefilings=0">0001351715</a></td>
 <td scope="row">Publix Super Markets, Inc. 401(k) SMART Plan</td>
 <td valign="top" scope="row"><a href="/cgi-bin/browse-edgar?action=getcompany&amp;State=FL&amp;owner=include&amp;count=10&amp;hidefilings=0">FL</a></td>
 </tr>
 </table>
 </div>
</div>
<!-- END CONTENT -->
```

### S30. SEC EDGAR company submissions, Jabil Inc.
https://data.sec.gov/submissions/CIK0000898293.json
Retrieved: 2026-10-23T15:19:52Z
```
  "cik": "0000898293",
  "entityType": "operating",
  "sic": "3672",
  "sicDescription": "Printed Circuit Boards",
  "ownerOrg": "04 Manufacturing",
  "insiderTransactionForOwnerExists": 0,
  "insiderTransactionForIssuerExists": 1,
  "name": "JABIL INC",
  "tickers": [
    "JBL"
  ],
  "exchanges": [
    "NYSE"
  ],
  "ein": "381886260",
  "lei": null,
  "description": "",
```
```
    "NYSE"
  ],
  "ein": "381886260",
  "lei": null,
  "description": "",
  "website": "",
  "investorWebsite": "",
  "category": "Large accelerated filer",
  "fiscalYearEnd": "0831",
  "stateOfIncorporation": "DE",
  "stateOfIncorporationDescription": "DE",
  "addresses": {
    "mailing": {
      "street1": "10800 ROOSEVELT BOULEVARD NORTH",
```
```
  "formerNames": [
    {
      "name": "JABIL CIRCUIT INC",
      "from": "1996-07-15T04:00:00.000Z",
      "to": "2017-06-05T04:00:00.000Z"
    }
  ],
  "filings": {
    "recent": {
      "accessionNumber": [
        "0001225208-26-008484",
```

### S31. SEC EDGAR company submissions, Raymond James Financial, Inc.
https://data.sec.gov/submissions/CIK0000720005.json
Retrieved: 2026-10-23T15:19:56Z
```
  "cik": "0000720005",
  "entityType": "operating",
  "sic": "6211",
  "sicDescription": "Security Brokers, Dealers & Flotation Companies",
  "ownerOrg": "02 Finance",
  "insiderTransactionForOwnerExists": 1,
  "insiderTransactionForIssuerExists": 1,
  "name": "RAYMOND JAMES FINANCIAL INC",
  "tickers": [
    "RJF"
  ],
  "exchanges": [
    "NYSE"
  ],
  "ein": "591517485",
  "lei": null,
  "description": "",
```
```
    "NYSE"
  ],
  "ein": "591517485",
  "lei": null,
  "description": "",
  "website": "",
  "investorWebsite": "",
  "category": "Large accelerated filer",
  "fiscalYearEnd": "0930",
  "stateOfIncorporation": "FL",
  "stateOfIncorporationDescription": "FL",
  "addresses": {
    "mailing": {
      "street1": "880 CARILLON PKWY",
```
```
  "formerNames": [],
  "filings": {
    "recent": {
      "accessionNumber": [
        "0000720005-26-000077",
        "0000720005-26-000075",
        "0001225208-26-007407",
        "0001974078-26-000334",
        "0001225208-26-007342",
        "0001225208-26-007224",
        "0000720005-26-000073",
```

### S32. SEC EDGAR company submissions, Publix Super Markets, Inc.
https://data.sec.gov/submissions/CIK0000081061.json
Retrieved: 2026-10-23T15:20:00Z
```
  "cik": "0000081061",
  "entityType": "operating",
  "sic": "5411",
  "sicDescription": "Retail-Grocery Stores",
  "ownerOrg": "07 Trade & Services",
  "insiderTransactionForOwnerExists": 0,
  "insiderTransactionForIssuerExists": 1,
  "name": "PUBLIX SUPER MARKETS INC",
  "tickers": [],
  "exchanges": [],
  "ein": "590324412",
  "lei": null,
  "description": "",
  "website": "",
  "investorWebsite": "",
  "category": "Non-accelerated filer",
  "fiscalYearEnd": "1226",
```
```
  "tickers": [],
  "exchanges": [],
  "ein": "590324412",
  "lei": null,
  "description": "",
  "website": "",
  "investorWebsite": "",
  "category": "Non-accelerated filer",
  "fiscalYearEnd": "1226",
  "stateOfIncorporation": "FL",
  "stateOfIncorporationDescription": "FL",
  "addresses": {
    "mailing": {
      "street1": "3300 PUBLIX CORPORATE PARKWAY",
```
```
  "formerNames": [],
  "filings": {
    "recent": {
      "accessionNumber": [
        "0000081061-26-000093",
        "0000081061-26-000091",
        "0000081061-26-000089",
        "0000081061-26-000088",
        "0000081061-26-000083",
        "0000081061-26-000080",
        "0000081061-26-000078",
```

### S33. SEC EDGAR company submissions, Lennar Corporation
https://data.sec.gov/submissions/CIK0000920760.json
Retrieved: 2026-10-23T15:20:04Z
```
  "cik": "0000920760",
  "entityType": "operating",
  "sic": "1520",
  "sicDescription": "General Bldg Contractors - Residential Bldgs",
  "ownerOrg": "05 Real Estate & Construction",
  "insiderTransactionForOwnerExists": 1,
  "insiderTransactionForIssuerExists": 1,
  "name": "LENNAR CORP /NEW/",
  "tickers": [
    "LEN",
    "LEN-B"
  ],
  "exchanges": [
    "NYSE",
    "NYSE"
  ],
  "ein": "954337490",
```
```
    "NYSE"
  ],
  "ein": "954337490",
  "lei": null,
  "description": "",
  "website": "",
  "investorWebsite": "",
  "category": "Large accelerated filer",
  "fiscalYearEnd": "1130",
  "stateOfIncorporation": "DE",
  "stateOfIncorporationDescription": "DE",
  "addresses": {
    "mailing": {
      "street1": "5505 WATERFORD DISTRICT DRIVE",
```
```
  "formerNames": [
    {
      "name": "PACIFIC GREYSTONE CORP /DE/",
      "from": "1996-06-27T04:00:00.000Z",
      "to": "1997-09-26T04:00:00.000Z"
    }
  ],
  "filings": {
    "recent": {
      "accessionNumber": [
        "0001193125-26-422909",
```

### S34. SEC EDGAR company submissions, NextEra Energy, Inc.
https://data.sec.gov/submissions/CIK0000753308.json
Retrieved: 2026-10-23T15:20:09Z
```
  "cik": "0000753308",
  "entityType": "operating",
  "sic": "4911",
  "sicDescription": "Electric Services",
  "ownerOrg": "01 Energy & Transportation",
  "insiderTransactionForOwnerExists": 1,
  "insiderTransactionForIssuerExists": 1,
  "name": "NEXTERA ENERGY INC",
  "tickers": [
    "NEE",
    "NEE-PN",
    "NEE-PS",
    "NEE-PT",
    "NEE-PU",
    "NEE-PV",
    "NEE-PW"
  ],
```
```
    "NYSE"
  ],
  "ein": "592449419",
  "lei": null,
  "description": "",
  "website": "",
  "investorWebsite": "",
  "category": "Large accelerated filer",
  "fiscalYearEnd": "1231",
  "stateOfIncorporation": "FL",
  "stateOfIncorporationDescription": "FL",
  "addresses": {
    "mailing": {
      "street1": "P O BOX 14000",
```
```
  "formerNames": [
    {
      "name": "FPL GROUP INC",
      "from": "1994-02-28T05:00:00.000Z",
      "to": "2010-05-21T04:00:00.000Z"
    }
  ],
  "filings": {
    "recent": {
      "accessionNumber": [
        "0000753308-26-000081",
```

### S35. GLEIF LEI record, entity status field, Jabil Inc.
https://api.gleif.org/api/v1/lei-records/5493000CGCQY2OQU7669
Retrieved: 2026-10-23T15:39:36Z
```
        "registeredAt": {
          "id": "RA000602",
          "other": null
        },
        "registeredAs": "2288884",
        "jurisdiction": "US-DE",
        "category": "GENERAL",
        "legalForm": {
          "id": "XTIQ",
          "other": null
        },
        "associatedEntity": {
          "lei": null,
          "name": null
        },
        "status": "ACTIVE",
        "expiration": {
          "date": null,
          "reason": null
        },
        "successorEntity": {
```

### S36. GLEIF LEI record, entity status field, Raymond James Financial, Inc.
https://api.gleif.org/api/v1/lei-records/RGUZHJ05YTITL6D76949
Retrieved: 2026-10-23T15:39:37Z
```
        "registeredAt": {
          "id": "RA000603",
          "other": null
        },
        "registeredAs": "444750",
        "jurisdiction": "US-FL",
        "category": "GENERAL",
        "legalForm": {
          "id": "TRI2",
          "other": null
        },
        "associatedEntity": {
          "lei": null,
          "name": null
        },
        "status": "ACTIVE",
        "expiration": {
          "date": null,
          "reason": null
        },
        "successorEntity": {
```

### S37. GLEIF LEI record, entity status field, Lennar Corporation
https://api.gleif.org/api/v1/lei-records/529900G61XVRLX5TJX09
Retrieved: 2026-10-23T15:39:38Z
```
        "registeredAt": {
          "id": "RA000602",
          "other": null
        },
        "registeredAs": "2272968",
        "jurisdiction": "US-DE",
        "category": "GENERAL",
        "legalForm": {
          "id": "8888",
          "other": "Corporation"
        },
        "associatedEntity": {
          "lei": null,
          "name": null
        },
        "status": "ACTIVE",
        "expiration": {
          "date": null,
          "reason": null
        },
        "successorEntity": {
```

### S38. GLEIF LEI record, entity status field, NextEra Energy, Inc.
https://api.gleif.org/api/v1/lei-records/254900RHL9MEUS5NKX63
Retrieved: 2026-10-23T15:39:40Z
```
        "registeredAt": {
          "id": "RA000603",
          "other": null
        },
        "registeredAs": "M04961",
        "jurisdiction": "US-FL",
        "category": "GENERAL",
        "legalForm": {
          "id": "TRI2",
          "other": null
        },
        "associatedEntity": {
          "lei": null,
          "name": null
        },
        "status": "ACTIVE",
        "expiration": {
          "date": null,
          "reason": null
        },
        "successorEntity": {
```
