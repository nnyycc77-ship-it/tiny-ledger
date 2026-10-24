# Growth proposal: scaling up and new lines of business

Status: **proposal, not adopted.** Written 2026-10-24 from a read of this
repository (`AGENT-BRIEF.md`, `PLAYBOOK.md`, `BACKLOG.md`,
`docs/services-catalog.md`, `deliveries/`, `agents/`, `api/`, `mcpize.yaml`,
and the git history). Repo facts below are cited to the file they come
from. **Every price and revenue figure marked "estimate" is unsourced
judgement, not data**, and must be checked through workstream E2/E3
research before it goes into any listing or delivery.

## 1. Where the operation stands

### Strengths

- **The evidence format is a real edge.** Every claim sits next to its
  source link and raw excerpt, empty results show the full raw response,
  and a failed fetch never shows as "nothing found" (`AGENT-BRIEF.md`,
  hard rule 3; `PLAYBOOK.md`, lessons 3 and 4). Buyers can check that
  mechanically, which most agent sellers can't offer.
- **There is a lot of capacity.** 41 Python files in `tools/` at the
  read this proposal was written from, about 30 of them source fetchers
  and the rest support tools: pregate (`pregate.py`), smoke
  (`api_smoke.py`, on live main), acceptance (`acceptance_all.py`,
  `acceptance_common.py`), packager (`delivery_packager.py`), dataset
  (`build_cpsc_dataset.py`, `validate_cpsc_dataset.py`) and probe
  (`hosted_mcp_probe.py`) tools. Live main had moved to 42 Python files
  in `tools/` at the 2026-10-24 correction read. The API serves 23
  routes in total: 22 endpoints beyond `/recall` in the `api/README.md`
  table, plus `/recall` itself. There is also an MCP server
  (`mcp_server/`) and seven prebuilt NEAR agents (`agents/`).
- **The revenue is real but tiny.** The figure in `AGENT-BRIEF.md`,
  hard rule 4, of seven paid jobs and 68.26 USDC is superseded by the
  delivery record of nine paid jobs and 78.0579 USDC as of 2026-10-24,
  about 8.67 USDC per job.

### Constraints

1. **Capacity is far ahead of demand.** Only one tool is sold for
   per-call payment today: `recall_check` at 0.05 USDC (`mcpize.yaml`).
   The ruled shelf price of 0.25 USDC per call under issue 147 is not
   live until a redeploy carries it. The other endpoints earn nothing
   unless someone hires a 10 USD job.
2. **The prebuilds are speculative.** call-for-me, catering-finder,
   local-quotes, field-service-planner, media-generator, video-clipping
   and video-dubbing were each built for a NEAR job with a bid pending at
   125 to 450 USDC per bid, totalling 1,775 USDC across the seven
   prebuilds (each `agents/*/README.md`). None is recorded as awarded.
3. **Process overhead is eating build time.** At the 2026-10-24 read,
   about 32 of 178 non-merge commits in the history are census, pin,
   drift or refresh commits (`git log --no-merges`; counted by commit
   subjects naming a census, pin, drift or refresh, with false
   positives removed), which add no new capability.
4. **There are too many revision rounds.** One carrier-vetting delivery
   has five versions (the original plus rev1 to rev4) and demand-map has
   four (`deliveries/`). Revisions delay payment and cost margin.
5. **The price has never been tested.** The flat 10 USD rate
   (`AGENT-BRIEF.md`, hard rule 4) hasn't been checked against the
   market; workstream E3 hasn't run yet (`BACKLOG.md`).
6. **There's one channel and one payment rail per product.** Sales
   depend on whoever posts on agent boards.

## 2. Scaling up the current business

1. **Put the tools and endpoints behind per-call payment, as two
   separate tracks.**
   - **MCP tool pricing.** This is the shelf pricing already in flight
     under issue 147: the MCP tools join the shelf at the ruled
     0.25 USDC per call. That ruling supersedes the single lookup
     estimate that was here before; it is a ruled price, not an
     estimate.
   - **HTTP API gate extension.** This is separate work. The x402
     payment gate in `api/payment_gate.py` wraps `GET /recall` only
     today (`api/README.md`). Extending the gate to the other API
     routes, such as `/carrier`, `/litigation`, `/awards`,
     `/nonprofit`, `/formd`, `/pagespeed`, `/domain`, `/app` and
     `/vin`, is its own task, with its own acceptance bar, and is not
     done by listing the MCP tools.
2. **Sell bundles instead of single checks.** Combine existing fetchers
   into higher-value products:
   - **Vendor/KYB pack:** company registry, OFAC (`ofac_sdn_check.py`),
     OIG exclusion (`oig_screen.py`), litigation
     (`courtlistener_recap.py`), awards (`usaspending_awards.py`), and
     domain trust (`domain_trust_check.py`).
   - **Carrier onboarding pack:** FMCSA SAFER and insurance
     (`fmcsa_carrier.py`), litigation, and OFAC.
   - **Nonprofit grantee pack:** `nonprofit_pack.py` plus OFAC and
     litigation.

   Estimate: 25 to 75 USD per pack rather than 10 USD.
3. **Turn one-off checks into subscriptions.** `tools/standing_watch.py`
   and `tools/weekly_brief.py` already exist. Sell monitoring: "alert me
   when any carrier on my list loses insurance," "weekly Form D and
   contract-award brief for my sector," "re-screen my vendor list against
   OFAC monthly." Recurring revenue is the main way out of 10 USD jobs.
4. **Cut the overhead.** Generate the census and pin files in CI on merge
   (mind `PLAYBOOK.md` lesson 7 on workflow merge routes), or drop the
   pins that don't protect a buyer. Each revision round so far points to
   a check that `tools/pregate.py` should run before delivery.
5. **Run the price test now.** Do E3 for carrier vetting and litigation
   screens first. Those are the services where a 10 USD price is most
   likely leaving money on the table.
6. **Give the prebuilds a deadline.** If a NEAR bid isn't awarded within,
   say, 14 days, either list that agent as its own product (an MCP tool
   or a fixed-price service) or stop maintaining it. local-quotes and
   catering-finder could be standalone listings.

## 3. New lines of business

Each reuses code already in the repo. Buyer segments are hypotheses to
test through workstream E2, not findings.

| Idea | Built on | Likely buyer |
| --- | --- | --- |
| Sanctions and exclusion screening API | `ofac_sdn_check.py`, `oig_screen.py` | Fintechs, marketplaces, healthcare staffing; high per-call volume |
| Freight broker carrier monitoring | `fmcsa_carrier.py` + `standing_watch.py` | Small freight brokers |
| Ecommerce compliance checker | CPSC and NHTSA recalls, `uspto_trademarks.py` | Amazon and Shopify sellers checking products before listing |
| Government contracting intel | `usaspending_awards.py` + `weekly_brief.py` | Small contractors and BD consultants; subscription |
| Deal sourcing feed | `edgar_formd.py` + awards | VCs, real estate syndicators, M&A scouts |
| Grantmaker diligence | `propublica_nonprofits.py`, `nonprofit_pack.py` | Foundations, donor-advised funds, CSR teams |
| Bilingual EN/ZH research | `templates/service-09-bilingual-research-brief.md` | Cross-border sourcing and diligence buyers; less competition |
| Public dataset builds | `templates/service-08-public-dataset-build.md`, `datasets/` | AI and data teams wanting sourced, licence-clean CSVs |
| Read-only Solidity reviews | `templates/service-10-solidity-read-only-review.md` | Small Web3 projects before launch |

The strongest new lines are **sanctions/exclusion screening** and
**carrier monitoring**. In both, buyers already pay by volume, the data
is public, and the fail-closed evidence format is what compliance teams
want.

## 4. Suggested order

1. **This week:** carry the two per-call tracks in section 2, item 1:
   the MCP shelf at the ruled price, and the separate HTTP API gate
   extension.
2. **Next two weeks:** run the E3 price scan, launch the KYB and
   carrier-onboarding packs, and automate the census refreshes.
3. **Within a month:** launch one monitoring subscription (carrier or
   OFAC), and decide which prebuilds to list or stop maintaining.

## 5. Boundaries

The hard rules in `AGENT-BRIEF.md` still apply. Listing, pricing,
account, wallet and payment changes are made by the owner outside this
repo; nothing here sends outreach or creates accounts. Any repo work this
proposal leads to goes into `BACKLOG.md` as tasks with acceptance bars
before it starts.
