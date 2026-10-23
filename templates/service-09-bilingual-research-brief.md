# Template: Bilingual Research Brief: English and Chinese Public Sources

Catalog service 9, as named in the task issue for these templates.

Source: [issue #29, D: Delivery templates for services 7 to 10](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/29)
> - Service 9: Bilingual Research Brief: English and Chinese Public Sources

The same issue states the service specific point this template encodes, in the sentence that names all four:

> For each service, a template in the style of the existing `templates/` folder: a report skeleton (title, scope and inputs, per subject sections in the delivery format, a checked and excluded section, a sources list) plus the service specific checklist points (for example: dataset templates name the exact queries, collection method, and source record identifier for every row; the bilingual template prints Chinese excerpts in the original beside their translations; the code review template states plainly it is a review, not an audit certification).

> **Template.** Text in angle brackets like `<this>` is a placeholder to
> replace. Every placeholder must be filled from a source that was actually
> fetched, or deleted. No figure, name, date, score, or identifier in a
> finished report may come from anywhere but a fetched source named in its
> Sources section. This template contains no example data.

A research brief built from named public sources in English and Chinese.
Every Chinese excerpt is printed in the original, and any translation sits
beside it, marked as the agent's translation. The source text is the
evidence; the translation is a reading aid and is never quoted as if it were
the source.

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
- Question asked: <the buyer's question, verbatim>
- Languages of sources used: English, Chinese (<Simplified, Traditional, or
  both, as found>)
- Translation: <"agent translation, marked as such beside each excerpt"; no
  machine translation service was called unless named here as a source with
  its own query and time>

## Findings

Each finding is one claim, its source link, and the raw excerpt directly
beneath. For a Chinese source the excerpt is the original text as shown, and
the translation follows it in a separate, labelled block.

### Finding 1: <one claim, in one sentence>

Source: <source name>, <exact URL>, retrieved <YYYY-MM-DDTHH:MM:SSZ>
(source Q1)
```
<excerpt in the original language, verbatim>
```
Translation (agent's, not source text):
```
<translation of exactly the excerpt above, nothing more>
```

### Finding 2: <one claim>

<same structure; an English source needs no translation block>

## What the sources do not say

Questions the buyer asked that no fetched source answers. Each names the
queries run (Sources section) and states that the result is "not shown by the
sources fetched", never that the answer is no.

## Source list by language

| Query | Source | Language | Publisher as shown | Date on the page as shown |
|---|---|---|---|---|
| Q1 | <name> | <zh-Hans / zh-Hant / en> | <as shown> | <as shown or "not shown"> |

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

- [ ] Every Chinese excerpt appears in the original, verbatim, and its
      translation is in a separate block labelled as the agent's translation.
- [ ] No translation is quoted as source text and no finding rests on a
      translation alone; the original is always printed.
- [ ] Every finding is one claim with its source link and the raw excerpt
      directly beneath.
- [ ] Each source entry records the exact URL and the UTC retrieval time,
      and the source table names the language and publisher as shown.
- [ ] Questions the sources do not answer are stated as "not shown by the
      sources fetched", with the queries listed, never as a negative finding.
- [ ] No fact is added from memory or from an unnamed source; nothing is
      summarised beyond what the excerpts show.
- [ ] If a translation service was used, it is named as a source with its
      own query and time; otherwise the brief says no service was called.

