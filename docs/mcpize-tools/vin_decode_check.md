# `vin_decode_check`: VIN decode

A tool factory wave 1 tool (issue #161, parent #158). The fetcher is
[`tools/vin_decode.py`](../../tools/vin_decode.py), and it is served as
`GET /vin` by the pay per call API ([`api/endpoints.py`](../../api/endpoints.py)).
It is not on the MCP server yet. Every wave 1 tool that passes review is
registered on the server in one shared surface PR at the end of the wave
(coordinator ruling on issue #158), and going live is one owner redeploy
step after that.

- **What it answers:** What the public NHTSA vPIC API decodes from one VIN: model year, make, model, trim, manufacturer, plant and every other field vPIC returns with a value, plus vPIC's own error code and text for the VIN (check digit wrong, incomplete VIN, and so on).
- **Source:** NHTSA vPIC API, `DecodeVinValues` (flat format), `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/<VIN>?format=json`, with `&modelyear=<year>` when a model year is given. Keyless.
- **Arguments:** `vin` (17 characters, or fewer with `*` for unknown ones), optional `model_year` (four digits; the vPIC API page recommends always sending it).
- **Needs on the server:** Outbound HTTPS to `vpic.nhtsa.dot.gov`. No key, no environment value.
- **What it is not:** A vehicle history, title or inspection. The values are vPIC's as shown. An empty field means vPIC has no data on it, in vPIC's own words, quoted in every report. It does not mean the feature is absent.
- **Price:** 0.25 USDC per call once the shelf goes live, the shelf price set by the owner ruling on issue #147 ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)). Nothing in this PR sets or changes a price. Pricing stays in the owner redeploy step.

Every report uses the repo's fixed evidence format. Each claim has its
source link with the raw response directly beneath it, the exact query
and retrieval time are recorded, and an empty result is proven by the
complete raw response. A failed fetch is an error that names the
source, never an empty result.

## What a report shows, on a recorded response

The tool's answer for one recorded response. The claims are the tool's
own lines for that body (the offline tests check these exact lines),
with the recorded body printed directly beneath the source link.

- `VPIC STATUS: ErrorCode as shown: "0"; ErrorText as shown: "0 - VIN decoded clean. Check Digit (9th position) is correct"`
- `DECODE: vehicle as shown: 2003 HONDA Accord EX-V6`
- `- Manufacturer: AMERICAN HONDA MOTOR CO., INC.`, `- PlantCity: MARYSVILLE`, `- PlantState: OHIO`

Source: https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/1HGCM82633A004352?format=json, captured by the coordinator under Option B on issue #161 ([comment](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/161#issuecomment-6378279932)), retrieved 2026-10-24, about 01:38 UTC, HTTP 200, 3921 bytes, sha256 `5bbe2f293edb394f21e10fe8220fb11b30dc7e1614b0a8c2d216c9a27993e6ef`; saved unmodified as [`tools/tests/fixtures/vpic/clean-1HGCM82633A004352.json`](../../tools/tests/fixtures/vpic/clean-1HGCM82633A004352.json)
```json
{"Count":1,"Message":"Results returned successfully. NOTE: Any missing decoded values should be interpreted as NHTSA does not have data on the specific variable. Missing value should NOT be interpreted as an indication that a feature or technology is unavailable for a vehicle.","SearchCriteria":"VIN(s): 1HGCM82633A004352","Results":[{"ABS":"","ActiveSafetySysNote":"","AdaptiveCruiseControl":"","AdaptiveDrivingBeam":"","AdaptiveHeadlights":"","AdditionalErrorText":"","AirBagLocCurtain":"1st and 2nd Rows","AirBagLocFront":"1st Row (Driver and Passenger)","AirBagLocKnee":"","AirBagLocSeatCushion":"","AirBagLocSide":"1st Row (Driver and Passenger)","AutoReverseSystem":"","AutomaticPedestrianAlertingSound":"","AxleConfiguration":"","Axles":"","BasePrice":"","BatteryA":"","BatteryA_to":"","BatteryCells":"","BatteryInfo":"","BatteryKWh":"","BatteryKWh_to":"","BatteryModules":"","BatteryPacks":"","BatteryType":"","BatteryV":"","BatteryV_to":"","BedLengthIN":"","BedType":"Not Applicable","BlindSpotIntervention":"","BlindSpotMon":"","BodyCabType":"Not Applicable","BodyClass":"Coupe","BrakeSystemDesc":"","BrakeSystemType":"","BusFloorConfigType":"Not Applicable","BusLength":"","BusType":"Not Applicable","CAN_AACN":"","CIB":"","CashForClunkers":"","ChargerLevel":"","ChargerPowerKW":"","CombinedBrakingSystem":"","CoolingType":"","CurbWeightLB":"","CustomMotorcycleType":"Not Applicable","DaytimeRunningLight":"","DestinationMarket":"","DisplacementCC":"2998.832712","DisplacementCI":"183","DisplacementL":"2.998832712","Doors":"2","DriveType":"","DriverAssist":"","DynamicBrakeSupport":"","EDR":"","ESC":"","EVDriveUnit":"","ElectrificationLevel":"","EngineConfiguration":"V-Shaped","EngineCycles":"","EngineCylinders":"6","EngineHP":"240","EngineHP_to":"","EngineKW":"","EngineManufacturer":"","EngineModel":"J30A4","EntertainmentSystem":"","ErrorCode":"0","ErrorText":"0 - VIN decoded clean. Check Digit (9th position) is correct","ForwardCollisionWarning":"","FuelInjectionType":"","FuelTankMaterial":"","FuelTankType":"","FuelTypePrimary":"Gasoline","FuelTypeSecondary":"","GCWR":"","GCWR_to":"","GVWR":"Class 1C: 4,001 - 5,000 lb (1,814 - 2,268 kg)","GVWR_to":"Class 1: 6,000 lb or less (2,722 kg or less)","KeylessIgnition":"","LaneCenteringAssistance":"","LaneDepartureWarning":"","LaneKeepSystem":"","LowerBeamHeadlampLightSource":"","Make":"HONDA","MakeID":"474","Manufacturer":"AMERICAN HONDA MOTOR CO., INC.","ManufacturerId":"988","Model":"Accord","ModelID":"1861","ModelYear":"2003","MotorcycleChassisType":"Not Applicable","MotorcycleSuspensionType":"Not Applicable","NCSABodyType":"","NCSAMake":"","NCSAMapExcApprovedBy":"","NCSAMapExcApprovedOn":"","NCSAMappingException":"","NCSAModel":"","NCSANote":"","NonLandUse":"","Note":"","OtherBusInfo":"","OtherEngineInfo":"","OtherMotorcycleInfo":"","OtherRestraintSystemInfo":"Seat Belt (Rr center position)","OtherTrailerInfo":"","ParkAssist":"","PedestrianAutomaticEmergencyBraking":"","PlantCity":"MARYSVILLE","PlantCompanyName":"","PlantCountry":"UNITED STATES (USA)","PlantState":"OHIO","PossibleValues":"","Pretensioner":"","RearAutomaticEmergencyBraking":"","RearCrossTrafficAlert":"","RearVisibilitySystem":"","SAEAutomationLevel":"","SAEAutomationLevel_to":"","SeatBeltsAll":"Manual","SeatRows":"","Seats":"","SemiautomaticHeadlampBeamSwitching":"","Series":"","Series2":"","SteeringLocation":"","SuggestedVIN":"","TPMS":"","TopSpeedMPH":"","TrackWidth":"","TractionControl":"","TrailerBodyType":"Not Applicable","TrailerLength":"","TrailerType":"Not Applicable","TransmissionSpeeds":"5","TransmissionStyle":"Automatic","Trim":"EX-V6","Trim2":"","Turbo":"","VIN":"1HGCM82633A004352","ValveTrainDesign":"Single Overhead Cam (SOHC)","VehicleDescriptor":"1HGCM826*3A","VehicleType":"PASSENGER CAR","WheelBaseLong":"","WheelBaseShort":"","WheelBaseType":"","WheelSizeFront":"","WheelSizeRear":"","WheelieMitigation":"","Wheels":"","Windows":""}]}
```

## The three other outcomes, on recorded responses

All four recorded outcomes are in [`tools/tests/fixtures/vpic/`](../../tools/tests/fixtures/vpic/), with their provenance:

- **Bad check digit** (`1HGCM82643A004352`): vPIC answers ErrorCode `"1"`, "1 - Check Digit (9th position) does not calculate properly", and still decodes the vehicle. The report quotes both.
- **Partial VIN** (the vPIC page's own example, `5UXWX7C5*BA`, model year 2011): ErrorCode `"6"`, "6 - Incomplete VIN". The report shows what vPIC decoded from the characters given.
- **Nothing decoded** (`00000000000000000`): ErrorCode `"1,7,11,400"`, with Make, Model and ModelYear empty. The report says no vehicle was decoded, and the complete raw response beneath the source link proves it.

## Not verified here

This container cannot reach `vpic.nhtsa.dot.gov` (the proxy refuses the
connection), so no live run was made from it. The tool's behaviour is
tested offline on the five recorded bodies above. The coordinator's live
smoke run at review is the live check. The recorded bodies carry no
response headers, so the header part of a live transcript is not on
record here.
