# Agent brief: working in this repo

Read this before changing anything here. It takes five minutes and it
will save you from the mistakes that actually cost money.

## What this repo is

This is the public workbench of Hojo Research Agent, an AI research
agent that earns small USDC payments for sourced research work. The
services it sells are:

* Product recall checks (CPSC SaferProducts and NHTSA records)
* FMCSA carrier vetting (SAFER and Licensing and Insurance records)
* Federal litigation screens (CourtListener and the RECAP archive)
* Public registry verification (NPPES, state license boards, the OIG
  exclusion list)
* Federal contract award briefs (USAspending records)
* Nonprofit diligence from IRS Form 990 filings

The repo holds three kinds of thing:

* `deliveries/` — real reports delivered to paying buyers, kept as
  public proof of the work.
* `contracts/`, `app/`, `test/` — AgentTab, a minimal on chain USDC
  tab contract for paying AI agents on Arc: a payer deposits USDC
  into a tab, releases it when the work is done, can refund inside a
  48 hour grace window after expiry, and the agent can claim after
  that window. No admin keys, no owner, no upgrade path.
* `.well-known/agent-card.json` — the agent its public card.

## Who reviews

Every change is reviewed by the coordinating agent before it is used
in paid work. Land changes as small pull requests, or as a reviewed
push when a maintainer asks for one. Nothing here goes live in a
delivery, a listing, or a submission just because it was merged; the
reviewer checks it against the hard rules below first.

## Hard rules

These are not negotiable. A change that breaks one of them will be
sent back, and work built on it will not be used.

1. **This repo is public. Never commit secrets.** No API keys, no
   passwords, no private keys, no seed phrases, no platform config
   files, no account credentials, and no copies of any of those. If a
   tool needs a key, the key comes from the environment at run time
   and is never written to a file in this repo. The `.gitignore`
   already excludes config and key files; do not weaken it.
2. **Never invent data.** Every figure in any deliverable, example,
   or doc must come from a source that was actually fetched, and the
   source must be named. If a number cannot be pulled from the
   source, the report says so plainly. It never fills the gap.
3. **The delivery format is fixed, because paying platforms check
   it mechanically.** Every claim sits with its source link, and the
   raw excerpt from that source is printed directly beneath the
   link, in a code block or in quoted lines, verbatim and
   unreformatted. An empty result is proven by printing the full raw
   response, never by asserting that nothing was found. Every query
   records the exact query used and the retrieval time.
4. **Track record claims stay honest and current.** As of
   2026-10-24 the true record is: nine paid jobs won and delivered
   on Synmerco (a recall check, a carrier vetting report, a
   litigation screen, a Cook County property tax comps report, a
   Tampa flood zone screen, a Florida company verification, a site
   diligence report, a Tampa wage benchmark, and a Grants.gov grant
   opportunities scan), all nine paid out and swept to the owner
   wallet, 78.0579 USDC in total, six released with no revision
   round and three released after a single revision each; ten
   services listed for hire on ugig at 10 USD each; AgentTab
   deployed on Arc testnet, with the mainnet deployment and grant
   submission in preparation for a Nov 1, 2026 deadline. Do not write any claim
   stronger than this. When the record changes, the reviewer updates
   this paragraph.

## Boundaries

Helpers build code, tooling, docs, and drafts in this repo only.
Platform accounts, agent wallets, bidding, submissions, and payments
are operated outside this repo and are never part of a repo task. Do
not ask for access to them, do not simulate them, and do not write
code that needs them. If a task seems to need a platform account or
a wallet, stop and say so in the pull request; the reviewer will
rework the task so it fits inside this repo.

One workstream is research only. Workstream E in `BACKLOG.md` is
sourcing: finding new boards, buyer segments, pricing evidence,
and programs, and filing them as issues in this repo with their
sources. Sourcing helpers never send outreach, create accounts, or
post messages anywhere, and a sourcing lead counts for nothing
until the coordinating agent has verified it on the platform
itself. See workstream E in `BACKLOG.md` for its tasks and rules.

## How to work

* Small pull requests, one purpose each, with a plain description of
  what changed and how it was checked.
* Code ships with tests where tests make sense, and existing tests
  keep passing.
* Docs are plain Markdown. Write the way the rest of the repo is
  written: direct, sourced, no padding.
* No new dependency without a reason stated in the pull request.
  Light and readable beats clever.
* Start from `BACKLOG.md`. It lists the work that is wanted, in
  value order, with the acceptance bar for each piece.
