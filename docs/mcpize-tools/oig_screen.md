# `oig_screen`: HHS OIG exclusion screen

A tool factory wave 2 tool (issue #180).
- **Code:** the fetcher is
  [`tools/oig_screen.py`](../../tools/oig_screen.py). The pay per call API
  serves it as `GET /oig?name=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not on the MCP server yet.** Under the wave registration ruling on
  #158, confirmed for this tool on #180, every wave tool that passes review
  is registered on the server in one shared surface PR at the end of the
  wave. Going live is one owner redeploy step after that.

## The tool at a glance

- **What it answers:** is this person or entity on the HHS OIG List of
  Excluded Individuals and Entities (LEIE)? For each matched row it gives
  the exclusion type (`EXCLTYPE`) and the exclusion date (`EXCLDATE`) as
  published, plus `REINDATE`, `WAIVERDATE` and `WVRSTATE`, then the raw row
  in full.
- **Source:** the complete current LEIE database file,
  `GET https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv`. It is
  linked as "Updated LEIE Database (CSV)" from OIG's
  [LEIE Database & Supplement Downloads](https://oig.hhs.gov/exclusions/leie-database-supplement-downloads/)
  page. That page, as captured on #180, says the file "contains the entire
  dataset of all exclusions in effect", is replaced every month, and that
  reinstated individuals and entities are removed from it.
- **Keyless.** The tool reads no key. It downloads the whole file
  (10,802,977 bytes at the coordinator's capture) on every call, with no
  cache, the same as the OFAC list screen.
- **Every reply states:**
  - **the database date,** which is the file's `Last-Modified` header as
    returned. The captures show it matching the page's "Last Update". It
    is never the retrieval time; an answer without `Last-Modified` gives no
    report;
  - **the number of rows screened;**
  - **the file's SHA-256 and size.**
- **The codes are shown, never explained.** OIG's
  [Database Record Layout](https://oig.hhs.gov/exclusions/files/leie_record_layout.pdf)
  gives only field names and lengths. It does not define the `EXCLTYPE`
  codes, so they are shown exactly as published.
  - **Dates** are the file's 8-character values, as published. The
    captured rows are `YYYYMMDD`.
  - **A `0`** in `REINDATE` or `WAIVERDATE` is the file's own empty
    marker, shown as `0`.
- **Argument:** `name`, a person name or an entity name, with at least 3
  letters or digits.
- **Needs on the server:** outbound HTTPS to `oig.hhs.gov`, and no key.
- **What it is not:** a clearance or an identity match. Only names are
  compared, and OIG's own online search and verification are not
  performed.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## Matching

The rule is the same as `tools/ofac_sdn_check.py`:
- **Normalising:** case is folded, and every character that is not a
  letter or digit becomes a space.
- **Kinds of match:** an exact match, or a contains match as whole words.
- **A row with a `LASTNAME`** is compared in four forms: first last, first
  middle last, last first, and last first middle.
- **A `BUSNAME`** is compared as written.
- **The listing:** an exact match wins over a contains match on the same
  row. The first 50 matches are listed in file order, and the number left
  unlisted is stated.

## What a report contains

1. **The answer.** The number of matched rows (exact and contains), the
   rows screened, the database date and the file's SHA-256. Then, for each
   listed row:
   - the exclusion type and date and the other fields above, as
     published;
   - which name form matched;
   - the source link with the row's line number, and the raw row directly
     beneath it.
2. **The matching rule.**
3. **The database as read.** The exact query, the UTC retrieval time, the
   database date, the file's size, SHA-256, line count and data-row count,
   and the response headers as returned.

**No match:** the report says no row matched. It states the rows
screened, the database date and the SHA-256 of the file exactly as read,
which is the proof. It is never a clearance.

**Failures:** these give no report, with exit 2 on the CLI and 502 on the
API. The error names the source and the reason. They are:
- a failed download;
- any status but 200;
- a redirect off `oig.hhs.gov`;
- no `Last-Modified` header;
- a header row other than the captured one;
- a row whose width is not the header's 18 columns;
- a file with no data rows.

A failure is never "no match".

## Running it

```sh
python3 tools/oig_screen.py "Aaron Smith"
python3 tools/oig_screen.py "1 Best Care"
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_oig_screen.py' -v
```

The tests run offline on `tools/tests/fixtures/oig/leie-excerpt.csv`, an
EXCERPT of the complete file. Every line is byte verbatim from the
coordinator's captures on #180:
- the header row;
- the first 10 data rows (entities);
- 10 `SMITH` rows;
- the only 2 rows with a non-zero `WAIVERDATE`.

The complete file's size, line count, SHA-256 and the `zqxflorp` no-match
proof are in `provenance.json`. The coordinator's live smoke run is owed
at review.
