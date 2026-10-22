// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AgentTab} from "../contracts/AgentTab.sol";

/// @notice Hook a contract token receiver can implement. The reentrant token
/// below calls it on contract recipients during a transfer, which is the
/// moment a hostile receiver would try to reenter the paying contract.
interface ITransferHook {
    function onTransferReceived() external;
}

/// @notice Test only USDC stand in that notifies contract recipients during
/// transfer, giving a hostile agent its chance to reenter AgentTab mid
/// payout. Never deploy this on mainnet.
contract ReentrantUSDC {
    string public name = "Reentrant USDC";
    string public symbol = "USDC";
    uint8 public decimals = 6;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 amount);
    event Approval(address indexed owner, address indexed spender, uint256 amount);

    function mint(address to, uint256 amount) external {
        totalSupply += amount;
        balanceOf[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        _move(msg.sender, to, amount);
        _notify(to);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        require(allowed >= amount, "allowance too low");
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        _move(from, to, amount);
        _notify(to);
        return true;
    }

    function _notify(address to) internal {
        if (to.code.length > 0) {
            try ITransferHook(to).onTransferReceived() {} catch {}
        }
    }

    function _move(address from, address to, uint256 amount) internal {
        require(balanceOf[from] >= amount, "balance too low");
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
    }
}

/// @notice Test only hostile agent. When a payout transfer reaches it, it
/// tries to reenter AgentTab and settle the same tab a second time, once
/// through release and once through claim, and records whether either
/// attempt succeeded.
contract MaliciousAgent is ITransferHook {
    AgentTab public tabs;
    uint256 public tabId;
    bool public reentryAttempted;
    bool public reentrySucceeded;

    function arm(AgentTab tabsContract, uint256 id) external {
        tabs = tabsContract;
        tabId = id;
    }

    function claimTab() external {
        tabs.claim(tabId);
    }

    function onTransferReceived() external override {
        reentryAttempted = true;
        try tabs.release(tabId) {
            reentrySucceeded = true;
        } catch {}
        try tabs.claim(tabId) {
            reentrySucceeded = true;
        } catch {}
    }
}
