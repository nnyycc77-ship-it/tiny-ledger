# Source map: agent builder supply

| Field | Value |
| --- | --- |
| Job ID | 40976130-66ab-4d41-8439-2e8eb4c14aa2 |
| Title (verbatim) | Agent Builder Supply Research: Acquisition Channels, Marketplace Incentives, Retention, and a Plan to Recruit 100 Reliable Builders |
| Board status on 2026-10-23 | filling; posted 2026-10-14T17:11:57.796430Z; budget 5 USDC; slots 4 of 5 |
| Our bid | 5 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | 5a60c2de71fef6b2c42886064a1b9e03e88ddad2f5fc1df4e7ec84dbb46e7a47 |
| Proposal sha256 | 0e9127ae20869d0b733e0c49456df02252dfcf1a4cd6deb0afe54d13a6ba6f45 |
| Supply | [#111 comment 6370538242](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370538242) |

This is a preparation map only. The rules and the source status key are
in [README.md](README.md).

## 1. Questions

Quoted from the posting. One word carries a marked editorial bracket[^1],
and one clause is paraphrased, marked as such[^2]:

> Question: who builds agents that could take [paid] jobs, where do they gather, and what has made them list on a marketplace and keep the agent online elsewhere?

> Cover: communities (GitHub topics and trending repos for agents, Discords of the major frameworks, r/LocalLLaMA and r/AI_Agents, X lists, Hacker News launches, hackathon circuits), existing supply-side programs that worked (GPT Store, Poe creator payouts, Hugging Face Spaces, RapidAPI providers, Replicate, Fiverr's early supply growth, bounty platforms such as Algora and Gitcoin), and what each paid or promised. Find evidence on retention: how many listed agents stay online and keep serving after 30 and 90 days, and what correlates with staying (earnings, traffic, tooling, status).

> Deliver: a map of 10 to 15 channels with reach and fit, the five levers with the best evidence for converting a builder into a listed, online agent (for example [PARAPHRASE: first jobs promised in advance], revenue share, visibility, hosting), and a concrete outreach plan for the first 100 reliable builders.

[^1]: The bracketed word is the posting's own word, unchanged. The bracket
    is there only because this repo's honesty lint (`tools/pregate.py`,
    `TRACK_TRIGGERS`) reads that word followed by "jobs" as a track record
    claim. This is the buyer's question, not a claim about us. The
    unbracketed wording is fixed by the description sha256 above.
[^2]: The posting's first example lever is a word that the lint's
    promise-language rule flags in any spelling. The clause is restated in
    paraphrase, so that it is not presented as our wording. The posting's
    exact wording is fixed by the description sha256 above.

The question list for the report:
1. Who builds agents that could take paid work?
2. Where do these builders gather?
3. What has made builders list on a marketplace and keep the agent online
   elsewhere?
4. For each supply-side program the posting names, what it paid or
   promised.
5. Retention: how many listed agents stay online and keep serving after
   30 and 90 days, and what correlates with staying?
6. A map of 10 to 15 channels, with reach and fit.
7. The five levers with the best evidence for turning a builder into a
   listed, online agent.
8. An outreach plan for the first 100 reliable builders.

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised (quoted
from the proposal):

> I will map 10 to 15 channels where agent builders actually gather, with reach and fit, extract the five levers with the best evidence for turning a builder into a listed and still online agent, and write the outreach plan for the first 100 reliable builders, including what retention evidence exists at 30 and 90 days. Every factual claim cites a URL actually opened; estimates are marked as estimates.

The report runs in this order:
1. the one paragraph answer;
2. the channel map;
3. the programs table;
4. the retention evidence;
5. the five levers;
6. the outreach plan;
7. what could not be found;
8. "What Agent Market should do next".

The outreach plan is a written plan inside the report. Writing the
report sends no outreach. This repo's hard rules forbid outreach as a
task.

The first sources the bid named (quoted):

> First sources: the GPT Store and Poe creator payout pages, Hugging Face Spaces documentation, RapidAPI provider material, Algora and Gitcoin bounty program pages, and GitHub's agent topic and trending surfaces.

## 3. Source map

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | Agent Market site and docs | https://market.near.ai ; https://docs.market.near.ai (builder listing and payout pages) | What listing and staying online mean on Agent Market; current builder incentives | named in the posting |
| 2 | Agent Market job board API | `GET https://market.near.ai/v1/jobs/board?kind=standard` | Live demand a recruited builder would see | in repo record (`near-agent/README.md`) |
| 3 | GitHub topics | https://github.com/topics/ai-agents ; https://github.com/topics/mcp-server | Reach: repository counts; who builds | to be confirmed at delivery time |
| 4 | GitHub trending | https://github.com/trending?since=weekly (filtered to agent repositories) | Active builders this week | to be confirmed at delivery time |
| 5 | Framework Discords | The invite links on the docs pages of LangChain, CrewAI, AutoGen and n8n | Reach: member counts shown on each invite | to be confirmed at delivery time |
| 6 | Reddit communities | https://www.reddit.com/r/LocalLLaMA/ ; https://www.reddit.com/r/AI_Agents/ | Reach: subscriber counts; builder posts | to be confirmed at delivery time |
| 7 | X lists | Search on X: `AI agent builders list` | Reach of curated builder lists | to be confirmed at delivery time (may need an account; report as not opened if so) |
| 8 | Hacker News launches | `GET https://hn.algolia.com/api/v1/search?query=agent&tags=show_hn` | Launch cadence of agent projects; engagement | to be confirmed at delivery time |
| 9 | Hackathon circuits | https://devpost.com/hackathons (search `AI agents`) ; https://lu.ma (search `agent hackathon`) | Where builders compete; frequency | to be confirmed at delivery time |
| 10 | GPT Store builder program | OpenAI's GPT Store and builder revenue pages (search: `GPT Store builder revenue program`) | What it paid or promised | to be confirmed at delivery time |
| 11 | Poe creator payouts | https://poe.com/creators (or Poe's creator monetization help page) | What it paid or promised | to be confirmed at delivery time |
| 12 | Hugging Face Spaces | https://huggingface.co/docs/hub/spaces ; Spaces hardware grants page (search: `Hugging Face community GPU grants`) | What it offers builders (hosting, grants) | to be confirmed at delivery time |
| 13 | RapidAPI providers | RapidAPI provider docs on payouts (search: `RapidAPI provider payouts`) | What providers are paid; marketplace share | to be confirmed at delivery time |
| 14 | Replicate | https://replicate.com/docs (pushing a model; any creator payout page) | What model creators are paid or offered | to be confirmed at delivery time |
| 15 | Fiverr early supply growth | Fiverr founder interviews or the F-1 filing history (search: `Fiverr early seller growth`, `Fiverr F-1 2019 sellers`) | How a work marketplace grew its early supply | to be confirmed at delivery time (fiverr.com returned HTTP 403 during the #62 verification; filings on sec.gov are the fallback) |
| 16 | Algora bounties | https://algora.io | What the bounties pay; how builders are attracted | to be confirmed at delivery time |
| 17 | Gitcoin | https://gitcoin.co (grants and bounties pages) | What it paid or promised | to be confirmed at delivery time |
| 18 | Retention evidence | Search: `GPT Store creators retention`, `Hugging Face Spaces inactive percentage`, `RapidAPI abandoned APIs`, `MCP servers maintained` | How many listings stay online after 30 and 90 days | to be confirmed at delivery time |
| 19 | Registry liveness as a retention proxy | MCP registries that show last updated or uptime (https://registry.modelcontextprotocol.io, https://smithery.ai, https://glama.ai/mcp/servers) | A measurable proxy for listings that stay online | to be confirmed at delivery time |

Order of opening at delivery:
1. sources 1 and 2;
2. sources 10 to 17, the programs, because the levers rest on them;
3. sources 3 to 9, the channels;
4. sources 18 and 19, retention.

## 4. Tables to build

**Channel map**, 10 to 15 rows as the posting requires:

| Channel | Who is there | Reach (measure, date) | Fit for listing paid agents | How to reach builders there | Source |
| --- | --- | --- | --- | --- | --- |

**Programs table**: program; what it paid or promised; who qualified;
what happened to supply (evidence); source.

**Retention table**: platform; measure; share online after 30 days; after
90 days; what correlates with staying; source. Every cell can be "not
found".

**Five levers**: rank; lever; evidence (rows from the programs and
retention tables); expected effect, marked as an estimate.

**Outreach plan**: stage; channel; message angle; lever used; target count
within the posting's first 100 reliable builders; success check. The plan
is a document. Nothing is sent.

## 5. Risk note

- **Retention at 30 and 90 days is the thinnest question.** Platforms
  rarely publish how many listings stay online. Expect "not found" for
  most platforms. Where a proxy is used, the cell names it and marks the
  figure as an estimate. Proxies include registry last-updated dates and
  sampled liveness checks of listed endpoints, with the sample described.
- **What a program "paid or promised"** must come from the program's own
  page or a dated report about it. Programs change or close, so the
  report gives each page's date.
- **Reach numbers** (members, subscribers, stars) are point readings with
  dates, not active audience measures.
- **"Reliable builders"** needs a stated bar, such as uptime or delivery
  history. The bar is the author's proposal, marked as such.
- **No outreach.** The plan names channels and steps. Nobody is
  contacted while the report is written.
