# `csl_screen`: US Consolidated Screening List screen

A tool factory wave 2 tool (issue #179).
- **Code:** the fetcher is
  [`tools/csl_screen.py`](../../tools/csl_screen.py). The pay per call
  API serves it as `GET /csl?name=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Registered on the MCP server.** The server on main lists it
  (`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
  PR #208 (issue #204), the shared surface step the #158 ruling called for.
  Going live still waits on the owner redeploy step.

## The tool at a glance

- **What it answers:** is this person or company name on any US export
  control list, as published in the Consolidated Screening List: the
  Entity List, the Denied Persons List, the Unverified List, the
  Military End User List, the ITAR Debarred list, the SDN list, and the
  other lists the consolidated file carries. Each row of the file names
  its own list in its source column, and the report prints that name as
  shown.
- **Source:** the Consolidated Screening List downloadable file
  published by the International Trade Administration on trade.gov,
  linked as the downloadable CSV from the Consolidated Screening List
  page (https://www.trade.gov/consolidated-screening-list):
  `GET https://data.trade.gov/downloadable_consolidated_screening_list/v1/consolidated.csv`.
  - **Keyless.** No key, account or credentials of any kind.
  - **The list publication date** a report states is the file's
    `Last-Modified` response header, the date the source itself
    publishes for the file.
  - **Caching.** The file is about 16 MB, so it is downloaded once and
    cached locally for 24 hours (under `tools/.csl_cache/`, never
    committed); a run inside that window matches against the cache and
    says so, with the original retrieval time. The bytes and SHA-256
    are printed either way, so a screen can be repeated against the
    same file. `--refresh` downloads again.
- **Arguments:** `name`, a person or company name with at least 3
  letters or digits.
- **Needs on the server:** outbound HTTPS to `data.trade.gov`, room
  for the cached file, and no key.
- **The matching rule** is the rule of the OFAC SDN check already on
  the shelf: names are compared after folding case and replacing every
  character that is not a letter or digit with a space. An exact match
  is the whole normalised query equal to the whole normalised name; a
  contains match is the normalised query appearing inside the
  normalised name as whole words. The name column and every `alt_names`
  entry are both checked. No fuzzy or phonetic score is computed or
  claimed.
- **What it is not:** a determination. A name match is not a finding
  that a party is the listed person or entity, and no match is not a
  screening clearance.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The matching rule**, stated in full.
- **The file read.** The exact query, the UTC retrieval time, the list
  publication date as published, the response headers the tool lists,
  and the file as read: bytes, SHA-256, lines, and the number of rows
  screened. Every reply states the list date and the rows screened.
- **The result.** For each match: the list name as shown, the program
  as shown, the type as shown, which field matched and how, and the
  matched raw row printed in full beneath the source link. At most 50
  matches are listed, in file order, with any further matches counted.
- **No match** is stated with the list publication date and the number
  of rows screened, against the file exactly as read (its SHA-256 is
  printed), so the screen can be repeated.

**Failures:** these give no report, with exit 2 on the CLI and 502 on
the API: a failed request; a non 200 answer; a file whose header is
not the published CSL header; a row that does not carry every
published column. A failed fetch is never shown as no match, and a
stale or unreadable cache is never quietly used: the download is tried
again and its failure is the report's end.

## Running it

```sh
python3 tools/csl_screen.py "Huawei Technologies"
python3 tools/csl_screen.py --refresh "Aeroflot"
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_csl_screen.py' -v
```

The tests run offline:
- **Fixture:** an excerpt of the real file in
  `tools/tests/fixtures/csl/` (the header line plus seven data lines,
  verbatim, in file order), with provenance recording the complete
  file as retrieved on 2026-10-24: 26,173 rows, its byte count, its
  SHA-256, and its Last-Modified date.
- **Shapes covered:** a primary name exact match with its raw row, an
  alias match, contains matches across two lists, a no match answer
  stating the list date and rows screened, a file not in the published
  shape refused, fetch failures failing closed, and the cache round
  trip (download, cache hit, refresh, and a corrupt cache downloaded
  again).
- **Live smoke run:** one live run is recorded in the PR description,
  with its retrieval time.
