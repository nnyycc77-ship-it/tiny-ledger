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

Not a fetcher: `pregate.py` is the offline review pre gate (secrets scan,
honesty lint, fixture provenance check) from `REVIEW.md`. See
[`pregate-README.md`](pregate-README.md).

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

## edgar_formd.py

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
contact must be the plain "Name you@example.com" form: on 2026-10-23
EDGAR answered 403 "Your Request Originates from an Undeclared
Automated Tool" to a contact carrying a URL in parentheses (captured as
`tests/fixtures/edgar/undeclared-403.http`), so URLs, parentheses and
brackets are refused up front.

Any non-200 answer, non-JSON index, or malformed XML stops the run with
a diagnostic on stderr and no report on stdout.

### Verification

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
