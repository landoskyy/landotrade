"""
Secure version of HyperLiquid MCP Server with API authentication
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from fastmcp import FastMCP
from fastmcp.server import Server
from dotenv import load_dotenv
import json
from services.hyperliquid_services import HyperLiquidService
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hyperliquid_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Key authentication
API_KEY = os.getenv("API_KEY", "")
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Check API key if authentication is required
        if REQUIRE_AUTH and API_KEY:
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            if api_key != API_KEY:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Unauthorized - Invalid API Key"}
                )
        
        response = await call_next(request)
        return response

# Initialize FastMCP server
mcp = FastMCP(
    "HyperLiquid Trading MCP Server",
    version="1.0.0",
    description="Secure MCP server for HyperLiquid trading with API authentication"
)

# Rate limiting storage
from collections import defaultdict
from datetime import datetime, timedelta

rate_limit_storage = defaultdict(list)
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit"""
    if not REQUIRE_AUTH:
        return True
    
    now = datetime.now()
    minute_ago = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    # Clean old requests
    rate_limit_storage[client_id] = [
        req_time for req_time in rate_limit_storage[client_id]
        if req_time > minute_ago
    ]
    
    # Check limit
    if len(rate_limit_storage[client_id]) >= RATE_LIMIT:
        return False
    
    # Add current request
    rate_limit_storage[client_id].append(now)
    return True

# Initialize HyperLiquid service
def init_service():
    """Initialize HyperLiquid service with configuration"""
    # Check for config file first
    config_file = os.getenv("CONFIG_FILE", "config.json")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            private_key = config.get("private_key")
            account_address = config.get("account_address")
            is_testnet = config.get("testnet", False)
    else:
        # Use environment variables
        private_key = os.getenv("HYPERLIQUID_PRIVATE_KEY")
        account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")
        is_testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"
    
    if not private_key:
        raise ValueError("HYPERLIQUID_PRIVATE_KEY is required")
    
    return HyperLiquidService(
        private_key=private_key,
        account_address=account_address,
        is_testnet=is_testnet
    )

# Global service instance
service = None

@mcp.tool()
async def get_account_balance():
    """Get current account balance and buying power"""
    if not check_rate_limit("default"):
        return {"error": "Rate limit exceeded"}
    return await service.get_account_balance()

@mcp.tool()
async def get_open_positions():
    """Get all open positions with current PnL"""
    if not check_rate_limit("default"):
        return {"error": "Rate limit exceeded"}
    return await service.get_open_positions()

@mcp.tool()
async def get_open_orders():
    """Get all open orders"""
    if not check_rate_limit("default"):
        return {"error": "Rate limit exceeded"}
    return await service.get_open_orders()

@mcp.tool()
async def market_open_position(
    symbol: str,
    side: str,
    size_in_dollars: float,
    leverage: Optional[int] = None,
    reduce_only: bool = False,
    slippage_tolerance: float = 0.05
):
    """
    Open a market position (optimized for opening new positions)
    
    Args:
        symbol: Trading symbol (e.g., 'BTC', 'ETH')
        side: 'buy' or 'sell'
        size_in_dollars: Position size in USD
        leverage: Optional leverage (1-100)
        reduce_only: If True, only reduces existing position
        slippage_tolerance: Max acceptable slippage (default 5%)
    """
    if not check_rate_limit("default"):
        return {"error": "Rate limit exceeded"}
    return await service.market_open_position(
        symbol, side, size_in_dollars, leverage, reduce_only, slippage_tolerance
    )

# Add remaining tools with rate limiting...
# (Copy all other tool definitions from original main.py, adding rate limit checks)

# Health check endpoint
@mcp.route("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "service": "hyperliquid-mcp",
        "auth_required": REQUIRE_AUTH,
        "rate_limit": f"{RATE_LIMIT} requests per minute" if REQUIRE_AUTH else "unlimited"
    }

# CORS configuration for browser access
@mcp.route("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "HyperLiquid MCP Server",
        "version": "1.0.0",
        "auth": "Use X-API-Key header or api_key query parameter" if REQUIRE_AUTH else "No authentication required",
        "endpoints": {
            "/health": "Health check",
            "/mcp": "MCP protocol endpoint"
        },
        "documentation": "https://github.com/landoskyy/landotrade"
    }

async def main():
    """Main entry point"""
    global service
    
    try:
        # Initialize service
        service = init_service()
        logger.info("HyperLiquid service initialized successfully")
        
        # Check if running in stdio mode
        if len(sys.argv) > 1 and sys.argv[1] == "stdio":
            logger.info("Running in stdio mode")
            server = Server(mcp)
            await server.run()
        else:
            # Run HTTP server
            port = int(os.getenv("PORT", "8080"))
            host = os.getenv("HOST", "0.0.0.0")
            
            logger.info(f"Starting HTTP server on {host}:{port}")
            if REQUIRE_AUTH:
                logger.info("API authentication is ENABLED")
                logger.info(f"Rate limit: {RATE_LIMIT} requests per minute")
            else:
                logger.info("API authentication is DISABLED (not recommended for production)")
            
            # Add authentication middleware
            app = mcp.get_app()
            app.add_middleware(AuthMiddleware)
            
            # Run server
            import uvicorn
            await uvicorn.Server(
                uvicorn.Config(
                    app,
                    host=host,
                    port=port,
                    log_level="info"
                )
            ).serve()
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())