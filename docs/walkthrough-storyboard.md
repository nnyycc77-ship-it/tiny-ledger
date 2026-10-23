# AgentTab walkthrough: storyboard

Shot by shot plan for a 60 to 90 second screen recording of AgentTab.
Three settlement paths are shown, because those three paths are the
product: release by the payer, refund by the payer inside the grace
window, and claim by the agent after the grace window. Every narration
line states only what `contracts/AgentTab.sol` does; the matching code
and tests are cited under each shot so the narration can be checked.

Running time: 12 shots, 78 seconds at the durations below. Trim shot 2
or shot 12 to land nearer 60 seconds; do not cut shots 5, 8 or 10, which
are the three settlement paths.

Recording notes:

* Record `app/index.html` with a wallet on Arc testnet and two wallets
  you control (one payer, one agent). The contract address, the chain,
  and the transaction hashes shown on screen come from that recording;
  nothing in this document states them.
* The grace window is 48 hours, so shots 8 and 10 are recorded on tabs
  opened earlier (one past expiry, one past expiry plus 48 hours), or on
  a local Foundry chain with time warped. Say which on screen; do not
  imply the whole recording happened in real time.
* Show the explorer page for each transaction, so every figure on screen
  is also visible on chain.

## Shot 1 (0:00 to 0:06): the problem

On screen: a plain title card, "AgentTab: a tab for paying AI agents in
USDC".

Narration: "Paying an AI agent today means trusting it with money up
front, or chasing it for delivery afterwards. AgentTab is the smallest
fix: an escrow shaped like a bar tab."

Backed by: the contract header comment, `contracts/AgentTab.sol` lines
11 to 20.

## Shot 2 (0:06 to 0:14): the contract

On screen: `contracts/AgentTab.sol` scrolled slowly from the top; pause
on the four event declarations.

Narration: "One contract, no imports, no owner, no admin keys, no
upgrade path. Four events: opened, released, claimed, refunded. That is
the whole surface."

Backed by: lines 1 to 53 of the contract (no `import` statement, no
owner or admin storage, the four `event` lines at 50 to 53).

## Shot 3 (0:14 to 0:22): open a tab

On screen: `app/index.html`, payer wallet connected. Fill in the agent
address, an amount, an expiry of 1 hour, and a task reference. Click
"Approve and open tab". Two wallet prompts: approve, then open.

Narration: "The payer opens a tab: who gets paid, how much USDC, and an
expiry. The USDC moves into the contract, and the tab records a task
reference so anyone can tie the payment to the job."

Backed by: `openTab` at lines 77 to 102; `testDepositHoldsFundsInContract`
and `testTaskRefStoredAndEmitted` in `test/AgentTab.t.sol`.

## Shot 4 (0:22 to 0:28): the tab on chain

On screen: the explorer page for the open transaction, with the
`TabOpened` event decoded: tabId, payer, agent, amount, expiresAt,
taskRef.

Narration: "Every step emits an event, so the whole life of a tab is
readable from the explorer."

Backed by: the `emit` lines at 99, 114, 132 and 150.

## Shot 5 (0:28 to 0:36): path one, release

On screen: back in the app, the tab appears under "Your tabs as payer".
Click "Release". Wallet prompt. The status flips to Released; the agent
wallet balance rises by the full amount.

Narration: "Path one. The work arrives, the payer releases, the agent
is paid in full. No fee, no third party."

Backed by: `release` at lines 107 to 117; `testReleasePaysAgentInFull`.

## Shot 6 (0:36 to 0:42): what cannot happen

On screen: the agent wallet tries "Release" on a tab it did not open
(from the console or a second browser); the transaction reverts with
"only the payer can release".

Narration: "Only the payer can release. The agent cannot pay itself
early, and a stranger cannot touch the tab at all."

Backed by: line 110; `testStrangerCannotRelease` and
`testAgentCannotReleaseOwnTab`.

## Shot 7 (0:42 to 0:48): the clock

On screen: a second tab, already past its expiry. The app shows
"Open, in refund grace". A caption: "expiry + 48 hours".

Narration: "If the payer never releases, time settles the tab. From the
expiry, the payer has a 48 hour grace window."

Backed by: `REFUND_GRACE = 48 hours` at line 41; lines 145 to 146.

## Shot 8 (0:48 to 0:56): path two, refund inside the window

On screen: click "Refund" on that tab. Wallet prompt. Status flips to
Refunded; the payer wallet balance is back where it started.

Narration: "Path two. Inside that window the payer can take the deposit
back. A payer who never got the work keeps a fair exit."

Backed by: `refund` at lines 141 to 153;
`testRefundAfterExpiryReturnsFundsToPayer`,
`testRefundExactlyAtExpirySucceeds`.

## Shot 9 (0:56 to 1:02): the window closes

On screen: a third tab, past expiry plus 48 hours. In the payer view
the Refund button is gone; the console shows a refund attempt reverting
with "grace window has ended".

Narration: "Once the window closes, the refund right is gone."

Backed by: line 146; `testRefundAfterGraceEndsReverts`.

## Shot 10 (1:02 to 1:10): path three, claim after the window

On screen: switch to the agent wallet. The same tab appears under "Tabs
paying you as agent" with a "Claim" button. Click it. Wallet prompt.
The agent is paid the full amount.

Narration: "Path three. After the window, the agent claims the tab and
is paid in full. A payer who received the work and then went silent
cannot reclaim the deposit."

Backed by: `claim` at lines 124 to 135;
`testClaimByAgentAfterGracePaysInFull`, `testClaimBeforeGraceEndsReverts`.

## Shot 11 (1:10 to 1:15): the proof page

On screen: `app/proof.html` pointed at the same contract. Three tabs
listed: Released, Refunded, Claimed; totals summed; each row with its
transaction links and a green check against `getTab`.

Narration: "The proof page reads the contract's own events and lists
every tab, every outcome, and every transaction."

Backed by: `app/proof.html` and `app/proof-core.js`, which use the four
event signatures from lines 50 to 53.

## Shot 12 (1:15 to 1:18): close

On screen: the repository README, cursor on "Run the tests", then the
terminal output of `forge test` showing the suite passing.

Narration: "Twenty six tests, no admin keys, one contract. AgentTab."

Backed by: the 26 `function test...` definitions in
`test/AgentTab.t.sol`; CI in `.github/workflows/test.yml`.
