# Deployment notes: recall check MCP server on MCPize

Status: **draft, nothing deployed.** These notes exist so the coordinator
can confirm each step before anything is done under the owner's account.
Steps marked "to confirm" could not be checked against MCPize's published
docs from the build environment (the host was unreachable) and must be
read there before use; nothing below should be taken as how MCPize works
until that reading is done.

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
2. **Manifest and metadata**: to confirm. Write the file(s) MCPize requires,
   using only the values fixed above: entry command `python3 -m mcp_server`,
   working directory the repository root, runtime Python 3.10+, system
   dependency `curl`, environment value `PAYOUT_WALLET_ADDRESS` (set on the
   platform side, value never committed), tool `recall_check` with the
   schema from `LISTING.md`. Add the file(s) to this folder and extend the
   test in `tools/tests/test_mcpize_listing.py` to check the entry command
   and tool name in them.
3. **Local check with the packaging in place**: run
   `python3 -m unittest discover -s tools/tests -v` (all suites) and the
   try-it command in `mcp_server/README.md`; the packaged server must answer
   the sample query with the same text the core gives.
4. **Price and payout settings**: to confirm. Where MCPize takes the per
   call price and the payout wallet, and in what units. The suggested price
   and its reasoning are in `LISTING.md`; the wallet is the owner's, set by
   the owner, never written here.
5. **Listing**: to confirm. Where the title, description and tool summary
   from `LISTING.md` go, and any length limits. The copy states only what
   the server demonstrably does; shorten by cutting, never by adding.
6. **Go live**: only after the coordinator has confirmed steps 2, 4 and 5 in
   writing on issue #38, and only by the owner or on the owner's explicit
   instruction. Record the deployment URL and date on issue #38 when done.

## To confirm from the MCPize docs

Each item needs a quoted excerpt and its URL before it is acted on.

- Manifest file name, format, and required fields.
- How the entry command, working directory and runtime version are declared.
- Whether a system dependency (`curl`) can be declared, and how; if it
  cannot, the CPSC form cannot run there and the listing must say so.
- How environment values are set for a hosted server, so the payout wallet
  never enters the repo.
- Per call pricing: units, minimum, and where it is set.
- Payout: the creator share, the payout token and chain, and any KYC or
  account requirement, quoted from the platform. The task text says USDC on
  Base at an 80 percent creator share; that is unverified until read there.
- Any health check, timeout, or request size limit the host imposes; a
  single recall check can return a response body of some hundred kilobytes
  (the raw source response is printed in full by design).
