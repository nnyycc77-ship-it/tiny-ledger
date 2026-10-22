# Recall check: six named consumer products in the CPSC and NHTSA recall databases

Observation only: this report records what the public recall databases show; no product was bought, sold, handled, or tested.

This report was produced by unattended agent work using public sources only.

Revision note (round 1): this revised file addresses the three items in the evaluator revision request. For the Instant Pot Smart WiFi empty result, source S10 now gives the complete raw HTTP response transcript for the exact query, status line and headers in the order returned followed by the body, which is the empty array shown on the last line of that transcript. For Fisher-Price, source S4 now quotes only the records of the ProductName response, in response order, and the separate detail query for recall 13-087 is shown as its own source, S25, quoted from the start of its own response. For NHTSA, source S24 was recaptured fresh and its head excerpt now shows the opening brace of the first result object directly after the results array opening. The recaptured sources are S4, S10, S24 and S25, each labelled with its exact query URL and its fresh UTC retrieval time in 2026-10-22. No recall, figure, date or count in the body changed as a result of the recapture; only retrieval times for the recaptured queries and the NHTSA excerpt order changed.

Each subject states the query run, the UTC retrieval time, and the number of results, followed by every matching recall with the values as shown in the source. Verbatim raw excerpts for every query and every recall are in the Sources section at the end.

## Subject 1: Peloton Tread+ treadmill

Database: CPSC public recall data (SaferProducts.gov RestWebServices API), with the remedy text read from the CPSC recall page for the same record.

QUERY: RecallTitle = "Peloton" returned 5 records (retrieved 2026-10-22T03:30:55Z); 1 of them is for this subject, the Tread+ treadmill (the other 4 are records 21-129, 23-201, 26-067, and 21-702). A detail query, RecallNumber = 21-128, returned 1 record (retrieved 2026-10-22T03:28:32Z).

RECALLS: 1 matching recall found.

#### Recall 21-128
- Recall number: 21-128
- Announcement date: May 5, 2021
- Product as shown: Tread+
- Hazard as shown: Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.
- Remedy as shown: Consumers should immediately stop using the recalled Tread+ and contact Peloton for a full refund until November 6, 2022. Consumers who return the Tread+ treadmill after that date will receive a partial refund. Peloton is offering consumers who do not want a refund the option of moving the Tread+ free of charge to a room where children or pets cannot access the treadmill, and is implementing software improvements to the product to automatically lock the Tread+ after each use and prevent unauthorized access by assigning a 4-digit passcode that will be required to unlock the Tread+.
- Units as shown: About 125,000
- Remedy options as shown in the API record: Refund; Repair
- Note: in the API record for 21-128, the remedy text field repeats the hazard text word for word, so the remedy above is quoted from the CPSC recall page for 21-128 instead; both excerpts are in the Sources section.

## Subject 2: Fisher-Price Rock 'n Play Sleeper

Database: CPSC public recall data (SaferProducts.gov RestWebServices API).

QUERY: ProductName = "Rock 'n Play" returned 3 records (retrieved 2026-10-22T11:48:06Z). Detail queries by recall number were also run for 13-087 (retrieved 2026-10-22T11:48:09Z, shown as source S25), 19-105 (retrieved 2026-10-22T03:29:19Z) and 23-088 (retrieved 2026-10-22T03:29:20Z).

RECALLS: 3 matching recalls found.

#### Recall 13-087
- Recall number: 13-087
- Announcement date: January 8, 2013
- Product as shown: Newborn Rock 'n Play Sleeper™
- Hazard as shown: Mold can develop between the removable seat cushion and the hard plastic frame of the sleeper when it remains wet/moist or is infrequently cleaned, posing a risk of exposure to mold to infants sleeping in the product. The CPSC advises that mold has been associated with respiratory illnesses and other infections. Although mold is not present at the time of purchase, mold growth can occur after use of the product.
- Remedy as shown: Consumers should immediately check for mold under the removable seat cushion. Dark brown, gray or black spots can indicate the presence of mold. If mold is found, consumers should immediately stop using the product. Consumers can contact Fisher-Price for cleaning instructions or further assistance. Cleaning and care instructions can also be found at www.service.mattel.com or by contacting the firm.
- Units as shown: About 800,000 units

#### Recall 19-105
- Recall number: 19-105
- Announcement date: April 12, 2019
- Product as shown: All Models of Rock 'n Play Sleeper
- Hazard as shown: Infant fatalities have occurred in Rock 'n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.
- Remedy as shown: Consumers should immediately stop using the product and contact Fisher-Price for a refund or voucher.
- Units as shown: About 4.7 million products

#### Recall 23-088
- Recall number: 23-088
- Announcement date: January 9, 2023
- Product as shown: All models of Rock 'n Play Sleepers
- Hazard as shown: Infant fatalities have occurred in the Rock 'n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.
- Remedy as shown: Consumers should stop using the Rock 'n Play immediately and contact Fisher-Price for a refund or voucher. It is illegal to sell or distribute the recalled sleepers.
- Units as shown: About 4.7 million (The original recall was announced on April 12, 2019)

## Subject 3: Instant Pot Smart WiFi 6 Qt

Database: CPSC public recall data (SaferProducts.gov RestWebServices API).

QUERY: ProductName = "Instant Pot Smart WiFi" returned 0 records (retrieved 2026-10-22T11:48:05Z). The complete body of the response was an empty array; the complete raw HTTP response transcript for this query, headers and body, is shown verbatim in the Sources section (source S10).

RECALLS: none found for the Instant Pot Smart WiFi 6 Qt.

Other Instant Pot records in the same database, checked and excluded because they name different models: a ProductName = "Instant Pot" query returned 1 record (retrieved 2026-10-22T03:29:56Z), record 15-741 below, and a detail query for record 18-110 was run as well (retrieved 2026-10-22T03:29:25Z). Neither record names the Smart WiFi, and neither names a 6 Qt model.

#### Recall 15-741
- Recall number: 15-741
- Announcement date: July 15, 2015
- Product as shown: Instant Pot 'Smart' pressure cookers
- Hazard as shown: The thermal probe in the base can conduct electricity throughout the cooker, posing a risk of electric shock.
- Remedy as shown: Consumers should stop using the recalled product immediately and contact Instant Pot for instructions to receive a free replacement base, which consists of the entire bottom of the pressure cooker including the control panel. The firm is contacting all purchasers directly.
- Units as shown: About 1,000 (in addition, 140 were sold in Canada)

#### Recall 18-110
- Recall number: 18-110
- Announcement date: March 1, 2018
- Product as shown: Gem 65 8-in-1 multicookers
- Hazard as shown: A manufacturer defect can cause the multicooker to overheat and melt on the underside, posing a fire hazard.
- Remedy as shown: Consumers should immediately stop using the recalled multicookers, unplug the unit and return it to Walmart to receive a free replacement.
- Units as shown: About 104,000

## Subject 4: Vornado VH101 heater

Database: CPSC public recall data (SaferProducts.gov RestWebServices API).

QUERY: ProductName = "VH101" returned 2 records (retrieved 2026-10-22T03:29:54Z). Detail queries by recall number were also run for 18-136 (retrieved 2026-10-22T03:29:21Z) and 18-199 (retrieved 2026-10-22T03:29:22Z).

RECALLS: 2 matching recalls found.

#### Recall 18-136
- Recall number: 18-136
- Announcement date: April 4, 2018
- Product as shown: VH101 Personal Vortex electric space heaters
- Hazard as shown: The electric space heater can overheat when in use, posing fire and burn hazards.
- Remedy as shown: Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit, including free shipping.
- Units as shown: About 350,000

#### Recall 18-199
- Recall number: 18-199
- Announcement date: August 22, 2018
- Product as shown: VH101 Personal Vortex electric space heaters
- Hazard as shown: The electric space heater can overheat when in use, posing fire and burn hazards.
- Remedy as shown: Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit.
- Units as shown: About 350,000 (This recall was first announced in April 2018)

## Subject 5: Samsung top-load washer (2018-2023 models)

Database: CPSC public recall data (SaferProducts.gov RestWebServices API).

QUERY: ProductName = "Top-Load Washing Machines" with RecallDateStart = 2018-01-01 and RecallDateEnd = 2023-12-31 returned 1 record (retrieved 2026-10-22T03:30:56Z), and that record is the Samsung recall below.

RECALLS: 1 matching recall found.

#### Recall 23-080
- Recall number: 23-080
- Announcement date: December 22, 2022
- Product as shown: Samsung Top-Load Washing Machines
- Hazard as shown: The washing machines can short-circuit and overheat, posing a fire hazard.
- Remedy as shown: Consumers should immediately check whether their washer's software has been updated to prevent the hazard; and, if not, consumers should immediately stop using the washer until the software is updated. Instructions on how to check whether a washer's software has been updated can be found here https://www.samsung.com/us/support/tlw-sw-update. All Wi-Fi equipped washers that are plugged into a power source and actively connected to the internet will automatically download the free software repair over-the-air when they are connected to the internet. Consumers who have not connected their Wi-Fi equipped washer to the internet should contact Samsung for instructions on how to download the software repair. Consumers whose washer does not have Wi-Fi capability or who otherwise wish to receive a free software repair without connecting to the internet, should immediately stop using the washer and contact Samsung directly for a free dongle to plug in and download the free software repair.
- Units as shown: About 663,500

## Subject 6: Hyundai Elantra 2021

Database: NHTSA public recall data (recallsByVehicle API), queried by make, model, and model year.

QUERY: make = Hyundai, model = Elantra, modelYear = 2021 returned 6 campaigns (retrieved 2026-10-22T11:48:10Z). The API shows no unit counts for these campaigns, so units are stated as not shown.

RECALLS: 6 matching campaigns found.

#### Campaign 21V302000
- NHTSA campaign number: 21V302000
- Date as shown (ReportReceivedDate): 28/04/2021 (April 28, 2021)
- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: SEATS:FRONT ASSEMBLY:RECLINER
- Hazard as shown (Consequence): An improperly welded seat back recliner could separate from the seat back frame during a crash, increasing the risk of injury.
- Remedy as shown: Dealers will inspect and if necessary, replace the seat back frame assembly, free of charge.  Owner notification letters were mailed on June 21, 2021.  Owners may contact Hyundai customer service at 1-888-371-9460.  Hyundai's number for this recall is 204.
- Units: not shown

#### Campaign 21V796000
- NHTSA campaign number: 21V796000
- Date as shown (ReportReceivedDate): 13/10/2021 (October 13, 2021)
- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: SEAT BELTS:FRONT
- Hazard as shown (Consequence): An exploding seat belt pretensioner could project metal fragments into the vehicle, striking vehicle occupants and resulting in injury.
- Remedy as shown: Dealers will replace the seat belt pretensioners, free of charge.  Owner notification letters were mailed February 10, 2022. Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's numbers for this recall are 211 and 009G.  This recall is replaced by NHTSA recall numbers 22V-354 for Elantra and Elantra HEV vehicles, 22V-458 for Venue vehicles, and 23V-094 for Genesis vehicles.  Elantra, Elantra HEV, Venue, and Genesis vehicles already repaired under this recall will need to have the new remedies completed.
- Units: not shown

#### Campaign 21V00M000
- NHTSA campaign number: 21V00M000
- Date as shown (ReportReceivedDate): 28/12/2021 (December 28, 2021)
- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: VISIBILITY:WINDSHIELD
- Hazard as shown (Consequence): A windshield that detaches from a vehicle during a crash can increase the risk of injury.
- Remedy as shown: Dealers will remove and reinstall the front windshield panel, free of charge.  Owner notification letters were mailed June 20, 2022.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 216.
- Units: not shown

#### Campaign 22V218000
- NHTSA campaign number: 22V218000
- Date as shown (ReportReceivedDate): 01/04/2022 (April 1, 2022)
- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: SEAT BELTS:FRONT
- Hazard as shown (Consequence): Exploding seat belt pretensioners can project metal fragments into the vehicle, strike vehicle occupants, and result in injury.
- Remedy as shown: Dealers will replace the seat belt pretensioners, free of charge.  Interim notification letters, notifying owners of the safety risk, were mailed on May 31, 2022. A second notice will be sent once remedy parts become available.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 223.  This recall is replaced by NHTSA recall number 22V-354.  Vehicles already repaired under this recall will need to have the new remedy completed.
- Units: not shown

#### Campaign 22V354000
- NHTSA campaign number: 22V354000
- Date as shown (ReportReceivedDate): 19/05/2022 (May 19, 2022)
- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: SEAT BELTS:FRONT
- Hazard as shown (Consequence): An exploding seat belt pretensioner can project metal fragments into the vehicle, strike vehicle occupants, and result in injury.
- Remedy as shown: Dealers will secure the seat belt pretensioner(s) with a cap, free of charge.  Owner notification letters were mailed August 28, 2022.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 229.  This recall expands and replaces NHTSA recall numbers 21V-796, 22V-069, 22V-218, and 22V-123 for Accent, Elantra, and Elantra HEV vehicles.  All Accent, Elantra, and Elantra HEV vehicles already repaired under the previous recalls will need to have the new remedy completed.
- Units: not shown

#### Campaign 24V879000
- NHTSA campaign number: 24V879000
- Date as shown (ReportReceivedDate): 21/11/2024 (November 21, 2024)
- Product as shown: 2021 HYUNDAI ELANTRA; Component as shown: BACK OVER PREVENTION: SENSING SYSTEM: CAMERA
- Hazard as shown (Consequence): A rearview image that does not display reduces the driver's visibility and increases the risk of a crash.
- Remedy as shown: Dealers will replace the rearview camera, free of charge.  Owner notification letters were mailed January 14, 2025.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 271.
- Units: not shown

## Summary table

| Subject | Recalls found | Most recent recall date |
| --- | --- | --- |
| Peloton Tread+ treadmill | 1 | May 5, 2021 |
| Fisher-Price Rock 'n Play Sleeper | 3 | January 9, 2023 |
| Instant Pot Smart WiFi 6 Qt | 0 (none found) | none |
| Vornado VH101 heater | 2 | August 22, 2018 |
| Samsung top-load washer (2018-2023 models) | 1 | December 22, 2022 |
| Hyundai Elantra 2021 | 6 | November 21, 2024 |

## Sources

Every excerpt below is pasted verbatim from the response or page named above it. API responses are shown pretty printed, one JSON value per line, with the values unchanged. Source S10 is the one exception in form: it is a complete raw HTTP response transcript, status line and headers in the order returned followed by the body exactly as returned. Sources S4, S10, S24 and S25 were recaptured fresh for this revision at the UTC times shown in their headings, and their excerpts are quoted contiguously from those fresh responses.

### S1. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallTitle=Peloton
- Retrieved (UTC): 2026-10-22T03:30:55Z
Excerpt (RecallTitle = Peloton response, record 1 of 5):
```
{
  "RecallID": 10467,
  "RecallNumber": "26067",
  "RecallDate": "2025-11-06T00:00:00",
  "Description": "This recall involves Peloton Original Series Bike+ units, with model number PL02 and serial numbers beginning with the letter \"T\". The bike measures 4 ft. long by 2 ft. wide and has an adjustable seat and handlebar. The bike's serial number is located inside the front fork, behind the front fork, or behind the flywheel. Additional information to help locate your Bike+ serial number is available at https://www.onepeloton.com/history-summary.",
  "URL": "https://www.cpsc.gov/Recalls/2026/Peloton-Recalls-Original-Series-Bike-Exercise-Bikes-Due-to-Fall-and-Injury-Hazards",
  "Title": "Peloton Recalls Original Series Bike+ Exercise Bikes Due to Fall and Injury Hazards",
  "ConsumerContact": "Contact Peloton toll-free at 866-679-9129 from 6 a.m. to 12 a.m. ET Monday through Friday, or online at https://support.onepeloton.com/s/article/Peloton-Recall-Information?language=en_US or at www.onepeloton.com and click on \"Product Recalls\" at the bottom of the page for information on how to request the free seat post and instructions for installation.",
  "LastPublishDate": "2025-11-06T00:00:00",
  "Products": [
    {
      "Name": "Peloton Original Series Bike+ Model PL02",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 833,000"
```
Excerpt (RecallTitle = Peloton response, record 2 of 5):
```
{
  "RecallID": 9621,
  "RecallNumber": "23201",
  "RecallDate": "2023-05-11T00:00:00",
  "Description": "This recall involves Peloton Bikes with model number PL01. The Peloton Bike measures 4 ft. long x 2 ft. wide, and has an adjustable seat, handlebar, and screen, which tilts up and down to accommodate different heights. The Peloton name and the model number are displayed on the inside front fork, near the flywheel.",
  "URL": "https://www.cpsc.gov/Recalls/2023/Peloton-Recalls-Two-Million-Exercise-Bikes-Due-to-Fall-and-Injury-Hazards",
  "Title": "Peloton Recalls Two Million Exercise Bikes Due to Fall and Injury Hazards",
  "ConsumerContact": "Peloton toll-free at 866-679-9129 from 6 a.m. to 12 a.m. ET, 7 days a week or online at https://support.onepeloton.com/hc/en-us/articles/360060446032-Peloton-Recalls-Tread-And-Tread-Full-Details-Here or at www.onepeloton.com and click on Product Recalls at the bottom of the page for information on how to request the free seat post and instructions for installation.",
  "LastPublishDate": "2023-05-11T00:00:00",
  "Products": [
    {
      "Name": "Peloton Bikes Model PL01",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 2.2 million"
```
Excerpt (RecallTitle = Peloton response, record 3 of 5):
```
{
  "RecallID": 9058,
  "RecallNumber": "21129",
  "RecallDate": "2021-05-05T00:00:00",
  "Description": "This recall involves Peloton Tread treadmills with model TR02.The recalled Tread has a running space of 59 inches, a 23.8-inch high definition (HD) touchscreen console and a non-slatted running belt. The model number TR02 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread+ that was also recalled by the CPSC on May 5, 2021 because children, pets, and objects can be pulled underneath the Tread+ deck, posing a risk of injury or death.",
  "URL": "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Treadmills-Due-to-Risk-of-Injury",
  "Title": "Peloton Recalls Tread Treadmills Due to Risk of Injury",
  "ConsumerContact": "Peloton toll-free 866-679-9129 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. ET on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.",
  "LastPublishDate": "2021-05-05T00:00:00",
  "Products": [
    {
      "Name": "Tread",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 1,050 (In addition, about 5,400 in Canada)"
```
Excerpt (RecallTitle = Peloton response, record 4 of 5):
```
{
  "RecallID": 9057,
  "RecallNumber": "21128",
  "RecallDate": "2021-05-05T00:00:00",
  "Description": "This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.",
  "URL": "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported",
  "Title": "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported",
  "ConsumerContact": "Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.",
  "LastPublishDate": "2021-05-05T00:00:00",
  "Products": [
    {
      "Name": "Tread+",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 125,000"
```
Excerpt (RecallTitle = Peloton response, record 5 of 5):
```
{
  "RecallID": 8919,
  "RecallNumber": "21702",
  "RecallDate": "2020-10-15T00:00:00",
  "Description": "The pedals being recalled are the PR70P or first-generation pedal fitted on Peloton bikes sold between July 2013 and May 2016. The Peloton logo and the word \"PELOTON\" are molded into the pedal body. An orange Peloton symbol and white lettering spelling \"PELOTON\" are printed on the top of the cleat binding. Pedals are warranted for one year and all remaining PR70P Clip-In pedals in service are out of warranty. Peloton recommends that consumers replace pedals annually.",
  "URL": "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-PR70P-Bike-Pedals-Due-to-Laceration-Hazard-Recall-Alert",
  "Title": "Peloton Recalls PR70P Bike Pedals Due to Laceration Hazard (Recall Alert)",
  "ConsumerContact": "Peloton toll-free 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. ET on weekends. Affected consumers received a touchscreen notice and an email. Only consumers who have not already replaced their PR70P pedals should contact Peloton.",
  "LastPublishDate": "2020-10-15T00:00:00",
  "Products": [
    {
      "Name": "PR70P Clip-In Pedals fitted on Peloton bikes (sold between July 2013 and May 2016)",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 27,000 bikes (54,000 pedals)"
```

### S2. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128
- Retrieved (UTC): 2026-10-22T03:28:32Z
Excerpt (RecallNumber = 21-128 response, part 1):
```
[
  {
    "RecallID": 9057,
    "RecallNumber": "21128",
    "RecallDate": "2021-05-05T00:00:00",
    "Description": "This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.",
    "URL": "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported",
    "Title": "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported",
    "ConsumerContact": "Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.",
    "LastPublishDate": "2021-05-05T00:00:00",
    "Products": [
      {
        "Name": "Tread+",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 125,000"
      }
    ],
```
Excerpt (RecallNumber = 21-128 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Refund"
      },
      {
        "Option": "Repair"
```

### S3. CPSC recall page for 21-128 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported
- Retrieved (UTC): 2026-10-22T03:31:10Z
Excerpt (CPSC page 21-128, summary block):
```
Name of Product:
Tread+
Hazard:
Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.
Remedy:
Refund
Recall Date:
May 05, 2021
Units:
About 125,000
```
Excerpt (CPSC page 21-128, details block):
```
Description:
This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread + model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails.
PLEASE NOTE: This product is different than [the Peloton Tread](https://www.cpsc.gov/Recalls/2021/peloton-recalls-tread-treadmills-due-to-risk-of-injury) that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.
Remedy:
Consumers should immediately stop using the recalled Tread+ and contact Peloton for a full refund until November 6, 2022. Consumers who return the Tread+ treadmill after that date will receive a partial refund. Peloton is offering consumers who do not want a refund the option of moving the Tread+ free of charge to a room where children or pets cannot access the treadmill, and is implementing software improvements to the product to automatically lock the Tread+ after each use and prevent unauthorized access by assigning a 4-digit passcode that will be required to unlock the Tread+.
Incidents/Injuries:
A 6-year-old child recently died after being pulled under the rear of the treadmill. In addition, Peloton has received 72 reports of adult users, children, pets and/or objects being pulled under the rear of the treadmill, including 29 reports of injuries to children such as second- and third-degree abrasions, broken bones, and lacerations.
Online at onepeloton.com and at Peloton showrooms from September 2018 through April 2021 for about $4,295.
Importer(s):
Peloton Interactive, Inc., of New York
Distributor(s):
Peloton Interactive, Inc., of New York
Manufactured In:
Taiwan
Recall number:
21-128
```

### S4. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Rock%20%27n%20Play
- Retrieved (UTC): 2026-10-22T11:48:06Z
- Note: the three excerpts below are the three records of this one response, in the order the response returns them. The detail query for record 13-087 is a separate response and is shown separately as source S25.
Excerpt (ProductName = Rock 'n Play response, record 1 of 3):
```
{
  "RecallID": 9494,
  "RecallNumber": "23088",
  "RecallDate": "2023-01-09T00:00:00",
  "Description": "All Rock 'n Play Sleepers are included in this recall.",
  "URL": "https://www.cpsc.gov/Recalls/2023/Fisher-Price-Reannounces-Recall-of-4-7-Million-Rock-n-Play-Sleepers-At-Least-Eight-Deaths-Occurred-After-Recall",
  "Title": "Fisher-Price Reannounces Recall of 4.7 Million Rock 'n Play Sleepers; At Least Eight Deaths Occurred After Recall",
  "ConsumerContact": "Fisher-Price online at Rock 'n Play recall or www.mattel.com and click on \"Recall & Safety\" or toll-free at 866-812-6518 from 9 a.m. to 6 p.m. ET Monday through Friday for more information.",
  "LastPublishDate": "2023-01-09T00:00:00",
  "Products": [
    {
      "Name": "All models of Rock 'n Play Sleepers",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 4.7 million (The original recall was announced on April 12, 2019)"
```
Excerpt (ProductName = Rock 'n Play response, record 2 of 3):
```
{
  "RecallID": 8532,
  "RecallNumber": "19105",
  "RecallDate": "2019-04-12T00:00:00",
  "Description": "This recall involves all Rock 'n Play Sleepers.",
  "URL": "https://www.cpsc.gov/Recalls/2019/Fisher-Price-Recalls-Rock-n-Play-Sleepers-Due-to-Reports-of-Deaths",
  "Title": "Fisher-Price Recalls Rock 'n Play Sleepers Due to Reports of Deaths",
  "ConsumerContact": "Fisher-Price online at www.service.mattel.com and click on “Recalls & Safety Alerts” or at 866-812-6518 from 9 a.m. to 6 p.m. ET Monday through Friday for more information.",
  "LastPublishDate": "2019-04-12T00:00:00",
  "Products": [
    {
      "Name": "All Models of Rock 'n Play Sleeper",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 4.7 million products"
```
Excerpt (ProductName = Rock 'n Play response, record 3 of 3):
```
{
  "RecallID": 1285,
  "RecallNumber": "13087",
  "RecallDate": "2013-01-08T00:00:00",
  "Description": "This recall to inspect includes all Fisher-Price Rock N' Play infant recliner seats called sleepers. The sleeper is designed for babies up to 25 pounds and is composed of a soft plastic seat held by a metal rocking frame. The product has a removable, fabric cover that is sold in 14 patterns and color palettes.",
  "URL": "https://www.cpsc.gov/Recalls/2013/Fisher-Price-Recalls-to-Inspect-Rock-N-Play-Infant-Sleepers-Due-to-Risk-of-Exposure-to-Mold",
  "Title": "Fisher-Price Recalls to Inspect Rock 'N Play Infant Sleepers Due to Risk of Exposure to Mold",
  "ConsumerContact": "Fisher-Price; at (800) 432-5437, from 9 a.m. to 6 p.m. ET Monday through Friday, or online at www.service.mattel.com for more information.",
  "LastPublishDate": "2015-01-13T00:00:00",
  "Products": [
    {
      "Name": "Newborn Rock 'n Play Sleeper™",
      "Description": "",
      "Model": "",
      "Type": "Bassinets and Cradles",
      "CategoryID": "67558",
      "NumberOfUnits": "About 800,000 units"
```

### S5. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=19-105
- Retrieved (UTC): 2026-10-22T03:29:19Z
Excerpt (RecallNumber = 19-105 response, part 1):
```
[
  {
    "RecallID": 8532,
    "RecallNumber": "19105",
    "RecallDate": "2019-04-12T00:00:00",
    "Description": "This recall involves all Rock 'n Play Sleepers.",
    "URL": "https://www.cpsc.gov/Recalls/2019/Fisher-Price-Recalls-Rock-n-Play-Sleepers-Due-to-Reports-of-Deaths",
    "Title": "Fisher-Price Recalls Rock 'n Play Sleepers Due to Reports of Deaths",
    "ConsumerContact": "Fisher-Price online at www.service.mattel.com and click on “Recalls & Safety Alerts” or at 866-812-6518 from 9 a.m. to 6 p.m. ET Monday through Friday for more information.",
    "LastPublishDate": "2019-04-12T00:00:00",
    "Products": [
      {
        "Name": "All Models of Rock 'n Play Sleeper",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 4.7 million products"
      }
    ],
```
Excerpt (RecallNumber = 19-105 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "Infant fatalities have occurred in Rock 'n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately stop using the product and contact Fisher-Price for a refund or voucher."
      }
    ],
    "RemedyOptions": []
```

### S6. CPSC recall page for 19-105 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2019/Fisher-Price-Recalls-Rock-n-Play-Sleepers-Due-to-Reports-of-Deaths
- Retrieved (UTC): 2026-10-22T03:31:50Z
Excerpt (CPSC page 19-105, summary block):
```
Name of Product:
All Models of Rock ‘n Play Sleeper
Hazard:
Infant fatalities have occurred in Rock ‘n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.
Remedy:
Refund
Recall Date:
April 12, 2019
Units:
About 4.7 million products
```
Excerpt (CPSC page 19-105, details block):
```
Description:
This recall involves all Rock ‘n Play Sleepers.
Remedy:
Consumers should immediately stop using the product and contact Fisher-Price for a refund or voucher.
Incidents/Injuries:
Since the 2009 product introduction, over 30 infant fatalities have occurred in Rock ‘n Play Sleepers, after the infants rolled over while unrestrained, or under other circumstances.
Sold At:
Major retailers for approximately $40 to $149.
Importer(s):
Fisher-Price, of East Aurora, N.Y.
Manufactured In:
China
Recall number:
19-105
```

### S7. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=23-088
- Retrieved (UTC): 2026-10-22T03:29:20Z
Excerpt (RecallNumber = 23-088 response, part 1):
```
[
  {
    "RecallID": 9494,
    "RecallNumber": "23088",
    "RecallDate": "2023-01-09T00:00:00",
    "Description": "All Rock 'n Play Sleepers are included in this recall.",
    "URL": "https://www.cpsc.gov/Recalls/2023/Fisher-Price-Reannounces-Recall-of-4-7-Million-Rock-n-Play-Sleepers-At-Least-Eight-Deaths-Occurred-After-Recall",
    "Title": "Fisher-Price Reannounces Recall of 4.7 Million Rock 'n Play Sleepers; At Least Eight Deaths Occurred After Recall",
    "ConsumerContact": "Fisher-Price online at Rock 'n Play recall or www.mattel.com and click on \"Recall & Safety\" or toll-free at 866-812-6518 from 9 a.m. to 6 p.m. ET Monday through Friday for more information.",
    "LastPublishDate": "2023-01-09T00:00:00",
    "Products": [
      {
        "Name": "All models of Rock 'n Play Sleepers",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 4.7 million (The original recall was announced on April 12, 2019)"
      }
    ],
```
Excerpt (RecallNumber = 23-088 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "Infant fatalities have occurred in the Rock 'n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should stop using the Rock 'n Play immediately and contact Fisher-Price for a refund or voucher. It is illegal to sell or distribute the recalled sleepers."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Refund"
```

### S8. CPSC recall page for 23-088 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2023/Fisher-Price-Reannounces-Recall-of-4-7-Million-Rock-n-Play-Sleepers-At-Least-Eight-Deaths-Occurred-After-Recall
- Retrieved (UTC): 2026-10-22T03:31:55Z
Excerpt (CPSC page 23-088, summary block):
```
Name of Product:
All models of Rock ‘n Play Sleepers
Hazard:
Infant fatalities have occurred in the Rock ‘n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.
Remedy:
Refund
Recall Date:
January 09, 2023
Units:
About 4.7 million (The original [recall](https://www.cpsc.gov/Recalls/2019/Fisher-Price-Recalls-Rock-n-Play-Sleepers-Due-to-Reports-of-Deaths) was announced on April 12, 2019.)
```
Excerpt (CPSC page 23-088, details block):
```
Description:
All Rock ‘n Play Sleepers
Remedy:
Consumers should stop using the Rock ‘n Play immediately and contact Fisher-Price for a refund or voucher. It is illegal to sell or distribute the recalled sleepers.
Incidents/Injuries:
On April 12, 2019, at the time the original recall was announced, over 30 fatalities were reported to have occurred in the Rock ‘n Play Sleepers after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances. Since the recall, approximately 70 additional fatalities have been reported, which includes at least 8 fatalities that were reported to have occurred after the initial recall announcement. Approximately 100 deaths have reportedly occurred while infants were in the products. Fisher-Price notes that in some of the reports, it has been unable to confirm the circumstances of the incidents or that the product was a Rock ‘n Play Sleeper.
Sold At:
Major stores nationwide including Walmart, Target, and online at Amazon from September 2009 through April 2019 for between $40 and $149.
Importer(s):
Fisher-Price, of East Aurora, New York
Manufactured In:
China
Recall number:
23-088
```

### S9. CPSC recall page for 13-087 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2013/Fisher-Price-Recalls-to-Inspect-Rock-N-Play-Infant-Sleepers-Due-to-Risk-of-Exposure-to-Mold
- Retrieved (UTC): 2026-10-22T03:32:15Z
Excerpt (CPSC page 13-087, summary block):
```
Name of Product:
Newborn Rock 'n Play Sleeper™
Hazard:
Mold can develop between the removable seat cushion and the hard plastic frame of the sleeper when it remains wet/moist or is infrequently cleaned, posing a risk of exposure to mold to infants sleeping in the product. The CPSC advises that mold has been associated with respiratory illnesses and other infections. Although mold is not present at the time of purchase, mold growth can occur after use of the product.
Remedy:
New Instructions
Repair
Recall Date:
January 08, 2013
Units:
About 800,000 units
```
Excerpt (CPSC page 13-087, details block):
```
Description:
This recall to inspect includes all Fisher-Price Rock N' Play infant recliner seats called sleepers. The sleeper is designed for babies up to 25 pounds and is composed of a soft plastic seat held by a metal rocking frame. The product has a removable, fabric cover that is sold in 14 patterns and color palettes.
Remedy:
Consumers should immediately check for mold under the removable seat cushion. Dark brown, gray or black spots can indicate the presence of mold. If mold is found, consumers should immediately stop using the product. Consumers can contact Fisher-Price for cleaning instructions or further assistance. Cleaning and care instructions can also be found at [www.service.mattel.com](http://www.service.mattel.com/) or by contacting the firm.
Incidents/Injuries:
Fisher-Price has received 600 reports of mold on the product. Sixteen consumers have reported that their infants have been treated for respiratory issues, coughs and hives after sleeping in the product.
Sold At:
Mass merchandise stores nationwide and online since September 2009 for between $50 and $85. Units currently in retail stores are not affected by this recall to inspect. Only products that show signs of mold after use by consumers are included in this announcement.
Manufactured In:
China
Recall number:
13-087
```

### S10. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant%20Pot%20Smart%20WiFi
- Retrieved (UTC): 2026-10-22T11:48:05Z
- Note: this is the empty result for the Instant Pot Smart WiFi subject. The excerpt below is the complete raw HTTP response transcript for the exact query above: the status line, then the response headers in the order returned, then a blank line, then the complete response body. The body is the empty array on the last line of the transcript, meaning 0 records.
Excerpt (Complete raw HTTP response transcript to the Instant Pot Smart WiFi query):
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Cache-Control: no-cache
Expires: Thu, 22 Oct 2026 11:48:07 GMT
Date: Thu, 22 Oct 2026 11:48:07 GMT
Alt-Svc: h3=":443"; ma=93600
Connection: close
Content-Length: 2

[]
```

### S11. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant%20Pot
- Retrieved (UTC): 2026-10-22T03:29:56Z
Excerpt (ProductName = Instant Pot response, record 1 of 1):
```
{
  "RecallID": 6443,
  "RecallNumber": "15741",
  "RecallDate": "2015-07-15T00:00:00",
  "Description": "This recall involves Instant Pot \"Smart\" and \"Smart-60\" electric pressure cookers. They are stainless steel with black molded plastic attachments, have a control panel/keypad on the front and measure about 12 inches in diameter and 12 inches tall. They are Bluetooth® enabled and can be controlled by an app. \"Instant Pot\" and \"Smart\" are printed on the front of the control panel. Serial numbers between 1410 and 1503 and manufacture dates between 12/1/2014 and 6/1/2015 are included in the recall. The serial numbers and dates are printed on a label on the bottom of the pressure cooker's base.",
  "URL": "https://www.cpsc.gov/Recalls/2015/Instant-Pot-Pressure-Cookers-Recalled-by-Double-Insight",
  "Title": "Instant Pot Pressure Cookers Recalled by Double Insight Due to Shock Hazard (Recall Alert)",
  "ConsumerContact": "Instant Pot at (800) 828-7280 between 9 a.m. and 5 p.m. PT Monday through Friday, or at http://instantpot.com and click on \"Instant Pot Smart recall\" under \"Useful Information\" for more information.",
  "LastPublishDate": "2015-07-15T00:00:00",
  "Products": [
    {
      "Name": "Instant Pot 'Smart' pressure cookers",
      "Description": "",
      "Model": "",
      "Type": "Pressure Cookers or Canners",
      "CategoryID": "68137",
      "NumberOfUnits": "About 1,000 (in addition, 140 were sold in Canada)"
```

### S12. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=15-741
- Retrieved (UTC): 2026-10-22T03:29:24Z
Excerpt (RecallNumber = 15-741 response, part 1):
```
[
  {
    "RecallID": 6443,
    "RecallNumber": "15741",
    "RecallDate": "2015-07-15T00:00:00",
    "Description": "This recall involves Instant Pot \"Smart\" and \"Smart-60\" electric pressure cookers. They are stainless steel with black molded plastic attachments, have a control panel/keypad on the front and measure about 12 inches in diameter and 12 inches tall. They are Bluetooth® enabled and can be controlled by an app. \"Instant Pot\" and \"Smart\" are printed on the front of the control panel. Serial numbers between 1410 and 1503 and manufacture dates between 12/1/2014 and 6/1/2015 are included in the recall. The serial numbers and dates are printed on a label on the bottom of the pressure cooker's base.",
    "URL": "https://www.cpsc.gov/Recalls/2015/Instant-Pot-Pressure-Cookers-Recalled-by-Double-Insight",
    "Title": "Instant Pot Pressure Cookers Recalled by Double Insight Due to Shock Hazard (Recall Alert)",
    "ConsumerContact": "Instant Pot at (800) 828-7280 between 9 a.m. and 5 p.m. PT Monday through Friday, or at http://instantpot.com and click on \"Instant Pot Smart recall\" under \"Useful Information\" for more information.",
    "LastPublishDate": "2015-07-15T00:00:00",
    "Products": [
      {
        "Name": "Instant Pot 'Smart' pressure cookers",
        "Description": "",
        "Model": "",
        "Type": "Pressure Cookers or Canners",
        "CategoryID": "68137",
        "NumberOfUnits": "About 1,000 (in addition, 140 were sold in Canada)"
      }
    ],
```
Excerpt (RecallNumber = 15-741 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "The thermal probe in the base can conduct electricity throughout the cooker, posing a risk of electric shock.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should stop using the recalled product immediately and contact Instant Pot for instructions to receive a free replacement base, which consists of the entire bottom of the pressure cooker including the control panel. The firm is contacting all purchasers directly."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Replace"
```

### S13. CPSC recall notice text for 15-741 as republished by Justia (recalls.justia.com)
- Query URL: https://recalls.justia.com/household-and-office/pressure-cookers-or-canners/15-741/index.html
- Retrieved (UTC): 2026-10-22T03:37:10Z
Excerpt (Justia notice block 15-741):
```
Description: This recall involves Instant Pot "Smart" and "Smart-60" electric pressure cookers. They are stainless steel with black molded plastic attachments, have a control panel/keypad on the front and measure about 12 inches in diameter and 12 inches tall. They are Bluetooth® enabled and can be controlled by an app. "Instant Pot" and "Smart" are printed on the front of the control panel. Serial numbers between 1410 and 1503 and manufacture dates between 12/1/2014 and 6/1/2015 are included in the recall. The serial numbers and dates are printed on a label on the bottom of the pressure cooker's base.
Name of product: Instant Pot 'Smart' pressure cookers
Units: About 1,000 (in addition, 140 were sold in Canada)
Hazard: The thermal probe in the base can conduct electricity throughout the cooker, posing a risk of electric shock.
Remedy: Consumers should stop using the recalled product immediately and contact Instant Pot for instructions to receive a free replacement base, which consists of the entire bottom of the pressure cooker including the control panel. The firm is contacting all purchasers directly.
Recall date: July 15, 2015
Incidents/Injuries: The firm has received reports from three consumers of being shocked while using the pressure cooker.
Sold At: Online at Instantpot.com and Amazon.com from November 2014 through May 2015 for about $250.
Importers: Double Insight Inc., of Canada
Manufactured in: China
Consumer contact: Instant Pot at (800) 828-7280 between 9 a.m. and 5 p.m. PT Monday through Friday, or at http://instantpot.com and click on "Instant Pot Smart recall" under "Useful Information" for more information.
Recall number: 15-741
```

### S14. CPSC recall page for 15-741 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2015/Instant-Pot-Pressure-Cookers-Recalled-by-Double-Insight
- Retrieved (UTC): 2026-10-22T03:32:08Z
Excerpt (CPSC page 15-741, summary block):
```
Hazard:
The thermal probe in the base can conduct electricity throughout the cooker, posing a risk of electric shock.
Remedy:
Replace
Recall Date:
July 15, 2015
Units:
About 1,000 (in addition, 140 were sold in Canada)
```
Excerpt (CPSC page 15-741, details block):
```
Description:
This recall involves Instant Pot "Smart" and "Smart-60" electric pressure cookers. They are stainless steel with black molded plastic attachments, have a control panel/keypad on the front and measure about 12 inches in diameter and 12 inches tall. They are Bluetooth® enabled and can be controlled by an app. "Instant Pot" and "Smart" are printed on the front of the control panel. Serial numbers between 1410 and 1503 and manufacture dates between 12/1/2014 and 6/1/2015 are included in the recall. The serial numbers and dates are printed on a label on the bottom of the pressure cooker's base.
Remedy:
Consumers should stop using the recalled product immediately and contact Instant Pot for instructions to receive a free replacement base, which consists of the entire bottom of the pressure cooker including the control panel. The firm is contacting all purchasers directly.
Incidents/Injuries:
The firm has received reports from three consumers of being shocked while using the pressure cooker.
Sold At:
Online at Instantpot.com and Amazon.com from November 2014 through May 2015 for about $250.
Importer(s):
Double Insight Inc., of Canada
Manufactured In:
China
Recall number:
15-741
```

### S15. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=18-110
- Retrieved (UTC): 2026-10-22T03:29:25Z
Excerpt (RecallNumber = 18-110 response, part 1):
```
[
  {
    "RecallID": 8267,
    "RecallNumber": "18110",
    "RecallDate": "2018-03-01T00:00:00",
    "Description": "This recall involves Gem 65 8-in-1 model multicookers, a multifunctional, programmable cooking appliance, which includes the functions of roasting, baking, stewing, slow cooking, rice cooking, searing/sautéing, steaming and food warming. Instant Pot is printed on the front of the multicookers. Gem 65 8-in-1 and a batchcode of 1728, 1730, 1731, 1734 or 1746 are printed on the rating label on the underside of the product.",
    "URL": "https://www.cpsc.gov/Recalls/2018/Double-Insight-Recalls-Multicookers-Due-to-Fire-Hazard-Sold-Exclusively-at-Walmart",
    "Title": "Double Insight Recalls Multicookers Due to Fire Hazard; Sold Exclusively at Walmart",
    "ConsumerContact": "Double Insight toll-free at 888-891-1473 from 8:30 a.m. to 10 p.m. ET Monday through Friday and from 10 a.m. to 6 p.m. ET Saturday and Sunday or online at www.instantpot.com and click on “Product Recall” or visit www.gemmulticooker.com for more information.",
    "LastPublishDate": "2018-03-01T00:00:00",
    "Products": [
      {
        "Name": "Gem 65 8-in-1 multicookers",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 104,000"
      }
    ],
```
Excerpt (RecallNumber = 18-110 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "A manufacturer defect can cause the multicooker to overheat and melt on the underside, posing a fire hazard.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately stop using the recalled multicookers, unplug the unit and return it to Walmart to receive a free replacement."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Replace"
```

### S16. CPSC recall page for 18-110 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2018/Double-Insight-Recalls-Multicookers-Due-to-Fire-Hazard-Sold-Exclusively-at-Walmart
- Retrieved (UTC): 2026-10-22T03:32:11Z
Excerpt (CPSC page 18-110, summary block):
```
Name of Product:
Gem 65 8-in-1 multicookers
Hazard:
A manufacturer defect can cause the multicooker to overheat and melt on the underside, posing a fire hazard.
Remedy:
Refund
Replace
Recall Date:
March 01, 2018
Units:
About 104,000
```
Excerpt (CPSC page 18-110, details block):
```
Description:
This recall involves Gem 65 8-in-1 model multicookers, a multifunctional, programmable cooking appliance, which includes the functions of roasting, baking, stewing, slow cooking, rice cooking, searing/sautéing, steaming and food warming. Instant Pot is printed on the front of the multicookers. Gem 65 8-in-1 and a batchcode of 1728, 1730, 1731, 1734 or 1746 are printed on the rating label on the underside of the product.
Remedy:
Consumers should immediately stop using the recalled multicookers, unplug the unit and return it to Walmart to receive a full refund or contact Double Insight to receive a free replacement.
Incidents/Injuries:
Double Insight has received 107 reports of overheating, five resulting in minor property damage. No injuries have been reported.
Sold Exclusively At:
Walmart stores nationwide and online at www.walmart.com from August 2017 through January 2018 for about $80.
Manufacturer(s):
Foshan Linshine Technology Co., Guangdong, China
Importer(s):
Double Insight Inc., of Canada
Distributor(s):
Double Insight Inc., of Canada
Manufactured In:
China
Recall number:
18-110
```

### S17. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=VH101
- Retrieved (UTC): 2026-10-22T03:29:54Z
Excerpt (ProductName = VH101 response, record 1 of 2):
```
{
  "RecallID": 8381,
  "RecallNumber": "18199",
  "RecallDate": "2018-08-22T00:00:00",
  "Description": "This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. \"Vornado\" with a \"V\" behind it is printed on the front of the unit. The model/type \"VH101,\" serial number and ETL mark are printed on a silver rating label on the bottom of the unit.",
  "URL": "https://www.cpsc.gov/Recalls/2018/Vornado-Air-Reannounces-Recall-of-Electric-Space-Heaters-Following-Report-of-Death-Fire-and-Burn-Hazards",
  "Title": "Vornado Air Reannounces Recall of Electric Space Heaters Following Report of Death; Fire and Burn Hazards",
  "ConsumerContact": "Vornado toll-free at 855-215-5131 from 8 a.m. to 5 p.m. CT Monday through Friday or online at www.vornado.com and click on “Recalls” in the lower right corner of the homepage or www.vornado.com/recalls and click on the VH101 Personal Heater recall button for more information.",
  "LastPublishDate": "2018-08-22T00:00:00",
  "Products": [
    {
      "Name": "VH101 Personal Vortex electric space heaters",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 350,000 (This recall was first announced in April 2018)"
```
Excerpt (ProductName = VH101 response, record 2 of 2):
```
{
  "RecallID": 8298,
  "RecallNumber": "18136",
  "RecallDate": "2018-04-04T00:00:00",
  "Description": "This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. \"Vornado\" with a \"V\" behind it is printed on the front of the unit. The model/type \"VH101,\" serial number and ETL mark are printed on a silver rating label on the bottom of the unit.",
  "URL": "https://www.cpsc.gov/Recalls/2018/Vornado-Air-Recalls-Electric-Space-Heaters-Due-to-Fire-and-Burn-Hazards",
  "Title": "Vornado Air Recalls Electric Space Heaters Due to Fire and Burn Hazards",
  "ConsumerContact": "Vornado toll-free at 855-215-5131 from 8 a.m. to 5p.m. CT Monday through Friday or online at www.vornado.com and click on “Recalls” in the lower right corner of the homepage or www.vornado.com/recalls and click on the VH101 Personal Heater recall button for more information.",
  "LastPublishDate": "2018-04-04T00:00:00",
  "Products": [
    {
      "Name": "VH101 Personal Vortex electric space heaters",
      "Description": "",
      "Model": "",
      "Type": "",
      "CategoryID": "",
      "NumberOfUnits": "About 350,000"
```

### S18. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=18-136
- Retrieved (UTC): 2026-10-22T03:29:21Z
Excerpt (RecallNumber = 18-136 response, part 1):
```
[
  {
    "RecallID": 8298,
    "RecallNumber": "18136",
    "RecallDate": "2018-04-04T00:00:00",
    "Description": "This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. \"Vornado\" with a \"V\" behind it is printed on the front of the unit. The model/type \"VH101,\" serial number and ETL mark are printed on a silver rating label on the bottom of the unit.",
    "URL": "https://www.cpsc.gov/Recalls/2018/Vornado-Air-Recalls-Electric-Space-Heaters-Due-to-Fire-and-Burn-Hazards",
    "Title": "Vornado Air Recalls Electric Space Heaters Due to Fire and Burn Hazards",
    "ConsumerContact": "Vornado toll-free at 855-215-5131 from 8 a.m. to 5p.m. CT Monday through Friday or online at www.vornado.com and click on “Recalls” in the lower right corner of the homepage or www.vornado.com/recalls and click on the VH101 Personal Heater recall button for more information.",
    "LastPublishDate": "2018-04-04T00:00:00",
    "Products": [
      {
        "Name": "VH101 Personal Vortex electric space heaters",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 350,000"
      }
    ],
```
Excerpt (RecallNumber = 18-136 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "The electric space heater can overheat when in use, posing fire and burn hazards.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit, including free shipping."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Refund"
      },
      {
        "Option": "Replace"
```

### S19. CPSC recall page for 18-136 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2018/Vornado-Air-Recalls-Electric-Space-Heaters-Due-to-Fire-and-Burn-Hazards
- Retrieved (UTC): 2026-10-22T03:31:57Z
Excerpt (CPSC page 18-136, summary block):
```
Name of Product:
VH101 Personal Vortex electric space heaters
Hazard:
The electric space heater can overheat when in use, posing fire and burn hazards.
Remedy:
Refund
Replace
Recall Date:
April 04, 2018
Units:
About 350,000 |[This recall was reannounced on August 22, 2018](https://www.cpsc.gov/Recalls/2018/Vornado-Air-Reannounces-Recall-of-Electric-Space-Heaters-Following-Report-of-Death-Fire-and-Burn-Hazards)
```
Excerpt (CPSC page 18-136, details block):
```
Description:
This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. “Vornado” with a “V” behind it is printed on the front of the unit. The model/type “VH101,” serial number and ETL mark are printed on a silver rating label on the bottom of the unit.
Remedy:
Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit, including free shipping.
Incidents/Injuries:
Vornado has received 15 reports of the heaters catching on fire.
Sold At:
Bed Bath & Beyond, Home Depot, Menards, Orchard Supply, Target and other stores nationwide and online at Amazon.com, Target.com, Vornado.com and other websites from August 2009 through March 2018 for about $30.
Importer(s):
Vornado Air LLC, of Andover, Kan.
Manufactured In:
China
Recall number:
18-136
```

### S20. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=18-199
- Retrieved (UTC): 2026-10-22T03:29:22Z
Excerpt (RecallNumber = 18-199 response, part 1):
```
[
  {
    "RecallID": 8381,
    "RecallNumber": "18199",
    "RecallDate": "2018-08-22T00:00:00",
    "Description": "This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. \"Vornado\" with a \"V\" behind it is printed on the front of the unit. The model/type \"VH101,\" serial number and ETL mark are printed on a silver rating label on the bottom of the unit.",
    "URL": "https://www.cpsc.gov/Recalls/2018/Vornado-Air-Reannounces-Recall-of-Electric-Space-Heaters-Following-Report-of-Death-Fire-and-Burn-Hazards",
    "Title": "Vornado Air Reannounces Recall of Electric Space Heaters Following Report of Death; Fire and Burn Hazards",
    "ConsumerContact": "Vornado toll-free at 855-215-5131 from 8 a.m. to 5 p.m. CT Monday through Friday or online at www.vornado.com and click on “Recalls” in the lower right corner of the homepage or www.vornado.com/recalls and click on the VH101 Personal Heater recall button for more information.",
    "LastPublishDate": "2018-08-22T00:00:00",
    "Products": [
      {
        "Name": "VH101 Personal Vortex electric space heaters",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 350,000 (This recall was first announced in April 2018)"
      }
    ],
```
Excerpt (RecallNumber = 18-199 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "The electric space heater can overheat when in use, posing fire and burn hazards.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Refund"
      },
      {
        "Option": "Replace"
```

### S21. CPSC recall page for 18-199 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2018/Vornado-Air-Reannounces-Recall-of-Electric-Space-Heaters-Following-Report-of-Death-Fire-and-Burn-Hazards
- Retrieved (UTC): 2026-10-22T03:32:00Z
Excerpt (CPSC page 18-199, summary block):
```
Name of Product:
VH101 Personal Vortex electric space heaters
Hazard:
The electric space heater can overheat when in use, posing fire and burn hazards.
Remedy:
Refund
Replace
Recall Date:
August 22, 2018
Units:
About 350,000 ([This recall was first announced in April 2018.](https://www.cpsc.gov/Recalls/2018/Vornado-Air-Recalls-Electric-Space-Heaters-Due-to-Fire-and-Burn-Hazards))
```
Excerpt (CPSC page 18-199, details block):
```
Description:
This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. “Vornado” with a “V” behind it is printed on the front of the unit. The model/type “VH101,” serial number and ETL mark are printed on a silver rating label on the bottom of the unit.
Remedy:
Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit.
Incidents/Injuries:
In December 2017, a 90-year-old man in Chanhassen, Minnesota died as a result of a fire involving the recalled heater. Vornado has received a total of 19 reports of the heaters catching on fire.
Sold At:
Bed Bath & Beyond, Home Depot, Menards, Orchard Supply, Target and other stores nationwide and online at Amazon.com, Target.com, Vornado.com and other websites from August 2009 through March 2018 for about $30.
Importer(s):
Vornado Air LLC, of Andover, Kan.
Manufactured In:
China
Recall number:
18-199
```

### S22. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Top-Load%20Washing%20Machines&RecallDateStart=2018-01-01&RecallDateEnd=2023-12-31
- Retrieved (UTC): 2026-10-22T03:30:56Z
Excerpt (Samsung subject query response, part 1):
```
[
  {
    "RecallID": 9486,
    "RecallNumber": "23080",
    "RecallDate": "2022-12-22T00:00:00",
    "Description": "This recall involves several models of Samsung's top-load washers with super speed wash. The washers were sold in white, black, champagne, and ivory colors and include model series WA49B, WA50B, WA51A, WA52A, WA54A, and WA55A. The model and serial numbers are found on the washer's label attached to the inside of the top lid. An additional label is located on the rear of the washer. The following model and serial number ranges are included in the recall: Model Number Serial Number Range WA49B5105AV/US 01J457BT700001W through 01J457BTB00111H WA49B5105AW/US 01J557BT700001J through 01J557BT700010D WA49B5205AW/US 01HH57BT300006X through 01HH57BTB00932W WA50B5100AV/US 01J257BT70001B through 01J257BTB01232B WA50B5100AW/US 01J357BT770001L through 01J357BT700010F WA51A5505AC/US 01HA57BR700003P through 01HA57BTB00346F WA51A5505AV/US 01H257BR600003R through 01H257BTB02018L WA51A5505AW/US 01GY57BR600026P through 01GY57BTB00269W WA52A5500AC/US 01HB57BR700003Y through 01HB57BTB02968X WA52A5500AV/US 01H357BR600006A through 01H357BTB01820Y WA52A5500AW/US 01H457BR600003X through 01H457BTB01503Y WA54A7305AV/US 01H557BR600003P through 01H557BR800650T WA55A7300AE/US 01H057BR600001H through 01H057BTB05872Z WA55A7700AV/US 01H157BR600151Z through 01H157ZT700005K",
    "URL": "https://www.cpsc.gov/Recalls/2023/Samsung-Recalls-Top-Load-Washing-Machines-Due-to-Fire-Hazard-Software-Repair-Available",
    "Title": "Samsung Recalls Top-Load Washing Machines Due to Fire Hazard; Software Repair Available",
    "ConsumerContact": "Samsung at http://www.samsung.com and http://www.samsung.com/us/support/tlw-sw-update or by phone toll-free at 833-916-4555 from 8 a.m. to 12 a.m. ET daily.",
    "LastPublishDate": "2022-12-22T00:00:00",
    "Products": [
      {
        "Name": "Samsung Top-Load Washing Machines",
        "Description": "",
        "Model": "",
        "Type": "",
        "CategoryID": "",
        "NumberOfUnits": "About 663,500"
      }
    ],
```
Excerpt (Samsung subject query response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "The washing machines can short-circuit and overheat, posing a fire hazard.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately check whether their washer's software has been updated to prevent the hazard; and, if not, consumers should immediately stop using the washer until the software is updated. Instructions on how to check whether a washer's software has been updated can be found here https://www.samsung.com/us/support/tlw-sw-update. All Wi-Fi equipped washers that are plugged into a power source and actively connected to the internet will automatically download the free software repair over-the-air when they are connected to the internet. Consumers who have not connected their Wi-Fi equipped washer to the internet should contact Samsung for instructions on how to download the software repair. Consumers whose washer does not have Wi-Fi capability or who otherwise wish to receive a free software repair without connecting to the internet, should immediately stop using the washer and contact Samsung directly for a free dongle to plug in and download the free software repair."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "Repair"
```

### S23. CPSC recall page for 23-080 (cpsc.gov)
- Query URL: https://www.cpsc.gov/Recalls/2023/Samsung-Recalls-Top-Load-Washing-Machines-Due-to-Fire-Hazard-Software-Repair-Available
- Retrieved (UTC): 2026-10-22T03:32:03Z
Excerpt (CPSC page 23-080, summary block):
```
Name of Product:
Samsung Top-Load Washing Machines
Hazard:
The washing machines can short-circuit and overheat, posing a fire hazard.
Remedy:
Repair
Recall Date:
December 22, 2022
Units:
About 663,500
```
Excerpt (CPSC page 23-080, details block part 1):
```
Description:
This recall involves several models of Samsung’s top-load washers with super speed wash. The washers were sold in white, black, champagne, and ivory colors and include model series WA49B, WA50B, WA51A, WA52A, WA54A, and WA55A. The model and serial numbers are found on the washer’s label attached to the inside of the top lid. An additional label is located on the rear of the washer. The following model and serial number ranges are included in the recall:
| **Model Number** | **Serial Number Range** |
| --- | --- |
| WA49B5105AV/US | 01J457BT700001W through 01J457BTB00111H |
| WA49B5105AW/US | 01J557BT700001J through 01J557BT700010D |
| WA49B5205AW/US | 01HH57BT300006X through 01HH57BTB00932W |
| WA50B5100AV/US | 01J257BT70001B through 01J257BTB01232B |
| WA50B5100AW/US | 01J357BT770001L through 01J357BT700010F |
| WA51A5505AC/US | 01HA57BR700003P through 01HA57BTB00346F |
| WA51A5505AV/US | 01H257BR600003R through 01H257BTB02018L |
| WA51A5505AW/US | 01GY57BR600026P through 01GY57BTB00269W |
| WA52A5500AC/US | 01HB57BR700003Y through 01HB57BTB02968X |
| WA52A5500AV/US | 01H357BR600006A through 01H357BTB01820Y |
| WA52A5500AW/US | 01H457BR600003X through 01H457BTB01503Y |
| WA54A7305AV/US | 01H557BR600003P through 01H557BR800650T |
| WA55A7300AE/US | 01H057BR600001H through 01H057BTB05872Z |
| WA55A7700AV/US | 01H157BR600151Z through 01H157ZT700005K |
```
Excerpt (CPSC page 23-080, details block part 2):
```
Remedy:
Consumers should immediately check whether their washer’s software has been updated to prevent the hazard; and, if not, consumers should immediately stop using the washer until the software is updated. Instructions on how to check whether a washer’s software has been updated can be found here [https://www.samsung.com/us/support/tlw-sw-update](https://www.samsung.com/us/support/tlw-sw-update)
All Wi-Fi equipped washers that are plugged into a power source and actively connected to the internet will automatically download the free software repair over-the-air when they are connected to the internet. Consumers who have not connected their Wi-Fi equipped washer to the internet should contact Samsung for instructions on how to download the software repair.
Consumers whose washer does not have Wi-Fi capability or who otherwise wish to receive a free software repair without connecting to the internet, should immediately stop using the washer and contact Samsung directly for a free dongle to plug in and download the free software repair.
Incidents/Injuries:
Samsung has received 51 reports of smoking, melting, overheating or fire involving the washers; 10 of which resulted in property damage. Three consumers have reported injuries due to smoke inhalation.
Sold At:
Best Buy, Costco, The Home Depot, Lowe’s and other appliance stores nationwide and online at Samsung.com from June 2021 through December 2022 for between $900 and $1,500.
Distributor(s):
Samsung Electronics America Inc., of Ridgefield Park, New Jersey
Manufactured In:
United States
Recall number:
23-080
```

### S24. NHTSA recalls API (api.nhtsa.gov recallsByVehicle)
- Query URL: https://api.nhtsa.gov/recalls/recallsByVehicle?make=Hyundai&model=Elantra&modelYear=2021
- Retrieved (UTC): 2026-10-22T11:48:10Z
- Note: on this fresh retrieval the response returns the six campaigns in the order 21V796000, 21V00M000, 21V302000, 22V218000, 22V354000, 24V879000. The excerpts below follow that response order.
Excerpt (Response head and campaign 1 of 6, in response order):
```
{
  "Count": 6,
  "Message": "Results returned successfully",
  "results": [
    {
      "Manufacturer": "Hyundai Motor America",
      "NHTSACampaignNumber": "21V796000",
      "parkIt": false,
      "parkOutSide": false,
      "overTheAirUpdate": false,
      "ReportReceivedDate": "13/10/2021",
      "Component": "SEAT BELTS:FRONT",
      "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2021 Elantra, Elantra HEV, Venue, Genesis GV80 and 2022 Genesis GV70 vehicles.  In the event of a crash, the front driver-side and/or passenger-side seat belt pretensioner(s) may explode upon deployment.",
      "Consequence": "An exploding seat belt pretensioner could project metal fragments into the vehicle, striking vehicle occupants and resulting in injury.",
      "Remedy": "Dealers will replace the seat belt pretensioners, free of charge.  Owner notification letters were mailed February 10, 2022. Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's numbers for this recall are 211 and 009G.  This recall is replaced by NHTSA recall numbers 22V-354 for Elantra and Elantra HEV vehicles, 22V-458 for Venue vehicles, and 23V-094 for Genesis vehicles.  Elantra, Elantra HEV, Venue, and Genesis vehicles already repaired under this recall will need to have the new remedies completed.",
      "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.nhtsa.gov.",
      "ModelYear": "2021",
      "Make": "HYUNDAI",
      "Model": "ELANTRA"
    },
```
Excerpt (Campaign 2 of 6, in response order):
```
{
  "Manufacturer": "Hyundai Motor America",
  "NHTSACampaignNumber": "21V00M000",
  "parkIt": false,
  "parkOutSide": false,
  "overTheAirUpdate": false,
  "ReportReceivedDate": "28/12/2021",
  "Component": "VISIBILITY:WINDSHIELD",
  "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2020-2021 Santa Fe, 2021 Sonata, and Elantra vehicles.  During manufacturing, the windshield may not have been properly bonded to the vehicle, allowing it to detach in a crash.",
  "Consequence": "A windshield that detaches from a vehicle during a crash can increase the risk of injury.",
  "Remedy": "Dealers will remove and reinstall the front windshield panel, free of charge.  Owner notification letters were mailed June 20, 2022.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 216.",
  "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.nhtsa.gov.",
  "ModelYear": "2021",
  "Make": "HYUNDAI",
  "Model": "ELANTRA"
},
```
Excerpt (Campaign 3 of 6, in response order):
```
{
  "Manufacturer": "Hyundai Motor America",
  "NHTSACampaignNumber": "21V302000",
  "parkIt": false,
  "parkOutSide": false,
  "overTheAirUpdate": false,
  "ReportReceivedDate": "28/04/2021",
  "Component": "SEATS:FRONT ASSEMBLY:RECLINER",
  "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2021 Elantra vehicles.  The driver and front passenger seat back recliners may have been improperly welded.",
  "Consequence": "An improperly welded seat back recliner could separate from the seat back frame during a crash, increasing the risk of injury.",
  "Remedy": "Dealers will inspect and if necessary, replace the seat back frame assembly, free of charge.  Owner notification letters were mailed on June 21, 2021.  Owners may contact Hyundai customer service at 1-888-371-9460.  Hyundai's number for this recall is 204.",
  "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.safercar.gov.",
  "ModelYear": "2021",
  "Make": "HYUNDAI",
  "Model": "ELANTRA"
},
```
Excerpt (Campaign 4 of 6, in response order):
```
{
  "Manufacturer": "Hyundai Motor America",
  "NHTSACampaignNumber": "22V218000",
  "parkIt": false,
  "parkOutSide": false,
  "overTheAirUpdate": false,
  "ReportReceivedDate": "01/04/2022",
  "Component": "SEAT BELTS:FRONT",
  "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2021-2022 Elantra and 2020 Accent vehicles.  In the event of a crash, the front driver and passenger-side seat belt pretensioners may explode upon deployment.",
  "Consequence": "Exploding seat belt pretensioners can project metal fragments into the vehicle, strike vehicle occupants, and result in injury.",
  "Remedy": "Dealers will replace the seat belt pretensioners, free of charge.  Interim notification letters, notifying owners of the safety risk, were mailed on May 31, 2022. A second notice will be sent once remedy parts become available.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 223.  This recall is replaced by NHTSA recall number 22V-354.  Vehicles already repaired under this recall will need to have the new remedy completed.",
  "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.nhtsa.gov.",
  "ModelYear": "2021",
  "Make": "HYUNDAI",
  "Model": "ELANTRA"
},
```
Excerpt (Campaign 5 of 6, in response order):
```
{
  "Manufacturer": "Hyundai Motor America",
  "NHTSACampaignNumber": "22V354000",
  "parkIt": false,
  "parkOutSide": false,
  "overTheAirUpdate": false,
  "ReportReceivedDate": "19/05/2022",
  "Component": "SEAT BELTS:FRONT",
  "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2020-2022 Accent, 2021-2022 Elantra, and 2021-2022 Elantra HEV vehicles.   In the event of a crash, the front driver-side and/or passenger-side seat belt pretensioners may explode upon deployment.",
  "Consequence": "An exploding seat belt pretensioner can project metal fragments into the vehicle, strike vehicle occupants, and result in injury.",
  "Remedy": "Dealers will secure the seat belt pretensioner(s) with a cap, free of charge.  Owner notification letters were mailed August 28, 2022.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 229.  This recall expands and replaces NHTSA recall numbers 21V-796, 22V-069, 22V-218, and 22V-123 for Accent, Elantra, and Elantra HEV vehicles.  All Accent, Elantra, and Elantra HEV vehicles already repaired under the previous recalls will need to have the new remedy completed.",
  "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153), or go to www.nhtsa.gov.",
  "ModelYear": "2021",
  "Make": "HYUNDAI",
  "Model": "ELANTRA"
},
```
Excerpt (Campaign 6 of 6, in response order):
```
{
  "Manufacturer": "Hyundai Motor America",
  "NHTSACampaignNumber": "24V879000",
  "parkIt": false,
  "parkOutSide": false,
  "overTheAirUpdate": false,
  "ReportReceivedDate": "21/11/2024",
  "Component": "BACK OVER PREVENTION: SENSING SYSTEM: CAMERA",
  "Summary": "Hyundai Motor America (Hyundai) is recalling certain 2021-2022 Santa Fe, Santa Fe HEV, Elantra, Elantra HEV and 2022 Elantra N and Santa Fe PHEV vehicles.  Due to a damaged printed circuit board, the rearview camera image may fail to display.  As such, these vehicles fail to comply with the requirements of Federal Motor Vehicle Safety Standard number 111, \"Rear Visibility.\"",
  "Consequence": "A rearview image that does not display reduces the driver's visibility and increases the risk of a crash.",
  "Remedy": "Dealers will replace the rearview camera, free of charge.  Owner notification letters were mailed January 14, 2025.  Owners may contact Hyundai customer service at 1-855-371-9460.  Hyundai's number for this recall is 271.",
  "Notes": "Owners may also contact the National Highway Traffic Safety Administration Vehicle Safety Hotline at 1-888-327-4236 (TTY 1-800-424-9153) or go to nhtsa.gov.",
  "ModelYear": "2021",
  "Make": "HYUNDAI",
  "Model": "ELANTRA"
}
```

### S25. CPSC public recall API (SaferProducts.gov RestWebServices)
- Query URL: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=13-087
- Retrieved (UTC): 2026-10-22T11:48:09Z
- Note: this is the separate detail query for Fisher-Price recall 13-087. Its response holds the single record for that recall, the same record that is record 3 of 3 in the S4 ProductName response. The excerpts below are quoted from the start of this detail response and, following that, contiguously from the same response.
Excerpt (RecallNumber = 13-087 response, part 1):
```
[
  {
    "RecallID": 1285,
    "RecallNumber": "13087",
    "RecallDate": "2013-01-08T00:00:00",
    "Description": "This recall to inspect includes all Fisher-Price Rock N' Play infant recliner seats called sleepers. The sleeper is designed for babies up to 25 pounds and is composed of a soft plastic seat held by a metal rocking frame. The product has a removable, fabric cover that is sold in 14 patterns and color palettes.",
    "URL": "https://www.cpsc.gov/Recalls/2013/Fisher-Price-Recalls-to-Inspect-Rock-N-Play-Infant-Sleepers-Due-to-Risk-of-Exposure-to-Mold",
    "Title": "Fisher-Price Recalls to Inspect Rock 'N Play Infant Sleepers Due to Risk of Exposure to Mold",
    "ConsumerContact": "Fisher-Price; at (800) 432-5437, from 9 a.m. to 6 p.m. ET Monday through Friday, or online at www.service.mattel.com for more information.",
    "LastPublishDate": "2015-01-13T00:00:00",
    "Products": [
      {
        "Name": "Newborn Rock 'n Play Sleeper™",
        "Description": "",
        "Model": "",
        "Type": "Bassinets and Cradles",
        "CategoryID": "67558",
        "NumberOfUnits": "About 800,000 units"
      }
    ],
```
Excerpt (RecallNumber = 13-087 response, part 2):
```
    "ProductUPCs": [],
    "Hazards": [
      {
        "Name": "Mold can develop between the removable seat cushion and the hard plastic frame of the sleeper when it remains wet/moist or is infrequently cleaned, posing a risk of exposure to mold to infants sleeping in the product. The CPSC advises that mold has been associated with respiratory illnesses and other infections. Although mold is not present at the time of purchase, mold growth can occur after use of the product.",
        "HazardType": "",
        "HazardTypeID": ""
      }
    ],
    "Remedies": [
      {
        "Name": "Consumers should immediately check for mold under the removable seat cushion. Dark brown, gray or black spots can indicate the presence of mold. If mold is found, consumers should immediately stop using the product. Consumers can contact Fisher-Price for cleaning instructions or further assistance. Cleaning and care instructions can also be found at www.service.mattel.com or by contacting the firm."
      }
    ],
    "RemedyOptions": [
      {
        "Option": "New Instructions"
      },
      {
        "Option": "Repair"
      }
```
