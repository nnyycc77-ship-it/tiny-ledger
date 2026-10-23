/* AgentTab proof page: the pure logic, kept out of proof.html so it can be
   tested with node and read on its own. No network, no ethers, no DOM.

   Everything here mirrors contracts/AgentTab.sol. The four event names and
   their fields are copied from the contract's event declarations; the grace
   window matches REFUND_GRACE (48 hours); the status names match the Status
   enum (Open, Released, Refunded). A claimed tab reads Released on chain
   because claim() sets Status.Released, so this module keeps the event-level
   distinction (claimed vs released) alongside the contract-level status. */
(function (root) {
  "use strict";

  /* Event signatures exactly as declared in contracts/AgentTab.sol. The page
     derives its log topics from these strings, so a mismatch with the
     contract would make the page find no events at all, not wrong ones. */
  const EVENT_SIGNATURES = Object.freeze({
    TabOpened: "TabOpened(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount, uint64 expiresAt, string taskRef)",
    TabReleased: "TabReleased(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount)",
    TabClaimed: "TabClaimed(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount)",
    TabRefunded: "TabRefunded(uint256 indexed tabId, address indexed payer, uint256 amount)"
  });

  /* Status enum from the contract, in declaration order. getTab returns the
     index. */
  const STATUS_NAMES = Object.freeze(["Open", "Released", "Refunded"]);

  /* REFUND_GRACE = 48 hours in the contract. */
  const GRACE_SECONDS = 48 * 3600;

  /* USDC ERC-20 units on Arc use 6 decimals (contract header comment). */
  const USDC_DECIMALS = 6;

  function toBig(v) {
    if (typeof v === "bigint") return v;
    if (typeof v === "number") return BigInt(v);
    if (typeof v === "string") return BigInt(v);
    if (v && typeof v.toString === "function") return BigInt(v.toString());
    throw new Error("cannot convert to bigint: " + v);
  }

  /* Format an integer USDC amount (6 decimals) without floating point.
     5000000n -> "5", 1234567n -> "1.234567", 100n -> "0.0001". */
  function formatUsdc(units) {
    const u = toBig(units);
    const neg = u < 0n;
    const abs = neg ? -u : u;
    const base = 10n ** BigInt(USDC_DECIMALS);
    const whole = abs / base;
    let frac = (abs % base).toString().padStart(USDC_DECIMALS, "0").replace(/0+$/, "");
    return (neg ? "-" : "") + whole.toString() + (frac ? "." + frac : "");
  }

  /* Settlement phase of an open tab at a given unix time, from the contract
     rules: refund is allowed from expiresAt up to but not including
     expiresAt + REFUND_GRACE; claim from expiresAt + REFUND_GRACE onwards. */
  function openPhase(expiresAt, now) {
    const exp = Number(expiresAt);
    if (now < exp) return "Open, before expiry";
    if (now < exp + GRACE_SECONDS) return "Open, in refund grace window";
    return "Open, claimable by agent";
  }

  /* Reduce decoded logs into tabs and totals.

     events: array of { name, args, txHash, blockNumber, logIndex } where
     name is one of the four event names and args holds the fields named in
     EVENT_SIGNATURES (bigint-compatible values for tabId, amount, expiresAt).

     Returns { tabs: [...], totals: {...}, events: [...sorted] }.
     Totals are bigint USDC units:
       opened    sum of TabOpened.amount
       released  sum of TabReleased.amount
       claimed   sum of TabClaimed.amount
       refunded  sum of TabRefunded.amount
       settledToAgents = released + claimed
       stillOpen = opened - released - claimed - refunded
     Each tab carries: tabId, payer, agent, amount, expiresAt, taskRef,
     outcome ("Open" | "Released" | "Claimed" | "Refunded"),
     contractStatus (the Status enum name the contract would report:
     Released for both released and claimed tabs), and tx hashes. */
  function summarize(events) {
    const sorted = events.slice().sort(function (a, b) {
      const ba = Number(a.blockNumber), bb = Number(b.blockNumber);
      if (ba !== bb) return ba - bb;
      return Number(a.logIndex) - Number(b.logIndex);
    });
    const tabs = new Map();
    const totals = { opened: 0n, released: 0n, claimed: 0n, refunded: 0n, count: 0 };
    const problems = [];

    for (const ev of sorted) {
      const id = toBig(ev.args.tabId).toString();
      if (ev.name === "TabOpened") {
        if (tabs.has(id)) { problems.push("tab " + id + " opened twice"); continue; }
        const amount = toBig(ev.args.amount);
        tabs.set(id, {
          tabId: id,
          payer: ev.args.payer,
          agent: ev.args.agent,
          amount: amount,
          expiresAt: Number(toBig(ev.args.expiresAt)),
          taskRef: ev.args.taskRef || "",
          outcome: "Open",
          contractStatus: "Open",
          openedTx: ev.txHash,
          settledTx: null,
          openedBlock: Number(ev.blockNumber)
        });
        totals.opened += amount;
        totals.count += 1;
        continue;
      }
      const tab = tabs.get(id);
      if (!tab) { problems.push(ev.name + " for unknown tab " + id); continue; }
      if (tab.outcome !== "Open") { problems.push(ev.name + " on already settled tab " + id); continue; }
      const amount = toBig(ev.args.amount);
      if (amount !== tab.amount) problems.push(ev.name + " amount differs from TabOpened amount for tab " + id);
      if (ev.name === "TabReleased") {
        tab.outcome = "Released"; tab.contractStatus = "Released"; totals.released += amount;
      } else if (ev.name === "TabClaimed") {
        tab.outcome = "Claimed"; tab.contractStatus = "Released"; totals.claimed += amount;
      } else if (ev.name === "TabRefunded") {
        tab.outcome = "Refunded"; tab.contractStatus = "Refunded"; totals.refunded += amount;
      } else {
        problems.push("unknown event " + ev.name);
        continue;
      }
      tab.settledTx = ev.txHash;
    }

    totals.settledToAgents = totals.released + totals.claimed;
    totals.stillOpen = totals.opened - totals.released - totals.claimed - totals.refunded;

    return {
      tabs: Array.from(tabs.values()).sort(function (a, b) { return Number(a.tabId) - Number(b.tabId); }),
      totals: totals,
      events: sorted,
      problems: problems
    };
  }

  /* Human readable status for a tab row at time `now`. */
  function describeTab(tab, now) {
    if (tab.outcome !== "Open") return tab.outcome;
    return openPhase(tab.expiresAt, now);
  }

  const api = {
    EVENT_SIGNATURES: EVENT_SIGNATURES,
    STATUS_NAMES: STATUS_NAMES,
    GRACE_SECONDS: GRACE_SECONDS,
    USDC_DECIMALS: USDC_DECIMALS,
    formatUsdc: formatUsdc,
    openPhase: openPhase,
    summarize: summarize,
    describeTab: describeTab
  };

  root.AgentTabProof = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
