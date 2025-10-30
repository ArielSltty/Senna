# backend/wallet_core.py
"""
💰 Web3.py Blockchain Operations for Senna Wallet
Core wallet functionality for Somnia Blockchain
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
import secrets
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
import aiohttp
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)

class WalletCore:
    """
    Core wallet functionality for Somnia Blockchain
    Handles all blockchain interactions
    """
    
    def __init__(self):
        # Somnia Testnet configuration
        self.rpc_url = os.getenv("SOMNIA_RPC_URL", "https://dream-rpc.somnia.network/")
        self.chain_id = int(os.getenv("SOMNIA_CHAIN_ID", "50312"))
        self.symbol = os.getenv("SOMNIA_SYMBOL", "STT")
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add POA middleware for testnet compatibility
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Price API configuration
        self.coingecko_api_url = "https://api.coingecko.com/api/v3"
        self.stripe_api_key = os.getenv("STRIPE_API_KEY")
        
        # Contract addresses (to be deployed)
        self.token_addresses = {
            "SOMI": os.getenv("SOMI_TOKEN_ADDRESS", "0x..."),  # Update after deployment
            "STT": "0x0000000000000000000000000000000000000000"  # Native token
        }
        
        logger.info(f"🔗 Connected to Somnia Testnet: {self.w3.is_connected()}")
        logger.info(f"📊 Latest block: {self.w3.eth.block_number}")
    
    def create_wallet(self) -> Dict[str, Any]:
        """
        Create a new Ethereum wallet
        Returns: {address, private_key, mnemonic}
        """
        try:
            # Enable unaudited HD wallet features
            Account.enable_unaudited_hdwallet_features()
            
            # Generate mnemonic and account
            mnemonic = Account.create_with_mnemonic()[1]
            account = Account.from_mnemonic(mnemonic)
            
            wallet_info = {
                "address": account.address,
                "private_key": account.key.hex(),
                "mnemonic": mnemonic,
                "message": "✅ Wallet created successfully! Save your private key and mnemonic securely."
            }
            
            logger.info(f"🆕 New wallet created: {account.address}")
            return wallet_info
            
        except Exception as e:
            logger.error(f"❌ Wallet creation failed: {str(e)}")
            raise Exception(f"Wallet creation failed: {str(e)}")
    
    def get_balance(self, address: str) -> int:
        """
        Get balance of an address in wei
        """
        try:
            # Validate address format
            if not self.w3.is_address(address):
                raise ValueError("Invalid Ethereum address format")
            
            checksum_address = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_address)
            
            logger.info(f"💰 Balance check: {address} = {balance_wei} wei")
            return balance_wei
            
        except Exception as e:
            logger.error(f"❌ Balance check failed for {address}: {str(e)}")
            raise Exception(f"Balance check failed: {str(e)}")
    
    def wei_to_ether(self, wei_amount: int) -> float:
        """
        Convert wei to ether
        """
        return self.w3.from_wei(wei_amount, 'ether')
    
    def ether_to_wei(self, ether_amount: float) -> int:
        """
        Convert ether to wei
        """
        return self.w3.to_wei(ether_amount, 'ether')
    
    def send_transaction(self, private_key: str, to_address: str, amount_wei: int, 
                        gas_limit: int = 21000) -> str:
        """
        Send native token (STT) transaction
        Returns: transaction hash
        """
        try:
            # Validate addresses
            if not self.w3.is_address(to_address):
                raise ValueError("Invalid recipient address")
            
            # Create account from private key
            account = Account.from_key(private_key)
            from_address = account.address
            
            # Validate sender has sufficient balance
            balance = self.get_balance(from_address)
            if balance < amount_wei:
                raise ValueError("Insufficient balance for transaction")
            
            # Get current gas price
            gas_price = self.w3.eth.gas_price
            
            # Calculate total cost
            total_cost = amount_wei + (gas_limit * gas_price)
            if balance < total_cost:
                raise ValueError("Insufficient balance for transaction + gas fees")
            
            # Build transaction
            transaction = {
                'to': self.w3.to_checksum_address(to_address),
                'value': amount_wei,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_address),
                'chainId': self.chain_id
            }
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"📤 Transaction sent: {tx_hash.hex()} from {from_address} to {to_address}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"❌ Transaction failed: {str(e)}")
            raise Exception(f"Transaction failed: {str(e)}")
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction status and receipt
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            status = "confirmed" if receipt.status == 1 else "failed"
            block_number = receipt.blockNumber if receipt.blockNumber else "pending"
            
            return {
                "status": status,
                "block_number": block_number,
                "gas_used": receipt.gasUsed,
                "transaction_hash": tx_hash
            }
            
        except Exception as e:
            logger.error(f"❌ Transaction status check failed: {str(e)}")
            return {
                "status": "pending",
                "error": str(e)
            }
    
    async def get_token_price(self, symbol: str = "SOMI") -> Dict[str, Any]:
        """
        Get current token price from CoinGecko API
        """
        try:
            # For testnet, we'll use mock data or fetch from CoinGecko
            if symbol.upper() == "STT":
                # Mock price for testnet token
                return {
                    "usd": 0.15,
                    "idr": 2300,
                    "symbol": "STT",
                    "source": "mock",
                    "last_updated": self._get_current_timestamp()
                }
            
            async with aiohttp.ClientSession() as session:
                # Try to get price from CoinGecko
                coin_id = self._get_coin_gecko_id(symbol)
                if coin_id:
                    url = f"{self.coingecko_api_url}/simple/price"
                    params = {
                        "ids": coin_id,
                        "vs_currencies": "usd,idr",
                        "include_last_updated_at": "true"
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if coin_id in data:
                                return {
                                    "usd": data[coin_id]["usd"],
                                    "idr": data[coin_id]["idr"],
                                    "symbol": symbol.upper(),
                                    "source": "coingecko",
                                    "last_updated": data[coin_id].get("last_updated_at")
                                }
                
                # Fallback to mock data
                return await self._get_mock_price(symbol)
                
        except Exception as e:
            logger.error(f"❌ Price fetch failed for {symbol}: {str(e)}")
            return await self._get_mock_price(symbol)
    
    def _get_coin_gecko_id(self, symbol: str) -> Optional[str]:
        """
        Map symbol to CoinGecko coin ID
        """
        coin_mapping = {
            "SOMI": "somnia",  # This would need to be updated when SOMI is listed
            "ETH": "ethereum",
            "BTC": "bitcoin",
            "BNB": "binancecoin"
        }
        return coin_mapping.get(symbol.upper())
    
    async def _get_mock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get mock price data for development
        """
        mock_prices = {
            "SOMI": {"usd": 0.25, "idr": 3850},
            "STT": {"usd": 0.15, "idr": 2300},
            "ETH": {"usd": 3500, "idr": 53900000},
        }
        
        base_price = mock_prices.get(symbol.upper(), {"usd": 1.0, "idr": 15400})
        
        return {
            "usd": base_price["usd"],
            "idr": base_price["idr"],
            "symbol": symbol.upper(),
            "source": "mock",
            "last_updated": self._get_current_timestamp()
        }
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Convert between fiat and crypto currencies
        """
        try:
            from_upper = from_currency.upper()
            to_upper = to_currency.upper()
            
            # Get conversion rates
            if from_upper in ["USD", "IDR"] and to_upper in ["SOMI", "STT"]:
                # Fiat to crypto
                price_data = await self.get_token_price(to_upper)
                fiat_rate = price_data["idr"] if from_upper == "IDR" else price_data["usd"]
                crypto_amount = amount / fiat_rate
                
                return {
                    "from_amount": amount,
                    "from_currency": from_upper,
                    "to_amount": crypto_amount,
                    "to_currency": to_upper,
                    "conversion_rate": fiat_rate,
                    "message": f"💱 {amount} {from_upper} = {crypto_amount:.6f} {to_upper}"
                }
            
            elif from_upper in ["SOMI", "STT"] and to_upper in ["USD", "IDR"]:
                # Crypto to fiat
                price_data = await self.get_token_price(from_upper)
                fiat_amount_idr = amount * price_data["idr"]
                fiat_amount_usd = amount * price_data["usd"]
                
                target_amount = fiat_amount_idr if to_upper == "IDR" else fiat_amount_usd
                target_currency = "IDR" if to_upper == "IDR" else "USD"
                
                return {
                    "from_amount": amount,
                    "from_currency": from_upper,
                    "to_amount": target_amount,
                    "to_currency": target_currency,
                    "conversion_rate": price_data["idr"] if to_upper == "IDR" else price_data["usd"],
                    "message": f"💱 {amount} {from_upper} = {target_amount:,.2f} {target_currency}"
                }
            
            else:
                raise ValueError(f"Unsupported conversion: {from_currency} to {to_currency}")
                
        except Exception as e:
            logger.error(f"❌ Currency conversion failed: {str(e)}")
            raise Exception(f"Currency conversion failed: {str(e)}")
    
    async def get_gas_price(self) -> Dict[str, Any]:
        """
        Get current gas price information
        """
        try:
            gas_price = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
            
            return {
                "gas_price_wei": gas_price,
                "gas_price_gwei": float(gas_price_gwei),
                "estimated_tx_cost_usd": float(gas_price_gwei) * 0.01,  # Rough estimate
                "message": f"⛽ Current gas price: {gas_price_gwei:.2f} Gwei"
            }
        except Exception as e:
            logger.error(f"❌ Gas price check failed: {str(e)}")
            return {
                "gas_price_gwei": 10.0,  # Fallback
                "message": "Using default gas price"
            }
    
    def validate_address(self, address: str) -> bool:
        """
        Validate Ethereum address format
        """
        return self.w3.is_address(address)
    
    def get_checksum_address(self, address: str) -> str:
        """
        Get checksummed version of address
        """
        return self.w3.to_checksum_address(address)
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get Somnia network information
        """
        try:
            block_number = self.w3.eth.block_number
            is_connected = self.w3.is_connected()
            
            return {
                "network": "Somnia Testnet",
                "chain_id": self.chain_id,
                "symbol": self.symbol,
                "block_number": block_number,
                "is_connected": is_connected,
                "rpc_url": self.rpc_url
            }
        except Exception as e:
            logger.error(f"❌ Network info failed: {str(e)}")
            return {
                "network": "Somnia Testnet",
                "chain_id": self.chain_id,
                "symbol": self.symbol,
                "is_connected": False,
                "error": str(e)
            }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for price updates"""
        from datetime import datetime
        return datetime.now().isoformat()

# Utility functions
def generate_random_private_key() -> str:
    """Generate a cryptographically secure private key"""
    return "0x" + secrets.token_hex(32)

def private_key_to_address(private_key: str) -> str:
    """Convert private key to Ethereum address"""
    account = Account.from_key(private_key)
    return account.address

# Test function
def test_wallet_core():
    """Test wallet core functionality"""
    wallet_core = WalletCore()
    
    print("🧪 Testing Wallet Core...")
    print(f"🔗 Connected: {wallet_core.w3.is_connected()}")
    print(f"📊 Network: {wallet_core.get_network_info()}")
    
    # Test wallet creation
    wallet = wallet_core.create_wallet()
    print(f"🆕 Wallet created: {wallet['address']}")
    
    # Test balance check (should be 0 for new wallet)
    balance = wallet_core.get_balance(wallet['address'])
    print(f"💰 Balance: {wallet_core.wei_to_ether(balance)} {wallet_core.symbol}")
    
    print("✅ Wallet Core test completed!")

if __name__ == "__main__":
    test_wallet_core()