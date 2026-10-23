# USAspending contract award fetcher

Run from the repo root with Python 3.11 or later. No packages, API key,
environment configuration, account, or wallet are required.

```sh
python3 tools/usaspending_awards.py --recipient Boeing --limit 2
python3 tools/usaspending_awards.py --recipient Boeing --naics 336411 --limit 2
python3 tools/usaspending_awards.py --recipient 'Instant Pot Smart WiFi' --limit 2
```

These are the exact inputs used for the captured live responses under
`tools/tests/fixtures/usaspending/`. The last command is an empty-search
check using a product name from the published recall delivery as recipient
search text; it does not identify a company or establish that one has no awards.
See [the rendered evidence](examples/usaspending.md) for results, exact POST
bodies, source links, UTC retrieval times, and unmodified response bodies.

Use `--recipient` for recipient search text, `--naics` for a required NAICS
prefix (repeatable), or both. Optional `--start` and `--end` pass a
date range to the API's `time_period` filter; they must be supplied together.
Only prime contract award types A, B, C and D are requested.

Recipient search covers name, UEI and DUNS; it is not an exact legal-entity check.
Source: <https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_award.md>
```text
    + Text searched across a recipient’s name, UEI, and DUNS
```

NAICS filtering uses prefixes.
Source: <https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/search_filters.md>
```text
a NAICS code that starts with one element from the require list.
```

Each invocation fetches one page, sorted by Award Amount descending. Use
`--page` to request another page. `--limit` defaults to 10 and the CLI caps it
at 100. This is a tool limit, not a claim about the API's maximum. The report
prints the API's `hasNext` value and always labels its scope as one page.
It never calculates an all-award count or total. Paging a changing live dataset
does not provide a consistent snapshot; review scope before using paid work.

The output groups the returned fields and checked/excluded records above the
source link, then prints the complete raw UTF-8 JSON response body directly
under that link. No field order, spacing, or number in the evidence is changed.
HTTP headers are not collected or published because they can contain session
cookies. The request method, URL, content type, exact JSON request body, and
retrieval time in UTC are recorded separately. An empty results array retains
the entire response body, including pagination and messages.

To list a near match you have checked, copy its `generated_internal_id` from
the report and pass `--exclude 'GENERATED_ID=REASON'`. For example, the following
reruns the captured recipient query with the agency-scope exclusion shown in
the rendered evidence:

```sh
python3 tools/usaspending_awards.py --recipient Boeing --limit 2 \
  --exclude 'CONT_AWD_NAS1510000_8000_-NONE-_-NONE-=Outside this brief’s Department of Defense scope; source Awarding Agency is National Aeronautics and Space Administration.'
```

Exclusion reasons are explicitly reviewer-supplied. The tool checks that the
identifier is on the fetched page, retains its source fields and full raw
evidence, and does not decide relevance or verify your reason. Unknown or
duplicate exclusions fail. Supply only public research inputs and reasons.

Transport errors, non-JSON responses, missing pagination metadata, and invalid
record identifiers exit with status 2 and no report on stdout. They never
produce an empty-result claim. Source fields that are missing or null say
`not supplied by source` in the summary. Source warnings remain visible.

Run offline regression tests or opt in to real public API calls:

```sh
python3 -m unittest discover -s tools/tests -p 'test_usaspending_awards.py' -v
USASPENDING_LIVE=1 python3 -m unittest discover -s tools/tests -p 'test_usaspending_awards.py' -v
```

Fixtures contain full bodies captured from live public POST requests. Each
matching `.meta.json` records the source URL, method, exact request string,
and UTC retrieval time. Offline fault-injection tests deliberately corrupt
copies to exercise error handling; these are not report examples. The live
test sends fresh requests and never uses fixtures as substitute responses.
