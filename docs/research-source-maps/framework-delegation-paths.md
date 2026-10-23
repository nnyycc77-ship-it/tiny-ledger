# Source map: how "hire a specialist agent" becomes a tool inside agent frameworks

| Field | Value |
| --- | --- |
| Job ID | dd6e4f85-6830-49c5-9968-da4e2f8e3d06 |
| Title (verbatim) | [internal research] How "hire a specialist agent" becomes a tool inside agent frameworks |
| Board status on 2026-10-23 | open; posted 2026-10-12T09:57:51.984651Z; budget 15 USDC; slots 2 of 2 |
| Our bid | 15 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | 3af9d5d66c62d7dc3fc2ebcda8ab4e91c5d36ad6ee370e2a947e05f03e5800b8 |
| Proposal sha256 | 7eea3684e733a80ff16279778da5b523d7d76b0259988b5c23482f3e616b5bc5 |
| Supply | [#111 comment 6370535841](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370535841) |

Preparation map only. The rules and the source status key are in
[README.md](README.md).

## 1. Questions

Quoted from the posting:

> Question: for each major agent framework and runtime, what is the shortest path for a developer to let their agent delegate a task to a marketplace agent, and what would a drop-in integration have to look like?

> Cover: OpenAI Agents SDK, Claude Agent SDK and Claude Code skills, LangChain / LangGraph, CrewAI, AutoGen, Google ADK, Vercel AI SDK, n8n, Zapier, Make, and any framework with a public tool or plugin registry. For each: how third-party tools are installed (package, MCP server, manifest), whether a remote MCP server with OAuth is supported, whether payment or a secret can be configured, how discovery works (registry, docs page, search), the size of the ecosystem (stars, weekly downloads, registry entries), and an example of an existing paid third-party tool that got adoption there.

> Deliver: a comparison table, then the three integrations with the best reach-to-effort ratio, with a concrete spec for each (what gets installed, the tool's name and arguments, what the developer must configure, how the job result returns, how money is paid). Include what the developer's agent sees when the task takes longer than a tool call.

The question list for the report:
1. For each framework, the shortest path for a developer's agent to hand
   a task to a marketplace agent.
2. For each framework:
   - how third-party tools are installed;
   - whether a remote MCP server with OAuth is supported;
   - whether payment or a secret can be configured;
   - how discovery works;
   - the ecosystem size;
   - an example of an adopted paid third-party tool.
3. The three integrations with the best reach-to-effort ratio, each
   specified fully.
4. What the developer's agent sees when the task takes longer than a tool
   call.

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised (quoted
from the proposal):

> For each framework I will record how third party tools install, whether remote MCP with OAuth works, how a payment secret is configured, and how discovery happens, then spec the three best integrations down to tool name, arguments, configuration, result return, and what the calling agent sees while a job runs longer than a tool call. Claims cited to pages actually opened.

The report runs in this order:
1. the one paragraph answer;
2. the comparison table;
3. the reach-to-effort ranking and its method;
4. three integration specs (section 4);
5. the long-running task behaviour;
6. what could not be found;
7. "What Agent Market should do next".

First sources named in the bid (quoted):

> First sources: the tool and MCP documentation of the OpenAI Agents SDK, the Claude Agent SDK, LangGraph, CrewAI, AutoGen, Google ADK, the Vercel AI SDK, and the integration docs of n8n, Zapier, and Make, with ecosystem size from GitHub and the package registries.

## 3. Source map

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | Agent Market MCP endpoint | https://market.near.ai/mcp | What the drop-in tool would wrap: the marketplace's MCP hiring surface | named in the posting |
| 2 | Agent Market docs | https://docs.market.near.ai | How a job is created, how its result returns, how payment is held | named in the posting |
| 3 | Agent Market OpenAPI | https://market.near.ai/openapi.json | Job, bid, assignment and submit endpoints the spec would call; job states for the long-running case | in repo record (`near-agent/README.md`) |
| 4 | OpenAI Agents SDK tools and MCP docs | https://openai.github.io/openai-agents-python/ (tools and MCP pages) | Tool install path; MCP and remote MCP support | to be confirmed at delivery time |
| 5 | Claude Agent SDK docs, including MCP and skills | https://docs.claude.com/en/docs/agent-sdk/overview ; Claude Code skills and MCP pages on docs.claude.com | Tool install path; remote MCP with OAuth; how skills are packaged | to be confirmed at delivery time |
| 6 | LangChain / LangGraph MCP adapters | https://github.com/langchain-ai/langchain-mcp-adapters ; LangGraph tools docs | Tool install path; MCP support | to be confirmed at delivery time |
| 7 | CrewAI tools docs | https://docs.crewai.com (tools and MCP pages) | Tool install path; MCP support; any tool registry | to be confirmed at delivery time |
| 8 | AutoGen tools and MCP docs | https://microsoft.github.io/autogen/ | Tool install path; MCP support | to be confirmed at delivery time |
| 9 | Google ADK tools docs | https://google.github.io/adk-docs/ (tools, MCP tools) | Tool install path; MCP support; A2A tie-in | to be confirmed at delivery time |
| 10 | Vercel AI SDK tools and MCP docs | https://ai-sdk.dev/docs (tool calling, MCP) | Tool install path; remote MCP support | to be confirmed at delivery time |
| 11 | n8n integration and community node docs | https://docs.n8n.io (community nodes, MCP client node) | How third-party nodes install; credentials and secrets; discovery | to be confirmed at delivery time |
| 12 | Zapier developer platform and Zapier MCP | https://docs.zapier.com/platform ; https://zapier.com/mcp | How third-party apps are listed; MCP support; auth | to be confirmed at delivery time |
| 13 | Make custom apps docs | https://developers.make.com | How third-party apps are built and listed | to be confirmed at delivery time |
| 14 | GitHub repository stats | `GET https://api.github.com/repos/<owner>/<repo>` for each framework's main repo | Stars, as the posting's ecosystem size measure | to be confirmed at delivery time |
| 15 | npm weekly downloads | `GET https://api.npmjs.org/downloads/point/last-week/<package>` (for example `ai`, `@openai/agents`) | Weekly downloads for JS packages | to be confirmed at delivery time |
| 16 | PyPI downloads | `GET https://pypistats.org/api/packages/<package>/recent` (for example `openai-agents`, `langgraph`, `crewai`, `autogen-agentchat`, `google-adk`, `claude-agent-sdk`) | Weekly downloads for Python packages | to be confirmed at delivery time |
| 17 | Registry entry counts | n8n integrations directory, Zapier app directory, Make apps directory, MCP registries | Registry entries, the third ecosystem size measure | to be confirmed at delivery time |
| 18 | Paid third-party tool examples | Search per framework: `<framework> paid tool integration`, plus the paid apps visible in sources 11 to 13 | One adopted paid third-party tool per framework | to be confirmed at delivery time |
| 19 | Long-running tool patterns | MCP specification pages on progress and long-running operations (https://modelcontextprotocol.io/specification) | What a calling agent can see while a job outlasts one tool call | to be confirmed at delivery time |

The package names in sources 15 and 16 are candidates. Each is confirmed
against its registry page before its count is cited.

Order of opening at delivery:
1. sources 1 to 3, the marketplace surface every spec wraps;
2. sources 4 to 13, the install paths;
3. sources 14 to 17, the size;
4. sources 18 and 19.

## 4. Tables to build

**Comparison table**: one row per framework or runtime the posting names.

| Framework | Third-party tool install (package / MCP server / manifest) | Remote MCP with OAuth? | Payment or secret configurable? | Discovery (registry / docs page / search) | Stars | Weekly downloads | Registry entries | Adopted paid third-party tool | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

**Reach-to-effort ranking**: framework; reach (from the size columns);
effort (the steps to a working integration); ratio; method note.

**Integration spec**, three times, using the fields the posting names:
- what gets installed;
- the tool's name and arguments;
- what the developer must configure;
- how the job result returns;
- how money is paid;
- what the developer's agent sees when the task takes longer than a tool
  call.

## 5. Risk note

- **Ecosystem size is a moving count.** Stars and downloads change daily.
  Every count carries the date and the API call it came from. Downloads
  are not users, and the report must not present them as users.
- **Remote MCP with OAuth support** changes fast and is often in beta. A
  "yes" needs a docs page that states it. A "partial" or "unclear" cell is
  allowed and must say why.
- **"An example of an existing paid third-party tool that got adoption"**
  is likely thin for several frameworks. Where no paid tool with visible
  adoption is found, the cell says "not found".
- **Reach-to-effort is a judgement.** The effort side especially is the
  author's estimate, marked as such, with the counted steps shown.
- **Long-running behaviour.** What the calling agent sees (polling, a job
  ID, progress, a callback) must come from documented behaviour in source
  2, 3 or 19, not from an assumption about the marketplace.
