# AgentTab: proof summary

What AgentTab does, the contract facts, and how each claim is checked
against the code in this repository. Every claim below is followed by
its source (a file in this repo, with line numbers as of the commit
that added this document) and the raw excerpt from that file. The live
counterpart of this document is `app/proof.html`, which reads the
contract's events from an Arc RPC endpoint and lists every tab.

What this document does not do: it states no deployment address, no
transaction, and no figure from any chain. Those come from the proof
page at run time, pointed at the deployed contract. The track record
of the operation that uses AgentTab is stated in `AGENT-BRIEF.md` and
is not repeated or extended here.

## 1. What AgentTab does

Claim: a payer deposits USDC into a tab that names an agent; the payer
can release it to the agent at any time while it is open; after the
expiry the payer has a 48 hour grace window to refund; after that
window the agent can claim. No other movement of funds exists.

Source: `contracts/AgentTab.sol` lines 11 to 20
```
/// @title AgentTab
/// @notice A minimal on chain tab for paying AI agents in USDC on Arc.
/// A payer deposits USDC into a tab naming an agent wallet. When the work is
/// done the payer releases the tab and the contract pays the agent. If the
/// payer never releases, the tab settles by time instead: once the expiry the
/// payer set has passed, the payer has a grace window of 48 hours to refund
/// the tab, and after that window the agent can claim the tab and be paid.
/// There are no admin keys, no owner, no upgrade path, and no way to move
/// funds out of a tab except release or claim to its agent, or refund to its
/// payer inside the grace window.
```

That comment is a description. The sections below check each part of
it against the code that runs.

## 2. Contract facts

### 2.1 The grace window is 48 hours

Source: `contracts/AgentTab.sol` line 41
```
    uint64 public constant REFUND_GRACE = 48 hours;
```

### 2.2 Refund is allowed from the expiry up to, but not including, expiry plus 48 hours

Source: `contracts/AgentTab.sol` lines 141 to 146
```
    function refund(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.payer, "only the payer can refund");
        require(block.timestamp >= tab.expiresAt, "tab has not expired yet");
        require(block.timestamp < uint256(tab.expiresAt) + REFUND_GRACE, "grace window has ended");
```

Tests that pin the boundaries: `test/AgentTab.t.sol`
`testRefundExactlyAtExpirySucceeds` (line 210, refund at the exact
expiry second succeeds), `testRefundBeforeExpiryReverts` (line 120),
`testRefundAfterGraceEndsReverts` (line 251, refund at expiry plus 48
hours reverts).

### 2.3 Claim is allowed from expiry plus 48 hours onwards, by the agent only

Source: `contracts/AgentTab.sol` lines 124 to 128
```
    function claim(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.agent, "only the agent can claim");
        require(block.timestamp >= uint256(tab.expiresAt) + REFUND_GRACE, "grace window has not ended");
```

Tests: `testClaimBeforeGraceEndsReverts` (line 221, one second early
reverts), `testClaimByAgentAfterGracePaysInFull` (line 230, the exact
second it opens succeeds), `testClaimByStrangerAfterGraceReverts`
(line 242).

### 2.4 Release is allowed at any time while open, by the payer only

Source: `contracts/AgentTab.sol` lines 107 to 110
```
    function release(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.payer, "only the payer can release");
```

Tests: `testReleasePaysAgentInFull` (line 97), `testStrangerCannotRelease`
(line 128), `testAgentCannotReleaseOwnTab` (line 136).

### 2.5 Three recipient rules on opening

Claim: the agent cannot be the zero address, the contract itself, or
the payer. Amount and duration must be above zero.

Source: `contracts/AgentTab.sol` lines 82 to 86
```
        require(agent != address(0), "agent is zero address");
        require(agent != address(this), "agent is this contract");
        require(agent != msg.sender, "agent is the payer");
        require(amount > 0, "amount is zero");
        require(durationSeconds > 0, "duration is zero");
```

Tests: `testOpenTabZeroAgentReverts` (line 182),
`testOpenTabContractAsAgentReverts` (line 192),
`testOpenTabPayerAsAgentReverts` (line 200).

### 2.6 Every settlement moves the full amount, and a tab settles once

Claim: release and claim transfer `tab.amount` to `tab.agent`; refund
transfers `tab.amount` to `tab.payer`; each sets the status before the
transfer, so a second settlement fails the "tab is not open" check.

Source: `contracts/AgentTab.sol` lines 112 to 116 (release)
```
        tab.status = Status.Released;

        emit TabReleased(tabId, tab.payer, tab.agent, tab.amount);

        require(usdc.transfer(tab.agent, tab.amount), "release transfer failed");
```

Source: `contracts/AgentTab.sol` lines 130 to 134 (claim)
```
        tab.status = Status.Released;

        emit TabClaimed(tabId, tab.payer, tab.agent, tab.amount);

        require(usdc.transfer(tab.agent, tab.amount), "claim transfer failed");
```

Source: `contracts/AgentTab.sol` lines 148 to 152 (refund)
```
        tab.status = Status.Refunded;

        emit TabRefunded(tabId, tab.payer, tab.amount);

        require(usdc.transfer(tab.payer, tab.amount), "refund transfer failed");
```

Note for readers of the proof page: a claimed tab reads `Released` from
`getTab`, because `claim` sets `Status.Released` (line 130). The page
keeps "Claimed" as the outcome from the event and shows the contract's
`Released` beside it.

Tests: `testDoubleReleaseReverts` (line 153), `testDoubleClaimReverts`
(line 260), `testRefundAfterReleaseReverts` (line 164),
`testReleaseAfterRefundReverts` (line 272),
`testMultipleTabsSettleIndependently` (line 286).

### 2.7 A failed token transfer reverts the whole call and leaves the tab open

Each transfer above sits inside `require(...)`, so a transfer that
reports `false` reverts the call, including the status change made
before it.

Tests: `testOpenRevertsWhenDepositTransferFails` (line 329),
`testReleaseRevertsWhenPayoutTransferFails` (line 347), both against
`test/FlakyUSDC.sol`.

### 2.8 Every entry point carries a reentrancy lock

Source: `contracts/AgentTab.sol` lines 55 to 56
```
    modifier nonReentrant() {
        require(!_locked, "reentrant call");
```

`nonReentrant` is on `openTab` (line 79), `release` (line 107), `claim`
(line 124) and `refund` (line 141). `getTab` (line 156) is a view and
moves nothing.

Tests: `testReentrantAgentCannotDoubleSettleOnRelease` (line 374),
`testReentrantAgentCannotDoubleSettleOnClaim` (line 395), both against
`test/ReentrantUSDC.sol`.

### 2.9 No owner, no admin, no pause, no upgrade, no fee

Claim: the contract has no owner or admin role, no pause switch, no
upgrade path, no fee, and no function that withdraws funds other than
the three settlements.

This is a claim about absence, so it is proven by the full raw result
of searching the contract for those words. The one match is the
header comment that makes the same claim.

Query: `grep -n -i "owner\|admin\|pause\|upgrade\|selfdestruct\|delegatecall\|fee\|onlyOwner\|withdraw\|sweep" contracts/AgentTab.sol`

Full raw result:
```
18:/// There are no admin keys, no owner, no upgrade path, and no way to move
```

The complete list of functions in the contract, from
`grep -n "function " contracts/AgentTab.sol`, full raw result:
```
7:    function transfer(address to, uint256 amount) external returns (bool);
8:    function transferFrom(address from, address to, uint256 amount) external returns (bool);
77:    function openTab(address agent, uint256 amount, uint64 durationSeconds, string calldata taskRef)
107:    function release(uint256 tabId) external nonReentrant {
124:    function claim(uint256 tabId) external nonReentrant {
141:    function refund(uint256 tabId) external nonReentrant {
156:    function getTab(uint256 tabId)
```

Lines 7 and 8 are the ERC-20 interface the contract calls, not
functions of AgentTab. The contract's own functions are the four
settlement entry points and one view.

### 2.10 The four events and their fields

Source: `contracts/AgentTab.sol` lines 50 to 53
```
    event TabOpened(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount, uint64 expiresAt, string taskRef);
    event TabReleased(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount);
    event TabClaimed(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount);
    event TabRefunded(uint256 indexed tabId, address indexed payer, uint256 amount);
```

These four signatures are copied character for character into
`app/proof-core.js` (`EVENT_SIGNATURES`), and the test
`event signatures match the contract declarations` in
`app/proof-core.test.mjs` asserts them. The proof page derives its log
filter topics from these strings, so a mismatch would return no events
rather than wrong ones.

### 2.11 The status enum

Source: `contracts/AgentTab.sol` lines 22 to 25
```
    enum Status {
        Open,
        Released,
        Refunded
```

`app/proof-core.js` holds the same three names in the same order
(`STATUS_NAMES`), used to decode the `status` value returned by
`getTab`.

### 2.12 Amounts are USDC ERC-20 units with 6 decimals

Source: `contracts/AgentTab.sol` lines 5 and 6
```
/// @notice Minimal ERC-20 surface AgentTab needs from USDC.
/// On Arc the USDC ERC-20 interface lives at a fixed address and uses 6 decimals.
```

The contract itself never scales amounts; it stores and transfers the
integer it is given. The 6 decimal display in `app/index.html` and
`app/proof.html` rests on this comment and on `README.md`, not on
anything the contract enforces. The proof page shows the raw integer
in the Fields column next to the scaled value.

## 3. The test suite

Claim: 26 tests, run by Foundry, with no external dependency and no
fork.

Query: `grep -n "function test" test/AgentTab.t.sol`, full raw result:
```
82:    function testDepositHoldsFundsInContract() public {
97:    function testReleasePaysAgentInFull() public {
108:    function testRefundAfterExpiryReturnsFundsToPayer() public {
120:    function testRefundBeforeExpiryReverts() public {
128:    function testStrangerCannotRelease() public {
136:    function testAgentCannotReleaseOwnTab() public {
144:    function testStrangerCannotRefundAfterExpiry() public {
153:    function testDoubleReleaseReverts() public {
164:    function testRefundAfterReleaseReverts() public {
176:    function testOpenTabWithoutApprovalReverts() public {
182:    function testOpenTabZeroAgentReverts() public {
192:    function testOpenTabContractAsAgentReverts() public {
200:    function testOpenTabPayerAsAgentReverts() public {
210:    function testRefundExactlyAtExpirySucceeds() public {
221:    function testClaimBeforeGraceEndsReverts() public {
230:    function testClaimByAgentAfterGracePaysInFull() public {
242:    function testClaimByStrangerAfterGraceReverts() public {
251:    function testRefundAfterGraceEndsReverts() public {
260:    function testDoubleClaimReverts() public {
272:    function testReleaseAfterRefundReverts() public {
286:    function testMultipleTabsSettleIndependently() public {
310:    function testTaskRefStoredAndEmitted() public {
329:    function testOpenRevertsWhenDepositTransferFails() public {
347:    function testReleaseRevertsWhenPayoutTransferFails() public {
374:    function testReentrantAgentCannotDoubleSettleOnRelease() public {
395:    function testReentrantAgentCannotDoubleSettleOnClaim() public {
```

The cheatcode interface is declared locally so the suite needs no
dependency. Source: `test/AgentTab.t.sol` lines 9 to 11
```
/// @notice Minimal cheatcode surface used by these tests, declared locally so
/// the suite needs no external dependency. This is the canonical Foundry
/// cheatcode address.
```

CI runs the suite on every push and pull request. Source:
`.github/workflows/test.yml`
```
      - uses: foundry-rs/foundry-toolchain@v1
      - name: Run the AgentTab test suite
        run: forge test -vvv
```

Compiler: `foundry.toml` line 5
```
solc_version = "0.8.24"
```

## 4. How the proof page maps to the contract

| Page element | Comes from | Contract source |
| --- | --- | --- |
| Tabs table rows | `TabOpened` logs | event, line 50 |
| Outcome "Released" | `TabReleased` log | event, line 51; `release`, line 114 |
| Outcome "Claimed" | `TabClaimed` log | event, line 52; `claim`, line 132 |
| Outcome "Refunded" | `TabRefunded` log | event, line 53; `refund`, line 150 |
| "Open, in refund grace window" / "claimable by agent" | `expiresAt` plus 48 hours | lines 41, 128, 145, 146 |
| Amount in USDC | `amount` field, divided by 10^6 for display | 6 decimals, line 6 |
| "Contract says" column | `getTab(tabId)` read live | `getTab`, line 156 |
| Totals | sums of the `amount` field per event | the emit lines |
| Transaction links | the log's transaction hash | n/a |

The page refuses to show anything if the RPC answers with a different
chain id than configured, or if there is no contract code at the
address; it never fills a table from a failed read.

## 5. What is stated elsewhere and not provable from this repo

* The deployed contract address, on testnet or mainnet, is not in this
  repo. The proof page takes it from its CONFIG block or a URL
  parameter. The `app/index.html` CONFIG block carries a placeholder.
* The network facts in `README.md` (Arc chain ids 5042 and 5042002,
  the RPC and explorer URLs, the USDC address, gas paid in USDC) are
  facts about Arc, not about this code. They are repeated in the two
  pages' CONFIG blocks and were not re-verified here.
* The explorer URL patterns the pages use (`/tx/<hash>` in both pages,
  `/address/<address>` in the proof page) are assumptions about the
  explorer, not contract facts.
* The track record of the operation is stated in `AGENT-BRIEF.md`
  under hard rule 4 and is the only place it is stated.
