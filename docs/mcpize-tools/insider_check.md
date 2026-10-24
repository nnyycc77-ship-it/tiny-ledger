# `insider_check`: SEC EDGAR insider activity

A tool factory wave 2 tool (issue #182).
- **Code:** the fetcher is
  [`tools/insider_check.py`](../../tools/insider_check.py). The pay per call
  API serves it as `GET /insider?cik=...` or `GET /insider?issuer=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Not on the MCP server yet.** Under the wave registration ruling on
  #158, confirmed for this tool on #182, every wave tool that passes review
  is registered on the server in one shared surface PR at the end of the
  wave. Going live is one owner redeploy step after that.

## The tool at a glance

- **What it answers:** what insider purchases and sales has this public
  company reported recently? It reads the newest Form 3, 4 and 5 filings in
  the issuer's EDGAR submissions index. For each, it gives:
  - the reporting owner and their relationship flags, as filed;
  - each transaction's security, date, `transactionCode`, shares, price
    per share, acquired or disposed code, shares owned afterwards, and
    direct or indirect code, all as filed;
  - for derivative rows, the conversion or exercise price.
- **Codes are shown, never explained.** No SEC documentation of the codes
  was captured on #182.
- **Footnote prices:** a price given only as a footnote reference is shown
  with that footnote's text, verbatim.
- **Sources,** all public EDGAR endpoints:
  - **The submissions index,** `https://data.sec.gov/submissions/CIK##########.json`.
    Its filings with form 3, 3/A, 4, 4/A, 5 or 5/A in the recent window are
    the ownership filings. The newest `max_filings` of them (default 5,
    at most 20) are read, in index order.
  - **The raw ownership XML of each filing,** in its Archives folder. This
    is the last path segment of the index's `primaryDocument`. Capture 1 on
    #182 shows `form4.xml` listed in the folder for `primaryDocument`
    `xslF345X06/form4.xml`. The `xslF345X06` path is a rendered view and is
    never read.
  - **With `issuer`, the EDGAR company search,** exactly as
    `tools/edgar_formd.py` sends it.
    - **One match** proceeds.
    - **Several matches** are listed with their CIKs.
    - **None** is reported with its raw response.

    That search is the one captured for Form D (`type=D`). Whether it
    resolves an issuer that has never filed a Form D is not verified;
    pass `cik` for those.
- **EDGAR fair access,** exactly as in `tools/edgar_formd.py`, whose helpers
  this tool uses:
  - a declared contact (`EDGAR_CONTACT` or `--contact`, plain
    `Name address` form) in a User-Agent that names this tool;
  - paced requests;
  - no contact value anywhere in the repo.

  Without a contact the CLI refuses to run, and the API answers 503 and
  fetches nothing.
- **Needs on the server:** outbound HTTPS to `data.sec.gov` and
  `www.sec.gov`, and `EDGAR_CONTACT`.
- **What it is not:** an analysis of any trade or person, or a full
  history. It reads the index's recent window only.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

1. **The answer.**
   - the issuer as shown in the index;
   - how many ownership filings the recent window lists, and how many are
     read;
   - one section per filing with the fields above, as filed.
2. **The evidence for each filing,** beneath it:
   - the exact query and the UTC retrieval time;
   - the status line, body size and SHA-256;
   - the source link, with these verbatim from the document beneath it:
     the reporting owner block, each transaction row, and the footnotes.
3. **The evidence for the submissions index.** The exact query, the
   retrieval time, the status, body size and SHA-256, and the index entries
   read.

**Empty result:** an index with no Form 3, 4 or 5 filing in its recent
window is reported with the complete raw submissions response as the
proof. It covers that window only. Older index pages, when the index names
them, are listed and not read.

**Failures:** these give no report, with exit 2 on the CLI and 502 on the
API. The error names the source, the query and the reason. They are:
- a failed request;
- any status but 200, such as the captured Archives 404 `NoSuchKey`
  answer for a wrong accession folder;
- a body that is not an `ownershipDocument`;
- an ownership document with no reporting owner;
- rows that cannot be paired with their raw text.

## Running it

```sh
# "Your Name you@example.com" is a placeholder contact: use your own.
EDGAR_CONTACT="Your Name you@example.com" python3 tools/insider_check.py --cik 320193
python3 tools/insider_check.py --contact "Your Name you@example.com" --cik 320193 --max-filings 2
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_insider_check.py' -v
```

The tests run offline:
- **The new captures:** the coordinator's four captures from #182,
  verbatim in `tools/tests/fixtures/insider/` with their posted hashes:
  - the folder index;
  - two Apple Form 4 documents, one a single sale and one with 7
    non-derivative and 4 derivative rows and footnote-only prices;
  - the Archives 404.
- **The existing indexes:** the submissions indexes already in
  `tools/tests/fixtures/edgar/`: Apple (616 ownership filings) for the hit,
  and 8VC DSS III (no ownership filing) for the empty result.

The coordinator's live smoke run, with a declared contact, is owed at
review.
