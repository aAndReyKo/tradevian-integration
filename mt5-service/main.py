"""
MT5 Cloud Service - Self-hosted MT5 integration API
Connects to MetaTrader 5 accounts and provides REST API for trade data
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MT5 Cloud Service",
    description="Self-hosted MetaTrader 5 integration API for Tradevian",
    version="1.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key authentication
API_KEY = os.getenv('API_KEY', '')

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if not API_KEY:
        logger.error("API_KEY not set in environment variables!")
        raise HTTPException(status_code=500, detail="Server configuration error")

    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return x_api_key

# Pydantic models
class MT5Credentials(BaseModel):
    """MT5 login credentials"""
    login: int
    password: str
    server: str

class MT5Account(BaseModel):
    """MT5 account information"""
    login: int
    server: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    currency: str
    leverage: int
    profit: float
    company: str

class MT5Trade(BaseModel):
    """MT5 trade/deal information"""
    ticket: int
    order: int
    symbol: str
    type: str
    volume: float
    price: float
    time: str
    profit: float
    commission: float
    swap: float
    comment: str

class TradeHistoryRequest(BaseModel):
    """Request for trade history"""
    login: int
    password: str
    server: str
    days: int = 30

# Active connections storage
active_connections: Dict[str, dict] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize MT5 on startup"""
    if not mt5.initialize():
        logger.error("❌ MT5 initialization failed")
    else:
        logger.info("✅ MT5 Cloud Service started successfully")
        logger.info(f"📡 Listening on {os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', 8000)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    mt5.shutdown()
    logger.info("🛑 MT5 Cloud Service stopped")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MT5 Cloud Service",
        "version": "1.0.0",
        "status": "running",
        "description": "Self-hosted MetaTrader 5 integration API"
    }

@app.get("/status")
async def status():
    """Health check endpoint"""
    mt5_initialized = mt5.initialize()

    return {
        "status": "ok" if mt5_initialized else "error",
        "message": "MT5 Cloud Service is running",
        "mt5_initialized": mt5_initialized,
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/mt5/connect")
async def connect_mt5(
    credentials: MT5Credentials,
    api_key: str = Depends(verify_api_key)
):
    """
    Connect to MT5 account

    This establishes a connection to the MT5 server and retrieves account information.
    The connection is stored for future requests.
    """
    logger.info(f"🔌 Connection request: {credentials.login}@{credentials.server}")

    # Initialize MT5 if not already
    if not mt5.initialize():
        logger.error("MT5 initialization failed")
        raise HTTPException(
            status_code=500,
            detail="MT5 initialization failed. Check if MT5 Terminal is running."
        )

    # Attempt login
    authorized = mt5.login(
        login=credentials.login,
        password=credentials.password,
        server=credentials.server
    )

    if not authorized:
        error = mt5.last_error()
        logger.error(f"❌ MT5 login failed for {credentials.login}: {error}")
        raise HTTPException(
            status_code=401,
            detail=f"MT5 login failed: {error[1] if error else 'Unknown error'}"
        )

    # Get account info
    account_info = mt5.account_info()
    if account_info is None:
        logger.error("Failed to retrieve account info")
        raise HTTPException(status_code=500, detail="Failed to get account info")

    # Store connection
    connection_id = f"{credentials.login}@{credentials.server}"
    active_connections[connection_id] = {
        "login": credentials.login,
        "server": credentials.server,
        "connected_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    }

    logger.info(f"✅ Connected successfully: {connection_id}")

    return {
        "success": True,
        "connection_id": connection_id,
        "account": {
            "login": account_info.login,
            "server": account_info.server,
            "balance": account_info.balance,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "free_margin": account_info.margin_free,
            "margin_level": account_info.margin_level,
            "currency": account_info.currency,
            "leverage": account_info.leverage,
            "profit": account_info.profit,
            "company": account_info.company
        }
    }

@app.post("/mt5/account")
async def get_account_info(
    credentials: MT5Credentials,
    api_key: str = Depends(verify_api_key)
):
    """Get current account information without storing connection"""
    logger.info(f"📊 Account info request: {credentials.login}@{credentials.server}")

    if not mt5.initialize():
        raise HTTPException(status_code=500, detail="MT5 initialization failed")

    authorized = mt5.login(
        login=credentials.login,
        password=credentials.password,
        server=credentials.server
    )

    if not authorized:
        error = mt5.last_error()
        raise HTTPException(status_code=401, detail=f"MT5 login failed: {error}")

    account_info = mt5.account_info()
    if account_info is None:
        raise HTTPException(status_code=500, detail="Failed to get account info")

    return {
        "success": True,
        "account": {
            "login": account_info.login,
            "server": account_info.server,
            "balance": account_info.balance,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "free_margin": account_info.margin_free,
            "margin_level": account_info.margin_level,
            "currency": account_info.currency,
            "leverage": account_info.leverage,
            "profit": account_info.profit,
            "company": account_info.company
        }
    }

@app.post("/mt5/trades")
async def get_trade_history(
    request: TradeHistoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Get trade history from MT5 account

    Retrieves closed trades/deals from the last N days (default 30).
    Only includes BUY/SELL deals, excluding deposits, withdrawals, etc.
    """
    logger.info(f"📊 Trade history request: {request.login}@{request.server} (last {request.days} days)")

    # Initialize and login
    if not mt5.initialize():
        raise HTTPException(status_code=500, detail="MT5 initialization failed")

    authorized = mt5.login(
        login=request.login,
        password=request.password,
        server=request.server
    )

    if not authorized:
        error = mt5.last_error()
        logger.error(f"Login failed: {error}")
        raise HTTPException(status_code=401, detail=f"MT5 login failed: {error}")

    # Calculate date range
    from_date = datetime.now() - timedelta(days=request.days)
    to_date = datetime.now()

    logger.info(f"Fetching deals from {from_date} to {to_date}")

    # Get history deals
    deals = mt5.history_deals_get(from_date, to_date)

    if deals is None:
        logger.warning("No deals found in history")
        return {
            "success": True,
            "trades": [],
            "count": 0,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat()
        }

    # Filter and format deals (only BUY/SELL, not deposits/withdrawals)
    trades = []
    for deal in deals:
        if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
            trades.append({
                "ticket": deal.ticket,
                "order": deal.order,
                "symbol": deal.symbol,
                "type": "buy" if deal.type == mt5.DEAL_TYPE_BUY else "sell",
                "volume": deal.volume,
                "price": deal.price,
                "time": datetime.fromtimestamp(deal.time).isoformat(),
                "profit": deal.profit,
                "commission": deal.commission,
                "swap": deal.swap,
                "comment": deal.comment
            })

    logger.info(f"✅ Found {len(trades)} trades out of {len(deals)} total deals")

    return {
        "success": True,
        "trades": trades,
        "count": len(trades),
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat()
    }

@app.post("/mt5/positions")
async def get_open_positions(
    credentials: MT5Credentials,
    api_key: str = Depends(verify_api_key)
):
    """Get currently open positions"""
    logger.info(f"📈 Open positions request: {credentials.login}@{credentials.server}")

    if not mt5.initialize():
        raise HTTPException(status_code=500, detail="MT5 initialization failed")

    authorized = mt5.login(
        login=credentials.login,
        password=credentials.password,
        server=credentials.server
    )

    if not authorized:
        error = mt5.last_error()
        raise HTTPException(status_code=401, detail=f"MT5 login failed: {error}")

    positions = mt5.positions_get()

    if positions is None:
        return {"success": True, "positions": [], "count": 0}

    formatted_positions = []
    for pos in positions:
        formatted_positions.append({
            "ticket": pos.ticket,
            "symbol": pos.symbol,
            "type": "buy" if pos.type == mt5.POSITION_TYPE_BUY else "sell",
            "volume": pos.volume,
            "price_open": pos.price_open,
            "price_current": pos.price_current,
            "profit": pos.profit,
            "swap": pos.swap,
            "time": datetime.fromtimestamp(pos.time).isoformat(),
            "comment": pos.comment
        })

    logger.info(f"✅ Found {len(formatted_positions)} open positions")

    return {
        "success": True,
        "positions": formatted_positions,
        "count": len(formatted_positions)
    }

@app.post("/mt5/disconnect")
async def disconnect_mt5(
    connection_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Disconnect from MT5 and remove from active connections"""
    if connection_id in active_connections:
        del active_connections[connection_id]
        logger.info(f"🔌 Disconnected: {connection_id}")
        return {"success": True, "message": f"Disconnected {connection_id}"}

    return {"success": False, "message": "Connection not found"}

@app.get("/mt5/connections")
async def list_connections(api_key: str = Depends(verify_api_key)):
    """List all active MT5 connections"""
    return {
        "success": True,
        "connections": active_connections,
        "count": len(active_connections)
    }

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')

    logger.info(f"🚀 Starting MT5 Cloud Service on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.getenv('LOG_LEVEL', 'info').lower()
    )
