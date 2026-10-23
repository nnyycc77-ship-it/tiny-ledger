# Wage benchmark for five tech occupations in the Tampa-St. Petersburg-Clearwater, FL metro from BLS OEWS

This work was unattended agent work and observation of public records only, with no contact with anyone (no emails, calls, messages or test sends).

Every figure taken from a source appears in a raw excerpt in section 4, directly under the exact query it came from. Computed figures are labelled as computed and show their arithmetic; their inputs are excerpted.

## 1. METHOD

Source and release. All values are from the U.S. Bureau of Labor Statistics (BLS) Occupational Employment and Wage Statistics (OEWS) program, latest annual release: the May 2025 OEWS estimates (reference period May 2025). The BLS Tampa area news release for this release is 26-1165-ATL, dated Tuesday, July 07, 2026 (source Q0 in section 4, which also prints the area name used below). The API responses print the observation year as 2025, period A01 (Annual).

Areas. Metro area, exactly as BLS prints it: Tampa-St. Petersburg-Clearwater, FL Metropolitan Statistical Area; area type M, area code 0045300 (the code appears in every metro series ID in sources Q1, Q3, Q5, Q7 and Q9, and in the BLS data listing address data.bls.gov/oes/#/area/0045300/2025 quoted in Q0). National area: area type N, area code 0000000, printed as National in the dataset.

Series construction. Each value is one BLS public data API series, built as: OE (survey) + U (not seasonally adjusted) + area type (M or N) + area code (0045300 or 0000000) + industry code 000000 + six digit occupation code (the SOC code with the dash removed) + two digit data type code. Data type codes used: 01 employment, 03 hourly mean wage, 04 annual mean wage, 11 annual 10th percentile wage, 12 annual 25th percentile wage, 13 annual median wage, 14 annual 75th percentile wage, 15 annual 90th percentile wage. One POST query per occupation and area carried its eight series (sources Q1 to Q10), with startyear and endyear both 2025, so each response holds exactly the one annual observation used. No registration key was used, so no key appears anywhere in this file and there is nothing to redact.

Datatype check (computed). The decoding above was verified against the returned values before use: in all ten rows the annual percentile values rise in code order (11 below 12 below 13 below 14 below 15), and the annual mean (code 04) equals the hourly mean (code 03) times 2,080 hours after rounding, within 11 dollars in every row, which is the relation the BLS footnote quoted in Q0 prints for annual wages. No value in the 80 series was suppressed or top coded: every series returned a numeric 2025 value, so no BLS symbol such as # appears in the dataset and no comparison had to be skipped.

Retrieval. The ten API queries were run on 2026-10-23 between 22:27:38 UTC and 22:27:56 UTC; the exact UTC retrieval time of each query is printed in the dataset row it produced and again under its source entry in section 4. Source Q0 was retrieved 2026-10-23T22:29Z.

## 2. DATASET

```csv
soc_code,occupation_title,area,employment,mean_hourly_wage,mean_annual_wage,pct10_annual,pct25_annual,median_annual,pct75_annual,pct90_annual,query_url,retrieved_at_utc
15-1252,Software Developers,"Tampa-St. Petersburg-Clearwater, FL",14230,64.24,133630,78480,100450,130450,165430,207330,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:38Z
15-1252,Software Developers,National,1687890,71.20,148100,82460,105210,135980,171980,214670,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:41Z
15-1211,Computer Systems Analysts,"Tampa-St. Petersburg-Clearwater, FL",7100,53.78,111870,67240,83980,105080,134260,161720,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:43Z
15-1211,Computer Systems Analysts,National,519530,55.10,114610,67340,82860,105850,134110,167710,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:45Z
15-1212,Information Security Analysts,"Tampa-St. Petersburg-Clearwater, FL",2460,58.42,121510,76810,87120,118970,151040,171390,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:47Z
15-1212,Information Security Analysts,National,190650,63.71,132510,75090,97810,129180,163500,199850,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:49Z
15-1244,Network and Computer Systems Administrators,"Tampa-St. Petersburg-Clearwater, FL",4720,49.14,102210,62280,79990,101560,119880,153200,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:51Z
15-1244,Network and Computer Systems Administrators,National,314340,49.85,103680,62640,78010,99130,126640,155050,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:53Z
15-1232,Computer User Support Specialists,"Tampa-St. Petersburg-Clearwater, FL",7410,32.00,66570,40330,48110,61050,78230,102810,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:55Z
15-1232,Computer User Support Specialists,National,717190,32.37,67330,40980,49000,61860,79040,100540,https://api.bls.gov/publicAPI/v2/timeseries/data/,2026-10-23T22:27:56Z
```

## 3. COMPARISON

Metro median annual wage as a percent of the national median annual wage, per occupation (computed from the dataset medians in section 2; both inputs are excerpted under the row sources in section 4):

- 15-1252 Software Developers: 130450 / 135980 x 100 = 95.93 percent (metro median 130450, national median 135980).
- 15-1211 Computer Systems Analysts: 105080 / 105850 x 100 = 99.27 percent (metro median 105080, national median 105850).
- 15-1212 Information Security Analysts: 118970 / 129180 x 100 = 92.10 percent (metro median 118970, national median 129180).
- 15-1244 Network and Computer Systems Administrators: 101560 / 99130 x 100 = 102.45 percent (metro median 101560, national median 99130).
- 15-1232 Computer User Support Specialists: 61050 / 61860 x 100 = 98.69 percent (metro median 61050, national median 61860).

No median was suppressed, so no occupation is skipped in this section.

## 4. SOURCES

For the API sources Q1 to Q10: source name is the BLS public data API (OEWS survey), the endpoint and the exact JSON request body are printed for each query, JSON responses were pretty printed with 2 space indentation before excerpting, and each excerpt below is 10 to 30 consecutive lines of that pretty printed response, one excerpt per series, showing the series ID, the 2025 annual observation and the value used. For Q0, an HTML page, the excerpts are the page visible text as extracted, printed in extracted order.

### Q0. BLS Tampa area news release for the May 2025 OEWS release (release date, reference period, area name and area listing address).

Source name: U.S. Bureau of Labor Statistics, Southeast Information Office news release, Occupational Employment and Wages in Tampa-St. Petersburg-Clearwater, FL, May 2025 (HTML page, visible text as extracted)

Exact query URL: https://www.bls.gov/regions/southeast/news-release/occupationalemploymentandwages_tampa.htm

UTC retrieval time: 2026-10-23T22:29Z

```
News Release Information

26-1165-ATL

Tuesday, July 07, 2026

Workers in the Tampa-St. Petersburg-Clearwater, FL Metropolitan Statistical Area had an average (mean) hourly wage of $31.96 in May 2025, compared to the
nationwide average of $33.54, the U.S. Bureau of Labor Statistics reported today. Regional Commissioner Victoria G. Lee noted that higher paying major
occupational groups included management ($66.50), computer and mathematical ($52.34), and legal ($51.03). Lower paying occupational groups included building and
grounds cleaning and maintenance ($18.07) and food preparation and serving related ($18.23). (See table A.)
```

```
**Metropolitan area definitions**

The substate area data published in this release reflect the standards and definitions established by the U.S. Office of Management and Budget.

The **Tampa-St. Petersburg-Clearwater, FL Metropolitan Statistical Area** includes Hernando County, Hillsborough County, Pasco County, and Pinellas County.

**For more information**

Answers to frequently asked questions about the OEWS data, as well as general program documentation, are available on the OEWS website.

If you are deaf, hard of hearing, or have a speech disability, please dial 7-1-1 to access telecommunications relay services.
```

```
| Proofreaders and copy markers | 30 | 0.82 | 18.03 | 37,510 |

| Office and administrative support workers, all other | 3,400 | 1.90 | 20.41 | 42,450 |

| Footnotes:   (1) For a complete listing of all detailed occupations in the Tampa-St. Petersburg-Clearwater, FL Metropolitan Statistical Area, see
data.bls.gov/oes/#/area/0045300/2025.   (2) Estimates for detailed occupations may not sum to the totals due to rounding, and because the totals may include
occupations that are not shown separately. Estimates do not include self-employed workers.   (3) The location quotient is the ratio of the area concentration of
occupational employment to the national average concentration. A location quotient greater than one indicates the occupation has a higher share of employment
than average, and a location quotient less than one indicates the occupation is less prevalent in the area than average.   (4) Annual wages have been calculated
by multiplying the hourly mean wage by a 'year-round, full-time' hours figure of 2,080 hours; for those occupations where there is not an hourly mean wage
published, the annual wage has been directly calculated from the reported survey data.   (5) Estimate not released. | | | | |
```

### Q1. 15-1252 Software Developers, Tampa-St. Petersburg-Clearwater, FL: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUM004530000000015125201", "OEUM004530000000015125203", "OEUM004530000000015125204", "OEUM004530000000015125211", "OEUM004530000000015125212", "OEUM004530000000015125213", "OEUM004530000000015125214", "OEUM004530000000015125215"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:38Z

Series OEUM004530000000015125201 (employment):

```
      {
        "seriesID": "OEUM004530000000015125201",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "14230",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125203 (hourly mean wage):

```
      {
        "seriesID": "OEUM004530000000015125203",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "64.24",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125204 (annual mean wage):

```
      {
        "seriesID": "OEUM004530000000015125204",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "133630",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125211 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015125211",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "78480",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125212 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015125212",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "100450",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125213 (annual median wage):

```
      {
        "seriesID": "OEUM004530000000015125213",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "130450",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125214 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015125214",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "165430",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015125215 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015125215",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "207330",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q2. 15-1252 Software Developers, National: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUN000000000000015125201", "OEUN000000000000015125203", "OEUN000000000000015125204", "OEUN000000000000015125211", "OEUN000000000000015125212", "OEUN000000000000015125213", "OEUN000000000000015125214", "OEUN000000000000015125215"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:41Z

Series OEUN000000000000015125201 (employment):

```
      {
        "seriesID": "OEUN000000000000015125201",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "1687890",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125203 (hourly mean wage):

```
      {
        "seriesID": "OEUN000000000000015125203",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "71.20",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125204 (annual mean wage):

```
      {
        "seriesID": "OEUN000000000000015125204",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "148100",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125211 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015125211",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "82460",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125212 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015125212",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "105210",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125213 (annual median wage):

```
      {
        "seriesID": "OEUN000000000000015125213",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "135980",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125214 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015125214",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "171980",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015125215 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015125215",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "214670",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q3. 15-1211 Computer Systems Analysts, Tampa-St. Petersburg-Clearwater, FL: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUM004530000000015121101", "OEUM004530000000015121103", "OEUM004530000000015121104", "OEUM004530000000015121111", "OEUM004530000000015121112", "OEUM004530000000015121113", "OEUM004530000000015121114", "OEUM004530000000015121115"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:43Z

Series OEUM004530000000015121101 (employment):

```
      {
        "seriesID": "OEUM004530000000015121101",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "7100",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121103 (hourly mean wage):

```
      {
        "seriesID": "OEUM004530000000015121103",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "53.78",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121104 (annual mean wage):

```
      {
        "seriesID": "OEUM004530000000015121104",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "111870",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121111 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121111",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "67240",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121112 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121112",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "83980",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121113 (annual median wage):

```
      {
        "seriesID": "OEUM004530000000015121113",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "105080",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121114 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121114",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "134260",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121115 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121115",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "161720",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q4. 15-1211 Computer Systems Analysts, National: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUN000000000000015121101", "OEUN000000000000015121103", "OEUN000000000000015121104", "OEUN000000000000015121111", "OEUN000000000000015121112", "OEUN000000000000015121113", "OEUN000000000000015121114", "OEUN000000000000015121115"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:45Z

Series OEUN000000000000015121101 (employment):

```
      {
        "seriesID": "OEUN000000000000015121101",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "519530",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121103 (hourly mean wage):

```
      {
        "seriesID": "OEUN000000000000015121103",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "55.10",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121104 (annual mean wage):

```
      {
        "seriesID": "OEUN000000000000015121104",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "114610",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121111 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121111",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "67340",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121112 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121112",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "82860",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121113 (annual median wage):

```
      {
        "seriesID": "OEUN000000000000015121113",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "105850",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121114 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121114",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "134110",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121115 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121115",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "167710",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q5. 15-1212 Information Security Analysts, Tampa-St. Petersburg-Clearwater, FL: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUM004530000000015121201", "OEUM004530000000015121203", "OEUM004530000000015121204", "OEUM004530000000015121211", "OEUM004530000000015121212", "OEUM004530000000015121213", "OEUM004530000000015121214", "OEUM004530000000015121215"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:47Z

Series OEUM004530000000015121201 (employment):

```
      {
        "seriesID": "OEUM004530000000015121201",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "2460",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121203 (hourly mean wage):

```
      {
        "seriesID": "OEUM004530000000015121203",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "58.42",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121204 (annual mean wage):

```
      {
        "seriesID": "OEUM004530000000015121204",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "121510",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121211 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121211",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "76810",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121212 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121212",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "87120",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121213 (annual median wage):

```
      {
        "seriesID": "OEUM004530000000015121213",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "118970",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121214 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121214",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "151040",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015121215 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015121215",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "171390",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q6. 15-1212 Information Security Analysts, National: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUN000000000000015121201", "OEUN000000000000015121203", "OEUN000000000000015121204", "OEUN000000000000015121211", "OEUN000000000000015121212", "OEUN000000000000015121213", "OEUN000000000000015121214", "OEUN000000000000015121215"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:49Z

Series OEUN000000000000015121201 (employment):

```
      {
        "seriesID": "OEUN000000000000015121201",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "190650",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121203 (hourly mean wage):

```
      {
        "seriesID": "OEUN000000000000015121203",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "63.71",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121204 (annual mean wage):

```
      {
        "seriesID": "OEUN000000000000015121204",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "132510",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121211 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121211",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "75090",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121212 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121212",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "97810",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121213 (annual median wage):

```
      {
        "seriesID": "OEUN000000000000015121213",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "129180",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121214 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121214",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "163500",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015121215 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015121215",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "199850",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q7. 15-1244 Network and Computer Systems Administrators, Tampa-St. Petersburg-Clearwater, FL: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUM004530000000015124401", "OEUM004530000000015124403", "OEUM004530000000015124404", "OEUM004530000000015124411", "OEUM004530000000015124412", "OEUM004530000000015124413", "OEUM004530000000015124414", "OEUM004530000000015124415"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:51Z

Series OEUM004530000000015124401 (employment):

```
      {
        "seriesID": "OEUM004530000000015124401",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "4720",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124403 (hourly mean wage):

```
      {
        "seriesID": "OEUM004530000000015124403",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "49.14",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124404 (annual mean wage):

```
      {
        "seriesID": "OEUM004530000000015124404",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "102210",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124411 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015124411",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "62280",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124412 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015124412",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "79990",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124413 (annual median wage):

```
      {
        "seriesID": "OEUM004530000000015124413",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "101560",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124414 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015124414",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "119880",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015124415 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015124415",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "153200",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q8. 15-1244 Network and Computer Systems Administrators, National: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUN000000000000015124401", "OEUN000000000000015124403", "OEUN000000000000015124404", "OEUN000000000000015124411", "OEUN000000000000015124412", "OEUN000000000000015124413", "OEUN000000000000015124414", "OEUN000000000000015124415"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:53Z

Series OEUN000000000000015124401 (employment):

```
      {
        "seriesID": "OEUN000000000000015124401",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "314340",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124403 (hourly mean wage):

```
      {
        "seriesID": "OEUN000000000000015124403",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "49.85",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124404 (annual mean wage):

```
      {
        "seriesID": "OEUN000000000000015124404",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "103680",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124411 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015124411",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "62640",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124412 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015124412",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "78010",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124413 (annual median wage):

```
      {
        "seriesID": "OEUN000000000000015124413",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "99130",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124414 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015124414",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "126640",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015124415 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015124415",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "155050",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q9. 15-1232 Computer User Support Specialists, Tampa-St. Petersburg-Clearwater, FL: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUM004530000000015123201", "OEUM004530000000015123203", "OEUM004530000000015123204", "OEUM004530000000015123211", "OEUM004530000000015123212", "OEUM004530000000015123213", "OEUM004530000000015123214", "OEUM004530000000015123215"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:55Z

Series OEUM004530000000015123201 (employment):

```
      {
        "seriesID": "OEUM004530000000015123201",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "7410",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123203 (hourly mean wage):

```
      {
        "seriesID": "OEUM004530000000015123203",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "32.00",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123204 (annual mean wage):

```
      {
        "seriesID": "OEUM004530000000015123204",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "66570",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123211 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015123211",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "40330",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123212 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015123212",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "48110",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123213 (annual median wage):

```
      {
        "seriesID": "OEUM004530000000015123213",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "61050",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123214 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015123214",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "78230",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUM004530000000015123215 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUM004530000000015123215",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "102810",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```

### Q10. 15-1232 Computer User Support Specialists, National: the eight OEWS series for this dataset row.

Source name: BLS public data API, OEWS survey (api.bls.gov)

Endpoint (POST): https://api.bls.gov/publicAPI/v2/timeseries/data/

Exact JSON request body: {"seriesid": ["OEUN000000000000015123201", "OEUN000000000000015123203", "OEUN000000000000015123204", "OEUN000000000000015123211", "OEUN000000000000015123212", "OEUN000000000000015123213", "OEUN000000000000015123214", "OEUN000000000000015123215"], "startyear": "2025", "endyear": "2025"}

UTC retrieval time: 2026-10-23T22:27:56Z

Series OEUN000000000000015123201 (employment):

```
      {
        "seriesID": "OEUN000000000000015123201",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "717190",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123203 (hourly mean wage):

```
      {
        "seriesID": "OEUN000000000000015123203",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "32.37",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123204 (annual mean wage):

```
      {
        "seriesID": "OEUN000000000000015123204",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "67330",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123211 (annual 10th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015123211",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "40980",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123212 (annual 25th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015123212",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "49000",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123213 (annual median wage):

```
      {
        "seriesID": "OEUN000000000000015123213",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "61860",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123214 (annual 75th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015123214",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "79040",
            "footnotes": [
              {}
            ]
          }
        ]
      },
```

Series OEUN000000000000015123215 (annual 90th percentile wage):

```
      {
        "seriesID": "OEUN000000000000015123215",
        "data": [
          {
            "year": "2025",
            "period": "A01",
            "periodName": "Annual",
            "latest": "true",
            "value": "100540",
            "footnotes": [
              {}
            ]
          }
        ]
      }
```
