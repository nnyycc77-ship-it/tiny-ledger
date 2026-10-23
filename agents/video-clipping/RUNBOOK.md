# Award runbook: Video Clipping Agent

Issue #98. Turns an award on NEAR Agent Market job `06d8adcb-4635-4d54-83df-4ef7bbbc8344` into a live, hireable agent. Built from issue #74, `agents/video-clipping/README.md`, and the worker loop in `near-agent/` (PR #52). Every step is grounded in that code, its README, the job text posted on the task issue, or the coordinator answer on issue #98 (quoted under **Grounded answers**, citing the program record and the OpenAPI spec supplied on issue #48) for the platform's web UI, token, submit path and award notice; anything not grounded is listed under **Open questions** and is never guessed. This file creates no token, touches no listing and makes no call.

## The award at a glance

| Item | Value | Source |
| --- | --- | --- |
| Job | `06d8adcb-4635-4d54-83df-4ef7bbbc8344` | issue #74 |
| Bid | 150 USDC | board update on #22 (2026-10-23 12:31 UTC) |
| Build deadline | working, listed agent within 5 days of award | same |
| Agent code | `agents/video-clipping` | `agents/video-clipping/README.md` |
| Delivery clock | runs from the award, frozen by the bid SLA | issue #98 |

## 1. What the award brings and where it appears

- The job text (posted verbatim on the task issue) says: build the agent, list it on Agent Market, then submit the listing URL as the job deliverable; "a link posted only in the job thread is not a submission". Testing follows within the job's review window; if it fails, the market requests changes with test findings, and a new version is submitted.
- The worker's read path for assignments is `GET /v1/agents/me/assignments` (`worker.py poll`). Run it with the token of the account that placed the bid to see the assignment id and status:

```sh
NEAR_AGENT_TOKEN=... NEAR_AGENT_HANDLE=<listing slug> python3 near-agent/worker.py poll
```

- The award itself: "An accepted bid becomes an assignment that appears in the assignments read (GET /v1/agents/me/assignments via the connector), carrying its delivery deadline. A row with startedAt null is a fresh hire" (answer F). Bid status is readable in the my bids read; no separate award message channel is recorded.

## 2. Owner steps (checklist)

- [ ] Create the agent shell for this agent in the Agent Market web UI under the owner's account session (Building, Your agents, New agent). No endpoint for this is recorded. *Answer A.*
- [ ] Create its API token in the same UI under Agent API tokens (shown once), store it through the Secure Vault API access flow (connection `custom.near-agent-market`), and hand it to the worker host's environment only (`NEAR_AGENT_TOKEN`), never to a file in this repo. *Answers A and B.*
- [ ] Decide anything this agent needs before going live (listed under **Live dependencies**).
- [ ] Approve the listing copy (the README's listing draft) and decide the per hire price and window (*open question 3*).
- [ ] Create, price and publish the listing on the agent's Edit page in the web UI (steps 4 and 5). The API token cannot do this. *Answer C.*

## 3. Agent side steps, in order

1. **Check out main and run the offline suite.** It must be green before anything else:

   ```sh
   python3 -m unittest discover -s agents/video-clipping/tests -v
   python3 -m unittest discover -s tools/tests -v
   python3 tools/pregate.py
   ```

2. **Check the live dependencies** below on the host that will run the agent.

3. **Configure the worker with the new token** the way `near-agent/README.md` ("Runbook", step 1) prescribes: export `NEAR_AGENT_TOKEN` in the shell or have the scheduler inject it, together with `NEAR_AGENT_HANDLE` (the listing slug from `market.near.ai/a/<slug>`, which labels the worker's deadline alarms). Confirm it with a read only poll: the poll first validates its config and names every problem (exit 2, nothing sent), and a 401 or 403 is a stop condition (see the failure table). The poll also runs the deadline guard, which writes an escalating alarm (`alarms.log` plus a marker file) at half the window left, a quarter left, and under two hours left with no submit recorded (`near-agent/README.md`):

   ```sh
   NEAR_AGENT_TOKEN=... NEAR_AGENT_HANDLE=<listing slug> python3 near-agent/worker.py poll --state /path/outside/repo/state.json
   ```

4. **Set price and delivery window on the listing.** The bid (150 USDC) is the build fee the market pays for this job, not a per hire price, and no per hire price or per hire delivery window is recorded: *open question 3*. The 5 days from award is the deadline for a working, listed agent, which this runbook is built to meet. The owner sets price and window on the agent's Edit page in the web UI, under the owner's account session; the API token "cannot create or edit listings, prices, or settings" (answers A and C), and the worker has no listing command.

5. **Publish the listing** from the README's listing draft (owner approved), on the same Edit page. Note the listing URL; its shape is `market.near.ai/a/<slug>` (answer C).

6. **One live dry run hire** against our own account, where the platform allows. *Open question 2.* If it is not allowed, run the agent's own dry run on its fixtures as `agents/video-clipping/README.md` documents (`python3 agents/video-clipping/clipper.py --help` confirms the CLI loads) and record that the live hire path was not exercised.

7. **Submit the listing URL as the job deliverable** through the assignment submit path. Dry run first, read the printed request, then add `--execute` (the operator's act). This is the documented submit path, `POST /v1/assignments/{id}/submit` with the URL in `deliverableMarkdown` (answer D); `ASSIGNMENT_ID` is the id of the assignment row from step 3's poll:

   ```sh
   NEAR_AGENT_TOKEN=... python3 near-agent/worker.py submit ASSIGNMENT_ID --text "Listing: <listing URL>"
   NEAR_AGENT_TOKEN=... python3 near-agent/worker.py submit ASSIGNMENT_ID --text "Listing: <listing URL>" --execute
   ```

   Whether this is the same act as the job page's "Submit deliverable": *open question 1*. Never post the link only as a `message`; the job text says a thread link is not a submission.

## Live dependencies

- `ffmpeg` and `ffprobe` must be on the host's PATH; the suite skips the media tests when ffmpeg is missing (README), so a green run on a host without ffmpeg proves less than it looks. Confirm `ffmpeg -version` first.
- The core path needs no account and no key (README).

## Failure table

| Failure | First move |
| --- | --- |
| Token refused (401 or 403 on `poll`) | Stop; the worker has already exited 2 (near-agent README, stop conditions). The owner re-checks or creates a new token in the web UI (Agent API tokens), stores it through the vault flow and re-injects it into the environment. Never edit a file here to fix it. |
| Listing rejected | Read the rejection reason, fix the listing copy against the README's listing draft and the job's requirements (category, name, what buyers provide, locations, window, FAQ), and republish. Where a reason names behaviour, reproduce it with the offline suite first. |
| Test failure inside the window | Reproduce the market's test findings locally with `python3 -m unittest discover -s agents/video-clipping/tests -v`, fix in a small PR through the normal review gate, and submit a new version through the submit path above. If the fix cannot land inside the window, send the buyer a short status through `worker.py message` (dry run first). |
| 429 or 5xx from the market | Stop polling and wait for the operator (near-agent README, stop conditions). |
| A response shape the worker does not recognise | Stop; the API changed. Update the documented shape before trusting any digest. |

## Grounded answers

The coordinator answered the runbook questions on issue #98 (2026-10-23), citing the NEAR Agent Market connector doc in the program record and the OpenAPI spec supplied on issue #48. Each claim below is followed by its source and the raw excerpt, verbatim (`[...]` marks an omitted span):

**A. Agent shell.** The owner creates the agent shell in the web UI; the per agent token is created in the same UI and shown once; no endpoint for shell creation is recorded.

Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>

```text
1. Agent shell: web UI only. The owner creates the agent shell under the account session in the web UI (Building, Your agents, New agent). The per agent API token is created in the same UI, under Agent API tokens, and is shown once. The API token cannot create or edit listings, prices, or settings; those live on the agent's Edit page under the owner's account session.
```

**B. Token.** The token is a per agent bearer token stored through the Secure Vault flow; one worker invocation per agent with that agent's token in `NEAR_AGENT_TOKEN` is confirmed.

Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>

```text
2. Token: the token is minted in the web UI as above, then stored through the Secure Vault API access flow (connection custom.near-agent-market) and verified working by the coordinator. It is a per agent bearer token (aat_ prefix). Your assumption is correct and matches the merged worker loop: one worker invocation per agent, with that agent's token in NEAR_AGENT_TOKEN. The token can work jobs and bid; it cannot create or edit listings.
```

**C. Listing, price and delivery window.** The listing is created and published, and its price and window set, on the agent's Edit page in the web UI; the listing URL has the shape `market.near.ai/a/<slug>`.

Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>

```text
3. Listing: created and published in the web UI under the owner's account session; price and delivery window are set there (Edit page). Listing URL shape: market.near.ai/a/<slug>
```

**D. Submission path.** The documented submit path is `POST /v1/assignments/{id}/submit` with `deliverableMarkdown`; its equivalence to the job page button is not verified (open question 1).

Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>

```text
4. Submission: the assignment submit path in the record is POST /v1/assignments/{id}/submit with a SubmitRequest whose required field is deliverableMarkdown (OpenAPI, supplied on #48). [...] Whether the API submit is the identical act as the job page Submit deliverable button is NOT verified in the program record: mark that equivalence as an open question in the runbooks, and state the API path as the documented one. The job text rule stands: a link posted only in the job thread is not a submission.
```

**E. Self hire dry run.** Not recorded; stays open question 2.

Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>

```text
5. Self hire dry run: NOT recorded. Whether the platform allows our own account to hire a new agent, and by which path, is unverified in the program record.
```

**F. Award notice.** An accepted bid appears as an assignment in `GET /v1/agents/me/assignments` with its delivery deadline; a row with `startedAt` null is a fresh hire; bid status is in the my bids read; no other award channel is recorded.

Source: <https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>

```text
6. Award notice: grounded in the connector doc. An accepted bid becomes an assignment that appears in the assignments read (GET /v1/agents/me/assignments via the connector), carrying its delivery deadline. A row with startedAt null is a fresh hire, and the row carries the job brief and the latest thread message. Bid status itself is readable in the my bids read (pending, accepted, rejected, withdrawn). No separate award message channel is recorded beyond the assignment appearing.
```

## Open questions

Not grounded in this repo or in the coordinator answer on issue #98. Until answered they are not guessed:

1. **Submission path:** whether `POST /v1/assignments/{id}/submit` with the listing URL in `deliverableMarkdown` (`worker.py submit`) is the same act as the job page's "Submit deliverable" button or `marketplace__submit_deliverable` over MCP, which the job text names. The coordinator answer (answer D below) records the API path as the documented one and says the equivalence "is NOT verified in the program record".
2. **Self hire dry run:** whether the platform lets our own account hire the new agent, and by which path. The worker has no hire command. The coordinator answer (answer E below) says it is "NOT recorded".
3. **Per hire price and window:** the per hire listing price and per hire delivery window for this agent. The coordinator answer (answer C below) says where they are set (the agent's Edit page), not what they are. Issue #98 says to set them "from the bid", but the bid amount is the build fee and the bid proposals posted on the task issues state a build deadline, not a per hire price. To confirm with the owner before publishing; not guessed.

## Sources

- `near-agent/worker.py` and `near-agent/README.md` (PR #52): commands, the `NEAR_AGENT_TOKEN` rule, dry run and `--execute`, stop conditions, and the endpoint sources quoted on issue #48.
- The job text and bid proposal posted verbatim on issue #74; the build, list and submit sequence quoted above is from the job text verified on issue #76 (sha256 `03fa1d4e…`), which the market's build jobs share.
- `agents/video-clipping/README.md` for the agent's commands, tests and live dependencies.
- The coordinator answer on issue #98 (<https://github.com/nnyycc77-ship-it/tiny-ledger/issues/98#issuecomment-6368327577>) for the agent shell, token, listing, submit path and award notice, quoted under **Grounded answers**.
- Board update on issue #22, 2026-10-23 12:31 UTC, for the bid and promised window.
