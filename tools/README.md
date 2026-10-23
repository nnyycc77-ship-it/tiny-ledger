# tools

Command line fetchers, one per source, that query a live public source
and print one Markdown section in the delivery format from
`AGENT-BRIEF.md`: the claim lines, the source link, and the complete
raw response printed verbatim directly beneath the link. Each run
records the exact query URL and the retrieval time in UTC. Standard
library Python 3 only, no dependencies, no keys stored here. Where a
source needs a free public key, the fetcher reads it from the
environment and its header comment says so.

| Source | Fetcher | Key |
| --- | --- | --- |
| NHTSA recalls API | `nhtsa_recalls.py` | none needed |

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

## Tests

```
python3 -m unittest discover -s tools -v
```

The tests need no network. Their fixtures are verbatim copies of
responses recorded in `deliveries/`, and the fetch test runs against a
local server on 127.0.0.1.
