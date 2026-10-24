# Carrier Watch: listing copy (draft)

**Status:** Draft for the owner's listing step, built for issue #332
(W2). This page posts nothing and changes no listing. The samples
below are real runs of `tools/standing_watch.py` against public
records, stored in this repo under `tools/examples/standing-watch/`
and named where they appear; nothing below is a mockup.

## Paste order

### 1. Name

Carrier Watch: weekly carrier monitoring with change alerts

### 2. Category

To confirm at listing.

### 3. Price

79 USD per month. That is the asking price the owner approved on
2026-10-24, for a watch of up to 50 carriers and 20 products. It is
an asking price; no buyer has paid it yet. No other price appears on
this page, and no plan estimate is a price.

### 4. Listing description

You hand over your carrier list once. Every week, Carrier Watch
rechecks every carrier on it against the public FMCSA record and
sends you one report: an alert for each carrier whose record
changed, naming the field, the old value, and the new value, with
the new state's source evidence printed under its source link, and
one line for each carrier that did not change.

The watch type covered today is carriers by USDOT number. Each
carrier is rechecked against three public sources: the FMCSA
Company Census File (authority state and safety rating as the
record shows them), the SAFER Company Snapshot (operating authority
status, USDOT status, rating), and FMCSA Licensing and Insurance
(the insurance record lines the source returns). Products are
watched in the same subscription, pinned by recall number once
known, up to the approved scope of 50 carriers and 20 products in
total.

The cycle is weekly. The first run is a baseline edition: the
fields that matter for every entry, with the complete raw response
for every query printed beneath its source link. Every run stores a
dated snapshot of its pulls, each response with its query URL, its
retrieval time, and its SHA-256, so any line in any report can be
checked against the pull it came from.

Nothing is scored or interpreted. Values are reported exactly as
the public record shows them.

### 5. What buyers get

- A baseline edition for the pinned list, fields and full source
  evidence for every entry.
- A weekly change report: change alerts with the field, the old
  value, the new value, and the new state's evidence; one line per
  unchanged entry with that run's source URLs, retrieval times, and
  response hashes.
- A one line note in a quiet week: the run happened, nothing
  changed.
- The dated snapshots behind every report, kept so any claim can be
  rechecked against the stored pull.

### 6. Sample report (a real live run)

The report below is the output of a real live run of
`tools/standing_watch.py`, run at build time for this page
(2026-10-24T14:28:10Z) against the previous day's stored snapshot.
The watchlist is the public demonstration list committed in this
repo (`tools/examples/standing-watch/watchlist.json`): three
carriers by USDOT number and four products, not a client list. The
previous snapshot is the run of 2026-10-23T21:57:45Z stored as
`snapshot-run2-2026-10-23.json` in the same folder; this run's own
snapshot is stored there as `snapshot-run3-2026-10-24.json`, and
this report as `report-run3-no-change-2026-10-24.md`. It was a
quiet cycle, which is the ordinary case, so the sample shows the no
change shape with its provenance lines:

```markdown
# Standing watch: change report

Watchlist: watchlist.json
Previous snapshot (UTC): 2026-10-23T21:57:45Z
This run (UTC): 2026-10-24T14:28:10Z

Entries checked: 7. Changed: 0. New: 0. No change: 7. No longer on the watchlist: 0.

## No change

- OLD DOMINION FREIGHT LINE INC (carrier, USDOT 90849): no change in the fields that matter.
  Source: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=90849&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef, retrieved 2026-10-24T14:28:10Z, response SHA-256 a68c02bb88904a8fd2e8f6e5328a04cfd457200f8141923b8fd66898d01d284f
  Source: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=90849, retrieved 2026-10-24T14:28:16Z, response SHA-256 8a1dd726ed11a6f306a660849df4d05bcb6a738a9170fb045df82d0fc57c5632
  Source: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=90849&s_prefix=MC&pv_vpath=LIVIEW, retrieved 2026-10-24T14:28:18Z, response SHA-256 aef4e298823dbeaa55104ad40377b997fd10c6ac4d2f7d8ae15e4c920c38a58b
- SCHNEIDER NATIONAL CARRIERS INC (carrier, USDOT 264184): no change in the fields that matter.
  Source: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=264184&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef, retrieved 2026-10-24T14:28:19Z, response SHA-256 5b35373c1c2c61a0758922d11954824e9ad856ef0720e93b370d9e66fbc1eefd
  Source: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=264184, retrieved 2026-10-24T14:28:20Z, response SHA-256 25343219064270f2ba354ac7f436240546284ad3373a534451e46513c4bbb61d
  Source: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=264184&s_prefix=MC&pv_vpath=LIVIEW, retrieved 2026-10-24T14:28:21Z, response SHA-256 6177e13476885eae0ad2ce593818425e04cd462c2d242accc4029dbd4cd7d54d
- XPO LOGISTICS FREIGHT INC (carrier, USDOT 241829): no change in the fields that matter.
  Source: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=241829&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef, retrieved 2026-10-24T14:28:22Z, response SHA-256 4871b2cd49d7ac9c25192108cedf943b9c39d35e7e7826d296f0082dc23f508e
  Source: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=241829, retrieved 2026-10-24T14:28:23Z, response SHA-256 5a1048ccae599352ce93134dbd8b2714d44a135dd3e091d497080600be7a4396
  Source: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=241829&s_prefix=MC&pv_vpath=LIVIEW, retrieved 2026-10-24T14:28:25Z, response SHA-256 842f3e263f9e635835c831c382c63e6154d37f5fbf7da5c06c79f5af729a7ded
- Peloton Tread+ (product): no change in the fields that matter.
  Source: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128, retrieved 2026-10-24T14:28:27Z, response SHA-256 b624c3df1188aa6d7cbfceae58c3917ec4177208a1b9c2030fb549158eaf346a
  Source: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Tread%2B, retrieved 2026-10-24T14:28:28Z, response SHA-256 f15c64faf7a6c075503353d25fe4382e3452ba77f561c0cbbe964c0e97062a2d
- Fisher-Price Rock 'n Play Sleeper (product): no change in the fields that matter.
  Source: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=19-105, retrieved 2026-10-24T14:28:29Z, response SHA-256 e53f95f62983d8dfcfb7557a0cd25ccaccc953fc342edcb852b1a41b9e3b51ca
- Vornado VH101 Personal Vortex electric space heaters (product): no change in the fields that matter.
  Source: https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=18-136, retrieved 2026-10-24T14:28:30Z, response SHA-256 ab5f6160a4d5204bff383aac377a8e3cbd27f2f3f2ea859d1d9c88cf2a2d1738
- Instant Pot Smart WiFi 6 Qt (product): no change in the fields that matter.
  Source: https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant+Pot+Smart+WiFi, retrieved 2026-10-24T14:28:31Z, response SHA-256 b2172029861883963971759432a254dc62bb83f7c13a7bfe8fe527cf1e34d49c

No entry changed in this run.
```

### 7. Sample alert

One changed entry, in the change report's real format: the field,
the old value, the new value, and the new state's source evidence
beneath its link. This alert is also a real run of the tool, made
for this page (2026-10-24T14:33:17Z). Its previous state is the
carrier's record as recorded in this repo's published carrier
vetting delivery of 2026-10-22 (stored as
`snapshot-alert-sample-prev-2026-10-22.json`); the full report and
this run's snapshot are stored as
`report-alert-sample-2026-10-24.md` and
`snapshot-alert-sample-2026-10-24.json` in
`tools/examples/standing-watch/`.

Read the change for what it is: the Licensing and Insurance source
answered this run with its verification challenge page instead of
the carrier's record, so the insurance lines changed to the two
empty field labels the challenge page carries, and the report says
so rather than stating an insurance position. One SAFER address
line also differs, in spacing only, between the two captures.

```markdown
# Standing watch: change report

Watchlist: watchlist.json
Previous snapshot (UTC): 2026-10-22T21:34:25Z
This run (UTC): 2026-10-24T14:33:17Z

Entries checked: 1. Changed: 1. New: 0. No change: 0. No longer on the watchlist: 0.

## Change alerts

### GARDA CL CENTRAL INC (carrier, USDOT 2046)

- safer.Physical Address:: changed from 2000 NW CORPORATE BLVD BOCA RATON, FL   33431-7304 to 2000 NW CORPORATE BLVD BOCA RATON, FL   33431-7304
- li.record_lines: changed from US DOT: 2046, Docket Number: MC00065419, Legal Name: GARDA CL CENTRAL, INC to Docket Number:, Legal Name:

Source evidence for the new state:
```

The evidence for the changed insurance field, from the same
report (the report also carries the Census and SAFER sections for
the new state; the complete report is the stored file named
above):

```markdown
### Licensing and Insurance

QUERY: n_dotno = 2046, s_prefix = MC, pv_vpath = LIVIEW (retrieved 2026-10-24T14:33:20Z). 2 record text lines found.

- As shown: Docket Number:
- As shown: Legal Name:

Source. FMCSA Licensing and Insurance carrier search, USDOT 2046
- Query URL: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=2046&s_prefix=MC&pv_vpath=LIVIEW
- Retrieved (UTC): 2026-10-24T14:33:20Z
```

The complete raw response printed under that link in the stored
report is the challenge page itself; its form carries the line
"Please enter the challenge question." That is the whole point of
the format: the alert shows what the source returned, not a
conclusion drawn from it.

### 8. What the watch does not cover

- The Licensing and Insurance source sometimes cannot be read
  automatically. On those days the report says so, rather than
  stating an insurance position.
- A product name search can miss a record that stands in the same
  database. That is why products are pinned to recall numbers once
  known, and tracked under name variants until then.
- The watch reports changes to the public record. It does not rate
  carriers, judge products, or recommend action; what a change
  means for your operation is your call.
- The cycle is weekly. A change between cycles is reported at the
  next cycle, not in real time.
