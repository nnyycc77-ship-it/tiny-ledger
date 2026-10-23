# tiny-ledger

Small data tools for public records. Fetchers and checkers for public registries (product recalls, vehicle safety campaigns, motor carrier records, federal court dockets, nonprofit filings, federal contract awards), a recall lookup API with a payment gate, and report templates.

Mostly Python, standard library first. Layout: tools/ fetchers and report builders, api/ the recall API, mcp_server/ an MCP wrapper for the checkers, datasets/ a public recalls dataset, deliveries/ completed report files, agents/ small single purpose agent programs, contracts/ and app/ an escrow contract experiment.

## Working in this repo

If you are an agent or a helper picking up work here, read
[AGENT-BRIEF.md](AGENT-BRIEF.md) first: it carries the hard rules
(public repo, no secrets ever, no invented data, one fixed delivery
format). Then take work from [BACKLOG.md](BACKLOG.md), which lists
what is wanted, in value order, with the acceptance bar for each
piece. Platform accounts, wallets, bidding, and payments are
operated outside this repo and are never part of a repo task.

## AgentTab

A minimal on chain tab for paying AI agents in USDC on Arc. A payer
opens a tab by depositing USDC into a simple contract that names
the agent wallet and the amount. The tab then settles in one of
three ways, all fixed by the contract at opening time and none of
them needing a third party.

### Settlement rules (v2)

1. **Release.** While the tab is open, the payer can release it at any
   time. The full amount goes to the agent.
2. **Refund, inside a grace window.** If the payer never releases, the
   expiry set at opening starts a grace window of 48 hours. Inside that
   window the payer can refund the tab and take the deposit back.
3. **Claim, after the grace window.** Once the window has passed, the
   refund right ends and the agent can claim the tab, paying the full
   amount to themselves. A payer who received the work and then went
   silent cannot reclaim the deposit after going quiet for the expiry plus
   48 hours, and a payer who never got the work keeps a fair window to
   take the money back first.

Three recipient rules keep tabs meaningful: the agent cannot be the zero
address, cannot be the AgentTab contract itself, and cannot be the payer.

A tab can also carry an optional task reference, a short string such as a
marketplace job id. It is stored on the tab and emitted in the TabOpened
event, so anyone can link a payment to the job it pays for. The contract
never acts on it; it is a label, not a workflow.

### How the flow works

1. Payer approves the AgentTab contract to spend the tab amount in USDC.
2. Payer calls `openTab(agent, amount, duration, taskRef)`. The USDC moves
   into the contract and the tab is recorded with an expiry of now plus
   duration.
3. The agent does the work, arranged between the two sides off chain.
4. Payer calls `release(tabId)` and the contract sends the full amount to
   the agent. Done.
5. Or the expiry passes: the payer may `refund(tabId)` inside the 48 hour
   grace window, and after the window the agent may `claim(tabId)`.

Every step emits an event (TabOpened, TabReleased, TabClaimed,
TabRefunded), so the whole life of a tab is readable from the Arc
explorer.

### Contract design notes

- One contract, no imports, nothing to hide behind.
- No admin keys, no owner, no upgrade path, no pause switch, no fee. There
  is no function that can move funds anywhere except release or claim to a
  tab's agent, or refund to a tab's payer inside the grace window.
- State is set before any token transfer, and every entry point carries a
  simple reentrancy lock, so a hostile token or receiver cannot reenter
  mid payment. A payout token transfer that reports failure reverts the
  whole call and leaves the tab open.
- Amounts are USDC ERC-20 units. On Arc the USDC ERC-20 interface uses 6
  decimals, so a 5 USDC tab is amount 5000000.

The contract is `contracts/AgentTab.sol`. Its Foundry suite is
`test/AgentTab.t.sol` (26 tests), with the test only token stand ins in
`test/`: `MockUSDC.sol`, `FlakyUSDC.sol` (a token whose transfers can be
made to report failure), and `ReentrantUSDC.sol` (a notifying token plus
a hostile agent used for the reentrancy tests). The app in `app/` is one
static page plus a read only proof page whose pure logic lives in
`app/proof-core.js`, with node tests in `app/proof-core.test.mjs`;
`PROOF.md` is the written proof the page backs. Foundry config is
`foundry.toml`, solc 0.8.24.

### Deployment facts

- Network: Arc mainnet, chain ID 5042.
- Public RPC: https://rpc.mainnet.arc.io
- Explorer: https://explorer.arc.io
- USDC on Arc: 0x3600000000000000000000000000000000000000 (the ERC-20 view
  of the native balance, 6 decimals; the same address serves testnet).
- Gas on Arc is USDC itself.
- The AgentTab constructor takes one argument: the USDC address above.

Deploying is the owner's wallet signing the deployment, either through
Arc Studio on testnet first (chain ID 5042002) or with Foundry, same
bytecode:

```
forge create contracts/AgentTab.sol:AgentTab \
  --rpc-url https://rpc.mainnet.arc.io \
  --constructor-args 0x3600000000000000000000000000000000000000 \
  --private-key <owner key, used locally only>
```

After deployment the deployed AgentTab address goes into the CONFIG
block at the top of `app/index.html` (one value, AGENTTAB_ADDRESS), and
the page can be hosted anywhere static. Until that value is set, the app
shows a not configured banner and disables its transaction buttons.

## Run the tests

```
forge test
node --test app/proof-core.test.mjs
```

All 26 tests run locally against the mock tokens, no fork and no network
needed: deposit, release, refund at and inside the expiry boundaries,
claim before and after the grace window, recipient rejections, wrong
caller rejections, double settle rejections, several tabs settling
independently, the task reference stored and emitted, failed token
transfer paths, and reentrancy attempts against both release and claim.
