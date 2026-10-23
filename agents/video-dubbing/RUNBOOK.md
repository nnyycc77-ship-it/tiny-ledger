# Award runbook: Video Dubbing Agent

Issue #98. Turns an award on NEAR Agent Market job `2f1d5b6b-691f-4642-916a-570d340a4fb4` into a live, hireable agent. Built from issue #77, `agents/video-dubbing/README.md`, and the worker loop in `near-agent/` (PR #52). Every step is grounded in that code, its README or the job text posted on the task issue; anything this repo cannot ground is listed under **Open questions** and is never guessed. This file creates no token, touches no listing and makes no call.

## The award at a glance

| Item | Value | Source |
| --- | --- | --- |
| Job | `2f1d5b6b-691f-4642-916a-570d340a4fb4` | issue #77 |
| Bid | 125 USDC | board update on #22 (2026-10-23 12:31 UTC) |
| Build deadline | working, listed agent within 5 days of award | same |
| Agent code | `agents/video-dubbing` | `agents/video-dubbing/README.md` |
| Delivery clock | runs from the award, frozen by the bid SLA | issue #98 |

## 1. What the award brings and where it appears

- The job text (posted verbatim on the task issue) says: build the agent, list it on Agent Market, then submit the listing URL as the job deliverable; "a link posted only in the job thread is not a submission". Testing follows within the job's review window; if it fails, the market requests changes with test findings, and a new version is submitted.
- The worker's read path for assignments is `GET /v1/agents/me/assignments` (`worker.py poll`). Run it with the token of the account that placed the bid to see the assignment id and status:

```sh
NEAR_AGENT_TOKEN=... python3 near-agent/worker.py poll
```

- Exactly what the award message contains and which account's assignments list shows it: **open question 6**.

## 2. Owner steps (checklist)

- [ ] Create the agent shell for this agent in the Agent Market web UI. *Open question 1.*
- [ ] Mint its token through the Secure Vault flow and hand it to the worker host's environment only (`NEAR_AGENT_TOKEN`), never to a file in this repo. *Open question 2.*
- [ ] Decide anything this agent needs before going live (listed under **Live dependencies**).
- [ ] Approve the listing copy (the README's listing draft) and the price and window below.

## 3. Agent side steps, in order

1. **Check out main and run the offline suite.** It must be green before anything else:

   ```sh
   python3 -m unittest discover -s agents/video-dubbing/tests -v
   python3 -m unittest discover -s tools/tests -v
   python3 tools/pregate.py
   ```

2. **Check the live dependencies** below on the host that will run the agent.

3. **Configure the worker with the new token** the way `near-agent/README.md` ("Runbook", step 1) prescribes: export `NEAR_AGENT_TOKEN` in the shell or have the scheduler inject it. Confirm it with a read only poll; a 401 or 403 is a stop condition (see the failure table):

   ```sh
   NEAR_AGENT_TOKEN=... python3 near-agent/worker.py poll --state /path/outside/repo/state.json
   ```

4. **Set price and delivery window on the listing.** The bid (125 USDC) is the build fee the market pays for this job, not a per hire price, and no per hire price or per hire delivery window is recorded in this repo: *open question 7*. The 5 days from award is the deadline for a working, listed agent, which this runbook is built to meet. How price and window are set (UI or endpoint): *open question 3*.

5. **Publish the listing** from the README's listing draft (owner approved). *Open question 3.*

6. **One live dry run hire** against our own research agent account, where the platform allows. *Open question 5.* If it is not allowed, run the agent's own dry run on its fixtures as `agents/video-dubbing/README.md` documents (`python3 agents/video-dubbing/dubber.py --help` confirms the CLI loads) and record that the live hire path was not exercised.

7. **Submit the listing URL as the job deliverable** through the assignment submit path. Dry run first, read the printed request, then add `--execute` (the operator's act):

   ```sh
   NEAR_AGENT_TOKEN=... python3 near-agent/worker.py submit ASSIGNMENT_ID --text "Listing: <listing URL>"
   NEAR_AGENT_TOKEN=... python3 near-agent/worker.py submit ASSIGNMENT_ID --text "Listing: <listing URL>" --execute
   ```

   Whether this is the same act as the job page's "Submit deliverable": *open question 4*. Never post the link only as a `message`; the job text says a thread link is not a submission.

## Live dependencies

- The translation provider shipped is `stub`, an offline test stub that the report marks "not a deliverable"; the background separator `duck` is a local ffmpeg fallback, not true source separation (README, "Providers"). A real translator and voice provider must be wired before a listing can pass the job's tests; that choice and any spend are owner decisions at award (README).
- No real person's voice is cloned anywhere in this build; a cloning provider is added only after an award and an owner decision (README).

## Failure table

| Failure | First move |
| --- | --- |
| Token refused (401 or 403 on `poll`) | Stop; the worker has already exited 2 (near-agent README, stop conditions). The owner re-checks or re-mints the token through the vault flow and re-injects it into the environment. Never edit a file here to fix it. |
| Listing rejected | Read the rejection reason, fix the listing copy against the README's listing draft and the job's requirements (category, name, what buyers provide, locations, window, FAQ), and republish. Where a reason names behaviour, reproduce it with the offline suite first. |
| Test failure inside the window | Reproduce the market's test findings locally with `python3 -m unittest discover -s agents/video-dubbing/tests -v`, fix in a small PR through the normal review gate, and submit a new version through the submit path above. If the fix cannot land inside the window, send the buyer a short status through `worker.py message` (dry run first). |
| 429 or 5xx from the market | Stop polling and wait for the operator (near-agent README, stop conditions). |
| A response shape the worker does not recognise | Stop; the API changed. Update the documented shape before trusting any digest. |

## Open questions

Not grounded in this repo's code or docs; asked on issue #98. Until answered they are not guessed:

1. **Agent shell:** how the owner creates the new agent (web UI only or an endpoint) and what it yields (agent id, handle). Not recorded in this repo; asked on issue #98.
2. **Token:** the Secure Vault flow that mints the agent's token, and whether that token is the per agent bearer that `/v1/agents/me/assignments` accepts. Not recorded in this repo; asked on issue #98. This runbook assumes one worker invocation per agent with that agent's token in `NEAR_AGENT_TOKEN`; the worker itself reads only that variable.
3. **Listing, price and delivery window:** how a listing is created and published and how price and delivery window are set (UI or endpoint), and what the listing URL looks like. The worker has no listing command. Asked on issue #98.
4. **Submission path:** whether `POST /v1/assignments/{id}/submit` with the listing URL in `deliverableMarkdown` (`worker.py submit`) is the same act as the job page's "Submit deliverable" button or `marketplace__submit_deliverable` over MCP, which the job text names. Asked on issue #98.
5. **Self hire dry run:** whether the platform lets our own research agent account hire the new agent, and by which path. The worker has no hire command. Asked on issue #98.
6. **Award notice:** what an award looks like and where it lands (an assignment in `/v1/agents/me/assignments`, a message, a job status). Asked on issue #98.
7. **Per hire price and window:** the per hire listing price and per hire delivery window. Issue #98 says to set them "from the bid", but the bid amount is the build fee and the bid proposals posted on the task issues state a build deadline, not a per hire price. To confirm with the owner before publishing; not guessed.

## Sources

- `near-agent/worker.py` and `near-agent/README.md` (PR #52): commands, the `NEAR_AGENT_TOKEN` rule, dry run and `--execute`, stop conditions, and the endpoint sources quoted on issue #48.
- The job text and bid proposal posted verbatim on issue #77; the build, list and submit sequence quoted above is from the job text verified on issue #76 (sha256 `03fa1d4e…`), which the market's build jobs share.
- `agents/video-dubbing/README.md` for the agent's commands, tests and live dependencies.
- Board update on issue #22, 2026-10-23 12:31 UTC, for the bid and promised window.
