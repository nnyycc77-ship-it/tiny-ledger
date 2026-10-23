# Deployment notes: recall check MCP server on MCPize

Status: **draft, nothing deployed.** These notes exist so the coordinator
can confirm each step before anything is done under the owner's account.
MCPize's pages were not reachable from the build environment; the MCPize
facts below come from the coordinator's reading of the published docs on
2026-10-23, recorded on pull request #44 and quoted here beneath its link
with the page URLs the coordinator cited. Items still marked "to confirm"
need the page itself read before use.

## What the server is

- Code: `mcp_server/` on `main` (merged in PR #41). One Model Context
  Protocol server over stdio (JSON-RPC 2.0, newline delimited).
- Entry point: `python3 -m mcp_server`, run from the repository root.
- One tool: `recall_check`. Arguments: `product`, `exact_name`, `near`
  (product form, CPSC SaferProducts) or `make`, `model`, `year`, `exclude`
  (vehicle form, NHTSA recalls). Full schema: the server's own `tools/list`
  response, reproduced in [`LISTING.md`](LISTING.md).
- Output: the recall check as Markdown in the repo's fixed evidence format;
  a failed fetch or bad request is a tool error (`isError: true`), never an
  empty result.

## Prerequisites known from the core (no docs needed)

1. Python 3.10 or later.
2. `curl` on PATH. The CPSC fetcher captures responses with the system curl
   executable (`tools/README.md`).
3. Outbound HTTPS to `www.saferproducts.gov` and `api.nhtsa.gov`. The
   server fetches live on every call and caches nothing; if the host
   cannot reach these, every call returns a fail closed tool error.
4. No Python packages. No API keys. No secrets of any kind.
5. One optional environment value: `PAYOUT_WALLET_ADDRESS`, the EVM address
   (0x plus 40 hex digits) that receives USDC per call. The server refuses
   to start on a malformed value and runs without one when it is unset. It
   is set in the host's environment, never in a file in this repo.
6. The repository checkout, since the server imports `api/recall_api.py`
   and `tools/` as library code. The entry point must run with the
   repository root as the working directory.

## Steps

1. **Read the MCPize docs** (coordinator or a helper with access) and fill
   the "to confirm" items below with quoted excerpts and their page URLs,
   in this file, before any other step.
2. **Manifest**: [`mcpize.yaml`](mcpize.yaml) in this folder, built from the
   coordinator's reading of the publish page (quoted under "MCPize facts"
   below). It declares runtime `python3.12`, entry `mcp_server/__main__.py`,
   a stdio start command `python3 -m mcp_server` with bridge mode, and the
   `recall_check` tool. Before deployment, check the nesting of
   `startCommand` and the bridge mode key against the page itself, since
   only the field list was read, not an example file. Runtime: the core
   requires Python 3.10 or later; the publish page names 3.11 or 3.12; the
   manifest declares 3.12, which satisfies both.
3. **Local check with the packaging in place**: run
   `python3 -m unittest discover -s tools/tests -v` (all suites) and the
   try-it command in `mcp_server/README.md`; the packaged server must answer
   the sample query with the same text the core gives.
4. **Price and payout settings**: configured in the MCPize dashboard, not in
   `mcpize.yaml`. The two documented routes conflict: the monetization page
   describes a pricing block in `mcpize.yaml`, while the publish page says
   pricing is configured via the dashboard, and the monetization page says
   the dashboard is the source of truth at runtime (quotes below). This
   deployment uses the dashboard route, so no price, network, or recipient
   wallet ever enters this public repo, and `mcpize.yaml` carries no pricing
   block on purpose. Set there: per tool price 1.00 USDC for `recall_check`
   (the suggestion and its arithmetic are in `LISTING.md`; the documented
   range is 0.01 to 100 USDC), asset USDC, network `base-sepolia` for the
   test deployment and `base` for production, and the recipient wallet, which
   is the owner's, set by the owner, never written here.
5. **Listing**: to confirm. Where the title, description and tool summary
   from `LISTING.md` go, and any length limits. The copy states only what
   the server demonstrably does; shorten by cutting, never by adding.
6. **Go live**: only after the coordinator has confirmed steps 2, 4 and 5 in
   writing on issue #38, and only by the owner or on the owner's explicit
   instruction. Record the deployment URL and date on issue #38 when done.

## MCPize facts, as read by the coordinator

Source: [coordinator review on pull request #44](https://github.com/nnyycc77-ship-it/tiny-ledger/pull/44#issuecomment-6356274881), citing the publish page https://mcpize.com/developers/publish-mcp-server and the monetization page https://mcpize.com/docs/monetization, both read 2026-10-23.
> 1. Add the MCPize manifest the task requires. The build environment could not reach MCPize, but the coordinator read the published docs from a working environment on 2026-10-23, so the docs gap is now fillable. Source: https://mcpize.com/developers/publish-mcp-server, which gives mcpize.yaml as the deployment configuration (version, name, description, runtime, entry, build, startCommand with type http, sse, or stdio, and bridge mode for stdio servers) and lists the server runtimes as Python 3.11 or 3.12 in its server configuration notes. Add a mcpize.yaml for this server using only the values fixed by the merged core (entry python3 -m mcp_server from the repo root, stdio bridge), fill the manifest, entry, and runtime items under To confirm from the MCPize docs in DEPLOYMENT.md with quoted excerpts and that page URL, and reconcile the runtime version: the core states Python 3.10 or later, the publish page names 3.11 or 3.12, so the manifest must declare a docs supported runtime or the notes must flag the difference explicitly.
>
> 2. Fill the pricing and payout items under To confirm from the quoted monetization docs. Source: https://mcpize.com/docs/monetization (read by the coordinator 2026-10-23): pay per call pricing lives in a pricing block in mcpize.yaml (protocol x402, network base-sepolia for testing then base for production, asset usdc, per tool price a string between 0.01 and 100 USDC), default revenue share 80 percent, the dashboard is the source of truth at runtime, and the recipient is a wallet the creator controls that MCPize never custodies. Reconcile that page with the publish page, which states pricing is configured via the MCPize Dashboard, not in the YAML file. Keep the owner wallet address OUT of this repo, as this PR already does and as the task acceptance requires (no platform config files): the recipient is set on the platform side at deployment, and the notes should say which of the two documented routes the deployment will use. The suggested 1.00 USDC price itself passes: it is inside the documented 0.01 to 100 range and its arithmetic is sourced in LISTING.md.

Read from those two quotes and used above: the manifest is `mcpize.yaml`
with fields version, name, description, runtime, entry, build, and
startCommand (type http, sse, or stdio; bridge mode for stdio servers);
server runtimes Python 3.11 or 3.12; pay per call pricing with protocol
x402, asset USDC, network base-sepolia for testing then base for
production, per tool price a string between 0.01 and 100 USDC; default
revenue share 80 percent; the dashboard is the source of truth at runtime
and the publish page places pricing configuration in the dashboard; the
recipient is a wallet the creator controls and MCPize never custodies.

## To confirm from the MCPize docs

Each remaining item needs the page itself read, with a quoted excerpt and
its URL added here, before it is acted on.

- The exact nesting of `startCommand` and the key for bridge mode in
  `mcpize.yaml` (only the field list was read, not an example file), and
  what the `version` field means (this file uses the server version).
- Whether a system dependency (`curl`) is available or declarable on the
  host; if it is not, the CPSC form cannot run there and the listing must
  say so.
- How environment values are set for a hosted server, so the payout wallet
  never enters the repo.
- Any KYC or account requirement for payouts, quoted from the platform.
- Any health check, timeout, or request size limit the host imposes; a
  single recall check can return a response body of some hundred kilobytes
  (the raw source response is printed in full by design).
