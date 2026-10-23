# AgentTab

A minimal on chain tab for paying AI agents in USDC on Arc.

Work increasingly gets done by AI agents, and paying an agent today still
means either trusting it with money up front or chasing an invoice after
the work is done. AgentTab is the smallest possible fix: an escrow shaped
like a bar tab. A payer opens a tab by depositing USDC into a simple
contract that names the agent wallet and the amount. The tab then settles
in one of three ways, all fixed by the contract at opening time and none of
them needing a third party.

## Working in this repo

This repo is also the public workbench of Hojo Research Agent, the
research agent whose paid deliveries live in `deliveries/`. If you
are an agent or a helper picking up work here, read
[AGENT-BRIEF.md](AGENT-BRIEF.md) first: it carries the hard rules
(public repo, no secrets ever, no invented data, one fixed delivery
format). Then take work from [BACKLOG.md](BACKLOG.md), which lists
what is wanted, in value order, with the acceptance bar for each
piece. Platform accounts, wallets, bidding, and payments are
operated outside this repo and are never part of a repo task.

## Settlement rules (v2)

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

## How the flow works

1. Payer approves the AgentTab contract to spend the tab amount in USDC.
2. Payer calls `openTab(agent, amount, duration, taskRef)`. The USDC moves
   into the contract and the tab is recorded with an expiry of now plus
   duration.
3. The agent does the work, arranged between the two sides as described
   below.
4. Payer calls `release(tabId)` and the contract sends the full amount to
   the agent. Done.
5. Or the expiry passes: the payer may `refund(tabId)` inside the 48 hour
   grace window, and after the window the agent may `claim(tabId)`.

Every step emits an event (TabOpened, TabReleased, TabClaimed,
TabRefunded), so the whole life of a tab is readable from the Arc
explorer.

## How work connects

AgentTab is a settlement layer only, and it is honest about that. Finding
an agent, agreeing the task, and delivering the result happen between the
payer and the agent off chain, or through an agent marketplace that
handles intake and delivery. The tab is opened against that agreement, the
task reference ties the tab to the job, and the contract guarantees that
the money set aside for the job can only end up with the agent or, inside
the grace window, back with the payer. There is no task intake, execution,
or delivery backend in this repo, by design.

## Contract design notes

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

## Repo layout

- `contracts/AgentTab.sol` — the contract.
- `test/AgentTab.t.sol` — Foundry test suite (26 tests), plus the test
  only token stand ins in `test/`: `MockUSDC.sol`, `FlakyUSDC.sol` (a
  token whose transfers can be made to report failure), and
  `ReentrantUSDC.sol` (a notifying token plus a hostile agent used for
  the reentrancy tests).
- `app/proof.html` and `app/proof-core.js` — the read only proof page:
  it reads the four contract events from an Arc RPC endpoint, lists every
  tab with its outcome and transaction links, sums the amounts, and
  checks each tab against `getTab`. The pure logic lives in
  `proof-core.js` with node tests in `proof-core.test.mjs`. `PROOF.md`
  is the written proof the page backs.
- `app/index.html` — the whole app: one static page, wallet connect via
  window.ethereum, no build step. It validates its configuration before
  allowing transactions, follows wallet account and network changes,
  checks the network before every transaction, and lists tabs by reading
  TabOpened logs filtered to the connected account rather than scanning
  every tab.
- `foundry.toml` — Foundry config, solc 0.8.24.
- `docs/walkthrough-storyboard.md` — shot by shot plan for the
  walkthrough video: open, release, refund inside the grace window, and
  claim after it.
- `.github/workflows/test.yml` — CI: runs the Foundry suite, the
  delivery tool tests, and the proof page tests on every push.

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

## Deployment

The facts this deployment relies on:

- Network: Arc mainnet, chain ID 5042.
- Public RPC: https://rpc.mainnet.arc.io
- Explorer: https://explorer.arc.io
- USDC on Arc: 0x3600000000000000000000000000000000000000 (the ERC-20 view
  of the native balance, 6 decimals; the same address serves testnet).
- Gas on Arc is USDC itself.
- The AgentTab constructor takes one argument: the USDC address above.

### Route A: Arc Studio

1. Open Arc Studio and create a project describing AgentTab (an on chain
   USDC tab for paying AI agents: deposit, release, refund inside a grace
   window, agent claim after it).
2. Bring the code in: paste `contracts/AgentTab.sol` as the project
   contract, unchanged, and the contents of `app/index.html` as the app
   page.
3. Review the contract inside Studio and run its test pass on Arc testnet
   (chain ID 5042002).
4. Deploy to mainnet. Studio does not sign or fund mainnet transactions,
   so this step is the owner's wallet signing the deployment, with the
   USDC address above as the constructor argument.
5. Copy the deployed AgentTab address into the CONFIG block at the top of
   `app/index.html` (one value, AGENTTAB_ADDRESS) and host the page
   anywhere static. Until that value is set, the app shows a not
   configured banner and disables its transaction buttons.

### Route B: Foundry, same bytecode

```
forge create contracts/AgentTab.sol:AgentTab \
  --rpc-url https://rpc.mainnet.arc.io \
  --constructor-args 0x3600000000000000000000000000000000000000 \
  --private-key <owner key, used locally only>
```

## Run the app

Host `app/index.html` on any static host (or open it from a local static
server), connect an EVM wallet on Arc mainnet, and use the panels:
connect, open a tab, then release or refund it from the payer list. Tabs
where the connected wallet is the agent appear in the second list, with a
claim button once their grace window has passed.

## A worked example

After deployment, open one small tab from the app (for example 1 USDC to a
second wallet you control, expiry 1 hour) and release it. Those two
mainnet transactions are real USDC moving through the contract, and the
release transaction is visible at https://explorer.arc.io under the
contract address.
