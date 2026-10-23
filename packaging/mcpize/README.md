# MCPize packaging (B2 of issue #33)

Part 2 of the recall check MCP server: the material needed to list and
deploy the merged core (`mcp_server/`, issue #37, PR #41) on MCPize, which
is described in the task that created this work as follows.

Source: [issue #33, B: Recall check MCP server for MCPize](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/33)
> MCPize (mcpize.com) hosts MCP servers itself and settles per call payments in USDC on Base to the seller wallet at an 80 percent creator share, which removes the hosting blocker that parked the pay per call API.

That sentence is the coordinator's description in the task, not text read
from the platform; nothing in this folder has been checked against MCPize's
own pages yet (see "What is not here").

**Nothing is deployed, submitted, or listed anywhere.** This folder is
drafting material inside the repo. Deployment goes ahead only on steps the
coordinator has confirmed, and nothing goes live under the owner's account
before that confirmation.

## What is here

| File | Contents |
| --- | --- |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Every prerequisite and step known from the merged core, and the platform specific steps marked as still to be confirmed from the MCPize docs. |
| [`LISTING.md`](LISTING.md) | Draft listing copy: title, description, tool summary, one example rendered from a recorded source response, and a per call price suggestion with its arithmetic and sources. |
| [`mcpize.yaml`](mcpize.yaml) | The MCPize deployment configuration, built from the coordinator's reading of the publish page; no pricing or wallet fields, by design. |

The core itself is untouched by this folder. Its entry point is
`python3 -m mcp_server` from the repository root; its behaviour, tests and
configuration are documented in [`mcp_server/README.md`](../../mcp_server/README.md).

## What was read, and how

MCPize's pages were not reachable from the environment that built this
folder (`mcpize.com`, `www.mcpize.com`, `docs.mcpize.com` and
`mcpize.com/docs` all failed at the network layer on 2026-10-23). The
coordinator read the publish and monetization pages from a working
environment the same day and recorded the reading on pull request #44;
`DEPLOYMENT.md` quotes that reading beneath its link with the page URLs,
and `mcpize.yaml` is built from it. The items that still need the page
itself (the exact nesting of the start command and bridge key, `curl`
availability, environment values, KYC terms, host limits) are listed in
`DEPLOYMENT.md` under "To confirm". No pricing or payout value is in this
repo: pricing and the recipient wallet are set in the MCPize dashboard at
deployment, the route the notes choose and explain.

## Verification

```sh
python3 -m unittest discover -s tools/tests -p 'test_mcpize_listing.py' -v
```

The test re-renders the recorded CPSC capture through the real server
(offline, fetcher patched) and checks the example in `LISTING.md` equals
that output byte for byte, that the tool name and every argument named in
the listing match the server's live `tools/list` schema, that the track
record paragraph quoted in the listing matches `AGENT-BRIEF.md` byte for
byte, that `mcpize.yaml` names the entry command and the `recall_check`
tool and carries no pricing or wallet field, and that no file in this
folder claims a deployment or listing has been done.
