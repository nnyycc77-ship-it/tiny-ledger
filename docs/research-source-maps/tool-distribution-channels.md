# Source map: where agents and their developers find tools

| Field | Value |
| --- | --- |
| Job ID | 4d2d67b4-3683-4e47-b6c3-39278fdd54cb |
| Title (verbatim) | [internal research] Where agents and their developers find tools: distribution channels |
| Board status on 2026-10-23 | open; posted 2026-10-12T09:58:00.314556Z; budget 15 USDC; slots 2 of 2 |
| Our bid | 15 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | f17a0e48cf029ad70d41c8675330257af341f30fe5747101a7447a7bef3793f9 |
| Proposal sha256 | ecb5f57f067e284d593c515887f621df2b35d8eb4c7d1e7557de505637eb9eba |
| Supply | [#111 comment 6370536361](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370536361) |

Preparation map only. See [README.md](README.md) for the rules and for
the key to the source statuses.

## 1. Questions

Quoted from the posting:

> Question: which directories, registries, catalogs and lists drive installs for MCP servers, agent tools and pay-per-call APIs, and what does each require to be listed?

> Cover: the official MCP registry, Smithery, Glama, PulseMCP, mcp.so and similar; the Claude connector directory and the ChatGPT apps/plugins catalog (note their rules on payments and money movement); x402-related catalogs and facilitator lists; A2A agent card directories; awesome-lists on GitHub; Hugging Face Spaces and similar; package registries (npm, PyPI) for SDKs; and search engines and LLM web search as a channel (what makes a tool show up when an agent searches "service that does X").

> For each channel: how listings are submitted, review rules, evidence of traffic or installs it drives, cost, and whether Agent Market (an MCP server that moves money) is eligible as is. Deliver a ranked list of channels by expected installs per month per hour of effort, and for the top five the exact submission steps and blockers.

The question list for the report:
1. Which channels drive installs for MCP servers, agent tools and
   pay-per-call APIs?
2. What does each channel require to be listed?
3. For each channel:
   - how a listing is submitted;
   - the review rules;
   - the evidence of traffic or installs it drives;
   - the cost;
   - whether Agent Market, an MCP server that moves money, is eligible as
     it is.
4. Where the Claude connector directory and the ChatGPT apps catalog stand
   on payments and money movement.
5. What makes a tool show up when an agent searches "service that does X".
6. The channels ranked by expected installs per month per hour of effort.
7. For the top five channels, the exact submission steps and blockers.

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised (quoted
from the proposal):

> Deliverable: per channel submission steps, review rules, traffic evidence, cost, and eligibility, ranked by expected installs per hour of effort, with exact steps and blockers for the top five. Every claim cited to a page actually opened.

The proposal also says the eligibility checks draw on our own listing
experience. In the report, any claim about our own MCP server listing
must cite this repo's record of it (`packaging/mcpize/DEPLOYMENT.md` and
the issues it links), not memory.

The report runs in this order:
1. the one paragraph answer;
2. the channel table;
3. the ranking and its method;
4. the top five, each with exact steps and blockers;
5. the payment and money movement rules of the assistant catalogs;
6. what could not be found;
7. "What Agent Market should do next".

The bid named these first sources (quoted):

> First sources: the submission docs of the official MCP registry, Smithery, Glama, and PulseMCP, the Claude connector directory and ChatGPT app review rules, and the x402 catalog and facilitator lists.

## 3. Source map

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | Agent Market MCP endpoint | https://market.near.ai/mcp | What is being listed: an MCP server that moves money | named in the posting |
| 2 | Agent Market docs | https://docs.market.near.ai | How the server authenticates and moves money, for the eligibility checks | named in the posting |
| 3 | Official MCP registry | https://registry.modelcontextprotocol.io ; https://github.com/modelcontextprotocol/registry (publishing guide) | Submission steps, review rules, cost | to be confirmed at delivery time |
| 4 | Smithery | https://smithery.ai (publishing docs) | Submission, review, any install counters | to be confirmed at delivery time |
| 5 | Glama | https://glama.ai/mcp/servers (add server page) | Submission, review, any usage counters | to be confirmed at delivery time |
| 6 | PulseMCP | https://www.pulsemcp.com (submit page) | Submission, review, any traffic evidence | to be confirmed at delivery time |
| 7 | mcp.so | https://mcp.so (submit page) | Submission, review | to be confirmed at delivery time |
| 8 | MCPize | https://mcpize.com/developers/publish-mcp-server ; https://mcpize.com/docs/monetization | Submission and paid listing rules for a similar channel | in repo record (`packaging/mcpize/DEPLOYMENT.md`, both read by the coordinator 2026-10-23) |
| 9 | Claude connector directory | Anthropic's connector directory submission and policy pages (search: `Claude connectors directory submit remote MCP server`) | Submission steps; rules on payments and money movement | to be confirmed at delivery time |
| 10 | ChatGPT apps catalog | OpenAI Apps SDK submission guidelines and app review policy (search: `OpenAI apps SDK app submission guidelines`) | Submission steps; rules on payments and money movement | to be confirmed at delivery time |
| 11 | x402 catalogs: Coinbase Bazaar | https://docs.cdp.coinbase.com/x402 (Bazaar discovery page) | How a pay-per-call endpoint is listed; requirements | to be confirmed at delivery time (`docs/listing-kit.md` drafts a Bazaar listing; the page itself is still to be opened) |
| 12 | x402 facilitator lists | The x402 site's ecosystem or facilitator page (https://x402.org) ; https://facilitator.payai.network | Which facilitators exist and how a service gets listed | in repo record for PayAI (`docs/listing-kit.md`); the list page to be confirmed at delivery time |
| 13 | A2A agent card directories | Search: `A2A agent card directory`, `a2a registry` | Whether any directory exists, how listing works | to be confirmed at delivery time |
| 14 | Awesome-lists on GitHub | https://github.com/punkpeye/awesome-mcp-servers ; GitHub search `awesome mcp servers`, `awesome ai agents` | Submission by pull request; contribution rules; stars as a reach proxy | to be confirmed at delivery time |
| 15 | Hugging Face Spaces | https://huggingface.co/docs/hub/spaces ; https://huggingface.co/spaces (MCP filter, if present) | How a Space is published; whether MCP servers are listed | to be confirmed at delivery time |
| 16 | npm | https://docs.npmjs.com/cli/commands/npm-publish ; `GET https://api.npmjs.org/downloads/point/last-week/<package>` | Publishing an SDK; download counts as install evidence | to be confirmed at delivery time |
| 17 | PyPI | https://packaging.python.org/en/latest/tutorials/packaging-projects/ ; `GET https://pypistats.org/api/packages/<package>/recent` | Publishing an SDK; download counts as install evidence | to be confirmed at delivery time |
| 18 | Search engines and LLM web search | Run the queries `service that does <task> API` and `MCP server for <task>` in a web search engine and in an assistant with web search; record the results pages | What shows up today and which page types rank | to be confirmed at delivery time |
| 19 | Search guidance for tool pages | Search: `llms.txt`, plus the search engine webmaster guidelines for structured data | What makes a tool page findable by agents and engines | to be confirmed at delivery time |

Order of opening at delivery:
1. sources 3 to 7 and 9 to 10, the directories with formal review;
2. sources 11 to 13, the payment-native catalogs;
3. sources 14 to 19, the open channels.

Source 18 is a live search run at delivery time. The report records the
exact queries and the date. It does not generalise from a single run.

## 4. Tables to build

**Channel table**: one row per channel covered in section 3.

| Channel | How listings are submitted | Review rules | Traffic or install evidence | Cost | Agent Market eligible as is? (yes / no / unclear, with the rule) | Sources |
| --- | --- | --- | --- | --- | --- | --- |

**Ranking**: channel; expected installs per month (estimate, method); hours
of effort (estimate, counted steps); installs per month per hour; rank.

**Top five**: per channel, the numbered submission steps, then the
blockers. A blocker can be a rule against money movement, a review queue,
an account requirement or a technical requirement, each cited.

## 5. Risk note

- **Installs per month is an estimate for nearly every channel.**
  Directories rarely publish install or traffic counts. Where a channel
  shows a counter, it is cited with its date. Otherwise the figure is
  marked as an estimate and its method is given: a proxy such as stars,
  downloads or listed view counts. Where there is no proxy, it says "not
  found".
- **Money movement rules are the decisive and riskiest cells.** The
  Claude and ChatGPT catalog rules must be quoted from the policy page
  itself. An eligibility "no" or "unclear" must name the exact rule.
- **Hours of effort** is the author's estimate, marked, with the counted
  steps from the submission docs.
- **Search as a channel** has no stable measure. The report says what
  its own queries returned on the day, and does not claim a ranking
  factor unless a guideline page states it.
- **Our own listing experience** goes only into what the repo record
  shows. Anything else is cited from the channel's pages.
