// frontend/app.js
// ⚡ Enhanced JavaScript Frontend for Senna Wallet - ChatGPT Style

class SennaWallet {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentWallet = null;
        this.chatHistory = [];
        this.isConnected = false;
        this.currentSection = 'home';
        this.metaMaskProvider = null;
        
        // Initialize the application
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadWalletFromStorage();
        this.updateMarketData();
        this.setupAutoRefresh();
        this.checkMetaMask();
        this.showSection('home');
        this.setupMetaMaskListeners();
        
        console.log('🧠 Senna Wallet AI Assistant initialized');
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Chat functionality
        document.getElementById('sendMessageBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatInput').addEventListener('keypress', (e) => this.handleChatInputKeypress(e));
        document.getElementById('clearChatBtn').addEventListener('click', () => this.clearChat());
        document.getElementById('helpBtn').addEventListener('click', () => this.showHelp());
        document.getElementById('exportChatBtn').addEventListener('click', () => this.exportChat());

        // Quick actions in chat
        document.getElementById('quickActionsBtn').addEventListener('click', () => this.toggleQuickActions());
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.currentTarget.getAttribute('data-command');
                this.insertQuickCommand(command);
            });
        });

        // Wallet management
        document.getElementById('connectWalletBtn').addEventListener('click', () => this.connectMetaMask());
        document.getElementById('createWalletBtn').addEventListener('click', () => this.createWallet());
        document.getElementById('exportWalletBtn').addEventListener('click', () => this.exportWallet());
        document.getElementById('viewOnExplorerBtn').addEventListener('click', () => this.viewOnExplorer());
        document.getElementById('gasPriceBtn').addEventListener('click', () => this.checkGasPrice());

        // Dashboard actions
        document.getElementById('startChattingBtn').addEventListener('click', () => this.showSection('chat'));
        document.getElementById('learnMoreBtn').addEventListener('click', () => this.showSection('how-it-works'));
        document.getElementById('refreshBalanceBtn').addEventListener('click', () => this.updateWalletInfo());
        document.getElementById('viewAllTransactionsBtn').addEventListener('click', () => this.viewOnExplorer());

        // Dashboard quick actions
        document.getElementById('dashboardSendBtn').addEventListener('click', () => this.showSection('chat'));
        document.getElementById('dashboardReceiveBtn').addEventListener('click', () => this.showReceiveModal());
        document.getElementById('dashboardBuyBtn').addEventListener('click', () => this.quickAction('buy'));
        document.getElementById('dashboardSwapBtn').addEventListener('click', () => this.quickAction('swap'));

        // Modal management
        document.getElementById('closeWalletModal').addEventListener('click', () => this.hideModal('walletModal'));
        document.getElementById('closeTransactionModal').addEventListener('click', () => this.hideModal('transactionModal'));
        document.getElementById('copyWalletData').addEventListener('click', () => this.copyWalletData());
        document.getElementById('downloadWalletData').addEventListener('click', () => this.downloadWalletData());
        document.getElementById('cancelTransaction').addEventListener('click', () => this.hideModal('transactionModal'));
        document.getElementById('confirmTransaction').addEventListener('click', () => this.confirmTransaction());

        // Enhanced confirmation flows
        document.getElementById('confirmTransactionYes').addEventListener('click', () => this.handleConfirmation('yes'));
        document.getElementById('confirmTransactionNo').addEventListener('click', () => this.handleConfirmation('no'));
        document.getElementById('editTransaction').addEventListener('click', () => this.handleConfirmation('edit'));

        // Close modals on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
            }
        });

        // Auto-resize textarea
        this.setupAutoResize();

        // Close quick actions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.quick-actions-panel') && !e.target.closest('#quickActionsBtn')) {
                this.hideQuickActions();
            }
        });
    }

    // Section Navigation
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Activate corresponding nav link
        const targetLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (targetLink) {
            targetLink.classList.add('active');
        }

        this.currentSection = sectionName;

        // Special handling for chat section
        if (sectionName === 'chat') {
            setTimeout(() => {
                const chatMessages = document.getElementById('chatMessages');
                if (chatMessages) {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            }, 100);
        }
    }

    // Enhanced MetaMask Integration
    async checkMetaMask() {
        return new Promise((resolve) => {
            // Check if MetaMask is installed
            if (typeof window.ethereum !== 'undefined') {
                this.metaMaskProvider = window.ethereum;
                console.log('✅ MetaMask detected:', this.metaMaskProvider);
                
                // Check if already connected
                this.metaMaskProvider.request({ method: 'eth_accounts' })
                    .then(accounts => {
                        if (accounts.length > 0) {
                            console.log('✅ MetaMask already connected:', accounts[0]);
                            this.handleMetaMaskConnection(accounts[0]);
                        } else {
                            console.log('ℹ️ MetaMask installed but not connected');
                        }
                        resolve(true);
                    })
                    .catch(error => {
                        console.warn('MetaMask accounts request failed:', error);
                        resolve(false);
                    });
            } else {
                console.warn('❌ MetaMask not detected');
                this.metaMaskProvider = null;
                
                // Show user-friendly message
                this.showNotification(
                    'MetaMask Required', 
                    'Please install MetaMask to connect your wallet. Download from https://metamask.io/', 
                    'warning'
                );
                resolve(false);
            }
        });
    }

    setupMetaMaskListeners() {
        if (typeof window.ethereum !== 'undefined') {
            // Listen for account changes
            window.ethereum.on('accountsChanged', (accounts) => {
                console.log('🦊 MetaMask accounts changed:', accounts);
                if (accounts.length === 0) {
                    // User disconnected
                    this.handleMetaMaskDisconnect();
                } else {
                    this.handleMetaMaskConnection(accounts[0]);
                }
            });

            // Listen for chain changes
            window.ethereum.on('chainChanged', (chainId) => {
                console.log('🦊 MetaMask chain changed:', chainId);
                // Reload the page when chain changes
                window.location.reload();
            });
        }
    }

    handleMetaMaskDisconnect() {
        this.currentWallet = null;
        this.isConnected = false;
        
        // Update UI
        const connectBtn = document.getElementById('connectWalletBtn');
        if (connectBtn) {
            connectBtn.innerHTML = '<i class="fas fa-wallet"></i> Connect MetaMask';
            connectBtn.disabled = false;
        }
        
        this.showNotification('Disconnected', 'MetaMask wallet disconnected', 'info');
        this.updateDashboard();
    }

    async connectMetaMask() {
        try {
            this.showLoading();
            
            if (!this.metaMaskProvider) {
                const isAvailable = await this.checkMetaMask();
                if (!isAvailable) {
                    this.showNotification(
                        'MetaMask Not Found', 
                        'Please install MetaMask browser extension first.', 
                        'error'
                    );
                    this.hideLoading();
                    return;
                }
            }

            console.log('🦊 Connecting to MetaMask...');
            
            // Request account access
            const accounts = await this.metaMaskProvider.request({ 
                method: 'eth_requestAccounts' 
            });
            
            if (accounts.length > 0) {
                await this.handleMetaMaskConnection(accounts[0]);
                this.showNotification('Success', 'MetaMask connected successfully!', 'success');
            } else {
                throw new Error('No accounts returned from MetaMask');
            }
            
        } catch (error) {
            console.error('❌ MetaMask connection failed:', error);
            
            if (error.code === 4001) {
                // User rejected the connection request
                this.showNotification('Connection Rejected', 'Please approve the connection in MetaMask', 'warning');
            } else if (error.code === -32002) {
                // Request already pending
                this.showNotification('Request Pending', 'Please check MetaMask for pending connection', 'info');
            } else {
                this.showNotification('Connection Failed', error.message, 'error');
            }
        } finally {
            this.hideLoading();
        }
    }

    async handleMetaMaskConnection(address) {
        this.currentWallet = {
            address: address,
            isMetaMask: true
        };

        this.saveWalletToStorage();
        await this.updateWalletInfo();
        
        // Update UI
        document.getElementById('connectWalletBtn').innerHTML = '<i class="fas fa-wallet"></i> Connected';
        document.getElementById('connectWalletBtn').disabled = true;
        
        // Update dashboard
        this.updateDashboard();
    }

    // Enhanced Chat functionality
    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessageToChat('user', message);
        input.value = '';
        this.resizeTextarea();
        this.hideQuickActions();

        // Show loading state
        this.showLoading();

        try {
            const response = await this.apiCall('/api/chat', 'POST', {
                message: message,
                wallet_address: this.currentWallet?.address,
                session_id: this.getSessionId(),
                has_metamask: !!this.metaMaskProvider
            });

            // Handle AI response with enhanced features
            await this.handleAIResponse(response, message);

        } catch (error) {
            this.addMessageToChat('ai', `❌ Sorry, I encountered an error: ${error.message}`);
            this.showNotification('API Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async handleAIResponse(response, userMessage) {
        // Add AI response to chat
        this.addMessageToChat('ai', response.response, response);

        // Handle specific actions with enhanced logic
        switch (response.action) {
            case 'send_transaction':
                if (response.transaction_data) {
                    await this.showEnhancedTransactionModal(response.transaction_data);
                }
                break;
                
            case 'get_balance':
                if (response.data) {
                    this.updateWalletDisplay(response.data);
                    this.updateDashboard();
                }
                break;
                
            case 'check_price':
                if (response.market_data) {
                    this.updateMarketDisplay(response.market_data);
                }
                break;
                
            case 'create_wallet':
                if (response.wallet_data) {
                    this.handleWalletCreation(response.wallet_data);
                }
                break;
                
            case 'buy_crypto':
                if (response.payment_data) {
                    this.handleBuyCrypto(response.payment_data);
                }
                break;
        }

        // Update chat suggestions based on context
        this.updateChatSuggestions(response);
    }

    // NEW: Add missing method for chat suggestions
    updateChatSuggestions(response) {
        try {
            const suggestedActions = response.suggested_actions || [];
            
            if (suggestedActions.length > 0) {
                // Update quick actions panel based on context
                this.updateQuickActions(suggestedActions);
            }
            
            // Update input hints based on intent
            this.updateInputHints(response.action);
            
        } catch (error) {
            console.warn('Chat suggestions update failed:', error);
        }
    }

    updateQuickActions(suggestions) {
        const quickActionsPanel = document.getElementById('quickActionsPanel');
        if (!quickActionsPanel) return;
        
        const actionsGrid = quickActionsPanel.querySelector('.quick-actions-grid');
        if (!actionsGrid) return;
        
        // Clear existing custom actions
        const customActions = actionsGrid.querySelectorAll('.quick-action-btn:not([data-command])');
        customActions.forEach(action => action.remove());
        
        // Add new context-aware actions
        suggestions.forEach(suggestion => {
            const actionBtn = document.createElement('button');
            actionBtn.className = 'quick-action-btn';
            actionBtn.setAttribute('data-command', this.getSuggestionCommand(suggestion));
            actionBtn.innerHTML = this.getSuggestionIcon(suggestion) + ' ' + this.getSuggestionLabel(suggestion);
            actionBtn.addEventListener('click', () => this.insertQuickCommand(actionBtn.getAttribute('data-command')));
            
            actionsGrid.appendChild(actionBtn);
        });
    }

    getSuggestionCommand(suggestion) {
        const commands = {
            'check_balance': 'Show my balance',
            'send_transaction': 'Send 10 STT to',
            'get_price': 'What is the current SOMI price?',
            'buy_crypto': 'I want to buy 100000 IDR worth of SOMI',
            'gas_price': 'Show current gas prices',
            'create_wallet': 'Create a new wallet for me',
            'view_transactions': 'Show my transaction history',
            'market_analysis': 'Show SOMI market analysis',
            'help': 'Help me with available commands'
        };
        return commands[suggestion] || suggestion;
    }

    getSuggestionIcon(suggestion) {
        const icons = {
            'check_balance': '💰',
            'send_transaction': '🔄', 
            'get_price': '📈',
            'buy_crypto': '🛒',
            'gas_price': '⛽',
            'create_wallet': '🆕',
            'view_transactions': '📋',
            'market_analysis': '🔍',
            'help': '❓'
        };
        return icons[suggestion] || '💡';
    }

    getSuggestionLabel(suggestion) {
        const labels = {
            'check_balance': 'Check Balance',
            'send_transaction': 'Send Crypto',
            'get_price': 'Check Price', 
            'buy_crypto': 'Buy Crypto',
            'gas_price': 'Gas Price',
            'create_wallet': 'New Wallet',
            'view_transactions': 'Transactions',
            'market_analysis': 'Market Analysis',
            'help': 'Help'
        };
        return labels[suggestion] || suggestion;
    }

    updateInputHints(action) {
        const inputHints = document.querySelector('.input-hints');
        if (!inputHints) return;
        
        const hints = {
            'get_balance': 'Try: "balance", "show my STT", "how much do I have"',
            'send_transaction': 'Try: "send 10 STT to 0x...", "transfer 5 SOMI"',
            'get_price': 'Try: "SOMI price", "STT value", "market data"',
            'buy_crypto': 'Try: "buy 50k IDR of SOMI", "purchase crypto"',
            'help': 'Try: "commands", "what can you do", "features"'
        };
        
        const hintText = hints[action] || 'Try: "balance", "send STT", "SOMI price", "help"';
        
        if (inputHints) {
            const hintExamples = inputHints.querySelector('.hint-examples');
            if (hintExamples) {
                hintExamples.textContent = hintText;
            } else {
                inputHints.innerHTML = `<span>Press Enter to send • Shift+Enter for new line</span><span class="hint-examples">${hintText}</span>`;
            }
        }
    }

    handleChatInputKeypress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    addMessageToChat(sender, message, data = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // Enhanced message formatting with markdown-like support
        const formattedMessage = this.formatMessage(message);
        bubble.innerHTML = formattedMessage;

        // Add enhanced transaction data if available
        if (data && data.transaction_data) {
            bubble.appendChild(this.createTransactionDataElement(data.transaction_data));
        }

        // Add confirmation flow for transactions
        if (data && data.requires_confirmation) {
            bubble.appendChild(this.createConfirmationFlow(data));
        }

        // Add explorer links for successful transactions
        if (data && data.transaction_hash) {
            bubble.appendChild(this.createExplorerLinkElement(data.transaction_hash));
        }

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        contentDiv.appendChild(bubble);
        contentDiv.appendChild(time);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Store in history
        this.chatHistory.push({ 
            sender, 
            message, 
            data,
            timestamp: new Date().toISOString() 
        });
    }

    formatMessage(message) {
        // Simple markdown-like formatting
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/👉/g, '👉')
            .replace(/✅/g, '✅')
            .replace(/❌/g, '❌')
            .replace(/⚠️/g, '⚠️');
    }

    createTransactionDataElement(txData) {
        const txElement = document.createElement('div');
        txElement.className = 'transaction-data enhanced';
        txElement.innerHTML = `
            <div class="tx-summary">
                <strong>📋 Transaction Summary:</strong>
                <div class="tx-details">
                    <div>Amount: <span class="highlight">${txData.amount} ${txData.symbol}</span></div>
                    <div>To: <code>${this.shortenAddress(txData.to_address)}</code></div>
                    <div>Network: <span class="network-badge">Somnia Testnet</span></div>
                </div>
            </div>
        `;
        return txElement;
    }

    createConfirmationFlow(data) {
        const confirmationElement = document.createElement('div');
        confirmationElement.className = 'confirmation-flow';
        confirmationElement.innerHTML = `
            <div class="confirmation-prompt">
                <p><strong>🤖 Please confirm this action:</strong></p>
                <div class="confirmation-buttons">
                    <button class="btn btn-small btn-confirm" onclick="sennaWallet.handleConfirmation('yes', '${JSON.stringify(data).replace(/'/g, "\\'")}')">
                        ✅ Yes, proceed
                    </button>
                    <button class="btn btn-small btn-cancel" onclick="sennaWallet.handleConfirmation('no')">
                        ❌ Cancel
                    </button>
                    <button class="btn btn-small btn-edit" onclick="sennaWallet.handleConfirmation('edit')">
                        ✏️ Edit details
                    </button>
                </div>
            </div>
        `;
        return confirmationElement;
    }

    createExplorerLinkElement(txHash) {
        const explorerElement = document.createElement('div');
        explorerElement.className = 'explorer-link-container';
        explorerElement.innerHTML = `
            <div class="success-message">
                <p>✅ Transaction Successful!</p>
                <div class="explorer-actions">
                    <a href="https://shannon-explorer.somnia.network/tx/${txHash}" 
                       target="_blank" 
                       class="explorer-link-btn">
                        <i class="fas fa-external-link-alt"></i>
                        View on Explorer
                    </a>
                    <button class="btn btn-small btn-secondary" onclick="sennaWallet.copyToClipboard('${txHash}')">
                        <i class="fas fa-copy"></i>
                        Copy TX Hash
                    </button>
                </div>
            </div>
        `;
        return explorerElement;
    }

    async handleConfirmation(action, data = null) {
        switch (action) {
            case 'yes':
                if (data) {
                    const txData = JSON.parse(data);
                    await this.executeConfirmedTransaction(txData);
                }
                break;
            case 'no':
                this.addMessageToChat('ai', 'Transaction cancelled. Is there anything else I can help you with?');
                break;
            case 'edit':
                this.addMessageToChat('ai', 'Please provide the updated transaction details.');
                // Here you could implement an edit flow
                break;
        }
    }

    async executeConfirmedTransaction(txData) {
        try {
            this.showLoading();
            
            // Execute transaction via backend
            const response = await this.apiCall('/api/transaction/send', 'POST', {
                transaction_data: txData,
                wallet_address: this.currentWallet?.address
            });

            this.hideLoading();
            
            if (response.success) {
                this.addMessageToChat('ai', `
                    ✅ Transaction executed successfully!
                    \nTransaction Hash: ${response.transaction_hash}
                    \nYou can view it on the explorer below.
                `, {
                    transaction_hash: response.transaction_hash,
                    explorer_url: `https://shannon-explorer.somnia.network/tx/${response.transaction_hash}`
                });

                this.showNotification('Success', 'Transaction confirmed on blockchain!', 'success');
                await this.updateWalletInfo();
            }
        } catch (error) {
            this.hideLoading();
            this.addMessageToChat('ai', `❌ Transaction failed: ${error.message}`);
            this.showNotification('Transaction Failed', error.message, 'error');
        }
    }

    // Enhanced Quick Actions
    toggleQuickActions() {
        const panel = document.getElementById('quickActionsPanel');
        panel.classList.toggle('show');
    }

    hideQuickActions() {
        const panel = document.getElementById('quickActionsPanel');
        panel.classList.remove('show');
    }

    insertQuickCommand(command) {
        const input = document.getElementById('chatInput');
        input.value = command;
        input.focus();
        this.hideQuickActions();
        
        // Auto-send for simple commands
        if (!command.includes('to') && !command.includes('address')) {
            this.sendMessage();
        }
    }

    // Enhanced Wallet Management
    async createWallet() {
        try {
            this.showLoading();
            const response = await this.apiCall('/api/wallet/create', 'POST');
            
            this.currentWallet = {
                address: response.address,
                privateKey: response.private_key,
                mnemonic: response.mnemonic,
                isMetaMask: false
            };

            this.saveWalletToStorage();
            this.showWalletModal(response);
            this.showNotification('Success', 'New wallet created successfully!', 'success');
            await this.updateWalletInfo();
            this.updateDashboard();

        } catch (error) {
            this.showNotification('Error', 'Failed to create wallet: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async updateWalletInfo() {
        if (!this.currentWallet) return;

        try {
            const balance = await this.apiCall(`/api/balance/${this.currentWallet.address}`);
            this.updateWalletDisplay(balance);
            this.updateDashboard();
        } catch (error) {
            console.error('Failed to update wallet info:', error);
        }
    }

    updateWalletDisplay(balanceData) {
        if (!balanceData) return;

        // Update header
        const walletAddressElement = document.getElementById('walletAddress');
        const walletBalanceElement = document.getElementById('walletBalance');
        
        if (walletAddressElement) {
            walletAddressElement.textContent = this.shortenAddress(balanceData.address);
        }
        if (walletBalanceElement) {
            walletBalanceElement.textContent = `${parseFloat(balanceData.balance).toFixed(4)} ${balanceData.symbol}`;
        }

        this.isConnected = true;
        
        const connectBtn = document.getElementById('connectWalletBtn');
        if (connectBtn) {
            connectBtn.innerHTML = '<i class="fas fa-wallet"></i> Connected';
            connectBtn.disabled = true;
        }
    }

    // Enhanced Dashboard
    updateDashboard() {
        if (!this.currentWallet) return;

        // Update dashboard balance
        const dashboardBalance = document.getElementById('dashboardBalance');
        const dashboardAddress = document.getElementById('dashboardAddress');
        const connectionStatus = document.getElementById('connectionStatus');

        if (dashboardBalance && this.currentWallet.balance) {
            dashboardBalance.textContent = `${parseFloat(this.currentWallet.balance).toFixed(4)} STT`;
        }

        if (dashboardAddress) {
            dashboardAddress.textContent = this.shortenAddress(this.currentWallet.address);
        }

        if (connectionStatus) {
            connectionStatus.textContent = 'Connected';
            connectionStatus.className = 'info-value status-connected';
        }
    }

    // Enhanced Market Data
    async updateMarketData() {
        try {
            const marketData = await this.apiCall('/api/market/data');
            this.updateMarketDisplay(marketData);
        } catch (error) {
            // Fallback to mock data
            const mockData = {
                somi: { price: '$0.25', change: '+2.5%', market_cap: '$12.5M' },
                stt: { price: '$0.15', change: '+1.2%', market_cap: '$8.2M' }
            };
            this.updateMarketDisplay(mockData);
        }
    }

    updateMarketDisplay(marketData) {
        // Update chat section market data
        const elements = {
            'somiPrice': marketData.somi?.price,
            'sttPrice': marketData.stt?.price,
            'priceChange': marketData.somi?.change,
            'dashboardSomiPrice': marketData.somi?.price,
            'dashboardSttPrice': marketData.stt?.price,
            'dashboardPriceChange': marketData.somi?.change,
            'dashboardMarketCap': marketData.somi?.market_cap
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value) {
                element.textContent = value;
                
                // Add color coding for price changes
                if (id.includes('Change') || id.includes('change')) {
                    element.className = value.startsWith('+') ? 'market-value positive' : 'market-value negative';
                }
            }
        });
    }

    // Utility Functions
    async apiCall(endpoint, method = 'GET', data = null) {
        const url = this.apiBaseUrl + endpoint;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `API request failed: ${response.status}`);
        }

        return await response.json();
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    showLoading() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    shortenAddress(address, chars = 6) {
        if (!address) return 'Not connected';
        if (address.length <= chars * 2) return address;
        return `${address.slice(0, chars)}...${address.slice(-chars)}`;
    }

    getSessionId() {
        let sessionId = localStorage.getItem('senna_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('senna_session_id', sessionId);
        }
        return sessionId;
    }

    loadWalletFromStorage() {
        try {
            const walletData = localStorage.getItem('senna_wallet');
            if (walletData) {
                this.currentWallet = JSON.parse(walletData);
                this.updateWalletInfo();
                this.updateDashboard();
            }
        } catch (error) {
            console.error('Failed to load wallet from storage:', error);
        }
    }

    saveWalletToStorage() {
        if (this.currentWallet) {
            localStorage.setItem('senna_wallet', JSON.stringify(this.currentWallet));
        }
    }

    setupAutoResize() {
        const textarea = document.getElementById('chatInput');
        textarea.addEventListener('input', () => this.resizeTextarea());
    }

    resizeTextarea() {
        const textarea = document.getElementById('chatInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    setupAutoRefresh() {
        // Refresh wallet balance every 30 seconds if connected
        setInterval(() => {
            if (this.isConnected && this.currentWallet) {
                this.updateWalletInfo();
            }
        }, 30000);

        // Refresh market data every minute
        setInterval(() => {
            this.updateMarketData();
        }, 60000);
    }

    // Enhanced helper methods
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied!', 'Text copied to clipboard', 'success');
        });
    }

    exportChat() {
        const chatData = {
            timestamp: new Date().toISOString(),
            session_id: this.getSessionId(),
            messages: this.chatHistory
        };

        const dataStr = JSON.stringify(chatData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `senna-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Chat Exported', 'Chat history downloaded as JSON', 'success');
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        this.chatHistory = [];
        
        // Add enhanced welcome message
        this.addMessageToChat('ai', `
            <h4>🤖 Welcome to Senna Wallet AI Assistant!</h4>
            <p>I'm your intelligent crypto companion for the Somnia Blockchain. I understand natural language and can help you with:</p>
            <div class="quick-examples">
                <ul>
                    <li><strong>Wallet Management</strong>: "Create wallet", "Show balance"</li>
                    <li><strong>Transactions</strong>: "Send 10 STT to 0x...", "Transfer SOMI"</li>
                    <li><strong>Market Data</strong>: "SOMI price", "Market analysis"</li>
                    <li><strong>Trading</strong>: "Buy 100k IDR of SOMI", "Compare exchanges"</li>
                    <li><strong>Blockchain Info</strong>: "Gas prices", "Network status"</li>
                </ul>
            </div>
            <p>Try asking me anything in plain English! 👇</p>
        `);
    }

    showHelp() {
        this.addMessageToChat('ai', `
            <h4>🆘 Senna Wallet Help Center</h4>
            <div class="help-sections">
                <div class="help-section">
                    <h5>💼 Wallet Commands</h5>
                    <ul>
                        <li><code>"Create new wallet"</code> - Generate a new Somnia wallet</li>
                        <li><code>"Show my balance"</code> - Check STT/SOMI balance</li>
                        <li><code>"Connect MetaMask"</code> - Link your MetaMask wallet</li>
                    </ul>
                </div>
                <div class="help-section">
                    <h5>🔄 Transaction Commands</h5>
                    <ul>
                        <li><code>"Send 5 STT to 0xabc..."</code> - Transfer tokens</li>
                        <li><code>"Transfer 10 SOMI"</code> - With recipient confirmation</li>
                        <li><code>"Transaction history"</code> - View recent transactions</li>
                    </ul>
                </div>
                <div class="help-section">
                    <h5>📈 Market Commands</h5>
                    <ul>
                        <li><code>"SOMI price"</code> - Current market price</li>
                        <li><code>"Market analysis"</code> - Detailed market insights</li>
                        <li><code>"Compare exchanges"</code> - Best trading platforms</li>
                    </ul>
                </div>
                <div class="help-section">
                    <h5>🛒 Trading Commands</h5>
                    <ul>
                        <li><code>"Buy 50k IDR of SOMI"</code> - Fiat to crypto purchase</li>
                        <li><code>"Sell 100 SOMI"</code> - Crypto to fiat exchange</li>
                        <li><code>"Best price SOMI"</code> - Price optimization</li>
                    </ul>
                </div>
            </div>
            <p><strong>Pro Tip:</strong> Use the quick action buttons for faster access to common commands!</p>
        `);
    }

    // Keep existing modal methods (showWalletModal, hideModal, etc.)
    showWalletModal(walletData) {
        const modal = document.getElementById('walletModal');
        document.getElementById('newWalletAddress').textContent = walletData.address;
        document.getElementById('newWalletPrivateKey').textContent = walletData.privateKey;
        document.getElementById('newWalletMnemonic').textContent = walletData.mnemonic || 'N/A';
        modal.classList.add('show');
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
    }

    copyWalletData() {
        const address = document.getElementById('newWalletAddress').textContent;
        const privateKey = document.getElementById('newWalletPrivateKey').textContent;
        const mnemonic = document.getElementById('newWalletMnemonic').textContent;
        
        const data = `Senna Wallet Backup\n\nADDRESS: ${address}\nPRIVATE KEY: ${privateKey}\nMNEMONIC: ${mnemonic}\n\n⚠️ IMPORTANT: Store this information securely! Never share your private key or mnemonic.\n\nGenerated: ${new Date().toLocaleString()}`;
        
        navigator.clipboard.writeText(data).then(() => {
            this.showNotification('Copied!', 'Wallet data copied to clipboard', 'success');
        });
    }

    downloadWalletData() {
        const address = document.getElementById('newWalletAddress').textContent;
        const privateKey = document.getElementById('newWalletPrivateKey').textContent;
        const mnemonic = document.getElementById('newWalletMnemonic').textContent;
        
        const data = `Senna Wallet Backup\n\nADDRESS: ${address}\nPRIVATE KEY: ${privateKey}\nMNEMONIC: ${mnemonic}\n\n⚠️ IMPORTANT SECURITY NOTICE:\n- Store this file in a secure location\n- Never share your private key or mnemonic with anyone\n- We cannot recover your funds if you lose this information\n- Consider using a hardware wallet for large amounts\n\nGenerated: ${new Date().toLocaleString()}\nWallet: Senna Wallet AI Assistant`;
        
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `senna-wallet-backup-${address.slice(2, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Backup Downloaded', 'Wallet backup saved securely', 'success');
    }

    // Quick actions (keep existing)
    quickAction(action) {
        const actions = {
            balance: 'Show my current balance',
            send: 'Send 10 STT to ',
            price: 'What is the current SOMI price and market analysis?',
            buy: 'I want to buy 100000 IDR worth of SOMI',
            swap: 'Swap 50 STT for SOMI'
        };

        const input = document.getElementById('chatInput');
        input.value = actions[action];
        
        if (action === 'send') {
            input.value += '0x...';
            input.focus();
            input.setSelectionRange(input.value.length - 4, input.value.length - 1);
        } else {
            this.sendMessage();
        }
    }

    viewOnExplorer() {
        if (!this.currentWallet) {
            this.showNotification('Error', 'No wallet connected', 'error');
            return;
        }
        const explorerUrl = `https://shannon-explorer.somnia.network/address/${this.currentWallet.address}`;
        window.open(explorerUrl, '_blank');
    }

    async checkGasPrice() {
        try {
            const gasData = await this.apiCall('/api/gas/price');
            this.showNotification('Gas Prices', 
                `Current: ${gasData.current} Gwei\nFast: ${gasData.fast} Gwei\nSlow: ${gasData.slow} Gwei`, 
                'info');
        } catch (error) {
            this.showNotification('Gas Price', 'Current gas price: 25 Gwei (estimated)', 'info');
        }
    }

    showReceiveModal() {
        if (!this.currentWallet) {
            this.showNotification('Error', 'Please connect a wallet first', 'error');
            return;
        }

        this.showNotification('Receive Funds', 
            `Share this address to receive funds:\n${this.currentWallet.address}\n\nClick to copy address.`, 
            'info');
        
        this.copyToClipboard(this.currentWallet.address);
    }

    async showEnhancedTransactionModal(transactionData) {
        const modal = document.getElementById('transactionModal');
        const details = document.getElementById('transactionDetails');
        
        // Enhanced transaction details with explorer preview
        details.innerHTML = `
            <div class="transaction-preview">
                <h4>🔄 Transaction Preview</h4>
                <div class="tx-details-grid">
                    <div class="tx-detail">
                        <span class="tx-label">From:</span>
                        <span class="tx-value">${this.shortenAddress(transactionData.from_address)}</span>
                    </div>
                    <div class="tx-detail">
                        <span class="tx-label">To:</span>
                        <span class="tx-value">${this.shortenAddress(transactionData.to_address)}</span>
                    </div>
                    <div class="tx-detail">
                        <span class="tx-label">Amount:</span>
                        <span class="tx-value highlight">${transactionData.amount} ${transactionData.symbol}</span>
                    </div>
                    <div class="tx-detail">
                        <span class="tx-label">Network:</span>
                        <span class="tx-value">Somnia Testnet</span>
                    </div>
                    <div class="tx-detail">
                        <span class="tx-label">Estimated Gas:</span>
                        <span class="tx-value">${transactionData.estimated_gas || '21000'} Gwei</span>
                    </div>
                </div>
                <div class="explorer-preview">
                    <i class="fas fa-external-link-alt"></i>
                    <small>You can verify this transaction on <a href="https://shannon-explorer.somnia.network/" target="_blank">Shannon Explorer</a></small>
                </div>
            </div>
        `;

        modal.classList.add('show');
    }

    handleWalletCreation(walletData) {
        this.currentWallet = {
            address: walletData.address,
            privateKey: walletData.private_key,
            mnemonic: walletData.mnemonic,
            isMetaMask: false
        };
        this.saveWalletToStorage();
        this.showWalletModal(walletData);
    }

    handleBuyCrypto(paymentData) {
        // Handle crypto purchase flow
        this.addMessageToChat('ai', `
            🛒 **Crypto Purchase Ready**
            
            I can help you buy ${paymentData.amount} ${paymentData.symbol}!
            
            **Next Steps:**
            1. Confirm the amount and payment method
            2. Complete the secure payment process
            3. Receive your crypto in your wallet
            
            Would you like to proceed with the purchase?
        `);
    }
}

// Enhanced copy to clipboard utility with better feedback
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
        const btn = e.target.classList.contains('copy-btn') ? e.target : e.target.closest('.copy-btn');
        const targetId = btn.getAttribute('data-target');
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            navigator.clipboard.writeText(targetElement.textContent).then(() => {
                // Enhanced success state
                const originalHTML = btn.innerHTML;
                const originalBg = btn.style.background;
                btn.innerHTML = '<i class="fas fa-check"></i>';
                btn.style.background = 'var(--success-color)';
                btn.style.color = 'white';
                
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.style.background = originalBg;
                    btn.style.color = '';
                }, 2000);
            });
        }
    }
});

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sennaWallet = new SennaWallet();
});

// Export for global access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SennaWallet;
}