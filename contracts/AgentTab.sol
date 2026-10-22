// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Minimal ERC-20 surface AgentTab needs from USDC.
/// On Arc the USDC ERC-20 interface lives at a fixed address and uses 6 decimals.
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

/// @title AgentTab
/// @notice A minimal on chain tab for paying AI agents in USDC on Arc.
/// A payer deposits USDC into a tab naming an agent wallet. When the work is
/// done the payer releases the tab and the contract pays the agent. If the
/// payer never releases, the payer can refund the tab after the expiry they
/// set at opening. There are no admin keys, no owner, no upgrade path, and no
/// way to move funds out of a tab except release to its agent or refund to
/// its payer after expiry.
contract AgentTab {
    enum Status {
        Open,
        Released,
        Refunded
    }

    struct Tab {
        address payer;
        address agent;
        uint256 amount;
        uint64 expiresAt;
        Status status;
    }

    IERC20 public immutable usdc;

    uint256 public nextTabId;
    mapping(uint256 => Tab) private _tabs;

    bool private _locked;

    event TabOpened(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount, uint64 expiresAt);
    event TabReleased(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount);
    event TabRefunded(uint256 indexed tabId, address indexed payer, uint256 amount);

    modifier nonReentrant() {
        require(!_locked, "reentrant call");
        _locked = true;
        _;
        _locked = false;
    }

    constructor(address usdcAddress) {
        require(usdcAddress != address(0), "usdc is zero address");
        usdc = IERC20(usdcAddress);
    }

    /// @notice Open a tab. The caller is the payer and must have approved this
    /// contract to spend at least `amount` of USDC first.
    /// @param agent The wallet that gets paid on release.
    /// @param amount USDC amount in ERC-20 units (6 decimals on Arc).
    /// @param durationSeconds Seconds from now until the payer may refund.
    /// @return tabId The id of the new tab.
    function openTab(address agent, uint256 amount, uint64 durationSeconds) external nonReentrant returns (uint256 tabId) {
        require(agent != address(0), "agent is zero address");
        require(amount > 0, "amount is zero");
        require(durationSeconds > 0, "duration is zero");

        tabId = nextTabId++;
        uint64 expiresAt = uint64(block.timestamp) + durationSeconds;
        _tabs[tabId] = Tab({payer: msg.sender, agent: agent, amount: amount, expiresAt: expiresAt, status: Status.Open});

        emit TabOpened(tabId, msg.sender, agent, amount, expiresAt);

        require(usdc.transferFrom(msg.sender, address(this), amount), "deposit transfer failed");
    }

    /// @notice Release an open tab, paying its full amount to its agent.
    /// Only the payer who opened the tab can release it.
    function release(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.payer, "only the payer can release");

        tab.status = Status.Released;

        emit TabReleased(tabId, tab.payer, tab.agent, tab.amount);

        require(usdc.transfer(tab.agent, tab.amount), "release transfer failed");
    }

    /// @notice Refund an open tab back to its payer after its expiry.
    /// Only the payer who opened the tab can refund it, and only once the
    /// expiry they set has passed.
    function refund(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.payer, "only the payer can refund");
        require(block.timestamp >= tab.expiresAt, "tab has not expired yet");

        tab.status = Status.Refunded;

        emit TabRefunded(tabId, tab.payer, tab.amount);

        require(usdc.transfer(tab.payer, tab.amount), "refund transfer failed");
    }

    /// @notice Read one tab.
    function getTab(uint256 tabId)
        external
        view
        returns (address payer, address agent, uint256 amount, uint64 expiresAt, Status status)
    {
        Tab storage tab = _tabs[tabId];
        return (tab.payer, tab.agent, tab.amount, tab.expiresAt, tab.status);
    }
}
