# AgentTab

A minimal on chain tab for paying AI agents in USDC on Arc.

Work increasingly gets done by AI agents, and paying an agent today still means
either trusting it with money up front or chasing an invoice after the work is
done. AgentTab is the smallest possible fix: an escrow shaped like a bar tab.
A payer opens a tab by depositing USDC into a simple contract that names the
agent wallet and the amount. When the work is done, the payer releases the tab
and the contract pays the agent. If the payer never releases, the payer can
refund the tab once the expiry they set has passed, so funds are never stuck.

## How the flow works

1. Payer approves the AgentTab contract to spend the tab amount in USDC.
2. Payer calls `openTab(agent, amount, duration)`. The USDC moves into the
   contract and the tab is recorded with an expiry of now plus duration.
3. The agent does the work, off chain, however the two sides arranged it.
4. Payer calls `release(tabId)` and the contract sends the full amount to the
   agent. Done.
5. Or, after the expiry passes with no release, the payer calls
   `refund(tabId)` and the full amount returns to the payer.

Every step emits an event (TabOpened, TabReleased, TabRefunded), so the whole
life of a tab is readable from the Arc explorer.

## Contract design notes

- One contract, about 120 lines, no imports, nothing to hide behind.
- No admin keys, no owner, no upgrade path, no pause switch, no fee. There is
  no function that can move funds anywhere except release to a tab's agent or
  refund to a tab's payer after expiry.
- State is set before any token transfer, and every entry point carries a
  simple reentrancy lock, so a hostile token or receiver cannot reenter mid
  payment.
- Amounts are USDC ERC-20 units. On Arc the USDC ERC-20 interface uses 6
  decimals, so a 5 USDC tab is amount 5000000.

## Repo layout

- `contracts/AgentTab.sol` — the contract.
- `test/AgentTab.t.sol` — Foundry test suite (11 tests), plus `test/MockUSDC.sol`,
  a test only USDC stand in.
- `app/index.html` — the whole app: one static page, wallet connect via
  window.ethereum, no build step.
- `foundry.toml` — Foundry config, solc 0.8.24.
- `FACTS.md` — every Arc chain fact this package relies on, with its source.

## Run the tests

```
forge test
```

All 11 tests run locally against the mock token, no fork and no network
needed: deposit, release, refund after expiry, refund before expiry rejection,
wrong caller rejections, double release rejection, release then refund
rejection, missing approval rejection.

## Deploy

Facts first: see FACTS.md for chain ID 5042, the RPC, the explorer, and the
USDC address 0x3600000000000000000000000000000000000000. Gas on Arc is USDC.

### Route A: Arc Studio (the route this entry uses)

1. Open Arc Studio and create a project describing AgentTab (an on chain USDC
   tab for paying AI agents: deposit, release, refund after expiry).
2. Bring the code in: paste `contracts/AgentTab.sol` as the project contract,
   unchanged, and the contents of `app/index.html` as the app page.
3. Review the contract inside Studio and run its test pass on Arc testnet
   (chain ID 5042002). USDC on testnet sits at the same ERC-20 address.
4. Deploy to mainnet. Studio does not sign or fund mainnet transactions, so
   this step is the owner's wallet signing the deployment. Follow
   OWNER-STEPS.md in the submission package for the exact order.
5. Copy the deployed AgentTab address into the CONFIG block at the top of
   `app/index.html` (one value, AGENTTAB_ADDRESS) and host the page anywhere
   static.

### Route B: Foundry, same bytecode

```
forge create contracts/AgentTab.sol:AgentTab \
  --rpc-url https://rpc.mainnet.arc.io \
  --constructor-args 0x3600000000000000000000000000000000000000 \
  --private-key <owner key, used locally only>
```

## Run the app

Host `app/index.html` on any static host (or open it from a local static
server), connect an EVM wallet on Arc mainnet, and use the three panels:
connect, open a tab, then release or refund from the tab list. The app adds
the Arc network to the wallet automatically if it is missing.

## The example transaction for the submission

After deployment, open one small tab from the app (for example 1 USDC to a
second wallet you control, expiry 1 hour) and release it. Those two mainnet
transactions are real USDC moving through the contract, and the release
transaction hash is the example hash the submission asks for.
