"""
GateAgent - Trading agent for Gate.io cryptocurrency exchange
Connects to Gate.io API for real-time crypto trading
"""

import asyncio
import json
import os
import sys
import time
import hmac
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from prompts.gate_prompt import STOP_SIGNAL, get_gate_system_prompt
from tools.general_tools import extract_conversation, extract_tool_messages, get_config_value, write_config_value

load_dotenv()


class GateAgent:
    """
    Gate.io Trading Agent
    
    Features:
    1. Real-time connection to Gate.io API
    2. Crypto trading (BTC, ETH, USDT pairs)
    3. Portfolio management
    4. AI-driven trading decisions
    """
    
    def __init__(
        self,
        signature: str,
        basemodel: str,
        api_key: str = None,
        api_secret: str = None,
        log_path: str = "./data/gate_agent_data",
        max_steps: int = 30,
        max_retries: int = 3,
        base_delay: float = 1.0,
        initial_cash: float = 1000.0,
        openai_base_url: str = None,
        openai_api_key: str = None,
    ):
        """
        Initialize Gate.io Trading Agent
        
        Args:
            signature: Agent identifier
            basemodel: AI model name
            api_key: Gate.io API key
            api_secret: Gate.io API secret
            log_path: Log directory path
            max_steps: Max reasoning steps
            max_retries: Max retry attempts
            base_delay: Delay between operations
            initial_cash: Initial USDT balance
            openai_base_url: OpenAI API base URL
            openai_api_key: OpenAI API key
        """
        self.signature = signature
        self.basemodel = basemodel
        self.log_path = Path(log_path)
        self.max_steps = max_steps
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.initial_cash = initial_cash
        
        # Gate.io API credentials
        self.api_key = api_key or os.getenv("GATE_API_KEY")
        self.api_secret = api_secret or os.getenv("GATE_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ Gate.io API credentials required! Set GATE_API_KEY and GATE_API_SECRET")
        
        # Gate.io API endpoints
        self.base_url = "https://api.gateio.ws/api/v4"
        
        # OpenAI configuration
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_API_BASE")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Trading pairs
        self.trading_pairs = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "BNB_USDT"]
        
        # Initialize components
        self.mcp_client = None
        self.llm = None
        self.agent = None
        
        # Create log directories
        self._setup_directories()
        
        print(f"✅ GateAgent initialized: {signature}")
        print(f"💰 Initial balance: ${initial_cash} USDT")
        print(f"📊 Trading pairs: {', '.join(self.trading_pairs)}")
    
    def _setup_directories(self):
        """Create necessary directories"""
        dirs = [
            self.log_path / self.signature / "position",
            self.log_path / self.signature / "log",
            self.log_path / self.signature / "trades"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _generate_signature(self, method: str, url: str, query_string: str = "", payload_string: str = ""):
        """Generate Gate.io API signature"""
        timestamp = str(int(time.time()))
        
        # Create signature string
        sign_string = f"{method}\n{url}\n{query_string}\n{hashlib.sha512(payload_string.encode()).hexdigest()}\n{timestamp}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.api_secret.encode(),
            sign_string.encode(),
            hashlib.sha512
        ).hexdigest()
        
        return {
            "KEY": self.api_key,
            "Timestamp": timestamp,
            "SIGN": signature
        }
    
    def _api_request(self, method: str, endpoint: str, params: dict = None, data: dict = None):
        """Make authenticated Gate.io API request"""
        url = f"{self.base_url}{endpoint}"
        
        # Prepare query string
        query_string = ""
        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        
        # Prepare payload
        payload_string = ""
        if data:
            payload_string = json.dumps(data)
        
        # Generate signature
        headers = self._generate_signature(method, endpoint, query_string, payload_string)
        headers["Content-Type"] = "application/json"
        
        # Make request
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=payload_string, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def get_balance(self):
        """Get account balance"""
        result = self._api_request("GET", "/spot/accounts")
        if result:
            balances = {}
            for item in result:
                currency = item.get("currency")
                available = float(item.get("available", 0))
                if available > 0:
                    balances[currency] = available
            return balances
        return {}
    
    def get_ticker(self, pair: str):
        """Get current price for trading pair"""
        result = self._api_request("GET", "/spot/tickers", params={"currency_pair": pair})
        if result and len(result) > 0:
            return {
                "pair": pair,
                "last": float(result[0].get("last", 0)),
                "high": float(result[0].get("high_24h", 0)),
                "low": float(result[0].get("low_24h", 0)),
                "volume": float(result[0].get("base_volume", 0))
            }
        return None
    
    def place_order(self, pair: str, side: str, amount: float, price: float = None):
        """
        Place order on Gate.io
        
        Args:
            pair: Trading pair (e.g., "BTC_USDT")
            side: "buy" or "sell"
            amount: Amount to trade
            price: Limit price (None for market order)
        """
        order_data = {
            "currency_pair": pair,
            "side": side,
            "amount": str(amount),
            "type": "market" if price is None else "limit"
        }
        
        if price:
            order_data["price"] = str(price)
        
        result = self._api_request("POST", "/spot/orders", data=order_data)
        
        if result:
            print(f"✅ Order placed: {side} {amount} {pair}")
            self._log_trade(pair, side, amount, price)
            return result
        else:
            print(f"❌ Order failed: {side} {amount} {pair}")
            return None
    
    def _log_trade(self, pair: str, side: str, amount: float, price: float = None):
        """Log trade to file"""
        trade_log = self.log_path / self.signature / "trades" / f"trades_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "pair": pair,
            "side": side,
            "amount": amount,
            "price": price,
            "type": "market" if price is None else "limit"
        }
        
        with open(trade_log, "a") as f:
            f.write(json.dumps(trade_record) + "\n")
    
    async def initialize(self):
        """Initialize MCP client and AI model"""
        print("🔧 Initializing Gate.io Agent...")
        
        # Initialize MCP client for tools
        try:
            self.mcp_client = MultiServerMCPClient()
            
            # Connect to MCP services
            math_port = os.getenv("MATH_HTTP_PORT", "8000")
            search_port = os.getenv("SEARCH_HTTP_PORT", "8001")
            
            await self.mcp_client.connect_to_server(
                "math",
                {"command": "python", "args": ["-m", "uvicorn", "agent_tools.tool_math:app", "--port", math_port]}
            )
            
            await self.mcp_client.connect_to_server(
                "search",
                {"command": "python", "args": ["-m", "uvicorn", "agent_tools.tool_jina_search:app", "--port", search_port]}
            )
            
            print("✅ MCP tools connected")
        
        except Exception as e:
            print(f"⚠️  MCP connection failed: {e}")
            self.mcp_client = None
        
        # Initialize AI model
        self.llm = ChatOpenAI(
            model=self.basemodel,
            base_url=self.openai_base_url,
            api_key=self.openai_api_key,
            temperature=0.7
        )
        
        print(f"✅ AI model initialized: {self.basemodel}")
    
    def get_system_prompt(self, market_data: dict = None):
        """Generate system prompt for trading agent"""
        balance = self.get_balance()
        return get_gate_system_prompt(balance, self.trading_pairs, market_data)
    
    async def run_trading_session(self):
        """Run single trading session"""
        print("🚀 Starting trading session...")
        
        # Get current market data
        market_data = {}
        for pair in self.trading_pairs:
            ticker = self.get_ticker(pair)
            if ticker:
                market_data[pair] = ticker
        
        print(f"📊 Market data: {json.dumps(market_data, indent=2)}")
        
        # Create agent prompt with market data
        system_prompt = self.get_system_prompt(market_data)
        
        # Get MCP tools
        tools = []
        if self.mcp_client:
            tools = await self.mcp_client.list_tools()
        
        # Create agent
        self.agent = create_agent(
            self.llm,
            tools,
            system_prompt
        )
        
        # Run agent
        messages = [{"role": "user", "content": f"قم بتحليل السوق واتخذ قرارات التداول المناسبة. بيانات السوق الحالية:\n{json.dumps(market_data, indent=2)}"}]
        
        step = 0
        while step < self.max_steps:
            step += 1
            print(f"\n{'='*60}")
            print(f"🔄 Step {step}/{self.max_steps}")
            
            try:
                response = await self.agent.ainvoke({"messages": messages})
                
                # Check for stop signal
                if isinstance(response, AIMessage):
                    content = response.content
                    if STOP_SIGNAL in content:
                        print("✅ Trading session completed")
                        break
                
                messages.append(response)
                
                # Log step
                self._log_step(step, response)
                
                await asyncio.sleep(self.base_delay)
            
            except Exception as e:
                print(f"❌ Error in step {step}: {e}")
                break
        
        print("🎉 Trading session finished")
    
    def _log_step(self, step: int, response):
        """Log agent step"""
        log_file = self.log_path / self.signature / "log" / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        log_record = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "response": str(response)
        }
        
        with open(log_file, "a") as f:
            f.write(json.dumps(log_record) + "\n")
    
    async def run_continuous(self, interval_minutes: int = 60):
        """Run continuous trading with specified interval"""
        print(f"🔁 Starting continuous trading (interval: {interval_minutes} minutes)")
        
        while True:
            try:
                await self.run_trading_session()
                print(f"⏰ Waiting {interval_minutes} minutes until next session...")
                await asyncio.sleep(interval_minutes * 60)
            
            except KeyboardInterrupt:
                print("\n⛔ Stopping continuous trading...")
                break
            
            except Exception as e:
                print(f"❌ Error in continuous trading: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def get_portfolio_summary(self):
        """Get portfolio summary"""
        balance = self.get_balance()
        
        total_value_usdt = balance.get("USDT", 0)
        
        # Calculate value of other assets in USDT
        for currency, amount in balance.items():
            if currency != "USDT":
                pair = f"{currency}_USDT"
                ticker = self.get_ticker(pair)
                if ticker:
                    total_value_usdt += amount * ticker["last"]
        
        return {
            "balance": balance,
            "total_value_usdt": total_value_usdt,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test Gate.io connection
    async def test():
        agent = GateAgent(
            signature="gate-test",
            basemodel="gpt-4",
            initial_cash=1000.0
        )
        
        await agent.initialize()
        
        # Test balance
        balance = agent.get_balance()
        print(f"💰 Balance: {balance}")
        
        # Test ticker
        ticker = agent.get_ticker("BTC_USDT")
        print(f"📊 BTC/USDT: {ticker}")
        
        # Run trading session
        await agent.run_trading_session()
    
    asyncio.run(test())
