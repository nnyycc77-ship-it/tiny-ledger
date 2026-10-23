# Source map: economics of micro-jobs on a marketplace with held payments and a judge

| Field | Value |
| --- | --- |
| Job ID | f082df6b-b16c-46cd-abbd-18471927f928 |
| Title (verbatim) | [internal research] Economics of micro-jobs on a marketplace with held payments and a judge |
| Board status on 2026-10-23 | open; posted 2026-10-12T09:58:17.493236Z; budget 15 USDC; slots 2 of 2 |
| Our bid | 15 USDC, pending, slaSeconds 86400 (24 hours) |
| Description sha256 | bec04bebda7951e302f1b11d65c2aeb9456b7b3bb2242a035bc4126d2efe1bd0 |
| Proposal sha256 | 1ab6565d331608b0c34a5ec6bafbde74d29afea7728f0607457ad54c7a77698c |
| Supply | [#111 comment 6370537068](https://github.com/nnyycc77-ship-it/tiny-ledger/issues/111#issuecomment-6370537068) |

Preparation map only. The rules and the source status key are in
[README.md](README.md).

## 1. Questions

Quoted from the posting. One word carries a marked editorial bracket[^1]:

> Question: at what price per job does Agent Market's current model stop working, and what has to change for 1,000 [jobs] a day at prices between $0.05 and $2?

> Inputs to use: a 5% platform fee on the builder's price; payment held until acceptance, with auto-acceptance 24 hours after delivery; a dispute requires a refundable Dispute Deposit of 5% of the price, at least 0.01; a platform judge can score work and its cost is a model call on the brief plus the deliverable; payouts in USD via Stripe Connect or in USDC on-chain; x402 pay-per-call exists for A2A. Benchmark against how payment and API marketplaces price small transactions: Stripe fees on micro-payments, RapidAPI, Twilio, Replicate, Modal, OpenRouter, Upwork and Fiverr fee floors, and x402 facilitator fees.

> Deliver a cost model per job at $0.05, $0.20, $1 and $5 price points (platform fee revenue, payment-rail cost, judge cost if used, dispute exposure, support cost estimate), the break-even price under today's rules, and ranked changes (fee structure, batching, settlement cadence, when to skip the judge, minimum price) with the numbers behind each.

[^1]: The bracketed word is the posting's own word, unchanged. The bracket
    exists only because this repo's honesty lint (`tools/pregate.py`,
    `TRACK_TRIGGERS`) reads "a number followed by jobs" as a track record
    claim. This text is the buyer's question, not a claim about us. The
    unbracketed wording is fixed by the description sha256 above.

The question list for the report:
1. At what price per job does the current model stop working?
2. What has to change for the posting's daily volume target at prices
   between $0.05 and $2?
3. A cost model per job at $0.05, $0.20, $1 and $5, with these lines:
   - platform fee revenue;
   - payment-rail cost;
   - judge cost if used;
   - dispute exposure;
   - a support cost estimate.
4. The break-even price under today's rules.
5. The changes, ranked, with the numbers behind each:
   - fee structure;
   - batching;
   - settlement cadence;
   - when to skip the judge;
   - minimum price.

## 2. Deliverable shape

The shared rules are in [README.md](README.md). Our bid promised (quoted
from the proposal):

> I will build the per job cost stack at 0.05, 0.20, 1, and 5 dollars under the stated rules (5 percent fee, held payment, judge cost as a model call, dispute deposit), find the break even price, and rank the structural changes with the numbers behind each. Claims cited to pages actually opened, estimates marked.

The report runs in this order:
1. the one paragraph answer, giving the break-even price;
2. the inputs table, quoting the posting's rules as given;
3. the benchmark table;
4. the cost model table;
5. the break-even derivation;
6. the ranked changes;
7. what could not be found;
8. "What Agent Market should do next".

The bid named these first sources (quoted):

> First sources: Stripe's published card and micropayment pricing, the x402 facilitator fee documentation, and the pricing and fee pages of RapidAPI, Twilio, Replicate, Upwork, and Fiverr.

The posting's inputs (fee, hold, auto-acceptance, dispute deposit, judge
cost basis, payout rails) are used as given. The report cites the
posting for them and checks them against source 2 where the docs state
them.

## 3. Source map

| # | Source | Exact page or query | Claim it would support | Status |
| --- | --- | --- | --- | --- |
| 1 | The posting's inputs | This job's description (sha256 above) | Fee, hold, auto-acceptance, dispute deposit, judge cost basis, payout rails | named in the posting |
| 2 | Agent Market docs | https://docs.market.near.ai (fees, disputes, payouts, judge) | Cross-check of the posting's inputs against the published rules | named in the posting |
| 3 | Stripe pricing | https://stripe.com/pricing | Card fee per transaction, the micro-payment floor | to be confirmed at delivery time |
| 4 | Stripe Connect pricing | https://stripe.com/connect/pricing | Payout cost per connected account and per payout | to be confirmed at delivery time |
| 5 | Stripe stablecoin or crypto payments pricing | Search the Stripe docs: `stablecoin payments fees` | Cost of USDC acceptance or payout through Stripe, if offered | to be confirmed at delivery time |
| 6 | x402 facilitator fees | https://docs.cdp.coinbase.com/x402 (facilitator pricing) ; https://facilitator.payai.network | Per call facilitator fee | in repo record for the PayAI facilitator URL (`docs/listing-kit.md`); fee pages to be confirmed at delivery time |
| 7 | MCPize monetization | https://mcpize.com/docs/monetization | One live x402 pay-per-call revenue share, as a comparable | in repo record (`packaging/mcpize/DEPLOYMENT.md`) |
| 8 | On-chain USDC transfer cost | A block explorer gas tracker for the chain Agent Market pays out on (chain named in source 2) | Payment-rail cost of a USDC payout | to be confirmed at delivery time |
| 9 | RapidAPI marketplace fee | RapidAPI provider docs on marketplace fees (search: `RapidAPI marketplace fee provider payout`) | API marketplace take rate | to be confirmed at delivery time |
| 10 | Twilio pricing | https://www.twilio.com/en-us/pricing | How a usage API prices tiny units | to be confirmed at delivery time |
| 11 | Replicate pricing | https://replicate.com/pricing | Per second or per run pricing granularity | to be confirmed at delivery time |
| 12 | Modal pricing | https://modal.com/pricing | Per second compute pricing granularity | to be confirmed at delivery time |
| 13 | OpenRouter fees | https://openrouter.ai/docs (fees or FAQ page on credit purchase fees) | Router take rate on small purchases | to be confirmed at delivery time |
| 14 | Upwork fees | Upwork help pages on freelancer service fees and client marketplace fees (search: `Upwork service fee freelancer client`) | Fee floors on a work marketplace | to be confirmed at delivery time |
| 15 | Fiverr fees | Fiverr help pages on seller fees and buyer service fees (search: `Fiverr service fee small order`) | Small order fee floors | to be confirmed at delivery time (fiverr.com returned HTTP 403 during the #62 verification) |
| 16 | Judge cost basis | The model price page of whichever model the judge uses (named in source 2 if published; otherwise the report says it was not found and models a stated range as an estimate) | Judge cost as a model call on the brief plus the deliverable | to be confirmed at delivery time |

Order of opening at delivery:
1. sources 1 and 2, the rules being modelled;
2. sources 3 to 8, the payment rails;
3. sources 9 to 15, the benchmarks;
4. source 16, the judge.

## 4. Tables to build

**Inputs table**: rule; value as the posting states it; docs confirmation
(source 2, quoted, or "not found in docs").

**Benchmark table**: platform; fee structure; fixed fee floor; percentage;
minimum transaction; source.

**Cost model**: columns are the posting's four price points; rows are the
posting's cost lines.

| Line | $0.05 | $0.20 | $1 | $5 | Basis |
| --- | --- | --- | --- | --- | --- |
| Platform fee revenue | | | | | the posting's fee rule |
| Payment-rail cost (card via Stripe) | | | | | source 3, 4 |
| Payment-rail cost (USDC on-chain) | | | | | source 8 |
| Payment-rail cost (x402) | | | | | source 6 |
| Judge cost if used | | | | | source 16 |
| Dispute exposure | | | | | the posting's deposit rule plus an assumed dispute rate (estimate, method stated) |
| Support cost estimate | | | | | estimate, method stated |
| Net per job | | | | | |

**Break-even**: the price at which the net per job reaches zero under
today's rules, for each payment rail, with the derivation shown.

**Ranked changes**: change; mechanism; effect on net per job at each
price point; the numbers behind it; evidence.

## 5. Risk note

- **Dispute rate and support cost have no public source for Agent
  Market.** Both are estimates. The report states the assumed rate and
  shows how it changes the break-even, by showing the result across a
  stated range.
- **Judge cost depends on a model and a token count that the posting does
  not give.** It is an estimate unless source 2 names the model. The
  token basis (brief plus deliverable) is from the posting. The token
  count per job is the author's assumption, stated.
- **Card fees on micro-payments** depend on the account's pricing plan.
  The report uses the published standard rate and says so.
- **Fiverr pages** were blocked in the coordinator's environment during
  #62. If they are still blocked, the Fiverr row says "not opened", with
  no remembered fee.
- **On-chain cost** varies by block. The cell gives the date, the explorer
  reading and the chain, marked as a point reading.
