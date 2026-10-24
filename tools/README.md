# tools

Command line fetchers, one per source, that query a live public source
and print one Markdown section in the delivery format from
`AGENT-BRIEF.md`: the claim lines, the source link, and the complete
raw response printed verbatim directly beneath the link. Each run
records the exact query URL and the retrieval time in UTC. Standard
library Python 3 only, no package dependencies, and no keys stored
here. The CPSC fetcher also uses the system `curl` executable to
preserve the received HTTP status line and header order. Where a
source needs a free public key, the fetcher reads it from the
environment and its header comment says so.

| Source | Fetcher | Key |
| --- | --- | --- |
| CPSC SaferProducts recalls | `cpsc_recalls.py` | none needed |
| NHTSA recalls API | `nhtsa_recalls.py` | none needed |
| USAspending contract awards | `usaspending_awards.py` | none needed |
| CourtListener RECAP docket search | `courtlistener_recap.py` | none needed; optional `COURTLISTENER_TOKEN` from the environment |
| FMCSA carrier data (Census File, SAFER, Licensing and Insurance) | `fmcsa_carrier.py` | none needed |
| Google PageSpeed Insights (Lighthouse) | `pagespeed_snapshot.py` | free key from `PAGESPEED_API_KEY`; keyless requests are answered 429 (quota 0) |
| SEC EDGAR Form D filings | `edgar_formd.py` | none needed; an operator contact for the User-Agent is required (`--contact` or `EDGAR_CONTACT`) |
| ProPublica Nonprofit Explorer (IRS Form 990 extracts) | `propublica_nonprofits.py` | none needed |
| NHTSA vPIC VIN decode (DecodeVinValues) | `vin_decode.py` | none needed |
| Frankfurter exchange rates (API v1) | `exchange_rate_check.py` | none needed |
| NHTSA safety file: ratings, recalls, complaints | `safety_file.py` | none needed |
| EPA ECHO facility compliance screen | `epa_screen.py` | none needed |
| Brand name checks: RDAP domains, X / Instagram / TikTok handles, iTunes Search (trademarks not covered) | `brand_name_checker.py` | none needed |
| Weekly brief: watchlist Form D filings and NAICS filtered contract awards for a seven day window (docs/weekly-brief.md) | `weekly_brief.py` | EDGAR contact |
| OFAC SDN list name check, primary names and aliases (docs/ofac-sdn-check.md) | `ofac_sdn_check.py` | none needed |
| GitHub repository check, keyless: stars, license, last push, archived (docs/mcpize-tools/github_repo_check.md) | `github_repo_check.py` | none needed; 60 requests per hour unauthenticated |
| Meta tag check: title, description and Open Graph tags present or missing on a page (docs/mcpize-tools/meta_tag_check.md) | `meta_tag_check.py` | none needed; the source is the page itself |
| ClinicalTrials.gov API v2 studies search: trial count and top trials with status (docs/mcpize-tools/clinical_trial_check.md) | `clinical_trial_check.py` | none needed |
| FEMA NFHL flood zone check for a point or a US address (Census Geocoder), screening only (docs/mcpize-tools/flood_check.md) | `flood_check.py` | none needed |
| openFDA food and device enforcement recall search (docs/mcpize-tools/fda_recall_check.md) | `fda_recall_check.py` | none needed; keyless limits 240 per minute and 1,000 per day per IP address |
| HHS OIG LEIE exclusion screen, persons and entities (docs/mcpize-tools/oig_screen.md) | `oig_screen.py` | none needed |

Not a fetcher: `pregate.py` is the offline review pre gate (secrets scan,
honesty lint, fixture provenance check) from `REVIEW.md`. See
[`pregate-README.md`](pregate-README.md).

Also not a fetcher: `standing_watch.py` rechecks a buyer watchlist
through the FMCSA and CPSC fetchers, stores a dated snapshot of the
fields that matter per entry, diffs it against the previous snapshot,
and prints a baseline or change report. See
[`../docs/standing-watch.md`](../docs/standing-watch.md) for the
watchlist format and report shapes, and
[`examples/standing-watch/`](examples/standing-watch/) for a live
demo run.

## cpsc_recalls.py

Run from the repository root with Python and curl installed. No API key,
account, wallet, or Python package installation is needed. curl is used to
retain the received HTTP status line and header order alongside the complete
response body. Its default config is disabled; redirects are not followed.

```sh
python3 tools/cpsc_recalls.py 'Instant Pot'
python3 tools/cpsc_recalls.py 'Instant Pot Smart WiFi' \
  --exact-name 'Instant Pot Smart WiFi' --near-product 'Instant Pot'
python3 tools/cpsc_recalls.py --recall-title Peloton
python3 tools/cpsc_recalls.py --recall-number 21-128
```

One query shape per run: a product name (`ProductName` search, the
default), `--recall-title` (`RecallTitle` search, the shape of the
published delivery's Peloton query), or `--recall-number` (`RecallNumber`
detail query, the shape of the delivery's per recall detail queries).
`--near-product` searches are always `ProductName` searches.

These search terms come from the published recall delivery.
Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/5be7e2905c9b8253793ce45455f4b698f38919f4/deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md>
```text
## Subject 3: Instant Pot Smart WiFi 6 Qt
```

The broader search term is recorded in that delivery too.
Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/5be7e2905c9b8253793ce45455f4b698f38919f4/deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md>
```text
Other Instant Pot records in the same database, checked and excluded because they name different models: a ProductName = "Instant Pot" query returned 1 record (retrieved 2026-10-22T03:29:56Z), record 15-741 below, and a detail query for record 18-110 was run as well (retrieved 2026-10-22T03:29:25Z). Neither record names the Smart WiFi, and neither names a 6 Qt model.
```

The CLI emits a single Markdown section on stdout. Every query has its exact
GET URL, retrieval time in UTC, result claims, one claim block per returned
record, the source link, and the complete curl response capture immediately
beneath the link. A claim block (`#### Recall NN-NNN`) gives the recall
number, announcement date, title, product, hazard, remedy, units, remedy
options and CPSC page, each value as shown in the response (JSON quoted and
Markdown escaped); a field the record does not carry is printed as "not
present in the API record", never filled in. When a record's remedy text
repeats its hazard text word for word, as the published delivery found for
recall 21-128, the block carries a note to read the remedy from the CPSC
page instead. The body is not pretty printed
or reordered, including for an empty array. HTTP headers and body retain their
original line endings; the Markdown closing fence adds a separator newline
when the captured body has none. curl removes transfer framing, such as chunk
sizes; this is an HTTP response capture, not a packet trace.

By default records are candidates, not verified model matches. `--exact-name`
keeps records where any product name equals the supplied name, ignoring case
and whitespace. Other records are listed as checked and excluded with the
source names and this narrow reason. `--near-product` adds another search and
requires `--exact-name`; it can be repeated. These are name comparisons only:
alternate names and actual model applicability require reviewer judgment.
An empty result is never described as proof that a product is safe. The tool
does not claim to search other databases or resolve hazard/remedy discrepancies.

Transport, HTTP, JSON, and required-field errors exit unsuccessfully, with a
diagnostic on stderr and no partial report on stdout. No failed query becomes
an empty-result claim. Review a generated report before using it in a delivery.

### Verification

```sh
python3 -m unittest discover -s tools/tests -v
CPSC_LIVE=1 python3 -m unittest discover -s tools/tests -v
```

Offline tests use the unmodified public HTTP captures in `tests/fixtures/`.
`provenance.json` records each source URL, actual UTC retrieval time, and SHA-256
digest. Malformed-response tests deliberately corrupt captures only to verify
error handling. The optional live tests invoke the CLI against CPSC: an empty query and a
broader query with a checked/excluded name, then a `--recall-title` and a
`--recall-number` query; none needs a fixture or mocked transport. Live results can change; a failure requires review,
not replacement with invented data.

## nhtsa_recalls.py

```
python3 tools/nhtsa_recalls.py --subject "Hyundai Elantra 2021" \
  --make Hyundai --model Elantra --model-year 2021
python3 tools/nhtsa_recalls.py --subject "Hyundai Elantra 2021" \
  --make Hyundai --model Elantra --model-year 2021 \
  --exclude 21V796000="replaced by 22V354000, which is listed" --pretty
python3 tools/nhtsa_recalls.py --endpoint recallsByVehicle \
  --param make=Hyundai --param model=Elantra --param modelYear=2021
```

Query fields: `--make`, `--model` and `--model-year`, which together
form the `recallsByVehicle` query, and `--param KEY=VALUE` for any
other field. The query URL is built in that order with spaces encoded
as `%20`, so it reproduces the URL recorded in the published recall
delivery byte for byte. `recallsByVehicle` is the one endpoint checked
against a recorded live response (source S24 in
`deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md`).
`--endpoint NAME` reaches any other path under
`https://api.nhtsa.gov/recalls/` the API accepts; the response is
printed verbatim whatever its shape, and campaign blocks are rendered
only for fields that are present.

Each campaign block gives the campaign number, manufacturer, report
received date as shown with its long form in brackets, product
(model year, make, model) and component, summary, hazard
(Consequence), remedy, notes, the parkIt / parkOutSide /
overTheAirUpdate flags, and units. The recorded responses carry no
unit count, so units are stated as not shown; if a record ever
carries a field whose name contains "unit", it is printed as shown
instead. Campaigns are kept in response order. If the response's own
`Count` field differs from the number of entries in its results
array, the QUERY line says so.

An empty result is proven, not asserted: the section prints the
complete raw HTTP response transcript (status line, headers in order,
blank line, body) for the exact query. Every query prints that
transcript, so the raw excerpt is always directly beneath the source
link.

Near matches the operator has checked and ruled out are listed with
`--exclude NNVNNNNNN="reason"`, repeatable. The campaign is printed
under "Checked and excluded" with the reason, in the same block format
as a match. The tool refuses an exclusion for a campaign number that is
not in the response, so an exclusion can never describe a record that
was not fetched. The tool never decides relevance itself.

`--pretty` adds one pretty printed JSON excerpt per campaign after the
transcript, in response order, values unchanged, the way `deliveries/`
shows records.


A per-tool copy of this section is also kept in
[`nhtsa-README.md`](nhtsa-README.md).

## usaspending_awards.py

```sh
python3 tools/usaspending_awards.py --recipient Boeing --limit 2
python3 tools/usaspending_awards.py --recipient Boeing --naics 336411 --limit 2
python3 tools/usaspending_awards.py --recipient 'Instant Pot Smart WiFi' --limit 2
```

The USAspending fetcher searches one requested page of prime contract
awards by recipient and/or NAICS prefix, with optional start and end
dates supplied together. It records the exact POST body and UTC
retrieval time, prints source fields and reviewer-supplied near-match
exclusions, and places the complete unmodified JSON response body
immediately beneath its source link. An empty results array retains
the entire response body, including pagination and messages, so the
empty result is proven rather than asserted. HTTP headers are not
collected or published because public responses can include session
cookies.

Each run reports one requested page, not a complete award universe.
Recipient search covers name, UEI and DUNS and is not an exact
legal-entity check. Exclusions remain reviewer decisions: the tool
checks that an excluded identifier is on the fetched page and does
not decide relevance or verify the reason. Full usage, evidence and
scope notes are in [`usaspending-README.md`](usaspending-README.md),
with rendered captured examples in
[`examples/usaspending.md`](examples/usaspending.md).

## fmcsa_carrier.py

```sh
python3 tools/fmcsa_carrier.py --subject "GARDA CL CENTRAL INC" --usdot 2046
python3 tools/fmcsa_carrier.py --usdot 2046 --source census --source safer
python3 tools/fmcsa_carrier.py --name "CHENEY BROTHERS" \
  --exclude 123456="different state; not the subject carrier"
```

One carrier per run, by USDOT number. Three public FMCSA sources are
queried in order and each gets its own sub-section: claim lines, then
the source link with the exact query URL and UTC retrieval time, then
the complete raw HTTP response transcript directly beneath it.

1. FMCSA Company Census File (DOT open data portal, dataset
   az4n-8mr2, JSON), with the same `$select` field list the published
   carrier vetting delivery used. The query URL reproduces the one
   recorded there byte for byte.
   Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/aaacd5e/deliveries/carrier-vetting-3b4e7143-c7e2-4fda-92f4-c19a99bbd98f.md>
   ```text
   https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=2046&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef
   ```
   Every selected field is printed as shown or marked not present in
   the record.
2. FMCSA SAFER Company Snapshot (HTML). The query URL is the recorded
   one. The claim lines are the text lines that follow each labelled
   field in the page text (Entity Type, USDOT Status, Out of Service
   Date, USDOT Number, MCS-150 Form Date and Mileage, Operating
   Authority Status, MC/MX/FF Number(s), Legal Name, DBA Name, Physical
   Address, Phone, Power Units, Non-CMV Units, Drivers, Total
   Inspections, Rating Date, Review Date, Rating), the way the delivery
   quotes them. A label that is not in the page text is said to be not
   found; a blank field is reported as none shown. The inspection, out
   of service and crash tables are not parsed; they are read from the
   complete page printed beneath the source link.
3. FMCSA Licensing and Insurance carrier search (HTML), using the form
   fields the delivery recorded (`n_dotno`, `s_prefix=MC`,
   `pv_vpath=LIVIEW`) as a GET query. The delivery records that this
   site presents a verification challenge to automated reads.
   Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/aaacd5e/deliveries/carrier-vetting-3b4e7143-c7e2-4fda-92f4-c19a99bbd98f.md>
   ```text
   Retrieval note: SAFER and the Census API answered direct automated reads. The Licensing and Insurance site presents a verification challenge to automated reads, so its records were read in a live browser session at the UTC times shown; the excerpts under its entries are the record text as displayed in that session.
   ```
   The tool prints whatever the site returns in full. When no record
   text lines (`US DOT:`, `Docket Number:`, `Legal Name:`) are found in
   it, the section says so and claims nothing from it.

`--name TEXT` runs a Census File full text search (`$q`) instead and
lists every returned record as a candidate, with the operator choosing
the subject carrier; `--exclude USDOT="reason"` lists a candidate as
checked and excluded with the reason and is refused for a USDOT number
not in the response. The `$q` query shape and the GET form of the
Licensing and Insurance request have not been checked against a
recorded live response; whatever they return is printed verbatim.

A transport failure (no connection, blocked host, timeout) prints
nothing on stdout and exits 2, so a failed fetch is never shown as an
empty result. An HTTP error status is captured, printed in full, and
the claim lines say the fields are not determinable from it. Bodies
that are not valid UTF-8 are decoded as Latin-1, which keeps every
byte, and the source block says so. No key is needed or read.

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_fmcsa_carrier.py' -v
```

The tests need no network. The fixtures are verbatim copies of sources
S1, S2, S3, S8, S9 and S35 of the published carrier vetting delivery,
with their delivery line ranges named in the test file. Two things in
the tests are labelled as not recordings: the Census excerpt gets the
object braces the delivery omitted so it parses, values unchanged, and
the HTML parser runs on a harness that wraps each recorded text line in
a table row, because no page HTML was recorded. The fetch tests run
against a local server on 127.0.0.1.

## courtlistener_recap.py

```sh
python3 tools/courtlistener_recap.py --subject "Jabil Inc." \
  --party "Jabil Inc." --party "Jabil Inc" --party "Jabil" --filed-after 2021-10-22
python3 tools/courtlistener_recap.py --subject "Jabil Inc." --party "Jabil Inc." \
  --list 10 --docket-details \
  --exclude 69574962="the subject is a listed party but on neither side of the caption"
```

One subject company per run. Each `--party` value is a party name
variant searched on the CourtListener search API (type `d`, federal
dockets from the RECAP archive) with `q=party:("<variant>")`,
`filed_after` (default five years before today) and `order_by=dateFiled
desc`, in that parameter order, so the first command reproduces the
query URL recorded in the published litigation screen byte for byte.
Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/aaacd5e/deliveries/litigation-screen-5c567ad5-77c5-4ccc-a207-a1acc743b3bd.md>
```text
https://www.courtlistener.com/api/rest/v4/search/?type=d&q=party%3A%28%22Jabil+Inc.%22%29&filed_after=2021-10-22&order_by=dateFiled+desc
```

The section opens with the fixed scope line (index level only, not a
legal opinion) and the method line, then:

- **Searches:** one line per variant with the exact query fields, the
  `count` the API returned, how many results the first page held,
  whether a next page cursor was returned (it is never followed), and
  the UTC retrieval time. Counts are reported per variant and never
  merged, because shorter forms also match other parties.
- **Cases:** a table of the first `--list` results (default 10) of the
  first variant's search, in the order returned, with docket number,
  court, case name, date filed, nature of suit, cause, role, status and
  CourtListener docket ID as shown. Role is the caption rule the
  delivery used, applied mechanically to the first variant's name
  ignoring case and punctuation: before " v. " is plaintiff, after it
  is defendant, a listed party on neither side is other; the rule is
  printed with the table. Status is open when `dateTerminated` is null,
  else the date shown. An empty nature of suit or cause is "not shown".
  `--exclude DOCKET_ID="reason"` moves a listed result to a checked and
  excluded table with the operator's reason; it is refused for a docket
  ID that is not among the listed results.
- **Totals:** role and status counts with their arithmetic, and the
  API's count for the first variant.
- **Sources:** every search, and with `--docket-details` every listed
  case's docket record lookup (`q=docket_id:N`, the lookup the delivery
  recorded), each with its query URL, UTC retrieval time, and the
  complete raw HTTP response transcript directly beneath. An empty
  result is proven by that transcript.

No key is needed; the published delivery used none. If
`COURTLISTENER_TOKEN` is set in the environment it is sent as the
Authorization header to lift the anonymous rate limit; it is never
printed or written. A transport failure prints nothing on stdout and
exits 2. An HTTP error status is captured and printed in full and the
claim lines say the count is not determinable from it.

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_courtlistener_recap.py' -v
```

The tests need no network. The fixtures are verbatim copies of sources
Q1, Q5, D1, D5 and D9 of the published litigation screen, with their
delivery line ranges named in the test file; the delivery prints
contiguous slices of each JSON response, and the tests close each slice
syntactically where it ends, values unchanged, as the file explains.
The fetch tests run against a local server on 127.0.0.1.

## pagespeed_snapshot.py

```sh
python3 tools/pagespeed_snapshot.py https://example.com/
python3 tools/pagespeed_snapshot.py --strategy desktop https://example.com/ https://example.com/about
PAGESPEED_API_KEY=... python3 tools/pagespeed_snapshot.py --subject "Example site" \
  https://example.com/ --exclude https://example.com/about="redirects to a login page; not a public page"
```

Catalog service 7 tooling, matching the delivery shape in
[`templates/service-07-pagespeed-snapshot.md`](../templates/service-07-pagespeed-snapshot.md).
Up to five page URLs per run; each is measured once with the Google
PageSpeed Insights API (v5 `runPagespeed`, which runs Lighthouse against
the live page) with `strategy` (default `mobile`) and the four categories
`performance`, `accessibility`, `best-practices`, `seo` as request
parameters. The output opens with a fixed scope line (a snapshot of one
run at a stated time, not a permanent grade), then one section per page:
the QUERY line with the exact request, strategy, UTC retrieval time and
HTTP status; for a 200 JSON response the four category scores and the
three lab metrics (Largest Contentful Paint, Cumulative Layout Shift,
Total Blocking Time) as shown, each with the field path it was read from
under `lighthouseResult`, and `not shown` for any path absent from the
response. A page the API cannot measure keeps its section: the status,
the error fields as shown, and its complete raw response. The Sources
section prints every request's complete raw HTTP transcript directly
beneath its request URL.

Key. A keyless request from this environment was answered live by the API
with HTTP 429 and a daily quota of zero for the anonymous consumer; the
capture is the fixture below.
Source: [`tests/fixtures/pagespeed/keyless-429.http`](tests/fixtures/pagespeed/keyless-429.http), provenance in [`tests/fixtures/pagespeed/provenance.json`](tests/fixtures/pagespeed/provenance.json)
```text
HTTP/1.1 429 Too Many Requests
```
```text
    "message": "Quota exceeded for quota metric 'Queries' and limit 'Queries per day' of service 'pagespeedonline.googleapis.com' for consumer 'project_number:583797351490'.",
```
```text
          "quota_limit_value": "0"
```
So a real measurement needs a free API key. If `PAGESPEED_API_KEY` is set
in the environment its value is sent as the `key` parameter. The value is
never printed: the recorded request URL shows
`key=<redacted, supplied from the environment>`, and if the value appears
anywhere in a response it is replaced by `[key value redacted]` and the
source block says how many times. No key is written to any file here.

`--exclude URL="reason"` measures the page like any other but lists it
under "Checked and excluded" with the operator's reason; it is refused for
a URL that is not among the pages given. The tool never decides
relevance. A transport failure prints nothing on stdout and exits 2.

Not checked from this environment: a successful (keyed) response, so the
field paths the tool reads (`lighthouseResult.categories.<name>.score`,
`lighthouseResult.audits.<id>.displayValue`, `.numericValue`,
`.numericUnit`) follow the Lighthouse result shape and have not been
confirmed against a live 200 body; a path that is absent prints
`not shown`, and the full response is always printed.

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_pagespeed_snapshot.py' -v
```

The tests need no network. The error path runs on the real keyless
capture, whose SHA-256 is checked against its provenance. The success
path parser runs on a hand built structure that is labelled synthetic at
the place it appears and carries placeholder values, because no
successful live response was available. The fetch tests run against a
local server on 127.0.0.1.

## vin_decode.py

```sh
python3 tools/vin_decode.py 1HGCM82633A004352
python3 tools/vin_decode.py "5UXWX7C5*BA" --model-year 2011 --pretty
```

Tool factory wave 1, issue #161. One VIN per run, decoded once with the
NHTSA vPIC `DecodeVinValues` endpoint (flat format, `format=json`, plus
`modelyear` when `--model-year` is given), keyless, through the capture
path of `nhtsa_recalls.py`. The section shows the QUERY line, vPIC's own
ErrorCode and ErrorText quoted as shown, the vehicle as shown (model year,
make, model, trim), then every field with a value in response order. It
counts the empty fields and quotes the response's own Message about
missing values. When make, model and model year are all empty it says no
vehicle was decoded, and the complete raw HTTP response transcript
directly beneath the source link proves it. The tool checks only that the
VIN is 1 to 17 letters, digits or `*`; validity is vPIC's answer. A
transport failure prints nothing on stdout and exits 2. Docs page:
[`docs/mcpize-tools/vin_decode_check.md`](../docs/mcpize-tools/vin_decode_check.md).

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_vin_decode.py' -v
```

The tests need no network. They run on five real vPIC response bodies
(clean decode, bad check digit, the vPIC page's partial VIN example and
its 9th character variant, and an all zeros VIN that decodes nothing).
The coordinator captured them under Option B on issue #161, because this
container cannot reach vpic.nhtsa.dot.gov. Their URLs, sizes and SHA-256
are in `tests/fixtures/vpic/provenance.json`, and the hashes are checked.

## exchange_rate_check.py

```sh
python3 tools/exchange_rate_check.py USD EUR
python3 tools/exchange_rate_check.py USD EUR --amount 100
python3 tools/exchange_rate_check.py USD EUR --date 2024-01-06
```

Tool factory wave 1, issue #168. One currency pair per run, looked up
once with the Frankfurter API v1 (`/v1/latest`, or `/v1/<date>`, with
`base`, `symbols` and an optional `amount`), keyless, through the capture
path of `nhtsa_recalls.py`. The section shows the QUERY line with the
HTTP status, then the RATE line: the response's own amount, base, rate
and date, with numbers printed as the body writes them. With an amount
the converted figure is the API's own, and the tool does no arithmetic.
When the response's date differs from the date asked, both are stated.
A pair the API has no rate for (the recorded USD to XYZ answer is HTTP
404, `{"message":"not found"}`) is reported as no rate returned, quoting
the body's message, and the complete raw HTTP response transcript
directly beneath the source link proves it. A transport failure prints
nothing on stdout and exits 2. The v1 documentation says v1 is deprecated
in favor of v2 but will continue to work. Docs page:
[`docs/mcpize-tools/exchange_rate_check.md`](../docs/mcpize-tools/exchange_rate_check.md).

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_exchange_rate_check.py' -v
```

The tests need no network. They run on five real, keyless Frankfurter
responses: latest, latest with an amount, a weekend date, an unknown
code, and the currencies list. The coordinator captured them under
Option B on issue #168, because this container cannot reach
api.frankfurter.dev. Their URLs, body sizes and SHA-256 hashes are in
`tests/fixtures/frankfurter/provenance.json`, and the hashes are checked.

## safety_file.py

```sh
python3 tools/safety_file.py --make Hyundai --model Elantra --year 2021
```

Tool factory wave 2, issue #176. One combined safety file for a make,
model and model year from three keyless NHTSA APIs on api.nhtsa.gov,
fetched through the capture path of `nhtsa_recalls.py`. The safety
ratings come from the variants list and then each variant's ratings
(at most six variants are fetched). The recalls come from
recallsByVehicle and the complaints from complaintsByVehicle. Each
section states only what its own response shows, and its complete raw
HTTP transcript sits directly beneath its own source link. The recalls
and complaints sections state the response's own count field and the
records in its results array. The complaints section adds this tool's
own counts of the records shown (crash, fire, injuries, deaths), labelled
as such. A cross check shows the counts the ratings record carries
beside the records returned, neither adjusted.

The HTTP status is checked first, because these endpoints can answer 400
or 500 with a body that still reads "Results returned successfully". Any
non-200 status, or a body without the expected results array, is a
source failure: nothing is printed on stdout, the failed sources are
named on stderr with their query, status and body, and the exit status
is 2. A 200 with empty results is an empty result, proven by its
transcript. Docs page:
[`docs/mcpize-tools/safety_file.md`](../docs/mcpize-tools/safety_file.md).

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_safety_file.py' -v
```

The tests need no network. They run on real, keyless NHTSA responses
captured by the coordinator under Option B on issue #176, because this
container cannot reach api.nhtsa.gov. Their URLs, body sizes and SHA-256
hashes are in `tests/fixtures/nhtsa-safety/provenance.json`, and the
hashes are checked.

## epa_screen.py

```sh
python3 tools/epa_screen.py --name "BAYTOWN OLEFINS" --city BAYTOWN --state TX
python3 tools/epa_screen.py --name "BAYTOWN OLEFINS" --state TX --registry-id 110000463178
```

Tool factory wave 2, issue #178. It searches the EPA ECHO facility search
web service by facility name and state (city optional), keyless, through
the capture path of `nhtsa_recalls.py`, in the two steps the coordinator's
captures show: `get_facilities` for the summary and QueryID, then `get_qid`
for the rows. The answer quotes each row's `FacComplianceStatus`,
`FacSNCFlg` and `FacQtrsWithNC` as shown. `--registry-id` selects one row
from the results; no single-facility route is verified. QueryRows `"0"`
is an empty result, proven by its transcript and never called clean.
Any non-200 answer, or an `Error` in `Results` (ECHO also answers HTTP 200
with one), is a source failure: nothing is printed on stdout, and the exit
status is 2. Docs page:
[`docs/mcpize-tools/epa_screen.md`](../docs/mcpize-tools/epa_screen.md).

### Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_epa_screen.py' -v
```

The tests need no network. They run on eight real, keyless ECHO responses
captured by the coordinator under Option B on issue #178, because this
container cannot reach echodata.epa.gov. They are posted byte for byte and
saved as curl output with CRLF line ends, and the tests read them as
bytes. Their URLs, sizes and SHA-256 hashes are in
`tests/fixtures/epa-echo/provenance.json`, and the hashes are checked.

## edgar_formd.py

Usage examples; the contact shown is a placeholder, give your own name and address:

```sh
python3 tools/edgar_formd.py --contact "Your Name you@example.com" --cik 2156237
python3 tools/edgar_formd.py --contact "Your Name you@example.com" --issuer "8VC DSS III"
EDGAR_CONTACT="Your Name you@example.com" python3 tools/edgar_formd.py --cik 320193
python3 tools/edgar_formd.py --cik 1801756 --max-filings 2 \
  --exclude 0001801756-23-000001="older amendment superseded by the one listed above"
```

Given a CIK or an issuer name, the fetcher queries the public EDGAR
APIs and prints one Markdown section: with `--issuer`, the EDGAR company
search (exactly one match proceeds, several are listed with their CIKs
for the operator to pick with `--cik`, none is proven by the raw
response); then the submissions index for the CIK, where Form D filings
are the entries whose form is `D` or `D/A`; then, for each Form D filing
up to `--max-filings`, the filing's `primary_doc.xml` parsed into one
claim block: issuer name and CIK, form type and filing date (from the
index), date of first sale, total offering amount, total amount sold,
total remaining, investors, industry group, federal exemptions, and the
filing index page link, each value as shown. A value the XML does not
carry prints as "not present in the filing XML". Every request prints
its exact URL, UTC retrieval time, source link, and complete raw HTTP
transcript directly beneath the link. Zero Form D filings is proven by
the submissions transcript; when the index names older index files
beyond its recent window, the section says they were not queried.

Exclusions are operator supplied with `--exclude ACCESSION=reason`
(repeatable), rendered as "Checked and excluded" on that filing's
block; an accession not in the submissions response is refused. The tool
never decides relevance or picks an issuer.

Fair access is enforced, not optional. The SEC states the limit and the
user agent it expects.
Source: <https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data> (retrieved 2026-10-23T03:41:45Z, HTTP 200)
```html
	<li><strong>Current max request rate: 10 requests/second.</strong></li>
```
```html
			<p>Sample Company Name AdminContact@&lt;sample company domain&gt;.com</p>
```
The tool sends `User-Agent: tiny-ledger edgar_formd.py <contact>` and
refuses to run without a contact that contains an email address. It
paces requests to at most one every 0.2 seconds (5 per second). The
contact must be the plain "Name you@example.com" form (a placeholder; use
your own address): on 2026-10-23
EDGAR answered 403 "Your Request Originates from an Undeclared
Automated Tool" to a contact carrying a URL in parentheses (captured as
`tests/fixtures/edgar/undeclared-403.http`), so URLs, parentheses and
brackets are refused up front.

Any non-200 answer, non-JSON index, or malformed XML stops the run with
a diagnostic on stderr and no report on stdout.

### Verification

The second command runs the opt-in live test; the contact shown is a placeholder, give your own.

```sh
python3 -m unittest discover -s tools/tests -v
EDGAR_LIVE=1 EDGAR_CONTACT="Your Name you@example.com" python3 -m unittest discover -s tools/tests -v
```

Offline tests use the unmodified captures in `tests/fixtures/edgar/`;
`provenance.json` there records each URL, UTC retrieval time, status
line and SHA-256 digest. The optional live test runs the CLI against
EDGAR for one CIK and needs a real contact in `EDGAR_CONTACT`.

## Tests

All six suites live in `tools/tests/` and run offline with one
discovery command:

```
python3 -m unittest discover -s tools/tests -v
```

The tests need no network. Their fixtures are verbatim copies of
responses recorded in `deliveries/` or captured public responses with
recorded provenance, and the fetch tests run against a local server
on 127.0.0.1.

## propublica_nonprofits.py

```sh
python3 tools/propublica_nonprofits.py --ein 53-0196605
python3 tools/propublica_nonprofits.py --name 'American Red Cross' --ein 530196605 \
  --exclude 204801016="separate local club, not the national organization"
```

Nonprofit diligence from the ProPublica Nonprofit Explorer API v2. These
inputs are the ones captured live for the tests. Per EIN: the legal name,
EIN, city and state from the `organization` block, then `tax_prd`,
`totrevenue`, `totfuncexpns`, `totassetsend` and `totliabend` from the
`filings_with_data` entry with the highest `tax_prd`. Each claim is followed
by its source link and the exact `"key":value` text cut from the response
body. A later filing listed only under `filings_without_data` is disclosed,
so the figures are never presented as coming from the latest filing when
they do not. `organization.tax_period` is printed with a label and no figure
is taken from it. The response states no unit, so values are printed as
shown.

A `--name` search lists every result as shown. The tool does not choose the
subject. It examines only the EINs given with `--ein` and any result whose
name equals the search text, ignoring case and spacing. `--exclude
EIN="reason"` lists a checked-and-excluded result with the operator's
reason, and an exclusion for an EIN not in the response is refused. An empty
search prints the complete raw response. Any transport failure, non-200
status, or body that is not the expected JSON prints nothing on stdout and
exits 2.

```sh
python3 -m unittest discover -s tools/tests -p 'test_propublica_nonprofits.py' -v
PROPUBLICA_LIVE=1 python3 -m unittest discover -s tools/tests -p 'test_propublica_nonprofits.py' -v
```

The fixtures in `tests/fixtures/propublica/` are real response bodies. The
coordinator captured them live and posted them verbatim on issue #47; their
URLs, times and SHA-256 hashes are in `provenance.json`. Only the bodies
were captured, not the status lines or headers.

## nonprofit_pack.py

The batch form of the ProPublica fetcher: given a list of nonprofit names or
EINs, it resolves each entry against the same API and assembles one combined
Markdown pack: a summary table up front, one evidence section per entry
rendered by `propublica_nonprofits.py` itself, and a closing list of the
entities that could not be found. Resolution keeps the single fetcher's
discipline: an EIN is fetched directly, a name is examined only on an exact
name match, and an entity listed twice is examined once. The one behavior
that is the runner's alone: the search endpoint answers an empty search
with HTTP 404 and the usual search body carrying `total_results` 0 and an
empty `organizations` array (observed live on 2026-10-23), and the runner
reads that one shape as an empty result and prints the complete raw
response as the not found proof; the single fetcher still fails closed on
any non-200, and every other failure fails the whole run closed. The design
note is `docs/nonprofit-pack.md`.

```bash
python3 tools/nonprofit_pack.py --list tools/examples/nonprofit-pack-list.txt
python3 tools/nonprofit_pack.py --name "Feeding America" --ein 53-0196605
```

`tools/examples/nonprofit-pack.md` is a real demo pack from a live run on
2026-10-23 over `tools/examples/nonprofit-pack-list.txt`: five well known
nonprofits, each resolved by exact name, plus one name that is not found.
Tests: `tests/test_nonprofit_pack.py`, offline against the captures in
`tests/fixtures/propublica/` (the Feeding America and empty search captures
were taken live by H5 on 2026-10-23 for issue #149; provenance in
`provenance.json`), with the live demo list check under the same
`PROPUBLICA_LIVE=1` gate as the single fetcher's tests.

## brand_name_checker.py

```sh
python3 tools/brand_name_checker.py Nike
python3 tools/brand_name_checker.py zqxflorp --tlds com,io --platforms x,instagram,tiktok --variations 3
```

One report per candidate name, containing a domains table, a handles
table, App Store matches and a trademark section. Every row carries its
check time in UTC, and the evidence follows each table: claim, source link,
then the status line and headers (Set-Cookie values withheld) and any body
the verdict rests on.

How each check is judged:
- **Domains:** RDAP via rdap.org, following redirects. 200 means
  registered, 404 means no registration found (the 404 body is never read),
  and anything else means could not confirm.
- **X:** 200 means taken, 404 means no account found.
- **Instagram and TikTok:** a 200 is a login wall, so it means could not
  confirm, never available. Only a hard 404 means no account found.
- **App Store:** the iTunes Search API, filtered to exact name matches. The
  exact-name comparison takes the title part before the first `:`, ` - ` or
  ` | `, compared on letters and digits only.
- **Google Play:** out of scope, because it has no official public search
  API.
- **Trademarks:** not covered. No working trademark source has been
  captured, so the report names the USPTO database it would search and
  states no mark. The section comes from `uspto_trademarks.py`, which reads
  an optional key from `USPTO_API_KEY` only and keeps this wording until a
  documented name search and a live keyed run exist; see
  `uspto_trademarks-README.md` (issue #125) for the owner step sheet.

**Offline dry run** (issue #137): `python3 tools/brand_check_dryrun.py` runs
every leg against recorded responses, with no network. The responses are
the issue #51 captures and status records, plus SYNTHETIC bodies labelled
inside their files. It covers three cases (taken, free and mixed) and
prints each leg's expected and actual verdict. It exits 0 only when every
verdict matches. `--report` also prints the rendered reports. The cases
are in `tests/fixtures/brandcheck-dryrun/cases.json`.

Variations appear only with `--variations` and are listed only after every
requested domain and X answer 404. A failed request is "could not confirm",
never available. The tool only sends GET requests; it never registers or
reserves a name.

```sh
python3 -m unittest discover -s tools/tests -p 'test_brand_name_checker.py' -v
```

The fixtures in `tests/fixtures/brandcheck/` come from the coordinator's
live captures on issue #51:
- The RDAP 200 body for nike.com and two iTunes Search bodies, hash checked
  against `provenance.json`.
- `status-captures.json`, a transcription of the recorded statuses for the
  status-only checks.

## domain_trust_check.py

One domain in, its A and MX records, SPF record and ending policy,
DMARC record and policy, and its HTTPS answer and redirects out. DNS
comes from the Cloudflare DNS over HTTPS JSON API (keyless), the HTTPS
leg from the site itself. Every response is printed in full beneath its
request URL. Full documentation, with the source, the empty and fail
closed cases, and the shelf price: [`domain-trust-check-README.md`](domain-trust-check-README.md).

```sh
python3 tools/domain_trust_check.py example.com   # the reserved example domain, as the example input
```

## app_lookup_check.py

An app name in, the App Store apps the iTunes Search API returns for it
out: seller, rating as shown, store link, and whether the name matches
exactly. Every response is printed in full beneath its request URL. The
search matches loosely, so "none found" means zero exact name matches.
Full documentation, with the source, the failures and the shelf price:
[`app-lookup-check-README.md`](app-lookup-check-README.md).

```sh
python3 tools/app_lookup_check.py "Nike"   # example app name
```

## clinical_trial_check.py

A company, drug, or condition in, the ClinicalTrials.gov trial count
and the top trials with status out: NCTId, brief title, lead sponsor,
conditions, and phases, each as shown, with the complete raw response
printed beneath the source link. An empty result is proven by its raw
response. Full documentation, with the source, the failures and the
shelf price:
[`../docs/mcpize-tools/clinical_trial_check.md`](../docs/mcpize-tools/clinical_trial_check.md).

```sh
python3 tools/clinical_trial_check.py "elivaldogene"   # example drug name
```

## Cross agent offline integration pass (`tests/test_agents_integration.py`)

Issue #100. It runs every agent in `agents/` plus the brand checker through
the offline entry point its README documents, in process, on the agent's
committed fixtures (or, for the two video agents, on the fixture their own
suite generates):

| Agent | Offline entry point used |
| --- | --- |
| catering-finder | `run` on the fixture store |
| local-quotes | `run` on the fixture store with a fixed `--now` |
| field-service-planner | `plan` with the `--places` fixture provider |
| call-for-me | `simulate` over every scenario, plus `call` (must refuse) |
| media-generator | `generate` with the stub providers on the README's four sample scenarios |
| video-clipping | `run` on the generated fixture video |
| video-dubbing | `run` with the stub voice on the generated fixture video |
| brand checker | the captured fixtures replayed from a loopback server |

```sh
python3 -m unittest discover -s tools/tests -p 'test_agents_integration.py' -v
```

**What a green run proves.** Every agent:
- still completes its documented dry run;
- writes the report or files its README promises;
- prints every section its README lists, in the README's words;
- reaches for no network on that path.

Every run is wrapped in a guard that fails the test on any socket connection
or name lookup to a host other than loopback. Proxy settings are cleared for
the run, so a proxy on loopback cannot carry a request out. The guard's own
tests prove it blocks outside hosts, keeps loopback, and stops a real agent's
live command (catering-finder `capture`). A coverage test fails when a
folder is added to `agents/` without a case here.

**What it does not prove.** Nothing about live sources, real speech or
translation, or output quality. The guard sees only sockets opened by
Python in this process. ffmpeg and ffprobe run as subprocesses on local
files, with no URLs given to them. The video cases skip when ffmpeg is
missing.

## Acceptance self tests for the built NEAR agents (`acceptance_all.py`)

Issue #124. A marketplace tester checks a delivered agent against the job's
acceptance criteria, and a failed check means no payment. These scripts run
that test first, offline, one per built agent:

| Agent | Script | Criteria source |
| --- | --- | --- |
| field-service-planner | `agents/field-service-planner/acceptance/acceptance.py` | posting on #73 (comment 6365291384) |
| catering-finder | `agents/catering-finder/acceptance/acceptance.py` | posting on #75 (comment 6365588905) |
| local-quotes | `agents/local-quotes/acceptance/acceptance.py` | posting on #76 (comment 6366190586) |
| media-generator | `agents/media-generator/acceptance/acceptance.py` | posting on #78 (comment 6366897388) |
| video-clipping | `agents/video-clipping/acceptance/acceptance.py` | posting on #124 (comment 6372113964) |
| video-dubbing | `agents/video-dubbing/acceptance/acceptance.py` | posting on #77 (comment 6365954974) |

```sh
python3 tools/acceptance_all.py              # one table, then every FAIL with its evidence
python3 tools/acceptance_all.py --details    # every criterion with its evidence
python3 agents/catering-finder/acceptance/acceptance.py   # one agent
```

**How each script works.**
- It takes two or three of the posting's own sample scenarios, as far as
  an offline fixture can stand in for them, and runs the agent through
  its documented entry point.
- Each posting criterion, quoted word for word, is printed as `PASS`,
  `FAIL` or `UNTESTABLE`, with the evidence line, then a summary count.
- The sample scenarios' expected results are checked as `S` rows where a
  case exercises them.
- The checks recompute from the inputs where they can: shift hours and
  windows from the CSV files, drive minutes from the places file, page
  lines and replies from the store and the log, frame sizes from ffprobe,
  cut points from the word timings, background level from ffmpeg.
- `tools/acceptance_common.py` holds the shared layer: the offline guard
  (every non loopback connection refused and recorded), the loader and
  the result format.

**What `UNTESTABLE` means.** The criterion needs something an offline run
cannot give, and the reason is printed. Examples:
- a live routing or generation service;
- a listing's delivery time;
- a person's judgement (meaning, readability, what a clip shows);
- an ambiguous wording, which is never given an invented threshold.

**What `FAIL` means.** The agent does not meet the criterion as written. A
FAIL is filed as its own QUEUE task issue with the evidence. It is never
patched inside the test, and CI does not gate on it.

`tests/test_acceptance_selftests.py` runs in CI. It checks that:
- every script runs and reports a status for every criterion;
- an UNTESTABLE carries its reason and a FAIL its evidence;
- every posting criterion is covered.

Its tamper tests feed broken outputs and require the matching criterion to
FAIL, so a check cannot pass vacuously. The video agents need ffmpeg (and
its flite filter for dubbing). Without them their criteria are UNTESTABLE
with that reason.

## api_smoke.py

```sh
python3 tools/api_smoke.py                                  # offline, captured fixtures
python3 tools/api_smoke.py --live http://127.0.0.1:8000     # a running server
```

Read-only smoke checks for the public recall API (issue #68). They send
GET requests and never an `X-PAYMENT` header, so nothing is ever paid. Three
shapes are asserted:
1. `GET /` is 200 JSON naming the service, `/recall`, and an EVM-shaped
   `payout_wallet`.
2. `GET /recall?product=...` without payment is a 402 x402 v1 document. Its
   `accepts[0]` has scheme `exact`, network `base`, a numeric
   `maxAmountRequired`, an asset address, a `payTo` equal to the descriptor
   wallet, a `resource`, and a description of at most 500 characters.
3. `GET /openapi.json` is 200 OpenAPI naming `/recall`.

Output is one Markdown section in the delivery format: a PASS or FAIL claim
line per assertion, the source link, the UTC time, and the complete raw
transcript beneath. Exit codes:
- 0: every assertion passes.
- 1: any assertion fails. The failed ones are listed by name at the top.
- 2: the checks cannot run, because of a transport failure, a fixture that
  no longer matches its SHA-256, or bad input.

Offline mode reads `tests/fixtures/api_smoke/`, which holds transcripts
captured from the local gated server (`python3 server.py`) with a synthetic
placeholder payout address. Their provenance and hashes are in
`provenance.json`.

```sh
python3 -m unittest discover -s tools/tests -p 'test_api_smoke.py' -v
```

