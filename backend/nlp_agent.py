# backend/nlp_agent.py
import os
import json
import logging
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
from datetime import datetime
from decimal import Decimal, ROUND_DOWN

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedNLPAgent:
    """
    Advanced AI Agent for processing natural language commands with enhanced features:
    - Multi-AI provider support with fallback
    - Smart confirmation flows
    - Enhanced parameter extraction
    - Explorer integration
    - Market analysis capabilities
    """
    
    def __init__(self, wallet_core):
        self.wallet_core = wallet_core
        self.session = None
        
        # Enhanced AI Provider Configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "groq").lower()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_base_url = "https://api.groq.com/openai/v1"
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = "https://api.openai.com/v1"
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Enhanced intent patterns with better matching
        self.intent_patterns = {
            "get_balance": [
                "saldo", "balance", "cek saldo", "berapa saldo", "lihat saldo", 
                "my balance", "check balance", "show balance", "what's my balance",
                "how much do i have", "wallet balance"
            ],
            "send_transaction": [
                "kirim", "send", "transfer", "berikan", "kasih", "to 0x", "to ",
                "send to", "transfer to", "pay", "make payment", "forward"
            ],
            "receive": [
                "terima", "receive", "dapat", "minta", "get", "receive funds",
                "my address", "where to send", "deposit"
            ],
            "create_wallet": [
                "buat wallet", "buat dompet", "wallet baru", "dompet baru", 
                "create wallet", "new wallet", "generate wallet", "make wallet"
            ],
            "get_price": [
                "harga", "price", "nilai", "berapa harga", "kurs", "current price", 
                "what's the price", "price of", "how much is", "market price",
                "value of", "crypto price"
            ],
            "buy_crypto": [
                "beli", "buy", "pembelian", "purchase", "i want to buy", 
                "get some", "acquire", "buy some", "purchase crypto"
            ],
            "compare_exchanges": [
                "bandingkan", "compare", "mana yang", "terbaik", "best place",
                "where to buy", "best exchange", "compare prices", "price comparison"
            ],
            "help": [
                "bantuan", "help", "tolong", "cara pakai", "what can you do", 
                "how to use", "commands", "features", "help me"
            ],
            "gas_price": [
                "gas", "gas price", "fee", "transaction fee", "network fee",
                "how much gas", "gas cost", "ethereum gas"
            ],
            "transaction_history": [
                "history", "riwayat", "transaksi", "transaction history",
                "my transactions", "recent transactions", "past transactions"
            ],
            "market_analysis": [
                "analysis", "analisis", "market", "trend", "prediction",
                "market analysis", "price prediction", "market trend"
            ]
        }
        
        # Enhanced response templates with confirmation flows
        self.response_templates = {
            "balance": "💰 **Your Wallet Balance**\n\n**Address:** `{address}`\n**Balance:** `{balance} {symbol}`\n**Network:** Somnia Testnet",
            
            "send_confirmation": """
🔔 **Transaction Confirmation Required**

I'm about to send:
- **Amount:** `{amount} {symbol}`
- **To:** `{to_address}`
- **From:** `{from_address}`
- **Network:** Somnia Testnet

**Are you sure you want to proceed?** Please confirm this transaction.
""",
            
            "send_success": """
✅ **Transaction Successful!**

**Details:**
- Amount: `{amount} {symbol}`
- To: `{to_address}`
- Transaction Hash: `{tx_hash}`
- Explorer: [View on Shannon Explorer]({explorer_url})

Your new balance will be updated shortly.
""",
            
            "send_failed": "❌ **Transaction Failed**\n\nError: `{error}`\n\nPlease check the details and try again.",
            
            "wallet_created": """
🎉 **New Wallet Created Successfully!**

**Wallet Details:**
- Address: `{address}`
- Private Key: `{private_key}`
- Mnemonic: `{mnemonic}`

⚠️ **Important Security Notice:**
- Save your private key and mnemonic securely
- We cannot recover your wallet if you lose these
- Never share your private key with anyone
""",
            
            "price_info": """
📊 **Market Data - {symbol}**

**Current Price:**
- USD: `${usd_price}`
- IDR: `₨{idr_price}`
- 24h Change: `{change_24h}`

**Market Stats:**
- Market Cap: `${market_cap}`
- 24h Volume: `${volume_24h}`
- All-Time High: `${ath}`
""",
            
            "help": """
🤖 **Senna Wallet AI Assistant - Help Guide**

**💼 Wallet Management**
• "Show my balance" - Check your STT/SOMI balance
• "Create new wallet" - Generate a new Somnia wallet
• "My wallet address" - View your receiving address

**🔄 Transactions**
• "Send 10 STT to 0x..." - Transfer tokens (with confirmation)
• "Transaction history" - View recent transactions
• "Gas price" - Check current network fees

**📈 Market & Trading**
• "SOMI price" - Current market price
• "Buy 100k IDR of SOMI" - Fiat to crypto purchase
• "Compare exchanges" - Best trading platforms
• "Market analysis" - Detailed market insights

**🔧 Tools & Info**
• "Help" - Show this guide
• "Network status" - Blockchain information
• "Explorer links" - Transaction verification

**💡 Pro Tips:**
- Use natural language - no technical commands needed
- Always confirm transaction details before sending
- Verify transactions on the explorer
- Keep your private keys secure!
"""
        }
        
        # Enhanced parameter extraction patterns
        self.parameter_patterns = {
            "amount": [
                r'(\d+\.?\d*)\s*(SOMI|STT|ETH|BTC|USD|IDR|RP|\\$|₨)',
                r'(\d+\.?\d*)\s*(token|coin|crypto)',
                r'send\s+(\d+\.?\d*)',
                r'transfer\s+(\d+\.?\d*)'
            ],
            "address": [
                r'0x[a-fA-F0-9]{40}',
                r'[a-zA-Z0-9]{34}',  # For other blockchain addresses
                r'to\s+(\S+)'
            ],
            "currency": [
                r'\$(\\d+\\.?\\d*)',
                r'₨(\\d+\\.?\\d*)',
                r'(\\d+\\.?\\d*)\s*(USD|IDR|RP)',
                r'(\\d+\\.?\\d*)\s*(dollar|rupiah)'
            ]
        }
        
        logger.info(f"🧠 Enhanced NLP Agent initialized with provider: {self.ai_provider}")
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ Enhanced NLP Agent session initialized")
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def process_message(self, message: str, wallet_address: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Enhanced message processing with advanced features
        """
        try:
            logger.info(f"🧠 Processing message: {message}")
            
            # Enhanced context building
            context = await self._build_context(wallet_address, session_id)
            
            # Try AI provider first
            ai_response = await self._call_ai_api(message, wallet_address, context)
            
            if ai_response and ai_response.get("success", True):
                response = await self._execute_enhanced_action(ai_response, wallet_address, context)
            else:
                # Enhanced fallback processing
                response = await self._enhanced_fallback_processing(message, wallet_address, context)
            
            # Add session and context data
            response.update({
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "requires_confirmation": response.get("requires_confirmation", False),
                "explorer_links": response.get("explorer_links", [])
            })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Enhanced NLP processing error: {str(e)}")
            return self._create_error_response(str(e))
    
    async def _build_context(self, wallet_address: str = None, session_id: str = None) -> Dict[str, Any]:
        """Build enhanced context for AI processing"""
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "network": "Somnia Testnet",
            "chain_id": 50312,
            "explorer_url": "https://shannon-explorer.somnia.network/"
        }
        
        if wallet_address:
            context["wallet_address"] = wallet_address
            try:
                # Get current balance for context
                balance_wei = self.wallet_core.get_balance(wallet_address)
                balance_ether = self.wallet_core.wei_to_ether(balance_wei)
                context["current_balance"] = f"{balance_ether} STT"
            except Exception as e:
                logger.warning(f"Could not fetch balance for context: {e}")
        
        # Add market context
        try:
            market_data = await self.wallet_core.get_market_data()
            context["market_data"] = market_data
        except Exception as e:
            logger.warning(f"Could not fetch market data for context: {e}")
        
        return context
    
    async def _call_ai_api(self, message: str, wallet_address: str = None, context: Dict = None) -> Optional[Dict[str, Any]]:
        """Enhanced AI API calls with better error handling and context"""
        try:
            if self.ai_provider == "groq" and self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
                return await self._call_enhanced_groq_api(message, wallet_address, context)
            elif self.ai_provider == "deepseek" and self.deepseek_api_key and self.deepseek_api_key != "your_deepseek_api_key_here":
                return await self._call_enhanced_deepseek_api(message, wallet_address, context)
            elif self.ai_provider == "openai" and self.openai_api_key and self.openai_api_key != "your_openai_api_key_here":
                return await self._call_enhanced_openai_api(message, wallet_address, context)
            else:
                logger.warning("No valid AI provider configured, using enhanced fallback")
                return None
        except Exception as e:
            logger.error(f"Enhanced AI API call failed: {str(e)}")
            return None
    
    async def _call_enhanced_groq_api(self, message: str, wallet_address: str = None, context: Dict = None) -> Optional[Dict[str, Any]]:
        """Enhanced Groq API call with better context and response handling"""
        if not self.session:
            await self.initialize()
        
        try:
            prompt = self._build_enhanced_ai_prompt(message, wallet_address, context)
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.groq_model,
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_enhanced_system_prompt(context)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 800,
                "top_p": 0.9,
                "response_format": {"type": "json_object"}
            }
            
            async with self.session.post(
                f"{self.groq_base_url}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_content = data["choices"][0]["message"]["content"]
                    
                    return self._parse_enhanced_ai_response(ai_content, message, context)
                else:
                    error_text = await response.text()
                    logger.error(f"Groq API error: {response.status} - {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Groq API timeout")
            return None
        except Exception as e:
            logger.error(f"Enhanced Groq API call failed: {str(e)}")
            return None
    
    def _get_enhanced_system_prompt(self, context: Dict = None) -> str:
        """Get enhanced system prompt for AI"""
        base_prompt = """You are Senna, an advanced AI wallet assistant for Somnia blockchain. 
        Parse user messages and return structured JSON with intent, parameters, and enhanced features.

        Available enhanced actions:
        - get_balance: Get wallet balance with enhanced display
        - send_transaction: Send crypto with confirmation flow
        - create_wallet: Create new wallet with security warnings
        - get_price: Get token price with market analysis
        - convert_currency: Convert between fiat and crypto
        - buy_crypto: Initiate crypto purchase
        - compare_exchanges: Compare exchange prices with recommendations
        - gas_price: Get current network gas prices
        - transaction_history: Get transaction history
        - market_analysis: Provide market insights
        - help: Show enhanced help guide

        Enhanced Response Format:
        {
            "intent": "action_name",
            "parameters": {"key": "value"},
            "confidence": 0.9,
            "response_message": "Enhanced friendly response with formatting",
            "requires_confirmation": false,
            "explorer_links": [],
            "suggested_actions": [],
            "market_insights": {}
        }

        Special Features:
        - Always include explorer links for transactions
        - Add confirmation flows for sensitive actions
        - Provide market insights when relevant
        - Suggest next actions for better UX
        """
        
        if context:
            base_prompt += f"\n\nCurrent Context:\nNetwork: {context.get('network')}\n"
            if context.get('wallet_address'):
                base_prompt += f"Wallet: {context.get('wallet_address')}\n"
            if context.get('current_balance'):
                base_prompt += f"Balance: {context.get('current_balance')}\n"
        
        return base_prompt
    
    def _build_enhanced_ai_prompt(self, message: str, wallet_address: str = None, context: Dict = None) -> str:
        """Build enhanced prompt for AI understanding"""
        prompt = f"User message: \"{message}\"\n\n"
        
        if context:
            prompt += "Context Information:\n"
            for key, value in context.items():
                if key != 'market_data':  # Don't include full market data in prompt
                    prompt += f"- {key}: {value}\n"
        
        prompt += """
        Analyze this message and extract:
        - Primary intent and action required
        - All relevant parameters (amounts, addresses, symbols, currencies)
        - Whether confirmation is needed
        - Relevant explorer links
        - Market insights if applicable
        - Suggested next actions

        Return only valid JSON.
        """
        
        return prompt
    
    def _parse_enhanced_ai_response(self, ai_content: str, original_message: str, context: Dict = None) -> Dict[str, Any]:
        """Parse enhanced AI response with better error handling"""
        try:
            response_data = json.loads(ai_content)
            
            # Validate required fields
            if not response_data.get("intent"):
                response_data["intent"] = "help"
            
            if not response_data.get("response_message"):
                response_data["response_message"] = "I understand your request. Let me help you with that."
            
            # Ensure confidence score
            if "confidence" not in response_data:
                response_data["confidence"] = 0.8
            
            return response_data
            
        except json.JSONDecodeError:
            logger.warning("AI response was not valid JSON, using enhanced pattern matching")
            return self._enhanced_intent_extraction(original_message, context)
    
    def _enhanced_intent_extraction(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Enhanced intent extraction with better parameter parsing"""
        message_lower = message.lower()
        
        # Enhanced balance check
        if any(word in message_lower for word in self.intent_patterns["get_balance"]):
            return {
                "intent": "get_balance",
                "parameters": {},
                "confidence": 0.85,
                "response_message": "I'll check your current balance and provide detailed wallet information.",
                "requires_confirmation": False
            }
        
        # Enhanced price check with market context
        elif any(word in message_lower for word in self.intent_patterns["get_price"]):
            symbol = self._extract_symbol(message)
            return {
                "intent": "get_price",
                "parameters": {"symbol": symbol},
                "confidence": 0.8,
                "response_message": f"I'll fetch the current {symbol} price with comprehensive market data.",
                "requires_confirmation": False,
                "market_insights": {"requested_symbol": symbol}
            }
        
        # Enhanced send transaction with confirmation
        elif any(word in message_lower for word in self.intent_patterns["send_transaction"]):
            params = self._enhanced_extract_send_parameters(message)
            return {
                "intent": "send_transaction",
                "parameters": params,
                "confidence": 0.7 if params else 0.4,
                "response_message": self._create_send_confirmation_message(params),
                "requires_confirmation": True if params else False,
                "explorer_links": [f"https://shannon-explorer.somnia.network/address/{params.get('to_address', '')}"] if params.get('to_address') else []
            }
        
        # Enhanced help with context
        elif any(word in message_lower for word in self.intent_patterns["help"]):
            return {
                "intent": "help",
                "parameters": {},
                "confidence": 0.9,
                "response_message": "I'll provide you with a comprehensive help guide and available features.",
                "requires_confirmation": False
            }
        
        # Gas price check
        elif any(word in message_lower for word in self.intent_patterns["gas_price"]):
            return {
                "intent": "gas_price",
                "parameters": {},
                "confidence": 0.8,
                "response_message": "I'll check the current network gas prices for you.",
                "requires_confirmation": False
            }
        
        # Default to enhanced help
        else:
            return {
                "intent": "help",
                "parameters": {},
                "confidence": 0.5,
                "response_message": "I'm not quite sure what you'd like to do. Here's what I can help you with:",
                "requires_confirmation": False,
                "suggested_actions": ["check_balance", "get_price", "send_transaction", "view_help"]
            }
    
    def _enhanced_extract_send_parameters(self, message: str) -> Dict[str, Any]:
        """Enhanced parameter extraction for send transactions"""
        params = {}
        
        # Extract amount and symbol with better patterns
        amount_patterns = [
            r'(\d+\.?\d*)\s*(SOMI|STT|ETH|BTC)',
            r'send\s+(\d+\.?\d*)\s*(SOMI|STT|ETH|BTC)',
            r'transfer\s+(\d+\.?\d*)\s*(SOMI|STT|ETH|BTC)',
            r'(\d+\.?\d*)\s*(SOMI|STT|ETH|BTC)\s+to'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                params["amount"] = float(match.group(1))
                params["symbol"] = match.group(2).upper()
                break
        
        # Extract address with better validation
        address_pattern = r'0x[a-fA-F0-9]{40}'
        address_match = re.search(address_pattern, message)
        if address_match:
            params["to_address"] = address_match.group(0)
        
        # Extract additional context
        if "all" in message.lower() or "everything" in message.lower():
            params["send_all"] = True
        
        return params
    
    def _create_send_confirmation_message(self, params: Dict) -> str:
        """Create enhanced confirmation message for send transactions"""
        if not params or not params.get('amount') or not params.get('to_address'):
            return "I'd like to help you send a transaction. Please specify the amount, cryptocurrency, and recipient address. Example: 'Send 10 STT to 0x1a2b3c4d...'"
        
        return self.response_templates["send_confirmation"].format(
            amount=params['amount'],
            symbol=params.get('symbol', 'STT'),
            to_address=params['to_address'],
            from_address="[Your Wallet]"
        )
    
    def _extract_symbol(self, message: str) -> str:
        """Extract cryptocurrency symbol from message"""
        message_upper = message.upper()
        
        if 'SOMI' in message_upper:
            return 'SOMI'
        elif 'STT' in message_upper:
            return 'STT'
        elif 'ETH' in message_upper or 'ETHER' in message_upper.upper():
            return 'ETH'
        elif 'BTC' in message_upper or 'BITCOIN' in message_upper.upper():
            return 'BTC'
        else:
            return 'SOMI'  # Default to SOMI
    
    async def _execute_enhanced_action(self, ai_data: Dict[str, Any], wallet_address: str = None, context: Dict = None) -> Dict[str, Any]:
        """Execute enhanced action with confirmation flows and explorer integration"""
        intent = ai_data.get("intent")
        parameters = ai_data.get("parameters", {})
        
        logger.info(f"🎯 Executing enhanced intent: {intent} with params: {parameters}")
        
        try:
            if intent == "get_balance":
                return await self._handle_enhanced_get_balance(wallet_address, context)
            
            elif intent == "send_transaction":
                return await self._handle_enhanced_send_transaction(parameters, wallet_address, context)
            
            elif intent == "create_wallet":
                return await self._handle_enhanced_create_wallet(context)
            
            elif intent == "get_price":
                return await self._handle_enhanced_get_price(parameters, context)
            
            elif intent == "gas_price":
                return await self._handle_enhanced_gas_price(context)
            
            elif intent == "help":
                return self._handle_enhanced_help(context)
            
            else:
                return self._handle_enhanced_help(context)
                
        except Exception as e:
            logger.error(f"❌ Enhanced action execution error: {str(e)}")
            return self._create_error_response(str(e))
    
    async def _handle_enhanced_get_balance(self, wallet_address: str, context: Dict = None) -> Dict[str, Any]:
        """Enhanced balance check with explorer integration"""
        if not wallet_address:
            return {
                "response": "Please connect your wallet or create a new one to check your balance.",
                "success": False,
                "action": "get_balance",
                "suggested_actions": ["create_wallet", "connect_wallet"]
            }
        
        try:
            balance_wei = self.wallet_core.get_balance(wallet_address)
            balance_ether = self.wallet_core.wei_to_ether(balance_wei)
            
            explorer_url = f"https://shannon-explorer.somnia.network/address/{wallet_address}"
            
            return {
                "response": self.response_templates["balance"].format(
                    address=wallet_address,
                    balance=balance_ether,
                    symbol="STT"
                ),
                "success": True,
                "action": "get_balance",
                "data": {
                    "balance": balance_ether,
                    "balance_wei": balance_wei,
                    "symbol": "STT",
                    "address": wallet_address
                },
                "explorer_links": [explorer_url],
                "suggested_actions": ["send_transaction", "check_price", "view_transactions"]
            }
        except Exception as e:
            return self._create_error_response(f"Error checking balance: {str(e)}")
    
    async def _handle_enhanced_send_transaction(self, parameters: Dict, wallet_address: str, context: Dict = None) -> Dict[str, Any]:
        """Enhanced send transaction with confirmation flow"""
        amount = parameters.get("amount")
        to_address = parameters.get("to_address")
        symbol = parameters.get("symbol", "STT")
        
        if not amount or not to_address:
            return {
                "response": "To send a transaction, I need both the amount and recipient address. Please provide details like: 'Send 10 STT to 0x1a2b3c4d...'",
                "success": False,
                "action": "send_transaction",
                "requires_confirmation": False
            }
        
        # Create enhanced transaction data with explorer preview
        transaction_data = {
            "amount": amount,
            "to_address": to_address,
            "symbol": symbol,
            "from_address": wallet_address,
            "network": "Somnia Testnet",
            "chain_id": 50312,
            "estimated_gas": "21000",  # Default gas limit
            "explorer_url": f"https://shannon-explorer.somnia.network/address/{to_address}"
        }
        
        return {
            "response": self.response_templates["send_confirmation"].format(
                amount=amount,
                symbol=symbol,
                to_address=to_address,
                from_address=wallet_address
            ),
            "success": True,
            "action": "send_transaction",
            "transaction_data": transaction_data,
            "requires_confirmation": True,
            "explorer_links": [transaction_data["explorer_url"]],
            "suggested_actions": ["confirm_transaction", "cancel_transaction", "edit_amount"]
        }
    
    async def _handle_enhanced_create_wallet(self, context: Dict = None) -> Dict[str, Any]:
        """Enhanced wallet creation with security emphasis"""
        try:
            wallet_info = self.wallet_core.create_wallet()
            
            explorer_url = f"https://shannon-explorer.somnia.network/address/{wallet_info['address']}"
            
            return {
                "response": self.response_templates["wallet_created"].format(
                    address=wallet_info["address"],
                    private_key=wallet_info["private_key"],
                    mnemonic=wallet_info["mnemonic"]
                ),
                "success": True,
                "action": "create_wallet",
                "data": wallet_info,
                "explorer_links": [explorer_url],
                "requires_confirmation": False,
                "suggested_actions": ["backup_wallet", "check_balance", "send_transaction"]
            }
        except Exception as e:
            return self._create_error_response(f"Error creating wallet: {str(e)}")
    
    async def _handle_enhanced_get_price(self, parameters: Dict, context: Dict = None) -> Dict[str, Any]:
        """Enhanced price check with market analysis"""
        try:
            symbol = parameters.get("symbol", "SOMI")
            price_data = await self.wallet_core.get_enhanced_token_price(symbol)
            
            explorer_url = f"https://shannon-explorer.somnia.network/"
            
            return {
                "response": self.response_templates["price_info"].format(
                    symbol=symbol,
                    usd_price=price_data.get("usd", "N/A"),
                    idr_price=price_data.get("idr", "N/A"),
                    change_24h=price_data.get("change_24h", "N/A"),
                    market_cap=price_data.get("market_cap", "N/A"),
                    volume_24h=price_data.get("volume_24h", "N/A"),
                    ath=price_data.get("ath", "N/A")
                ),
                "success": True,
                "action": "get_price",
                "data": price_data,
                "explorer_links": [explorer_url],
                "market_insights": price_data.get("insights", {}),
                "suggested_actions": ["buy_crypto", "compare_exchanges", "market_analysis"]
            }
        except Exception as e:
            return self._create_error_response(f"Error fetching price: {str(e)}")
    
    async def _handle_enhanced_gas_price(self, context: Dict = None) -> Dict[str, Any]:
        """Enhanced gas price check"""
        try:
            gas_data = await self.wallet_core.get_gas_prices()
            
            response = f"⛽ **Current Network Gas Prices**\n\n"
            response += f"• **Current:** {gas_data.get('current', 'N/A')} Gwei\n"
            response += f"• **Fast:** {gas_data.get('fast', 'N/A')} Gwei\n"
            response += f"• **Slow:** {gas_data.get('slow', 'N/A')} Gwei\n"
            response += f"• **Network:** Somnia Testnet\n\n"
            response += "💡 *Lower gas prices mean slower but cheaper transactions*"
            
            return {
                "response": response,
                "success": True,
                "action": "gas_price",
                "data": gas_data,
                "requires_confirmation": False,
                "suggested_actions": ["send_transaction", "check_balance", "get_price"]
            }
        except Exception as e:
            return self._create_error_response(f"Error fetching gas prices: {str(e)}")
    
    def _handle_enhanced_help(self, context: Dict = None) -> Dict[str, Any]:
        """Enhanced help with context-aware suggestions"""
        return {
            "response": self.response_templates["help"],
            "success": True,
            "action": "help",
            "requires_confirmation": False,
            "suggested_actions": ["get_balance", "get_price", "send_transaction", "create_wallet"]
        }
    
    async def _enhanced_fallback_processing(self, message: str, wallet_address: str = None, context: Dict = None) -> Dict[str, Any]:
        """Enhanced fallback processing with better context awareness"""
        # Use the enhanced intent extraction
        fake_ai_response = self._enhanced_intent_extraction(message, context)
        return await self._execute_enhanced_action(fake_ai_response, wallet_address, context)
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "response": f"❌ **I encountered an error**\n\n`{error_message}`\n\nPlease try again or contact support if the issue persists.",
            "success": False,
            "action": "error",
            "requires_confirmation": False,
            "suggested_actions": ["retry", "help", "contact_support"]
        }
    
    # Method to handle transaction confirmations from frontend
    async def confirm_transaction(self, transaction_data: Dict, private_key: str = None) -> Dict[str, Any]:
        """Handle transaction confirmation with enhanced features"""
        try:
            # Execute the transaction
            result = await self.wallet_core.send_transaction(
                transaction_data, 
                private_key
            )
            
            if result.get("success"):
                tx_hash = result.get("transaction_hash")
                explorer_url = f"https://shannon-explorer.somnia.network/tx/{tx_hash}"
                
                return {
                    "response": self.response_templates["send_success"].format(
                        amount=transaction_data["amount"],
                        symbol=transaction_data["symbol"],
                        to_address=transaction_data["to_address"],
                        tx_hash=tx_hash,
                        explorer_url=explorer_url
                    ),
                    "success": True,
                    "action": "send_transaction",
                    "transaction_hash": tx_hash,
                    "explorer_links": [explorer_url],
                    "requires_confirmation": False,
                    "suggested_actions": ["view_on_explorer", "check_balance", "new_transaction"]
                }
            else:
                return {
                    "response": self.response_templates["send_failed"].format(
                        error=result.get("error", "Unknown error")
                    ),
                    "success": False,
                    "action": "send_transaction",
                    "requires_confirmation": False
                }
                
        except Exception as e:
            return self._create_error_response(f"Transaction confirmation failed: {str(e)}")

# Maintain backward compatibility
class NLPAgent(EnhancedNLPAgent):
    """Backward compatibility layer"""
    pass