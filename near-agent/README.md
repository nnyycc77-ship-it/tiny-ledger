# near-agent: self hosted worker for the NEAR AI Agent Market

Task: issue #48. This folder holds the agent side loop for the Hojo
Research Agent's listing on the NEAR AI Agent Market
(`https://market.near.ai`), run from code in this repo instead of by hand.
One file, `worker.py`, standard library only. Its tests live in `tests/`
and are also discovered by the CI job through `tools/tests/test_near_agent.py`.

Every endpoint path and field name the program uses is cited in the
"Sources" section at the end. An action or field the cited documents do not
name is refused by the program, not guessed.

## What it does

| Command | Reads or sends | Default |
| --- | --- | --- |
| `poll` | `GET /v1/agents/me/assignments` and `GET /v1/jobs/board?kind=standard` | runs; read only |
| `start ASSIGNMENT_ID` | the start request for an assignment | dry run |
| `message ASSIGNMENT_ID --text ...` | `POST /v1/assignments/{id}/messages`, body `{"body": ...}` | dry run |
| `submit ASSIGNMENT_ID --text ...` | `POST /v1/assignments/{id}/submit`, body `{"deliverableMarkdown": ...}` | dry run |
| `bid JOB_ID --amount ... --note ...` | `POST /v1/jobs/{id}/bids`, body `{"amount": ..., "proposal": ...}` | dry run |

`start` is `POST /v1/assignments/{id}/start` with no body. Optional spec
fields (`attachmentIds`, `clientRequestId`, `files`, `slaSeconds`) have no
CLI option and are never sent; `agentId` and `asSelf` are not sent either,
because for an agent token the bidder is pinned from the token.

A dry run prints the exact request the program would send (method, URL,
every header with the token shown as a placeholder, and the body) and
sends nothing. Adding `--execute` sends it. There is no `--execute` for
`poll`.

The poll digest prints: the assignment count and ids; the board job
count; and every job whose id is new or whose budget changed since the
previous poll. The previous poll is kept in a small state file holding job
ids and budgets only (never a response body, never the token). Each poll
also runs a config validation pass first and a deadline guard on the open
assignments (Runbook, step 2).

## Runbook

1. **Token.** The agent API token comes from the environment variable
   `NEAR_AGENT_TOKEN` and from nowhere else. Export it in the shell that
   runs the worker, or have the scheduler inject it. It is never read from
   a file in this repo, never written to the state file, and never printed:
   every output line passes through a redaction step, and the Authorization
   header is printed as
   `Bearer <redacted, supplied from the environment variable NEAR_AGENT_TOKEN>`.
   Without the variable the program stops with exit 2 before building any
   request.

2. **Poll.** From the repository root:

   ```sh
   NEAR_AGENT_TOKEN=... NEAR_AGENT_HANDLE=<listing slug> python3 near-agent/worker.py poll
   ```

   Before the first request, the poll validates its config. It reports
   every problem at once, one named reason each, then exits 2 with nothing
   sent (issue #110). The checks:

   - **`NEAR_AGENT_TOKEN`**, by shape only: the `aat_` prefix of a per
     agent token (coordinator answer on #98, comment 6368327577), then no
     whitespace. The value is never shown.
   - **`NEAR_AGENT_HANDLE`**: the agent's listing slug, as in
     `market.near.ai/a/<slug>`. It labels the deadline alarms and is never
     sent in a request.
   - **`--repeat` and `--interval`.**
   - **`NEAR_AGENT_SUBMIT_MAX_BYTES`** (optional; default 262144): a
     narrower submit limit that must lie within the marketplace rule of
     1 byte to 256 KiB. That rule is recorded in issue #110, and is read
     here as the UTF-8 byte length of `deliverableMarkdown`. The submit
     path itself does not enforce the limit.

   The act commands do not run this pass and are unchanged.

   **Deadline guard.** After both reads of a poll parse, the guard checks
   every open assignment, meaning one whose `submittedAt` is null. It uses
   the assignment's own `slaDeadlineAt`, with the window taken from
   `slaSeconds`, or else from `startedAt` to `slaDeadlineAt` (OpenAPI
   `JobAssignment` fields, quoted on issue #48). It raises an escalating
   alarm at three points:

   - `half`: half the window or less left;
   - `quarter`: a quarter or less left;
   - `final`: under two hours left with no submit recorded, which includes
     past the deadline.

   An assignment whose deadline cannot be read raises `unreadable` instead
   of being skipped. Each alarm does three things:

   - appends one JSON line to `alarms.log`;
   - writes the marker file `<assignmentId>.json`, which remembers the
     highest level reached so that each level fires once;
   - prints the same line on stderr after `ALARM `.

   These are the only files the guard writes. They go in `alarms/` beside
   the state file, or in `--alarm-dir DIR`. A marker that cannot be read
   stops the poll (exit 2) before the state is saved. Move the marker
   aside to reset it.

   The state file defaults to `~/.local/state/near-agent/state.json`
   (`XDG_STATE_HOME` honoured), which is outside the repository. To keep it
   elsewhere pass `--state PATH`; inside this folder, `state/` and
   `*.state.json` are gitignored. `--repeat N --interval S` polls N times S
   seconds apart (minimum 30 seconds); any error stops the loop.

   To see the digest without sending anything, replay the two saved
   response bodies in `tests/fixtures`:

   ```sh
   NEAR_AGENT_TOKEN=aat_placeholder-for-replay-only NEAR_AGENT_HANDLE=replay-check python3 near-agent/worker.py poll \
     --state /tmp/near-agent-replay.json \
     --replay-assignments near-agent/tests/fixtures/assignments-empty.json \
     --replay-board near-agent/tests/fixtures/board-excerpt.json
   ```

   The token is still required (one rule, no exceptions), but a replay
   builds no connection, so any string of the token's shape works there.
   `tests/fixtures/assignments-deadline-SYNTHETIC.json` is a SYNTHETIC
   assignments body: replay it with `--alarm-dir` pointed at a scratch
   folder to see the deadline guard fire.

3. **Dry run first, always.** Run an act command without `--execute`, read
   the printed request, and only then decide. A bid is never sent by this
   tool on its own: `--execute` on `bid` is the operator's act, and it
   needs the coordinator's separate approval first, outside this tool.

4. **Stop conditions.** Stop the loop and do not retry when:
   - the token is missing or any request answers 401 or 403 (the token is
     wrong or revoked; fix it out of band, never by editing a file here);
   - a request answers 429 or any 5xx (rate limited or the service is
     unwell; wait for the operator before polling again);
   - the program reports a response shape it does not recognise (the API
     changed; update the documented shape before trusting any digest);
   - the state file cannot be parsed (move it aside; the next poll starts
     a fresh snapshot and reports every job as new);
   - anything suggests a bid, start, message or submit went out that the
     operator did not run with `--execute`.
   In every case the program has already exited 2 with the reason on
   stderr; it never prints a digest from a response it did not understand.

## Hard limits this folder keeps

- Nothing here talks to the live marketplace as part of the task or the
  tests. The test suite uses a placeholder token string and a fake
  transport that records requests instead of sending them.
- The real transport sends only to `https://market.near.ai`, follows no
  redirect, and refuses any other scheme or host.
- No secret, key, token or wallet value is committed anywhere in this
  folder. The token is a runtime environment value only.

## Verification

```sh
python3 -m unittest discover -s near-agent/tests -v
python3 -m unittest discover -s tools/tests -v        # includes the loader
```

## Sources

The two read paths (`/v1/agents/me/assignments`, `/v1/jobs/board?kind=standard`)
and the environment variable name are fixed by the task text of issue #48:
<https://github.com/nnyycc77-ship-it/tiny-ledger/issues/48>.

The build environment for this folder cannot reach `market.near.ai`, and
the task forbids live calls, so the coordinator read the two sources below
from a working environment on 2026-10-23 and quoted them on issue #48. The
fixture provenance file `tests/fixtures/provenance.json` records the same
facts next to the files.

1. **Captured responses** (coordinator, registered NEAR connector read,
   about 2026-10-23T03:36Z), quoted at
   <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/48#issuecomment-6356778084>
   and <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/48#issuecomment-6356778439>:
   - `GET /v1/agents/me/assignments` answered `{"assignments": []}`,
     kept verbatim as `tests/fixtures/assignments-empty.json`.
   - `GET /v1/jobs/board?kind=standard` answered HTTP 200 with 32 job objects
     (129,848 bytes; full body SHA-256
     `46226e14044ad4cb53f111856e747220b1c8a91f6aafabe1cceeb8ed65639e8c` as
     reported by the coordinator). `tests/fixtures/board-excerpt.json` is
     the first job object, verbatim, inside a `jobs` array: a one job
     excerpt, labelled as such in its provenance. The digest reads `jobs[]`,
     `jobId`, `budgetAmount`, `budgetToken` and `title` from this shape.
2. **OpenAPI document** <https://market.near.ai/openapi.json> (coordinator,
   about 2026-10-23T03:37Z, document SHA-256
   `a53af35b919984af572e453a868f1ebc32fd3f9383afa09538efa3e4bf6e9782` as
   reported), quoted in the first comment above. It gives the four act
   endpoints and their request bodies (`SendMessageRequest`,
   `SubmitRequest`, `PlaceBidRequest`) and the assignment schemas
   (`JobAssignment` inside `MyAssignmentItem {assignment, job,
   latestMessage, autoAcceptAt}`), which is where the digest reads
   `assignments[].assignment.assignmentId` and `.status`. The document
   itself is not in this repo.

Not verified from this folder: the live behaviour of any endpoint. No
request was sent to `market.near.ai` while building or testing this code.
