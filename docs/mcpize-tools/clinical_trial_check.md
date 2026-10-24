# `clinical_trial_check`: Clinical trial check

A tool factory wave 1 tool (issue #162, parent #158).
- **Code:** the fetcher is
  [`tools/clinical_trial_check.py`](../../tools/clinical_trial_check.py). The pay
  per call API serves it as `GET /trials?term=...&limit=...`
  ([`api/endpoints.py`](../../api/endpoints.py)).
- **Registered on the MCP server.** The server on main lists it
  (`tool_definitions()` in `mcp_server/recall_mcp.py`). It was added by
  PR #208 (issue #204), the shared surface step the #158 ruling called for.
  Going live still waits on the owner redeploy step.

## The tool at a glance

- **What it answers:** for one company, drug, or condition, how many
  trials the ClinicalTrials.gov registry reports for that search, and
  what the top trials are, with their status. Each value is shown
  exactly as the API returns it.
- **Source:** ClinicalTrials.gov API v2, the studies search,
  `GET https://clinicaltrials.gov/api/v2/studies`.
  - **Keyless.** No key, account, or Authorization header is used, and
    nothing is read from the environment.
  - **Fields.** The request names the fields the report prints through
    the API's `fields` parameter: `NCTId`, `BriefTitle`,
    `OverallStatus`, `LeadSponsorName`, `Condition`, `Phase`. The
    captured responses in `tools/tests/fixtures/clinical-trials/` show
    the API answering with only those fields, plus `totalCount`, the
    studies array, and a `nextPageToken` when more results follow.
- **Arguments:** `term` (a company, drug, or condition), and an
  optional `limit`, the page size asked for: 1 to 100, default 10. The
  limit is this tool's own cap.
- **Needs on the server:** outbound HTTPS to `clinicaltrials.gov`, and
  no key.
- **What it is not:** medical advice, a judgement of any trial, drug,
  or sponsor, or a statement about whether a trial is open to any
  reader. Statuses mean what ClinicalTrials.gov reports.
- **Price:** 0.25 USDC per call once the shelf goes live. This is the
  shelf price set by the owner's ruling on issue #147
  ([comment 6377953191](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/147#issuecomment-6377953191)).
  Nothing in this PR sets or changes a price.

## What a report contains

- **The request.** The exact query (term, `countTotal`, page size,
  fields, format), the UTC retrieval time, and the HTTP status as
  returned.
- **The count.** `totalCount` as shown, and the number of studies in
  this response. The two differ whenever the count runs past one page;
  both are shown and never reconciled.
- **The top trials.** In response order, per study, each as shown or
  "not shown" when the response omits that module or field:
  - `nctId` and `briefTitle` (identificationModule);
  - `overallStatus` (statusModule);
  - the lead sponsor name (sponsorCollaboratorsModule);
  - `conditions` (conditionsModule) and `phases` (designModule).
- **The page note.** How many of the counted trials are shown, and
  whether the response carries a `nextPageToken`, as shown.
- **The evidence.** The complete raw response under the source link.

**Empty:** a response with `totalCount` 0 and an empty studies array
is reported as "the search returned no trials", with the complete raw
response as the proof. It is not claimed as proof that no matching
trial exists.

**Failures:** these give no report, with exit 2 on the CLI and 502 on
the API:
- any status other than 200;
- a body that is not a JSON object with an integer `totalCount` and a
  studies array of objects;
- a failed request.

A source failure is never shown as an empty result.

## Running it

```sh
python3 tools/clinical_trial_check.py "elivaldogene"
```

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_clinical_trial_check.py' -v
```

The tests run offline:
- **Fixtures:** two live captures made by the builder with the tool's
  own fetch on 2026-10-24, in `tools/tests/fixtures/clinical-trials/`
  with their hashes in `provenance.json`: a hit (elivaldogene, four
  studies of a `totalCount` of 4, the first study with an empty
  designModule, so its phases read "not shown"; the response carries
  no `nextPageToken`, and the token present case is covered in the
  tests by a derived variant labelled there) and an empty result
  (an invented term, `totalCount` 0). Fixture transcripts omit any
  Set-Cookie header; the bodies are byte for byte as returned.
- **Failure shapes** (a 503, a non JSON body, a JSON body in the wrong
  shape, a transport failure) are built in the test file and labelled
  SYNTHETIC there; they are not recordings.
- **Live smoke run:** the builder ran the tool live in the PR, with
  the retrieval time stamped in the report it printed.
