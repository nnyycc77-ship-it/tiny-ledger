// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AgentTab} from "../contracts/AgentTab.sol";
import {MockUSDC} from "./MockUSDC.sol";

/// @notice Minimal cheatcode surface used by these tests, declared locally so
/// the suite needs no external dependency. This is the canonical Foundry
/// cheatcode address.
interface Vm {
    function prank(address msgSender) external;
    function warp(uint256 newTimestamp) external;
    function expectRevert() external;
}

/// @notice Dependency free Foundry tests for AgentTab. Local only, no fork.
contract AgentTabTest {
    Vm private constant vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    MockUSDC private usdc;
    AgentTab private tabs;

    address private payer = address(0x1001);
    address private agent = address(0x1002);
    address private stranger = address(0x1003);

    uint256 private constant FIVE_USDC = 5_000_000; // 5 USDC at 6 decimals
    uint64 private constant ONE_DAY = 1 days;

    function setUp() public {
        usdc = new MockUSDC();
        tabs = new AgentTab(address(usdc));
        usdc.mint(payer, 100_000_000); // 100 USDC
    }

    // --- helpers ---

    function _approveAndOpen(uint256 amount, uint64 duration) internal returns (uint256 tabId) {
        vm.prank(payer);
        usdc.approve(address(tabs), amount);
        vm.prank(payer);
        tabId = tabs.openTab(agent, amount, duration);
    }

    function _assertEq(uint256 a, uint256 b, string memory what) internal pure {
        if (a != b) revert(string.concat("assertEq failed: ", what));
    }

    function _assertEq(address a, address b, string memory what) internal pure {
        if (a != b) revert(string.concat("assertEq failed: ", what));
    }

    // --- tests ---

    function testDepositHoldsFundsInContract() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        _assertEq(usdc.balanceOf(address(tabs)), FIVE_USDC, "contract holds the deposit");
        _assertEq(usdc.balanceOf(payer), 100_000_000 - FIVE_USDC, "payer balance dropped by the deposit");

        (address p, address a, uint256 amt, uint64 exp, AgentTab.Status st) = tabs.getTab(tabId);
        _assertEq(p, payer, "tab payer");
        _assertEq(a, agent, "tab agent");
        _assertEq(amt, FIVE_USDC, "tab amount");
        if (exp <= block.timestamp) revert("expiry should be in the future");
        if (st != AgentTab.Status.Open) revert("tab should be open");
    }

    function testReleasePaysAgentInFull() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.prank(payer);
        tabs.release(tabId);

        _assertEq(usdc.balanceOf(agent), FIVE_USDC, "agent received the full tab");
        _assertEq(usdc.balanceOf(address(tabs)), 0, "contract is empty after release");
        (, , , , AgentTab.Status st) = tabs.getTab(tabId);
        if (st != AgentTab.Status.Released) revert("tab should be released");
    }

    function testRefundAfterExpiryReturnsFundsToPayer() public {
        uint256 tabId = _approveAndOpen(FIVE_USDC, ONE_DAY);

        vm.warp(block.timestamp + ONE_DAY + 1);
        vm.prank(payer);
        tabs.refund(tabId);

        _assertEq(usdc.balanceOf(payer), 100_000_000, "payer got everything back");
        _assertEq(usdc.balanceOf(address(tabs)), 0, "contract is empty after refund");
        (, , , , AgentTab.Status st) = tabs.getTab(tabId);
        if (st != AgentTab.Status.Refunded) revert("tab should be refunded");
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
        tabs.openTab(agent, FIVE_USDC, ONE_DAY);
    }

    function testOpenTabZeroAgentReverts() public {
        vm.prank(payer);
        usdc.approve(address(tabs), FIVE_USDC);
        vm.prank(payer);
        vm.expectRevert();
        tabs.openTab(address(0), FIVE_USDC, ONE_DAY);
    }
}
