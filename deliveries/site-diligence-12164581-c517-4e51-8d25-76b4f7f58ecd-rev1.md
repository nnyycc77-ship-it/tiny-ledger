# Site Due-Diligence Desk Packet for One Fixed Tampa Site (Federal Data Only)

Not an engineering opinion, not a Phase I environmental site assessment, not a survey.

This work was unattended agent work and observation of public records only, with no contact with anyone (no emails, calls, messages or test sends).

Site points (WGS84, fixed, as given in the job text): C 27.96000, -82.53000; N 27.96090, -82.53000; E 27.96000, -82.52898; S 27.95910, -82.53000; W 27.96000, -82.53102. Site square corners (lon lat): -82.53102 27.95910, -82.52898 27.95910, -82.52898 27.96090, -82.53102 27.96090.

Field notes: SFHA is shown as true when the Flood Hazard Zones layer returns SFHA_TF T, and as false when it returns F. Static BFE is shown as none when the service returns -9999, as this job directs. FIRM panel effective dates are converted from epoch milliseconds: the raw number is shown first, followed by the converted UTC date in parentheses. Distances in section 5 are computed with the haversine formula stated there and are shown rounded to two decimal places. Flood data note (revision 1): in the original delivery the flood and panel values came from a county republication because the FEMA service dropped connections from this machine. In this revision every flood and panel value below was pulled from the FEMA National Flood Hazard Layer itself, at hazards.fema.gov (Flood Hazard Zones layer 28 and FIRM Panels layer 3); the service again dropped direct connections from this machine, so the exact FEMA query URLs in section 7 were fetched through a reader proxy and the excerpts in S6 to S11 are the FEMA service responses to those URLs. The FEMA values match the original table at all five points, so no body figure changed. Each flood response returned exactly one feature, and each excerpt in S6 to S11 starts at the features array so that is visible.

## REVISION 1 NOTE

This revision answers the evaluator revision request of 2026-10-23 (round 1 of 3) on escrow esc_7495cc05591c45e2b2496126. All six unmet items concern one point: the flood section must come from the FEMA National Flood Hazard Layer itself, from public federal geodata only. That is now the case. Sources S6 to S11 are FEMA NFHL queries at hazards.fema.gov: Flood Hazard Zones layer 28 at all five points (S6 to S10) and FIRM Panels layer 3 at C (S11), each with its raw excerpt printed directly under its FEMA link, starting at the features array. The panel number 12057C0334J and EFF_DATE 1633564800000 (2021-10-07) in section 2 are backed by the FEMA FIRM Panels excerpt at S11. No county service is used anywhere in this revision, and no flood value changed from the original delivery because the FEMA responses match the earlier values at every point. Nothing else in the file changed.

## 1. ELEVATION

USGS Elevation Point Query Service values in feet:

| Point | Latitude | Longitude | Elevation in feet |
|---|---|---|---|
| C | 27.96 | -82.53 | 14.69784411862496 |
| N | 27.9609 | -82.53 | 14.365236112574681 |
| E | 27.96 | -82.52898 | 14.779017513610958 |
| S | 27.9591 | -82.53 | 13.951024491708358 |
| W | 27.96 | -82.53102 | 14.592888314741439 |

Range (max minus min): 14.779017513610958 - 13.951024491708358 = 0.8279930219025999 feet. The maximum is at E and the minimum is at S.

## 2. FLOOD

FEMA National Flood Hazard Layer, Flood Hazard Zones layer, at each of the five points:

| Point | Flood zone | Zone subtype | SFHA | Static BFE | DFIRM ID |
|---|---|---|---|---|---|
| C | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C |
| N | X | 0.2 PCT ANNUAL CHANCE FLOOD HAZARD IN COASTAL ZONE | false | none | 12057C |
| E | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C |
| S | X | 0.2 PCT ANNUAL CHANCE FLOOD HAZARD IN COASTAL ZONE | false | none | 12057C |
| W | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C |

FIRM Panels layer at C: panel number 12057C0334J, effective date 1633564800000 (2021-10-07).

## 3. WETLANDS

USFWS National Wetlands Inventory wetlands layer, polygons within 100 m of C:

| Attribute code | Wetland type |
|---|---|
| R2UBHx | Riverine |
| R2UBFx | Riverine |

2 wetland polygons were returned within 100 m of C.

## 4. SOILS

USDA NRCS Soil Data Access, map units intersecting the site square (polygon intersection, not a point). SQL run (also shown with the source in section 7):

```sql
SELECT m.mukey, m.musym, m.muname, a.hydgrpdcd, a.drclassdcd FROM mapunit m LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE m.mukey IN (SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POLYGON((-82.53102 27.95910, -82.52898 27.95910, -82.52898 27.96090, -82.53102 27.96090, -82.53102 27.95910))')) ORDER BY m.musym
```

| Map unit symbol | Map unit name | Dominant hydrologic group | Dominant drainage class | Mukey |
|---|---|---|---|---|
| 29 | Myakka fine sand, 0 to 2 percent slopes | A/D | Poorly drained | 1406979 |
| 4 | Arents, nearly level | A | Somewhat poorly drained | 1406990 |
| 59 | Winder fine sand, 0 to 2 percent slopes | C/D | Poorly drained | 1407008 |

## 5. FACILITIES

EPA Facility Registry Service, 1 mile radius of C (27.96000, -82.53000).

Total rows returned: 153 (the count of FRSFacility objects in the response at the source URL in section 7, counted from the response itself).

Haversine formula used for every distance: a = sin squared(delta lat / 2) + cos(lat1) x cos(lat2) x sin squared(delta lon / 2); distance in metres = 2 x 6371000 x arcsin(sqrt(a)), with all angles in radians and the Earth radius 6371000 metres.

Rows excluded for having no coordinates: 0. Every returned row carried Latitude83 and Longitude83 values, so no row was excluded.

The 20 nearest facilities, in ascending computed distance, ties broken by RegistryId ascending:

| # | Registry ID | Facility name | Address | Distance in metres |
|---|---|---|---|---|
| 1 | 110041943653 | AIRFIELD AND ROADWAY REHABILIT | UNKNOWN, TAMPA, FL 33622 | 175.01 |
| 2 | 110063603774 | TIA CONSOLIDATED RENTAL CAR FACIL & AUTOMATED PEOPLE MOVER | 5302 AIRPORT SERVICE RD, TAMPA, FL 33607 | 203.20 |
| 3 | 110070545653 | SKYCENTER SITE DEVELOPMENT, ATRIUM, AND PEDESTRIAN BRIDGE | 5302 AIRPORT SERVICE RD, TAMPA, FL 33607-1407 | 203.20 |
| 4 | 110035595763 | VALUE CAR RENTAL | 5210 W SPRUCE ST, TAMPA, FL 336071424 | 211.43 |
| 5 | 110035688048 | FORMER VALUE RENT - A - CAR | 5210 W SPRUCE ST, TAMPA, FL 336071424 | 211.43 |
| 6 | 110067370990 | SOUTH TERMINAL SUPPORT AREA ROADWAY IMPROVEMENTS | UNKNOWN, TAMPA, FL 33607 | 222.43 |
| 7 | 110035479121 | UNITED STATES POSTAL SERVICE | 5201 SPRUCE ST., TAMPA, FL 33630-5000 | 243.62 |
| 8 | 110009080779 | OVERFLOW PARKING LOT HCAA PROJ #1005 - LOT | 5401 W SPRUCE ST, TAMPA, FL 336075976 | 276.23 |
| 9 | 110035526687 | HILLS COUNTY AVIATION AUTHORITY | 5401 W SPRUCE ST, TAMPA, FL 336075976 | 276.23 |
| 10 | 110035569104 | ECONOMY GARAGE & POST OFC - AR | 5401 SPRUCE ST, TAMPA, FL 33607 | 276.23 |
| 11 | 110037458275 | US AIRWAYS  - TAMPA INTERNATIO | 5503 W SPRUCE ST, TAMPA, FL 33607 | 292.83 |
| 12 | 110031337587 | TRANSPORTATION SECURITY ADMIN TSA AT TAMPA INTL AIRPORT TPA | 5521 W SPRUCE ST STE B-33, TAMPA, FL 33607-1441 | 295.78 |
| 13 | 110070598959 | HYATT HOUSE - AVION PARK | 5308 AVION PARK DR, TAMPA, FL 33607-1412 | 301.75 |
| 14 | 110027366188 | AVION PARK | 5301 AVION PARK DR, TAMPA, FL 33607 | 312.21 |
| 15 | 110064750844 | HAMPTON INN & SUITES AT AVION PARK | 5329 AVION PARK DR, TAMPA, FL 33607 | 330.38 |
| 16 | 110027971336 | ENTERPRISE RENT A CAR | 4912 W SPRUCE ST, TAMPA, FL 336071418 | 334.30 |
| 17 | 110063604531 | AVION PARK MOB | 5332 AVION PARK DR, TAMPA, FL 33607 | 335.77 |
| 18 | 110063604933 | AVION PARK OFFICE CENTER | 5332 AVION PARK DR, TAMPA, FL 33607 | 335.77 |
| 19 | 110002563226 | LAW ENGINEERING | 4919 W LAUREL ST, TAMPA, FL 336073811 | 435.13 |
| 20 | 110070111772 | LAUREL STREET STORAGE FACILITY | 5012 WEST LAUREL ST, TAMPA, FL 33607 | 476.89 |

## 6. SUMMARY

| Topic | Headline value | What to check next on site |
|---|---|---|
| Elevation | Five points run from 13.951024491708358 to 14.779017513610958 feet, a range of 0.8279930219025999 feet | Confirm grade and drainage direction on the ground against the low point at S |
| Flood | All five points are zone X with SFHA false; C and E and W are AREA OF MINIMAL FLOOD HAZARD, N and S are 0.2 PCT ANNUAL CHANCE FLOOD HAZARD IN COASTAL ZONE; panel 12057C0334J | Check whether any structure sits toward the N or S edges, which carry the 0.2 percent annual chance subtype |
| Wetlands | 2 Riverine wetland polygons within 100 m of C, attribute codes R2UBHx and R2UBFx | Walk the watercourse corridor the Riverine polygons follow and confirm its on site course and buffers |
| Soils | Three map units intersect the square: Myakka fine sand (29, A/D, Poorly drained), Arents (4, A, Somewhat poorly drained), Winder fine sand (59, C/D, Poorly drained) | Expect poor drainage across most of the square; check for ponding and a high water table in any excavation |
| Facilities | 153 EPA registered facilities within 1 mile, none excluded; the nearest is Registry ID 110041943653 at 175.01 metres | Note the airport area operations immediately west and north of the site during the visit |

## 7. SOURCES

Every query run is listed below with its source name, exact query URL or form fields, UTC retrieval time, and a raw excerpt in a code block directly under its URL. JSON responses are pretty printed with 2 space indent before excerpting, as this job allows. An excerpt is 10 to 30 consecutive lines of that text; a response shorter than 10 lines is quoted whole.

### S1. USGS Elevation Point Query Service, feet, point C (27.96, -82.53)

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.53&y=27.96&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T16:05:58Z

```
{"location":{"x":-82.53,"y":27.96,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":14.69784411862496,"rasterId":14543,"resolution":0.0000308641987179478}
```

### S2. USGS Elevation Point Query Service, feet, point N (27.9609, -82.53)

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.53&y=27.9609&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T16:05:59Z

```
{"location":{"x":-82.53,"y":27.9609,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":14.365236112574681,"rasterId":14543,"resolution":0.0000308641987179478}
```

### S3. USGS Elevation Point Query Service, feet, point E (27.96, -82.52898)

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.52898&y=27.96&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T16:06:01Z

```
{"location":{"x":-82.52898,"y":27.96,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":14.779017513610958,"rasterId":14543,"resolution":0.0000308641987179478}
```

### S4. USGS Elevation Point Query Service, feet, point S (27.9591, -82.53)

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.53&y=27.9591&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T16:06:02Z

```
{"location":{"x":-82.53,"y":27.9591,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":13.951024491708358,"rasterId":14543,"resolution":0.0000308641987179478}
```

### S5. USGS Elevation Point Query Service, feet, point W (27.96, -82.53102)

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.53102&y=27.96&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T16:06:03Z

```
{"location":{"x":-82.53102,"y":27.96,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":14.592888314741439,"rasterId":14543,"resolution":0.0000308641987179478}
```

### S6. FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point C (27.96, -82.53)

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.53%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:59:04Z

```
  "features": [
    {
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124101,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FLD_AR_ID": "12057C_8629",
        "STUDY_TYP": "NP",
        "FLD_ZONE": "X",
        "ZONE_SUBTY": "AREA OF MINIMAL FLOOD HAZARD",
        "SFHA_TF": "F",
        "STATIC_BFE": -9999.0,
        "V_DATUM": "",
        "DEPTH": -9999.0,
        "LEN_UNIT": "",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
        "BFE_REVERT": -9999.0,
        "DEP_REVERT": -9999.0,
        "DUAL_ZONE": "",
        "SOURCE_CIT": "12057C_STUDY4",
        "GlobalID": "{28308CBB-42C0-4CCD-8249-7C5F48455E57}",
        "SHAPE.STArea()": 0.006033573356055642,
        "SHAPE.STLength()": 1.7746243475506678
      }
```

### S7. FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point N (27.9609, -82.53)

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.53%2C27.9609&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:59:04Z

```
  "features": [
    {
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28123983,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FLD_AR_ID": "12057C_9441",
        "STUDY_TYP": "SFHAs WITH HIGH FLOOD RISK",
        "FLD_ZONE": "X",
        "ZONE_SUBTY": "0.2 PCT ANNUAL CHANCE FLOOD HAZARD IN COASTAL ZONE",
        "SFHA_TF": "F",
        "STATIC_BFE": -9999.0,
        "V_DATUM": "",
        "DEPTH": -9999.0,
        "LEN_UNIT": "",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
        "BFE_REVERT": -9999.0,
        "DEP_REVERT": -9999.0,
        "DUAL_ZONE": "",
        "SOURCE_CIT": "12057C_STUDY7",
        "GlobalID": "{A4C4FEE3-515D-4173-B520-231933CE0102}",
        "SHAPE.STArea()": 6.170193331655577e-05,
        "SHAPE.STLength()": 0.16108306117004592
      }
```

### S8. FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point E (27.96, -82.52898)

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.52898%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:59:05Z

```
  "features": [
    {
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124101,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FLD_AR_ID": "12057C_8629",
        "STUDY_TYP": "NP",
        "FLD_ZONE": "X",
        "ZONE_SUBTY": "AREA OF MINIMAL FLOOD HAZARD",
        "SFHA_TF": "F",
        "STATIC_BFE": -9999.0,
        "V_DATUM": "",
        "DEPTH": -9999.0,
        "LEN_UNIT": "",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
        "BFE_REVERT": -9999.0,
        "DEP_REVERT": -9999.0,
        "DUAL_ZONE": "",
        "SOURCE_CIT": "12057C_STUDY4",
        "GlobalID": "{28308CBB-42C0-4CCD-8249-7C5F48455E57}",
        "SHAPE.STArea()": 0.006033573356055642,
        "SHAPE.STLength()": 1.7746243475506678
      }
```

### S9. FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point S (27.9591, -82.53)

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.53%2C27.9591&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:59:10Z

```
  "features": [
    {
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124185,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FLD_AR_ID": "12057C_9438",
        "STUDY_TYP": "SFHAs WITH HIGH FLOOD RISK",
        "FLD_ZONE": "X",
        "ZONE_SUBTY": "0.2 PCT ANNUAL CHANCE FLOOD HAZARD IN COASTAL ZONE",
        "SFHA_TF": "F",
        "STATIC_BFE": -9999.0,
        "V_DATUM": "",
        "DEPTH": -9999.0,
        "LEN_UNIT": "",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
        "BFE_REVERT": -9999.0,
        "DEP_REVERT": -9999.0,
        "DUAL_ZONE": "",
        "SOURCE_CIT": "12057C_STUDY7",
        "GlobalID": "{6865B3A8-8A39-4489-A0D4-D92ED7AA4DD8}",
        "SHAPE.STArea()": 0.00021839482541887356,
        "SHAPE.STLength()": 0.7029081868116063
      }
```

### S10. FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point W (27.96, -82.53102)

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.53102%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:59:11Z

```
  "features": [
    {
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124101,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FLD_AR_ID": "12057C_8629",
        "STUDY_TYP": "NP",
        "FLD_ZONE": "X",
        "ZONE_SUBTY": "AREA OF MINIMAL FLOOD HAZARD",
        "SFHA_TF": "F",
        "STATIC_BFE": -9999.0,
        "V_DATUM": "",
        "DEPTH": -9999.0,
        "LEN_UNIT": "",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
        "BFE_REVERT": -9999.0,
        "DEP_REVERT": -9999.0,
        "DUAL_ZONE": "",
        "SOURCE_CIT": "12057C_STUDY4",
        "GlobalID": "{28308CBB-42C0-4CCD-8249-7C5F48455E57}",
        "SHAPE.STArea()": 0.006033573356055642,
        "SHAPE.STLength()": 1.7746243475506678
      }
```

### S11. FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point C (27.96, -82.53)

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.53%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:59:12Z

```
  "features": [
    {
      "attributes": {
        "OBJECTID": 835394,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_88",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0334",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0334J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765708119937944,
        "SHAPE.STLength()": 0.12500053196659278,
        "GlobalID": "{08BF3624-529F-4145-AF3C-92AB4114C1CE}"
      }
    }
  ]
}
```

### S12. USFWS National Wetlands Inventory, wetlands layer, 100 m around C, polygon 1 (R2UBHx)

Exact query URL: https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query?geometry=-82.53%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&distance=100&units=esriSRUnit_Meter&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:08:48Z

```
        "OBJECTID": 16054811,
        "Shape_Length": 2964.554089119026,
        "Shape_Area": 15677.816473639472,
        "GlobalID": "{27953A62-72C4-40D7-B1F8-1B495E5727A7}",
        "ATTRIBUTE": "R2UBHx",
        "WETLAND_TYPE": "Riverine",
        "QAQC_CODE": null,
        "ACRES": 3.0110815958485335
      }
    },
    {
      "attributes": {
        "OBJECTID": 16054812,
        "Shape_Length": 4817.362928347186,
        "Shape_Area": 13298.49197932295,
        "GlobalID": "{3E7E7151-4253-4271-9D57-E3AE2C505B62}",
        "ATTRIBUTE": "R2UBFx",
        "WETLAND_TYPE": "Riverine",
        "QAQC_CODE": null,
        "ACRES": 2.5537564211707977
      }
    }
  ]
}
```

### S13. USFWS National Wetlands Inventory, wetlands layer, 100 m around C, polygon 2 (R2UBFx)

Exact query URL: https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query?geometry=-82.53%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&distance=100&units=esriSRUnit_Meter&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T16:08:48Z

```
        "OBJECTID": 16054812,
        "Shape_Length": 4817.362928347186,
        "Shape_Area": 13298.49197932295,
        "GlobalID": "{3E7E7151-4253-4271-9D57-E3AE2C505B62}",
        "ATTRIBUTE": "R2UBFx",
        "WETLAND_TYPE": "Riverine",
        "QAQC_CODE": null,
        "ACRES": 2.5537564211707977
      }
    }
  ]
}
```

### S14. USDA NRCS Soil Data Access, tabular POST, site square polygon intersection

Exact query URL: https://sdmdataaccess.sc.egov.usda.gov/Tabular/post.rest

Form fields: format = json+columnname; query = SELECT m.mukey, m.musym, m.muname, a.hydgrpdcd, a.drclassdcd FROM mapunit m LEFT JOIN muaggatt a ON a.mukey = m.mukey WHERE m.mukey IN (SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POLYGON((-82.53102 27.95910, -82.52898 27.95910, -82.52898 27.96090, -82.53102 27.96090, -82.53102 27.95910))')) ORDER BY m.musym

UTC retrieval time: 2026-10-23T16:12:01Z

```
{"Table":[["mukey","musym","muname","hydgrpdcd","drclassdcd"],["1406979","29","Myakka fine sand, 0 to 2 percent slopes","A/D","Poorly drained"],["1406990","4","Arents, nearly level","A","Somewhat poorly drained"],["1407008","59","Winder fine sand, 0 to 2 percent slopes","C/D","Poorly drained"]]}
```

### S15. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 1 (Registry ID 110041943653)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.949434",
        "Longitude83": "-82.5298"
      },
      {
        "RegistryId": "110041943653",
        "FacilityName": "AIRFIELD AND ROADWAY REHABILIT",
        "LocationAddress": "UNKNOWN",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33622",
        "FIPSCode": "FL057",
        "Latitude83": "27.960556",
        "Longitude83": "-82.531667"
      },
      {
        "RegistryId": "110005607101",
        "FacilityName": "AMOCO SERVICE STATION #628",
        "LocationAddress": "5109 W KENNEDY BLVD",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "33609",
        "FIPSCode": "12057",
        "Latitude83": "27.945545",
        "Longitude83": "-82.530069"
      },
      {
```

### S16. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 2 (Registry ID 110063603774)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.9668",
        "Longitude83": "-82.5335"
      },
      {
        "RegistryId": "110063603774",
        "FacilityName": "TIA CONSOLIDATED RENTAL CAR FACIL & AUTOMATED PEOPLE MOVER",
        "LocationAddress": "5302 AIRPORT SERVICE RD",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.960672",
        "Longitude83": "-82.531924"
      },
      {
        "RegistryId": "110070701202",
        "FacilityName": "TIA SOLAR",
        "LocationAddress": null,
        "SupplementalLocation": null,
        "CityName": null,
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": null,
        "FIPSCode": "12057",
        "Latitude83": "27.965797",
        "Longitude83": "-82.532816"
      },
      {
```

### S17. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 3 (Registry ID 110070545653)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.965035",
        "Longitude83": "-82.535936"
      },
      {
        "RegistryId": "110070545653",
        "FacilityName": "SKYCENTER SITE DEVELOPMENT, ATRIUM, AND PEDESTRIAN BRIDGE",
        "LocationAddress": "5302 AIRPORT SERVICE RD",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607-1407",
        "FIPSCode": "FL057",
        "Latitude83": "27.960672",
        "Longitude83": "-82.531924"
      },
      {
        "RegistryId": "110067370990",
        "FacilityName": "SOUTH TERMINAL SUPPORT AREA ROADWAY IMPROVEMENTS",
        "LocationAddress": "UNKNOWN",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH COUNTY",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "12057",
        "Latitude83": "27.960706",
        "Longitude83": "-82.532119"
      },
      {
```

### S18. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 4 (Registry ID 110035595763)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.967917",
        "Longitude83": "-82.536922"
      },
      {
        "RegistryId": "110035595763",
        "FacilityName": "VALUE CAR RENTAL",
        "LocationAddress": "5210 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336071424",
        "FIPSCode": "12057",
        "Latitude83": "27.959794",
        "Longitude83": "-82.53214"
      },
      {
        "RegistryId": "110069997055",
        "FacilityName": "WCF - CYPRESS",
        "LocationAddress": "5016 W CYPRESS ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607-3804",
        "FIPSCode": "FL057",
        "Latitude83": "27.952323",
        "Longitude83": "-82.528561"
      },
      {
```

### S19. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 5 (Registry ID 110035688048)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.961639",
        "Longitude83": "-82.516056"
      },
      {
        "RegistryId": "110035688048",
        "FacilityName": "FORMER VALUE RENT - A - CAR",
        "LocationAddress": "5210 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336071424",
        "FIPSCode": "12057",
        "Latitude83": "27.959794",
        "Longitude83": "-82.53214"
      },
      {
        "RegistryId": "110035614537",
        "FacilityName": "FUJI",
        "LocationAddress": "1001N N WEST SHORE BLVD",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336074707",
        "FIPSCode": "12057",
        "Latitude83": "27.953131",
        "Longitude83": "-82.523968"
      },
      {
```

### S20. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 6 (Registry ID 110067370990)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.960672",
        "Longitude83": "-82.531924"
      },
      {
        "RegistryId": "110067370990",
        "FacilityName": "SOUTH TERMINAL SUPPORT AREA ROADWAY IMPROVEMENTS",
        "LocationAddress": "UNKNOWN",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH COUNTY",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "12057",
        "Latitude83": "27.960706",
        "Longitude83": "-82.532119"
      },
      {
        "RegistryId": "110027954391",
        "FacilityName": "SPIRIT AIRLINES - TAMPA INTERNATIONAL AIRPORT",
        "LocationAddress": "2450 N WEST SHORE BLVD",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336075741",
        "FIPSCode": "12057",
        "Latitude83": "27.966082",
        "Longitude83": "-82.523993"
      },
      {
```

### S21. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 7 (Registry ID 110035479121)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.95042",
        "Longitude83": "-82.53126"
      },
      {
        "RegistryId": "110035479121",
        "FacilityName": "UNITED STATES POSTAL SERVICE",
        "LocationAddress": "5201 SPRUCE ST.",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "33630-5000",
        "FIPSCode": "12057",
        "Latitude83": "27.96004",
        "Longitude83": "-82.53248"
      },
      {
        "RegistryId": "110037458275",
        "FacilityName": "US AIRWAYS  - TAMPA INTERNATIO",
        "LocationAddress": "5503 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.960048",
        "Longitude83": "-82.532981"
      },
      {
```

### S22. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 8 (Registry ID 110009080779)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.95422",
        "Longitude83": "-82.53231"
      },
      {
        "RegistryId": "110009080779",
        "FacilityName": "OVERFLOW PARKING LOT HCAA PROJ #1005 - LOT",
        "LocationAddress": "5401 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336075976",
        "FIPSCode": "00057",
        "Latitude83": "27.960045",
        "Longitude83": "-82.532812"
      },
      {
        "RegistryId": "110071346799",
        "FacilityName": "PARK GRAVITY SEWER REPLACEMENT",
        "LocationAddress": "W. GRAY STREET",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33609",
        "FIPSCode": "FL057",
        "Latitude83": "27.948155",
        "Longitude83": "-82.538328"
      },
      {
```

### S23. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 9 (Registry ID 110035526687)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.95042",
        "Longitude83": "-82.53126"
      },
      {
        "RegistryId": "110035526687",
        "FacilityName": "HILLS COUNTY AVIATION AUTHORITY",
        "LocationAddress": "5401 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336075976",
        "FIPSCode": "12057",
        "Latitude83": "27.960045",
        "Longitude83": "-82.532812"
      },
      {
        "RegistryId": "110005615977",
        "FacilityName": "HILLSBOROUGH COUNTY JEFFERSON HIGH SCHOOL",
        "LocationAddress": "4001 W CYPRESS ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336074806",
        "FIPSCode": "12057",
        "Latitude83": "27.953948",
        "Longitude83": "-82.519962"
      },
      {
```

### S24. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 10 (Registry ID 110035569104)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.94814",
        "Longitude83": "-82.53651"
      },
      {
        "RegistryId": "110035569104",
        "FacilityName": "ECONOMY GARAGE & POST OFC - AR",
        "LocationAddress": "5401 SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "12057",
        "Latitude83": "27.960045",
        "Longitude83": "-82.532812"
      },
      {
        "RegistryId": "110053892926",
        "FacilityName": "ENCORE RV RESORT TAMPA NORTH-LAND O'LAKES R V PARK",
        "LocationAddress": "4300 W. CYPRESS ST., #400",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "PASCO",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": null,
        "Latitude83": "27.9522",
        "Longitude83": "-82.51649"
      },
      {
```

### S25. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 11 (Registry ID 110037458275)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.96004",
        "Longitude83": "-82.53248"
      },
      {
        "RegistryId": "110037458275",
        "FacilityName": "US AIRWAYS  - TAMPA INTERNATIO",
        "LocationAddress": "5503 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.960048",
        "Longitude83": "-82.532981"
      },
      {
        "RegistryId": "110002523975",
        "FacilityName": "USPS",
        "LocationAddress": "5201 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336125222",
        "FIPSCode": "12057",
        "Latitude83": "27.967917",
        "Longitude83": "-82.536922"
      },
      {
```

### S26. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 12 (Registry ID 110031337587)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.96438",
        "Longitude83": "-82.51494"
      },
      {
        "RegistryId": "110031337587",
        "FacilityName": "TRANSPORTATION SECURITY ADMIN TSA AT TAMPA INTL AIRPORT TPA",
        "LocationAddress": "5521 W SPRUCE ST STE B-33",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "33607-1441",
        "FIPSCode": "12057",
        "Latitude83": "27.960048",
        "Longitude83": "-82.533011"
      },
      {
        "RegistryId": "110013232821",
        "FacilityName": "TROPICAL PALMS MHP-TROPICAL PALM MHP",
        "LocationAddress": "5100 W LEMON ST.",
        "SupplementalLocation": "STE 109",
        "CityName": "TAMPA",
        "CountyName": "CHARLOTTE",
        "StateAbbr": "FL",
        "ZipCode": "33609",
        "FIPSCode": "12015",
        "Latitude83": "27.95042",
        "Longitude83": "-82.53126"
      },
      {
```

### S27. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 13 (Registry ID 110070598959)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.94687",
        "Longitude83": "-82.536725"
      },
      {
        "RegistryId": "110070598959",
        "FacilityName": "HYATT HOUSE - AVION PARK",
        "LocationAddress": "5308 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607-1412",
        "FIPSCode": "FL057",
        "Latitude83": "27.95794",
        "Longitude83": "-82.532"
      },
      {
        "RegistryId": "110070596914",
        "FacilityName": "I-275 IMPROVEMENTS FROM S OF KENNEDY BLVD TO S OF LOIS AVE",
        "LocationAddress": "5010 CARMEN ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH COUNTY",
        "StateAbbr": "FL",
        "ZipCode": "33603",
        "FIPSCode": "12057",
        "Latitude83": "27.94909",
        "Longitude83": "-82.52884"
      },
      {
```

### S28. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 14 (Registry ID 110027366188)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.9543",
        "Longitude83": "-82.53843"
      },
      {
        "RegistryId": "110027366188",
        "FacilityName": "AVION PARK",
        "LocationAddress": "5301 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "12057",
        "Latitude83": "27.95794",
        "Longitude83": "-82.53216"
      },
      {
        "RegistryId": "110063604531",
        "FacilityName": "AVION PARK MOB",
        "LocationAddress": "5332 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.957948",
        "Longitude83": "-82.532508"
      },
      {
```

### S29. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 15 (Registry ID 110064750844)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.96605",
        "Longitude83": "-82.523994"
      },
      {
        "RegistryId": "110064750844",
        "FacilityName": "HAMPTON INN & SUITES AT AVION PARK",
        "LocationAddress": "5329 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH COUNTY",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "12057",
        "Latitude83": "27.95794",
        "Longitude83": "-82.532424"
      },
      {
        "RegistryId": "110007475428",
        "FacilityName": "HERTZ RENTAL CORP",
        "LocationAddress": "5109 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336077219",
        "FIPSCode": "12057",
        "Latitude83": "27.964204",
        "Longitude83": "-82.537835"
      },
      {
```

### S30. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 16 (Registry ID 110027971336)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.95851",
        "Longitude83": "-82.53662"
      },
      {
        "RegistryId": "110027971336",
        "FacilityName": "ENTERPRISE RENT A CAR",
        "LocationAddress": "4912 W SPRUCE ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336071418",
        "FIPSCode": "12057",
        "Latitude83": "27.95973",
        "Longitude83": "-82.52661"
      },
      {
        "RegistryId": "110037323535",
        "FacilityName": "ESUITES HOTEL - TAMPA",
        "LocationAddress": "2215 N LOIS AVE",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336072355",
        "FIPSCode": "12057",
        "Latitude83": "27.96132",
        "Longitude83": "-82.51379"
      },
      {
```

### S31. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 17 (Registry ID 110063604531)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.95794",
        "Longitude83": "-82.53216"
      },
      {
        "RegistryId": "110063604531",
        "FacilityName": "AVION PARK MOB",
        "LocationAddress": "5332 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.957948",
        "Longitude83": "-82.532508"
      },
      {
        "RegistryId": "110063604933",
        "FacilityName": "AVION PARK OFFICE CENTER",
        "LocationAddress": "5332 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.957948",
        "Longitude83": "-82.532508"
      },
      {
```

### S32. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 18 (Registry ID 110063604933)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.957948",
        "Longitude83": "-82.532508"
      },
      {
        "RegistryId": "110063604933",
        "FacilityName": "AVION PARK OFFICE CENTER",
        "LocationAddress": "5332 AVION PARK DR",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.957948",
        "Longitude83": "-82.532508"
      },
      {
        "RegistryId": "110070389856",
        "FacilityName": "AVIS-TIA",
        "LocationAddress": "5412 AIRPORT SERVICE RD",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH COUNTY",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "12057",
        "Latitude83": "27.96318",
        "Longitude83": "-82.53596"
      },
      {
```

### S33. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 19 (Registry ID 110002563226)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.955962",
        "Longitude83": "-82.528364"
      },
      {
        "RegistryId": "110002563226",
        "FacilityName": "LAW ENGINEERING",
        "LocationAddress": "4919 W LAUREL ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336073811",
        "FIPSCode": "12057",
        "Latitude83": "27.956669",
        "Longitude83": "-82.527675"
      },
      {
        "RegistryId": "110045494167",
        "FacilityName": "LEGACY WESTSHORE APARTMENTS",
        "LocationAddress": "UNKNOWN",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.959156",
        "Longitude83": "-82.521067"
      },
      {
```

### S34. EPA Facility Registry Service, get_facilities, 1 mile radius of C, listed facility 20 (Registry ID 110070111772)

Exact query URL: https://ofmpub.epa.gov/frs_public2/frs_rest_services.get_facilities?latitude83=27.96&longitude83=-82.53&search_radius=1&output=JSON

UTC retrieval time: 2026-10-23T16:21:10Z

```
        "Latitude83": "27.95607",
        "Longitude83": "-82.53502"
      },
      {
        "RegistryId": "110070111772",
        "FacilityName": "LAUREL STREET STORAGE FACILITY",
        "LocationAddress": "5012 WEST LAUREL ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLSBOROUGH",
        "StateAbbr": "FL",
        "ZipCode": "33607",
        "FIPSCode": "FL057",
        "Latitude83": "27.955962",
        "Longitude83": "-82.528364"
      },
      {
        "RegistryId": "110002563226",
        "FacilityName": "LAW ENGINEERING",
        "LocationAddress": "4919 W LAUREL ST",
        "SupplementalLocation": null,
        "CityName": "TAMPA",
        "CountyName": "HILLS",
        "StateAbbr": "FL",
        "ZipCode": "336073811",
        "FIPSCode": "12057",
        "Latitude83": "27.956669",
        "Longitude83": "-82.527675"
      },
      {
```

