# Flood Zone Screen for 10 Tampa Points, FEMA NFHL and USGS Elevation

Screening only, not a Standard Flood Hazard Determination and not insurance advice.

This work was unattended agent work and observation of public records only, with no contact with anyone.

Field notes: SFHA is shown as true when the FEMA Flood Hazard Zones layer returns SFHA_TF T, and as false when it returns F. Static BFE is shown as none when the service returns -9999, as this job directs. Ground elevation is shown as no data when USGS returns -1000000, as this job directs; no point in this run returned that value. FIRM panel effective dates are converted from epoch milliseconds: the raw number is shown first, followed by the converted UTC date in parentheses.

## 1. TABLE

| Point | Latitude | Longitude | Flood zone | Zone subtype | SFHA | Static BFE | DFIRM ID | FIRM panel number | FIRM panel effective date (epoch milliseconds and converted date) | Ground elevation in feet | Flood insurance required for a federally backed mortgage |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.9506 | -82.4572 | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C | 12057C0354J | 1633564800000 (2021-10-07) | 19.898163376242522 | no |
| 2 | 27.9235 | -82.4515 | AE | COASTAL FLOODPLAIN | true | 11.0 | 12057C | 12057C0362J | 1633564800000 (2021-10-07) | 4.38482834897592 | yes |
| 3 | 27.9325 | -82.4850 | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C | 12057C0361J | 1633564800000 (2021-10-07) | 20.833451017720282 | no |
| 4 | 27.9600 | -82.5300 | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C | 12057C0334J | 1633564800000 (2021-10-07) | 14.69784411862496 | no |
| 5 | 27.9940 | -82.5730 | AE | COASTAL FLOODPLAIN | true | 12.0 | 12057C | 12103C0155G; 12057C0327J | 1062547200000 (2003-09-03); 1633564800000 (2021-10-07) | 6.629299985759641 | yes |
| 6 | 28.0587 | -82.4139 | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C | 12057C0216H | 1219881600000 (2008-08-28) | 55.052891689514 | no |
| 7 | 27.8850 | -82.5190 | X | 0.2 PCT ANNUAL CHANCE FLOOD HAZARD IN COASTAL ZONE | false | none | 12057C | 12057C0344J | 1633564800000 (2021-10-07) | 10.54948821159936 | no |
| 8 | 27.9658 | -82.4378 | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C | 12057C0354J | 1633564800000 (2021-10-07) | 45.21563128941984 | no |
| 9 | 27.8950 | -82.4850 | VE | COASTAL FLOODPLAIN | true | 15.0 | 12057C | 12057C0363J | 1633564800000 (2021-10-07) | 0 | yes |
| 10 | 28.0300 | -82.4600 | X | AREA OF MINIMAL FLOOD HAZARD | false | none | 12057C | 12057C0214J | 1633564800000 (2021-10-07) | 33.67090270476544 | no |

## 2. NOTES

Points in a high risk zone (a flood zone starting with A or V):

- Point 2: zone AE
- Point 5: zone AE
- Point 9: zone VE

Points with no polygon: none. No point returned no polygon in this run.

Points with no data elevation: none. No point returned no data in this run.

## 3. SOURCES

Every query run is listed below with its source name, exact query URL, UTC retrieval time, and a raw excerpt in a code block directly under its URL. FEMA JSON responses are pretty printed with 2 space indent before excerpting, as this job allows. USGS responses are shorter than 10 lines and are quoted whole.

### Point 1 (27.9506, -82.4572)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.4572%2C27.9506&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T14:57:42Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124129,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FLD_AR_ID": "12057C_9452",
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.4572%2C27.9506&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T14:57:43Z

```
      "attributes": {
        "OBJECTID": 835187,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_99",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0354",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0354J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.000976567169454019,
        "SHAPE.STLength()": 0.1250002988447,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.4572&y=27.9506&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T14:57:44Z

```
{"location":{"x":-82.4572,"y":27.9506,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":19.898163376242522,"rasterId":14541,"resolution":0.0000308641987179478}
```

### Point 2 (27.9235, -82.4515)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.4515%2C27.9235&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:00:37Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28120424,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FLD_AR_ID": "12057C_6142",
        "STUDY_TYP": "SFHAs WITH HIGH FLOOD RISK",
        "FLD_ZONE": "AE",
        "ZONE_SUBTY": "COASTAL FLOODPLAIN",
        "SFHA_TF": "T",
        "STATIC_BFE": 11.0,
        "V_DATUM": "NAVD88",
        "DEPTH": -9999.0,
        "LEN_UNIT": "Feet",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.4515%2C27.9235&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:00:38Z

```
      "attributes": {
        "OBJECTID": 835375,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_104",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0362",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0362J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765720398121314,
        "SHAPE.STLength()": 0.12500061054687397,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.4515&y=27.9235&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:00:39Z

```
{"location":{"x":-82.4515,"y":27.9235,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":4.38482834897592,"rasterId":14541,"resolution":0.0000308641987179478}
```

### Point 3 (27.9325, -82.4850)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.485%2C27.9325&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:00:46Z

```
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.485%2C27.9325&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:01:27Z

```
      "attributes": {
        "OBJECTID": 835297,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_103",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0361",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0361J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765719988845483,
        "SHAPE.STLength()": 0.12500060792752798,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.485&y=27.9325&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:01:28Z

```
{"location":{"x":-82.485,"y":27.9325,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":20.833451017720282,"rasterId":14541,"resolution":0.0000308641987179478}
```

### Point 4 (27.9600, -82.5300)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.53%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:30Z

```
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.53%2C27.96&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:31Z

```
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
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.53&y=27.96&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:02:32Z

```
{"location":{"x":-82.53,"y":27.96,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":14.69784411862496,"rasterId":14543,"resolution":0.0000308641987179478}
```

### Point 5 (27.9940, -82.5730)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.573%2C27.994&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:33Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28123922,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FLD_AR_ID": "12057C_9705",
        "STUDY_TYP": "SFHAs WITH HIGH FLOOD RISK",
        "FLD_ZONE": "AE",
        "ZONE_SUBTY": "COASTAL FLOODPLAIN",
        "SFHA_TF": "T",
        "STATIC_BFE": 12.0,
        "V_DATUM": "NAVD88",
        "DEPTH": -9999.0,
        "LEN_UNIT": "Feet",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.573%2C27.994&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:35Z

Feature 1 excerpt from the same response:

```
      "attributes": {
        "OBJECTID": 766383,
        "DFIRM_ID": "12103C",
        "VERSION_ID": "1.1.1.0",
        "FIRM_ID": "12103C_128",
        "ST_FIPS": "12",
        "PCOMM": "103C",
        "PANEL": "0155",
        "SUFFIX": "G",
        "FIRM_PAN": "12103C0155G",
        "PANEL_TYP": "Countywide, Not Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1062547200000,
        "SCALE": "12000",
        "PNP_REASON": "OPEN WATER AREA",
        "BASE_TYP": "Vector",
        "SOURCE_CIT": "12103C_STUDY1",
        "GFID": "e7a617ac-46e4-4dc7-ac6c-50c6d1c7edf1",
        "SHAPE.STArea()": 0.0039061986073858144,
        "SHAPE.STLength()": 0.24999831623952792,
```

Feature 2 excerpt from the same response:

```
      "attributes": {
        "OBJECTID": 835203,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_82",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0327",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0327J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765683154205839,
        "SHAPE.STLength()": 0.12500037218648677,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.573&y=27.994&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:02:36Z

```
{"location":{"x":-82.573,"y":27.994,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":6.629299985759641,"rasterId":14543,"resolution":0.0000308641987179478}
```

### Point 6 (28.0587, -82.4139)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.4139%2C28.0587&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:37Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124225,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FLD_AR_ID": "12057C_7396",
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.4139%2C28.0587&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:38Z

```
      "attributes": {
        "OBJECTID": 835356,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FIRM_ID": "12057C_48",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0216",
        "SUFFIX": "H",
        "FIRM_PAN": "12057C0216H",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1219881600000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Vector",
        "SOURCE_CIT": "12057C_STUDY1",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765499799918473,
        "SHAPE.STLength()": 0.12499919871937998,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.4139&y=28.0587&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:02:42Z

```
{"location":{"x":-82.4139,"y":28.0587,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":55.052891689514,"rasterId":14553,"resolution":0.0000308641987179478}
```

### Point 7 (27.8850, -82.5190)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.519%2C27.885&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:44Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28116101,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FLD_AR_ID": "12057C_8534",
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.519%2C27.885&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:50Z

```
      "attributes": {
        "OBJECTID": 835280,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_95",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0344",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0344J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765670875930875,
        "SHAPE.STLength()": 0.12500029360600798,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.519&y=27.885&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:02:51Z

```
{"location":{"x":-82.519,"y":27.885,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":10.54948821159936,"rasterId":14543,"resolution":0.0000308641987179478}
```

### Point 8 (27.9658, -82.4378)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.4378%2C27.9658&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:02:58Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28124129,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "1.1.1.0",
        "FLD_AR_ID": "12057C_9452",
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.4378%2C27.9658&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:03:29Z

```
      "attributes": {
        "OBJECTID": 835187,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_99",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0354",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0354J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.000976567169454019,
        "SHAPE.STLength()": 0.1250002988447,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.4378&y=27.9658&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:03:30Z

```
{"location":{"x":-82.4378,"y":27.9658,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":45.21563128941984,"rasterId":14541,"resolution":0.0000308641987179478}
```

### Point 9 (27.8950, -82.4850)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.485%2C27.895&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:04:16Z

```
      "attributes": {
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "OBJECTID": 28115633,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FLD_AR_ID": "12057C_507",
        "STUDY_TYP": "SFHAs WITH HIGH FLOOD RISK",
        "FLD_ZONE": "VE",
        "ZONE_SUBTY": "COASTAL FLOODPLAIN",
        "SFHA_TF": "T",
        "STATIC_BFE": 15.0,
        "V_DATUM": "NAVD88",
        "DEPTH": -9999.0,
        "LEN_UNIT": "Feet",
        "VELOCITY": -9999.0,
        "VEL_UNIT": "",
        "AR_REVERT": "",
        "AR_SUBTRV": "",
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.485%2C27.895&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:05:06Z

```
      "attributes": {
        "OBJECTID": 835241,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_105",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0363",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0363J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.000976563404135298,
        "SHAPE.STLength()": 0.12500005786496676,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.485&y=27.895&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:05:08Z

```
{"location":{"x":-82.485,"y":27.895,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":0,"rasterId":14541,"resolution":0.0000308641987179478}
```

### Point 10 (28.0300, -82.4600)

Source name: FEMA National Flood Hazard Layer, Flood Hazard Zones layer (layer 28), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query?geometry=-82.46%2C28.03&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:06:03Z

```
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
```

Source name: FEMA National Flood Hazard Layer, FIRM Panels layer (layer 3), point query

Exact query URL: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/3/query?geometry=-82.46%2C28.03&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=%2A&returnGeometry=false&f=json

UTC retrieval time: 2026-10-23T15:06:04Z

```
      "attributes": {
        "OBJECTID": 835188,
        "DFIRM_ID": "12057C",
        "VERSION_ID": "2.4.3.5",
        "FIRM_ID": "12057C_47",
        "ST_FIPS": "12",
        "PCOMM": "057C",
        "PANEL": "0214",
        "SUFFIX": "J",
        "FIRM_PAN": "12057C0214J",
        "PANEL_TYP": "Countywide, Panel Printed",
        "PRE_DATE": 253392451200000,
        "EFF_DATE": 1633564800000,
        "SCALE": "6000",
        "PNP_REASON": "",
        "BASE_TYP": "Orthophoto",
        "SOURCE_CIT": "12057C_STUDY7",
        "GFID": "0aa9691f-7029-4198-bc41-0c92139fc0de",
        "SHAPE.STArea()": 0.0009765524355975439,
        "SHAPE.STLength()": 0.12499935588013998,
```

Source name: USGS Elevation Point Query Service, feet

Exact query URL: https://epqs.nationalmap.gov/v1/json?x=-82.46&y=28.03&wkid=4326&units=Feet

UTC retrieval time: 2026-10-23T15:06:06Z

```
{"location":{"x":-82.46,"y":28.03,"spatialReference":{"wkid":4326,"latestWkid":4326}},"locationId":0,"value":33.67090270476544,"rasterId":14552,"resolution":0.0000308641987179478}
```
