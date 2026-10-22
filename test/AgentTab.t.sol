// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AgentTab} from "../contracts/AgentTab.sol";
import {MockUSDC} from "./MockUSDC.sol";
import {FlakyUSDC} from "./FlakyUSDC.sol";
import {ReentrantUSDC, MaliciousAgent} from "./ReentrantUSDC.sol";

/// @notice Minimal cheatcode surface used by these tests, declared locally so
/// the suite needs no external dependency. This is the canonical Foundry
/// cheatcode address.
interface Vm {
    function prank(address msgSender) external;
    function warp(uint256 newTimestamp) external;
    function expectRevert() external;
    function expectEmit(bool checkTopic1, bool checkTopic2, bool checkTopic3, bool checkData) external;
}

/// @notice Dependency free Foundry tests for AgentTab. Local only, no fork.
contract AgentTabTest {
    Vm private constant vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    /// @notice Mirrors the contract event so a test can state the exact log
    /// it expects openTab to emit.
    event TabOpened(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount, uint64 expiresAt, string taskRef);

    MockUSDC private usdc;
    AgentTab private tabs;

    address private payer = address(0x1001);
    address private agent = address(0x1002);
    address private stranger = address(0x1003);
    address private payer2 = address(0x1004);
    address private agent2 = address(0x1005);

    uint256 private constant FIVE_USDC = 5_000_000; // 5 USDC at 6 decimals
    uint256 private constant SEVEN_USDC = 7_000_000; // 7 USDC at 6 decimals
    uint64 private constant ONE_DAY = 1 days;
    uint64 private constant GRACE = 48 hours;

    function setUp() public {
        usdc = new MockUSDC();
        tabs = new AgentTab(address(usdc));
        usdc.mint(payer, 100_000_000); // 100 USDC
        usdc.mint(payer2, 100_000_000); // 100 USDC
    }

    // --- helpers ---

    function _approveAndOpen(uint256 amount, uint64 duration) internal returns (uint256 tabId) {
        return _approveAndOpenFor(payer, agent, amount, duration, "");
    }

    function _approveAndOpenFor(address from, address toAgent, uint256 amount, uint64 duration, string memory taskRef)
        internal
        returns (uint256 tabId)
    {
        vm.prank(from);
        usdc.approve(address(tabs), amount);
        vm.prank(from);
        tabId = tabs.openTab(toAgent, amount, duration, taskRef);
    }

    function _expiryOf(uint256 tabId) internal view returns (uint64 exp) {
        (, , , exp, , ) = tabs.getTab(tabId);
    }

    function _statusOf(uint256 tabId) internal view returns (AgentTab.Status st) {
        (, , , , st, ) = tabs.getTab(tabId);
    }

    function _assertEq(uint256 a, uint256 b, string memory what) internal pure {
        if (a != b) revert(string.concat("assertEq failed: ", what));
    }

    function _assertEq(address a, address b, string memory what) internal pure {
        if (a != b) revert(string.concat("assertEq failed: ", what));
    }

    // --- the original suite, carried forward ---

    function testDepositHoldsFundsInContract() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        _assertEq(usdc.balanceOf(address(tabs)), FIVE_USDC, "contract holds the deposit");
        _assertEq(usdc.balanceOf(payer), 100_000_000 - FIVE_USDC, "payer balance dropped by the deposit");

        (address p, address a, uint256 amt, uint64 exp, AgentTab.Status st, string memory ref) = tabs.getTab(tabId);
        _assertEq(p, payer, "tab payer");
        _assertEq(a, agent, "tab agent");
        _assertEq(amt, FIVE_USDC, "tab amount");
        if (exp <= block.timestamp) revert("expiry should be in the future");
        if (st != AgentTab.Status.Open) revert("tab should be open");
        if (bytes(ref).length != 0) revert("taskRef should be empty when none is given");
    }

    function testReleasePaysAgentInFull() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(payer);
        tabs.release(tabId);

        _assertEq(usdc.balanceOf(agent), FIVE_USDC, "agent received the full tab");
        _assertEq(usdc.balanceOf(address(tabs)), 0, "contract is empty after release");
        if (_statusOf(tabId) != AgentTab.Status.Released) revert("tab should be released");
    }

    function testRefundAfterExpiryReturnsFundsToPayer() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(block.timestamp + ONE_DAY + 1); // inside the grace window
        vm.prank(payer);
        tabs.refund(tabId);

        _assertEq(usdc.balanceOf(payer), 100_000_000, "payer got everything back");
        _assertEq(usdc.balanceOf(address(tabs)), 0, "contract is empty after refund");
        if (_statusOf(tabId) != AgentTab.Status.Refunded) revert("tab should be refunded");
    }

    function testRefundBeforeExpiryReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(payer);
        vm.expectRevert();
        tabs.refund(tabId);
    }

    function testStrangerCannotRelease() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(stranger);
        vm.expectRevert();
        tabs.release(tabId);
    }

    function testAgentCannotReleaseOwnTab() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(agent);
        vm.expectRevert();
        tabs.release(tabId);
    }

    function testStrangerCannotRefundAfterExpiry() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(block.timestamp + ONE_DAY + 1);
        vm.prank(stranger);
        vm.expectRevert();
        tabs.refund(tabId);
    }

    function testDoubleReleaseReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(payer);
        tabs.release(tabId);

        vm.prank(payer);
        vm.expectRevert();
        tabs.release(tabId);
    }

    function testRefundAfterReleaseReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(payer);
        tabs.release(tabId);

        vm.warp(block.timestamp + ONE_DAY + 1);
        vm.prank(payer);
        vm.expectRevert();
        tabs.refund(tabId);
    }

    function testOpenTabWithoutApprovalReverts() public {
        vm.prank(payer);
        vm.expectRevert();
        tabs.openTab(agent, FIVE_USDC, ONE_DAY, "");
    }

    function testOpenTabZeroAgentReverts() public {
        vm.prank(payer);
        usdc.approve(address(tabs), FIVE_USDC);
        vm.prank(payer);
        vm.expectRevert();
        tabs.openTab(address(0), FIVE_USDC, ONE_DAY, "");
    }

    // --- v2: recipient rules ---

    function testOpenTabContractAsAgentReverts() public {
        vm.prank(payer);
        usdc.approve(address(tabs), FIVE_USDC);
        vm.prank(payer);
        vm.expectRevert();
        tabs.openTab(address(tabs), FIVE_USDC, ONE_DAY, "");
    }

    function testOpenTabPayerAsAgentReverts() public {
        vm.prank(payer);
        usdc.approve(address(tabs), FIVE_USDC);
        vm.prank(payer);
        vm.expectRevert();
        tabs.openTab(payer, FIVE_USDC, ONE_DAY, "");
    }

    // --- v2: grace window, claim, and refund boundaries ---

    function testRefundExactlyAtExpirySucceeds() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(_expiryOf(tabId)); // the exact expiry second
        vm.prank(payer);
        tabs.refund(tabId);

        _assertEq(usdc.balanceOf(payer), 100_000_000, "payer refunded at exact expiry");
        if (_statusOf(tabId) != AgentTab.Status.Refunded) revert("tab should be refunded");
    }

    function testClaimBeforeGraceEndsReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(uint256(_expiryOf(tabId)) + GRACE - 1); // one second before the claim opens
        vm.prank(agent);
        vm.expectRevert();
        tabs.claim(tabId);
    }

    function testClaimByAgentAfterGracePaysInFull() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(uint256(_expiryOf(tabId)) + GRACE); // the exact second the claim opens
        vm.prank(agent);
        tabs.claim(tabId);

        _assertEq(usdc.balanceOf(agent), FIVE_USDC, "agent claimed the full tab");
        _assertEq(usdc.balanceOf(address(tabs)), 0, "contract is empty after claim");
        if (_statusOf(tabId) != AgentTab.Status.Released) revert("claimed tab should read released");
    }

    function testClaimByStrangerAfterGraceReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(uint256(_expiryOf(tabId)) + GRACE);
        vm.prank(stranger);
        vm.expectRevert();
        tabs.claim(tabId);
    }

    function testRefundAfterGraceEndsReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(uint256(_expiryOf(tabId)) + GRACE); // window over, claim has priority now
        vm.prank(payer);
        vm.expectRevert();
        tabs.refund(tabId);
    }

    function testDoubleClaimReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(uint256(_expiryOf(tabId)) + GRACE);
        vm.prank(agent);
        tabs.claim(tabId);

        vm.prank(agent);
        vm.expectRevert();
        tabs.claim(tabId);
    }

    function testReleaseAfterRefundReverts() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(_expiryOf(tabId));
        vm.prank(payer);
        tabs.refund(tabId);

        vm.prank(payer);
        vm.expectRevert();
        tabs.release(tabId);
    }

    // --- v2: several tabs at once ---

    function testMultipleTabsSettleIndependently() public {
        uint256 tabA = _approveAndOpenFor(payer, agent, FIVE_USDC, ONE_DAY, "job A");
        uint256 tabB = _approveAndOpenFor(payer2, agent2, SEVEN_USDC, ONE_DAY, "job B");

        // Tab A settles by payer release right away.
        vm.prank(payer);
        tabs.release(tabA);

        // Tab B settles by agent claim after its grace window.
        vm.warp(uint256(_expiryOf(tabB)) + GRACE);
        vm.prank(agent2);
        tabs.claim(tabB);

        _assertEq(usdc.balanceOf(agent), FIVE_USDC, "agent A paid by release");
        _assertEq(usdc.balanceOf(agent2), SEVEN_USDC, "agent B paid by claim");
        _assertEq(usdc.balanceOf(payer), 100_000_000 - FIVE_USDC, "payer A spent only tab A");
        _assertEq(usdc.balanceOf(payer2), 100_000_000 - SEVEN_USDC, "payer B spent only tab B");
        _assertEq(usdc.balanceOf(address(tabs)), 0, "contract is empty at the end");
        if (_statusOf(tabA) != AgentTab.Status.Released) revert("tab A should be released");
        if (_statusOf(tabB) != AgentTab.Status.Released) revert("tab B should be released");
    }

    // --- v2: task reference ---

    function testTaskRefStoredAndEmitted() public {
        string memory ref = "marketplace job 479";

        vm.prank(payer);
        usdc.approve(address(tabs), FIVE_USDC);

        uint64 expectedExpiry = uint64(block.timestamp) + ONE_DAY;
        vm.expectEmit(true, true, true, true);
        emit TabOpened(0, payer, agent, FIVE_USDC, expectedExpiry, ref);

        vm.prank(payer);
        uint256 tabId = tabs.openTab(agent, FIVE_USDC, ONE_DAY, ref);

        (, , , , , string memory stored) = tabs.getTab(tabId);
        if (keccak256(bytes(stored)) != keccak256(bytes(ref))) revert("stored taskRef does not match");
    }

    // --- v2: token failure paths ---

    function testOpenRevertsWhenDepositTransferFails() public {
        FlakyUSDC flaky = new FlakyUSDC();
        AgentTab flakyTabs = new AgentTab(address(flaky));
        flaky.mint(payer, 100_000_000);

        vm.prank(payer);
        flaky.approve(address(flakyTabs), FIVE_USDC);
        flaky.setFailTransferFroms(true);

        vm.prank(payer);
        vm.expectRevert();
        flakyTabs.openTab(agent, FIVE_USDC, ONE_DAY, "");

        _assertEq(flakyTabs.nextTabId(), 0, "no tab recorded after a failed deposit");
        _assertEq(flaky.balanceOf(payer), 100_000_000, "payer balance unchanged");
        _assertEq(flaky.balanceOf(address(flakyTabs)), 0, "no funds moved");
    }

    function testReleaseRevertsWhenPayoutTransferFails() public {
        FlakyUSDC flaky = new FlakyUSDC();
        AgentTab flakyTabs = new AgentTab(address(flaky));
        flaky.mint(payer, 100_000_000);

        vm.prank(payer);
        flaky.approve(address(flakyTabs), FIVE_USDC);
        vm.prank(payer);
        uint256 tabId = flakyTabs.openTab(agent, FIVE_USDC, ONE_DAY, "");

        flaky.setFailTransfers(true);
        vm.prank(payer);
        vm.expectRevert();
        flakyTabs.release(tabId);

        (, , , , AgentTab.Status st, ) = flakyTabs.getTab(tabId);
        if (st != AgentTab.Status.Open) revert("tab should stay open after a failed release");
        _assertEq(flaky.balanceOf(address(flakyTabs)), FIVE_USDC, "funds still held after a failed release");

        flaky.setFailTransfers(false);
        vm.prank(payer);
        flakyTabs.release(tabId);
        _assertEq(flaky.balanceOf(agent), FIVE_USDC, "agent paid once the token recovers");
    }

    // --- v2: reentrancy attempts ---

    function testReentrantAgentCannotDoubleSettleOnRelease() public {
        ReentrantUSDC rUsdc = new ReentrantUSDC();
        AgentTab rTabs = new AgentTab(address(rUsdc));
        MaliciousAgent evil = new MaliciousAgent();
        rUsdc.mint(payer, 100_000_000);

        vm.prank(payer);
        rUsdc.approve(address(rTabs), FIVE_USDC);
        vm.prank(payer);
        uint256 tabId = rTabs.openTab(address(evil), FIVE_USDC, ONE_DAY, "");
        evil.arm(rTabs, tabId);

        vm.prank(payer);
        rTabs.release(tabId);

        if (!evil.reentryAttempted()) revert("the payout hook should have fired");
        if (evil.reentrySucceeded()) revert("reentry must not settle the tab twice");
        _assertEq(rUsdc.balanceOf(address(evil)), FIVE_USDC, "agent paid exactly once");
        _assertEq(rUsdc.balanceOf(address(rTabs)), 0, "contract is empty after release");
    }

    function testReentrantAgentCannotDoubleSettleOnClaim() public {
        ReentrantUSDC rUsdc = new ReentrantUSDC();
        AgentTab rTabs = new AgentTab(address(rUsdc));
        MaliciousAgent evil = new MaliciousAgent();
        rUsdc.mint(payer, 100_000_000);

        vm.prank(payer);
        rUsdc.approve(address(rTabs), FIVE_USDC);
        vm.prank(payer);
        uint256 tabId = rTabs.openTab(address(evil), FIVE_USDC, ONE_DAY, "");
        evil.arm(rTabs, tabId);

        (, , , uint64 exp, , ) = rTabs.getTab(tabId);
        vm.warp(uint256(exp) + GRACE);
        evil.claimTab();

        if (!evil.reentryAttempted()) revert("the payout hook should have fired");
        if (evil.reentrySucceeded()) revert("reentry must not settle the tab twice");
        _assertEq(rUsdc.balanceOf(address(evil)), FIVE_USDC, "agent paid exactly once");
        _assertEq(rUsdc.balanceOf(address(rTabs)), 0, "contract is empty after claim");
    }
}
