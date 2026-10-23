# Template: Public Dataset Build: Structured CSV from Named Public Sources

Catalog service 8, as named in the task issue for these templates.

Source: [issue #29, D: Delivery templates for services 7 to 10](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/29)
> - Service 8: Public Dataset Build: Structured CSV from Named Public Sources

The same issue states the service specific point this template encodes, in the sentence that names all four:

> For each service, a template in the style of the existing `templates/` folder: a report skeleton (title, scope and inputs, per subject sections in the delivery format, a checked and excluded section, a sources list) plus the service specific checklist points (for example: dataset templates name the exact queries, collection method, and source record identifier for every row; the bilingual template prints Chinese excerpts in the original beside their translations; the code review template states plainly it is a review, not an audit certification).

> **Template.** Text in angle brackets like `<this>` is a placeholder to
> replace. Every placeholder must be filled from a source that was actually
> fetched, or deleted. No figure, name, date, score, or identifier in a
> finished report may come from anywhere but a fetched source named in its
> Sources section. This template contains no example data.

A dataset delivery is a CSV file plus this report. The report is the
provenance of the file: it names every source and query, the collection
method, and the rule that ties every row to one source record. A row without
a source record identifier does not ship.

## How to use this template

1. Copy this file to the delivery and delete everything above the line
   "Report skeleton begins".
2. Fill every placeholder from a fetched source, or delete it.
3. Work through the service checklist at the end before delivering. Every
   box must be true of the finished report.

## Format rules that bind this delivery

Every claim in this report sits with its source link, and the raw excerpt
from that source is printed directly beneath the link, verbatim. The rule is
fixed by the repo brief and is quoted here so the template stands alone.

Source: [AGENT-BRIEF.md, hard rule 3](../AGENT-BRIEF.md)
> 3. **The delivery format is fixed, because paying platforms check
>    it mechanically.** Every claim sits with its source link, and the
>    raw excerpt from that source is printed directly beneath the
>    link, in a code block or in quoted lines, verbatim and
>    unreformatted. An empty result is proven by printing the full raw
>    response, never by asserting that nothing was found. Every query
>    records the exact query used and the retrieval time.

Source: [AGENT-BRIEF.md, hard rule 2](../AGENT-BRIEF.md)
> 2. **Never invent data.** Every figure in any deliverable, example,
>    or doc must come from a source that was actually fetched, and the
>    source must be named. If a number cannot be pulled from the
>    source, the report says so plainly. It never fills the gap.

Applied to every section below:

- One source block per query: the source name, the exact query (URL, or
  request body for POST, or the form fields used), the retrieval time in UTC
  (`YYYY-MM-DDTHH:MM:SSZ`), then the raw excerpt in a code block directly
  beneath the link. Nothing between the link and the excerpt.
- Excerpts are verbatim: not reformatted, reordered, trimmed inside, or
  corrected. A slice of a long response says where it starts and ends.
- An empty result is proven by the complete raw response (status line,
  headers in order, blank line, body), never asserted.
- Near matches that were checked and ruled out are listed under "Checked and
  excluded" with the identifier as shown and the reason, in the same block
  form as a kept result.
- A value the source does not show is reported as "not shown", never filled.
- Nothing is claimed about the subject beyond what the sources show; the
  scope line says what the report is and is not.

---

Report skeleton begins

# <Report title: service name, subject or subjects, date>

<Scope line: what this report is and is not, in one sentence.>
This report was produced by unattended agent work using public sources only.

## Scope and inputs

- Requested by: <platform job reference, as given>
- Inputs as received: <the exact subject names, URLs, addresses, or
  identifiers the buyer supplied, verbatim>
- Sources used: <each public source, by name, with its base URL>
- Retrieval window: <first and last retrieval time in UTC>
- Not in scope: <what was not checked, so the buyer does not read it in>
- Dataset requested: <what the rows are, in the buyer's words>
- Columns requested: <the column list as agreed>
- Sources named by the buyer or agreed: <each, with base URL>
- Delivered file: `<filename>.csv`, <N> rows, <M> columns, UTF-8, header row
  included, <delimiter> delimited.
- Row count arithmetic: <rows from Q1> + <rows from Q2> + ... = <N>.

## Column dictionary

| Column | Meaning | Source field it is copied from | Transformation |
|---|---|---|---|
| `<column>` | <what it holds> | <source name and field name as shown> | <"none (copied as shown)" or the exact rule, e.g. "date reformatted from DD/MM/YYYY to YYYY-MM-DD"> |

Two columns are mandatory in every dataset delivery:

| Column | Meaning |
|---|---|
| `source_record_id` | The source's own identifier for the record the row was built from, as shown. |
| `source_query` | The query id (Q1, Q2, ...) from the Sources section whose response contains the record. |

## Collection method

- For each source: the endpoint or page, the exact query or queries (listed
  in Sources), paging followed (which pages, how many results per page as the
  source reported), and the stopping rule.
- Filters applied after collection, if any, with the exact rule and the count
  of rows removed by each.
- De-duplication rule, if any, and the count removed.
- Nothing is computed, inferred, or looked up elsewhere to fill a cell. A
  cell the source does not show is empty in the CSV and the dictionary says
  so.

## Per source sections

### Source 1: <source name>

- Queries run: Q1 to Q<n> (Sources section).
- Rows produced: <count>.
- Records returned but not used: <count>, listed under Checked and excluded
  with reasons.
- Empty queries: <list, each proven by its complete raw response in Sources>.

### Source 2: <source name>

<same structure>

## Sample rows

Up to five rows of the delivered CSV, verbatim, with their `source_record_id`
and `source_query`, so the buyer can follow one row to one excerpt:

```
<header row>
<row>
<row>
```

## Checked and excluded

Near matches that were fetched, read, and ruled out. Each is listed in the
same block form as a kept result, with the identifier as shown in the source
and the reason it is excluded. If nothing was excluded, this section says
"None: every fetched record is reported above" and stays in the report.

### <Identifier as shown in the source>

- Query that returned it: <query id from the Sources section, e.g. Q2>
- Record as shown: <the identifying fields, as shown>
- Checked and excluded because: <the reason, in plain words>

## Sources

One entry per query, in the order the queries were run. Every figure, date,
name, score, and identifier in the body appears in an excerpt here. Each entry
gives the source name, the exact query, the UTC retrieval time, and the raw
excerpt in a code block directly beneath the link.

### Source Q1 — <source name>, <what the query was for>

<exact query URL, or "POST <URL>" with the exact request body quoted below,
or the exact form fields used>

```
<raw excerpt, verbatim: the complete raw response for an empty result; for a
long response a contiguous slice, stating where it starts and ends>
```
Retrieved: <YYYY-MM-DDTHH:MM:SSZ>

### Source Q2 — <source name>, <what the query was for>

<...>

Report skeleton ends

---

## Service checklist (before delivering)

- [ ] Every row carries `source_record_id` and `source_query`, and the
      excerpt for that query in Sources contains that record identifier.
- [ ] The column dictionary names, for every column, the source field it is
      copied from and the exact transformation or "none".
- [ ] The collection method states every query, the paging followed, every
      post-collection filter with its removed count, and the de-duplication
      rule with its removed count.
- [ ] Row count arithmetic adds up across sources and matches the file.
- [ ] Every empty query is proven by its complete raw response.
- [ ] Records returned but not used are listed as checked and excluded with
      reasons; none is silently dropped.
- [ ] No cell is filled from memory, inference, or an unnamed source; a value
      the source does not show is an empty cell.
- [ ] The delivered CSV, the sample rows, and the counts in the report agree.

