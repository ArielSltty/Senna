# backend/main.py
"""
🚀 FastAPI Server & API Routes for Senna Wallet
AI-Powered Wallet Agent for Somnia Blockchain
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import logging
from typing import Optional, Dict, Any
import os

# Import internal modules
from nlp_agent import NLPAgent
from wallet_core import WalletCore
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Senna Wallet API",
    description="AI-Powered Wallet Agent for Somnia Blockchain",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
nlp_agent = None
wallet_core = None

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    wallet_address: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    transaction_data: Optional[Dict[str, Any]] = None
    success: bool

class WalletCreateRequest(BaseModel):
    password: Optional[str] = None  # For encrypted wallet creation

class WalletCreateResponse(BaseModel):
    address: str
    private_key: str
    mnemonic: Optional[str] = None
    message: str

class BalanceResponse(BaseModel):
    address: str
    balance: str
    balance_wei: int
    symbol: str

class TransactionRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float
    private_key: str

class TransactionResponse(BaseModel):
    transaction_hash: str
    from_address: str
    to_address: str
    amount: str
    status: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize NLP agent and Wallet core on startup"""
    global nlp_agent, wallet_core
    try:
        logger.info("🚀 Initializing Senna Wallet Backend...")
        
        # Initialize Wallet Core
        wallet_core = WalletCore()
        logger.info("✅ Wallet Core initialized")
        
        # Initialize NLP Agent
        nlp_agent = NLPAgent(wallet_core)
        await nlp_agent.initialize()  # ⬅️ TAMBAH INI!
        logger.info("✅ NLP Agent initialized")
        
        logger.info("🎯 Senna Wallet Backend ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "🧠 Senna Wallet API is running!",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Senna Wallet API",
        "blockchain": "Somnia Testnet",
        "chain_id": 50312
    }

# Main chat endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_senna(request: ChatRequest):
    """
    Main endpoint for chatting with Senna AI agent
    """
    try:
        if not nlp_agent:
            raise HTTPException(status_code=503, detail="NLP agent not initialized")
        
        logger.info(f"💬 Received message: {request.message}")
        
        # Process message through NLP agent
        result = await nlp_agent.process_message(
            message=request.message,
            wallet_address=request.wallet_address,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=result.get("response", "I couldn't process that request."),
            action=result.get("action"),
            data=result.get("data"),
            transaction_data=result.get("transaction_data"),
            success=result.get("success", False)
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# Wallet management endpoints
@app.post("/api/wallet/create", response_model=WalletCreateResponse)
async def create_wallet(request: WalletCreateRequest):
    """Create a new wallet"""
    try:
        if not wallet_core:
            raise HTTPException(status_code=503, detail="Wallet core not initialized")
        
        wallet_info = wallet_core.create_wallet()
        
        return WalletCreateResponse(
            address=wallet_info["address"],
            private_key=wallet_info["private_key"],
            mnemonic=wallet_info.get("mnemonic"),
            message="Wallet created successfully. Save your private key securely!"
        )
        
    except Exception as e:
        logger.error(f"❌ Wallet creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Wallet creation failed: {str(e)}")

@app.get("/api/balance/{address}", response_model=BalanceResponse)
async def get_balance(address: str):
    """Get balance for a wallet address"""
    try:
        if not wallet_core:
            raise HTTPException(status_code=503, detail="Wallet core not initialized")
        
        balance_wei = wallet_core.get_balance(address)
        balance_ether = wallet_core.wei_to_ether(balance_wei)
        
        return BalanceResponse(
            address=address,
            balance=str(balance_ether),
            balance_wei=balance_wei,
            symbol="STT"  # Somnia Testnet Token
        )
        
    except Exception as e:
        logger.error(f"❌ Balance check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Balance check failed: {str(e)}")

@app.post("/api/transaction/send", response_model=TransactionResponse)
async def send_transaction(request: TransactionRequest):
    """Send a transaction"""
    try:
        if not wallet_core:
            raise HTTPException(status_code=503, detail="Wallet core not initialized")
        
        # Convert amount to wei
        amount_wei = wallet_core.ether_to_wei(request.amount)
        
        tx_hash = wallet_core.send_transaction(
            request.private_key,
            request.to_address,
            amount_wei
        )
        
        return TransactionResponse(
            transaction_hash=tx_hash.hex(),
            from_address=request.from_address,
            to_address=request.to_address,
            amount=str(request.amount),
            status="pending"
        )
        
    except Exception as e:
        logger.error(f"❌ Transaction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

# Price and market data endpoints
@app.get("/api/price/somi")
async def get_somi_price():
    """Get current SOMI/STT price"""
    try:
        # This will be implemented in wallet_core.py
        price_data = await wallet_core.get_token_price()
        return price_data
    except Exception as e:
        logger.error(f"❌ Price fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Price fetch failed: {str(e)}")

@app.get("/api/convert/{amount}/{from_currency}/{to_currency}")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Convert between fiat and crypto"""
    try:
        conversion_data = await wallet_core.convert_currency(amount, from_currency, to_currency)
        return conversion_data
    except Exception as e:
        logger.error(f"❌ Currency conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Currency conversion failed: {str(e)}")

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"🚨 Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )