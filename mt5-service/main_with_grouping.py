"""
MT5 Cloud Service - Self-hosted MT5 integration API
Connects to MetaTrader 5 accounts and provides REST API for trade data
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import metatrader5 as mt5
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
    Get trade history from MT5 account - Groups deals into complete trades

    In MT5, a completed trade consists of two deals:
    1. Opening deal (BUY or SELL)
    2. Closing deal (opposite of opening)

    This endpoint groups these deals by order ID to return complete trades.
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

    # Force load account history
    logger.info("📥 Forcing MT5 to load account history...")
    account_info = mt5.account_info()
    if account_info:
        logger.info(f"✅ Account loaded: {account_info.login}, Balance: {account_info.balance}")

    # Try to get deals with broader date range to force history load
    logger.info("🔄 Attempting to retrieve full history...")
    temp_from = datetime(2020, 1, 1)
    temp_to = datetime.now()

    # First request - this forces MT5 to load history
    temp_deals = mt5.history_deals_get(temp_from, temp_to)
    if temp_deals:
        logger.info(f"✅ History loaded successfully: {len(temp_deals)} total deals found")
    else:
        logger.warning("⚠️ No history found even after force load attempt")

    # Calculate actual date range for requested period
    from_date = datetime.now() - timedelta(days=request.days)
    to_date = datetime.now()

    logger.info(f"📅 Fetching deals from {from_date} to {to_date}")

    # Get history deals for requested period
    deals = mt5.history_deals_get(from_date, to_date)

    logger.info(f"🔍 Raw deals result: {deals}")
    logger.info(f"🔍 Deals type: {type(deals)}")
    if deals:
        logger.info(f"🔍 Total deals in period: {len(deals)}")

    if deals is None or len(deals) == 0:
        logger.warning("No deals found in requested period")
        return {
            "success": True,
            "trades": [],
            "count": 0,
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat()
        }

    # Group deals by order ID to form complete trades
    orders_map = defaultdict(list)

    for deal in deals:
        # Only process BUY/SELL deals, skip deposits/withdrawals
        if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
            orders_map[deal.order].append(deal)

    logger.info(f"📦 Grouped {len(deals)} deals into {len(orders_map)} orders")

    # Convert grouped deals into complete trades
    trades = []
    for order_id, order_deals in orders_map.items():
        # Sort deals by time (entry first, exit last)
        order_deals.sort(key=lambda d: d.time)

        if len(order_deals) < 2:
            # Incomplete trade (only entry, no exit yet) - skip for now
            logger.debug(f"⏭️ Skipping incomplete order {order_id} with {len(order_deals)} deals")
            continue

        # First deal is entry, last deal is exit
        entry_deal = order_deals[0]
        exit_deal = order_deals[-1]

        # Calculate total P&L from all deals in this order
        total_profit = sum(d.profit for d in order_deals)
        total_commission = sum(d.commission for d in order_deals)
        total_swap = sum(d.swap for d in order_deals)

        # Determine trade direction based on entry deal
        trade_type = "buy" if entry_deal.type == mt5.DEAL_TYPE_BUY else "sell"

        trades.append({
            "ticket": entry_deal.ticket,  # Use entry deal ticket as trade ID
            "order": order_id,
            "symbol": entry_deal.symbol,
            "type": trade_type,
            "volume": entry_deal.volume,
            "entry_price": entry_deal.price,
            "entry_time": datetime.fromtimestamp(entry_deal.time).isoformat(),
            "exit_price": exit_deal.price,
            "exit_time": datetime.fromtimestamp(exit_deal.time).isoformat(),
            "profit": total_profit,
            "commission": total_commission,
            "swap": total_swap,
            "comment": entry_deal.comment or exit_deal.comment or ""
        })

    logger.info(f"✅ Found {len(trades)} complete trades from {len(deals)} deals")

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
