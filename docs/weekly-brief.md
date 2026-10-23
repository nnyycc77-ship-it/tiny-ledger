# Filings and awards weekly brief

Issue #146. `tools/weekly_brief.py` produces one dated Markdown brief for
a seven-day window. It draws on two public sources, through the repo's
existing fetchers:

- **New Form D filings** from SEC EDGAR (`tools/edgar_formd.py`).
- **New federal contract awards** from USAspending
  (`tools/usaspending_awards.py`).

## What a brief contains

- **Heading.** The heading gives the window, which is the `--week-ending`
  date and the six days before it. The next line gives the count of
  entries in each section.
- **SEC EDGAR Form D filings.** One entry per Form D or D/A filed in the
  window by an issuer on the watchlist that passes the filters. Each entry
  gives:
  - the filer;
  - the filing date;
  - the total offering amount and total amount sold, only where the filing
    states them;
  - the industry group;
  - why the entry was listed;
  - the filing index link.

  Beneath each entry come two raw excerpts, each under its source link and
  retrieval time:
  - the filing's own entries in the EDGAR submissions index;
  - the quoted elements of the Form D XML.

  Filings in the window that fail the filters are listed by name, with the
  reason they were not included.
- **USAspending prime contract awards.** The exact query sent, then one
  entry per award on the returned page. Each entry gives the recipient,
  the Award Amount as the API returns it, the start date, and the award
  page link. The raw JSON record follows beneath its source.

**Evidence rules:**
- **Figures.** Every figure is quoted from the excerpt beneath it.
  `python3 tools/weekly_brief.py --check BRIEF.md` verifies this. It finds
  every "as shown" value and confirms each is a whole field inside its
  entry's excerpts.
- **Missing amounts.** A missing amount reads "not stated by the source".
  It is never estimated.
- **Empty results.** A section with no entries says so and prints every
  raw response it read, in full. It is never padded.
- **Failures.** A failed or unexpected response stops the run with no
  brief. A failure is never shown as an empty result.

## Scope, stated plainly

- **EDGAR is read per issuer.** The existing fetcher reads one issuer's
  submissions index at a time, so the Form D section covers the issuers on
  the watchlist, not every filing on EDGAR. A whole-EDGAR feed would need a
  new source and is not in this tool.
- **USAspending reads one page.** The brief reads one page of up to
  `limit` awards, sorted by Award Amount. If the API reports more pages,
  the brief says so.
- **What "in the window" means.** It means the `time_period` filter of the
  USAspending search API, as the fetcher sends it.

## Setting the filters (for a subscriber)

A subscriber's filters are one JSON file:

```json
{"title": "Weekly filings and awards brief",
 "edgar": {"ciks": ["2156237", "1801756"],
           "sectors": ["Pooled Investment Fund"],
           "keywords": ["8VC"]},
 "usaspending": {"naics": ["5415"], "limit": 10}}
```

- **`edgar.ciks`.** The issuers to watch, by SEC CIK. Use
  `tools/edgar_formd.py --issuer NAME` to find a CIK. It never picks
  between several matches.
- **`edgar.sectors`.** Form D industry groups, matched exactly but
  ignoring case against the filing's `industryGroupType`, such as
  `Pooled Investment Fund`.
- **`edgar.keywords`.** Words matched, ignoring case, inside the issuer
  name or the industry group.
- **When a filing is listed.** It is listed when it matches any sector or
  any keyword. With neither list, every Form D in the window is listed.
- **`usaspending.naics`.** NAICS code prefixes of 2 to 6 digits, for
  example `5415` for computer systems design. These are the category
  filter.
- **`usaspending.limit`.** The page size, from 1 to 100.
- **Optional sections.** Either section can be left out, but not both.

**Running it.** EDGAR needs an operator contact, under the SEC's fair
access rules (see `tools/edgar_formd.py`):

```sh
# "Your Name you@example.com" is a placeholder contact: use your own name and address.
EDGAR_CONTACT="Your Name you@example.com" python3 tools/weekly_brief.py \
    --config tools/weekly-brief/sample-config.json --week-ending 2026-10-23 > brief.md
python3 tools/weekly_brief.py --check brief.md
```

## Sample

`tools/weekly-brief/sample-brief-2026-10-23.md` is a real brief:
- **Run:** produced live from `sample-config.json` for the week ending
  2026-10-23, at 2026-10-23T21:58:06Z.
- **Who ran it:** the coordinator, under Option B on issue #146, because
  the build environment cannot reach the sources.
- **Contents:** 2 Form D filings and 10 awards.
- **How it was kept:** committed byte for byte, with its sha256 in
  `tools/weekly-brief/provenance.json`.
- **Check:** `--check` passes on it.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_weekly_brief.py' -v
```

The tests run offline:
- the EDGAR responses are the real captures in `tools/tests/fixtures/edgar/`;
- the USAspending bodies are SYNTHETIC and labelled inside their files, in
  `tools/tests/fixtures/weekly-brief/`.
