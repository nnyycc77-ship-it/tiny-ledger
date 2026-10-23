# CPSC Recalls Dataset 2023 to 2025: listing copy

**Status:** Not listable yet. The dataset is built by `tools/build_cpsc_dataset.py` and checked by `tools/validate_cpsc_dataset.py` (issue #148), but the live pull has not run, because this build container cannot reach the CPSC API. When it has run, the record count and the field list come from `datasets/cpsc-recalls/PROVENANCE.md` and `SCHEMA.md`, and the lines below marked "from PROVENANCE.md" are filled in from that file and nothing else.

**Sources:** the builder's and validator's own docstrings, and issue #148. Every claim below is either true of the file by construction (the builder writes it that way, and the validator checks it) or is read from PROVENANCE.md or SCHEMA.md once they exist.

## Paste order

### 1. Name

CPSC Recalls Dataset 2023 to 2025 (JSON Lines)

### 2. Category

To confirm at listing.

### 3. Suggested price

To set at listing. The repo records no price for a dataset product.

### 4. Listing description

Every U.S. Consumer Product Safety Commission recall the CPSC recall API returns for recall dates from 2023-01-01 to 2025-12-31, in one JSON Lines file, one recall per line.

- **As the source gives it.** Each line is the CPSC API's own record, with its own field names and values. Nothing is added, renamed, enriched or recalculated. Each record carries its CPSC recall page link in its own `URL` field.
- **Every field documented.** `SCHEMA.md` lists every field in the file, read from the records themselves, with the JSON types seen and how many records carry it.
- **Count you can check.** `PROVENANCE.md` lists every month query, with its exact URL, its retrieval time, its record count and the sha256 of the raw response. A whole-year query per year confirms the months add up. Record count: from PROVENANCE.md.
- **Validator included.** `validate_cpsc_dataset.py` checks:
  - that the file parses;
  - the count and the sha256;
  - unique recall IDs;
  - every date inside the range;
  - that no line carries a field missing from the schema.

  Its `--recheck` option compares sample lines against the live API.

### 5. What buyers get

- `recalls-2023-2025.jsonl`;
- `SCHEMA.md` and `schema.json`;
- `PROVENANCE.md` and `provenance.json`;
- the validator script.

### 6. FAQ

- *Is this every recall?* It is every record the CPSC recall API returned for those recall dates on the pull date in PROVENANCE.md, checked month by month and against one whole-year query per year. Records CPSC adds or changes after that date are not in it.
- *Is anything added from other sources?* No. Only the CPSC record's own fields are in the file, and the validator fails any line with a field the schema does not list.
- *Are the values cleaned or normalized?* No. Values are exactly as the API returned them, dates included.

## To confirm at listing

- The record count and the pull date, from PROVENANCE.md.
- That the field list in the description still matches SCHEMA.md.
- The category and the price.
