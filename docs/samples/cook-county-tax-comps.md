# Sample of delivered work: Cook County property tax comps report

| | |
| --- | --- |
| What this is | A sample of a report delivered on Synmerco (bid 897), shown in full as delivered |
| Job type | Cook County property tax comps report |
| Delivery date | 2026-10-23 (the date of the owner's commit adding the delivery, `04ba970` "Deliver Synmerco bid 897 Cook County tax comps (intent f5140faa)"; every query in it was retrieved on 2026-10-23 UTC) |
| Delivered file | [`deliveries/tax-comps-f5140faa-9527-4e30-8c10-441b62999811.md`](../../deliveries/tax-comps-f5140faa-9527-4e30-8c10-441b62999811.md), sha256 `ad70a07cb86c5607bd59f684401214f36cd42501716c75e08be5c3e2694f77ef` |
| More services | [Services catalog](../services-catalog.md) |

Everything below the line is the delivered report, copied in full,
byte for byte. Nothing is added, removed, reworded or recalculated:
`tools/tests/test_samples.py` checks that the text below the line
equals the delivered file and that its sha256 matches the one above.

---
# Cook County commercial valuation: subject value per square foot and comparable uniformity analysis

This is analysis only, not an appraisal and not legal or tax advice.

This work was unattended agent work and observation of public records only, with no contact with anyone (no emails, calls, messages or test sends).

Decimals used: dollar totals are rounded to 2 decimals (cents) and per square foot values are shown rounded to 2 decimals in the tables; the uniformity figures in section 3 are computed from the unrounded values printed by the source and then rounded to 2 decimals. Every figure taken from a source appears in a raw excerpt in section 4, directly under the exact query URL it came from.

## 1. SUBJECT

Year used: 2025. The subject query (source Q1 in section 4) returned exactly two rows for keypin 01-02-202-045-0000, one for 2025 and one for 2022, so 2025 is the latest year the subject has in 2021 to 2025. There is only one subject row in 2025, so the rule for choosing the largest building square feet row among several rows in the year used does not change the record; the other row (2022, building square feet 9586.0, printed property type/use "Retail-Storefront") is noted here and appears in the Q1 excerpt.

| Field | Value |
|---|---|
| Keypin | 01-02-202-045-0000 |
| Address (as printed) | 340  LAGESCHULTE BARRINGTON |
| Township | Barrington |
| Class (field class_es, as printed) | 5-17 |
| Property type/use (2025 field subclass2, as printed) | 76:RETAIL-SINGLE TENANT |
| Building square feet (field bldgsf) | 8,273 (printed 8273.0) |
| Assessor market value field printed for 2025 (field finalmarketvalue_sf) | 103.05280753443097 dollars per building square foot |
| Market value, total (computed, see below) | $852,555.88 |
| Market value per building square foot (computed) | $103.05 |

Two field facts about the 2025 data, proven by source Q2 in section 4: in 2025 the dataset prints no total market value field and no property_type_use field for any record (count of finalmarketvalue is 0 and count of property_type_use is 0 out of 13,343 records in 2025, while count of finalmarketvalue_sf is 11,566). The final market value field the 2025 records do print is finalmarketvalue_sf, so the total market value and the value per square foot are computed from it as follows, and the property type/use for 2025 is taken from the field the 2025 records print for use, subclass2.

Total market value arithmetic: finalmarketvalue_sf 103.05280753443097 x building square feet 8,273 = 852555.8767, rounded to $852,555.88.

Market value per building square foot arithmetic: 852555.8767 / 8,273 = 103.05280753443097, which is the printed finalmarketvalue_sf, rounded to $103.05 per square foot.

## 2. COMPARABLES

Query (source Q3 in section 4): the same dataset, year 2025, township Barrington, subclass2 "76:RETAIL-SINGLE TENANT" (the subject property type/use printed for 2025), ordered by keypin, limit 100. Exact query URL:

https://data.cookcountyil.gov/resource/csik-bsws.json?year=2025&township=Barrington&subclass2=76%3ARETAIL-SINGLE+TENANT&%24limit=100&%24order=keypin

Candidate count: the query returned 17 records. One of them is the subject itself, leaving 16 candidate records. Records excluded for blank or zero building square feet or blank or zero market value: 0. The 10 records closest in building square feet to the subject 8,273 square feet are listed below in order of closeness (difference in building square feet shown; ties would be ordered by keypin ascending, and no tie occurs in the 10). Each comparable total market value is computed as its printed finalmarketvalue_sf times its building square feet, with the multiplication shown under the table.

| # | Keypin | Address (as printed) | Class | Building sq ft | Difference from subject sq ft | Market value (total, computed) | Market value per building sq ft |
|---|---|---|---|---|---|---|---|
| 1 | 01-01-100-012-0000 | 123 W MAIN BARRINGTON | 5-92 | 5,024 | 3,249 | $828,582.65 | $164.92 |
| 2 | 01-02-204-001-0000 | 201  LAGESCHULTE BARRINGTON | 5-17 | 4,961 | 3,312 | $647,351.15 | $130.49 |
| 3 | 01-01-211-029-0000 | 860 S NORTHWEST BARRINGTON | 5-17 | 4,500 | 3,773 | $733,995.62 | $163.11 |
| 4 | 01-01-202-044-0000 | 181 S NORTHWEST BARRINGTON | 5-17 | 4,060 | 4,213 | $596,003.32 | $146.80 |
| 5 | 01-33-209-010-0000 | 100 W HIGGINS SOUTH BARRINGTON | 5-17 | 13,025 | 4,752 | $2,115,331.52 | $162.41 |
| 6 | 01-01-200-001-0000 | 325 E MAIN BARRINGTON | 5-92 | 3,493 | 4,780 | $569,742.35 | $163.11 |
| 7 | 01-01-101-021-0000 | 125 S HOUGH BARRINGTON | 5-17 | 2,428 | 5,845 | $533,917.55 | $219.90 |
| 8 | 01-01-105-001-0000 | 201 S COOK BARRINGTON | 5-92 | 2,230 | 6,043 | $362,435.43 | $162.53 |
| 9 | 01-32-400-029-0000 | 5251  PRAIRIE STONE HOFFMAN ESTATES | 5-17 | 14,376 | 6,103 | $1,594,591.81 | $110.92 |
| 10 | 01-01-105-002-0000 | 205 S COOK BARRINGTON | 5-92 | 2,095 | 6,178 | $340,494.45 | $162.53 |

Comparable total market value arithmetic (printed finalmarketvalue_sf x building square feet):

1. 01-01-100-012-0000: 164.924890272743 x 5,024 = $828,582.65
2. 01-02-204-001-0000: 130.48803693568607 x 4,961 = $647,351.15
3. 01-01-211-029-0000: 163.110137282362 x 4,500 = $733,995.62
4. 01-01-202-044-0000: 146.79884848132903 x 4,060 = $596,003.32
5. 01-33-209-010-0000: 162.405491131231 x 13,025 = $2,115,331.52
6. 01-01-200-001-0000: 163.10974760705798 x 3,493 = $569,742.35
7. 01-01-101-021-0000: 219.90014269900797 x 2,428 = $533,917.55
8. 01-01-105-001-0000: 162.52709733955402 x 2,230 = $362,435.43
9. 01-32-400-029-0000: 110.920410007836 x 14,376 = $1,594,591.81
10. 01-01-105-002-0000: 162.527183238515 x 2,095 = $340,494.45

## 3. UNIFORMITY

Comparable values per building square foot, sorted low to high (unrounded printed finalmarketvalue_sf values):

110.920410007836, 130.48803693568607, 146.79884848132903, 162.405491131231, 162.52709733955402, 162.527183238515, 163.10974760705798, 163.110137282362, 164.924890272743, 219.90014269900797

Median arithmetic: with 10 comparables the median is the mean of the 5th and 6th sorted values: (162.52709733955402 + 162.527183238515) / 2 = 162.5271402890345, rounded to $162.53 per square foot.

Mean arithmetic: (164.924890272743 + 130.48803693568607 + 163.110137282362 + 146.79884848132903 + 162.405491131231 + 163.10974760705798 + 219.90014269900797 + 162.52709733955402 + 110.920410007836 + 162.527183238515) / 10 = 1586.7119849953222 / 10 = 158.6711984995322, rounded to $158.67 per square foot. (The addends are in comparable table order.)

Subject percent above or below the median arithmetic: (103.05280753443097 / 162.5271402890345 - 1) x 100 = -36.5935 percent, rounded to 36.59 percent below the median. The subject value per square foot of $103.05 is therefore 36.59% below the comparable median of $162.53.

Subject value implied at the median arithmetic: median 162.5271402890345 x subject building square feet 8,273 = 1344587.0316, rounded to $1,344,587.03. Against the subject computed total market value of $852,555.88, the implied value at the comparable median is $492,031.15 higher.

## 4. SOURCES

Source for every query: Cook County Assessor commercial valuation data, Cook County open data portal (Socrata, dataset csik-bsws, no key). In the excerpts, JSON is pretty printed at 2 space indent before excerpting, each excerpt block holds 10 to 30 consecutive lines of that text (a response shorter than 10 lines is quoted whole), and no person's name appears in any response, so no excerpt needed redaction.

### Q0. Dataset inspection query, first record, used to learn the real field names printed by the dataset (year, keypin, township, class_es, property_type_use, bldgsf, finalmarketvalue, finalmarketvalue_sf).

Source name: Cook County Assessor commercial valuation data (Cook County open data portal, Socrata dataset csik-bsws)

Exact query URL: https://data.cookcountyil.gov/resource/csik-bsws.json?$limit=1

UTC retrieval time: 2026-10-23T14:41:37Z

```
[
  {
    "keypin": "01-02-202-045-0000",
    "pins": "01-02-202-045-0000",
    "year": "2022",
    "township": "Barrington",
    "sheet": "5-17s",
    "class_es": "5-17",
    "address": "340  LAGESCHULTE BARRINGTON",
    "adj_rent_sf": "7.776000000000001",
    "bldgsf": "9586.0",
    "caprate": "0.09",
    "excesslandval": "0.0",
    "exp": "0.15000000000000002",
    "finalmarketvalue": "633366.1919999999",
    "finalmarketvalue_sf": "66.07199999999999",
    "incomemarketvalue": "66.096",
    "investmentrating": "D",
    "landsf": "20944.0",
    "noi": "57023.66303999999",
    "pgi": "74540.73599999999",
    "property_type_use": "Retail-Storefront",
    "salecompmarketvalue_sf": "66.048",
    "vacancy": "0.1",
    "yearbuilt": "1975.0"
  }
]
```

### Q1. Subject query, all rows for the subject keypin, newest year first. Used for the year used and every subject field in section 1.

Source name: Cook County Assessor commercial valuation data (Cook County open data portal, Socrata dataset csik-bsws)

Exact query URL: https://data.cookcountyil.gov/resource/csik-bsws.json?keypin=01-02-202-045-0000&%24order=year+DESC&%24limit=100

UTC retrieval time: 2026-10-23T14:41:39Z

```
[
  {
    "keypin": "01-02-202-045-0000",
    "pins": "01-02-202-045-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "340  LAGESCHULTE BARRINGTON",
    "adj_rent_sf": "18.144000000000002",
    "bldgsf": "8273.0",
    "caprate": "0.0825",
    "egi": "142600.0464",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.5067613117521479",
    "finalmarketvalue_sf": "103.05280753443097",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "20944.0",
    "noi": "70335.8598304188",
    "pgi": "150105.312",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
```

```
  {
    "keypin": "01-02-202-045-0000",
    "pins": "01-02-202-045-0000",
    "year": "2022",
    "township": "Barrington",
    "sheet": "5-17s",
    "class_es": "5-17",
    "address": "340  LAGESCHULTE BARRINGTON",
    "adj_rent_sf": "7.776000000000001",
    "bldgsf": "9586.0",
    "caprate": "0.09",
    "excesslandval": "0.0",
    "exp": "0.15000000000000002",
    "finalmarketvalue": "633366.1919999999",
    "finalmarketvalue_sf": "66.07199999999999",
    "incomemarketvalue": "66.096",
    "investmentrating": "D",
    "landsf": "20944.0",
    "noi": "57023.66303999999",
    "pgi": "74540.73599999999",
    "property_type_use": "Retail-Storefront",
    "salecompmarketvalue_sf": "66.048",
    "vacancy": "0.1",
    "yearbuilt": "1975.0"
  }
]
```

### Q2. Field availability counts for 2025. Used for the section 1 field facts: no finalmarketvalue and no property_type_use printed anywhere in 2025.

Source name: Cook County Assessor commercial valuation data (Cook County open data portal, Socrata dataset csik-bsws)

Exact query URL: https://data.cookcountyil.gov/resource/csik-bsws.json?%24select=count%28finalmarketvalue%29+as+finalmarketvalue_count%2C+count%28property_type_use%29+as+property_type_use_count%2C+count%28finalmarketvalue_sf%29+as+finalmarketvalue_sf_count%2C+count%28%2A%29+as+total_count&year=2025

UTC retrieval time: 2026-10-23T14:41:40Z

```
[
  {
    "finalmarketvalue_count": "0",
    "property_type_use_count": "0",
    "finalmarketvalue_sf_count": "11566",
    "total_count": "13343"
  }
]
```

### Q3. Comparable pool query. Used for the candidate count, the exclusions count, and every comparable field in section 2.

Source name: Cook County Assessor commercial valuation data (Cook County open data portal, Socrata dataset csik-bsws)

Exact query URL: https://data.cookcountyil.gov/resource/csik-bsws.json?year=2025&township=Barrington&subclass2=76%3ARETAIL-SINGLE+TENANT&%24limit=100&%24order=keypin

UTC retrieval time: 2026-10-23T14:41:41Z

```
[
  {
    "keypin": "01-01-100-012-0000",
    "pins": "01-01-100-012-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Specials",
    "class_es": "5-92",
    "address": "123 W MAIN BARRINGTON",
    "adj_rent_sf": "27.72",
    "bldgsf": "5024.0",
    "caprate": "0.0825",
    "egi": "132302.016",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.4833180129300031",
    "finalmarketvalue_sf": "164.924890272743",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "8210.0",
    "noi": "68358.0685202466",
    "pgi": "139265.28",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05",
    "yearbuilt": "1985.0"
  },
```

```
  {
    "keypin": "01-01-101-021-0000",
    "pins": "01-01-101-021-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "125 S HOUGH BARRINGTON",
    "adj_rent_sf": "36.96",
    "bldgsf": "2428.0",
    "caprate": "0.0825",
    "egi": "85251.93599999999",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.4833173338839091",
    "finalmarketvalue_sf": "219.90014269900797",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "2783.0",
    "noi": "44048.197584038295",
    "pgi": "89738.88",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-01-101-022-0000",
```

```
    "pins": "01-01-101-022-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "113 S HOUGH BARRINGTON",
    "adj_rent_sf": "37.26800000000001",
    "bldgsf": "1250.0",
    "caprate": "0.0825",
    "egi": "44255.75",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.48331897419195413",
    "finalmarketvalue_sf": "221.73193995543704",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "1650.0",
    "noi": "22866.106307904498",
    "pgi": "46585.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-01-101-023-0000",
    "pins": "01-01-101-023-0000",
    "year": "2025",
```

```
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "115 S HOUGH BARRINGTON",
    "adj_rent_sf": "33.879999999999995",
    "bldgsf": "1500.0",
    "caprate": "0.0825",
    "egi": "48279.0",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.49592340794451506",
    "finalmarketvalue_sf": "196.65708111391302",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "1650.0",
    "noi": "24336.313787846797",
    "pgi": "50820.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-01-102-002-0000",
    "pins": "01-01-102-002-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
```

```
    "class_es": "5-17",
    "address": "113 S COOK BARRINGTON",
    "adj_rent_sf": "37.26800000000001",
    "bldgsf": "1246.0",
    "caprate": "0.0825",
    "egi": "44114.13159999999",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.4833177073431441",
    "finalmarketvalue_sf": "221.732483619381",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "1294.0",
    "noi": "22792.990653654302",
    "pgi": "46435.928",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-01-105-001-0000",
    "pins": "01-01-105-001-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Specials",
    "class_es": "5-92",
    "address": "201 S COOK BARRINGTON",
```

```
    "adj_rent_sf": "28.0",
    "bldgsf": "2230.0",
    "caprate": "0.0825",
    "egi": "59318.0",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.49592159659724905",
    "finalmarketvalue_sf": "162.52709733955402",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "1530.0",
    "noi": "29900.922733044405",
    "pgi": "62440.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05",
    "yearbuilt": "1948.0"
  },
  {
    "keypin": "01-01-105-002-0000",
    "pins": "01-01-105-002-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Specials",
    "class_es": "5-92",
    "address": "205 S COOK BARRINGTON",
    "adj_rent_sf": "28.0",
```

```
    "bldgsf": "2095.0",
    "caprate": "0.0825",
    "egi": "55727.0",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.49592133018129697",
    "finalmarketvalue_sf": "162.527183238515",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "2282.0",
    "noi": "28090.792032986898",
    "pgi": "58660.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10148",
    "vacancy": "0.05",
    "yearbuilt": "1895.0"
  },
  {
    "keypin": "01-01-200-001-0000",
    "pins": "01-01-200-001-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Specials",
    "class_es": "5-92",
    "address": "325 E MAIN BARRINGTON",
    "adj_rent_sf": "28.0",
    "bldgsf": "3493.0",
```

```
    "caprate": "0.0825",
    "egi": "92913.8",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.49411450460217",
    "finalmarketvalue_sf": "163.10974760705798",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "9660.0",
    "noi": "47003.7437422949",
    "pgi": "97804.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05",
    "yearbuilt": "1893.0"
  },
  {
    "keypin": "01-01-201-039-0000",
    "pins": "01-01-201-039-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "206 S NORTHWEST BARRINGTON",
    "adj_rent_sf": "30.8",
    "bldgsf": "1960.0",
    "caprate": "0.0825",
```

```
    "egi": "57349.6",
    "excesslandarea": "1503.0",
    "excesslandval": "30060.0",
    "exp": "0.49411547408171697",
    "finalmarketvalue_sf": "179.42037852568404",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "9343.0",
    "noi": "29012.2752076031",
    "pgi": "60368.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-01-202-044-0000",
    "pins": "01-01-202-044-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "181 S NORTHWEST BARRINGTON",
    "adj_rent_sf": "25.2",
    "bldgsf": "4060.0",
    "caprate": "0.0825",
    "egi": "97196.4",
    "excesslandarea": "0.0",
```

```
    "excesslandval": "0.0",
    "exp": "0.494114243955318",
    "finalmarketvalue_sf": "146.79884848132903",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "8400.0",
    "noi": "49170.2742988213",
    "pgi": "102312.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-01-211-029-0000",
    "pins": "01-01-211-029-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "860 S NORTHWEST BARRINGTON",
    "adj_rent_sf": "28.0",
    "bldgsf": "4500.0",
    "caprate": "0.0825",
    "egi": "119700.0",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.49411329602275",
```

```
    "finalmarketvalue_sf": "163.110137282362",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "13328.0",
    "noi": "60554.6384660768",
    "pgi": "126000.0",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-02-201-018-0000",
    "pins": "01-02-201-018-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "102 S HAGER BARRINGTON",
    "adj_rent_sf": "36.96",
    "bldgsf": "946.0",
    "caprate": "0.0825",
    "egi": "33215.952000000005",
    "excesslandarea": "4136.0",
    "excesslandval": "49632.0",
    "exp": "0.494113578609301",
    "finalmarketvalue_sf": "215.305260943882",
    "investmentrating": "C",
```

```
    "land_bldg": "4.0",
    "landsf": "7920.0",
    "noi": "16803.4990903652",
    "pgi": "34964.159999999996",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-02-202-045-0000",
    "pins": "01-02-202-045-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "340  LAGESCHULTE BARRINGTON",
    "adj_rent_sf": "18.144000000000002",
    "bldgsf": "8273.0",
    "caprate": "0.0825",
    "egi": "142600.0464",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.5067613117521479",
    "finalmarketvalue_sf": "103.05280753443097",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "20944.0",
```

```
    "noi": "70335.8598304188",
    "pgi": "150105.312",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-02-204-001-0000",
    "pins": "01-02-204-001-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "201  LAGESCHULTE BARRINGTON",
    "adj_rent_sf": "22.4",
    "bldgsf": "4961.0",
    "caprate": "0.0825",
    "egi": "105570.08",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.494113578609301",
    "finalmarketvalue_sf": "130.48803693568607",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "9966.0",
    "noi": "53406.469977129804",
    "pgi": "111126.4",
```

```
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10021",
    "vacancy": "0.05"
  },
  {
    "keypin": "01-32-400-029-0000",
    "pins": "01-32-400-029-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "5251  PRAIRIE STONE HOFFMAN ESTATES",
    "adj_rent_sf": "20.16",
    "bldgsf": "14376.0",
    "caprate": "0.0825",
    "egi": "275329.15199999994",
    "excesslandarea": "55815.0",
    "excesslandval": "390705.0",
    "exp": "0.52219434912038",
    "finalmarketvalue_sf": "110.920410007836",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "113319.0",
    "noi": "131553.82467749395",
    "pgi": "289820.16",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10110",
```

```
    "vacancy": "0.05"
  },
  {
    "keypin": "01-32-400-031-0000",
    "pins": "01-32-400-031-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Specials",
    "class_es": "5-97",
    "address": "2575  PRATUM HOFFMAN ESTATES",
    "adj_rent_sf": "29.567999999999998",
    "bldgsf": "49476.0",
    "caprate": "0.07250000000000001",
    "egi": "1389761.0496",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.5247071754052359",
    "finalmarketvalue_sf": "184.148763113615",
    "investmentrating": "B",
    "land_bldg": "4.0",
    "landsf": "204866.0",
    "noi": "660543.454776168",
    "pgi": "1462906.368",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10110",
    "vacancy": "0.05",
    "yearbuilt": "2015.0"
```

```
  },
  {
    "keypin": "01-33-209-010-0000",
    "pins": "01-33-209-010-0000",
    "year": "2025",
    "township": "Barrington",
    "sheet": "Comm517",
    "class_es": "5-17",
    "address": "100 W HIGGINS SOUTH BARRINGTON",
    "adj_rent_sf": "30.491999999999997",
    "bldgsf": "13025.0",
    "caprate": "0.0825",
    "egi": "377300.385",
    "excesslandarea": "0.0",
    "excesslandval": "0.0",
    "exp": "0.5374644248939648",
    "finalmarketvalue_sf": "162.405491131231",
    "investmentrating": "C",
    "land_bldg": "4.0",
    "landsf": "22574.0",
    "noi": "174514.85056370395",
    "pgi": "397158.3",
    "subclass2": "76:RETAIL-SINGLE TENANT",
    "taxdist": "10128",
    "vacancy": "0.05"
  }
]
```

