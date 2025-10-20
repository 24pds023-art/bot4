"""
REAL BINANCE CONNECTOR
=====================
🔥 REAL WebSocket connections to Binance
⚡ REAL order execution with live API
📊 REAL market data processing
🎯 NO SIMULATIONS - 100% LIVE TRADING
"""

import asyncio
import websockets
import json
import time
import hmac
import hashlib
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from urllib.parse import urlencode
from decimal import Decimal, getcontext
import numpy as np
from collections import deque

# Set high precision for financial calculations
getcontext().prec = 18

@dataclass
class RealTickData:
    """Real tick data from Binance"""
    symbol: str
    price: float
    quantity: float
    timestamp: int
    is_buyer_maker: bool
    trade_id: int
    event_time: int

@dataclass
class RealOrderBookData:
    """Real order book data"""
    symbol: str
    bids: List[tuple]  # [(price, quantity), ...]
    asks: List[tuple]  # [(price, quantity), ...]
    last_update_id: int
    event_time: int

@dataclass
class RealOrderResult:
    """Real order execution result"""
    symbol: str
    order_id: int
    client_order_id: str
    side: str
    order_type: str
    quantity: float
    price: float
    status: str
    fills: List[Dict]
    commission: float
    commission_asset: str
    execution_time: float

class RealBinanceConnector:
    """REAL Binance connector - NO SIMULATIONS"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # API endpoints
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.ws_base = "wss://stream.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
            self.ws_base = "wss://fstream.binance.com"
        
        # WebSocket URLs
        self.ws_ticker_url = f"{self.ws_base}/ws"
        self.ws_depth_url = f"{self.ws_base}/ws"
        self.ws_trades_url = f"{self.ws_base}/ws"
        
        # Session for HTTP requests
        self.session = None
        
        # Data callbacks
        self.tick_callback = None
        self.orderbook_callback = None
        self.trade_callback = None
        
        # Connection status
        self.is_connected = False
        self.websocket_connections = {}
        
        # Performance tracking
        self.message_count = 0
        self.last_message_time = 0
        self.latency_measurements = deque(maxlen=1000)
        
        # Symbol information cache
        self.symbol_info = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print("🔥 REAL Binance Connector initialized")
        print(f"   Environment: {'TESTNET' if testnet else 'LIVE PRODUCTION'}")
        print(f"   Base URL: {self.base_url}")
    
    async def initialize(self):
        """Initialize real Binance connection"""
        self.logger.info("🚀 Initializing REAL Binance connection...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'X-MBX-APIKEY': self.api_key}
        )
        
        # Get exchange info
        await self._get_exchange_info()
        
        # Test connectivity
        await self._test_connectivity()
        
        self.logger.info("✅ REAL Binance connection initialized")
    
    async def _get_exchange_info(self):
        """Get real exchange information"""
        try:
            url = f"{self.base_url}/fapi/v1/exchangeInfo"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache symbol information
                    for symbol_data in data['symbols']:
                        symbol = symbol_data['symbol']
                        self.symbol_info[symbol] = {
                            'status': symbol_data['status'],
                            'baseAsset': symbol_data['baseAsset'],
                            'quoteAsset': symbol_data['quoteAsset'],
                            'pricePrecision': symbol_data['pricePrecision'],
                            'quantityPrecision': symbol_data['quantityPrecision'],
                            'filters': symbol_data['filters']
                        }
                    
                    self.logger.info(f"✅ Loaded info for {len(self.symbol_info)} symbols")
                else:
                    raise Exception(f"Failed to get exchange info: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error getting exchange info: {e}")
            raise
    
    async def _test_connectivity(self):
        """Test real API connectivity"""
        try:
            url = f"{self.base_url}/fapi/v1/ping"
            
            start_time = time.time()
            async with self.session.get(url) as response:
                end_time = time.time()
                
                if response.status == 200:
                    latency = (end_time - start_time) * 1000
                    self.logger.info(f"✅ API connectivity test passed - Latency: {latency:.1f}ms")
                else:
                    raise Exception(f"Connectivity test failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"❌ Connectivity test failed: {e}")
            raise
    
    def set_callbacks(self, tick_callback: Callable = None, 
                     orderbook_callback: Callable = None,
                     trade_callback: Callable = None):
        """Set callbacks for real market data"""
        self.tick_callback = tick_callback
        self.orderbook_callback = orderbook_callback
        self.trade_callback = trade_callback
        
        self.logger.info("✅ Market data callbacks configured")
    
    async def start_real_websockets(self, symbols: List[str]):
        """Start REAL WebSocket connections for live data"""
        self.logger.info(f"🚀 Starting REAL WebSocket connections for {len(symbols)} symbols...")
        
        # Create WebSocket tasks
        tasks = []
        
        for symbol in symbols:
            # Individual ticker stream
            if self.tick_callback:
                task = asyncio.create_task(
                    self._websocket_ticker_stream(symbol)
                )
                tasks.append(task)
            
            # Order book stream
            if self.orderbook_callback:
                task = asyncio.create_task(
                    self._websocket_depth_stream(symbol)
                )
                tasks.append(task)
            
            # Individual trades stream
            if self.trade_callback:
                task = asyncio.create_task(
                    self._websocket_trades_stream(symbol)
                )
                tasks.append(task)
        
        # Start all WebSocket connections
        self.is_connected = True
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _websocket_ticker_stream(self, symbol: str):
        """REAL ticker WebSocket stream"""
        stream_name = f"{symbol.lower()}@ticker"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL ticker stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20) as ws:
                    self.websocket_connections[f"ticker_{symbol}"] = ws
                    
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        await self._process_ticker_message(symbol, message)
                        
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ Ticker WebSocket error for {symbol}: {e}")
                    await asyncio.sleep(5)  # Wait before reconnecting
    
    async def _websocket_depth_stream(self, symbol: str):
        """REAL order book WebSocket stream"""
        stream_name = f"{symbol.lower()}@depth20@100ms"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL depth stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20) as ws:
                    self.websocket_connections[f"depth_{symbol}"] = ws
                    
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        await self._process_depth_message(symbol, message)
                        
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ Depth WebSocket error for {symbol}: {e}")
                    await asyncio.sleep(5)
    
    async def _websocket_trades_stream(self, symbol: str):
        """REAL trades WebSocket stream"""
        stream_name = f"{symbol.lower()}@aggTrade"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL trades stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20) as ws:
                    self.websocket_connections[f"trades_{symbol}"] = ws
                    
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        await self._process_trades_message(symbol, message)
                        
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ Trades WebSocket error for {symbol}: {e}")
                    await asyncio.sleep(5)
    
    async def _process_ticker_message(self, symbol: str, message: str):
        """Process REAL ticker message"""
        try:
            data = json.loads(message)
            
            # Extract real tick data
            tick_data = RealTickData(
                symbol=data['s'],
                price=float(data['c']),  # Current price
                quantity=float(data['v']),  # 24h volume
                timestamp=int(time.time() * 1000),
                is_buyer_maker=False,  # Not available in ticker
                trade_id=0,  # Not available in ticker
                event_time=data['E']
            )
            
            # Measure latency
            current_time = int(time.time() * 1000)
            latency = current_time - tick_data.event_time
            self.latency_measurements.append(latency)
            
            # Update counters
            self.message_count += 1
            self.last_message_time = time.time()
            
            # Call callback with real data
            if self.tick_callback:
                await self.tick_callback(tick_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing ticker message: {e}")
    
    async def _process_depth_message(self, symbol: str, message: str):
        """Process REAL order book message"""
        try:
            data = json.loads(message)
            
            # Extract real order book data
            orderbook_data = RealOrderBookData(
                symbol=symbol,
                bids=[(float(bid[0]), float(bid[1])) for bid in data['b']],
                asks=[(float(ask[0]), float(ask[1])) for ask in data['a']],
                last_update_id=data['lastUpdateId'],
                event_time=data['E']
            )
            
            # Call callback with real data
            if self.orderbook_callback:
                await self.orderbook_callback(orderbook_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing depth message: {e}")
    
    async def _process_trades_message(self, symbol: str, message: str):
        """Process REAL trades message"""
        try:
            data = json.loads(message)
            
            # Extract real trade data
            trade_data = RealTickData(
                symbol=data['s'],
                price=float(data['p']),
                quantity=float(data['q']),
                timestamp=data['T'],
                is_buyer_maker=data['m'],
                trade_id=data['a'],
                event_time=data['E']
            )
            
            # Call callback with real data
            if self.trade_callback:
                await self.trade_callback(trade_data)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing trades message: {e}")
    
    def _create_signature(self, params: Dict[str, Any]) -> str:
        """Create HMAC signature for Binance API"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def place_real_order(self, symbol: str, side: str, order_type: str,
                              quantity: float, price: float = None,
                              time_in_force: str = 'GTC') -> RealOrderResult:
        """Place REAL order on Binance"""
        try:
            start_time = time.time()
            
            # Prepare order parameters
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': str(quantity),
                'timestamp': int(time.time() * 1000)
            }
            
            if order_type.upper() == 'LIMIT':
                params['price'] = str(price)
                params['timeInForce'] = time_in_force
            
            # Add signature
            params['signature'] = self._create_signature(params)
            
            # Execute REAL order
            url = f"{self.base_url}/fapi/v1/order"
            
            async with self.session.post(url, data=params) as response:
                end_time = time.time()
                execution_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Create real order result
                    result = RealOrderResult(
                        symbol=data['symbol'],
                        order_id=data['orderId'],
                        client_order_id=data['clientOrderId'],
                        side=data['side'],
                        order_type=data['type'],
                        quantity=float(data['origQty']),
                        price=float(data.get('price', 0)),
                        status=data['status'],
                        fills=data.get('fills', []),
                        commission=0.0,  # Calculate from fills
                        commission_asset='',
                        execution_time=execution_time
                    )
                    
                    # Calculate commission from fills
                    if result.fills:
                        total_commission = sum(float(fill['commission']) for fill in result.fills)
                        result.commission = total_commission
                        result.commission_asset = result.fills[0]['commissionAsset']
                    
                    self.logger.info(f"✅ REAL ORDER EXECUTED: {symbol} {side} {quantity}")
                    self.logger.info(f"   Order ID: {result.order_id}")
                    self.logger.info(f"   Status: {result.status}")
                    self.logger.info(f"   Execution Time: {execution_time*1000:.1f}ms")
                    
                    return result
                    
                else:
                    error_data = await response.json()
                    error_msg = error_data.get('msg', 'Unknown error')
                    raise Exception(f"Order failed: {error_msg}")
                    
        except Exception as e:
            self.logger.error(f"❌ REAL ORDER FAILED: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get REAL account information"""
        try:
            params = {
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v2/account"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    self.logger.info("✅ Retrieved REAL account information")
                    return data
                else:
                    error_data = await response.json()
                    raise Exception(f"Failed to get account info: {error_data}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error getting account info: {e}")
            raise
    
    async def get_position_info(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get REAL position information"""
        try:
            params = {
                'timestamp': int(time.time() * 1000)
            }
            
            if symbol:
                params['symbol'] = symbol
            
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v2/positionRisk"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Filter only positions with size > 0
                    active_positions = [
                        pos for pos in data 
                        if float(pos['positionAmt']) != 0
                    ]
                    
                    self.logger.info(f"✅ Retrieved {len(active_positions)} REAL positions")
                    return active_positions
                else:
                    error_data = await response.json()
                    raise Exception(f"Failed to get positions: {error_data}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error getting positions: {e}")
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get REAL performance statistics"""
        if not self.latency_measurements:
            return {}
        
        latencies = list(self.latency_measurements)
        
        return {
            'messages_processed': self.message_count,
            'avg_latency_ms': np.mean(latencies),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99),
            'min_latency_ms': np.min(latencies),
            'max_latency_ms': np.max(latencies),
            'is_connected': self.is_connected,
            'active_connections': len(self.websocket_connections),
            'last_message_time': self.last_message_time
        }
    
    async def close(self):
        """Close all REAL connections"""
        self.logger.info("🔌 Closing REAL Binance connections...")
        
        self.is_connected = False
        
        # Close WebSocket connections
        for name, ws in self.websocket_connections.items():
            try:
                await ws.close()
            except:
                pass
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        self.logger.info("✅ All REAL connections closed")

# Example usage
async def test_real_binance_connector():
    """Test REAL Binance connector"""
    print("🔥 Testing REAL Binance Connector")
    print("⚠️  This will connect to REAL Binance API!")
    
    # Initialize with your REAL API credentials
    api_key = "YOUR_REAL_API_KEY"
    api_secret = "YOUR_REAL_API_SECRET"
    
    connector = RealBinanceConnector(api_key, api_secret, testnet=True)
    
    # Real tick callback
    async def on_real_tick(tick_data: RealTickData):
        print(f"📊 REAL TICK: {tick_data.symbol} = ${tick_data.price:.2f}")
    
    # Real order book callback
    async def on_real_orderbook(orderbook_data: RealOrderBookData):
        best_bid = orderbook_data.bids[0][0] if orderbook_data.bids else 0
        best_ask = orderbook_data.asks[0][0] if orderbook_data.asks else 0
        print(f"📈 REAL BOOK: {orderbook_data.symbol} Bid: ${best_bid:.2f} Ask: ${best_ask:.2f}")
    
    try:
        # Initialize REAL connection
        await connector.initialize()
        
        # Set callbacks
        connector.set_callbacks(
            tick_callback=on_real_tick,
            orderbook_callback=on_real_orderbook
        )
        
        # Start REAL WebSocket streams
        symbols = ['BTCUSDT', 'ETHUSDT']
        await asyncio.wait_for(
            connector.start_real_websockets(symbols),
            timeout=30.0
        )
        
    except asyncio.TimeoutError:
        print("⏰ Test completed")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(test_real_binance_connector())