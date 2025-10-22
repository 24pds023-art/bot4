#!/usr/bin/env python3
"""
🔥 SIMPLE BINANCE CONNECTOR
===========================
Simplified, reliable Binance WebSocket connector
Focuses on stability and error handling
"""

import asyncio
import aiohttp
import websockets
import json
import time
import hmac
import hashlib
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from urllib.parse import urlencode
from decimal import Decimal, getcontext

# Set high precision
getcontext().prec = 18

@dataclass
class SimpleTick:
    """Simple tick data structure"""
    symbol: str
    price: float
    volume: float
    timestamp: int
    change_24h: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0

class SimpleBinanceConnector:
    """Simplified REAL Binance connector with better error handling"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Binance endpoints
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.ws_base = "wss://stream.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
            self.ws_base = "wss://fstream.binance.com"
        
        self.session = None
        self.is_connected = False
        self.tick_callback = None
        
        # Connection tracking
        self.connection_count = 0
        self.last_message_time = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize connection"""
        self.logger.info("🚀 Initializing Simple Binance connector...")
        
        # Create session
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'X-MBX-APIKEY': self.api_key}
        )
        
        # Test connectivity
        await self._test_ping()
        self.logger.info("✅ Simple Binance connector ready")
    
    async def _test_ping(self):
        """Test basic connectivity"""
        try:
            url = f"{self.base_url}/fapi/v1/ping"
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Ping failed: {response.status}")
                self.logger.info("✅ Binance API ping successful")
        except Exception as e:
            self.logger.error(f"❌ Ping failed: {e}")
            raise
    
    def _create_signature(self, params: Dict) -> str:
        """Create HMAC signature"""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_account_balance(self) -> float:
        """Get account balance"""
        try:
            params = {'timestamp': int(time.time() * 1000)}
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v2/account"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data['totalWalletBalance'])
                else:
                    error = await response.json()
                    raise Exception(f"Balance request failed: {error}")
        except Exception as e:
            self.logger.error(f"❌ Error getting balance: {e}")
            raise
    
    async def place_market_order(self, symbol: str, side: str, quantity: float):
        """Place market order with improved error handling"""
        try:
            # Round quantity to appropriate precision based on Binance requirements
            symbol_precision = {
                'BTCUSDT': 3, 'ETHUSDT': 3, 'BNBUSDT': 2, 'SOLUSDT': 1, 'XRPUSDT': 1,
                'ADAUSDT': 0, 'DOTUSDT': 1, 'LINKUSDT': 2, 'MATICUSDT': 0, 'UNIUSDT': 2,
                'LTCUSDT': 2, 'ETCUSDT': 1, 'ARBUSDT': 0, 'OPUSDT': 0, 'AVAXUSDT': 2,
                'ATOMUSDT': 2, 'FILUSDT': 2, 'APTUSDT': 1, 'INJUSDT': 1, 'NEARUSDT': 1,
                'SUIUSDT': 1, 'PEPEUSDT': 0, 'SHIBUSDT': 0, 'DOGEUSDT': 0, 'WIFUSDT': 0,
                'FLOKIUSDT': 0, 'BONKUSDT': 0, 'RENDERUSDT': 2, 'SANDUSDT': 0, 'MANAUSDT': 0,
                'ALGOUSDT': 0  # ALGO needs whole numbers
            }
            
            precision = symbol_precision.get(symbol, 1)  # Default to 1 decimal (safer)
            
            # Apply precision rounding with proper float handling
            from decimal import Decimal, ROUND_DOWN
            qty_decimal = Decimal(str(quantity))
            if precision == 0:
                quantity = float(qty_decimal.quantize(Decimal('1'), rounding=ROUND_DOWN))
            else:
                quantize_val = Decimal('0.1') ** precision
                quantity = float(qty_decimal.quantize(quantize_val, rounding=ROUND_DOWN))
            
            # Ensure minimum quantity (1 for whole number symbols, 0.01 for others)
            min_qty = 1 if precision == 0 else 0.01
            if quantity < min_qty:
                raise Exception(f"Quantity too small: {quantity} (min: {min_qty})")
            
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'MARKET',
                'quantity': str(quantity),
                'timestamp': int(time.time() * 1000)
            }
            
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v1/order"
            
            # Retry logic for server errors
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with self.session.post(url, data=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.logger.info(f"✅ Order executed: {symbol} {side} {quantity}")
                            return data
                        elif response.status == 502:
                            # Server error - retry
                            if attempt < max_retries - 1:
                                self.logger.warning(f"Server error (502), retrying... attempt {attempt + 1}")
                                await asyncio.sleep(1)
                                continue
                            else:
                                raise Exception("Server error after retries")
                        else:
                            try:
                                error = await response.json()
                                error_msg = error.get('msg', 'Unknown error')
                                
                                # Handle specific errors
                                if 'PERCENT_PRICE' in error_msg:
                                    self.logger.warning(f"Price filter error - skipping order: {error_msg}")
                                    return None  # Return None to indicate order should be skipped
                                elif 'LOT_SIZE' in error_msg:
                                    raise Exception(f"Quantity error: {error_msg}")
                                else:
                                    raise Exception(f"Order failed: {error}")
                            except Exception as json_error:
                                # If we can't parse JSON, use status code
                                raise Exception(f"HTTP {response.status}: {await response.text()}")
                                
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Timeout, retrying... attempt {attempt + 1}")
                        await asyncio.sleep(1)
                        continue
                    else:
                        raise Exception("Request timeout after retries")
                        
        except Exception as e:
            self.logger.error(f"❌ Order execution failed: {e}")
            raise
    
    async def start_simple_stream(self, symbols: List[str]):
        """Start simple multi-symbol stream"""
        # Create stream names
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        stream_url = f"{self.ws_base}/stream?streams={'/'.join(streams)}"
        
        self.logger.info(f"🔗 Starting simple stream for {len(symbols)} symbols")
        
        while self.is_connected:
            try:
                async with websockets.connect(
                    stream_url, 
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as ws:
                    
                    self.connection_count += 1
                    self.logger.info(f"✅ WebSocket connected (attempt #{self.connection_count})")
                    
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        try:
                            # Parse message
                            if isinstance(message, bytes):
                                message = message.decode('utf-8')
                            
                            data = json.loads(message)
                            
                            # Handle stream data format
                            if 'stream' in data and 'data' in data:
                                stream_name = data['stream']
                                tick_data = data['data']
                                
                                # Extract symbol from stream name
                                symbol = stream_name.split('@')[0].upper()
                                
                                # Create simple tick
                                tick = SimpleTick(
                                    symbol=symbol,
                                    price=float(tick_data.get('c', 0)),
                                    volume=float(tick_data.get('v', 0)),
                                    timestamp=int(time.time() * 1000),
                                    change_24h=float(tick_data.get('P', 0)),
                                    high_24h=float(tick_data.get('h', 0)),
                                    low_24h=float(tick_data.get('l', 0))
                                )
                                
                                # Track message timing
                                self.last_message_time[symbol] = time.time()
                                
                                # Send to callback
                                if self.tick_callback:
                                    await self.tick_callback(tick)
                                    
                            else:
                                # Handle single symbol format
                                if 's' in data and 'c' in data:
                                    tick = SimpleTick(
                                        symbol=data['s'],
                                        price=float(data['c']),
                                        volume=float(data.get('v', 0)),
                                        timestamp=int(time.time() * 1000),
                                        change_24h=float(data.get('P', 0)),
                                        high_24h=float(data.get('h', 0)),
                                        low_24h=float(data.get('l', 0))
                                    )
                                    
                                    if self.tick_callback:
                                        await self.tick_callback(tick)
                                        
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            self.logger.debug(f"Message parse error: {e}")
                            continue
                        except Exception as e:
                            self.logger.error(f"❌ Message processing error: {e}")
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                if self.is_connected:
                    self.logger.warning("⚠️ WebSocket connection closed, reconnecting...")
                    await asyncio.sleep(3)
            except websockets.exceptions.InvalidURI:
                self.logger.error("❌ Invalid WebSocket URI")
                break
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ WebSocket error: {e}")
                    await asyncio.sleep(5)
    
    async def close(self):
        """Close connections"""
        self.is_connected = False
        if self.session:
            await self.session.close()
        self.logger.info("🔒 Simple Binance connector closed")

class SimpleScalpingSignals:
    """Simple but effective scalping signal generator"""
    
    def __init__(self):
        self.price_history = {}
        self.volume_history = {}
        self.signal_count = 0
        self.last_signal_time = {}
        
        # Balanced parameters for good win rate with sufficient signals
        self.min_signal_interval = 10.0  # 10 seconds between signals
        self.momentum_threshold = 0.0012  # 0.12% momentum (balanced)
        self.volume_threshold = 1.4  # 40% above average (balanced confirmation)
        
        self.logger = logging.getLogger(__name__)
    
    def process_tick(self, tick: SimpleTick) -> Optional[Dict]:
        """Process tick and generate signals"""
        symbol = tick.symbol
        price = tick.price
        volume = tick.volume
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_signal_time.get(symbol, 0) < self.min_signal_interval:
            return None
        
        # Initialize history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []
        
        # Store data
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        
        # Keep last 20 points
        if len(self.price_history[symbol]) > 20:
            self.price_history[symbol].pop(0)
            self.volume_history[symbol].pop(0)
        
        # Need at least 10 points
        if len(self.price_history[symbol]) < 10:
            return None
        
        # Simple momentum calculation
        prices = self.price_history[symbol]
        volumes = self.volume_history[symbol]
        
        # Price momentum (current vs 5 periods ago)
        momentum = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        
        # Volume analysis
        avg_volume = sum(volumes[-5:]) / min(5, len(volumes))
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        # Simple moving averages
        sma_short = sum(prices[-3:]) / 3 if len(prices) >= 3 else price
        sma_long = sum(prices[-10:]) / 10 if len(prices) >= 10 else price
        
        # Generate signal with BALANCED criteria (quality + quantity)
        signal_strength = 0.0
        signal_type = None
        reasoning = []
        
        # Momentum signal (primary driver)
        if momentum > self.momentum_threshold:
            signal_strength += 0.4
            signal_type = 'BUY'
            reasoning.append(f'Positive momentum: {momentum:.4f}')
        elif momentum < -self.momentum_threshold:
            signal_strength += 0.4
            signal_type = 'SELL'
            reasoning.append(f'Negative momentum: {momentum:.4f}')
        
        # Moving average signal (important confirmation)
        if price > sma_short > sma_long and signal_type == 'BUY':
            signal_strength += 0.25
            reasoning.append('MA bullish alignment')
        elif price < sma_short < sma_long and signal_type == 'SELL':
            signal_strength += 0.25
            reasoning.append('MA bearish alignment')
        
        # Volume confirmation (nice to have, not required)
        if volume_ratio > self.volume_threshold:
            signal_strength += 0.20
            reasoning.append(f'Volume spike: {volume_ratio:.2f}x')
        elif volume_ratio > 1.2:  # Lower threshold still adds some value
            signal_strength += 0.10
            reasoning.append(f'Volume elevated: {volume_ratio:.2f}x')
        
        # 24h change confirmation (bonus)
        if tick.change_24h > 1.5 and signal_type == 'BUY':
            signal_strength += 0.10
            reasoning.append(f'24h gain: {tick.change_24h:.1f}%')
        elif tick.change_24h < -1.5 and signal_type == 'SELL':
            signal_strength += 0.10
            reasoning.append(f'24h drop: {tick.change_24h:.1f}%')
        
        # STRICT threshold for quality trades (was 0.55 - way too low!)
        if signal_strength < 0.75 or not signal_type:
            return None
        
        # Generate signal
        self.signal_count += 1
        self.last_signal_time[symbol] = current_time
        
        # Balanced stop/profit for crypto scalping
        if signal_type == 'BUY':
            stop_loss = price * 0.9975  # 0.25% stop
            take_profit = price * 1.0075  # 0.75% profit (1:3 R:R)
        else:
            stop_loss = price * 1.0025  # 0.25% stop
            take_profit = price * 0.9925  # 0.75% profit
        
        return {
            'signal_type': signal_type,
            'strength': min(signal_strength, 1.0),
            'confidence': min(signal_strength * 1.1, 1.0),
            'entry_price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reasoning': reasoning,
            'momentum': momentum,
            'volume_ratio': volume_ratio,
            'change_24h': tick.change_24h
        
        }
