// Tests for app/proof-core.js. Run: node --test app/proof-core.test.mjs
// No network. The fixture values mirror the Foundry tests in
// test/AgentTab.t.sol (5 and 7 USDC tabs at 6 decimals, 48 hour grace).
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const core = require("./proof-core.js");

const FIVE_USDC = 5_000_000n;
const SEVEN_USDC = 7_000_000n;
const PAYER = "0x0000000000000000000000000000000000001001";
const AGENT = "0x0000000000000000000000000000000000001002";
const PAYER2 = "0x0000000000000000000000000000000000001004";
const AGENT2 = "0x0000000000000000000000000000000000001005";

function opened(tabId, payer, agent, amount, expiresAt, taskRef, block, idx) {
  return { name: "TabOpened", args: { tabId, payer, agent, amount, expiresAt, taskRef }, txHash: "0xopen" + tabId, blockNumber: block, logIndex: idx };
}
function settled(name, tabId, payer, agent, amount, block, idx) {
  const args = name === "TabRefunded" ? { tabId, payer, amount } : { tabId, payer, agent, amount };
  return { name, args, txHash: "0x" + name.toLowerCase() + tabId, blockNumber: block, logIndex: idx };
}

test("event signatures match the contract declarations", () => {
  // Copied from contracts/AgentTab.sol lines 50 to 53.
  assert.equal(core.EVENT_SIGNATURES.TabOpened,
    "TabOpened(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount, uint64 expiresAt, string taskRef)");
  assert.equal(core.EVENT_SIGNATURES.TabReleased,
    "TabReleased(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount)");
  assert.equal(core.EVENT_SIGNATURES.TabClaimed,
    "TabClaimed(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount)");
  assert.equal(core.EVENT_SIGNATURES.TabRefunded,
    "TabRefunded(uint256 indexed tabId, address indexed payer, uint256 amount)");
  assert.deepEqual(core.STATUS_NAMES, ["Open", "Released", "Refunded"]);
  assert.equal(core.GRACE_SECONDS, 48 * 3600);
});

test("formatUsdc uses 6 decimals without floating point", () => {
  assert.equal(core.formatUsdc(FIVE_USDC), "5");
  assert.equal(core.formatUsdc(1_234_567n), "1.234567");
  assert.equal(core.formatUsdc(100n), "0.0001");
  assert.equal(core.formatUsdc(0n), "0");
  assert.equal(core.formatUsdc("28130000"), "28.13");
});

test("openPhase follows the contract boundaries", () => {
  const exp = 1_000_000;
  assert.equal(core.openPhase(exp, exp - 1), "Open, before expiry");
  assert.equal(core.openPhase(exp, exp), "Open, in refund grace window");           // refund allowed at the exact expiry
  assert.equal(core.openPhase(exp, exp + 48 * 3600 - 1), "Open, in refund grace window"); // one second before claim opens
  assert.equal(core.openPhase(exp, exp + 48 * 3600), "Open, claimable by agent");  // the exact second claim opens
});

test("release settles a tab to the agent in full", () => {
  const s = core.summarize([
    opened(0n, PAYER, AGENT, FIVE_USDC, 1_000_000n, "", 10, 0),
    settled("TabReleased", 0n, PAYER, AGENT, FIVE_USDC, 11, 0)
  ]);
  assert.equal(s.tabs.length, 1);
  assert.equal(s.tabs[0].outcome, "Released");
  assert.equal(s.tabs[0].contractStatus, "Released");
  assert.equal(s.tabs[0].settledTx, "0xtabreleased0");
  assert.equal(s.totals.released, FIVE_USDC);
  assert.equal(s.totals.settledToAgents, FIVE_USDC);
  assert.equal(s.totals.stillOpen, 0n);
  assert.deepEqual(s.problems, []);
});

test("claim reads Released on the contract but Claimed as the outcome", () => {
  const s = core.summarize([
    opened(0n, PAYER, AGENT, FIVE_USDC, 1_000_000n, "", 10, 0),
    settled("TabClaimed", 0n, PAYER, AGENT, FIVE_USDC, 12, 0)
  ]);
  assert.equal(s.tabs[0].outcome, "Claimed");
  assert.equal(s.tabs[0].contractStatus, "Released"); // claim() sets Status.Released
  assert.equal(s.totals.claimed, FIVE_USDC);
  assert.equal(s.totals.settledToAgents, FIVE_USDC);
});

test("refund returns the deposit to the payer", () => {
  const s = core.summarize([
    opened(0n, PAYER, AGENT, FIVE_USDC, 1_000_000n, "", 10, 0),
    settled("TabRefunded", 0n, PAYER, null, FIVE_USDC, 12, 0)
  ]);
  assert.equal(s.tabs[0].outcome, "Refunded");
  assert.equal(s.tabs[0].contractStatus, "Refunded");
  assert.equal(s.totals.refunded, FIVE_USDC);
  assert.equal(s.totals.settledToAgents, 0n);
  assert.equal(s.totals.stillOpen, 0n);
});

test("several tabs settle independently, as in testMultipleTabsSettleIndependently", () => {
  const s = core.summarize([
    settled("TabClaimed", 1n, PAYER2, AGENT2, SEVEN_USDC, 30, 0), // out of order on purpose
    opened(0n, PAYER, AGENT, FIVE_USDC, 1_000_000n, "job A", 10, 0),
    opened(1n, PAYER2, AGENT2, SEVEN_USDC, 1_000_000n, "job B", 10, 1),
    settled("TabReleased", 0n, PAYER, AGENT, FIVE_USDC, 11, 0),
    opened(2n, PAYER, AGENT, FIVE_USDC, 2_000_000n, "", 12, 0)
  ]);
  assert.equal(s.tabs.length, 3);
  assert.equal(s.tabs[0].outcome, "Released");
  assert.equal(s.tabs[1].outcome, "Claimed");
  assert.equal(s.tabs[1].taskRef, "job B");
  assert.equal(s.tabs[2].outcome, "Open");
  assert.equal(s.totals.count, 3);
  assert.equal(s.totals.opened, FIVE_USDC + SEVEN_USDC + FIVE_USDC);
  assert.equal(s.totals.settledToAgents, FIVE_USDC + SEVEN_USDC);
  assert.equal(s.totals.stillOpen, FIVE_USDC);
  assert.equal(s.events[0].name, "TabOpened"); // sorted by block then log index
  assert.deepEqual(s.problems, []);
});

test("inconsistent logs are reported, never silently merged", () => {
  const s = core.summarize([
    opened(0n, PAYER, AGENT, FIVE_USDC, 1_000_000n, "", 10, 0),
    settled("TabReleased", 0n, PAYER, AGENT, FIVE_USDC, 11, 0),
    settled("TabRefunded", 0n, PAYER, null, FIVE_USDC, 12, 0), // second settlement
    settled("TabReleased", 9n, PAYER, AGENT, FIVE_USDC, 13, 0)  // unknown tab
  ]);
  assert.equal(s.tabs[0].outcome, "Released");
  assert.equal(s.problems.length, 2);
  assert.match(s.problems[0], /already settled tab 0/);
  assert.match(s.problems[1], /unknown tab 9/);
});

test("describeTab gives the outcome or the open phase", () => {
  const tab = { outcome: "Open", expiresAt: 1_000_000 };
  assert.equal(core.describeTab(tab, 999_999), "Open, before expiry");
  assert.equal(core.describeTab({ outcome: "Claimed" }, 0), "Claimed");
});
