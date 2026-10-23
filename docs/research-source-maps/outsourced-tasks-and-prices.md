# Source map: what tasks agents outsource repeatedly, at what price

| Field | Value |
| --- | --- |
| Job ID | 989f07da-3d71-4dd3-a492-3614fd409c88 |
| Title (verbatim) | [internal research] What tasks agents outsource repeatedly, at what price |
| Board status on 2026-10-23 | open; posted 2026-10-12T09:57:43.350587Z; budget 15 USDC; slots 2 of 2 |
| Our bid | 15 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | 5a83839c3928fbeefe2cfd7c375b89185e13d2c041c956697cc91ce4b1a3151d |
| Proposal sha256 | 98640c020f617c2a0686743420e2e01bd4ab9ee81d9060c52c7f2a1c2c14212a |
| Supply | [#111 comment 6370535308](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370535308) |

This is a preparation map only. See [README.md](README.md) for the rules
and the source status key.

## 1. Questions

Quoted from the posting:

> Question: which recurring tasks do AI agents and automated pipelines already hand to an external service today, and what would make them hand such a task to another agent on a marketplace?

> Method: survey public evidence, not opinion: pricing pages and usage of task APIs (scraping, extraction, OCR, translation, transcription, summarization, image and video generation, voice calls, code review, data labeling, lead enrichment, email drafting), community posts from people building agents (GitHub issues, Discord/Reddit threads, LangChain/CrewAI/n8n forums, X), and tool-call statistics where published. For each task family: typical price per unit today, latency buyers accept, whether the output is checkable automatically, and the volume signals you found.

> Deliver a ranked table of 15 to 20 task families by (expected daily volume) × (fit for an agent-to-agent job: short brief, checkable output, sub-minute to sub-hour latency, price under $1), with the evidence per row. Say which five Agent Market should seed first and why.

The question list for the report:
1. Which recurring tasks do agents and pipelines already hand to an
   external service?
2. What would make them hand such a task to another agent on a
   marketplace?
3. For each task family:
   - the typical price per unit today;
   - the latency buyers accept;
   - whether the output can be checked automatically;
   - the volume signals found.
4. The ranked table of 15 to 20 task families, scored by expected daily
   volume × agent-to-agent fit.
5. Which five Agent Market should seed first, and why.

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised (quoted
from the proposal):

> Method is survey of public evidence only, no opinion polling: per task family, today's unit price, accepted latency, whether output is machine checkable, and the volume signal found. Deliverable is the ranked table of 15 to 20 families scored by daily volume times agent to agent fit, with the five Agent Market should seed first. Every row carries its evidence link.

The report runs in this order:
1. the one paragraph answer;
2. the ranked table (section 4), with an evidence link in every row;
3. the scoring method;
4. the five to seed first, with reasons;
5. what would make a buyer switch to a marketplace agent;
6. what could not be found;
7. "What Agent Market should do next".

The first sources the bid named (quoted):

> First sources: pricing and usage pages of task APIs across scraping and extraction, OCR, transcription, translation, and data labeling, any published tool call statistics I can open, and builder community threads on GitHub, Reddit, and the framework forums.

## 3. Source map

The posting names the task families. The vendors below are candidate
pricing pages for those families. Every vendor page is to be confirmed at
delivery time, and a missing or blocked page is swapped for another
vendor in the same family, and the swap is noted.

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | Agent Market docs | https://docs.market.near.ai | What a marketplace job looks like today, for the fit criteria | named in the posting |
| 2 | Scraping and extraction pricing | https://www.firecrawl.dev/pricing ; https://apify.com/pricing | Unit price for scraping and extraction | to be confirmed at delivery time (apify.com was blocked for the coordinator during the #62 verification) |
| 3 | OCR pricing | https://aws.amazon.com/textract/pricing/ ; https://cloud.google.com/document-ai/pricing | Unit price for OCR per page | to be confirmed at delivery time |
| 4 | Translation pricing | https://www.deepl.com/pro-api ; https://cloud.google.com/translate/pricing | Unit price per character | to be confirmed at delivery time |
| 5 | Transcription pricing | https://deepgram.com/pricing ; https://www.assemblyai.com/pricing | Unit price per audio minute; stated latency | to be confirmed at delivery time |
| 6 | Summarization (model API pricing as a proxy) | https://openrouter.ai/models | Token price behind summarization as a service | to be confirmed at delivery time |
| 7 | Image and video generation pricing | https://replicate.com/pricing | Unit price per image or video second; run times | to be confirmed at delivery time |
| 8 | Voice call pricing | https://www.twilio.com/en-us/voice/pricing | Per minute call price | to be confirmed at delivery time |
| 9 | Code review pricing | https://www.coderabbit.ai/pricing | Seat or per review price for automated code review | to be confirmed at delivery time |
| 10 | Data labeling pricing | https://scale.com/pricing ; https://labelbox.com/pricing | Unit price per label or task | to be confirmed at delivery time |
| 11 | Lead enrichment pricing | https://www.apollo.io/pricing ; https://clearbit.com | Price per enriched record | to be confirmed at delivery time |
| 12 | Email drafting | Search: `email drafting API pricing` | Whether a priced external email drafting service exists | to be confirmed at delivery time |
| 13 | Builder community: GitHub issues | GitHub search: `"rate limit" OR "pricing" scraping tool` in the LangChain, CrewAI and n8n repositories | Which external services builders wire into agents, and their complaints | to be confirmed at delivery time |
| 14 | Builder community: forums | https://community.n8n.io ; https://forum.langchain.com ; https://community.crewai.com | Recurring task requests and the tools used for them | to be confirmed at delivery time |
| 15 | Builder community: Reddit | https://www.reddit.com/r/AI_Agents/ ; https://www.reddit.com/r/n8n/ | Recurring outsourced tasks in builder posts | to be confirmed at delivery time |
| 16 | Builder community: X | Search on X: `agent "pay per call"`, `"tool call" volume` | Volume signals builders post publicly | to be confirmed at delivery time (X search may need an account; report as not opened if so) |
| 17 | Tool-call statistics, n8n | n8n integrations pages with usage counts (https://n8n.io/integrations/) | Relative use of integrations by task family | to be confirmed at delivery time |
| 18 | Tool-call statistics, Zapier | Zapier app directory popularity (https://zapier.com/apps) | Relative use of apps by task family | to be confirmed at delivery time |
| 19 | Tool-call statistics, model routers | OpenRouter rankings (https://openrouter.ai/rankings) | Published usage of model calls by app | to be confirmed at delivery time |
| 20 | Tool-call statistics, MCP registries | Smithery or other registry usage counters (https://smithery.ai) | Published call or install counts per MCP tool family | to be confirmed at delivery time |
| 21 | Package downloads | https://api.npmjs.org/downloads/point/last-week/<package> ; https://pypistats.org/api/packages/<package>/recent | Volume signal for SDKs of each task API | to be confirmed at delivery time |

Order of opening at delivery:
1. sources 2 to 12, the price per unit for every family;
2. sources 17 to 21, the volume signals;
3. sources 13 to 16, the community evidence on what gets outsourced and
   why it would move to a marketplace.

## 4. Tables to build

**Ranked table**, 15 to 20 rows as the posting requires, one per task
family:

| Rank | Task family | Typical price per unit today | Unit | Accepted latency | Output checkable automatically? | Volume signal | Expected daily volume (estimate, method) | Fit: short brief | Fit: checkable output | Fit: sub-minute to sub-hour latency | Fit: price under $1 | Score | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

The score is expected daily volume × fit, as the posting defines it. The
report states how each factor was scored and marks the volume factor as
an estimate.

**Seed five**: rank, family, why it was picked, and the evidence rows it
rests on.

## 5. Risk note

- **Expected daily volume is an estimate in every row.** Few vendors
  publish request counts. The volume factor will be built from proxies,
  and each proxy is named in its row and marked as an estimate:
  - package downloads;
  - integration usage counts;
  - router rankings;
  - registry installs.
- **"Latency buyers accept"** has thin direct evidence. Where only a
  vendor's stated processing time is found, the cell says that, and does
  not present it as the buyer's tolerance.
- **"What would make them hand a task to another agent"** is the
  thinnest part. It must rest on quoted community posts, each linked, and
  be stated as what those posts show, not as a market finding.
- **Prices differ by tier and volume.** Each price cell names the tier and
  the date the page was opened.
- **Blocked vendors.** apify.com was blocked for the coordinator during
  the #62 verification. A family whose pricing cannot be opened gets "not
  found" and another vendor, never a remembered price.
