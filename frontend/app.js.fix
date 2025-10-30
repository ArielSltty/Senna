// frontend/app.js
// ⚡ JavaScript Frontend Logic for Senna Wallet

class SennaWallet {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentWallet = null;
        this.chatHistory = [];
        this.isConnected = false;
        
        // Initialize the application
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadWalletFromStorage();
        this.updateMarketData();
        this.setupAutoRefresh();
        
        console.log('🧠 Senna Wallet initialized');
    }

    bindEvents() {
        // Chat functionality
        document.getElementById('sendMessageBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatInput').addEventListener('keypress', (e) => this.handleChatInputKeypress(e));
        document.getElementById('clearChatBtn').addEventListener('click', () => this.clearChat());
        document.getElementById('helpBtn').addEventListener('click', () => this.showHelp());

        // Wallet management
        document.getElementById('connectWalletBtn').addEventListener('click', () => this.connectWallet());
        document.getElementById('createWalletBtn').addEventListener('click', () => this.createWallet());
        document.getElementById('exportWalletBtn').addEventListener('click', () => this.exportWallet());
        document.getElementById('viewOnExplorerBtn').addEventListener('click', () => this.viewOnExplorer());
        document.getElementById('gasPriceBtn').addEventListener('click', () => this.checkGasPrice());

        // Quick actions
        document.getElementById('quickBalance').addEventListener('click', () => this.quickAction('balance'));
        document.getElementById('quickSend').addEventListener('click', () => this.quickAction('send'));
        document.getElementById('quickPrice').addEventListener('click', () => this.quickAction('price'));
        document.getElementById('quickBuy').addEventListener('click', () => this.quickAction('buy'));

        // Modal management
        document.getElementById('closeWalletModal').addEventListener('click', () => this.hideModal('walletModal'));
        document.getElementById('closeTransactionModal').addEventListener('click', () => this.hideModal('transactionModal'));
        document.getElementById('copyWalletData').addEventListener('click', () => this.copyWalletData());
        document.getElementById('downloadWalletData').addEventListener('click', () => this.downloadWalletData());
        document.getElementById('cancelTransaction').addEventListener('click', () => this.hideModal('transactionModal'));
        document.getElementById('confirmTransaction').addEventListener('click', () => this.confirmTransaction());

        // Close modals on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
            }
        });

        // Auto-resize textarea
        this.setupAutoResize();
    }

    // Chat functionality
    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessageToChat('user', message);
        input.value = '';
        this.resizeTextarea();

        // Show loading state
        this.showLoading();

        try {
            const response = await this.apiCall('/api/chat', 'POST', {
                message: message,
                wallet_address: this.currentWallet?.address,
                session_id: this.getSessionId()
            });

            // Add AI response to chat
            this.addMessageToChat('ai', response.response, response);

            // Handle specific actions
            if (response.action === 'send_transaction' && response.transaction_data) {
                this.showTransactionModal(response.transaction_data);
            }

            // Update wallet info if balance was checked
            if (response.action === 'get_balance' && response.data) {
                this.updateWalletDisplay(response.data);
            }

        } catch (error) {
            this.addMessageToChat('ai', `Sorry, I encountered an error: ${error.message}`);
            this.showNotification('Error', error.message, 'error');
        } finally {
            this.hideLoading();
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
        
        // Format message with proper line breaks
        const formattedMessage = message.replace(/\n/g, '<br>');
        bubble.innerHTML = formattedMessage;

        // Add transaction data if available
        if (data && data.transaction_data) {
            const txData = document.createElement('div');
            txData.className = 'transaction-data';
            txData.innerHTML = `
                <div style="margin-top: 10px; padding: 10px; background: var(--bg-card); border-radius: 8px;">
                    <strong>Transaction Details:</strong><br>
                    Amount: ${data.transaction_data.amount} ${data.transaction_data.symbol}<br>
                    To: ${this.shortenAddress(data.transaction_data.to_address)}
                </div>
            `;
            bubble.appendChild(txData);
        }

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString();

        contentDiv.appendChild(bubble);
        contentDiv.appendChild(time);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Store in history
        this.chatHistory.push({ sender, message, timestamp: new Date() });
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        this.chatHistory = [];
        
        // Add welcome message back
        this.addMessageToChat('ai', `
            <h4>🤖 Welcome to Senna Wallet!</h4>
            <p>I'm your AI-powered wallet assistant for Somnia Blockchain. You can talk to me naturally to manage your crypto!</p>
            <div class="quick-examples">
                <p><strong>Try saying:</strong></p>
                <ul>
                    <li>"Show my balance"</li>
                    <li>"Send 10 STT to 0x..."</li>
                    <li>"What's the SOMI price today?"</li>
                    <li>"Create a new wallet for me"</li>
                    <li>"I want to buy 100k IDR worth of SOMI"</li>
                </ul>
            </div>
            <p>Just type what you want to do below! 👇</p>
        `);
    }

    showHelp() {
        this.addMessageToChat('ai', `
            <h4>🤖 Senna Wallet Help Guide</h4>
            <p>Here's what I can help you with:</p>
            <ul>
                <li><strong>Check Balance</strong>: "Show my balance", "How much do I have?"</li>
                <li><strong>Send Crypto</strong>: "Send 10 SOMI to 0x...", "Transfer 5 STT"</li>
                <li><strong>Create Wallet</strong>: "Create new wallet for me"</li>
                <li><strong>Check Price</strong>: "What's SOMI price today?", "Current STT value"</li>
                <li><strong>Buy Crypto</strong>: "I want to buy 100k IDR worth of SOMI"</li>
                <li><strong>Compare Exchanges</strong>: "Compare best places to buy SOMI"</li>
            </ul>
            <p>Just type what you want to do in natural language!</p>
        `);
    }

    // Wallet management
    async connectWallet() {
        if (this.currentWallet) {
            this.showNotification('Info', 'Wallet already connected', 'info');
            return;
        }

        const privateKey = prompt('Enter your private key:');
        if (!privateKey) return;

        try {
            // Validate private key and get address
            // In a real app, you'd use a proper library like ethers.js
            if (privateKey.length !== 64 && !privateKey.startsWith('0x')) {
                throw new Error('Invalid private key format');
            }

            // For demo purposes, we'll create a mock wallet
            // In production, use: const wallet = new ethers.Wallet(privateKey);
            const mockWallet = {
                address: '0x' + Array(40).fill(0).map(() => 
                    Math.floor(Math.random() * 16).toString(16)).join(''),
                privateKey: privateKey
            };

            this.currentWallet = mockWallet;
            this.saveWalletToStorage();
            await this.updateWalletInfo();
            this.showNotification('Success', 'Wallet connected successfully', 'success');

        } catch (error) {
            this.showNotification('Error', 'Failed to connect wallet: ' + error.message, 'error');
        }
    }

    async createWallet() {
        try {
            this.showLoading();
            const response = await this.apiCall('/api/wallet/create', 'POST');
            
            this.currentWallet = {
                address: response.address,
                privateKey: response.private_key,
                mnemonic: response.mnemonic
            };

            this.saveWalletToStorage();
            this.showWalletModal(response);
            this.showNotification('Success', 'New wallet created!', 'success');
            await this.updateWalletInfo();

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
        } catch (error) {
            console.error('Failed to update wallet info:', error);
        }
    }

    updateWalletDisplay(balanceData) {
        // Update header
        document.getElementById('walletAddress').textContent = this.shortenAddress(balanceData.address);
        document.getElementById('walletBalance').textContent = `${parseFloat(balanceData.balance).toFixed(4)} ${balanceData.symbol}`;

        // Update wallet panel
        document.getElementById('detailAddress').textContent = this.shortenAddress(balanceData.address);
        document.getElementById('detailBalance').textContent = `${parseFloat(balanceData.balance).toFixed(4)} ${balanceData.symbol}`;

        this.isConnected = true;
        document.getElementById('connectWalletBtn').textContent = 'Connected';
        document.getElementById('connectWalletBtn').disabled = true;
    }

    exportWallet() {
        if (!this.currentWallet) {
            this.showNotification('Error', 'No wallet to export', 'error');
            return;
        }
        this.showWalletModal(this.currentWallet);
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
            // This would call your backend gas price endpoint
            const gasPrice = 25; // Mock data in Gwei
            this.showNotification('Gas Price', `Current gas price: ${gasPrice} Gwei`, 'info');
        } catch (error) {
            this.showNotification('Error', 'Failed to get gas price', 'error');
        }
    }

    // Quick actions
    quickAction(action) {
        const actions = {
            balance: 'Show my balance',
            send: 'Send 10 STT to ',
            price: 'What is the current SOMI price?',
            buy: 'I want to buy 100000 IDR worth of SOMI'
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

    // Transaction handling
    showTransactionModal(transactionData) {
        const modal = document.getElementById('transactionModal');
        const details = document.getElementById('transactionDetails');
        
        details.innerHTML = `
            <div style="background: var(--bg-tertiary); padding: 15px; border-radius: 8px;">
                <h4>Transaction Details</h4>
                <div style="margin-top: 10px;">
                    <div><strong>From:</strong> ${this.shortenAddress(transactionData.from_address)}</div>
                    <div><strong>To:</strong> ${this.shortenAddress(transactionData.to_address)}</div>
                    <div><strong>Amount:</strong> ${transactionData.amount} ${transactionData.symbol}</div>
                    <div><strong>Network:</strong> Somnia Testnet</div>
                </div>
            </div>
        `;

        modal.classList.add('show');
    }

    async confirmTransaction() {
        const privateKeyInput = document.getElementById('privateKeyInput');
        const privateKey = privateKeyInput.value.trim();

        if (!privateKey) {
            this.showNotification('Error', 'Please enter your private key', 'error');
            return;
        }

        try {
            this.showLoading();
            // In a real implementation, you'd send the transaction through your backend
            // const response = await this.apiCall('/api/transaction/send', 'POST', {
            //     private_key: privateKey,
            //     // ... transaction data
            // });
            
            // Mock success for demo
            setTimeout(() => {
                this.hideLoading();
                this.hideModal('transactionModal');
                privateKeyInput.value = '';
                this.showNotification('Success', 'Transaction sent successfully!', 'success');
                this.updateWalletInfo(); // Refresh balance
            }, 2000);

        } catch (error) {
            this.hideLoading();
            this.showNotification('Error', 'Transaction failed: ' + error.message, 'error');
        }
    }

    // Modal management
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
        
        const data = `Address: ${address}\nPrivate Key: ${privateKey}\nMnemonic: ${mnemonic}`;
        
        navigator.clipboard.writeText(data).then(() => {
            this.showNotification('Success', 'Wallet data copied to clipboard', 'success');
        });
    }

    downloadWalletData() {
        const address = document.getElementById('newWalletAddress').textContent;
        const privateKey = document.getElementById('newWalletPrivateKey').textContent;
        const mnemonic = document.getElementById('newWalletMnemonic').textContent;
        
        const data = `Senna Wallet Backup\n\nAddress: ${address}\nPrivate Key: ${privateKey}\nMnemonic: ${mnemonic}\n\nGenerated on: ${new Date().toLocaleString()}\n\n⚠️ Keep this information secure! Do not share with anyone.`;
        
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `senna-wallet-backup-${address.slice(2, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Success', 'Wallet backup downloaded', 'success');
    }

    // Market data
    async updateMarketData() {
        try {
            // Mock market data - in production, you'd fetch from your backend
            const mockData = {
                somi: { price: '$0.25', change: '+2.5%' },
                stt: { price: '$0.15', change: '+1.2%' }
            };

            document.getElementById('somiPrice').textContent = mockData.somi.price;
            document.getElementById('sttPrice').textContent = mockData.stt.price;
            document.getElementById('priceChange').textContent = mockData.somi.change;
            document.getElementById('priceChange').className = 'market-value positive';

        } catch (error) {
            console.error('Failed to update market data:', error);
        }
    }

    // Utility functions
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
            throw new Error(error.detail || 'API request failed');
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
        if (!address) return '';
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
        // Refresh wallet balance every 30 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.updateWalletInfo();
            }
        }, 30000);

        // Refresh market data every minute
        setInterval(() => {
            this.updateMarketData();
        }, 60000);
    }
}

// Copy to clipboard utility
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
        const btn = e.target.classList.contains('copy-btn') ? e.target : e.target.closest('.copy-btn');
        const targetId = btn.getAttribute('data-target');
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            navigator.clipboard.writeText(targetElement.textContent).then(() => {
                // Show temporary success state
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i>';
                btn.style.background = 'var(--success-color)';
                
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.style.background = '';
                }, 2000);
            });
        }
    }
});

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sennaWallet = new SennaWallet();
});

// Export for global access (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SennaWallet;
}