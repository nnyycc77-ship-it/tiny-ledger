# Delivery packager

Task: issue [#154](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/154).
`tools/delivery_packager.py` turns one job spec into one checked report
package for the six report services built on this repo's fetchers. It
also times every run. It is repo work only: it places no bids, submits
nothing, and handles no keys, wallets or prices.

| Service | `service` | Fetcher used, unchanged |
| --- | --- | --- |
| Product recall check | `recall` | `tools/cpsc_recalls.py` |
| Carrier vetting | `carrier` | `tools/fmcsa_carrier.py` |
| Federal litigation screen | `litigation` | `tools/courtlistener_recap.py` |
| Form D private offering check | `formd` | `tools/edgar_formd.py` |
| Nonprofit check | `nonprofit` | `tools/propublica_nonprofits.py` |
| Federal awards check | `awards` | `tools/usaspending_awards.py` |

## Run it

```sh
# package, verify, and time one job (replay: answered from committed captures)
python3 tools/delivery_packager.py package \
    --job tools/delivery-packager/jobs/recall.json \
    --replay tools/delivery-packager/bundles/recall.json \
    --out /tmp/recall-package --timing-log /tmp/timing.jsonl

# the same job live: drop --replay (the fetchers make the requests)
python3 tools/delivery_packager.py package \
    --job tools/delivery-packager/jobs/recall.json --out /tmp/recall-live

# verify a written package again, and require its hash in a timing log
python3 tools/delivery_packager.py verify --dir /tmp/recall-package \
    --timing-log /tmp/timing.jsonl
```

There are three exit codes:
- 0: the package was written and verified;
- 1: the package was written but verification failed, and every failure
  is printed;
- 2: nothing was written, because the job spec is bad, a fetch failed, or
  a replay request was not in the bundle.

In live mode, Form D reads the EDGAR fair access contact from
`EDGAR_CONTACT`, and litigation reads `COURTLISTENER_TOKEN` if it is set.
Both are read from the environment only, as the fetchers already do.

## Job spec

The job spec is one JSON object with these keys:
- `service`: one of the six names above;
- `subject`: the subject the report is about;
- `buyer_ask`: printed in the report as given;
- `inputs`: the service's own inputs, listed below.

| Service | `inputs` |
| --- | --- |
| `recall` | `queries`: list of `{"field": "ProductName" or "RecallTitle" or "RecallNumber", "value": ..., "near": false}`; `exact_name` (optional; required by any query marked `near`) |
| `carrier` | `usdot`; `sources` (optional subset of `census`, `safer`, `li`; default all three) |
| `litigation` | `parties` (name variants, the first is the exact name whose cases are listed); `filed_after` (YYYY-MM-DD); optional `order_by`, `list`, `exclusions` ({docket id: reason}), `docket_details`, `subject_name` |
| `formd` | exactly one of `cik` or `issuer`; optional `max_filings`, `exclusions` ({accession: reason}) |
| `nonprofit` | `name` and/or `eins`; optional `exclusions` ({EIN: reason}) |
| `awards` | `recipient` and/or `naics`; optional `start`, `end`, `page`, `limit`, `exclusions` ({generated id: reason}) |

`jobs/` holds the job spec of each filled example below.

## The package

`package` writes a directory holding two files.

**`report.md`**, the deliverable. It has these parts, in order:
1. The title.
2. **Scope and inputs.** The service, the subject, the buyer ask as
   given, the inputs, the source mode (live, or replay of committed
   captures), the packaging time, and the scope line.
3. **Summary.** One line per stated count, each ending in
   `(Section Sn)`.
4. **One `## Section Sn:` per source query.** Each section is the
   fetcher's own rendering: the query URL, the retrieval time, the
   claims, and the complete raw response beneath the source link.
5. **Package checked and excluded.** Every line from any section that
   sets a result aside as a near match.
6. **Package sources.** Every request with its retrieval time and where
   the capture came from.

This follows the report skeleton of the workstream D templates
(`templates/README.md`): title, scope and inputs, sections, checked and
excluded, sources.

**`manifest.json`**, what `verify` checks against:
- per section, every capture's URL, retrieval time, origin, and the
  SHA-256 of the raw response block as printed in the section;
- every count the section states, as `{rule, capture_url, label, value}`;
- `deliverable_sha256`, the SHA-256 of `report.md`.

## Verification

`verify` runs after every `package`, and on its own. It fails the package
when any of the following holds.

1. **A claim lacks its source.** Either a section has no capture
   recorded, or a recorded capture's URL, retrieval time, or complete raw
   response block is not in the section.
2. **A summary line is not sourced.** The line names no section, names a
   section that does not exist, or states a value the named section does
   not record.
3. **A count does not match.** A section's stated count must equal the
   manifest value, and must also equal the fetcher parser's own recount
   of the raw response printed in that section. The recount rules are
   fixed in the code (`RULES`), not taken from the manifest:

   | Rule | Section line | Recounted with |
   | --- | --- | --- |
   | `cpsc_records` | `CPSC returned N record(s) for this query.` | `cpsc_recalls.records` |
   | `census_records` | `QUERY: dot_number = ... returned N record(s)` | `fmcsa_carrier.parse_census` |
   | `safer_fields` | `N of M labelled fields were found` | `fmcsa_carrier.labelled_values` |
   | `li_lines` | `N record text line(s) found.` | `fmcsa_carrier.text_lines` and `LI_PREFIXES` |
   | `cl_window_count` | `Total count found in the window ...: N.` | `courtlistener_recap.parse_search` |
   | `edgar_formd` | `EDGAR lists N Form D filings` | `edgar_formd.parse_submissions` and `form_d_filings` |
   | `pp_orgs` | `Organizations on this page: N.` | `propublica_nonprofits.search_results` |
   | `pp_filings` | `(T of N entries)` | `propublica_nonprofits.root(...).children("filings_with_data")` |
   | `usa_records` | `USAspending returned N record(s) on requested page P.` | the JSON `results` array |

4. **The deliverable hash is wrong or missing.** It is missing from the
   manifest, does not match `report.md`, or (with `--timing-log`) is not
   in the timing log.
5. **Nothing can be checked.** The package holds no count that can be
   checked at all.

`examples/unsourced-SYNTHETIC/` is the deliberately unsourced package. It
fails verification for exactly the reasons its README lists. The tests
also break each check one at a time on a fresh package and confirm that
each failure is reported.

## Replay and capture bundles

`--replay BUNDLE` answers every request from a bundle and fetches
nothing. A request the bundle does not hold stops the run with nothing
written. Each bundle entry names its request and an `origin` pointing at
a capture already committed in this repo. The packager checks the
capture before serving it.

| `origin.type` | Capture | Check before use |
| --- | --- | --- |
| `standing_watch_snapshot` | a response in a `tools/standing_watch.py` snapshot (complete transcript) | the URL matches, and the transcript's SHA-256 equals the one recorded in the snapshot |
| `http_fixture` | a `.http` fixture (complete transcript) | the URL and SHA-256 recorded in that folder's `provenance.json` |
| `usaspending_fixture` | a USAspending body with its `.meta.json` | the request body recorded in the meta file |
| `published_transcript` | a transcript printed by a fetcher in a committed report | exactly one `QUERY: GET <url>` line, its `Retrieved` line, and the fenced transcript under `Source: <url>`, rebuilt as printed |
| `body_only_fixture` | a response body captured without its status line and headers, with a `provenance.json` beside it | the URL and SHA-256 recorded in that `provenance.json`; the replay status line comes from the recorded status, and the package prints a note saying so above the section |

## Filled examples

All six examples are replays of real responses committed in this repo.
None of them made a request when it was packaged.

| Service | Job | Captures replayed | Requests | In-run total (timing log) | Process wall time |
| --- | --- | --- | --- | --- | --- |
| recall | `jobs/recall.json`, Peloton Tread+ | standing watch live snapshot, 2026-10-23T21:57Z | 2 | 0.005 s (0.0001 min) | 0.078 s (0.0013 min) |
| carrier | `jobs/carrier.json`, USDOT 90849 | standing watch live snapshot, 2026-10-23T21:57Z | 3 | 0.025 s (0.0004 min) | 0.099 s (0.0016 min) |
| litigation | `jobs/litigation.json`, Jabil Inc. | `captures/courtlistener-search-jabil-inc.json`, coordinator live capture 2026-10-23T23:51:03Z (issue #154) | 1 | 0.003 s (0.0001 min) | 0.076 s (0.0013 min) |
| formd | `jobs/formd.json`, 8VC DSS III | `tools/tests/fixtures/edgar/*.http`, 2026-10-23T03:45Z | 3 | 0.002 s (0.0000 min) | 0.073 s (0.0012 min) |
| nonprofit | `jobs/nonprofit.json`, Feeding America | transcripts in `tools/examples/nonprofit-pack.md`, live run 2026-10-23T21:56Z | 2 | 0.007 s (0.0001 min) | 0.080 s (0.0013 min) |
| awards | `jobs/awards.json`, Boeing | `tools/tests/fixtures/usaspending/recipient.json`, 2026-10-23T00:17Z | 1 | 0.001 s (0.0000 min) | 0.073 s (0.0012 min) |

The packages are in `examples/<service>/`, and the timing lines are in
`timing-log.jsonl`. Process wall time was measured once per example on
the build machine (Python 3.13), around the whole command, interpreter
start included.

How to read the times:
- **These are replay times.** They measure assembling and verifying the
  package. They do not include any network time, because no request was
  made.
- **Live runs will be slower.** A live run's time is dominated by its
  requests, which are made one after another (the Requests column above
  counts them for these jobs), and EDGAR's are paced by the fetcher. The
  `fetch_seconds` field of a live timing line measures exactly that.
- **No live run has been timed yet.** This repo's build environment
  cannot reach the source hosts, so no live minutes per job are stated
  here.

## Litigation

The litigation example replays one complete CourtListener v4 search
response (party "Jabil Inc.", filed after 2021-10-22, 15 results). The
coordinator captured it live, without a token, and posted it on issue #154
([comment 6377076098](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/154#issuecomment-6377076098)).

Its provenance is in `captures/provenance.json`: URL, retrieval time,
SHA-256 and byte size, all matching the comment. The capture is the
response body only, so the package says so above the section: the status
line printed above the body is built from the stated HTTP 200, and no
headers were captured.

`tools/tests/test_delivery_packager.py` also packages the litigation
adapter on a SYNTHETIC response, labelled as such in the test.

## Timing log

`package --timing-log FILE` appends one JSON line per run with these
fields:

| Field | Meaning |
| --- | --- |
| `run_started_utc` | when the run started (UTC) |
| `service`, `subject` | from the job spec |
| `mode` | `live` or `replay` |
| `job`, `bundle` | the job spec and capture bundle used (`bundle` is null in live mode) |
| `package_dir` | where the package was written |
| `requests` | how many requests the job made or replayed |
| `fetch_seconds` | time obtaining responses: live requests, or loading captures in replay |
| `assemble_seconds` | time building and writing the package |
| `verify_seconds` | time verifying it |
| `total_seconds`, `total_minutes` | the whole run |
| `deliverable_sha256` | the SHA-256 of the report |
| `verify` | `PASS` or `FAIL` |

The log records time only. It has no price field, because price is the
owner's decision (issue #147).

## Tests

`tools/tests/test_delivery_packager.py`, run with the tools suite:

```sh
python3 -m unittest discover -s tools/tests -p 'test_delivery_packager.py' -v
```
