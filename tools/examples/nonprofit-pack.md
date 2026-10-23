# Nonprofit diligence pack: demo pack: live run 2026-10-23 by H5 for issue #149

Scope: the ProPublica Nonprofit Explorer API v2 as returned at the stated times; figures are the API's extracted Form 990 values as shown, not an audit, and not a full reading of any filing. Each summary row is traceable to the section numbered in its last column; every figure in the table appears in that section with its source link and the raw excerpt beneath it.

## Summary

| # | Entity (as listed) | Status | Filings with extracted figures | Filing tax period | Total revenue | Section |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | American National Red Cross | Found | 13 | `202306` | `3217077611` | 1 |
| 2 | Feeding America | Found | 12 | `202306` | `4916912461` | 2 |
| 3 | World Wildlife Fund Inc | Found | 13 | `202306` | `372835343` | 3 |
| 4 | Goodwill Industries International Inc | Found | 13 | `202312` | `70964985` | 4 |
| 5 | United States Fund for UNICEF | Found | 12 | `202306` | `829050932` | 5 |
| 6 | Zxqv Memorial Pancake Foundation | Not found | n/a | n/a | n/a | 6 |

## Section 1: American National Red Cross

### Search: "American National Red Cross"

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/search.json?q=American+National+Red+Cross
Retrieved (UTC): 2026-10-23T21:56:08Z
HTTP status: HTTP/1.1 200 OK

total_results as shown: 1. Organizations on this page: 1. num_pages as shown: 1.

- Result `530196605`: strein `"53-0196605"`, name `"American National Red Cross"`, city `"Washington"`, state `"DC"`. Status: examined below.

Source: <https://projects.propublica.org/nonprofits/api/v2/search.json?q=American+National+Red+Cross>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:10 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=_wTQ3vu9N86NypF03jXPp0woLnjS8mdufS9NDqA9GpY-1792792570.5469244-1.0.1.1-DlhEctfYcbdLh7uCXDItflb_KqcYwbSbYWnh1l.pmAQ; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd7de806c991-IAD
CF-Cache-Status: HIT
Age: 77308
Cache-Control: public, max-age=86400
ETag: W/"1f8fbd50a40cb4b51f521789568e67c2"
Expires: Sat, 24 Oct 2026 21:56:10 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: 13b4d17f-6b93-4f6d-9098-dff8af3f9f2f
x-runtime: 0.046513
Transfer-Encoding: chunked

{"total_results":1,"organizations":[{"ein":530196605,"strein":"53-0196605","name":"American National Red Cross","sub_name":"American National Red Cross Shared Services Center","city":"Washington","state":"DC","ntee_code":"P210","raw_ntee_code":"P210","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":125.509705}],"num_pages":1,"cur_page":0,"page_offset":0,"per_page":25,"search_query":"American National Red Cross","selected_state":null,"selected_ntee":null,"selected_code":null,"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

### Organization: EIN 530196605

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json
Retrieved (UTC): 2026-10-23T21:56:09Z
HTTP status: HTTP/1.1 200 OK

Identity, from the organization block:

- Legal name (name) as shown: `"American National Red Cross"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"name":"American National Red Cross"
```

- EIN (ein) as shown: `530196605`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"ein":530196605
```

- City (city) as shown: `"Washington"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"city":"Washington"
```

- State (state) as shown: `"DC"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"state":"DC"
```

Figures, from the filings_with_data entry with the highest tax_prd (202306 of 13 entries). The response states no unit; values are as shown.

- Tax period of the filing (tax_prd) as shown: `202306`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"tax_prd":202306
```

- Total revenue (totrevenue) as shown: `3217077611`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"totrevenue":3217077611
```

- Total functional expenses (totfuncexpns) as shown: `2971106889`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"totfuncexpns":2971106889
```

- Total assets, end of year (totassetsend) as shown: `4028321133`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"totassetsend":4028321133
```

- Total liabilities, end of year (totliabend) as shown: `1008326202`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"totliabend":1008326202
```

- A later filing is listed without extracted figures (filings_without_data), tax_prd as shown: `202406`. No figure above comes from it.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196605_202406_990_2025051223427881.pdf"}
```

- Organization record tax_period as shown: `"2025-06-01"`. This is the organization block's field, not the period of the figures above.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>

```
"tax_period":"2025-06-01"
```

Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196605.json>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:11 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=49KB58q4zNm5xrML58Lq2pFLoP2N.dVkgGUpqle.72k-1792792571.2681847-1.0.1.1-XoZZ.UuefUHYqPMQoBGUEtsCXJDnU_4NcyGzTlS8Gyw; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd826e451e1d-LAX
CF-Cache-Status: HIT
Age: 82196
Cache-Control: public, max-age=86400
ETag: W/"fdd12add3719fb29924c7b8c5c444f2f"
Expires: Sat, 24 Oct 2026 21:56:11 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: fb393f15-c58e-42d4-8a2c-44953fec35d0
x-runtime: 0.100560
Transfer-Encoding: chunked

{"organization":{"id":530196605,"ein":530196605,"name":"American National Red Cross","careofname":null,"address":"431 18TH ST NW","city":"Washington","state":"DC","zipcode":"20006-5310","exemption_number":0,"subsection_code":3,"affiliation_code":1,"classification_codes":"1000","ruling_date":"1938-12-01","deductibility_code":1,"foundation_code":15,"activity_codes":"902561000","organization_code":1,"exempt_organization_status_code":1,"tax_period":"2025-06-01","asset_code":9,"income_code":9,"filing_requirement_code":1,"pf_filing_requirement_code":0,"accounting_period":6,"asset_amount":5052941623,"income_amount":4608946426,"revenue_amount":3916983933,"ntee_code":"P210","sort_name":"Shared Services Center","created_at":"2023-05-09T20:32:12.933Z","updated_at":"2026-10-21T13:28:56.771Z","data_source":"current_2026_10_21","have_extracts":null,"have_pdfs":null,"latest_object_id":"202640829349300109"},"filings_with_data":[{"tax_prd":202306,"tax_prd_yr":2023,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=download990pdf_03_2024_prefixes_41-54%2F530196605_202306_990_2024031222316430.pdf","updated":"2025-08-05T16:09:45.876Z","totrevenue":3217077611,"totfuncexpns":2971106889,"totassetsend":4028321133,"totliabend":1008326202,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":919126379,"totprgmrevnue":2167924872,"invstmntinc":76827242,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":25402149,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":25402149,"rntlincprsnl":0,"netrntlinc":25402149,"grsalesecur":454390210,"grsalesothr":8620495,"cstbasisecur":454391512,"cstbasisothr":3228276,"gnlsecur":-1302,"gnlsothr":5392219,"netgnls":5390917,"grsincfndrsng":3103039,"lessdirfndrsng":3952668,"netincfndrsng":-849629,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":23255681,"compnsatncurrofcr":5947262,"othrsalwages":1182370329,"payrolltx":87718348,"profndraising":452216,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":512708726,"retainedearnend":0,"totnetassetend":3019994931,"nonpfrea":"7","gftgrntsrcvd170":4647251966,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":412696711,"grsrcptsrelated170":9996765269,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":202206,"tax_prd_yr":2022,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196605_202206_990_2023060221351871.pdf","updated":"2024-08-28T20:14:04.511Z","totrevenue":3182229338,"totfuncexpns":3048182336,"totassetsend":3872181875,"totliabend":1171891777,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1060031161,"totprgmrevnue":2018755758,"invstmntinc":48466117,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":25283390,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":25283390,"rntlincprsnl":0,"netrntlinc":25283390,"grsalesecur":412321405,"grsalesothr":27930409,"cstbasisecur":412082119,"cstbasisothr":16367240,"gnlsecur":239286,"gnlsothr":11563169,"netgnls":11802455,"grsincfndrsng":2175535,"lessdirfndrsng":2648079,"netincfndrsng":-472544,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":18363001,"compnsatncurrofcr":5758532,"othrsalwages":1119398026,"payrolltx":82099097,"profndraising":301063,"txexmptbndsend":0,"secrdmrtgsend":334041,"unsecurednotesend":517315807,"retainedearnend":0,"totnetassetend":2700290098,"nonpfrea":"7","gftgrntsrcvd170":5236602885,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":481689172,"grsrcptsrelated170":9678763883,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":202106,"tax_prd_yr":2021,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196605_202106_990_2022030219681333.pdf","updated":"2023-08-07T19:42:52.665Z","totrevenue":3090183560,"totfuncexpns":2796025309,"totassetsend":3668499985,"totliabend":1300112674,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":962942913,"totprgmrevnue":1999617756,"invstmntinc":63790894,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":25607891,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":25607891,"rntlincprsnl":0,"netrntlinc":25607891,"grsalesecur":16666627,"grsalesothr":17172347,"cstbasisecur":16533951,"cstbasisothr":8081092,"gnlsecur":132676,"gnlsothr":9091255,"netgnls":9223931,"grsincfndrsng":3241475,"lessdirfndrsng":997549,"netincfndrsng":2243926,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":26756249,"compnsatncurrofcr":5750681,"othrsalwages":1071857732,"payrolltx":81193947,"profndraising":216781,"txexmptbndsend":0,"secrdmrtgsend":3489207,"unsecurednotesend":534284657,"retainedearnend":0,"totnetassetend":2368387311,"nonpfrea":"07","gftgrntsrcvd170":4876612165,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":466300787,"grsrcptsrelated170":9508095160,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":202006,"tax_prd_yr":2020,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=04_2021_prefixes_52-54%2F530196605_202006_990_2021042117979664.pdf","updated":"2022-07-01T20:34:48.242Z","totrevenue":2839409246,"totfuncexpns":2683608516,"totassetsend":3266899381,"totliabend":1454684272,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":887785755,"totprgmrevnue":1840018144,"invstmntinc":44576430,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":25128547,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":25128547,"rntlincprsnl":0,"netrntlinc":25128547,"grsalesecur":134495269,"grsalesothr":22956765,"cstbasisecur":134520242,"cstbasisothr":12125970,"gnlsecur":-24973,"gnlsothr":10830795,"netgnls":10805822,"grsincfndrsng":2092433,"lessdirfndrsng":3134950,"netincfndrsng":-1042517,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":32137065,"compnsatncurrofcr":5988644,"othrsalwages":1099816849,"payrolltx":79456419,"profndraising":123953,"txexmptbndsend":47390000,"secrdmrtgsend":7906901,"unsecurednotesend":708884329,"retainedearnend":0,"totnetassetend":1812215109,"nonpfrea":"7","gftgrntsrcvd170":4551531907,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":443952672,"grsrcptsrelated170":9369518463,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201906,"tax_prd_yr":2019,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=02_2020_prefixes_52-56%2F530196605_201906_990_2020020717122251.pdf","updated":"2021-08-30T18:32:09.297Z","totrevenue":2813454935,"totfuncexpns":2937181875,"totassetsend":3049904049,"totliabend":1607739689,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":817365759,"totprgmrevnue":1883680966,"invstmntinc":51987786,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":25348337,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":25348337,"rntlincprsnl":0,"netrntlinc":25348337,"grsalesecur":786293166,"grsalesothr":30576116,"cstbasisecur":785046388,"cstbasisothr":17921265,"gnlsecur":1246778,"gnlsothr":12654851,"netgnls":13901629,"grsincfndrsng":4572337,"lessdirfndrsng":5746343,"netincfndrsng":-1174006,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":22344464,"compnsatncurrofcr":5593870,"othrsalwages":1096208468,"payrolltx":82728493,"profndraising":247242,"txexmptbndsend":51125000,"secrdmrtgsend":13076106,"unsecurednotesend":517100000,"retainedearnend":0,"totnetassetend":1442164360,"nonpfrea":"07","gftgrntsrcvd170":4323781812,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":438284950,"grsrcptsrelated170":9446704471,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201806,"tax_prd_yr":2018,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=02_2019_prefixes_52-54%2F530196605_201806_990_2019021416097064.pdf","updated":"2019-10-15T18:36:18.369Z","totrevenue":3608002096,"totfuncexpns":3142984060,"totassetsend":3240247122,"totliabend":1658095198,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1508477297,"totprgmrevnue":1849335300,"invstmntinc":149002623,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":22116216,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":22116216,"rntlincprsnl":0,"netrntlinc":22116216,"grsalesecur":338536220,"grsalesothr":51604889,"cstbasisecur":295753786,"cstbasisothr":38070815,"gnlsecur":42782434,"gnlsothr":13534074,"netgnls":56316508,"grsincfndrsng":4936178,"lessdirfndrsng":6550286,"netincfndrsng":-1614108,"grsincgaming":17050,"lessdirgaming":4527,"netincgaming":12523,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":24355737,"compnsatncurrofcr":6327939,"othrsalwages":1115029599,"payrolltx":83397683,"profndraising":413231,"txexmptbndsend":54760000,"secrdmrtgsend":4851848,"unsecurednotesend":552100000,"retainedearnend":0,"totnetassetend":1582151924,"nonpfrea":"7","gftgrntsrcvd170":4294642251,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":406602431,"grsrcptsrelated170":9717183551,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201706,"tax_prd_yr":2017,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=01_2018_prefixes_52-54%2F530196605_201706_990_2018011115111678.pdf","updated":"2018-12-10T23:07:31.595Z","totrevenue":2676037116,"totfuncexpns":2808630913,"totassetsend":3142581145,"totliabend":1946658460,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":700040441,"totprgmrevnue":1845547694,"invstmntinc":39175422,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":19778268,"grsrntsprsnl":0,"rntlexpnsreal":28966,"rntlexpnsprsnl":0,"rntlincreal":19749302,"rntlincprsnl":0,"netrntlinc":19749302,"grsalesecur":336940991,"grsalesothr":104641837,"cstbasisecur":336158838,"cstbasisothr":44816926,"gnlsecur":782153,"gnlsothr":59824911,"netgnls":60607064,"grsincfndrsng":5328866,"lessdirfndrsng":8208836,"netincfndrsng":-2879970,"grsincgaming":43377,"lessdirgaming":47784,"netincgaming":-4407,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":13801570,"compnsatncurrofcr":4965695,"othrsalwages":1086796068,"payrolltx":83783311,"profndraising":0,"txexmptbndsend":57395000,"secrdmrtgsend":7020,"unsecurednotesend":588209408,"retainedearnend":0,"totnetassetend":1195922685,"nonpfrea":"7","gftgrntsrcvd170":3919577964,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":280419574,"grsrcptsrelated170":10139869896,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201606,"tax_prd_yr":2016,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196605_201606_990_2017091514741563.pdf","updated":"2018-12-10T23:10:29.110Z","totrevenue":2618203252,"totfuncexpns":2679603949,"totassetsend":3235806694,"totliabend":2250133837,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":637862655,"totprgmrevnue":1878941932,"invstmntinc":46101344,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":20737699,"grsrntsprsnl":0,"rntlexpnsreal":31218,"rntlexpnsprsnl":0,"rntlincreal":20706481,"rntlincprsnl":0,"netrntlinc":20706482,"grsalesecur":510658346,"grsalesothr":27598121,"cstbasisecur":471419464,"cstbasisothr":30789121,"gnlsecur":39238882,"gnlsothr":-3191000,"netgnls":36047882,"grsincfndrsng":4779128,"lessdirfndrsng":7955099,"netincfndrsng":-3175971,"grsincgaming":72902,"lessdirgaming":41290,"netincgaming":31612,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":1687316,"compnsatncurrofcr":5108275,"othrsalwages":1112886481,"payrolltx":86664211,"profndraising":0,"txexmptbndsend":89242600,"secrdmrtgsend":7498,"unsecurednotesend":513699498,"retainedearnend":0,"totnetassetend":985672857,"nonpfrea":"7","gftgrntsrcvd170":3960728260,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":268012448,"grsrcptsrelated170":10604963672,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201506,"tax_prd_yr":2015,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2016_07_EO%2F53-0196605_990_201506.pdf","updated":"2017-06-30T00:37:49.920Z","totrevenue":2726672619,"totfuncexpns":2886003368,"totassetsend":3486142571,"totliabend":1892332242,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":660035659,"totprgmrevnue":1925059348,"invstmntinc":45381546,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":18655709,"grsrntsprsnl":0,"rntlexpnsreal":3919187,"rntlexpnsprsnl":0,"rntlincreal":14736522,"rntlincprsnl":0,"netrntlinc":14736522,"grsalesecur":367570725,"grsalesothr":2435393,"cstbasisecur":305393503,"cstbasisothr":1589442,"gnlsecur":62177222,"gnlsothr":845951,"netgnls":63023173,"grsincfndrsng":11396876,"lessdirfndrsng":8600196,"netincfndrsng":2796680,"grsincgaming":86551,"lessdirgaming":37164,"netincgaming":49387,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":15590304,"compnsatncurrofcr":4715289,"othrsalwages":1173075473,"payrolltx":101478465,"profndraising":0,"txexmptbndsend":120571350,"secrdmrtgsend":7943,"unsecurednotesend":524401996,"retainedearnend":0,"totnetassetend":1593810329,"nonpfrea":"7","gftgrntsrcvd170":4336738725,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":250818892,"grsrcptsrelated170":11074464478,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201406,"tax_prd_yr":2014,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2015_03_EO%2F53-0196605_990_201406.pdf","updated":"2017-06-30T00:19:22.372Z","totrevenue":2974133836,"totfuncexpns":3047227207,"totassetsend":3791643231,"totliabend":1830884753,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":788226198,"totprgmrevnue":2019244653,"invstmntinc":45653603,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":18744666,"grsrntsprsnl":0,"rntlexpnsreal":6544973,"rntlexpnsprsnl":0,"rntlincreal":12199693,"rntlincprsnl":0,"netrntlinc":12199693,"grsalesecur":275573412,"grsalesothr":17109724,"cstbasisecur":235389169,"cstbasisothr":10426804,"gnlsecur":40184243,"gnlsothr":6682920,"netgnls":46867163,"grsincfndrsng":9392554,"lessdirfndrsng":9088133,"netincfndrsng":304421,"grsincgaming":297969,"lessdirgaming":230835,"netincgaming":67134,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":61570971,"compnsatncurrofcr":4835529,"othrsalwages":1258269459,"payrolltx":101183661,"profndraising":0,"txexmptbndsend":212890782,"secrdmrtgsend":101811,"unsecurednotesend":532760781,"retainedearnend":0,"totnetassetend":1960758478,"nonpfrea":"7","gftgrntsrcvd170":4814837648,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":253076527,"grsrcptsrelated170":11795625185,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201306,"tax_prd_yr":2013,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_03_EO%2F53-0196605_990_201306.pdf","updated":"2017-06-30T00:05:45.017Z","totrevenue":3412238741,"totfuncexpns":3356880480,"totassetsend":3898835153,"totliabend":1908777901,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1133413010,"totprgmrevnue":2162884552,"invstmntinc":44935982,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":16745624,"grsrntsprsnl":0,"rntlexpnsreal":6290621,"rntlexpnsprsnl":0,"rntlincreal":10455003,"rntlincprsnl":0,"netrntlinc":10455003,"grsalesecur":302296016,"grsalesothr":13133120,"cstbasisecur":298535556,"cstbasisothr":8168344,"gnlsecur":3760460,"gnlsothr":4964776,"netgnls":8725236,"grsincfndrsng":9287437,"lessdirfndrsng":9726292,"netincfndrsng":-438855,"grsincgaming":820246,"lessdirgaming":660389,"netincgaming":159857,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":52103956,"compnsatncurrofcr":4602313,"othrsalwages":1324855754,"payrolltx":75800096,"profndraising":0,"txexmptbndsend":220597760,"secrdmrtgsend":191000,"unsecurednotesend":493202240,"retainedearnend":0,"totnetassetend":1990057252,"nonpfrea":"7","gftgrntsrcvd170":4742522673,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":271511447,"grsrcptsrelated170":11747515934,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201206,"tax_prd_yr":2012,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2013_03_EO%2F53-0196605_990_201206.pdf","updated":"2017-06-29T23:50:41.899Z","totrevenue":3154538043,"totfuncexpns":3329153707,"totassetsend":3777960071,"totliabend":2182737621,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":741190737,"totprgmrevnue":2290746478,"invstmntinc":46546564,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":16887550,"grsrntsprsnl":0,"rntlexpnsreal":5592036,"rntlexpnsprsnl":0,"rntlincreal":11295514,"rntlincprsnl":0,"netrntlinc":11295514,"grsalesecur":281058000,"grsalesothr":4463883,"cstbasisecur":269504077,"cstbasisothr":3527014,"gnlsecur":11553923,"gnlsothr":936869,"netgnls":12490792,"grsincfndrsng":11491685,"lessdirfndrsng":10471012,"netincfndrsng":1020673,"grsincgaming":572357,"lessdirgaming":494100,"netincgaming":78257,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":51169028,"compnsatncurrofcr":4647035,"othrsalwages":1318857177,"payrolltx":90333500,"profndraising":0,"txexmptbndsend":228736115,"secrdmrtgsend":274501,"unsecurednotesend":324347384,"retainedearnend":0,"totnetassetend":1595222450,"nonpfrea":"7","gftgrntsrcvd170":4336366349,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":315113708,"grsrcptsrelated170":11985150770,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605},{"tax_prd":201106,"tax_prd_yr":2011,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_03_EO%2F53-0196605_990_201106.pdf","updated":"2017-06-29T23:37:24.001Z","totrevenue":3452960387,"totfuncexpns":3422010386,"totassetsend":4253578616,"totliabend":2061654331,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1013873120,"totprgmrevnue":2328884915,"invstmntinc":49645488,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":16407139,"grsrntsprsnl":0,"rntlexpnsreal":5168882,"rntlexpnsprsnl":0,"rntlincreal":11238257,"rntlincprsnl":0,"netrntlinc":11238257,"grsalesecur":222948000,"grsalesothr":6406605,"cstbasisecur":223009049,"cstbasisothr":3707549,"gnlsecur":-61049,"gnlsothr":2699056,"netgnls":2638007,"grsincfndrsng":13879944,"lessdirfndrsng":13316334,"netincfndrsng":563610,"grsincgaming":1723385,"lessdirgaming":1503270,"netincgaming":220115,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":45896875,"compnsatncurrofcr":4480899,"othrsalwages":1344063923,"payrolltx":88614938,"profndraising":0,"txexmptbndsend":234405758,"secrdmrtgsend":561246,"unsecurednotesend":338414326,"retainedearnend":0,"totnetassetend":2191924285,"nonpfrea":"7","gftgrntsrcvd170":4248857254,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":381262012,"grsrcptsrelated170":12004505722,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196605}],"filings_without_data":[{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196605_202406_990_2025051223427881.pdf"},{"tax_prd":201006,"tax_prd_yr":2010,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_03_EO%2F53-0196605_990_201006.pdf"},{"tax_prd":200906,"tax_prd_yr":2009,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2010_05_EO%2F53-0196605_990_200906.pdf"},{"tax_prd":200806,"tax_prd_yr":2008,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2009_03_EO%2F53-0196605_990_200806.pdf"},{"tax_prd":200706,"tax_prd_yr":2007,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_11_EO%2F53-0196605_990_200706.pdf"},{"tax_prd":200606,"tax_prd_yr":2006,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_01_EO%2F53-0196605_990_200606.pdf"},{"tax_prd":200506,"tax_prd_yr":2005,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_04_EO%2F53-0196605_990_200506.pdf"},{"tax_prd":200406,"tax_prd_yr":2004,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_07_EO%2F53-0196605_990_200406.pdf"},{"tax_prd":200306,"tax_prd_yr":2003,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_06_EO%2F53-0196605_990_200306.pdf"},{"tax_prd":200206,"tax_prd_yr":2002,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2003_02_EO%2F53-0196605_990_200206.pdf"},{"tax_prd":200106,"tax_prd_yr":2001,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2002_03_EO%2F53-0196605_990_200106.pdf"}],"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

## Section 2: Feeding America

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

## Section 3: World Wildlife Fund Inc

### Search: "World Wildlife Fund Inc"

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/search.json?q=World+Wildlife+Fund+Inc
Retrieved (UTC): 2026-10-23T21:56:11Z
HTTP status: HTTP/1.1 200 OK

total_results as shown: 1. Organizations on this page: 1. num_pages as shown: 1.

- Result `521693387`: strein `"52-1693387"`, name `"World Wildlife Fund Inc"`, city `"Washington"`, state `"DC"`. Status: examined below.

Source: <https://projects.propublica.org/nonprofits/api/v2/search.json?q=World+Wildlife+Fund+Inc>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:13 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=3D49yniWQGMeDqi1IPo6Fs2aXTK1ISS74WjqDYyVLRI-1792792573.4811862-1.0.1.1-1m7xCYESArTFFXm.l9tCwIgtrf5hTNmoX3g9V0rrNC4; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd903a8abd62-ATL
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
ETag: W/"224a1f49acdc1500ed2c7f74dcaee25b"
Expires: Sat, 24 Oct 2026 21:56:13 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: d27c0264-66cf-46c8-8124-c0289aa26310
x-runtime: 0.052142
Transfer-Encoding: chunked

{"total_results":1,"organizations":[{"ein":521693387,"strein":"52-1693387","name":"World Wildlife Fund Inc","sub_name":"World Wildlife Fund Inc","city":"Washington","state":"DC","ntee_code":"C30","raw_ntee_code":"C30","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":112.67401}],"num_pages":1,"cur_page":0,"page_offset":0,"per_page":25,"search_query":"World Wildlife Fund Inc","selected_state":null,"selected_ntee":null,"selected_code":null,"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

### Organization: EIN 521693387

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json
Retrieved (UTC): 2026-10-23T21:56:12Z
HTTP status: HTTP/1.1 200 OK

Identity, from the organization block:

- Legal name (name) as shown: `"World Wildlife Fund Inc"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"name":"World Wildlife Fund Inc"
```

- EIN (ein) as shown: `521693387`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"ein":521693387
```

- City (city) as shown: `"Washington"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"city":"Washington"
```

- State (state) as shown: `"DC"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"state":"DC"
```

Figures, from the filings_with_data entry with the highest tax_prd (202306 of 13 entries). The response states no unit; values are as shown.

- Tax period of the filing (tax_prd) as shown: `202306`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"tax_prd":202306
```

- Total revenue (totrevenue) as shown: `372835343`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"totrevenue":372835343
```

- Total functional expenses (totfuncexpns) as shown: `352906681`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"totfuncexpns":352906681
```

- Total assets, end of year (totassetsend) as shown: `755426255`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"totassetsend":755426255
```

- Total liabilities, end of year (totliabend) as shown: `132347272`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"totliabend":132347272
```

- A later filing is listed without extracted figures (filings_without_data), tax_prd as shown: `202406`. No figure above comes from it.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F521693387_202406_990_2025050123418710.pdf"}
```

- Organization record tax_period as shown: `"2025-06-01"`. This is the organization block's field, not the period of the figures above.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>

```
"tax_period":"2025-06-01"
```

Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/521693387.json>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:14 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=h6QMoCWIPSewNiFQX5EC9QlTQg60D8vpFe2UO6MnfHU-1792792573.972704-1.0.1.1-wOAY9hr4az_0ERRztSmYZTBTeMN1yMaaeCJH8pdCOko; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd935a644e35-SJC
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
ETag: W/"c49bf96a6f3e8846ee394833dc6dcc1b"
Expires: Sat, 24 Oct 2026 21:56:14 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: dfe1371f-470b-4617-b675-5e5a53dec0b1
x-runtime: 0.224521
Transfer-Encoding: chunked

{"organization":{"id":521693387,"ein":521693387,"name":"World Wildlife Fund Inc","careofname":"% MIKE PEJCIC","address":"1250 24TH ST NW","city":"Washington","state":"DC","zipcode":"20037-1124","exemption_number":0,"subsection_code":3,"affiliation_code":3,"classification_codes":"1000","ruling_date":"1991-08-01","deductibility_code":1,"foundation_code":15,"activity_codes":"350000000","organization_code":1,"exempt_organization_status_code":1,"tax_period":"2025-06-01","asset_code":9,"income_code":9,"filing_requirement_code":1,"pf_filing_requirement_code":0,"accounting_period":6,"asset_amount":777252801,"income_amount":553088917,"revenue_amount":366655209,"ntee_code":"C30","sort_name":null,"created_at":"2023-05-09T20:32:04.445Z","updated_at":"2026-10-21T13:28:55.288Z","data_source":"current_2026_10_21","have_extracts":null,"have_pdfs":null,"latest_object_id":"202641079349300209"},"filings_with_data":[{"tax_prd":202306,"tax_prd_yr":2023,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F521693387_202306_990_2024040522347217.pdf","updated":"2025-08-05T16:09:43.653Z","totrevenue":372835343,"totfuncexpns":352906681,"totassetsend":755426255,"totliabend":132347272,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":355202055,"totprgmrevnue":3875631,"invstmntinc":10665221,"txexmptbndsproceeds":0,"royaltsinc":5448690,"grsrntsreal":3132664,"grsrntsprsnl":0,"rntlexpnsreal":4820908,"rntlexpnsprsnl":0,"rntlincreal":-1688244,"rntlincprsnl":0,"netrntlinc":-1688244,"grsalesecur":113977308,"grsalesothr":0,"cstbasisecur":114970258,"cstbasisothr":0,"gnlsecur":-992950,"gnlsothr":0,"netgnls":-992950,"grsincfndrsng":22585,"lessdirfndrsng":8521,"netincfndrsng":14064,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":310876,"compnsatncurrofcr":5005762,"othrsalwages":91441552,"payrolltx":5933202,"profndraising":2217504,"txexmptbndsend":0,"secrdmrtgsend":40099050,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":623078983,"nonpfrea":"7","gftgrntsrcvd170":1602645027,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":78293480,"grsrcptsrelated170":5850262,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":202206,"tax_prd_yr":2022,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=download990pdf_06_2023_prefixes_52-58%2F521693387_202206_990_2023060121342438.pdf","updated":"2024-08-28T20:13:54.613Z","totrevenue":381636162,"totfuncexpns":316378290,"totassetsend":704447333,"totliabend":131197167,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":353794252,"totprgmrevnue":3864228,"invstmntinc":5938191,"txexmptbndsproceeds":0,"royaltsinc":6116178,"grsrntsreal":2048487,"grsrntsprsnl":0,"rntlexpnsreal":4969536,"rntlexpnsprsnl":0,"rntlincreal":-2921049,"rntlincprsnl":0,"netrntlinc":-2921049,"grsalesecur":64381369,"grsalesothr":0,"cstbasisecur":49633532,"cstbasisothr":0,"gnlsecur":14747837,"gnlsothr":0,"netgnls":14747837,"grsincfndrsng":54845,"lessdirfndrsng":23522,"netincfndrsng":31323,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":65202,"compnsatncurrofcr":4750909,"othrsalwages":79615839,"payrolltx":5067729,"profndraising":2676422,"txexmptbndsend":0,"secrdmrtgsend":44892623,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":573250166,"nonpfrea":"7","gftgrntsrcvd170":1490148699,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":73833234,"grsrcptsrelated170":3128194,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":202106,"tax_prd_yr":2021,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F521693387_202106_990_2022031619760559.pdf","updated":"2023-08-07T19:42:42.756Z","totrevenue":408317459,"totfuncexpns":283476575,"totassetsend":698927854,"totliabend":124503195,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":391898333,"totprgmrevnue":76475,"invstmntinc":4996060,"txexmptbndsproceeds":0,"royaltsinc":4263833,"grsrntsreal":2287670,"grsrntsprsnl":0,"rntlexpnsreal":5588827,"rntlexpnsprsnl":0,"rntlincreal":-3301157,"rntlincprsnl":0,"netrntlinc":-3301157,"grsalesecur":65726359,"grsalesothr":0,"cstbasisecur":55573179,"cstbasisothr":0,"gnlsecur":10153180,"gnlsothr":0,"netgnls":10153180,"grsincfndrsng":114183,"lessdirfndrsng":18653,"netincfndrsng":95530,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":135205,"compnsatncurrofcr":4706160,"othrsalwages":71362356,"payrolltx":4873419,"profndraising":2075428,"txexmptbndsend":0,"secrdmrtgsend":44097834,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":574424659,"nonpfrea":"07","gftgrntsrcvd170":1350193366,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":73228578,"grsrcptsrelated170":25415,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":202006,"tax_prd_yr":2020,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=04_2021_prefixes_52-54%2F521693387_202006_990_2021041417944213.pdf","updated":"2022-07-01T20:34:37.480Z","totrevenue":286350088,"totfuncexpns":266981193,"totassetsend":507200384,"totliabend":121175113,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":271337477,"totprgmrevnue":651358,"invstmntinc":4216485,"txexmptbndsproceeds":0,"royaltsinc":6500213,"grsrntsreal":6086875,"grsrntsprsnl":0,"rntlexpnsreal":6515642,"rntlexpnsprsnl":0,"rntlincreal":-428767,"rntlincprsnl":0,"netrntlinc":-428767,"grsalesecur":78546715,"grsalesothr":0,"cstbasisecur":74546087,"cstbasisothr":0,"gnlsecur":4000628,"gnlsothr":0,"netgnls":4000628,"grsincfndrsng":40211,"lessdirfndrsng":126207,"netincfndrsng":-85996,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":158690,"compnsatncurrofcr":3996677,"othrsalwages":71445725,"payrolltx":4455647,"profndraising":2866216,"txexmptbndsend":0,"secrdmrtgsend":46112584,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":386025271,"nonpfrea":"7","gftgrntsrcvd170":1184018844,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":81819817,"grsrcptsrelated170":457825,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201906,"tax_prd_yr":2019,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=09_2020_prefixes_47-52%2F521693387_201906_990_2020091617302975.pdf","updated":"2021-08-30T18:52:38.627Z","totrevenue":249933507,"totfuncexpns":236248679,"totassetsend":508462156,"totliabend":133425481,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":230298727,"totprgmrevnue":794053,"invstmntinc":4195191,"txexmptbndsproceeds":0,"royaltsinc":5418710,"grsrntsreal":6774559,"grsrntsprsnl":0,"rntlexpnsreal":6086097,"rntlexpnsprsnl":0,"rntlincreal":688462,"rntlincprsnl":0,"netrntlinc":688462,"grsalesecur":69136314,"grsalesothr":0,"cstbasisecur":60784522,"cstbasisothr":0,"gnlsecur":8351792,"gnlsothr":0,"netgnls":8351792,"grsincfndrsng":2555,"lessdirfndrsng":222706,"netincfndrsng":-220151,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":406723,"compnsatncurrofcr":4129277,"othrsalwages":66452958,"payrolltx":4130736,"profndraising":2340754,"txexmptbndsend":0,"secrdmrtgsend":49097310,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":375036675,"nonpfrea":"07","gftgrntsrcvd170":1116993974,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":76606206,"grsrcptsrelated170":1335040,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201806,"tax_prd_yr":2018,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=07_2019_prefixes_51-56%2F521693387_201806_990_2019070516465381.pdf","updated":"2021-08-30T18:38:52.812Z","totrevenue":256825626,"totfuncexpns":258037473,"totassetsend":502673998,"totliabend":139602016,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":242705727,"totprgmrevnue":570889,"invstmntinc":2199377,"txexmptbndsproceeds":0,"royaltsinc":6369195,"grsrntsreal":6358169,"grsrntsprsnl":0,"rntlexpnsreal":5918456,"rntlexpnsprsnl":0,"rntlincreal":439713,"rntlincprsnl":0,"netrntlinc":439713,"grsalesecur":63431907,"grsalesothr":0,"cstbasisecur":59088682,"cstbasisothr":0,"gnlsecur":4343225,"gnlsothr":0,"netgnls":4343225,"grsincfndrsng":3380,"lessdirfndrsng":31120,"netincfndrsng":-27740,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":225240,"compnsatncurrofcr":5004897,"othrsalwages":59065635,"payrolltx":3867475,"profndraising":1313301,"txexmptbndsend":0,"secrdmrtgsend":51932974,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":363071982,"nonpfrea":"07","gftgrntsrcvd170":1104177849,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":72284877,"grsrcptsrelated170":1872645,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201706,"tax_prd_yr":2017,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=01_2018_prefixes_52-54%2F521693387_201706_990_2018011015106921.pdf","updated":"2018-12-10T23:07:32.962Z","totrevenue":226396387,"totfuncexpns":247189949,"totassetsend":488571414,"totliabend":140402662,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":213838919,"totprgmrevnue":94033,"invstmntinc":2098753,"txexmptbndsproceeds":0,"royaltsinc":5308848,"grsrntsreal":6056081,"grsrntsprsnl":0,"rntlexpnsreal":6951988,"rntlexpnsprsnl":0,"rntlincreal":-895907,"rntlincprsnl":0,"netrntlinc":-895907,"grsalesecur":52579247,"grsalesothr":0,"cstbasisecur":46829657,"cstbasisothr":0,"gnlsecur":5749590,"gnlsothr":0,"netgnls":5749590,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":202151,"compnsatncurrofcr":4207051,"othrsalwages":57503790,"payrolltx":3651117,"profndraising":1751225,"txexmptbndsend":0,"secrdmrtgsend":55478275,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":348168752,"nonpfrea":"7","gftgrntsrcvd170":1077290033,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":73383118,"grsrcptsrelated170":2239697,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201606,"tax_prd_yr":2016,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2017_01_EO%2F52-1693387_990_201606.pdf","updated":"2017-06-30T00:35:15.932Z","totrevenue":248630952,"totfuncexpns":230955849,"totassetsend":481710624,"totliabend":145153698,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":225837994,"totprgmrevnue":868592,"invstmntinc":2284735,"txexmptbndsproceeds":0,"royaltsinc":11085268,"grsrntsreal":6768799,"grsrntsprsnl":0,"rntlexpnsreal":6235198,"rntlexpnsprsnl":0,"rntlincreal":533601,"rntlincprsnl":0,"netrntlinc":533601,"grsalesecur":76994717,"grsalesothr":757637,"cstbasisecur":69260488,"cstbasisothr":757637,"gnlsecur":7734229,"gnlsothr":0,"netgnls":7734229,"grsincfndrsng":6400,"lessdirfndrsng":53808,"netincfndrsng":-47408,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":333941,"compnsatncurrofcr":3929512,"othrsalwages":54166540,"payrolltx":3423978,"profndraising":756295,"txexmptbndsend":0,"secrdmrtgsend":57681988,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":336556926,"nonpfrea":"7","gftgrntsrcvd170":1058793808,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":75811073,"grsrcptsrelated170":2739255,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201506,"tax_prd_yr":2015,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2016_04_EO%2F52-1693387_990_201506.pdf","updated":"2017-06-30T00:37:52.408Z","totrevenue":218083765,"totfuncexpns":225035121,"totassetsend":471481440,"totliabend":134447867,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":204312607,"totprgmrevnue":1307731,"invstmntinc":1682359,"txexmptbndsproceeds":0,"royaltsinc":3690098,"grsrntsreal":6217505,"grsrntsprsnl":0,"rntlexpnsreal":6006404,"rntlexpnsprsnl":0,"rntlincreal":211101,"rntlincprsnl":0,"netrntlinc":211101,"grsalesecur":47420914,"grsalesothr":0,"cstbasisecur":40826090,"cstbasisothr":0,"gnlsecur":6594824,"gnlsothr":0,"netgnls":6594824,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":285045,"compnsatncurrofcr":4524424,"othrsalwages":51415285,"payrolltx":3334892,"profndraising":818540,"txexmptbndsend":0,"secrdmrtgsend":59830701,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":337033573,"nonpfrea":"7","gftgrntsrcvd170":1004408367,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":68521777,"grsrcptsrelated170":2306845,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201406,"tax_prd_yr":2014,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_12_EO%2F52-1693387_990_201406.pdf","updated":"2017-06-30T00:07:58.943Z","totrevenue":227675082,"totfuncexpns":220790782,"totassetsend":491558242,"totliabend":133704323,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":217482602,"totprgmrevnue":810369,"invstmntinc":1428645,"txexmptbndsproceeds":0,"royaltsinc":4425244,"grsrntsreal":6095918,"grsrntsprsnl":0,"rntlexpnsreal":5847474,"rntlexpnsprsnl":0,"rntlincreal":248444,"rntlincprsnl":0,"netrntlinc":248444,"grsalesecur":92556905,"grsalesothr":0,"cstbasisecur":89497874,"cstbasisothr":0,"gnlsecur":3059031,"gnlsothr":0,"netgnls":3059031,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":220747,"compnsatncurrofcr":4171652,"othrsalwages":52002831,"payrolltx":3237442,"profndraising":1363186,"txexmptbndsend":29458981,"secrdmrtgsend":32140000,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":357853919,"nonpfrea":"7","gftgrntsrcvd170":964988967,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":67438503,"grsrcptsrelated170":1668939,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201306,"tax_prd_yr":2013,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2013_12_EO%2F52-1693387_990_201306.pdf","updated":"2017-06-29T23:52:53.233Z","totrevenue":229248747,"totfuncexpns":203731525,"totassetsend":450932452,"totliabend":132113971,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":215817911,"totprgmrevnue":568448,"invstmntinc":1883265,"txexmptbndsproceeds":0,"royaltsinc":5955760,"grsrntsreal":6682666,"grsrntsprsnl":0,"rntlexpnsreal":5524453,"rntlexpnsprsnl":0,"rntlincreal":1158213,"rntlincprsnl":0,"netrntlinc":1158213,"grsalesecur":70765878,"grsalesothr":0,"cstbasisecur":67155554,"cstbasisothr":0,"gnlsecur":3610324,"gnlsothr":0,"netgnls":3610324,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":254826,"compnsatncurrofcr":4104754,"othrsalwages":47179003,"payrolltx":3064347,"profndraising":947703,"txexmptbndsend":30906577,"secrdmrtgsend":32890000,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":318818481,"nonpfrea":"7","gftgrntsrcvd170":894019307,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":69363615,"grsrcptsrelated170":1474413,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201206,"tax_prd_yr":2012,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_12_EO%2F52-1693387_990_201206.pdf","updated":"2017-06-29T23:37:25.779Z","totrevenue":208495555,"totfuncexpns":191549257,"totassetsend":412075560,"totliabend":140380980,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":195342694,"totprgmrevnue":752916,"invstmntinc":2692203,"txexmptbndsproceeds":0,"royaltsinc":7730599,"grsrntsreal":5468835,"grsrntsprsnl":0,"rntlexpnsreal":5440896,"rntlexpnsprsnl":0,"rntlincreal":27939,"rntlincprsnl":0,"netrntlinc":27939,"grsalesecur":1584011,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":1584011,"gnlsothr":0,"netgnls":1584011,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":365193,"compnsatncurrofcr":3704209,"othrsalwages":43113552,"payrolltx":2806033,"profndraising":1301714,"txexmptbndsend":32533887,"secrdmrtgsend":33625000,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":271694580,"nonpfrea":"7","gftgrntsrcvd170":830521338,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":63638617,"grsrcptsrelated170":1565272,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387},{"tax_prd":201106,"tax_prd_yr":2011,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_06_EO%2F52-1693387_990_201106.pdf","updated":"2017-06-29T23:37:24.230Z","totrevenue":182067246,"totfuncexpns":184039636,"totassetsend":400489841,"totliabend":132496415,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":171452553,"totprgmrevnue":583515,"invstmntinc":3014345,"txexmptbndsproceeds":0,"royaltsinc":4167833,"grsrntsreal":5667328,"grsrntsprsnl":0,"rntlexpnsreal":5506885,"rntlexpnsprsnl":0,"rntlincreal":160443,"rntlincprsnl":0,"netrntlinc":160443,"grsalesecur":62088039,"grsalesothr":0,"cstbasisecur":59664654,"cstbasisothr":0,"gnlsecur":2423385,"gnlsothr":0,"netgnls":2423385,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":265172,"compnsatncurrofcr":3650764,"othrsalwages":38517299,"payrolltx":2747877,"profndraising":1255316,"txexmptbndsend":33190121,"secrdmrtgsend":34345000,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":267993426,"nonpfrea":"7","gftgrntsrcvd170":844515407,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":55376044,"grsrcptsrelated170":1451919,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":521693387}],"filings_without_data":[{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F521693387_202406_990_2025050123418710.pdf"},{"tax_prd":201006,"tax_prd_yr":2010,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2011_03_EO%2F52-1693387_990_201006.pdf"},{"tax_prd":200906,"tax_prd_yr":2009,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2010_03_EO%2F52-1693387_990_200906.pdf"},{"tax_prd":200806,"tax_prd_yr":2008,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2009_01_EO%2F52-1693387_990_200806.pdf"},{"tax_prd":200706,"tax_prd_yr":2007,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_11_EO%2F52-1693387_990_200706.pdf"},{"tax_prd":200606,"tax_prd_yr":2006,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2007_12_EO%2F52-1693387_990_200606.pdf"},{"tax_prd":200506,"tax_prd_yr":2005,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_02_EO%2F52-1693387_990_200506.pdf"},{"tax_prd":200406,"tax_prd_yr":2004,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2004_12_EO%2F52-1693387_990_200406.pdf"},{"tax_prd":200306,"tax_prd_yr":2003,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2003_12_EO%2F52-1693387_990_200306.pdf"},{"tax_prd":200206,"tax_prd_yr":2002,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2003_02_EO%2F52-1693387_990_200206.pdf"},{"tax_prd":200106,"tax_prd_yr":2001,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2002_01_EO%2F52-1693387_990_200106.pdf"}],"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

## Section 4: Goodwill Industries International Inc

### Search: "Goodwill Industries International Inc"

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/search.json?q=Goodwill+Industries+International+Inc
Retrieved (UTC): 2026-10-23T21:56:13Z
HTTP status: HTTP/1.1 200 OK

total_results as shown: 1. Organizations on this page: 1. num_pages as shown: 1.

- Result `530196517`: strein `"53-0196517"`, name `"Goodwill Industries International Inc"`, city `"Rockville"`, state `"MD"`. Status: examined below.

Source: <https://projects.propublica.org/nonprofits/api/v2/search.json?q=Goodwill+Industries+International+Inc>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:14 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=jKVUEigxdI.tp7ZtTr1F6VdT7Pw2u4VEsLocmnkJFTU-1792792574.6083724-1.0.1.1-ALuRce5Tj1oEY4yFbGucp6h14YIHOUpB30a2sPPdzcc; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd974802239e-SJC
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
ETag: W/"bdbfd3f62334b8e99ea7f18d5932e49f"
Expires: Sat, 24 Oct 2026 21:56:14 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: fee2f072-2727-491a-b80b-70f0c3129491
x-runtime: 0.069817
Transfer-Encoding: chunked

{"total_results":1,"organizations":[{"ein":530196517,"strein":"53-0196517","name":"Goodwill Industries International Inc","sub_name":"Goodwill Industries International Inc","city":"Rockville","state":"MD","ntee_code":"N320","raw_ntee_code":"N320","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":128.3335}],"num_pages":1,"cur_page":0,"page_offset":0,"per_page":25,"search_query":"Goodwill Industries International Inc","selected_state":null,"selected_ntee":null,"selected_code":null,"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

### Organization: EIN 530196517

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json
Retrieved (UTC): 2026-10-23T21:56:13Z
HTTP status: HTTP/1.1 200 OK

Identity, from the organization block:

- Legal name (name) as shown: `"Goodwill Industries International Inc"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"name":"Goodwill Industries International Inc"
```

- EIN (ein) as shown: `530196517`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"ein":530196517
```

- City (city) as shown: `"Rockville"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"city":"Rockville"
```

- State (state) as shown: `"MD"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"state":"MD"
```

Figures, from the filings_with_data entry with the highest tax_prd (202312 of 13 entries). The response states no unit; values are as shown.

- Tax period of the filing (tax_prd) as shown: `202312`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"tax_prd":202312
```

- Total revenue (totrevenue) as shown: `70964985`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"totrevenue":70964985
```

- Total functional expenses (totfuncexpns) as shown: `67699789`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"totfuncexpns":67699789
```

- Total assets, end of year (totassetsend) as shown: `67228414`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"totassetsend":67228414
```

- Total liabilities, end of year (totliabend) as shown: `9418211`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"totliabend":9418211
```

- A later filing is listed without extracted figures (filings_without_data), tax_prd as shown: `202412`. No figure above comes from it.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
{"tax_prd":202412,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196517_202412_990_2025122923825736.pdf"}
```

- Organization record tax_period as shown: `"2025-12-01"`. This is the organization block's field, not the period of the figures above.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>

```
"tax_period":"2025-12-01"
```

Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/530196517.json>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:15 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=07PiV31nSqdikJ_X0g9Q_TXeaIxKmiddXEN3dZJBtps-1792792575.632031-1.0.1.1-IOdwq_JAdrB1WVklWtSz_hZD49yb7eyjqomCnokWHto; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fd9dab570c7a-EWR
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
ETag: W/"7375e848c70064f4ce03b6a41805de98"
Expires: Sat, 24 Oct 2026 21:56:15 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: 893ad2c6-32ff-4dd7-9379-c4205d6f53a0
x-runtime: 0.177225
Transfer-Encoding: chunked

{"organization":{"id":530196517,"ein":530196517,"name":"Goodwill Industries International Inc","careofname":null,"address":"15810 INDIANOLA DR","city":"Rockville","state":"MD","zipcode":"20855-2674","exemption_number":0,"subsection_code":3,"affiliation_code":3,"classification_codes":"1200","ruling_date":"1952-01-01","deductibility_code":1,"foundation_code":15,"activity_codes":"059566160","organization_code":1,"exempt_organization_status_code":1,"tax_period":"2025-12-01","asset_code":9,"income_code":9,"filing_requirement_code":1,"pf_filing_requirement_code":0,"accounting_period":12,"asset_amount":76699426,"income_amount":185960280,"revenue_amount":66583568,"ntee_code":"N320","sort_name":null,"created_at":"2023-05-09T20:32:12.933Z","updated_at":"2026-10-21T13:28:56.771Z","data_source":"current_2026_10_21","have_extracts":null,"have_pdfs":null,"latest_object_id":"202611269349302811"},"filings_with_data":[{"tax_prd":202312,"tax_prd_yr":2023,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196517_202312_990_2024062122571371.pdf","updated":"2025-08-05T16:09:45.876Z","totrevenue":70964985,"totfuncexpns":67699789,"totassetsend":67228414,"totliabend":9418211,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":37920322,"totprgmrevnue":30563358,"invstmntinc":1797387,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":322673,"grsrntsprsnl":0,"rntlexpnsreal":166010,"rntlexpnsprsnl":0,"rntlincreal":156663,"rntlincprsnl":0,"netrntlinc":156663,"grsalesecur":7902238,"grsalesothr":0,"cstbasisecur":7570988,"cstbasisothr":0,"gnlsecur":331250,"gnlsothr":0,"netgnls":331250,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":196005,"compnsatncurrofcr":2943112,"othrsalwages":14440657,"payrolltx":1200956,"profndraising":75000,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":57810203,"nonpfrea":"7","gftgrntsrcvd170":208209143,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":4411009,"grsrcptsrelated170":124509572,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":202212,"tax_prd_yr":2022,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=download990pdf_08_2023_prefixes_52-81%2F530196517_202212_990_2023082921573294.pdf","updated":"2024-08-28T20:14:04.511Z","totrevenue":61913793,"totfuncexpns":63836428,"totassetsend":67000954,"totliabend":12716508,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":35637579,"totprgmrevnue":25799301,"invstmntinc":388166,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":291740,"grsrntsprsnl":0,"rntlexpnsreal":220766,"rntlexpnsprsnl":0,"rntlincreal":70974,"rntlincprsnl":0,"netrntlinc":70974,"grsalesecur":7809256,"grsalesothr":0,"cstbasisecur":7863190,"cstbasisothr":0,"gnlsecur":-53934,"gnlsothr":0,"netgnls":-53934,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":71707,"compnsatncurrofcr":2793500,"othrsalwages":12008081,"payrolltx":1071198,"profndraising":139100,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":54284446,"nonpfrea":"7","gftgrntsrcvd170":204680276,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2776251,"grsrcptsrelated170":117178315,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":202112,"tax_prd_yr":2021,"formtype":0,"pdf_url":null,"updated":"2023-08-07T19:42:52.665Z","totrevenue":66436715,"totfuncexpns":55346277,"totassetsend":67550943,"totliabend":9915849,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":43462789,"totprgmrevnue":22465633,"invstmntinc":216636,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":291133,"grsrntsprsnl":0,"rntlexpnsreal":184158,"rntlexpnsprsnl":0,"rntlincreal":106975,"rntlincprsnl":0,"netrntlinc":106975,"grsalesecur":3784585,"grsalesothr":0,"cstbasisecur":3613660,"cstbasisothr":0,"gnlsecur":170925,"gnlsothr":0,"netgnls":170925,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":13757,"compnsatncurrofcr":2693553,"othrsalwages":9817758,"payrolltx":884806,"profndraising":75000,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":57635094,"nonpfrea":"07","gftgrntsrcvd170":203616308,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2551419,"grsrcptsrelated170":114620238,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":202012,"tax_prd_yr":2020,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=05_2021_prefixes_52-54%2F530196517_202012_990_2021052418175317.pdf","updated":"2022-07-01T20:34:48.242Z","totrevenue":77145526,"totfuncexpns":52306762,"totassetsend":56845919,"totliabend":10460589,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":54802941,"totprgmrevnue":21616998,"invstmntinc":220444,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":303578,"grsrntsprsnl":0,"rntlexpnsreal":231048,"rntlexpnsprsnl":0,"rntlincreal":72530,"rntlincprsnl":0,"netrntlinc":72530,"grsalesecur":634002,"grsalesothr":0,"cstbasisecur":216620,"cstbasisothr":0,"gnlsecur":417382,"gnlsothr":0,"netgnls":417382,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":15231,"compnsatncurrofcr":1917011,"othrsalwages":9726312,"payrolltx":915583,"profndraising":0,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":1908300,"retainedearnend":0,"totnetassetend":46385330,"nonpfrea":"7","gftgrntsrcvd170":178632433,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2513560,"grsrcptsrelated170":116107613,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201912,"tax_prd_yr":2019,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=08_2020_prefixes_52-57%2F530196517_201912_990_2020082017247421.pdf","updated":"2021-08-30T18:55:31.607Z","totrevenue":60908886,"totfuncexpns":60671880,"totassetsend":32176942,"totliabend":8722993,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":36385512,"totprgmrevnue":24092732,"invstmntinc":284872,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":294380,"grsrntsprsnl":0,"rntlexpnsreal":288336,"rntlexpnsprsnl":0,"rntlincreal":6044,"rntlincprsnl":0,"netrntlinc":6044,"grsalesecur":8084684,"grsalesothr":0,"cstbasisecur":8018071,"cstbasisothr":0,"gnlsecur":66613,"gnlsothr":0,"netgnls":66613,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":73113,"compnsatncurrofcr":2110865,"othrsalwages":11756372,"payrolltx":978555,"profndraising":0,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":23453949,"nonpfrea":"07","gftgrntsrcvd170":144487505,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2460124,"grsrcptsrelated170":118467511,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201812,"tax_prd_yr":2018,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=06_2020_prefixes_51-57%2F530196517_201812_990_2020060517178771.pdf","updated":"2021-08-30T18:31:41.655Z","totrevenue":58110226,"totfuncexpns":59731817,"totassetsend":31781931,"totliabend":9168322,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":34391455,"totprgmrevnue":23248959,"invstmntinc":192761,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":292541,"grsrntsprsnl":0,"rntlexpnsreal":279297,"rntlexpnsprsnl":0,"rntlincreal":13244,"rntlincprsnl":0,"netrntlinc":13244,"grsalesecur":8778390,"grsalesothr":0,"cstbasisecur":8625094,"cstbasisothr":0,"gnlsecur":153296,"gnlsothr":0,"netgnls":153296,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":110511,"compnsatncurrofcr":2094239,"othrsalwages":12191499,"payrolltx":1056131,"profndraising":0,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":22613609,"nonpfrea":"07","gftgrntsrcvd170":127028868,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2343033,"grsrcptsrelated170":117805690,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201712,"tax_prd_yr":2017,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=07_2018_prefixes_52-58%2F530196517_201712_990_2018073015549508.pdf","updated":"2019-10-15T18:36:15.859Z","totrevenue":58045952,"totfuncexpns":54824634,"totassetsend":34308012,"totliabend":9568105,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":34573611,"totprgmrevnue":23256391,"invstmntinc":160668,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":286892,"grsrntsprsnl":0,"rntlexpnsreal":297080,"rntlexpnsprsnl":0,"rntlincreal":-10188,"rntlincprsnl":0,"netrntlinc":-10188,"grsalesecur":15554441,"grsalesothr":164719,"cstbasisecur":15502396,"cstbasisothr":165080,"gnlsecur":52045,"gnlsothr":-361,"netgnls":51684,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":13786,"compnsatncurrofcr":1601752,"othrsalwages":12179484,"payrolltx":968107,"profndraising":0,"txexmptbndsend":0,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":24739907,"nonpfrea":"7","gftgrntsrcvd170":115528678,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2321411,"grsrcptsrelated170":117343558,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201612,"tax_prd_yr":2016,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=01_2018_prefixes_52-54%2F530196517_201612_990_2018010915103405.pdf","updated":"2018-12-10T23:07:57.663Z","totrevenue":42532780,"totfuncexpns":44954642,"totassetsend":29242540,"totliabend":8294946,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":18478914,"totprgmrevnue":23948466,"invstmntinc":195363,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":274547,"grsrntsprsnl":0,"rntlexpnsreal":325472,"rntlexpnsprsnl":0,"rntlincreal":-50925,"rntlincprsnl":0,"netrntlinc":-50925,"grsalesecur":4939083,"grsalesothr":970764,"cstbasisecur":4977851,"cstbasisothr":983770,"gnlsecur":-38768,"gnlsothr":-13006,"netgnls":-51774,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":12736,"compnsatncurrofcr":1846955,"othrsalwages":11966582,"payrolltx":1048271,"profndraising":0,"txexmptbndsend":1205946,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":20947594,"nonpfrea":"7","gftgrntsrcvd170":109180557,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2363307,"grsrcptsrelated170":115913706,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201512,"tax_prd_yr":2015,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2016_08_EO%2F53-0196517_990_201512.pdf","updated":"2017-06-30T00:37:22.329Z","totrevenue":44941304,"totfuncexpns":45702551,"totassetsend":32028358,"totliabend":9040800,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":20658013,"totprgmrevnue":23977463,"invstmntinc":196047,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":274539,"grsrntsprsnl":0,"rntlexpnsreal":336347,"rntlexpnsprsnl":0,"rntlincreal":-61808,"rntlincprsnl":0,"netrntlinc":-61808,"grsalesecur":7219264,"grsalesothr":0,"cstbasisecur":7092851,"cstbasisothr":0,"gnlsecur":126413,"gnlsothr":0,"netgnls":126413,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":45176,"compnsatncurrofcr":1533817,"othrsalwages":12496589,"payrolltx":960043,"profndraising":0,"txexmptbndsend":1327329,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":22987558,"nonpfrea":"7","gftgrntsrcvd170":122612269,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2364921,"grsrcptsrelated170":112302801,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201412,"tax_prd_yr":2014,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2015_08_EO%2F53-0196517_990_201412.pdf","updated":"2017-06-30T00:19:34.479Z","totrevenue":42792561,"totfuncexpns":45993524,"totassetsend":34039625,"totliabend":10041644,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":18926875,"totprgmrevnue":23432494,"invstmntinc":188896,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":276450,"grsrntsprsnl":0,"rntlexpnsreal":255277,"rntlexpnsprsnl":0,"rntlincreal":21173,"rntlincprsnl":0,"netrntlinc":21173,"grsalesecur":10046205,"grsalesothr":0,"cstbasisecur":9897718,"cstbasisothr":0,"gnlsecur":148487,"gnlsothr":0,"netgnls":148487,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":74636,"compnsatncurrofcr":1741766,"othrsalwages":12072927,"payrolltx":967592,"profndraising":0,"txexmptbndsend":1448491,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":23997981,"nonpfrea":"7","gftgrntsrcvd170":135361880,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2521808,"grsrcptsrelated170":107752783,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201312,"tax_prd_yr":2013,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_09_EO%2F53-0196517_990_201312.pdf","updated":"2017-06-30T00:06:00.759Z","totrevenue":46058697,"totfuncexpns":43065887,"totassetsend":35447285,"totliabend":8457624,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":22891266,"totprgmrevnue":22783536,"invstmntinc":166436,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":297244,"grsrntsprsnl":0,"rntlexpnsreal":296963,"rntlexpnsprsnl":0,"rntlincreal":281,"rntlincprsnl":0,"netrntlinc":281,"grsalesecur":4716860,"grsalesothr":0,"cstbasisecur":4689375,"cstbasisothr":0,"gnlsecur":27485,"gnlsothr":0,"netgnls":27485,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":189693,"compnsatncurrofcr":1498667,"othrsalwages":11067474,"payrolltx":911820,"profndraising":0,"txexmptbndsend":1572176,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":26989661,"nonpfrea":"7","gftgrntsrcvd170":135460074,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2571297,"grsrcptsrelated170":102622769,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201212,"tax_prd_yr":2012,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_01_EO%2F53-0196517_990_201212.pdf","updated":"2017-06-29T23:50:52.549Z","totrevenue":50770992,"totfuncexpns":44582888,"totassetsend":31125117,"totliabend":7594637,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":28225490,"totprgmrevnue":21836015,"invstmntinc":199731,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":297239,"grsrntsprsnl":0,"rntlexpnsreal":291283,"rntlexpnsprsnl":0,"rntlincreal":5956,"rntlincprsnl":0,"netrntlinc":5956,"grsalesecur":5767459,"grsalesothr":0,"cstbasisecur":5269360,"cstbasisothr":0,"gnlsecur":498099,"gnlsothr":0,"netgnls":498099,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":5701,"compnsatncurrofcr":1437022,"othrsalwages":11093314,"payrolltx":871264,"profndraising":0,"txexmptbndsend":1709635,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":23530480,"nonpfrea":"7","gftgrntsrcvd170":126017091,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":2675431,"grsrcptsrelated170":97451201,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517},{"tax_prd":201112,"tax_prd_yr":2011,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_10_EO%2F53-0196517_990_201112.pdf","updated":"2017-06-29T23:37:24.469Z","totrevenue":52682395,"totfuncexpns":53107982,"totassetsend":25171878,"totliabend":7694009,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":31910626,"totprgmrevnue":20352270,"invstmntinc":152927,"txexmptbndsproceeds":0,"royaltsinc":0,"grsrntsreal":297239,"grsrntsprsnl":0,"rntlexpnsreal":292079,"rntlexpnsprsnl":0,"rntlincreal":5160,"rntlincprsnl":0,"netrntlinc":5160,"grsalesecur":249039,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":249039,"gnlsothr":0,"netgnls":249039,"grsincfndrsng":0,"lessdirfndrsng":0,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":12373,"compnsatncurrofcr":1797849,"othrsalwages":10253610,"payrolltx":849252,"profndraising":0,"txexmptbndsend":1811355,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":17477869,"nonpfrea":"7","gftgrntsrcvd170":108946507,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":3000429,"grsrcptsrelated170":91954947,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":530196517}],"filings_without_data":[{"tax_prd":202412,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F530196517_202412_990_2025122923825736.pdf"},{"tax_prd":201012,"tax_prd_yr":2010,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2011_09_EO%2F53-0196517_990_201012.pdf"},{"tax_prd":200912,"tax_prd_yr":2009,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2010_08_EO%2F53-0196517_990_200912.pdf"},{"tax_prd":200812,"tax_prd_yr":2008,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2009_06_EO%2F53-0196517_990_200812.pdf"},{"tax_prd":200712,"tax_prd_yr":2007,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2009_01_EO%2F53-0196517_990_200712.pdf"},{"tax_prd":200612,"tax_prd_yr":2006,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_02_EO%2F53-0196517_990_200612.pdf"},{"tax_prd":200512,"tax_prd_yr":2005,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_06_EO%2F53-0196517_990_200512.pdf"},{"tax_prd":200412,"tax_prd_yr":2004,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2005_06_EO%2F53-0196517_990_200412.pdf"},{"tax_prd":200312,"tax_prd_yr":2003,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2004_12_EO%2F53-0196517_990_200312.pdf"},{"tax_prd":200212,"tax_prd_yr":2002,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2003_06_EO%2F53-0196517_990_200212.pdf"},{"tax_prd":200112,"tax_prd_yr":2001,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2002_06_EO%2F53-0196517_990_200112.pdf"}],"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

## Section 5: United States Fund for UNICEF

### Search: "United States Fund for UNICEF"

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/search.json?q=United+States+Fund+for+UNICEF
Retrieved (UTC): 2026-10-23T21:56:14Z
HTTP status: HTTP/1.1 200 OK

total_results as shown: 3. Organizations on this page: 3. num_pages as shown: 1.

- Result `131760110`: strein `"13-1760110"`, name `"United States Fund For Unicef"`, city `"New York"`, state `"NY"`. Status: examined below.
- Result `810997990`: strein `"81-0997990"`, name `"Plus Fund Paid Leave For The United States"`, city `"San Francisco"`, state `"CA"`. Status: not examined.
- Result `464441337`: strein `"46-4441337"`, name `"Farragut Fund For Catalan Culture In The United States"`, city `"New York"`, state `"NY"`. Status: not examined.

Source: <https://projects.propublica.org/nonprofits/api/v2/search.json?q=United+States+Fund+for+UNICEF>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:16 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=7ZjpM.xdveCP4bLPr9vsGLJhSFBdoE8.6vJ4hhys3SA-1792792576.3914175-1.0.1.1-ZCfHf.nYWbNtpM3WJjZDAsAurNIkS1O9yQ7u8PXu1og; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fda269de7a41-ATL
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
ETag: W/"edb465a94a68993ffce5cd364e8be633"
Expires: Sat, 24 Oct 2026 21:56:16 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: b9e50001-6ebd-4b01-80e5-0c55f466ac09
x-runtime: 0.053503
Transfer-Encoding: chunked

{"total_results":3,"organizations":[{"ein":131760110,"strein":"13-1760110","name":"United States Fund For Unicef","sub_name":"United States Fund For Unicef","city":"New York","state":"NY","ntee_code":"Q420","raw_ntee_code":"Q420","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":148.92442},{"ein":810997990,"strein":"81-0997990","name":"Plus Fund Paid Leave For The United States","sub_name":"Plus Fund Paid Leave For The United States Plus Fund","city":"San Francisco","state":"CA","ntee_code":"B05","raw_ntee_code":"B05","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":86.22276},{"ein":464441337,"strein":"46-4441337","name":"Farragut Fund For Catalan Culture In The United States","sub_name":"Farragut Fund For Catalan Culture In The United States","city":"New York","state":"NY","ntee_code":"T21","raw_ntee_code":"T21","subseccd":3,"has_subseccd":true,"have_filings":null,"have_extracts":null,"have_pdfs":null,"score":81.21949}],"num_pages":1,"cur_page":0,"page_offset":0,"per_page":25,"search_query":"United States Fund for UNICEF","selected_state":null,"selected_ntee":null,"selected_code":null,"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

### Organization: EIN 131760110

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json
Retrieved (UTC): 2026-10-23T21:56:15Z
HTTP status: HTTP/1.1 200 OK

Identity, from the organization block:

- Legal name (name) as shown: `"United States Fund For Unicef"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"name":"United States Fund For Unicef"
```

- EIN (ein) as shown: `131760110`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"ein":131760110
```

- City (city) as shown: `"New York"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"city":"New York"
```

- State (state) as shown: `"NY"`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"state":"NY"
```

Figures, from the filings_with_data entry with the highest tax_prd (202306 of 12 entries). The response states no unit; values are as shown.

- Tax period of the filing (tax_prd) as shown: `202306`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"tax_prd":202306
```

- Total revenue (totrevenue) as shown: `829050932`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"totrevenue":829050932
```

- Total functional expenses (totfuncexpns) as shown: `857921084`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"totfuncexpns":857921084
```

- Total assets, end of year (totassetsend) as shown: `295994448`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"totassetsend":295994448
```

- Total liabilities, end of year (totliabend) as shown: `94774790`
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"totliabend":94774790
```

- A later filing is listed without extracted figures (filings_without_data), tax_prd as shown: `202506`. No figure above comes from it.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
{"tax_prd":202506,"tax_prd_yr":2025,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F131760110_202506_990_2026031123999775.pdf"}
```

- A later filing is listed without extracted figures (filings_without_data), tax_prd as shown: `202406`. No figure above comes from it.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F131760110_202406_990_2025042523388250.pdf"}
```

- Organization record tax_period as shown: `"2025-06-01"`. This is the organization block's field, not the period of the figures above.
  Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>

```
"tax_period":"2025-06-01"
```

Source: <https://projects.propublica.org/nonprofits/api/v2/organizations/131760110.json>
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:56:17 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=AkMhjNPK9Fl0AA9Sv.Mx3F3z9s5k8WAy8asXiW5coCY-1792792577.476997-1.0.1.1-y5gACYlDgcqqzfviNSAZG5y.isdrit0kA2TREh2FyRY; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fda93e9ccefc-ATL
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
ETag: W/"3c9bf9042a6e82cd496cdff502b9b074"
Expires: Sat, 24 Oct 2026 21:56:17 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: f6f88c56-3672-4b4a-84b2-f6bced6e7435
x-runtime: 0.155493
Transfer-Encoding: chunked

{"organization":{"id":131760110,"ein":131760110,"name":"United States Fund For Unicef","careofname":"% MICHAEL CHEN","address":"125 MAIDEN LANE","city":"New York","state":"NY","zipcode":"10038-4912","exemption_number":0,"subsection_code":3,"affiliation_code":3,"classification_codes":"1000","ruling_date":"1949-08-01","deductibility_code":1,"foundation_code":15,"activity_codes":"927602000","organization_code":1,"exempt_organization_status_code":1,"tax_period":"2025-06-01","asset_code":9,"income_code":9,"filing_requirement_code":1,"pf_filing_requirement_code":0,"accounting_period":6,"asset_amount":514509936,"income_amount":845648886,"revenue_amount":835217861,"ntee_code":"Q420","sort_name":null,"created_at":"2023-05-09T20:23:20.828Z","updated_at":"2026-10-21T13:27:03.269Z","data_source":"current_2026_10_21","have_extracts":null,"have_pdfs":null,"latest_object_id":"202630309349300223"},"filings_with_data":[{"tax_prd":202306,"tax_prd_yr":2023,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=download990pdf_05_2024_prefixes_06-16%2F131760110_202306_990_2024050722385081.pdf","updated":"2025-08-05T16:07:59.426Z","totrevenue":829050932,"totfuncexpns":857921084,"totassetsend":295994448,"totliabend":94774790,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":825269573,"totprgmrevnue":0,"invstmntinc":4922538,"txexmptbndsproceeds":0,"royaltsinc":588053,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":22348443,"grsalesothr":0,"cstbasisecur":23599928,"cstbasisothr":0,"gnlsecur":-1251485,"gnlsothr":0,"netgnls":-1251485,"grsincfndrsng":434176,"lessdirfndrsng":1427312,"netincfndrsng":-993136,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":515389,"compnsatncurrofcr":3808127,"othrsalwages":31315618,"payrolltx":2372770,"profndraising":21128759,"txexmptbndsend":27735183,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":201219658,"nonpfrea":"7","gftgrntsrcvd170":3491581513,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":15098023,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":202206,"tax_prd_yr":2022,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F131760110_202206_990_2023060621385934.pdf","updated":"2024-08-28T20:05:15.965Z","totrevenue":1061946827,"totfuncexpns":995720663,"totassetsend":445451590,"totliabend":218508462,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":1059261676,"totprgmrevnue":0,"invstmntinc":1865649,"txexmptbndsproceeds":0,"royaltsinc":427223,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":12648796,"grsalesothr":0,"cstbasisecur":12646489,"cstbasisothr":0,"gnlsecur":2307,"gnlsothr":0,"netgnls":2307,"grsincfndrsng":44972,"lessdirfndrsng":1360827,"netincfndrsng":-1315855,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":1705827,"compnsatncurrofcr":3865527,"othrsalwages":29867939,"payrolltx":2075257,"profndraising":19684992,"txexmptbndsend":29420545,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":226943128,"nonpfrea":"7","gftgrntsrcvd170":3232691177,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":11944183,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":202106,"tax_prd_yr":2021,"formtype":0,"pdf_url":null,"updated":"2023-08-07T19:34:28.586Z","totrevenue":510721032,"totfuncexpns":479181624,"totassetsend":313758367,"totliabend":142114941,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":507732515,"totprgmrevnue":0,"invstmntinc":1503096,"txexmptbndsproceeds":0,"royaltsinc":852978,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":16483110,"grsalesothr":0,"cstbasisecur":16379991,"cstbasisothr":0,"gnlsecur":103119,"gnlsothr":0,"netgnls":103119,"grsincfndrsng":42817,"lessdirfndrsng":42817,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":529324,"compnsatncurrofcr":3461726,"othrsalwages":28140187,"payrolltx":2105474,"profndraising":1954781,"txexmptbndsend":31056566,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":171643426,"nonpfrea":"07","gftgrntsrcvd170":2645532311,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":11935294,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":202006,"tax_prd_yr":2020,"formtype":0,"pdf_url":null,"updated":"2022-07-01T20:26:28.984Z","totrevenue":573865026,"totfuncexpns":588576039,"totassetsend":394704546,"totliabend":257310303,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":571213232,"totprgmrevnue":0,"invstmntinc":1508991,"txexmptbndsproceeds":0,"royaltsinc":902134,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":1652214,"lessdirfndrsng":1652214,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":240669,"compnsatncurrofcr":6025672,"othrsalwages":23871676,"payrolltx":2162186,"profndraising":4580188,"txexmptbndsend":32644654,"secrdmrtgsend":0,"unsecurednotesend":6583900,"retainedearnend":0,"totnetassetend":137394243,"nonpfrea":"7","gftgrntsrcvd170":2693459771,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":11902730,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201906,"tax_prd_yr":2019,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=08_2020_prefixes_06-16%2F131760110_201906_990_2020081917243063.pdf","updated":"2021-08-30T18:52:43.564Z","totrevenue":538517959,"totfuncexpns":520829209,"totassetsend":406758577,"totliabend":255799733,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":535776656,"totprgmrevnue":0,"invstmntinc":1400615,"txexmptbndsproceeds":0,"royaltsinc":1126746,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":2881808,"lessdirfndrsng":2881808,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":213942,"compnsatncurrofcr":3922287,"othrsalwages":21224717,"payrolltx":1792019,"profndraising":4135720,"txexmptbndsend":34183527,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":150958844,"nonpfrea":"07","gftgrntsrcvd170":2619279962,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":12438523,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201806,"tax_prd_yr":2018,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=02_2019_prefixes_11-13%2F131760110_201806_990_2019020116054486.pdf","updated":"2019-10-15T18:32:54.283Z","totrevenue":567056368,"totfuncexpns":547800710,"totassetsend":247213249,"totliabend":115248285,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"Y","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":564169559,"totprgmrevnue":0,"invstmntinc":1133127,"txexmptbndsproceeds":0,"royaltsinc":1223624,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":3528142,"lessdirfndrsng":3528142,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":530058,"compnsatncurrofcr":2801905,"othrsalwages":23762064,"payrolltx":1812221,"profndraising":2865899,"txexmptbndsend":35679892,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":131964964,"nonpfrea":"7","gftgrntsrcvd170":2554464537,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":14418833,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201706,"tax_prd_yr":2017,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=03_2018_prefixes_01-75%2F131760110_201706_990_2018031315215578.pdf","updated":"2019-10-15T18:32:55.184Z","totrevenue":473933337,"totfuncexpns":476195828,"totassetsend":231115739,"totliabend":118977927,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":471461166,"totprgmrevnue":0,"invstmntinc":950662,"txexmptbndsproceeds":0,"royaltsinc":1333321,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":2284918,"lessdirfndrsng":2284918,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":0,"lesscstofgoods":0,"netincsales":0,"miscrevtot11e":188188,"compnsatncurrofcr":4144600,"othrsalwages":19537621,"payrolltx":1683064,"profndraising":3201192,"txexmptbndsend":37136444,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":112137812,"nonpfrea":"7","gftgrntsrcvd170":2297300116,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":15688242,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201606,"tax_prd_yr":2016,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2017_03_EO%2F13-1760110_990_201606.pdf","updated":"2017-06-30T00:35:05.000Z","totrevenue":553250245,"totfuncexpns":545844767,"totassetsend":216632370,"totliabend":102486376,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":550839158,"totprgmrevnue":0,"invstmntinc":905327,"txexmptbndsproceeds":0,"royaltsinc":1418183,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":3446279,"lessdirfndrsng":3446279,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":181879,"lesscstofgoods":94302,"netincsales":87577,"miscrevtot11e":0,"compnsatncurrofcr":3657638,"othrsalwages":18880001,"payrolltx":1632754,"profndraising":3094775,"txexmptbndsend":37534066,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":114145994,"nonpfrea":"7","gftgrntsrcvd170":2034348991,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":16168246,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201506,"tax_prd_yr":2015,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2016_01_EO%2F13-126316_10038_131760110.pdf","updated":"2017-06-30T00:19:25.050Z","totrevenue":500119774,"totfuncexpns":529274354,"totassetsend":236806150,"totliabend":129130982,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":497033423,"totprgmrevnue":0,"invstmntinc":1361484,"txexmptbndsproceeds":0,"royaltsinc":1585434,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":1960320,"lessdirfndrsng":1960320,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":202350,"lesscstofgoods":62917,"netincsales":139433,"miscrevtot11e":0,"compnsatncurrofcr":1871746,"othrsalwages":19231691,"payrolltx":1476437,"profndraising":2405977,"txexmptbndsend":38341417,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":107675168,"nonpfrea":"7","gftgrntsrcvd170":1735250885,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":15905520,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201406,"tax_prd_yr":2014,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_12_EO%2F13-1760110_990_201406.pdf","updated":"2017-06-30T00:07:56.817Z","totrevenue":475591950,"totfuncexpns":413154382,"totassetsend":258125021,"totliabend":120537127,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":470961231,"totprgmrevnue":0,"invstmntinc":2800538,"txexmptbndsproceeds":0,"royaltsinc":1707133,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":2386007,"lessdirfndrsng":2386007,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":182418,"lesscstofgoods":59370,"netincsales":123048,"miscrevtot11e":0,"compnsatncurrofcr":2088419,"othrsalwages":16439831,"payrolltx":1316855,"profndraising":2335813,"txexmptbndsend":40050000,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":137587894,"nonpfrea":"7","gftgrntsrcvd170":1475417377,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":17477575,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201306,"tax_prd_yr":2013,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2014_03_EO%2F13-1760110_990_201306.pdf","updated":"2017-06-30T00:05:47.564Z","totrevenue":310900028,"totfuncexpns":297954807,"totassetsend":157177108,"totliabend":83096611,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":307005138,"totprgmrevnue":0,"invstmntinc":1875678,"txexmptbndsproceeds":0,"royaltsinc":1750482,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":1434549,"lessdirfndrsng":1434549,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":1277541,"lesscstofgoods":1008811,"netincsales":268730,"miscrevtot11e":0,"compnsatncurrofcr":1902684,"othrsalwages":16636659,"payrolltx":1220511,"profndraising":2517687,"txexmptbndsend":40815000,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":74080497,"nonpfrea":"7","gftgrntsrcvd170":1242023625,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":3066202,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110},{"tax_prd":201206,"tax_prd_yr":2012,"formtype":0,"pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2012_12_EO%2F13-1760110_990_201206.pdf","updated":"2017-06-29T23:37:17.271Z","totrevenue":211543386,"totfuncexpns":204636266,"totassetsend":143789814,"totliabend":83170988,"pct_compnsatncurrofcr":0.0,"tax_pd":null,"subseccd":3,"unrelbusinccd":"N","initiationfees":0,"grsrcptspublicuse":0,"grsincmembers":0,"grsincother":0,"totcntrbgfts":208510041,"totprgmrevnue":0,"invstmntinc":728597,"txexmptbndsproceeds":0,"royaltsinc":2035390,"grsrntsreal":0,"grsrntsprsnl":0,"rntlexpnsreal":0,"rntlexpnsprsnl":0,"rntlincreal":0,"rntlincprsnl":0,"netrntlinc":0,"grsalesecur":0,"grsalesothr":0,"cstbasisecur":0,"cstbasisothr":0,"gnlsecur":0,"gnlsothr":0,"netgnls":0,"grsincfndrsng":2142448,"lessdirfndrsng":2142448,"netincfndrsng":0,"grsincgaming":0,"lessdirgaming":0,"netincgaming":0,"grsalesinvent":1260902,"lesscstofgoods":991544,"netincsales":269358,"miscrevtot11e":0,"compnsatncurrofcr":3099724,"othrsalwages":14384120,"payrolltx":1250939,"profndraising":1467648,"txexmptbndsend":41540000,"secrdmrtgsend":0,"unsecurednotesend":0,"retainedearnend":0,"totnetassetend":60618826,"nonpfrea":"7","gftgrntsrcvd170":1155771225,"txrevnuelevied170":0,"srvcsval170":0,"grsinc170":4915714,"grsrcptsrelated170":0,"totgftgrntrcvd509":0,"grsrcptsadmissn509":0,"txrevnuelevied509":0,"srvcsval509":0,"subtotsuppinc509":0,"totsupp509":0,"ein":131760110}],"filings_without_data":[{"tax_prd":202506,"tax_prd_yr":2025,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F131760110_202506_990_2026031123999775.pdf"},{"tax_prd":202406,"tax_prd_yr":2024,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=IRS%2F131760110_202406_990_2025042523388250.pdf"},{"tax_prd":201106,"tax_prd_yr":2011,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2011_12_EO%2F13-1760110_990_201106.pdf"},{"tax_prd":201006,"tax_prd_yr":2010,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2011_03_EO%2F13-1760110_990_201006.pdf"},{"tax_prd":200906,"tax_prd_yr":2009,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2009_12_EO%2F13-1760110_990_200906.pdf"},{"tax_prd":200806,"tax_prd_yr":2008,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2009_01_EO%2F13-1760110_990_200806.pdf"},{"tax_prd":200706,"tax_prd_yr":2007,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_11_EO%2F13-1760110_990_200706.pdf"},{"tax_prd":200606,"tax_prd_yr":2006,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2008_01_EO%2F13-1760110_990_200606.pdf"},{"tax_prd":200506,"tax_prd_yr":2005,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2006_01_EO%2F13-1760110_990_200506.pdf"},{"tax_prd":200406,"tax_prd_yr":2004,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2005_03_EO%2F13-1760110_990_200406.pdf"},{"tax_prd":200306,"tax_prd_yr":2003,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2004_02_EO%2F13-1760110_990_200306.pdf"},{"tax_prd":200206,"tax_prd_yr":2002,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2003_03_EO%2F13-1760110_990_200206.pdf"},{"tax_prd":200106,"tax_prd_yr":2001,"formtype":0,"formtype_str":"990","pdf_url":"https://projects.propublica.org/nonprofits/download-filing?path=2002_03_EO%2F13-1760110_990_200106.pdf"}],"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

## Section 6: Zxqv Memorial Pancake Foundation

### Search: "Zxqv Memorial Pancake Foundation"

QUERY: GET https://projects.propublica.org/nonprofits/api/v2/search.json?q=Zxqv+Memorial+Pancake+Foundation
Retrieved (UTC): 2026-10-23T21:56:16Z
HTTP status: HTTP/1.1 404 Not Found

total_results as shown: 0. Organizations on this page: 0. num_pages as shown: 0.

The search returned no organizations. The complete raw response is below; this is a search observation, not proof that no such organization exists.

Source: <https://projects.propublica.org/nonprofits/api/v2/search.json?q=Zxqv+Memorial+Pancake+Foundation>
```
HTTP/1.1 404 Not Found
Date: Fri, 23 Oct 2026 21:56:18 GMT
Content-Type: application/json; charset=utf-8
alt-svc: h3=":443"; ma=86400
x-xss-protection: 0
set-cookie: _cfuvid=mVrwYQfeKk6LPYZQtgj1by6F7cJy.a6RJGQGzfGuAX8-1792792578.370341-1.0.1.1-HqdA8ZJni9kisnVQycL.n3uAWq2jZxvkZHXoBSj1nno; HttpOnly; SameSite=None; Secure; Path=/; Domain=propublica.org
CF-Ray: a4f3fdaeccfe3a10-SEA
CF-Cache-Status: HIT
Cache-Control: public, max-age=86400
Expires: Sat, 24 Oct 2026 21:56:18 GMT
Server: cloudflare
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Vary: Accept,Accept-Encoding,Content-Type
referrer-policy: strict-origin-when-cross-origin
x-content-type-options: nosniff
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-permitted-cross-domain-policies: none
x-request-id: d955706c-ba2a-4947-9af1-9124f66a86aa
x-runtime: 0.052934
Transfer-Encoding: chunked

{"total_results":0,"organizations":[],"num_pages":0,"cur_page":0,"page_offset":0,"per_page":25,"search_query":"Zxqv Memorial Pancake Foundation","selected_state":null,"selected_ntee":null,"selected_code":null,"data_source":"ProPublica Nonprofit Explorer API: https://projects.propublica.org/nonprofits/api/\nIRS Exempt Organizations Business Master File Extract (EO BMF): https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf\nIRS Annual Extract of Tax-Exempt Organization Financial Data: https://www.irs.gov/uac/soi-tax-stats-annual-extract-of-tax-exempt-organization-financial-data","api_version":2}
```

## Entities that could not be found

- Entry 6, "Zxqv Memorial Pancake Foundation": the search returned no organizations. The complete raw response, including the HTTP 404 status line the search endpoint answers an empty search with, is printed in section 6.
