// contracts/SennaWallet.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title SennaWallet Smart Contract
 * @dev AI-Powered Wallet Management Contract for Somnia Blockchain
 * Features: Multi-signature, transaction limits, recovery, and AI agent integration
 */
contract SennaWallet {
    // Structs
    struct Transaction {
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 confirmationCount;
    }

    struct WalletSettings {
        uint256 dailyLimit;
        uint256 transactionLimit;
        address recoveryAgent;
        bool isActive;
    }

    // Events
    event Deposit(address indexed sender, uint256 amount, uint256 balance);
    event TransactionCreated(
        uint256 indexed txId,
        address indexed to,
        uint256 value,
        bytes data
    );
    event TransactionConfirmed(uint256 indexed txId, address indexed owner);
    event TransactionExecuted(uint256 indexed txId, address indexed executor);
    event WalletSettingsUpdated(address indexed owner);
    event RecoveryInitiated(address indexed oldOwner, address indexed newOwner);
    event RecoveryCompleted(address indexed oldOwner, address indexed newOwner);

    // State Variables
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public requiredConfirmations;

    Transaction[] public transactions;
    mapping(uint256 => mapping(address => bool)) public isConfirmed;

    WalletSettings public settings;
    address public aiAgent;
    
    // Security features
    mapping(address => uint256) public lastTransactionTime;
    mapping(address => uint256) public dailySpent;
    uint256 public constant DAY = 1 days;

    // Recovery system
    address public pendingRecoveryOwner;
    uint256 public recoveryInitTime;
    uint256 public constant RECOVERY_DELAY = 7 days;

    // Modifiers
    modifier onlyOwner() {
        require(isOwner[msg.sender], "SennaWallet: caller is not an owner");
        _;
    }

    modifier onlyAIAgent() {
        require(msg.sender == aiAgent, "SennaWallet: caller is not AI agent");
        _;
    }

    modifier txExists(uint256 _txId) {
        require(_txId < transactions.length, "SennaWallet: transaction does not exist");
        _;
    }

    modifier notExecuted(uint256 _txId) {
        require(!transactions[_txId].executed, "SennaWallet: transaction already executed");
        _;
    }

    modifier notConfirmed(uint256 _txId) {
        require(!isConfirmed[_txId][msg.sender], "SennaWallet: transaction already confirmed");
        _;
    }

    /**
     * @dev Constructor - Initializes the Senna Wallet
     * @param _owners List of initial owners
     * @param _requiredConfirmations Number of required confirmations
     * @param _aiAgent Address of the AI Agent
     */
    constructor(
        address[] memory _owners,
        uint256 _requiredConfirmations,
        address _aiAgent
    ) {
        require(_owners.length > 0, "SennaWallet: owners required");
        require(
            _requiredConfirmations > 0 && _requiredConfirmations <= _owners.length,
            "SennaWallet: invalid number of required confirmations"
        );

        for (uint256 i = 0; i < _owners.length; i++) {
            address owner = _owners[i];
            require(owner != address(0), "SennaWallet: invalid owner");
            require(!isOwner[owner], "SennaWallet: owner not unique");

            isOwner[owner] = true;
            owners.push(owner);
        }

        requiredConfirmations = _requiredConfirmations;
        aiAgent = _aiAgent;

        // Initialize default settings
        settings = WalletSettings({
            dailyLimit: 10 ether,
            transactionLimit: 5 ether,
            recoveryAgent: _aiAgent,
            isActive: true
        });
    }

    /**
     * @dev Receive function - Allows the contract to receive ETH
     */
    receive() external payable {
        emit Deposit(msg.sender, msg.value, address(this).balance);
    }

    /**
     * @dev Fallback function
     */
    fallback() external payable {
        emit Deposit(msg.sender, msg.value, address(this).balance);
    }

    // TRANSACTION MANAGEMENT FUNCTIONS

    /**
     * @dev Submit a transaction for approval
     * @param _to Target address
     * @param _value ETH value to send
     * @param _data Transaction data
     * @return txId The ID of the created transaction
     */
    function submitTransaction(
        address _to,
        uint256 _value,
        bytes memory _data
    ) 
        public 
        onlyOwner 
        returns (uint256 txId) 
    {
        require(_to != address(0), "SennaWallet: invalid recipient");
        require(_value <= settings.transactionLimit, "SennaWallet: exceeds transaction limit");
        
        // Check daily limit
        _checkDailyLimit(msg.sender, _value);

        txId = transactions.length;
        transactions.push(Transaction({
            to: _to,
            value: _value,
            data: _data,
            executed: false,
            confirmationCount: 0
        }));

        emit TransactionCreated(txId, _to, _value, _data);

        // Auto-confirm if from AI Agent or if only one confirmation needed
        if (msg.sender == aiAgent || requiredConfirmations == 1) {
            confirmTransaction(txId);
        }
    }

    /**
     * @dev Confirm a transaction
     * @param _txId Transaction ID
     */
    function confirmTransaction(uint256 _txId)
        public
        onlyOwner
        txExists(_txId)
        notExecuted(_txId)
        notConfirmed(_txId)
    {
        Transaction storage transaction = transactions[_txId];
        isConfirmed[_txId][msg.sender] = true;
        transaction.confirmationCount += 1;

        emit TransactionConfirmed(_txId, msg.sender);

        // Auto-execute if enough confirmations
        if (transaction.confirmationCount >= requiredConfirmations) {
            executeTransaction(_txId);
        }
    }

    /**
     * @dev Execute a confirmed transaction
     * @param _txId Transaction ID
     */
    function executeTransaction(uint256 _txId)
        public
        onlyOwner
        txExists(_txId)
        notExecuted(_txId)
    {
        Transaction storage transaction = transactions[_txId];
        
        require(
            transaction.confirmationCount >= requiredConfirmations,
            "SennaWallet: cannot execute tx"
        );

        transaction.executed = true;

        // Update daily spending
        _updateDailySpending(msg.sender, transaction.value);

        // Execute the transaction
        (bool success, ) = transaction.to.call{value: transaction.value}(transaction.data);
        require(success, "SennaWallet: transaction execution failed");

        emit TransactionExecuted(_txId, msg.sender);
    }

    /**
     * @dev AI Agent can execute small transactions directly
     * @param _to Target address
     * @param _value ETH value to send
     * @param _data Transaction data
     */
    function executeAITransaction(
        address _to,
        uint256 _value,
        bytes memory _data
    )
        external
        onlyAIAgent
        returns (bool)
    {
        require(_value <= 0.1 ether, "SennaWallet: AI transaction limit exceeded");
        require(_to != address(0), "SennaWallet: invalid recipient");

        (bool success, ) = _to.call{value: _value}(_data);
        return success;
    }

    // WALLET MANAGEMENT FUNCTIONS

    /**
     * @dev Update wallet settings
     * @param _dailyLimit New daily spending limit
     * @param _transactionLimit New per transaction limit
     * @param _recoveryAgent New recovery agent address
     */
    function updateSettings(
        uint256 _dailyLimit,
        uint256 _transactionLimit,
        address _recoveryAgent
    )
        external
        onlyOwner
    {
        settings.dailyLimit = _dailyLimit;
        settings.transactionLimit = _transactionLimit;
        settings.recoveryAgent = _recoveryAgent;

        emit WalletSettingsUpdated(msg.sender);
    }

    /**
     * @dev Add a new owner to the wallet
     * @param _newOwner Address of new owner
     */
    function addOwner(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "SennaWallet: invalid owner");
        require(!isOwner[_newOwner], "SennaWallet: already an owner");

        isOwner[_newOwner] = true;
        owners.push(_newOwner);
    }

    /**
     * @dev Remove an owner from the wallet
     * @param _owner Address of owner to remove
     */
    function removeOwner(address _owner) external onlyOwner {
        require(isOwner[_owner], "SennaWallet: not an owner");
        require(owners.length > 1, "SennaWallet: cannot remove last owner");

        isOwner[_owner] = false;
        
        // Remove from owners array
        for (uint256 i = 0; i < owners.length; i++) {
            if (owners[i] == _owner) {
                owners[i] = owners[owners.length - 1];
                owners.pop();
                break;
            }
        }

        // Adjust required confirmations if needed
        if (requiredConfirmations > owners.length) {
            requiredConfirmations = owners.length;
        }
    }

    // RECOVERY SYSTEM

    /**
     * @dev Initiate wallet recovery
     * @param _newOwner Proposed new owner address
     */
    function initiateRecovery(address _newOwner) external {
        require(
            msg.sender == settings.recoveryAgent || isOwner[msg.sender],
            "SennaWallet: not authorized"
        );
        require(_newOwner != address(0), "SennaWallet: invalid new owner");

        pendingRecoveryOwner = _newOwner;
        recoveryInitTime = block.timestamp;

        emit RecoveryInitiated(msg.sender, _newOwner);
    }

    /**
     * @dev Complete wallet recovery after delay
     */
    function completeRecovery() external {
        require(pendingRecoveryOwner != address(0), "SennaWallet: no pending recovery");
        require(
            block.timestamp >= recoveryInitTime + RECOVERY_DELAY,
            "SennaWallet: recovery delay not passed"
        );

        address newOwner = pendingRecoveryOwner;
        
        // Add new owner
        isOwner[newOwner] = true;
        owners.push(newOwner);

        // Reset recovery state
        pendingRecoveryOwner = address(0);
        recoveryInitTime = 0;

        emit RecoveryCompleted(msg.sender, newOwner);
    }

    /**
     * @dev Cancel pending recovery
     */
    function cancelRecovery() external onlyOwner {
        require(pendingRecoveryOwner != address(0), "SennaWallet: no pending recovery");
        
        pendingRecoveryOwner = address(0);
        recoveryInitTime = 0;
    }

    // VIEW FUNCTIONS

    /**
     * @dev Get transaction count
     * @return Number of transactions
     */
    function getTransactionCount() external view returns (uint256) {
        return transactions.length;
    }

    /**
     * @dev Get owners list
     * @return List of owner addresses
     */
    function getOwners() external view returns (address[] memory) {
        return owners;
    }

    /**
     * @dev Get transaction details
     * @param _txId Transaction ID
     * @return to Recipient address
     * @return value Transaction value
     * @return data Transaction data
     * @return executed Execution status
     * @return confirmationCount Number of confirmations
     */
    function getTransaction(uint256 _txId)
        external
        view
        returns (
            address to,
            uint256 value,
            bytes memory data,
            bool executed,
            uint256 confirmationCount
        )
    {
        Transaction storage transaction = transactions[_txId];
        return (
            transaction.to,
            transaction.value,
            transaction.data,
            transaction.executed,
            transaction.confirmationCount
        );
    }

    /**
     * @dev Get contract balance
     * @return Current contract balance
     */
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    // INTERNAL FUNCTIONS

    /**
     * @dev Check if transaction exceeds daily limit
     * @param _owner Owner address
     * @param _value Transaction value
     */
    function _checkDailyLimit(address _owner, uint256 _value) internal {
        // Reset daily spent if new day
        if (block.timestamp >= lastTransactionTime[_owner] + DAY) {
            dailySpent[_owner] = 0;
            lastTransactionTime[_owner] = block.timestamp;
        }

        require(
            dailySpent[_owner] + _value <= settings.dailyLimit,
            "SennaWallet: exceeds daily limit"
        );
    }

    /**
     * @dev Update daily spending tracker
     * @param _owner Owner address
     * @param _value Transaction value
     */
    function _updateDailySpending(address _owner, uint256 _value) internal {
        dailySpent[_owner] += _value;
        lastTransactionTime[_owner] = block.timestamp;
    }

    /**
     * @dev Emergency pause function
     */
    function emergencyPause() external onlyAIAgent {
        settings.isActive = false;
    }

    /**
     * @dev Resume wallet operations
     */
    function resume() external onlyAIAgent {
        settings.isActive = true;
    }
}