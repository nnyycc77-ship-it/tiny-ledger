# Nonprofit check (ProPublica Nonprofit Explorer API v2): Feeding America

Produced by `tools/delivery_packager.py`. Every claim below sits under its source link with the complete raw response printed beneath it, and every summary line names the section that carries its evidence. Values are as the sources returned them at the stated retrieval times.

## Scope and inputs

- Service: Nonprofit check (ProPublica Nonprofit Explorer API v2)
- Subject: Feeding America
- Buyer ask, as given: Confirm this nonprofit's identity and its latest Form 990 figures on ProPublica Nonprofit Explorer.
- Inputs: `{"name": "Feeding America"}`
- Sources: replay of captures already committed in this repository; no request was made for this package
- Packaged (UTC): 2026-10-23T23:52:48Z
- Scope: only the queries listed in the sections below, as each source answered them. A section that finds nothing is a search observation, not a clearance.

## Summary

- Organizations on the search page for "Feeding America": 16. (Section S1)
- filings_with_data entries for EIN 363673599: 12. (Section S2)

## Section S1: ProPublica Nonprofit Explorer search "Feeding America"

### Search: "Feeding America"

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/search.json?q=Feeding+America
Retrieved (UTC): 2026-10-23T21:56:10Z
HTTP status: HTTP/1.1 200 OK

total_results as shown: 16. Organizations on this page: 16. num_pages as shown: 1.

- Result `363673599`: strein `"36-3673599"`, name `"Feeding America"`, city `"Chicago"`, state `"IL"`. Status: examined below.
- Result `921776845`: strein `"92-1776845"`, name `"Feeding America Texas"`, city `"Houston"`, state `"TX"`. Status: not examined.
- Result `933176598`: strein `"93-3176598"`, name `"Feeding America Florida"`, city `"Miami"`, state `"FL"`. Status: not examined.
- Result `382439659`: strein `"38-2439659"`, name `"Feeding America West Michigan"`, city `"Kentwood"`, state `"MI"`. Status: not examined.
- Result `334633736`: strein `"33-4633736"`, name `"Feeding America Children Inc"`, city `"Glendale"`, state `"AZ"`. Status: not examined.
- Result `933862964`: strein `"93-3862964"`, name `"Feeding America Real Meat"`, city `"Red Springs"`, state `"NC"`. Status: not examined.
- Result `412061798`: strein `"41-2061798"`, name `"Feeding Americas Hungry Children"`, city `"Peoria"`, state `"AZ"`. Status: not examined.
- Result `860986348`: strein `"86-0986348"`, name `"Feeding Americas Children Inc"`, city `"Peoria"`, state `"AZ"`. Status: not examined.
- Result `933703913`: strein `"93-3703913"`, name `"Feeding Americas Future Incorporated"`, city `"Ltl Torch Key"`, state `"FL"`. Status: not examined.
- Result `592116576`: strein `"59-2116576"`, name `"Feeding America Tampa Bay Inc"`, city `"Tampa"`, state `"FL"`. Status: not examined.
- Result `391384593`: strein `"39-1384593"`, name `"Feeding America Eastern Wisconsin Inc"`, city `"Milwaukee"`, state `"WI"`. Status: not examined.
- Result `611043635`: strein `"61-1043635"`, name `"Feeding America Kentuckys Heartland Inc"`, city `"Elizabethtown"`, state `"KY"`. Status: not examined.
- Result `391808502`: strein `"39-1808502"`, name `"Feeding America Eastern Wisconsin Foundation Inc"`, city `"Milwaukee"`, state `"WI"`. Status: not examined.
- Result `393788619`: strein `"39-3788619"`, name `"American-pinay Blog - Feeding Charity Philippines"`, city `"Rayne"`, state `"LA"`. Status: not examined.
- Result `330072922`: strein `"33-0072922"`, name `"Feeding America Riverside And San Bernardino Counties"`, city `"Riverside"`, state `"CA"`. Status: not examined.
- Result `273295358`: strein `"27-3295358"`, name `"The 3000 Club"`, city `"Phoenix"`, state `"AZ"`. Status: not examined.

Source: <https://projects.propublica.org/nonprofits/api/v2/search.json?q=Feeding+America>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:11 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=WXZCSMu9iTfKL7J.UanrP4j3x61tPXsqupSMvLVB3.U-1792792571.8666961-1.0.1.1-LSGuVpJ_Gn5sQKQ_AoXweaqs50OMqUHFLNsE1RrML.0; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd862e2880fd-SJC
CF-Cache-Status: HIT
Age: 68943
Cache-Control: public, max-age=86400
ETag: W/"5f1a557b483a4daef994080bbdfe1ef7"
Expires: Sat, 24 Oct 2026 21:56:11 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: ecb85b5f-fbb3-4947-a2b4-822e920caa33
x-runtime: 0.058974
Transfer-Encoding: chunked

{"total_results":16,"organizations":[{"ein":363673599,"strein":"36-3673599","name":"Feeding America","sub_name":"Feeding America","city":"Chicago","state":"IL","ntee_code":"K310","raw_ntee_code":"K310","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":95.01747},{"ein":921776845,"strein":"92-1776845","name":"Feeding America Texas","sub_name":"Feeding America Texas","city":"Houston","state":"TX","ntee_code":"K99","raw_ntee_code":"K99","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":85.25532},{"ein":933176598,"strein":"93-3176598","name":"Feeding America Florida","sub_name":"Feeding America Florida","city":"Miami","state":"FL","ntee_code":"K99","raw_ntee_code":"K99","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":85.25532},{"ein":382439659,"strein":"38-2439659","name":"Feeding America West Michigan","sub_name":"Feeding America West Michigan","city":"Kentwood","state":"MI","ntee_code":null,"raw_ntee_code":null,"subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":77.31572},{"ein":334633736,"strein":"33-4633736","name":"Feeding America Children Inc","sub_name":"Feeding America Children Inc","city":"Glendale","state":"AZ","ntee_code":"P30","raw_ntee_code":"P30","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":77.31572},{"ein":933862964,"strein":"93-3862964","name":"Feeding America Real Meat","sub_name":"Feeding America Real Meat","city":"Red Springs","state":"NC","ntee_code":"K20","raw_ntee_code":"K20","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":77.31572},{"ein":412061798,"strein":"41-2061798","name":"Feeding Americas Hungry Children","sub_name":"Feeding Americas Hungry Children","city":"Peoria","state":"AZ","ntee_code":"K30","raw_ntee_code":"K30","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":73.96247},{"ein":860986348,"strein":"86-0986348","name":"Feeding Americas Children Inc","sub_name":"Feeding Americas Children Inc","city":"Peoria","state":"AZ","ntee_code":"P60","raw_ntee_code":"P60","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":73.96247},{"ein":933703913,"strein":"93-3703913","name":"Feeding Americas Future Incorporated","sub_name":"Feeding Americas Future Incorporated","city":"Ltl Torch Key","state":"FL","ntee_code":"K30","raw_ntee_code":"K30","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":73.96247},{"ein":592116576,"strein":"59-2116576","name":"Feeding America Tampa Bay Inc","sub_name":"Feeding America Tampa Bay Inc","city":"Tampa","state":"FL","ntee_code":"K31Z","raw_ntee_code":"K31Z","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":70.73115},{"ein":391384593,"strein":"39-1384593","name":"Feeding America Eastern Wisconsin Inc","sub_name":"Feeding America Eastern Wisconsin Inc","city":"Milwaukee","state":"WI","ntee_code":"K310","raw_ntee_code":"K310","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":70.73115},{"ein":611043635,"strein":"61-1043635","name":"Feeding America Kentuckys Heartland Inc","sub_name":"Feeding America Kentuckys Heartland Inc","city":"Elizabethtown","state":"KY","ntee_code":"K31Z","raw_ntee_code":"K31Z","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":70.73115},{"ein":391808502,"strein":"39-1808502","name":"Feeding America Eastern Wisconsin Foundation Inc","sub_name":"Feeding America Eastern Wisconsin Foundation Inc","city":"Milwaukee","state":"WI","ntee_code":"K31I","raw_ntee_code":"K31I","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":65.18155},{"ein":393788619,"strein":"39-3788619","name":"American-pinay Blog - Feeding Charity Philippines","sub_name":"American-pinay Blog - Feeding Charity Philippines","city":"Rayne","state":"LA","ntee_code":"K30","raw_ntee_code":"K30","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":62.354557},{"ein":330072922,"strein":"33-0072922","name":"Feeding America Riverside And San Bernardino Counties","sub_name":"Feeding America Riverside And San Bernardino Counties","city":"Riverside","state":"CA","ntee_code":"K31Z","raw_ntee_code":"K31Z","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":60.440414},{"ein":273295358,"strein":"27-3295358","name":"The 3000 Club","sub_name":"The 3000 Club Dba Feeding Children In America","city":"Phoenix","state":"AZ","ntee_code":"P20","raw_ntee_code":"P20","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":19.76683}],"num_pages":1,"cur_page":0,"page_offset":0,"per_page":25,"search_query":"Feeding America","selected_state":null,"selected_ntee":null,"selected_code":null,"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```


## Section S2: ProPublica Nonprofit Explorer organization, EIN 363673599

### Organization: EIN 363673599

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json
Retrieved (UTC): 2026-10-23T21:56:10Z
HTTP status: HTTP/1.1 200 OK

Identity, from the organization block:

- Legal name (name) as shown: `"Feeding America"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"name":"Feeding America"
```

- EIN (ein) as shown: `363673599`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"ein":363673599
```

- City (city) as shown: `"Chicago"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"city":"Chicago"
```

- State (state) as shown: `"IL"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"state":"IL"
```

Figures, from the filings_with_data entry with the highest tax_prd (202306 of 12 entries). The response states no unit; values are as shown.

- Tax period of the filing (tax_prd) as shown: `202306`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"tax_prd":202306
```

- Total revenue (totrevenue) as shown: `4916912461`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"totrevenue":4916912461
```

- Total functional expenses (totfuncexpns) as shown: `4933690967`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"totfuncexpns":4933690967
```

- Total assets, end of year (totassetsend) as shown: `626129732`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"totassetsend":626129732
```

- Total liabilities, end of year (totliabend) as shown: `62229963`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"totliabend":62229963
```

- A later filing is listed without extracted figures (filings_without_data), tax_prd as shown: `202406`. No figure above comes from it.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F363673599_202406_990_2025051223426337.pdf"}
```

- Organization record tax_period as shown: `"2025-06-01"`. This is the organization block's field, not the period of the figures above.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>

```
"tax_period":"2025-06-01"
```

Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:12 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=AIhmWbnB2z0Q_vqJWSWfRUoYU6Cb9ufOek1EGczhlV4-1792792572.5939107-1.0.1.1-WvaBC8Q318EOLEcwSuhLFO908pWTTSMrzXNEnpN9EeQ; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd8abb3b4f08-SJC
CF-Cache-Status: HIT
Age: 81783
Cache-Control: public, max-age=86400
ETag: W/"b30a578f6e175189ada5e6b5da93262b"
Expires: Sat, 24 Oct 2026 21:56:12 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: 19380012-afb3-4522-a6f4-88d20fba9bf4
x-runtime: 0.196767
Transfer-Encoding: chunked

{"organization":{"id":363673599,"ein":363673599,"name":"Feeding America","careofname":"% DEBORAH HARRIS","address":"161 N CLARK ST STE 700","city":"Chicago","state":"IL","zipcode":"60601-3389","exemption_number":0,"subsection_code":3,"affiliation_code":3,"classification_codes":"1000","ruling_date":"1990-01-01","deductibility_code":1,"foundation_code":15,"activity_codes":"560000000","organization_code":1,"exempt_organization_status_code":1,"tax_period":"2025-06-01","asset_code":9,"income_code":9,"filing_requirement_code":1,"pf_filing_requirement_code":0,"accounting_period":6,"asset_amount":572495646,"income_amount":5109104956,"revenue_amount":5001395215,"ntee_code":"K310","sort_name":null,"created_at":"2023-05-09T20:29:29.059Z","updated_at":"2026-10-21T13:28:17.598Z","data_source":"current_2026_10_21","have_extracts":null,"have_pdfs":null,"latest_object_id":"202610909349301216"},"filings_with_data":[{"tax_prd":202306,"tax_prd_yr":2023,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=download990pdf_05_2024_prefixes_35-38%2F363673599_202306_990_2024050722387003.pdf","updated":"2025-08-05T16:09:03.394Z","totrevenue":4916912461,"totfuncexpns":4933690967,"totassetsend":626129732,"totliabend":62229963,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":4752844795,"totprgmrevnue":101808893,"invstmntinc":5023114,"txexmptbndsproceeds":0,"royaltsinc":55007782,"grsrntsreal":193852,"grsrntsprsnl":0,"rntlexpnsreal":318528,"rntlexpnsprsnl":0,"rntlincreal":-124676,"rntlincprsnl":0,"netrntlinc":-124676,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":1000114,"cstbasisothr":0,"gnlsecur":-1000114,"gnlsothr":0,"netgnls":-1000114,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":139375959,"lesscstofgoods":137963535,"netincsales":1412424,"miscrevtot11e":1940243,"compnsatncurrofcr":7068165,"othrsalwages":42446480,"payrolltx":3519394,"profndraising":1609306,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":563899769,"nonpfrea":"7","gftgrntsrcvd170":19042435108,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":364518582,"grsrcptsrelated170":740246542,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":202206,"tax_prd_yr":2022,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=download990pdf_06_2023_prefixes_36-41%2F363673599_202206_990_2023060721400096.pdf","updated":"2024-08-28T20:10:19.553Z","totrevenue":4267241782,"totfuncexpns":4231609823,"totassetsend":644823513,"totliabend":66462841,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":4152230760,"totprgmrevnue":47679794,"invstmntinc":1577662,"txexmptbndsproceeds":0,"royaltsinc":62123643,"grsrntsreal":237142,"grsrntsprsnl":0,"rntlexpnsreal":318528,"rntlexpnsprsnl":0,"rntlincreal":-81386,"rntlincprsnl":0,"netrntlinc":-81386,"grsalesecur":145458,"grsalesothr":0,"cstbasisecur":211962,"cstbasisothr":0,"gnlsecur":-66504,"gnlsothr":0,"netgnls":-66504,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":105070535,"lesscstofgoods":104345563,"netincsales":724972,"miscrevtot11e":3052841,"compnsatncurrofcr":5987410,"othrsalwages":36080997,"payrolltx":2871118,"profndraising":3584481,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":578360672,"nonpfrea":"7","gftgrntsrcvd170":17044179163,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":352789985,"grsrcptsrelated170":575456666,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":202106,"tax_prd_yr":2021,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F363673599_202106_990_2022040719831382.pdf","updated":"2023-08-07T19:39:17.885Z","totrevenue":4065318094,"totfuncexpns":3902891407,"totassetsend":603767243,"totliabend":38690535,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":3916234028,"totprgmrevnue":28800662,"invstmntinc":1689896,"txexmptbndsproceeds":0,"royaltsinc":115727530,"grsrntsreal":237108,"grsrntsprsnl":0,"rntlexpnsreal":318528,"rntlexpnsprsnl":0,"rntlincreal":-81420,"rntlincprsnl":0,"netrntlinc":-81420,"grsalesecur":1667218,"grsalesothr":0,"cstbasisecur":145656,"cstbasisothr":0,"gnlsecur":1521562,"gnlsothr":0,"netgnls":1521562,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":148318284,"lesscstofgoods":147839385,"netincsales":478899,"miscrevtot11e":946937,"compnsatncurrofcr":5856188,"othrsalwages":31899563,"payrolltx":128793,"profndraising":3368729,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":565076708,"nonpfrea":"07","gftgrntsrcvd170":15558243198,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":328111700,"grsrcptsrelated170":492592134,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":202006,"tax_prd_yr":2020,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=04_2021_prefixes_36-37%2F363673599_202006_990_2021041417944702.pdf","updated":"2022-07-01T20:31:17.918Z","totrevenue":3571430346,"totfuncexpns":3309075710,"totassetsend":432594156,"totliabend":32638854,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":3478482753,"totprgmrevnue":20326823,"invstmntinc":1930894,"txexmptbndsproceeds":0,"royaltsinc":68552710,"grsrntsreal":237076,"grsrntsprsnl":0,"rntlexpnsreal":318528,"rntlexpnsprsnl":0,"rntlincreal":-81452,"rntlincprsnl":0,"netrntlinc":-81452,"grsalesecur":125525,"grsalesothr":0,"cstbasisecur":147748,"cstbasisothr":0,"gnlsecur":-22223,"gnlsothr":0,"netgnls":-22223,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":73657752,"lesscstofgoods":72630105,"netincsales":1027647,"miscrevtot11e":1213194,"compnsatncurrofcr":4398170,"othrsalwages":28973099,"payrolltx":119305,"profndraising":2674356,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":399955302,"nonpfrea":"7","gftgrntsrcvd170":14018204301,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":246335688,"grsrcptsrelated170":382764190,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201906,"tax_prd_yr":2019,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=08_2020_prefixes_34-37%2F363673599_201906_990_2020082117249930.pdf","updated":"2021-08-30T18:52:57.265Z","totrevenue":2831620652,"totfuncexpns":2823972605,"totassetsend":156975013,"totliabend":18664170,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":2756779556,"totprgmrevnue":22629765,"invstmntinc":2030183,"txexmptbndsproceeds":0,"royaltsinc":49693518,"grsrntsreal":256472,"grsrntsprsnl":0,"rntlexpnsreal":318528,"rntlexpnsprsnl":0,"rntlincreal":-62056,"rntlincprsnl":0,"netrntlinc":-62056,"grsalesecur":565892,"grsalesothr":0,"cstbasisecur":135918,"cstbasisothr":0,"gnlsecur":429974,"gnlsothr":0,"netgnls":429974,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":46727425,"lesscstofgoods":47281910,"netincsales":-554485,"miscrevtot11e":674197,"compnsatncurrofcr":5609967,"othrsalwages":23685457,"payrolltx":2107580,"profndraising":3592191,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":138310843,"nonpfrea":"07","gftgrntsrcvd170":12690173944,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":203295152,"grsrcptsrelated170":357020507,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201806,"tax_prd_yr":2018,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=04_2019_prefixes_36-39%2F363673599_201806_990_2019040416206514.pdf","updated":"2021-08-30T18:41:21.566Z","totrevenue":2827633478,"totfuncexpns":2826138224,"totassetsend":148826212,"totliabend":18181684,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":2754138903,"totprgmrevnue":23606999,"invstmntinc":1235529,"txexmptbndsproceeds":0,"royaltsinc":47072720,"grsrntsreal":187902,"grsrntsprsnl":0,"rntlexpnsreal":122747,"rntlexpnsprsnl":0,"rntlincreal":65155,"rntlincprsnl":0,"netrntlinc":65155,"grsalesecur":561571,"grsalesothr":0,"cstbasisecur":272894,"cstbasisothr":0,"gnlsecur":288677,"gnlsothr":0,"netgnls":288677,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":54184485,"lesscstofgoods":53420943,"netincsales":763542,"miscrevtot11e":461953,"compnsatncurrofcr":4024835,"othrsalwages":24430857,"payrolltx":2050819,"profndraising":3658114,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":130644528,"nonpfrea":"07","gftgrntsrcvd170":11949664424,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":172437715,"grsrcptsrelated170":355409422,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201706,"tax_prd_yr":2017,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F363673599_201706_990_2018032715234353.pdf","updated":"2019-10-15T18:36:17.244Z","totrevenue":2717127060,"totfuncexpns":2684820721,"totassetsend":145276548,"totliabend":16277534,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":2654090409,"totprgmrevnue":22773762,"invstmntinc":746461,"txexmptbndsproceeds":0,"royaltsinc":38360347,"grsrntsreal":153354,"grsrntsprsnl":0,"rntlexpnsreal":184120,"rntlexpnsprsnl":0,"rntlincreal":-30766,"rntlincprsnl":0,"netrntlinc":-30766,"grsalesecur":381604,"grsalesothr":0,"cstbasisecur":101318,"cstbasisothr":0,"gnlsecur":280286,"gnlsothr":0,"netgnls":280286,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":49511297,"lesscstofgoods":49043066,"netincsales":468231,"miscrevtot11e":438330,"compnsatncurrofcr":3108254,"othrsalwages":22798231,"payrolltx":1909933,"profndraising":2974136,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":128999014,"nonpfrea":"7","gftgrntsrcvd170":11051029742,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":140784720,"grsrcptsrelated170":349316534,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201606,"tax_prd_yr":2016,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F363673599_201606_990_2017080714619115.pdf","updated":"2018-12-10T23:11:40.486Z","totrevenue":2437618536,"totfuncexpns":2423837553,"totassetsend":111828311,"totliabend":16061646,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":2375635807,"totprgmrevnue":24070602,"invstmntinc":511301,"txexmptbndsproceeds":0,"royaltsinc":35209467,"grsrntsreal":157754,"grsrntsprsnl":0,"rntlexpnsreal":204255,"rntlexpnsprsnl":0,"rntlincreal":-46501,"rntlincprsnl":0,"netrntlinc":-46501,"grsalesecur":134343,"grsalesothr":0,"cstbasisecur":318579,"cstbasisothr":0,"gnlsecur":-184236,"gnlsothr":0,"netgnls":-184236,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":44261941,"lesscstofgoods":43720747,"netincsales":541194,"miscrevtot11e":1880902,"compnsatncurrofcr":3339573,"othrsalwages":20996336,"payrolltx":1764075,"profndraising":2483495,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":95766665,"nonpfrea":"7","gftgrntsrcvd170":9907561941,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":120616060,"grsrcptsrelated170":343588635,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201506,"tax_prd_yr":2015,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2016_02_EO%2F36-3673599_990_201506.pdf","updated":"2017-06-30T00:19:27.515Z","totrevenue":2200852165,"totfuncexpns":2184632163,"totassetsend":109025819,"totliabend":26879369,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":2149634703,"totprgmrevnue":21540597,"invstmntinc":496098,"txexmptbndsproceeds":0,"royaltsinc":27004292,"grsrntsreal":179754,"grsrntsprsnl":0,"rntlexpnsreal":203108,"rntlexpnsprsnl":0,"rntlincreal":-23354,"rntlincprsnl":0,"netrntlinc":-23354,"grsalesecur":1288120,"grsalesothr":0,"cstbasisecur":777839,"cstbasisothr":0,"gnlsecur":510281,"gnlsothr":0,"netgnls":510281,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":43958840,"lesscstofgoods":43393415,"netincsales":565425,"miscrevtot11e":1124123,"compnsatncurrofcr":3328940,"othrsalwages":19495923,"payrolltx":1560203,"profndraising":2773110,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":82146450,"nonpfrea":"7","gftgrntsrcvd170":8676461880,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":103528156,"grsrcptsrelated170":109626242,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201406,"tax_prd_yr":2014,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2015_01_EO%2F36-3673599_990_201406.pdf","updated":"2017-06-30T00:19:28.568Z","totrevenue":2060362627,"totfuncexpns":2041987389,"totassetsend":86540942,"totliabend":19684709,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":2016270036,"totprgmrevnue":19308483,"invstmntinc":396403,"txexmptbndsproceeds":0,"royaltsinc":20557450,"grsrntsreal":168883,"grsrntsprsnl":0,"rntlexpnsreal":191963,"rntlexpnsprsnl":0,"rntlincreal":-23080,"rntlincprsnl":0,"netrntlinc":-23080,"grsalesecur":22967233,"grsalesothr":0,"cstbasisecur":20452388,"cstbasisothr":0,"gnlsecur":2514845,"gnlsothr":0,"netgnls":2514845,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":47158127,"lesscstofgoods":46881057,"netincsales":277070,"miscrevtot11e":1061420,"compnsatncurrofcr":3282418,"othrsalwages":17295084,"payrolltx":1411078,"profndraising":3275973,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":562500,"retainedearnend":0,"totnetassetend":66856233,"nonpfrea":"7","gftgrntsrcvd170":7193838364,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":89018773,"grsrcptsrelated170":103356458,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201306,"tax_prd_yr":2013,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_01_EO%2F36-3673599_990_201306.pdf","updated":"2017-06-29T23:53:00.673Z","totrevenue":1893358627,"totfuncexpns":1886998720,"totassetsend":71964420,"totliabend":22759130,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1855398787,"totprgmrevnue":18964585,"invstmntinc":376537,"txexmptbndsproceeds":0,"royaltsinc":16417505,"grsrntsreal":49114,"grsrntsprsnl":0,"rntlexpnsreal":61373,"rntlexpnsprsnl":0,"rntlincreal":-12259,"rntlincprsnl":0,"netrntlinc":-12259,"grsalesecur":10819000,"grsalesothr":187427,"cstbasisecur":10862628,"cstbasisothr":192427,"gnlsecur":-43628,"gnlsothr":-5000,"netgnls":-48628,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":51043799,"lesscstofgoods":51001425,"netincsales":42374,"miscrevtot11e":2219726,"compnsatncurrofcr":2837929,"othrsalwages":17232872,"payrolltx":1453039,"profndraising":3352444,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":1125000,"retainedearnend":0,"totnetassetend":49205290,"nonpfrea":"7","gftgrntsrcvd170":5766025980,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":73147981,"grsrcptsrelated170":98128303,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599},{"tax_prd":201206,"tax_prd_yr":2012,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_12_EO%2F36-3673599_990_201206.pdf","updated":"2017-06-29T23:37:20.745Z","totrevenue":1554156485,"totfuncexpns":1559486335,"totassetsend":62576375,"totliabend":19809724,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1510622608,"totprgmrevnue":24312736,"invstmntinc":381226,"txexmptbndsproceeds":0,"royaltsinc":18710276,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":49943000,"grsalesothr":26546,"cstbasisecur":50348911,"cstbasisothr":60016,"gnlsecur":-405911,"gnlsothr":-33470,"netgnls":-439381,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":42159022,"lesscstofgoods":42113734,"netincsales":45288,"miscrevtot11e":523732,"compnsatncurrofcr":2518968,"othrsalwages":16998032,"payrolltx":1452637,"profndraising":3112713,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":1625000,"retainedearnend":0,"totnetassetend":42766651,"nonpfrea":"7","gftgrntsrcvd170":4555231356,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":57878146,"grsrcptsrelated170":88448957,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":363673599}],"filings_without_data":[{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F363673599_202406_990_2025051223426337.pdf"},{"tax_prd":201106,"tax_prd_yr":2011,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_01_EO%2F36-3673599_990_201106.pdf"},{"tax_prd":201006,"tax_prd_yr":2010,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2010_12_EO%2F36-3673599_990_201006.pdf"},{"tax_prd":200906,"tax_prd_yr":2009,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2010_03_EO%2F36-3673599_990_200906.pdf"},{"tax_prd":200806,"tax_prd_yr":2008,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_12_EO%2F36-3673599_990_200806.pdf"},{"tax_prd":200706,"tax_prd_yr":2007,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2007_12_EO%2F36-3673599_990_200706.pdf"},{"tax_prd":200606,"tax_prd_yr":2006,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_12_EO%2F36-3673599_990_200606.pdf"},{"tax_prd":200506,"tax_prd_yr":2005,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2005_12_EO%2F36-3673599_990_200506.pdf"},{"tax_prd":200406,"tax_prd_yr":2004,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2004_12_EO%2F36-3673599_990_200406.pdf"},{"tax_prd":200306,"tax_prd_yr":2003,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2003_12_EO%2F36-3673599_990_200306.pdf"},{"tax_prd":200206,"tax_prd_yr":2002,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2002_12_EO%2F36-3673599_990_200206.pdf"}],"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```


## Package checked and excluded

- None: no result in any section was set aside as a near match for this job.

## Package sources

- S1: https://projects.propublica.org/nonprofits/api/v2/search.json?q=Feeding+America, retrieved 2026-10-23T21:56:10Z; replayed from the transcript printed in tools/examples/nonprofit-pack.md (lines 202 to 226; SHA-256 376552cfde9efe37194cad863a0e754ed6e5bbd89f42df609900dbf2658dfebc).
- S2: https://projects.propublica.org/nonprofits/api/v2/organizations/363673599.json, retrieved 2026-10-23T21:56:10Z; replayed from the transcript printed in tools/examples/nonprofit-pack.md (lines 318 to 342; SHA-256 91a8fd99798cf725087a1a3dcaa7aa1ab746bbe87ecf38a0180abbc3e0bc72de).
