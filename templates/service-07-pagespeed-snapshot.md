# Template: Website SEO and Core Web Vitals Snapshot from PageSpeed Insights

Catalog service 7. The service description this template follows is the one in the task issue for its fetcher.

Source: [issue #25, A: PageSpeed Insights fetcher in tools/](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/25)
> Workstream A style tooling for the catalog service "Website SEO and Core Web Vitals Snapshot from PageSpeed Insights" (service 7 in the service catalog). No fetcher exists for it yet; deliveries are built by hand.
>
> Build one small command line fetcher in `tools/` that:
>
> - Takes up to five page URLs.
> - Measures each with the public Google PageSpeed Insights API, which runs Lighthouse against the live page.
> - Emits one Markdown section in the delivery format from `AGENT-BRIEF.md`: per page, the performance, accessibility, best practices, and SEO category scores the API returns, plus the lab metrics behind the performance score (Largest Contentful Paint, Cumulative Layout Shift, Total Blocking Time), each quoted from the API response, with the raw excerpt printed directly beneath the source link.
> - Records the exact request and the UTC time it was run; the report reads as a snapshot of that moment, not a permanent grade. A page the API cannot measure is shown with the error response printed in full, never skipped silently.

> **Template.** Text in angle brackets like `<this>` is a placeholder to
> replace. Every placeholder must be filled from a source that was actually
> fetched, or deleted. No figure, name, date, score, or identifier in a
> finished report may come from anywhere but a fetched source named in its
> Sources section. This template contains no example data.

A snapshot report: what the PageSpeed Insights API returned for each
requested page at the moment it was run. It is not a grade of the site, not
an audit, and not a prediction of search ranking. Scores and metrics change
from run to run; the report says so in its scope line and dates every figure.

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
- Pages requested: <up to five URLs, verbatim as supplied>
- Strategy requested: <mobile or desktop, as the API call was made; one
  report per strategy if both were requested>
- API key: <"none used" or "a free public key supplied at run time from the
  environment; the key is not reproduced here">

## Page 1: <URL as requested>

Snapshot at <YYYY-MM-DDTHH:MM:SSZ> (source Q1). Strategy: <mobile/desktop>.
Final URL the API reports testing: <as shown in the response, or "not shown">.

### Category scores as shown

| Category | Score as shown in the response |
|---|---|
| Performance | <as shown> |
| Accessibility | <as shown> |
| Best Practices | <as shown> |
| SEO | <as shown> |

Scores are copied exactly as the response shows them, in the response's own
scale, with no rounding or conversion. If the response omits a category, the
row says "not shown".

### Lab metrics behind the performance score, as shown

| Metric | Value as shown | Unit as shown |
|---|---|---|
| Largest Contentful Paint | <as shown> | <as shown> |
| Cumulative Layout Shift | <as shown> | <as shown> |
| Total Blocking Time | <as shown> | <as shown> |

### Page the API could not measure

If the API returned an error for this page, this section replaces the two
tables: it names the HTTP status and the error message as shown, and source
Q<n> prints the complete raw error response. The page is never dropped from
the report.

## Page 2: <URL as requested>

<same structure>

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

- [ ] Every page the buyer supplied appears in the report, measured or with
      its full error response printed; none is skipped silently.
- [ ] Every score and metric is copied exactly as the API response shows it,
      in the response's own scale and unit, with the raw excerpt that contains
      it printed beneath the source link.
- [ ] Each page's source entry records the exact request URL (with the key
      value removed and marked as removed if one was used) and the UTC time.
- [ ] The scope line says this is a snapshot of one run at a stated time, not
      a permanent grade or a ranking prediction.
- [ ] No field is named that the response does not contain; a missing field
      is "not shown".
- [ ] No recommendation, estimate, or comparison appears that the responses
      do not themselves state.
- [ ] No key, token, or account detail appears anywhere in the report.

