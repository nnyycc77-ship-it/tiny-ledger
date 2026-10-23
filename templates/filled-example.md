# Filled example: a recall check delivery with the checklist applied

This file is the workstream D filled example (BACKLOG.md item D.3, issue #61).
It is built from one real published delivery in this repository and shows the
delivery checklist applied end to end: claim lines, the exact query and UTC
retrieval time for every query, the source link with the raw excerpt printed
directly beneath it verbatim, an empty result proven by the complete raw
response, and near matches listed as checked and excluded with reasons.

Source delivery: [`deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md`](../deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md)
(revision 1 of the recall check delivered on Synmerco escrow esc_e42fa25f7ced, added to this
repository in commit c638fef). Every figure, date, count, URL, retrieval time and
excerpt below is copied from that file line for line; nothing here was
fetched, edited or invented for this example. The test
`tools/tests/test_filled_example.py` checks that every body line of this file is
a line of the source delivery.

What is copied: two of the delivery's six subjects, chosen because together
they exercise every checklist item. Subject 1 (Peloton Tread+) shows a title
search whose other records are named and set aside, a detail query, and a
remedy read from the recall page because the API field repeats the hazard.
Subject 3 (Instant Pot Smart WiFi 6 Qt) shows an empty result proven by the
complete raw HTTP transcript, and two near matches checked and excluded with
the reason. The delivery's own source numbering (S1 to S3, S10 to S16) is kept,
so each excerpt can be found in the source file under the same label. The
delivery's revision note and its other four subjects are omitted here; they
are in the source file.

How to read it: the body between the two markers below is the delivery text,
arranged under the report skeleton headings. Lines in italics that begin with
*Checklist* are this example's annotations and are not part of a delivery;
they point at the checklist item each passage satisfies. The applied
checklist itself is at the end.

<!-- example body begins -->

# Recall check: six named consumer products in the CPSC and NHTSA recall databases

## Scope and inputs

*Checklist 1 applied: the delivery opens with its scope, what was and was not done, and how each subject is reported.*

Observation only: this report records what the public recall databases show; no product was bought, sold, handled, or tested.

This report was produced by unattended agent work using public sources only.

Each subject states the query run, the UTC retrieval time, and the number of results, followed by every matching recall with the values as shown in the source. Verbatim raw excerpts for every query and every recall are in the Sources section at the end.

## Subject 1: Peloton Tread+ treadmill

Database: CPSC public recall data (SaferProducts.gov RestWebServices API), with the remedy text read from the CPSC recall page for the same record.

*Checklist 2 applied: the exact query, its UTC retrieval time and its result count are stated before any claim; the records that belong to other subjects are named, not dropped silently.*

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

## Subject 3: Instant Pot Smart WiFi 6 Qt

Database: CPSC public recall data (SaferProducts.gov RestWebServices API).

*Checklist 3 applied: an empty result is stated with its query, retrieval time and count, and it points at the complete raw transcript in the Sources section (S10). "None found" alone would prove nothing.*

QUERY: ProductName = "Instant Pot Smart WiFi" returned 0 records (retrieved 2026-10-22T11:48:05Z). The complete body of the response was an empty array; the complete raw HTTP response transcript for this query, headers and body, is shown verbatim in the Sources section (source S10).

RECALLS: none found for the Instant Pot Smart WiFi 6 Qt.

## Checked and excluded

*Checklist 4 applied: near matches the operator checked are listed with the query that found them, the retrieval time, and the reason they are excluded. In the source delivery this paragraph and the two records sit inline under Subject 3; the skeleton gives them their own section.*

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

## Summary table

*Checklist 5 applied: the summary repeats only figures already stated above, subject by subject. Only the two subjects copied into this example are shown here.*

| Subject | Recalls found | Most recent recall date |
| --- | --- | --- |
| Peloton Tread+ treadmill | 1 | May 5, 2021 |
| Instant Pot Smart WiFi 6 Qt | 0 (none found) | none |

## Sources

Every excerpt below is pasted verbatim from the response or page named above it. API responses are shown pretty printed, one JSON value per line, with the values unchanged. Source S10 is the one exception in form: it is a complete raw HTTP response transcript, status line and headers in the order returned followed by the body exactly as returned. Sources S4, S10, S24 and S25 were recaptured fresh for this revision at the UTC times shown in their headings, and their excerpts are quoted contiguously from those fresh responses.

*Checklist 6 applied: every source has its exact query URL and UTC retrieval time, and the raw excerpt is printed directly beneath its own link, verbatim and unreformatted. S10 is the complete raw HTTP response transcript for the empty result: status line, headers in the order returned, blank line, body.*

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

<!-- example body ends -->

## Delivery checklist, as applied above

Each item is the rule from `AGENT-BRIEF.md` hard rules 2 and 3 and the revision
lessons recorded in `BACKLOG.md` workstream D, with the place in this example
where it is met.

- [x] 1. Scope stated first: what was checked, what was not done, how each subject is reported (the three opening lines under Scope and inputs).
- [x] 2. Every query recorded with its exact form, its UTC retrieval time and its result count, before any claim (the QUERY line of each subject; the Query URL and Retrieved lines of each source).
- [x] 3. An empty result proven by the complete raw response, never asserted (Subject 3 and source S10, the full HTTP transcript ending in the empty array).
- [x] 4. Near matches listed as checked and excluded with the reason, each backed by its own source (the Checked and excluded section; sources S11 to S16).
- [x] 5. No figure appears that is not in a source excerpt: every recall number, date, unit count and remedy in the subject sections is read from the excerpt under the matching source (S1 to S3 for Subject 1; S10 to S16 for Subject 3).
- [x] 6. Every claim sits with its source link and the raw excerpt is printed directly beneath that link, verbatim, unreformatted and unreordered; a field that repeats another field is noted and read from the page instead (Subject 1, recall 21-128, with S2 and S3).
- [x] 7. Nothing invented: where the source shows no value, the report says so plainly (NHTSA unit counts in the source delivery are stated as not shown; this example's subjects carry every value from the record).
- [x] 8. The source delivery file is named in the header and every body line of this file is a line of it (checked by `tools/tests/test_filled_example.py`).

