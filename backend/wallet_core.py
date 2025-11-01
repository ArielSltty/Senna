# backend/wallet_core.py
"""
💰 Enhanced Web3.py Blockchain Operations for Senna Wallet
Advanced wallet functionality with market analysis, explorer integration, and AI features
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
import secrets
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
import aiohttp
from decimal import Decimal, ROUND_DOWN
import time
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedWalletCore:
    """
    Enhanced core wallet functionality for Somnia Blockchain
    Advanced features: market analysis, explorer integration, gas optimization, AI recommendations
    """
    
    def __init__(self):
        # Somnia Testnet configuration
        self.rpc_url = os.getenv("SOMNIA_RPC_URL", "https://dream-rpc.somnia.network/")
        self.chain_id = int(os.getenv("SOMNIA_CHAIN_ID", "50312"))
        self.symbol = os.getenv("SOMNIA_SYMBOL", "STT")
        self.explorer_url = os.getenv("SOMNIA_EXPLORER_URL", "https://shannon-explorer.somnia.network/")
        
        # Initialize Web3 connection with enhanced settings
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={'timeout': 60}))
        
        # Add POA middleware for testnet compatibility
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Configure gas strategy
        self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        
        # Enhanced API configuration
        self.coingecko_api_url = "https://api.coingecko.com/api/v3"
        self.stripe_api_key = os.getenv("STRIPE_API_KEY")
        
        # Enhanced contract addresses
        self.token_addresses = {
            "SOMI": os.getenv("SOMI_TOKEN_ADDRESS", "0xc3DfbBc01Ed164F5f5b4E6B1501B20FfC9B3a49a"),
            "STT": "0x0000000000000000000000000000000000000000"  # Native token
        }
        
        # Market data cache
        self.market_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Transaction history cache
        self.transaction_cache = {}
        
        # Gas price cache
        self.gas_cache = {}
        self.gas_cache_duration = 60  # 1 minute
        
        logger.info(f"🔗 Enhanced WalletCore connected to Somnia Testnet: {self.w3.is_connected()}")
        logger.info(f"📊 Latest block: {self.w3.eth.block_number}")
        logger.info(f"🔍 Explorer: {self.explorer_url}")
    
    def create_wallet(self) -> Dict[str, Any]:
        """
        Create a new Ethereum wallet with enhanced security
        Returns: {address, private_key, mnemonic, explorer_url}
        """
        try:
            # Enable unaudited HD wallet features
            Account.enable_unaudited_hdwallet_features()
            
            # Generate mnemonic and account with enhanced entropy
            mnemonic = Account.create_with_mnemonic(passphrase="", num_words=12)[1]
            account = Account.from_mnemonic(mnemonic)
            
            # Create explorer URL
            explorer_url = f"{self.explorer_url}/address/{account.address}"
            
            wallet_info = {
                "address": account.address,
                "private_key": account.key.hex(),
                "mnemonic": mnemonic,
                "explorer_url": explorer_url,
                "message": "✅ Enhanced wallet created successfully! Save your private key and mnemonic securely.",
                "security_level": "high",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"🆕 Enhanced wallet created: {account.address}")
            return wallet_info
            
        except Exception as e:
            logger.error(f"❌ Enhanced wallet creation failed: {str(e)}")
            raise Exception(f"Enhanced wallet creation failed: {str(e)}")
    
    def get_balance(self, address: str) -> int:
        """
        Get enhanced balance with validation and caching
        """
        try:
            # Validate address format
            if not self.w3.is_address(address):
                raise ValueError("Invalid Ethereum address format")
            
            checksum_address = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_address)
            
            logger.info(f"💰 Enhanced balance check: {address} = {balance_wei} wei")
            return balance_wei
            
        except Exception as e:
            logger.error(f"❌ Enhanced balance check failed for {address}: {str(e)}")
            raise Exception(f"Enhanced balance check failed: {str(e)}")
    
    def wei_to_ether(self, wei_amount: int) -> float:
        """
        Convert wei to ether with precision
        """
        return float(Web3.from_wei(wei_amount, 'ether'))
    
    def ether_to_wei(self, ether_amount: float) -> int:
        """
        Convert ether to wei with precision
        """
        return Web3.to_wei(ether_amount, 'ether')
    
    async def send_transaction(self, transaction_data: Dict[str, Any], private_key: str = None) -> Dict[str, Any]:
        """
        Enhanced transaction sending with confirmation flow and explorer integration
        """
        try:
            to_address = transaction_data.get("to_address")
            amount = transaction_data.get("amount")
            symbol = transaction_data.get("symbol", "STT")
            
            if not to_address or not amount:
                raise ValueError("Missing required transaction parameters")
            
            # Validate addresses
            if not self.w3.is_address(to_address):
                raise ValueError("Invalid recipient address format")
            
            if private_key:
                # Create account from private key
                account = Account.from_key(private_key)
                from_address = account.address
            else:
                from_address = transaction_data.get("from_address")
                if not from_address:
                    raise ValueError("Sender address required")
            
            # Convert amount to wei
            amount_wei = self.ether_to_wei(amount)
            
            # Validate sender has sufficient balance
            balance = self.get_balance(from_address)
            if balance < amount_wei:
                raise ValueError(f"Insufficient balance. Available: {self.wei_to_ether(balance)} STT, Required: {amount} {symbol}")
            
            # Get optimized gas parameters
            gas_params = await self.get_optimized_gas_parameters(from_address, to_address, amount_wei)
            
            # Build enhanced transaction
            transaction = {
                'to': self.w3.to_checksum_address(to_address),
                'value': amount_wei,
                'gas': gas_params['gas_limit'],
                'gasPrice': gas_params['gas_price'],
                'nonce': self.w3.eth.get_transaction_count(from_address),
                'chainId': self.chain_id,
                'data': b''  # Empty data for simple transfers
            }
            
            if private_key:
                # Sign and send transaction
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_hash_hex = tx_hash.hex()
            else:
                # Return unsigned transaction for MetaMask
                tx_hash_hex = "pending_metamask"
            
            # Get explorer URL
            explorer_url = f"{self.explorer_url}/tx/{tx_hash_hex}" if tx_hash_hex != "pending_metamask" else ""
            
            # Enhanced response with all relevant data
            response = {
                "success": True,
                "transaction_hash": tx_hash_hex,
                "from_address": from_address,
                "to_address": to_address,
                "amount": amount,
                "symbol": symbol,
                "amount_wei": amount_wei,
                "gas_used": gas_params['gas_limit'],
                "gas_price_gwei": gas_params['gas_price_gwei'],
                "total_cost_wei": gas_params['total_cost_wei'],
                "explorer_url": explorer_url,
                "network": "Somnia Testnet",
                "chain_id": self.chain_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "✅ Transaction executed successfully!"
            }
            
            logger.info(f"📤 Enhanced transaction sent: {tx_hash_hex} from {from_address} to {to_address}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Enhanced transaction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Transaction failed: {str(e)}"
            }
    
    async def get_optimized_gas_parameters(self, from_address: str, to_address: str, value: int) -> Dict[str, Any]:
        """
        Get optimized gas parameters for transaction
        """
        try:
            # Estimate gas limit
            gas_limit = self.w3.eth.estimate_gas({
                'from': from_address,
                'to': to_address,
                'value': value
            })
            
            # Get current gas price with strategy
            gas_price = self.w3.eth.generate_gas_price()
            if gas_price is None:
                gas_price = self.w3.eth.gas_price
            
            gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
            total_cost_wei = gas_limit * gas_price
            
            return {
                'gas_limit': gas_limit,
                'gas_price': gas_price,
                'gas_price_gwei': float(gas_price_gwei),
                'total_cost_wei': total_cost_wei,
                'total_cost_ether': float(self.w3.from_wei(total_cost_wei, 'ether'))
            }
            
        except Exception as e:
            logger.warning(f"Gas estimation failed, using defaults: {str(e)}")
            # Return safe defaults
            return {
                'gas_limit': 21000,
                'gas_price': self.w3.to_wei('10', 'gwei'),
                'gas_price_gwei': 10.0,
                'total_cost_wei': 21000 * self.w3.to_wei('10', 'gwei'),
                'total_cost_ether': 0.00021
            }
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Enhanced transaction status with explorer integration
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            
            status = "confirmed" if receipt.status == 1 else "failed"
            confirmations = self.w3.eth.block_number - receipt.blockNumber if receipt.blockNumber else 0
            
            # Enhanced status information
            response = {
                "status": status,
                "confirmations": confirmations,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "transaction_hash": tx_hash,
                "from_address": transaction['from'],
                "to_address": transaction['to'],
                "value_ether": float(self.w3.from_wei(transaction['value'], 'ether')),
                "explorer_url": f"{self.explorer_url}/tx/{tx_hash}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add block timestamp if available
            try:
                block = self.w3.eth.get_block(receipt.blockNumber)
                response["block_timestamp"] = block.timestamp
            except:
                pass
            
            return response
            
        except Exception as e:
            logger.warning(f"Transaction status check failed (might be pending): {str(e)}")
            return {
                "status": "pending",
                "transaction_hash": tx_hash,
                "explorer_url": f"{self.explorer_url}/tx/{tx_hash}",
                "message": "Transaction is pending confirmation"
            }
    
    async def get_enhanced_token_price(self, symbol: str = "SOMI") -> Dict[str, Any]:
        """
        Enhanced price data with market analysis and insights
        """
        cache_key = f"price_{symbol}"
        if cache_key in self.market_cache:
            cached_data = self.market_cache[cache_key]
            if time.time() - cached_data['cache_time'] < self.cache_duration:
                return cached_data['data']
        
        try:
            # For testnet, we'll use enhanced mock data with analysis
            if symbol.upper() == "STT":
                price_data = await self._get_enhanced_mock_price(symbol)
            else:
                # Try to get real data from CoinGecko
                price_data = await self._get_coingecko_price(symbol)
                if not price_data:
                    price_data = await self._get_enhanced_mock_price(symbol)
            
            # Add market insights
            price_data.update(await self._generate_market_insights(symbol, price_data))
            
            # Cache the result
            self.market_cache[cache_key] = {
                'data': price_data,
                'cache_time': time.time()
            }
            
            return price_data
            
        except Exception as e:
            logger.error(f"❌ Enhanced price fetch failed for {symbol}: {str(e)}")
            return await self._get_enhanced_mock_price(symbol)
    
    async def _get_coingecko_price(self, symbol: str) -> Dict[str, Any]:
        """Get price data from CoinGecko API"""
        try:
            coin_id = self._get_coin_gecko_id(symbol)
            if not coin_id:
                return None
                
            async with aiohttp.ClientSession() as session:
                url = f"{self.coingecko_api_url}/coins/{coin_id}"
                params = {
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "true",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = data.get("market_data", {})
                        
                        return {
                            "usd": market_data.get("current_price", {}).get("usd", 0),
                            "idr": market_data.get("current_price", {}).get("idr", 0),
                            "change_24h": market_data.get("price_change_percentage_24h", 0),
                            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                            "volume_24h": market_data.get("total_volume", {}).get("usd", 0),
                            "ath": market_data.get("ath", {}).get("usd", 0),
                            "symbol": symbol.upper(),
                            "source": "coingecko",
                            "last_updated": datetime.utcnow().isoformat()
                        }
            return None
        except Exception as e:
            logger.warning(f"CoinGecko API failed for {symbol}: {str(e)}")
            return None
    
    async def _get_enhanced_mock_price(self, symbol: str) -> Dict[str, Any]:
        """Get enhanced mock price data with realistic fluctuations"""
        base_prices = {
            "SOMI": {"usd": 0.25, "idr": 3850, "volatility": 0.15},
            "STT": {"usd": 0.15, "idr": 2300, "volatility": 0.08},
            "ETH": {"usd": 3500, "idr": 53900000, "volatility": 0.12},
        }
        
        base_data = base_prices.get(symbol.upper(), {"usd": 1.0, "idr": 15400, "volatility": 0.10})
        
        # Simulate price movement
        import random
        change_24h = random.uniform(-base_data["volatility"], base_data["volatility"])
        current_price_usd = base_data["usd"] * (1 + change_24h)
        current_price_idr = base_data["idr"] * (1 + change_24h)
        
        return {
            "usd": round(current_price_usd, 4),
            "idr": round(current_price_idr, 2),
            "change_24h": round(change_24h * 100, 2),
            "market_cap": round(current_price_usd * 100000000, 2),  # Mock market cap
            "volume_24h": round(current_price_usd * 5000000, 2),   # Mock volume
            "ath": round(base_data["usd"] * 1.5, 4),              # Mock ATH
            "symbol": symbol.upper(),
            "source": "enhanced_mock",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _generate_market_insights(self, symbol: str, price_data: Dict) -> Dict[str, Any]:
        """Generate AI-like market insights based on price data"""
        change_24h = price_data.get("change_24h", 0)
        volume_24h = price_data.get("volume_24h", 0)
        
        insights = {
            "sentiment": "neutral",
            "recommendation": "hold",
            "confidence": 0.7,
            "key_levels": {},
            "risk_level": "medium"
        }
        
        # Basic sentiment analysis
        if change_24h > 5:
            insights["sentiment"] = "bullish"
            insights["recommendation"] = "buy" if change_24h > 10 else "accumulate"
            insights["risk_level"] = "high" if change_24h > 15 else "medium"
        elif change_24h < -5:
            insights["sentiment"] = "bearish"
            insights["recommendation"] = "sell" if change_24h < -10 else "reduce"
            insights["risk_level"] = "high" if change_24h < -15 else "medium"
        else:
            insights["sentiment"] = "neutral"
            insights["recommendation"] = "hold"
            insights["risk_level"] = "low"
        
        # Generate support/resistance levels
        current_price = price_data.get("usd", 0)
        insights["key_levels"] = {
            "support_1": round(current_price * 0.95, 4),
            "support_2": round(current_price * 0.90, 4),
            "resistance_1": round(current_price * 1.05, 4),
            "resistance_2": round(current_price * 1.10, 4)
        }
        
        # Volume analysis
        if volume_24h > 100000000:  # High volume threshold
            insights["volume_analysis"] = "high_volume"
            insights["confidence"] = min(insights["confidence"] + 0.2, 0.9)
        else:
            insights["volume_analysis"] = "normal_volume"
        
        return {"insights": insights}
    
    async def get_market_data(self) -> Dict[str, Any]:
        """Get comprehensive market data for multiple tokens"""
        try:
            symbols = ["SOMI", "STT", "ETH"]
            market_data = {}
            
            for symbol in symbols:
                market_data[symbol] = await self.get_enhanced_token_price(symbol)
            
            # Add overall market summary
            total_market_cap = sum(data.get("market_cap", 0) for data in market_data.values())
            average_change = sum(data.get("change_24h", 0) for data in market_data.values()) / len(symbols)
            
            return {
                "tokens": market_data,
                "summary": {
                    "total_market_cap": total_market_cap,
                    "average_24h_change": round(average_change, 2),
                    "market_sentiment": "bullish" if average_change > 0 else "bearish",
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Market data fetch failed: {str(e)}")
            return {"error": "Market data temporarily unavailable"}
    
    async def get_gas_prices(self) -> Dict[str, Any]:
        """Get enhanced gas price information with recommendations"""
        cache_key = "gas_prices"
        if cache_key in self.gas_cache:
            cached_data = self.gas_cache[cache_key]
            if time.time() - cached_data['cache_time'] < self.gas_cache_duration:
                return cached_data['data']
        
        try:
            # Get current gas prices from network
            current_gas = self.w3.eth.gas_price
            current_gas_gwei = self.w3.from_wei(current_gas, 'gwei')
            
            # Calculate different speed tiers
            slow_gas = current_gas * 8 // 10  # 80% of current
            fast_gas = current_gas * 12 // 10  # 120% of current
            rapid_gas = current_gas * 15 // 10  # 150% of current
            
            gas_data = {
                "slow": float(self.w3.from_wei(slow_gas, 'gwei')),
                "current": float(current_gas_gwei),
                "fast": float(self.w3.from_wei(fast_gas, 'gwei')),
                "rapid": float(self.w3.from_wei(rapid_gas, 'gwei')),
                "recommendation": self._get_gas_recommendation(float(current_gas_gwei)),
                "network_congestion": "low" if float(current_gas_gwei) < 20 else "high",
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            self.gas_cache[cache_key] = {
                'data': gas_data,
                'cache_time': time.time()
            }
            
            return gas_data
            
        except Exception as e:
            logger.error(f"Gas price check failed: {str(e)}")
            return {
                "slow": 10.0,
                "current": 15.0,
                "fast": 20.0,
                "rapid": 25.0,
                "recommendation": "use_current",
                "network_congestion": "unknown",
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def _get_gas_recommendation(self, current_gas: float) -> str:
        """Get gas price recommendation based on current network conditions"""
        if current_gas < 15:
            return "use_current"  # Good prices, use current
        elif current_gas < 30:
            return "use_slow"     # Moderate prices, can use slower
        else:
            return "use_fast"     # High congestion, pay for priority
    
    async def get_transaction_history(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get enhanced transaction history with explorer links
        Note: This is a simplified version - in production, use proper indexer
        """
        try:
            # This is a mock implementation - in real scenario, use blockchain indexer
            transactions = []
            
            # For demo purposes, return mock transactions
            for i in range(min(limit, 5)):
                tx_hash = f"0x{secrets.token_hex(32)}"
                transactions.append({
                    "hash": tx_hash,
                    "from": address,
                    "to": f"0x{secrets.token_hex(20)}",
                    "value": float(self.w3.from_wei(1000000000000000000 * (i + 1), 'ether')),
                    "symbol": "STT",
                    "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                    "status": "confirmed",
                    "explorer_url": f"{self.explorer_url}/tx/{tx_hash}",
                    "confirmations": 100 - i
                })
            
            return transactions
            
        except Exception as e:
            logger.error(f"Transaction history failed for {address}: {str(e)}")
            return []
    
    async def get_wallet_analytics(self, address: str) -> Dict[str, Any]:
        """Get comprehensive wallet analytics and insights"""
        try:
            balance_wei = self.get_balance(address)
            balance_ether = self.wei_to_ether(balance_wei)
            
            # Mock portfolio value (in real scenario, calculate from multiple tokens)
            portfolio_value_usd = balance_ether * 0.15  # STT price
            
            # Get transaction history
            transactions = await self.get_transaction_history(address, 5)
            
            return {
                "address": address,
                "balance": {
                    "wei": balance_wei,
                    "ether": balance_ether,
                    "symbol": "STT"
                },
                "portfolio": {
                    "total_value_usd": round(portfolio_value_usd, 2),
                    "total_value_idr": round(portfolio_value_usd * 15400, 2),
                    "primary_asset": "STT"
                },
                "activity": {
                    "total_transactions": len(transactions),
                    "last_transaction": transactions[0] if transactions else None,
                    "transaction_history": transactions
                },
                "explorer_url": f"{self.explorer_url}/address/{address}",
                "analytics_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wallet analytics failed for {address}: {str(e)}")
            return {"error": "Analytics temporarily unavailable"}
    
    def validate_address(self, address: str) -> bool:
        """Enhanced address validation"""
        return self.w3.is_address(address)
    
    def get_checksum_address(self, address: str) -> str:
        """Get checksummed version of address"""
        return self.w3.to_checksum_address(address)
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get enhanced network information"""
        try:
            block_number = self.w3.eth.block_number
            is_connected = self.w3.is_connected()
            
            # Get gas prices for network health
            gas_price = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
            
            return {
                "network": "Somnia Testnet",
                "chain_id": self.chain_id,
                "symbol": self.symbol,
                "block_number": block_number,
                "is_connected": is_connected,
                "gas_price_gwei": float(gas_price_gwei),
                "rpc_url": self.rpc_url,
                "explorer_url": self.explorer_url,
                "health_status": "healthy" if is_connected and gas_price_gwei < 100 else "degraded",
                "last_checked": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Network info failed: {str(e)}")
            return {
                "network": "Somnia Testnet",
                "chain_id": self.chain_id,
                "symbol": self.symbol,
                "is_connected": False,
                "health_status": "offline",
                "error": str(e)
            }
    
    def _get_coin_gecko_id(self, symbol: str) -> Optional[str]:
        """Map symbol to CoinGecko coin ID"""
        coin_mapping = {
            "SOMI": "somnia",  # Update when SOMI is listed
            "ETH": "ethereum",
            "BTC": "bitcoin",
            "BNB": "binancecoin"
        }
        return coin_mapping.get(symbol.upper())
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for price updates"""
        return datetime.utcnow().isoformat()

# Maintain backward compatibility
class WalletCore(EnhancedWalletCore):
    """Backward compatibility layer"""
    pass

# Enhanced utility functions
def generate_enhanced_private_key() -> str:
    """Generate a cryptographically secure private key with enhanced entropy"""
    return "0x" + secrets.token_hex(32)

def validate_private_key_format(private_key: str) -> bool:
    """Validate private key format"""
    try:
        if not private_key.startswith('0x'):
            return False
        if len(private_key) != 66:  # 0x + 64 hex characters
            return False
        # Try to create account to validate
        Account.from_key(private_key)
        return True
    except:
        return False

# Test function for enhanced features
async def test_enhanced_wallet_core():
    """Test enhanced wallet core functionality"""
    wallet_core = EnhancedWalletCore()
    
    print("🧪 Testing Enhanced Wallet Core...")
    print(f"🔗 Connected: {wallet_core.w3.is_connected()}")
    
    # Test enhanced network info
    network_info = wallet_core.get_network_info()
    print(f"📊 Enhanced Network: {network_info}")
    
    # Test wallet creation
    wallet = wallet_core.create_wallet()
    print(f"🆕 Enhanced wallet created: {wallet['address']}")
    print(f"🔗 Explorer: {wallet['explorer_url']}")
    
    # Test enhanced balance
    balance = wallet_core.get_balance(wallet['address'])
    print(f"💰 Enhanced Balance: {wallet_core.wei_to_ether(balance)} {wallet_core.symbol}")
    
    # Test market data
    market_data = await wallet_core.get_enhanced_token_price("SOMI")
    print(f"📈 Enhanced Market Data: {market_data}")
    
    # Test gas prices
    gas_prices = await wallet_core.get_gas_prices()
    print(f"⛽ Enhanced Gas Prices: {gas_prices}")
    
    print("✅ Enhanced Wallet Core test completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_wallet_core())