# Template: Smart Contract Code Review: Read Only Review of a Public Solidity Contract

Catalog service 10, as named in the task issue for these templates.

Source: [issue #29, D: Delivery templates for services 7 to 10](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/29)
> - Service 10: Smart Contract Code Review: Read Only Review of a Public Solidity Contract

The same issue states the service specific point this template encodes, in the sentence that names all four:

> For each service, a template in the style of the existing `templates/` folder: a report skeleton (title, scope and inputs, per subject sections in the delivery format, a checked and excluded section, a sources list) plus the service specific checklist points (for example: dataset templates name the exact queries, collection method, and source record identifier for every row; the bilingual template prints Chinese excerpts in the original beside their translations; the code review template states plainly it is a review, not an audit certification).

> **Template.** Text in angle brackets like `<this>` is a placeholder to
> replace. Every placeholder must be filled from a source that was actually
> fetched, or deleted. No figure, name, date, score, or identifier in a
> finished report may come from anywhere but a fetched source named in its
> Sources section. This template contains no example data.

A read only review of published Solidity source. The reviewer reads the
code and reports what it says, with every observation tied to a quoted line
range. This is a review, not an audit certification: it does not certify the
contract safe, does not test it, and does not run it unless a run is shown.

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
- Contract reviewed: <name as shown in the source>
- Where the source was read: <explorer verified-source page URL with chain
  and address, or repository file URL pinned to a commit hash>
- Compiler version and settings as shown: <as shown, or "not shown">
- Deployed address and chain, if any: <as shown on the explorer, or "not
  deployed / not checked">
- What was not reviewed: <dependencies, libraries, proxies, off-chain
  components, deployment scripts, test suites, as applicable>
- Tests or tools run: <"none; read only" or the exact command and its
  complete output quoted in Sources>

## Scope statement (fixed wording)

This is a read only code review of the source named above. It is not an
audit, not a certification, and not a statement that the contract is safe or
free of defects. Findings are the reviewer's reading of the quoted code at the
quoted commit or verified source; anything not quoted was not reviewed.

## Contract summary as read

- Purpose as stated in the source's own comments: <quoted, or "no stated
  purpose in the source">
- Public and external functions: <list, each with its line range in the
  source as read>
- Access control as read: <which functions check what, with line ranges>
- Funds flow as read: <where value enters, is held, and leaves, with line
  ranges>

## Findings

Each finding is one observation about quoted code. Severity is the reviewer's
opinion and is labelled as such.

### Finding 1: <one sentence observation>

- Location: <file, line range, at commit <hash> or verified source as of
  <retrieval time>>
- Severity (reviewer's opinion): <informational / low / medium / high>
- What the code does, as read: <plain words>
- Why it matters: <plain words, no speculation beyond the quoted code>

Source: <URL of the file at the commit, or the explorer verified-source page>
```solidity
<the exact lines quoted, verbatim, with their line numbers>
```
Retrieved: <YYYY-MM-DDTHH:MM:SSZ>

### Finding 2: <one sentence observation>

<same structure>

## Observations that are not findings

Things read and considered that do not rise to a finding, each with its line
range, so the buyer sees what was looked at.

## Not reviewed

What this review did not cover, named plainly.

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

- [ ] The scope statement is present in its fixed wording: a review, not an
      audit or certification, no claim of safety.
- [ ] Every finding quotes the exact lines it is about, verbatim with line
      numbers, beneath a link to the file at a commit hash or the explorer
      verified-source page, with the UTC retrieval time.
- [ ] Severity is labelled as the reviewer's opinion.
- [ ] Nothing is said about code that is not quoted; "Not reviewed" names
      what was left out.
- [ ] No test, tool, or execution result is claimed unless the exact command
      and its complete output are quoted in Sources.
- [ ] No deployment, balance, transaction, or ownership figure appears unless
      it was read from a named explorer page with its excerpt and time.
- [ ] No private key, seed phrase, wallet material, or account detail of any
      party appears anywhere in the report.

