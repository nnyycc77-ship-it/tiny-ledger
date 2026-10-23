# NHTSA recalls fetcher

Run from the repo root with Python 3. No packages, API key, environment
configuration, account, or wallet are required.

```sh
python3 tools/nhtsa_recalls.py --subject "Hyundai Elantra 2021" \
  --make Hyundai --model Elantra --model-year 2021
python3 tools/nhtsa_recalls.py --subject "Hyundai Elantra 2021" \
  --make Hyundai --model Elantra --model-year 2021 \
  --exclude 21V796000="replaced by 22V354000, which is listed" --pretty
```

The first command reproduces, byte for byte, the query URL recorded in
the published recall delivery.
Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/blob/5be7e2905c9b8253793ce45455f4b698f38919f4/deliveries/recall-check-b37362be-8d97-4b54-a8ce-7f7ed8e6eaf0-rev1.md>
```text
- Query URL: https://api.nhtsa.gov/recalls/recallsByVehicle?make=Hyundai&model=Elantra&modelYear=2021
- Retrieved (UTC): 2026-10-22T11:48:10Z
```

Query fields: `--make`, `--model` and `--model-year`, which together form
the `recallsByVehicle` query, and `--param KEY=VALUE` for any other field.
The URL is built in that order with spaces encoded as `%20`.
`recallsByVehicle` is the one endpoint checked against a recorded live
response (source S24 in the delivery above). `--endpoint NAME` reaches any
other path under `https://api.nhtsa.gov/recalls/` the API accepts; the
response is printed verbatim whatever its shape, and campaign blocks are
rendered only for fields that are present.

The CLI emits a single Markdown section on stdout: the subject heading
and database line, the QUERY line with the exact fields, the campaign
count and the retrieval time in UTC, one block per campaign with the
values as shown in the source, any checked and excluded campaigns with
their reasons, then the source link with the complete raw HTTP response
transcript (status line, headers in the order returned, a blank line,
then the body exactly as returned) directly beneath it. An empty result
is proven by that transcript, never asserted. Campaigns stay in response
order. If the response's own `Count` field differs from the number of
entries in its results array, the QUERY line says so.

Each campaign block gives the campaign number, manufacturer,
ReportReceivedDate as shown with its long form in brackets, product
(model year, make, model) and component, summary, hazard (Consequence),
remedy, notes, the parkIt / parkOutSide / overTheAirUpdate flags, and
units. The recorded response carries no unit count field, so units are
stated as not shown; if a record ever carries a field whose name contains
"unit", it is printed as shown instead. A field missing from a record is
marked "(not present in the API record)", never filled.

To list a near match you have checked, pass
`--exclude CAMPAIGN-NUMBER="reason"`, repeatable. The campaign is printed
under "Checked and excluded" in the same block format as a match, with
your reason. The tool refuses an exclusion for a campaign number that is
not in the response, so an exclusion can never describe a record that was
not fetched. The tool never decides relevance itself.

`--pretty` adds one pretty printed JSON excerpt per campaign after the
transcript, in response order, values unchanged, the way `deliveries/`
shows records.

A failed fetch (no network, blocked host) prints the error and the query
URL on stderr, prints nothing on stdout, and exits 2. An HTTP error
status from the API is not a failed fetch: its full transcript is printed
and the section says the result is not determinable from that response.

Run the offline tests:

```sh
python3 -m unittest discover -s tools/tests -p 'test_nhtsa_recalls.py' -v
```

The tests need no network. Their fixtures are verbatim copies of source
S24 in the delivery above (its lines 1194 to 1213 and 1236 to 1251), and
the fetch tests run against a local server on 127.0.0.1. No HTTP headers
from api.nhtsa.gov were recorded in the delivery, so no test claims any.
