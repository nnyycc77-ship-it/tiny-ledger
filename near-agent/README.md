# near-agent: self hosted worker for the NEAR AI Agent Market

Task: issue #48. This folder holds the agent side loop for the Hojo
Research Agent's listing on the NEAR AI Agent Market
(`https://market.near.ai`), run from code in this repo instead of by hand.
One file, `worker.py`, standard library only. Its tests live in `tests/`
and are also discovered by the CI job through `tools/tests/test_near_agent.py`.

Status: see the "Sources" section at the end for which parts of the
marketplace API this folder has documentation for. An action whose
endpoint is not recorded there is refused by the program, not guessed.

## What it does

| Command | Reads or sends | Default |
| --- | --- | --- |
| `poll` | `GET /v1/agents/me/assignments` and `GET /v1/jobs/board?kind=standard` | runs; read only |
| `start ASSIGNMENT_ID` | the start request for an assignment | dry run |
| `message ASSIGNMENT_ID --text ...` | a message on an assignment | dry run |
| `submit ASSIGNMENT_ID --text ...` | a submission on an assignment | dry run |
| `bid JOB_ID --amount ... --note ...` | a bid on a board job | dry run |

A dry run prints the exact request the program would send (method, URL,
every header with the token shown as a placeholder, and the body) and
sends nothing. Adding `--execute` sends it. There is no `--execute` for
`poll`.

The poll digest prints: the assignment count and ids; the board job
count; and every job whose id is new or whose budget changed since the
previous poll. The previous poll is kept in a small state file holding job
ids and budgets only (never a response body, never the token).

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
   NEAR_AGENT_TOKEN=... python3 near-agent/worker.py poll
   ```

   The state file defaults to `~/.local/state/near-agent/state.json`
   (`XDG_STATE_HOME` honoured), which is outside the repository. To keep it
   elsewhere pass `--state PATH`; inside this folder, `state/` and
   `*.state.json` are gitignored. `--repeat N --interval S` polls N times S
   seconds apart (minimum 30 seconds); any error stops the loop.

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

The two read paths and the environment variable name come from the task
text of issue #48:
<https://github.com/nnyycc77-ship-it/tiny-ledger/issues/48>.

The marketplace's response fields and the four action endpoints are not
yet recorded here. Until they are, `poll` and every act command stop with
"not recorded in this repo yet" and send nothing.
