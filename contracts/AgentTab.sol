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
/// payer never releases, the tab settles by time instead: once the expiry the
/// payer set has passed, the payer has a grace window of 48 hours to refund
/// the tab, and after that window the agent can claim the tab and be paid.
/// There are no admin keys, no owner, no upgrade path, and no way to move
/// funds out of a tab except release or claim to its agent, or refund to its
/// payer inside the grace window.
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
        string taskRef;
    }

    /// @notice How long after expiry the payer keeps the refund right before
    /// the agent claim opens. Refund is available from the expiry up to but
    /// not including expiry plus this window; claim is available from expiry
    /// plus this window onwards.
    uint64 public constant REFUND_GRACE = 48 hours;

    IERC20 public immutable usdc;

    uint256 public nextTabId;
    mapping(uint256 => Tab) private _tabs;

    bool private _locked;

    event TabOpened(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount, uint64 expiresAt, string taskRef);
    event TabReleased(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount);
    event TabClaimed(uint256 indexed tabId, address indexed payer, address indexed agent, uint256 amount);
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
    /// @param agent The wallet that gets paid on release or claim. It cannot
    /// be the zero address, this contract, or the payer.
    /// @param amount USDC amount in ERC-20 units (6 decimals on Arc).
    /// @param durationSeconds Seconds from now until the tab expiry.
    /// @param taskRef Optional reference linking the tab to a job, for example
    /// a marketplace intent id. May be empty. It is stored on the tab and
    /// emitted in TabOpened; the contract itself never acts on it.
    /// @return tabId The id of the new tab.
    function openTab(address agent, uint256 amount, uint64 durationSeconds, string calldata taskRef)
        external
        nonReentrant
        returns (uint256 tabId)
    {
        require(agent != address(0), "agent is zero address");
        require(agent != address(this), "agent is this contract");
        require(agent != msg.sender, "agent is the payer");
        require(amount > 0, "amount is zero");
        require(durationSeconds > 0, "duration is zero");

        tabId = nextTabId++;
        uint64 expiresAt = uint64(block.timestamp) + durationSeconds;
        _tabs[tabId] = Tab({
            payer: msg.sender,
            agent: agent,
            amount: amount,
            expiresAt: expiresAt,
            status: Status.Open,
            taskRef: taskRef
        });

        emit TabOpened(tabId, msg.sender, agent, amount, expiresAt, taskRef);

        require(usdc.transferFrom(msg.sender, address(this), amount), "deposit transfer failed");
    }

    /// @notice Release an open tab, paying its full amount to its agent.
    /// Only the payer who opened the tab can release it, at any time while
    /// the tab is open.
    function release(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.payer, "only the payer can release");

        tab.status = Status.Released;

        emit TabReleased(tabId, tab.payer, tab.agent, tab.amount);

        require(usdc.transfer(tab.agent, tab.amount), "release transfer failed");
    }

    /// @notice Claim an open tab after the refund grace window has ended,
    /// paying its full amount to its agent. Only the agent named on the tab
    /// can claim it. This is the settlement backstop: a payer who received
    /// the work and then went silent cannot reclaim the deposit once the
    /// grace window has passed.
    function claim(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.agent, "only the agent can claim");
        require(block.timestamp >= uint256(tab.expiresAt) + REFUND_GRACE, "grace window has not ended");

        tab.status = Status.Released;

        emit TabClaimed(tabId, tab.payer, tab.agent, tab.amount);

        require(usdc.transfer(tab.agent, tab.amount), "claim transfer failed");
    }

    /// @notice Refund an open tab back to its payer. Only the payer who opened
    /// the tab can refund it, and only inside the grace window: from the
    /// expiry they set until 48 hours after it. Once the window ends the
    /// refund right is gone and the agent claim has priority.
    function refund(uint256 tabId) external nonReentrant {
        Tab storage tab = _tabs[tabId];
        require(tab.status == Status.Open, "tab is not open");
        require(msg.sender == tab.payer, "only the payer can refund");
        require(block.timestamp >= tab.expiresAt, "tab has not expired yet");
        require(block.timestamp < uint256(tab.expiresAt) + REFUND_GRACE, "grace window has ended");

        tab.status = Status.Refunded;

        emit TabRefunded(tabId, tab.payer, tab.amount);

        require(usdc.transfer(tab.payer, tab.amount), "refund transfer failed");
    }

    /// @notice Read one tab.
    function getTab(uint256 tabId)
        external
        view
        returns (address payer, address agent, uint256 amount, uint64 expiresAt, Status status, string memory taskRef)
    {
        Tab storage tab = _tabs[tabId];
        return (tab.payer, tab.agent, tab.amount, tab.expiresAt, tab.status, tab.taskRef);
    }
}
