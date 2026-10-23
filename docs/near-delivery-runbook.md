# NEAR delivery runbook: from start to submitted

This is the runbook for issue
[#135](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/135). It
covers the NEAR AI Agent Market delivery path (`https://market.near.ai`)
as the first real assignment actually ran it. That assignment is
`87d3fce7-5c3d-4950-adfe-b7bfc911a571`: job 40976130, Agent Builder Supply
Research, run on 2026-10-23. The runbook is for two things: let the next delivery
repeat the run, and keep it clear of the two traps the run hit.

This file is repo work only. Nothing in it was started, submitted or sent
from this repo. Every platform act below is the operator's.

## Where the facts come from

There are two sources, and each step below names which one it uses.

- **The run record.** The repo does not hold the 87d3fce7 run record, so
  it was asked for on #135 (comment 6373742560). The coordinator supplied
  it in
  [comment 6373979132](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/135#issuecomment-6373979132).
  That comment quotes the program delivery record (`near-state.md`,
  section "ASSIGNMENT 87d3fce7 DELIVERED") and adds one live read. Its
  honesty note applies to every step here:

  > Important honesty note up front: the raw HTTP response bodies were NOT retained; what was retained is the delivery run's contemporaneous record, quoted below.

  Raw bodies were not kept, so the field values below are the record's
  own words, not response captures. Where the record does not hold
  something, this runbook says **NOT OBSERVED** and leaves it out.

- **The platform OpenAPI document**, as quoted on #48 in
  [comment 6356778084](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/48#issuecomment-6356778084):
  `https://market.near.ai/openapi.json`, retrieved about 03:37 UTC on
  2026-10-23 by the coordinator. The same source sits behind
  `near-agent/README.md` and `near-agent/tests/fixtures/provenance.json`.
  The document itself is not in this repo.

The delivery run sent its requests through the registered NEAR connector
and a local POST helper. Neither is in this repo, and this runbook does
not cover authentication.

## The assignment, as recorded at the start of the run

Source: comment 6373979132.

> Assignment: 87d3fce7-5c3d-4950-adfe-b7bfc911a571, job 40976130 (Agent Builder Supply Research), bid e9fc2ebf accepted, created 2026-10-23T19:03:37Z, status in_progress, escrow 5 USDC, slaSeconds 86400, slaDeadlineAt 2026-10-24T19:03:37Z.

The deadline is the assignment's own `slaDeadlineAt`. `slaSeconds` 86400
gives 24 hours from creation. That window is the one the deadline guard in
`near-agent/worker.py poll` watches (see `near-agent/README.md`,
"Deadline guard").

## Step 1. Start, then read it back

**The call.** It is in the OpenAPI document (comment 6356778084):

> - Start: POST /v1/assignments/{id}/start , no request body in the spec; response carries startedAt.

**What the run observed.** Source: comment 6373979132.

> 1. START. Record verbatim: 'Started: POST /v1/assignments/87d3fce7-5c3d-4950-adfe-b7bfc911a571/start returned HTTP 200, startedAt 2026-10-23T19:29:23.567275Z; read back confirmed status in_progress, escrowAmount 5, slaDeadlineAt 2026-10-24T19:03:37Z.' The full raw start response body is NOT RECORDED beyond those fields.

**Do this:**
1. Send the start call with no body.
2. Read the assignment back.
3. Before writing, check three things: the status is `in_progress`, the
   escrow amount matches the bid, and you know the `slaDeadlineAt`.

The full start response body is **NOT OBSERVED**. The record keeps only
the fields quoted above.

## Step 2. Write the deliverable in the shape the job asked for

The shape comes from the job text, not from a house template. For this
job, the record holds the job text as it read at award. Source: comment
6373979132.

> 8. DELIVERABLE SHAPE. From the job text as recorded at award: 'English Markdown research report, 1,000 to 2,500 words plus tables, lead answer paragraph, every factual claim cited with a URL actually opened, estimates marked, closing section "What Agent Market should do next" with at most five ranked recommendations.'

And as delivered:

> As delivered, per the record: 'Report: 1,487 words of prose plus tables, 17 unique cited URLs, all opened.'

The structure of the delivered report, per the same comment:

> The delivered Markdown lives in the program files, NOT in this repo, and carries the full job title as its heading, an Answer first lead paragraph, a Method and date note, then headed sections and tables, closing with the recommendations section.

**The order the run used:**
1. the full job title as the heading;
2. the answer paragraph;
3. a note on method and dates;
4. headed sections and tables;
5. the closing recommendations section, named as the job names it.

Before submitting, check the word count against the job's range. Also
check that every cited URL was actually opened.

The delivered file is not in this repo. This runbook gives its structure
only and does not restate its content.

## Step 3. Submit, with a JSON body

**The call.** It is in the OpenAPI document (comment 6356778084):

> - Submit: POST /v1/assignments/{id}/submit , body SubmitRequest: required deliverableMarkdown (string); optional files (string array).

**The body the run sent.** Source: comment 6373979132.

> 2. SUBMIT REQUEST SHAPE. Record verbatim: 'Submitted: POST /v1/assignments/87d3fce7-5c3d-4950-adfe-b7bfc911a571/submit with JSON body {"deliverableMarkdown": <report>, "files": []} per the playbook (market.near.ai/skill/SKILL.md).'

> So files held nothing: an empty list, no names or types.

The request body is JSON, and the Markdown report is the string value of
`deliverableMarkdown`. Sending the Markdown file as the body is wrong.
`files` was an empty list on this run, so no run has yet observed `files`
with content. The playbook page named in the record
(`market.near.ai/skill/SKILL.md`) was cited by the delivery run. It was
not fetched for this runbook.

`near-agent/worker.py submit` builds the body `{"deliverableMarkdown": ...}`
and never sends `files` (`near-agent/README.md`). That fits the OpenAPI,
where `files` is optional. The 87d3fce7 run did not use `worker.py`: it
used the local POST helper.

### Trap 1: the helper crashed, so check the read back before you call it

The first submit attempt never reached the platform. Source: comment
6373979132.

> 5. HELPER CRASH. Record verbatim: 'First attempt never reached the platform: the local POST helper was handed the Markdown file where it expects a JSON body file and crashed parsing it'.

> The read back that DID happen was after the failed first attempt: 'the assignment read back showed submittedAt still null, so the retry was the first real platform attempt.'

The helper's exact error output is **NOT OBSERVED**: the record does not
hold it. The helper is outside this repo.

**Rule.** A local POST helper that expects a JSON body file will crash on
a Markdown body. A crash or an error on your side does not tell you
whether the submit landed. Before you treat a submit as landed **or** as
failed, read the assignment back and check `submittedAt`:
- `submittedAt` is null: nothing reached the platform, and a retry is
  the first real attempt (as here).
- `submittedAt` is set, or the assignment has left the active list (step
  4): the submit landed. Do not send it again.

## Step 4. Keep the submit response: it is the record

**The response the run got.** Source: comment 6373979132.

> 3. SUBMIT RESPONSE. Record verbatim: 'Retry returned HTTP 200: status "submitted", submittedAt 2026-10-23T19:38:13.497088Z, deliverableHash 80b2b099f8ad2ac292b57aa8927dbae41efc2800ddb68345c912e0e69cd7aff0, deliverableUrl deliverables/managed/87d3fce7-5c3d-4950-adfe-b7bfc911a571/80b2b099f8ad2ac2.md.'

These are the fields that prove a submission:
- `status` is `"submitted"`;
- `submittedAt` holds a timestamp;
- `deliverableHash` and `deliverableUrl` are present.

On this run, the first 16 hex characters of `deliverableHash` were the
file name in `deliverableUrl`.

### Trap 2: after submission, the assignment leaves the active list

Source: comment 6373979132.

> 6. ACTIVE LIST. Record verbatim: 'Post submit poll note: GET assignments now returns an empty list; submitted work leaves the active assignments view. The submit response itself is the platform record of the submission.' Confirmed again live this run (item 4).

> A coordinator live assignments read this run (2026-10-23 about 20:25 UTC) still returns {"assignments": []}.

**Rule.** Save the submit response fields (step 4 list) in the delivery
record as soon as the response arrives. Once submitted, the assignment is
gone from `GET /v1/agents/me/assignments`. No later read back showed
`submittedAt` on the assignment, and this run had no other place to read
it from. So **NOT OBSERVED**: any read after submission that shows the
assignment with `submittedAt` set.

This also limits what a poll can see. The deadline guard in
`near-agent/worker.py poll` checks open assignments, those with a null
`submittedAt`. A submitted assignment drops out of the poll, so the poll
cannot show acceptance either.

## Step 5. The acceptance window

Source: comment 6373979132.

> 7. ACCEPTANCE WINDOW. Record verbatim: 'State now: awaiting buyer acceptance (acceptanceWindowDays 3, so auto accept by about 2026-10-26T19:38Z if the buyer does nothing).

> acceptanceWindowDays 3 is the observed field; a per assignment autoAcceptAt value is NOT RECORDED.

After submission the buyer has the window that the job's
`acceptanceWindowDays` sets. It was 3 here, and the same field appears on
the captured board job in `near-agent/tests/fixtures/board-excerpt.json`.
The record expects auto acceptance about three days after `submittedAt`
if the buyer does nothing.

**NOT OBSERVED** on this run:
- the per assignment `autoAcceptAt` value. The OpenAPI wraps assignment
  rows as `MyAssignmentItem {assignment, job, latestMessage, autoAcceptAt}`
  (comment 6356778084), but the record does not hold a value.
- an acceptance, whether by the buyer or automatic.
- a release of escrow.

As of the record, the assignment was awaiting acceptance. The record's
note on what happens at acceptance (comment 6373979132, item 7) is a
statement of expected behaviour, not an observation from this run. The
owner withdraws any funds; that is never a repo step.

## Checklist for the next NEAR delivery

1. Read the assignment and note `slaDeadlineAt` (the assignment record
   above).
2. Start with no body, then read back the status, the escrow and the
   deadline (step 1).
3. Write the deliverable in the job's own shape, and check the word range
   and the cited URLs (step 2).
4. Submit a JSON body with `deliverableMarkdown` as a string, never the
   Markdown file as the body (step 3).
5. If anything on your side errors, read back `submittedAt` before you
   retry or report a failure (trap 1).
6. Save `status`, `submittedAt`, `deliverableHash` and `deliverableUrl`
   from the submit response at once, because the assignment then leaves
   the active list (step 4, trap 2).
7. Note the acceptance window from `acceptanceWindowDays`. Record an
   acceptance only when one is actually observed (step 5).

## Not observed on the 87d3fce7 run

Each item below is either NOT RECORDED in comment 6373979132 or never
happened on this run, so none of it is stated as platform behaviour
above:
- the full raw start response body;
- every raw HTTP response body (not retained);
- the local POST helper's exact error output;
- a submit with a non empty `files` list;
- a read after submission showing the assignment with `submittedAt` set;
- the per assignment `autoAcceptAt` value;
- a buyer acceptance, an auto acceptance, or an escrow release;
- whether the API submit is the same act as the job page's submit button
  (open question 1 in the agent runbooks, e.g.
  `agents/video-clipping/RUNBOOK.md`).
