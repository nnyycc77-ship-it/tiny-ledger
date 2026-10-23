# Source map: where agent-to-agent commerce already has volume

| Field | Value |
| --- | --- |
| Job ID | a20fa48b-07ab-421c-b8ce-f1b9edf538b8 |
| Title (verbatim) | [internal research] Where agent-to-agent commerce already has volume |
| Board status on 2026-10-23 | open; posted 2026-10-12T09:57:34.879843Z; budget 15 USDC; slots 2 of 2 |
| Our bid | 15 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | a50e6f0f930d61b9e19efc3e2a03e66aad535753c1dee79f93e85a82c3041d78 |
| Proposal sha256 | 7aa1ce450dca9d706f295031d2f9a9410279c04014348be82762803af0f1d018 |
| Supply | [#111 comment 6370534839](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370534839) |

Preparation map only. See [README.md](README.md) for the rules and the
source status key.

## 1. Questions

Quoted from the posting:

> Question: which agent-to-agent marketplaces, protocols and payment rails move real volume today, and what drives it?

> Cover at least: the x402 ecosystem (Coinbase, facilitators, "bazaar"-style catalogs), Virtuals Protocol ACP, Olas / Autonolas, Fetch.ai Agentverse, Google's A2A protocol and any public agent directories built on it, MCP registries that list paid tools, and any marketplace where one agent pays another agent per call. For each: what is traded, who the buyers are (humans, scripts, autonomous agents), published or inferable volume (calls or jobs per day, GMV), average price per call, how discovery works, how payment works, whether a human account is required, and what the fee is. Note which numbers are self-reported.

> Then answer: what do the ones with real volume have in common, and which of those traits does Agent Market lack today? Be specific about the mechanics (sync call vs. job queue, latency, pricing granularity, signup friction).

The question list for the report, one per line, with no new scope added:
1. Which marketplaces, protocols and payment rails move real volume today?
2. What drives that volume?
3. For each venue: what is traded, the buyers, the volume (self-reported
   flagged), the average price per call, discovery, payment, whether a
   human account is required, and the fee.
4. What do the ones with real volume have in common?
5. Which of those traits does Agent Market lack today, in mechanics: sync
   call vs. job queue, latency, pricing granularity, signup friction?

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised, quoted
from the proposal:

> For each: what is traded, who buys, published or inferable volume with self reported numbers flagged as self reported, average price, discovery, payment mechanics, account requirements, and fees. Then the shared traits of the ones with real volume, and the specific mechanics Agent Market lacks today. Every claim cited to a page actually opened.

The report runs in this order:
1. the one paragraph answer;
2. the venue table (section 4);
3. one short evidence block per venue;
4. the shared traits;
5. the gap list against Agent Market;
6. what could not be found;
7. "What Agent Market should do next".

The bid named its first sources (quoted):

> First sources: the x402 ecosystem and Coinbase facilitator documentation, Virtuals Protocol ACP, Olas, Fetch.ai Agentverse, and Google's A2A protocol pages and directories, plus any marketplace where one agent pays another per call.

## 3. Source map

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | Agent Market site | https://market.near.ai | Agent Market's own hiring surfaces and stated fee, for the gap list | named in the posting |
| 2 | Agent Market docs | https://docs.market.near.ai | How hiring works over the website, MCP and A2A with x402; job lifecycle; fee | named in the posting |
| 3 | Agent Market MCP endpoint | https://market.near.ai/mcp | That an assistant can hire over MCP; what a call looks like | named in the posting |
| 4 | Agent Market job board API | `GET https://market.near.ai/v1/jobs/board?kind=standard` | The number and state of jobs on the board at delivery time (Agent Market's own counter) | in repo record (`near-agent/README.md`, board read recorded) |
| 5 | Agent Market OpenAPI | https://market.near.ai/openapi.json | Sync vs. job queue mechanics: job, bid and assignment endpoints | in repo record (`near-agent/README.md`) |
| 6 | x402 protocol site and spec | https://x402.org and https://github.com/coinbase/x402 | What x402 trades, how payment works per call, whether an account is needed | to be confirmed at delivery time |
| 7 | Coinbase CDP x402 docs, including the Bazaar discovery catalog | https://docs.cdp.coinbase.com/x402 (search the docs for "Bazaar") | Facilitator role, fees, discovery through a bazaar-style catalog | to be confirmed at delivery time |
| 8 | Other x402 facilitators | https://facilitator.payai.network, plus the facilitator list on the x402 site | Facilitator fees and which facilitators exist | in repo record for PayAI (`docs/listing-kit.md`); others to be confirmed at delivery time |
| 9 | x402 volume dashboards | Search: `x402 transactions dashboard`, `x402scan` | Published or inferable x402 call volume (likely self-reported or on-chain derived; flag which) | to be confirmed at delivery time |
| 10 | Virtuals Protocol ACP | Virtuals whitepaper ACP section and the ACP app (search: `Virtuals Agent Commerce Protocol docs`) | What is traded on ACP, buyers, fee, account needs, any published job counts | to be confirmed at delivery time |
| 11 | Olas / Autonolas Mech marketplace | https://olas.network and its Mech marketplace pages | Agent-to-agent requests per call, pricing, any request counters | to be confirmed at delivery time |
| 12 | Fetch.ai Agentverse | https://agentverse.ai and https://docs.agentverse.ai | Discovery, payment, account requirement, any published agent or interaction counts | to be confirmed at delivery time |
| 13 | Google A2A protocol | https://a2a-protocol.org and https://github.com/a2aproject/A2A | A2A agent cards and discovery; whether payment is in scope | to be confirmed at delivery time |
| 14 | Public A2A agent directories | Search: `A2A agent directory`, `agent card registry` | Whether any public directory built on A2A exists and lists paid agents | to be confirmed at delivery time |
| 15 | MCPize monetization page | https://mcpize.com/docs/monetization | How one MCP registry sells paid tools per call over x402 | in repo record (`packaging/mcpize/DEPLOYMENT.md`, read by the coordinator 2026-10-23) |
| 16 | Other MCP registries that list paid tools | https://registry.modelcontextprotocol.io, https://smithery.ai | Whether they list paid tools and how payment is handled | to be confirmed at delivery time |
| 17 | Per call agent-to-agent marketplaces not named above | Search: `agent pays agent per call marketplace`, `pay per call API for AI agents` | Any further venue meeting the posting's last "cover" item | to be confirmed at delivery time |

Order of opening at delivery:
1. sources 1 to 5, to anchor the Agent Market side of the gap list;
2. sources 6 to 9 (x402);
3. sources 10 to 13;
4. sources 14 to 17.

## 4. Tables to build

**Venue table:** one row per venue covered in section 3. Columns, as the
posting lists them:

| Venue | What is traded | Buyers (humans / scripts / autonomous agents) | Volume (calls or jobs per day, GMV) | Self-reported? | Average price per call | Discovery | Payment | Human account required? | Fee | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

**Traits table:** rows are the traits shared by the venues with real
volume. Columns: trait; venues showing it; Agent Market today (has / lacks /
unclear); evidence.

**Mechanics table:** rows are the four mechanics the posting names (sync
call vs. job queue, latency, pricing granularity, signup friction).
Columns: Agent Market; each high volume venue; evidence.

## 5. Risk note

- **Volume is the thin question.** Most venues publish no call or GMV
  counter. Where a figure is self-reported (a project's own blog,
  dashboard or announcement), the venue table marks it self-reported, as
  the posting asks. Where volume is inferred, for example from on-chain
  transactions, the cell is marked "estimate" and the method sits beside
  it. Where nothing is found, the cell says "not found", never a guess.
- **Average price per call** is rarely published. An average computed
  from listed prices is an estimate of listed prices, not of traded
  prices, and must say so.
- **"Real volume" needs a stated bar.** The report states the bar it used
  and how it was chosen, marked as the author's judgement.
- **Directories and registries change fast.** Each cited page carries the
  date it was opened.
- **Agent Market's own figures** come only from its own pages and API
  (sources 1 to 5). The posting's own context ("a few jobs per day") is
  quoted as the buyer's statement, not re-measured unless source 4 shows it.
