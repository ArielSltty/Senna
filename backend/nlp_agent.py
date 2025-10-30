# backend/nlp_agent.py
"""
🧠 Multi-AI Provider Integration & Intent Parsing for Senna Wallet
Supports: Groq, DeepSeek, and fallback pattern matching
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class NLPAgent:
    """
    AI Agent for processing natural language commands
    Supports multiple AI providers and fallback pattern matching
    """
    
    def __init__(self, wallet_core):
        self.wallet_core = wallet_core
        self.session = None
        
        # AI Provider Configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "groq").lower()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_base_url = "https://api.groq.com/openai/v1"
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # Intent patterns for fallback processing
        self.intent_patterns = {
            "balance": ["saldo", "balance", "cek saldo", "berapa saldo", "lihat saldo", "my balance", "check balance"],
            "send": ["kirim", "send", "transfer", "berikan", "kasih", "to 0x", "to "],
            "receive": ["terima", "receive", "dapat", "minta"],
            "create_wallet": ["buat wallet", "buat dompet", "wallet baru", "dompet baru", "create wallet", "new wallet"],
            "price": ["harga", "price", "nilai", "berapa harga", "kurs", "current price", "what's the price"],
            "buy": ["beli", "buy", "pembelian", "purchase", "i want to buy"],
            "compare": ["bandingkan", "compare", "mana yang", "terbaik", "best place"],
            "help": ["bantuan", "help", "tolong", "cara pakai", "what can you do", "how to use"]
        }
        
        # Response templates
        self.response_templates = {
            "balance": "💰 Your balance is {balance} {symbol}",
            "send_success": "✅ Successfully sent {amount} {symbol} to {address}",
            "send_failed": "❌ Failed to send transaction: {error}",
            "wallet_created": "🎉 New wallet created! Address: {address}",
            "price_info": "📊 Current {symbol} price: ${usd_price} (₨{idr_price})",
            "help": """
🤖 **Senna Wallet Help Guide**

Here's what I can help you with:

• **Check Balance**: "Show my balance", "How much do I have?"
• **Send Crypto**: "Send 10 SOMI to 0x...", "Transfer 5 STT"
• **Create Wallet**: "Create new wallet for me"
• **Check Price**: "What's SOMI price today?", "Current STT value"
• **Buy Crypto**: "I want to buy 100k IDR worth of SOMI"
• **Compare Exchanges**: "Compare best places to buy SOMI"

Just type what you want to do in natural language!
            """
        }
        
        logger.info(f"🧠 NLP Agent initialized with provider: {self.ai_provider}")
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ NLP Agent session initialized")
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def process_message(self, message: str, wallet_address: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Process natural language message and return appropriate action
        """
        try:
            logger.info(f"🧠 Processing message: {message}")
            
            # Try to use AI for advanced understanding
            ai_response = await self._call_ai_api(message, wallet_address)
            
            if ai_response and ai_response.get("success", True):
                return await self._execute_ai_action(ai_response, wallet_address)
            
            # Fallback to pattern matching if AI fails
            return await self._fallback_intent_processing(message, wallet_address)
            
        except Exception as e:
            logger.error(f"❌ NLP processing error: {str(e)}")
            return {
                "response": "Sorry, I encountered an error processing your request. Please try again.",
                "success": False,
                "action": "error"
            }
    
    async def _call_ai_api(self, message: str, wallet_address: str = None) -> Optional[Dict[str, Any]]:
        """
        Call AI API based on configured provider
        """
        try:
            if self.ai_provider == "groq" and self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
                return await self._call_groq_api(message, wallet_address)
            elif self.ai_provider == "deepseek" and self.deepseek_api_key and self.deepseek_api_key != "your_deepseek_api_key_here":
                return await self._call_deepseek_api(message, wallet_address)
            else:
                logger.warning("No valid AI provider configured, using fallback")
                return None
        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            return None
    
    async def _call_groq_api(self, message: str, wallet_address: str = None) -> Optional[Dict[str, Any]]:
        """
        Call Groq API for natural language understanding
        """
        if not self.session:
            await self.initialize()
        
        try:
            prompt = self._build_ai_prompt(message, wallet_address)
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.groq_model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are Senna, an AI wallet assistant for Somnia blockchain. 
                        Parse user messages and return structured JSON with intent and parameters.
                        
                        Available actions:
                        - get_balance: Get wallet balance
                        - send_transaction: Send crypto to address
                        - create_wallet: Create new wallet
                        - get_price: Get token price
                        - convert_currency: Convert between fiat and crypto
                        - buy_crypto: Initiate crypto purchase
                        - compare_exchanges: Compare exchange prices
                        - help: Show help guide
                        
                        Return ONLY valid JSON format:
                        {
                            "intent": "action_name",
                            "parameters": {"key": "value"},
                            "confidence": 0.9,
                            "response_message": "Friendly response"
                        }"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500,
                "top_p": 0.9
            }
            
            async with self.session.post(f"{self.groq_base_url}/chat/completions", 
                                       headers=headers, json=payload) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_content = data["choices"][0]["message"]["content"]
                    
                    # Extract JSON from AI response
                    try:
                        json_start = ai_content.find('{')
                        json_end = ai_content.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = ai_content[json_start:json_end]
                            return json.loads(json_str)
                        else:
                            return self._parse_ai_text_response(ai_content, message)
                    except json.JSONDecodeError:
                        return self._parse_ai_text_response(ai_content, message)
                else:
                    error_text = await response.text()
                    logger.error(f"Groq API error: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}")
            return None
    
    async def _call_deepseek_api(self, message: str, wallet_address: str = None) -> Optional[Dict[str, Any]]:
        """
        Call DeepSeek API for natural language understanding
        """
        if not self.session:
            await self.initialize()
        
        try:
            prompt = self._build_ai_prompt(message, wallet_address)
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.deepseek_model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are Senna, an AI wallet assistant. Return ONLY JSON:
                        {
                            "intent": "action_name",
                            "parameters": {"key": "value"},
                            "confidence": 0.9,
                            "response_message": "Friendly response"
                        }"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            async with self.session.post(f"{self.deepseek_base_url}/chat/completions", 
                                       headers=headers, json=payload) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_content = data["choices"][0]["message"]["content"]
                    
                    try:
                        return json.loads(ai_content)
                    except json.JSONDecodeError:
                        return self._parse_ai_text_response(ai_content, message)
                else:
                    logger.error(f"DeepSeek API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {str(e)}")
            return None
    
    def _build_ai_prompt(self, message: str, wallet_address: str = None) -> str:
        """Build prompt for AI understanding"""
        context = f"User message: \"{message}\"\n"
        
        if wallet_address:
            context += f"Current wallet address: {wallet_address}\n"
        
        context += """
Extract the intent and parameters from this message. Focus on:
- Amounts (numbers with or without currency)
- Cryptocurrency symbols (SOMI, STT, etc.)
- Wallet addresses (0x... format)
- Actions (send, receive, check, buy, etc.)
- Currency conversions (USD, IDR, etc.)

Return only valid JSON.
"""
        return context
    
    def _parse_ai_text_response(self, ai_text: str, original_message: str) -> Dict[str, Any]:
        """Parse AI text response when JSON parsing fails"""
        return self._extract_intent_from_pattern(original_message)
    
    def _extract_intent_from_pattern(self, message: str) -> Dict[str, Any]:
        """Extract intent using pattern matching"""
        message_lower = message.lower()
        
        # Balance check
        if any(word in message_lower for word in self.intent_patterns["balance"]):
            return {
                "intent": "get_balance",
                "parameters": {},
                "confidence": 0.8,
                "response_message": "I'll check your balance for you."
            }
        
        # Price check
        elif any(word in message_lower for word in self.intent_patterns["price"]):
            symbol = "SOMI"
            if "stt" in message_lower:
                symbol = "STT"
            elif "eth" in message_lower:
                symbol = "ETH"
            elif "btc" in message_lower:
                symbol = "BTC"
                
            return {
                "intent": "get_price",
                "parameters": {"symbol": symbol},
                "confidence": 0.8,
                "response_message": f"I'll check the current {symbol} price for you."
            }
        
        # Send transaction
        elif any(word in message_lower for word in self.intent_patterns["send"]):
            return self._extract_send_parameters(message)
        
        # Create wallet
        elif any(word in message_lower for word in self.intent_patterns["create_wallet"]):
            return {
                "intent": "create_wallet",
                "parameters": {},
                "confidence": 0.9,
                "response_message": "I'll create a new wallet for you."
            }
        
        # Help
        elif any(word in message_lower for word in self.intent_patterns["help"]):
            return {
                "intent": "help",
                "parameters": {},
                "confidence": 0.9,
                "response_message": "Here's how I can help you:"
            }
        
        # Default to help
        else:
            return {
                "intent": "help",
                "parameters": {},
                "confidence": 0.5,
                "response_message": "I'm not sure what you want to do. Here's how I can help:"
            }
    
    def _extract_send_parameters(self, message: str) -> Dict[str, Any]:
        """Extract send transaction parameters from message"""
        import re
        
        parameters = {}
        
        # Extract amount and symbol
        amount_pattern = r'(\d+\.?\d*)\s*(SOMI|STT|ETH|BTC)'
        amount_match = re.search(amount_pattern, message, re.IGNORECASE)
        if amount_match:
            parameters["amount"] = float(amount_match.group(1))
            parameters["symbol"] = amount_match.group(2).upper()
        
        # Extract address
        address_pattern = r'0x[a-fA-F0-9]{40}'
        address_match = re.search(address_pattern, message)
        if address_match:
            parameters["to_address"] = address_match.group(0)
        
        return {
            "intent": "send_transaction",
            "parameters": parameters,
            "confidence": 0.7 if parameters else 0.3,
            "response_message": f"I'll help you send {parameters.get('amount', '')} {parameters.get('symbol', '')} to {parameters.get('to_address', 'the address')}" if parameters else "Please specify amount and recipient address."
        }
    
    async def _execute_ai_action(self, ai_data: Dict[str, Any], wallet_address: str = None) -> Dict[str, Any]:
        """Execute action based on AI understanding"""
        intent = ai_data.get("intent")
        parameters = ai_data.get("parameters", {})
        
        logger.info(f"🎯 Executing intent: {intent} with params: {parameters}")
        
        try:
            if intent == "get_balance":
                return await self._handle_get_balance(wallet_address)
            
            elif intent == "send_transaction":
                return await self._handle_send_transaction(parameters, wallet_address)
            
            elif intent == "create_wallet":
                return await self._handle_create_wallet()
            
            elif intent == "get_price":
                return await self._handle_get_price(parameters)
            
            elif intent == "convert_currency":
                return await self._handle_convert_currency(parameters)
            
            elif intent == "buy_crypto":
                return await self._handle_buy_crypto(parameters)
            
            elif intent == "compare_exchanges":
                return await self._handle_compare_exchanges(parameters)
            
            elif intent == "help":
                return self._handle_help()

            else:
                # Prevent infinite recursion: do NOT call fallback again for unknown intents
                logger.warning(f"Unknown intent: {intent}. Returning help message instead.")
                return self._handle_help()


        except Exception as e:
            logger.error(f"❌ Action execution error: {str(e)}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "success": False,
                "action": intent
            }
    
    async def _handle_get_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Handle balance check request"""
        if not wallet_address:
            return {
                "response": "Please provide your wallet address to check balance, or create a new wallet first.",
                "success": False,
                "action": "get_balance"
            }
        
        try:
            balance_wei = self.wallet_core.get_balance(wallet_address)
            balance_ether = self.wallet_core.wei_to_ether(balance_wei)
            
            return {
                "response": self.response_templates["balance"].format(
                    balance=balance_ether, symbol="STT"
                ),
                "success": True,
                "action": "get_balance",
                "data": {
                    "balance": balance_ether,
                    "balance_wei": balance_wei,
                    "symbol": "STT",
                    "address": wallet_address
                }
            }
        except Exception as e:
            return {
                "response": f"Error checking balance: {str(e)}",
                "success": False,
                "action": "get_balance"
            }
    
    async def _handle_send_transaction(self, parameters: Dict, wallet_address: str) -> Dict[str, Any]:
        """Handle send transaction request"""
        amount = parameters.get("amount")
        to_address = parameters.get("to_address")
        symbol = parameters.get("symbol", "STT")
        
        if not amount or not to_address:
            return {
                "response": "Please specify both amount and recipient address. Example: 'Send 10 STT to 0x...'",
                "success": False,
                "action": "send_transaction"
            }
        
        return {
            "response": f"Ready to send {amount} {symbol} to {to_address}. Please confirm the transaction with your private key.",
            "success": True,
            "action": "send_transaction",
            "transaction_data": {
                "amount": amount,
                "to_address": to_address,
                "symbol": symbol,
                "from_address": wallet_address
            }
        }
    
    async def _handle_create_wallet(self) -> Dict[str, Any]:
        """Handle wallet creation request"""
        try:
            wallet_info = self.wallet_core.create_wallet()
            
            return {
                "response": self.response_templates["wallet_created"].format(
                    address=wallet_info["address"]
                ),
                "success": True,
                "action": "create_wallet",
                "data": wallet_info
            }
        except Exception as e:
            return {
                "response": f"Error creating wallet: {str(e)}",
                "success": False,
                "action": "create_wallet"
            }
    
    async def _handle_get_price(self, parameters: Dict) -> Dict[str, Any]:
        """Handle price check request"""
        try:
            symbol = parameters.get("symbol", "SOMI")
            price_data = await self.wallet_core.get_token_price(symbol)
            
            return {
                "response": self.response_templates["price_info"].format(
                    symbol=symbol,
                    usd_price=price_data.get("usd", "N/A"),
                    idr_price=price_data.get("idr", "N/A")
                ),
                "success": True,
                "action": "get_price",
                "data": price_data
            }
        except Exception as e:
            return {
                "response": f"Error fetching price: {str(e)}",
                "success": False,
                "action": "get_price"
            }
    
    async def _handle_convert_currency(self, parameters: Dict) -> Dict[str, Any]:
        """Handle currency conversion"""
        return {
            "response": "Currency conversion feature coming soon!",
            "success": True,
            "action": "convert_currency"
        }
    
    async def _handle_buy_crypto(self, parameters: Dict) -> Dict[str, Any]:
        """Handle crypto purchase request"""
        return {
            "response": "Crypto purchase with Stripe integration coming soon!",
            "success": True,
            "action": "buy_crypto"
        }
    
    async def _handle_compare_exchanges(self, parameters: Dict) -> Dict[str, Any]:
        """Handle exchange comparison"""
        return {
            "response": "Exchange comparison feature coming soon!",
            "success": True,
            "action": "compare_exchanges"
        }
    
    def _handle_help(self) -> Dict[str, Any]:
        """Handle help request"""
        return {
            "response": self.response_templates["help"],
            "success": True,
            "action": "help"
        }
    
    async def _fallback_intent_processing(self, message: str, wallet_address: str) -> Dict[str, Any]:
        """Fallback intent processing using pattern matching"""
        message_lower = message.lower()
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                fake_ai_response = {
                    "intent": intent,
                    "parameters": {},
                    "confidence": 0.6,
                    "response_message": f"Processing your {intent} request..."
                }
                return await self._execute_ai_action(fake_ai_response, wallet_address)
        
        # Default to help if no intent matched
        return self._handle_help()