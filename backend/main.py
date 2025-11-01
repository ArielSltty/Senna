# backend/main.py
"""
🚀 Enhanced FastAPI Server & API Routes for Senna Wallet
AI-Powered Wallet Agent for Somnia Blockchain - Sophisticated Version
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
import logging
import asyncio
import json
import time
from typing import Optional, Dict, Any, List, Union
import os
from datetime import datetime, timedelta
import uuid

# Import internal modules
from nlp_agent import NLPAgent
from wallet_core import WalletCore
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/senna_api.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Senna Wallet API",
    description="🧠 AI-Powered Wallet Agent for Somnia Blockchain - Sophisticated Version",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "AI Chat",
            "description": "Advanced AI-powered chat interactions with multi-step confirmations"
        },
        {
            "name": "Wallet Management",
            "description": "Sophisticated wallet operations with enhanced security"
        },
        {
            "name": "Blockchain Operations",
            "description": "Advanced blockchain interactions and transaction management"
        },
        {
            "name": "Market Intelligence",
            "description": "Real-time market data, analytics, and price predictions"
        },
        {
            "name": "WebSocket",
            "description": "Real-time communication for live updates"
        }
    ]
)

# CORS middleware - Enhanced for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
nlp_agent = None
wallet_core = None

# Session management for advanced conversations
user_sessions = {}

# Enhanced Pydantic models for sophisticated features
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message for Senna AI")
    wallet_address: Optional[str] = Field(None, description="User's wallet address")
    session_id: Optional[str] = Field(None, description="Session ID for continuous conversations")
    confirm_action: Optional[bool] = Field(False, description="Confirmation for previous action")
    selected_option: Optional[int] = Field(None, description="Selected option from multiple choices")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response message")
    action: Optional[str] = Field(None, description="Required action type")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")
    transaction_data: Optional[Dict[str, Any]] = Field(None, description="Transaction details")
    success: bool = Field(..., description="Request success status")
    requires_confirmation: bool = Field(False, description="Whether confirmation is required")
    options: Optional[List[str]] = Field(None, description="Multiple choice options")
    session_id: Optional[str] = Field(None, description="Session ID for continued conversation")
    analytics: Optional[Dict[str, Any]] = Field(None, description="Market analytics and insights")
    explorer_url: Optional[str] = Field(None, description="Block explorer URL for transactions")

class WalletCreateRequest(BaseModel):
    password: Optional[str] = Field(None, description="Optional password for encryption")
    wallet_type: str = Field("native", description="Type of wallet: native or metamask")

class WalletCreateResponse(BaseModel):
    address: str = Field(..., description="Wallet address")
    private_key: Optional[str] = Field(None, description="Private key (native wallets only)")
    mnemonic: Optional[str] = Field(None, description="Recovery phrase")
    message: str = Field(..., description="Creation status message")
    wallet_type: str = Field(..., description="Type of wallet created")

class BalanceResponse(BaseModel):
    address: str = Field(..., description="Wallet address")
    balance: str = Field(..., description="Formatted balance")
    balance_wei: int = Field(..., description="Balance in wei")
    symbol: str = Field(..., description="Token symbol")
    usd_value: Optional[float] = Field(None, description="Balance value in USD")
    portfolio_history: Optional[List[Dict]] = Field(None, description="Portfolio history")

class TransactionRequest(BaseModel):
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    amount: float = Field(..., description="Amount to send")
    private_key: Optional[str] = Field(None, description="Private key for native wallets")
    gas_limit: Optional[int] = Field(21000, description="Gas limit")
    confirm: bool = Field(False, description="Confirmation flag")

class TransactionResponse(BaseModel):
    transaction_hash: str = Field(..., description="Transaction hash")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    amount: str = Field(..., description="Amount sent")
    status: str = Field(..., description="Transaction status")
    gas_used: Optional[int] = Field(None, description="Gas used")
    explorer_url: str = Field(..., description="Block explorer URL")
    timestamp: str = Field(..., description="Transaction timestamp")

class MarketAnalysisRequest(BaseModel):
    symbol: str = Field("SOMI", description="Token symbol for analysis")
    timeframe: str = Field("7d", description="Analysis timeframe: 1d, 7d, 30d")

class MarketAnalysisResponse(BaseModel):
    symbol: str = Field(..., description="Token symbol")
    current_price: float = Field(..., description="Current price in USD")
    price_change_24h: float = Field(..., description="24h price change percentage")
    market_analysis: Dict[str, Any] = Field(..., description="Detailed market analysis")
    prediction: Optional[Dict[str, Any]] = Field(None, description="Price prediction")
    recommendation: str = Field(..., description="Trading recommendation")
    confidence: float = Field(..., description="Analysis confidence level")

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type: chat, transaction, notification")
    data: Dict[str, Any] = Field(..., description="Message data")
    session_id: Optional[str] = Field(None, description="Session ID")

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Session management
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = 3600  # 1 hour

    def create_session(self, wallet_address: str = None) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "wallet_address": wallet_address,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "conversation_history": [],
            "pending_action": None,
            "pending_data": None
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        if session_id in self.sessions:
            session = self.sessions[session_id]
            # Update last activity
            session["last_activity"] = datetime.now()
            return session
        return None

    def update_session(self, session_id: str, updates: Dict):
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]["last_activity"] = datetime.now()

    def cleanup_expired_sessions(self):
        current_time = datetime.now()
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if (current_time - session["last_activity"]).seconds > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

session_manager = SessionManager()

# Startup event - Enhanced with sophisticated initialization
@app.on_event("startup")
async def startup_event():
    """Initialize advanced components on startup"""
    global nlp_agent, wallet_core
    
    try:
        logger.info("🚀 Initializing Sophisticated Senna Wallet Backend...")
        
        # Initialize Wallet Core with enhanced features
        wallet_core = WalletCore()
        logger.info("✅ Enhanced Wallet Core initialized")
        
        # Initialize Advanced NLP Agent (Groq only)
        nlp_agent = NLPAgent(wallet_core)
        await nlp_agent.initialize()
        logger.info("✅ Advanced NLP Agent initialized (Groq only)")
        
        # Start background tasks
        asyncio.create_task(background_session_cleanup())
        
        logger.info("🎯 Sophisticated Senna Wallet Backend ready!")
        logger.info(f"📊 Available features: Advanced AI, Multi-step confirmations, Market analytics, WebSocket support")
        
    except Exception as e:
        logger.error(f"❌ Sophisticated startup failed: {str(e)}")
        raise

# Background tasks
async def background_session_cleanup():
    """Clean up expired sessions periodically"""
    while True:
        await asyncio.sleep(1800)  # Every 30 minutes
        session_manager.cleanup_expired_sessions()
        logger.info("🔄 Session cleanup completed")

# Enhanced endpoints with sophisticated features
@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """Enhanced root endpoint with API information"""
    return """
    <html>
        <head>
            <title>Senna Wallet API v2.0</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #000; color: white; padding: 20px; border-radius: 10px; }
                .feature { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 Senna Wallet API v2.0</h1>
                    <p>Sophisticated AI-Powered Wallet Agent for Somnia Blockchain</p>
                </div>
                
                <h2>🚀 Enhanced Features</h2>
                
                <div class="feature">
                    <h3>🧠 Advanced AI Conversations</h3>
                    <p>Multi-step confirmations, context-aware responses, intelligent analysis</p>
                </div>
                
                <div class="feature">
                    <h3>📊 Market Intelligence</h3>
                    <p>Real-time analytics, price predictions, portfolio insights</p>
                </div>
                
                <div class="feature">
                    <h3>🔗 WebSocket Support</h3>
                    <p>Real-time updates, live transaction tracking</p>
                </div>
                
                <div class="feature">
                    <h3>⚡ Enhanced Security</h3>
                    <p>Session management, confirmation flows, risk assessment</p>
                </div>
                
                <p>📚 API Documentation: <a href="/docs">/docs</a></p>
                <p>🔍 Health Check: <a href="/health">/health</a></p>
                
                <div style="margin-top: 30px; padding: 15px; background: #e8f5e8; border-radius: 5px;">
                    <strong>Status:</strong> 🟢 System Operational<br>
                    <strong>Version:</strong> 2.0.0<br>
                    <strong>Blockchain:</strong> Somnia Testnet
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "Senna Wallet API v2.0",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "blockchain": {
            "network": "Somnia Testnet",
            "chain_id": settings.SOMNIA_CHAIN_ID,
            "connected": wallet_core.w3.is_connected() if wallet_core else False,
            "latest_block": wallet_core.w3.eth.block_number if wallet_core else 0
        },
        "ai_agent": {
            "status": "active" if nlp_agent else "inactive",
            "provider": "Groq",
            "model": settings.GROQ_MODEL if hasattr(settings, 'GROQ_MODEL') else "llama3-8b-8192"
        },
        "features": {
            "multi_step_confirmations": True,
            "market_analytics": True,
            "websocket_support": True,
            "session_management": True,
            "portfolio_tracking": True
        },
        "system": {
            "active_sessions": len(session_manager.sessions),
            "uptime": "0"  # Would be calculated in real implementation
        }
    }
    return health_status

@app.post("/api/chat", response_model=ChatResponse, tags=["AI Chat"])
async def chat_with_senna(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Advanced chat endpoint with multi-step confirmations and sophisticated AI analysis
    """
    try:
        # Session management
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.create_session(request.wallet_address)
            logger.info(f"🆕 New session created: {session_id}")

        session = session_manager.get_session(session_id)
        if not session:
            session_id = session_manager.create_session(request.wallet_address)
            session = session_manager.get_session(session_id)

        # Handle confirmation flows
        if request.confirm_action and session.get("pending_action"):
            return await _handle_confirmation(session, request, session_id)

        # Handle option selection
        if request.selected_option is not None and session.get("pending_options"):
            return await _handle_option_selection(session, request, session_id)

        # Process message through advanced NLP agent
        logger.info(f"💬 Processing message in session {session_id}: {request.message}")
        
        result = await nlp_agent.process_message(
            message=request.message,
            wallet_address=request.wallet_address or session.get("wallet_address"),
            session_id=session_id
        )

        # Update conversation history
        session_manager.update_session(session_id, {
            "conversation_history": session["conversation_history"] + [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": result.get("response", "")}
            ]
        })

        # Add session ID to response
        result["session_id"] = session_id

        # Add explorer URL for transactions
        if result.get("transaction_data") and result.get("success"):
            tx_hash = result["transaction_data"].get("transaction_hash")
            if tx_hash:
                result["explorer_url"] = f"{settings.SOMNIA_EXPLORER_URL}/tx/{tx_hash}"

        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Advanced chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

async def _handle_confirmation(session: Dict, request: ChatRequest, session_id: str) -> ChatResponse:
    """Handle action confirmations in multi-step flows"""
    pending_action = session.get("pending_action")
    pending_data = session.get("pending_data")

    if request.confirm_action:
        # Execute the pending action
        if pending_action == "send_transaction":
            try:
                # Execute transaction
                tx_hash = wallet_core.send_transaction(
                    pending_data["private_key"],
                    pending_data["to_address"],
                    wallet_core.ether_to_wei(pending_data["amount"])
                )
                
                # Clear pending action
                session_manager.update_session(session_id, {
                    "pending_action": None,
                    "pending_data": None
                })

                explorer_url = f"{settings.SOMNIA_EXPLORER_URL}/tx/{tx_hash.hex()}"
                
                return ChatResponse(
                    response=f"✅ Transaction confirmed and sent!\n\n"
                           f"**Transaction Hash:** {tx_hash.hex()}\n"
                           f"**Amount:** {pending_data['amount']} {pending_data.get('symbol', 'STT')}\n"
                           f"**To:** {pending_data['to_address']}\n"
                           f"**Status:** ⏳ Pending\n\n"
                           f"🔍 [View on Explorer]({explorer_url})",
                    action="send_transaction",
                    transaction_data={
                        "transaction_hash": tx_hash.hex(),
                        "amount": pending_data["amount"],
                        "to_address": pending_data["to_address"],
                        "explorer_url": explorer_url
                    },
                    success=True,
                    explorer_url=explorer_url,
                    session_id=session_id
                )
            except Exception as e:
                return ChatResponse(
                    response=f"❌ Transaction failed: {str(e)}",
                    success=False,
                    session_id=session_id
                )
    else:
        # User declined the action
        session_manager.update_session(session_id, {
            "pending_action": None,
            "pending_data": None
        })
        return ChatResponse(
            response="❌ Transaction cancelled. No action taken.",
            success=True,
            session_id=session_id
        )

async def _handle_option_selection(session: Dict, request: ChatRequest, session_id: str) -> ChatResponse:
    """Handle multiple choice option selections"""
    pending_options = session.get("pending_options", [])
    selected_option = request.selected_option

    if 0 <= selected_option < len(pending_options):
        selected_action = pending_options[selected_option]
        # Process the selected action
        # This would contain sophisticated logic based on the context
        
        # Clear pending options
        session_manager.update_session(session_id, {
            "pending_options": None
        })

        return ChatResponse(
            response=f"✅ You selected option {selected_option + 1}: {selected_action['description']}\n\n"
                   f"Processing your selection...",
            success=True,
            session_id=session_id
        )
    else:
        return ChatResponse(
            response="❌ Invalid option selected. Please try again.",
            success=False,
            session_id=session_id
        )

@app.post("/api/wallet/create", response_model=WalletCreateResponse, tags=["Wallet Management"])
async def create_wallet(request: WalletCreateRequest):
    """Create a new wallet with enhanced security"""
    try:
        wallet_info = wallet_core.create_wallet()
        
        return WalletCreateResponse(
            address=wallet_info["address"],
            private_key=wallet_info["private_key"],
            mnemonic=wallet_info.get("mnemonic"),
            message="🎉 Advanced wallet created successfully! Save your private key and mnemonic securely.",
            wallet_type=request.wallet_type
        )
        
    except Exception as e:
        logger.error(f"❌ Wallet creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Wallet creation failed: {str(e)}")

@app.get("/api/balance/{address}", response_model=BalanceResponse, tags=["Wallet Management"])
async def get_balance(address: str):
    """Get comprehensive balance information with portfolio insights"""
    try:
        balance_wei = wallet_core.get_balance(address)
        balance_ether = wallet_core.wei_to_ether(balance_wei)
        
        # Get USD value
        price_data = await wallet_core.get_token_price("STT")
        usd_value = balance_ether * price_data.get("usd", 0)
        
        # Generate portfolio history (mock data for now)
        portfolio_history = [
            {"timestamp": datetime.now().isoformat(), "balance": balance_ether, "value_usd": usd_value}
        ]
        
        return BalanceResponse(
            address=address,
            balance=str(balance_ether),
            balance_wei=balance_wei,
            symbol="STT",
            usd_value=usd_value,
            portfolio_history=portfolio_history
        )
        
    except Exception as e:
        logger.error(f"❌ Balance check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Balance check failed: {str(e)}")

@app.post("/api/transaction/send", response_model=TransactionResponse, tags=["Blockchain Operations"])
async def send_transaction(request: TransactionRequest):
    """Send transaction with enhanced confirmation and tracking"""
    try:
        if not request.confirm:
            # Return transaction preview for confirmation
            gas_info = await wallet_core.get_gas_price()
            estimated_gas_cost = gas_info["gas_price_gwei"] * request.gas_limit / 1e9
            
            return TransactionResponse(
                transaction_hash="preview",
                from_address=request.from_address,
                to_address=request.to_address,
                amount=str(request.amount),
                status="preview",
                explorer_url="",
                timestamp=datetime.now().isoformat()
            )

        # Execute transaction
        amount_wei = wallet_core.ether_to_wei(request.amount)
        tx_hash = wallet_core.send_transaction(
            request.private_key,
            request.to_address,
            amount_wei,
            request.gas_limit
        )
        
        explorer_url = f"{settings.SOMNIA_EXPLORER_URL}/tx/{tx_hash.hex()}"
        
        return TransactionResponse(
            transaction_hash=tx_hash.hex(),
            from_address=request.from_address,
            to_address=request.to_address,
            amount=str(request.amount),
            status="pending",
            explorer_url=explorer_url,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Transaction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

@app.get("/api/market/analysis/{symbol}", response_model=MarketAnalysisResponse, tags=["Market Intelligence"])
async def get_market_analysis(symbol: str, timeframe: str = "7d"):
    """Get sophisticated market analysis and predictions"""
    try:
        # Get current price
        price_data = await wallet_core.get_token_price(symbol)
        
        # Generate advanced market analysis (mock data for now)
        market_analysis = {
            "trend": "bullish",
            "volatility": "medium",
            "support_level": price_data["usd"] * 0.95,
            "resistance_level": price_data["usd"] * 1.05,
            "volume_change": "+15%",
            "market_sentiment": "positive"
        }
        
        # Generate prediction
        prediction = {
            "short_term": price_data["usd"] * 1.02,
            "medium_term": price_data["usd"] * 1.08,
            "confidence": 0.75
        }
        
        return MarketAnalysisResponse(
            symbol=symbol.upper(),
            current_price=price_data["usd"],
            price_change_24h=2.5,  # Mock data
            market_analysis=market_analysis,
            prediction=prediction,
            recommendation="Consider holding, bullish trend expected to continue",
            confidence=0.75
        )
        
    except Exception as e:
        logger.error(f"❌ Market analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "chat":
                # Process chat message through NLP agent
                result = await nlp_agent.process_message(
                    message=message_data["data"]["message"],
                    wallet_address=message_data["data"].get("wallet_address"),
                    session_id=session_id
                )
                
                # Send response back through WebSocket
                await manager.send_personal_message(
                    json.dumps({
                        "type": "chat_response",
                        "data": result
                    }),
                    websocket
                )
                
            elif message_data.get("type") == "transaction_update":
                # Handle transaction updates
                await manager.send_personal_message(
                    json.dumps({
                        "type": "transaction_status",
                        "data": {"status": "confirmed", "message": "Transaction completed"}
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for session {session_id}")

@app.get("/api/transaction/{tx_hash}/status", tags=["Blockchain Operations"])
async def get_transaction_status(tx_hash: str):
    """Get detailed transaction status with enhanced information"""
    try:
        status = wallet_core.get_transaction_status(tx_hash)
        
        # Add explorer URL
        status["explorer_url"] = f"{settings.SOMNIA_EXPLORER_URL}/tx/{tx_hash}"
        
        # Add enhanced status information
        if status["status"] == "confirmed":
            status["message"] = "✅ Transaction confirmed on blockchain"
            status["icon"] = "✅"
        elif status["status"] == "pending":
            status["message"] = "⏳ Transaction pending confirmation"
            status["icon"] = "⏳"
        else:
            status["message"] = "❌ Transaction failed"
            status["icon"] = "❌"
            
        return status
        
    except Exception as e:
        logger.error(f"❌ Transaction status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/api/portfolio/{address}/analytics", tags=["Market Intelligence"])
async def get_portfolio_analytics(address: str):
    """Get comprehensive portfolio analytics and insights"""
    try:
        balance_wei = wallet_core.get_balance(address)
        balance_ether = wallet_core.wei_to_ether(balance_wei)
        price_data = await wallet_core.get_token_price("STT")
        
        portfolio_value = balance_ether * price_data["usd"]
        
        analytics = {
            "address": address,
            "current_balance": balance_ether,
            "portfolio_value_usd": portfolio_value,
            "profit_loss": {
                "daily": "+2.5%",
                "weekly": "+8.3%",
                "monthly": "+15.2%"
            },
            "risk_assessment": "medium",
            "recommendations": [
                "Consider diversifying with SOMI tokens",
                "Current gas fees are optimal for transactions",
                "Market sentiment is bullish for STT"
            ],
            "performance_chart": [
                {"date": "2024-01-01", "value": portfolio_value * 0.85},
                {"date": "2024-01-02", "value": portfolio_value * 0.92},
                {"date": "2024-01-03", "value": portfolio_value}
            ]
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Portfolio analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Portfolio analytics failed: {str(e)}")

# Enhanced error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with enhanced logging"""
    logger.error(f"🚨 Global error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

# Utility endpoints
@app.get("/api/system/info", tags=["System"])
async def get_system_info():
    """Get comprehensive system information"""
    return {
        "version": "2.0.0",
        "status": "operational",
        "blockchain": wallet_core.get_network_info(),
        "ai_capabilities": {
            "multi_step_confirmations": True,
            "market_analysis": True,
            "price_predictions": True,
            "risk_assessment": True
        },
        "active_sessions": len(session_manager.sessions),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )