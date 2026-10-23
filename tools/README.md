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

## cpsc_recalls.py

Run from the repository root with Python and curl installed. No API key,
account, wallet, or Python package installation is needed. curl is used to
retain the received HTTP status line and header order alongside the complete
response body. Its default config is disabled; redirects are not followed.

```sh
python3 tools/cpsc_recalls.py 'Instant Pot'
python3 tools/cpsc_recalls.py 'Instant Pot Smart WiFi' \
  --exact-name 'Instant Pot Smart WiFi' --near-product 'Instant Pot'
```

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
GET URL, retrieval time in UTC, result claims, source link, and complete curl
response capture immediately beneath the link. The body is not pretty printed
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
error handling. The optional live test invokes the CLI against CPSC, checks an
empty query and a broader query with a checked/excluded name, and requires no
fixture or mocked transport. Live results can change; a failure requires review,
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

## Tests

All three suites live in `tools/tests/` and run offline with one
discovery command:

```
python3 -m unittest discover -s tools/tests -v
```

The tests need no network. Their fixtures are verbatim copies of
responses recorded in `deliveries/` or captured public responses with
recorded provenance, and the fetch tests run against a local server
on 127.0.0.1.
