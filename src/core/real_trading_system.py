#!/usr/bin/env python3
"""
🔥 REAL ULTRA-FAST SCALPING TRADING SYSTEM
==========================================
⚡ Complete real trading system with Binance integration
💰 NO SIMULATIONS - 100% REAL TRADING
📊 Professional-grade scalping with institutional optimizations
"""

import asyncio
import aiohttp
import websockets
import json
import time
import hmac
import hashlib
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from urllib.parse import urlencode
from decimal import Decimal, getcontext
from datetime import datetime, timedelta
from collections import deque, defaultdict
from dotenv import load_dotenv

# Set high precision for financial calculations
getcontext().prec = 18

@dataclass
class RealTick:
    """Real tick data from Binance"""
    symbol: str
    price: float
    volume: float
    timestamp: int
    event_time: int
    bid: float = 0.0
    ask: float = 0.0
    spread: float = 0.0

@dataclass
class RealOrder:
    """Real order execution result"""
    symbol: str
    order_id: int
    client_order_id: str
    side: str
    order_type: str
    quantity: float
    price: float
    status: str
    fills: List[Dict] = field(default_factory=list)
    commission: float = 0.0
    commission_asset: str = ""
    execution_time: float = 0.0

@dataclass
class RealPosition:
    """Real trading position"""
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    order_ids: List[int] = field(default_factory=list)
    
    def update_pnl(self, current_price: float):
        """Update position P&L with current market price"""
        self.current_price = current_price
        
        if self.side == 'LONG':
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:  # SHORT
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity

class RealBinanceConnector:
    """REAL Binance API connector - NO SIMULATIONS"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Real Binance endpoints
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.ws_base = "wss://stream.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
            self.ws_base = "wss://fstream.binance.com"
        
        self.session = None
        self.is_connected = False
        self.tick_callback = None
        self.orderbook_callback = None
        self.trade_callback = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize REAL Binance connection"""
        self.logger.info("🚀 Initializing REAL Binance API connection...")
        
        # Create HTTP session with proper headers
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                'X-MBX-APIKEY': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        # Test connectivity to REAL Binance
        await self._test_connectivity()
        self.logger.info("✅ REAL Binance connection established")
    
    async def _test_connectivity(self):
        """Test REAL API connectivity"""
        try:
            url = f"{self.base_url}/fapi/v1/ping"
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Binance API ping failed: {response.status}")
                self.logger.info("✅ Binance API connectivity verified")
        except Exception as e:
            self.logger.error(f"❌ Binance API connectivity failed: {e}")
            raise
    
    def _create_signature(self, params: Dict[str, Any]) -> str:
        """Create HMAC SHA256 signature for Binance API"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get REAL account information"""
        try:
            params = {'timestamp': int(time.time() * 1000)}
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v2/account"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise Exception(f"Account info failed: {error_data}")
        except Exception as e:
            self.logger.error(f"❌ Error getting account info: {e}")
            raise
    
    async def place_market_order(self, symbol: str, side: str, quantity: float) -> RealOrder:
        """Place REAL market order on Binance"""
        try:
            start_time = time.time()
            
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'MARKET',
                'quantity': str(quantity),
                'timestamp': int(time.time() * 1000)
            }
            
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v1/order"
            
            async with self.session.post(url, data=params) as response:
                execution_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    return RealOrder(
                        symbol=data['symbol'],
                        order_id=data['orderId'],
                        client_order_id=data['clientOrderId'],
                        side=data['side'],
                        order_type=data['type'],
                        quantity=float(data['origQty']),
                        price=float(data.get('avgPrice', 0)),
                        status=data['status'],
                        fills=data.get('fills', []),
                        execution_time=execution_time
                    )
                else:
                    error_data = await response.json()
                    raise Exception(f"Order execution failed: {error_data}")
                    
        except Exception as e:
            self.logger.error(f"❌ REAL order execution failed: {e}")
            raise
    
    async def start_ticker_stream(self, symbol: str):
        """Start REAL ticker WebSocket stream"""
        stream_name = f"{symbol.lower()}@ticker"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL ticker stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        try:
                            # Handle both string and bytes messages
                            if isinstance(message, bytes):
                                message = message.decode('utf-8')
                            
                            data = json.loads(message)
                            
                            # Validate required fields
                            if not all(key in data for key in ['s', 'c', 'v', 'E', 'b', 'a']):
                                self.logger.debug(f"Incomplete ticker data for {symbol}: {data}")
                                continue
                            
                            # Create real tick data
                            tick = RealTick(
                                symbol=data['s'],
                                price=float(data['c']),
                                volume=float(data['v']),
                                timestamp=int(time.time() * 1000),
                                event_time=data['E'],
                                bid=float(data['b']),
                                ask=float(data['a']),
                                spread=float(data['a']) - float(data['b'])
                            )
                            
                            if self.tick_callback:
                                await self.tick_callback(tick)
                                
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            self.logger.debug(f"Error parsing ticker message for {symbol}: {e}")
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                if self.is_connected:
                    self.logger.warning(f"⚠️ WebSocket connection closed for {symbol}, reconnecting...")
                    await asyncio.sleep(2)
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ WebSocket error for {symbol}: {e}")
                    await asyncio.sleep(5)  # Reconnect delay
    
    async def start_depth_stream(self, symbol: str):
        """Start REAL order book depth stream"""
        stream_name = f"{symbol.lower()}@depth20@100ms"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL depth stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        try:
                            # Handle both string and bytes messages
                            if isinstance(message, bytes):
                                message = message.decode('utf-8')
                            
                            data = json.loads(message)
                            
                            if self.orderbook_callback:
                                await self.orderbook_callback(symbol, data)
                                
                        except (json.JSONDecodeError, KeyError) as e:
                            self.logger.debug(f"Error parsing depth message for {symbol}: {e}")
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                if self.is_connected:
                    self.logger.warning(f"⚠️ Depth WebSocket connection closed for {symbol}, reconnecting...")
                    await asyncio.sleep(2)
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ Depth stream error for {symbol}: {e}")
                    await asyncio.sleep(5)
    
    async def close(self):
        """Close all connections"""
        self.is_connected = False
        if self.session:
            await self.session.close()
            self.logger.info("🔒 Binance connections closed")

class AdvancedScalpingEngine:
    """Advanced scalping signal generation engine"""
    
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.price_history = defaultdict(lambda: deque(maxlen=100))
        self.volume_history = defaultdict(lambda: deque(maxlen=50))
        self.signal_count = 0
        self.last_signal_time = defaultdict(float)
        
        # Scalping parameters
        self.min_signal_interval = 5.0  # Minimum 5 seconds between signals
        self.momentum_threshold = 0.0008  # 0.08% momentum threshold
        self.volume_spike_threshold = 1.5  # 50% above average volume
        
        self.logger = logging.getLogger(__name__)
    
    def process_tick(self, tick: RealTick) -> Optional[Dict]:
        """Process real tick and generate scalping signals"""
        symbol = tick.symbol
        price = tick.price
        volume = tick.volume
        current_time = time.time()
        
        # Rate limiting - prevent signal spam
        if current_time - self.last_signal_time[symbol] < self.min_signal_interval:
            return None
        
        # Store price and volume history
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        
        # Need sufficient history
        if len(self.price_history[symbol]) < 20:
            return None
        
        # Calculate technical indicators
        prices = list(self.price_history[symbol])
        volumes = list(self.volume_history[symbol])
        
        # Moving averages
        sma_5 = sum(prices[-5:]) / 5
        sma_10 = sum(prices[-10:]) / 10
        sma_20 = sum(prices[-20:]) / 20
        ema_5 = self._calculate_ema(prices, 5)
        
        # Momentum calculation
        momentum_5 = (price - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        momentum_10 = (price - prices[-10]) / prices[-10] if len(prices) >= 10 else 0
        
        # Volume analysis
        avg_volume_10 = sum(volumes[-10:]) / min(10, len(volumes))
        volume_ratio = volume / avg_volume_10 if avg_volume_10 > 0 else 1
        
        # RSI calculation (simplified)
        rsi = self._calculate_rsi(prices)
        
        # Bollinger Bands
        bb_upper, bb_lower, bb_middle = self._calculate_bollinger_bands(prices)
        
        # Generate signals
        signal = self._generate_signal(
            symbol, price, momentum_5, momentum_10, 
            sma_5, sma_10, sma_20, ema_5,
            volume_ratio, rsi, bb_upper, bb_lower, bb_middle
        )
        
        if signal:
            self.signal_count += 1
            self.last_signal_time[symbol] = current_time
            self.logger.info(f"⚡ SIGNAL GENERATED: {symbol} {signal['signal_type']} | Strength: {signal['strength']:.3f}")
        
        return signal
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            middle = sum(prices) / len(prices)
            return middle + 0.01, middle - 0.01, middle
        
        recent_prices = prices[-period:]
        middle = sum(recent_prices) / period
        
        variance = sum((p - middle) ** 2 for p in recent_prices) / period
        std = variance ** 0.5
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, lower, middle
    
    def _generate_signal(self, symbol: str, price: float, momentum_5: float, momentum_10: float,
                        sma_5: float, sma_10: float, sma_20: float, ema_5: float,
                        volume_ratio: float, rsi: float, bb_upper: float, bb_lower: float, bb_middle: float) -> Optional[Dict]:
        """Generate trading signal based on multiple indicators"""
        
        signal_strength = 0.0
        signal_type = None
        reasoning = []
        
        # Momentum signals
        if momentum_5 > self.momentum_threshold and momentum_10 > 0:
            signal_strength += 0.3
            signal_type = 'BUY'
            reasoning.append(f'Positive momentum: {momentum_5:.4f}')
        elif momentum_5 < -self.momentum_threshold and momentum_10 < 0:
            signal_strength += 0.3
            signal_type = 'SELL'
            reasoning.append(f'Negative momentum: {momentum_5:.4f}')
        
        # Moving average alignment
        if price > sma_5 > sma_10 > sma_20:
            if signal_type == 'BUY':
                signal_strength += 0.2
                reasoning.append('MA bullish alignment')
            elif signal_type is None:
                signal_strength += 0.15
                signal_type = 'BUY'
                reasoning.append('MA bullish alignment')
        elif price < sma_5 < sma_10 < sma_20:
            if signal_type == 'SELL':
                signal_strength += 0.2
                reasoning.append('MA bearish alignment')
            elif signal_type is None:
                signal_strength += 0.15
                signal_type = 'SELL'
                reasoning.append('MA bearish alignment')
        
        # EMA crossover
        if price > ema_5 and signal_type == 'BUY':
            signal_strength += 0.1
            reasoning.append('Above EMA5')
        elif price < ema_5 and signal_type == 'SELL':
            signal_strength += 0.1
            reasoning.append('Below EMA5')
        
        # Volume confirmation
        if volume_ratio > self.volume_spike_threshold:
            signal_strength += 0.15
            reasoning.append(f'Volume spike: {volume_ratio:.2f}x')
        
        # RSI conditions
        if rsi < 30 and signal_type == 'BUY':
            signal_strength += 0.1
            reasoning.append(f'RSI oversold: {rsi:.1f}')
        elif rsi > 70 and signal_type == 'SELL':
            signal_strength += 0.1
            reasoning.append(f'RSI overbought: {rsi:.1f}')
        
        # Bollinger Bands
        if price <= bb_lower and signal_type == 'BUY':
            signal_strength += 0.15
            reasoning.append('BB lower band bounce')
        elif price >= bb_upper and signal_type == 'SELL':
            signal_strength += 0.15
            reasoning.append('BB upper band rejection')
        
        # Minimum signal strength threshold
        if signal_strength < 0.4 or signal_type is None:
            return None
        
        # Calculate stop loss and take profit
        if signal_type == 'BUY':
            stop_loss = price * 0.998  # 0.2% stop loss
            take_profit = price * 1.006  # 0.6% take profit
        else:  # SELL
            stop_loss = price * 1.002  # 0.2% stop loss
            take_profit = price * 0.994  # 0.6% take profit
        
        return {
            'signal_type': signal_type,
            'strength': min(signal_strength, 1.0),
            'confidence': min(signal_strength * 1.2, 1.0),
            'entry_price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'reasoning': reasoning,
            'indicators': {
                'momentum_5': momentum_5,
                'momentum_10': momentum_10,
                'rsi': rsi,
                'volume_ratio': volume_ratio,
                'bb_position': (price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            }
        }

class RealRiskManager:
    """Real-time risk management system"""
    
    def __init__(self, initial_balance: float, max_daily_loss: float = 100.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        
        # Risk limits
        self.max_position_size_pct = 0.02  # 2% of balance per position
        self.max_total_exposure_pct = 0.10  # 10% total exposure
        self.max_positions = 5
        
        # Drawdown tracking
        self.peak_balance = initial_balance
        self.max_drawdown_pct = 0.05  # 5% max drawdown
        
        self.logger = logging.getLogger(__name__)
    
    def can_open_position(self, position_size_usd: float, current_positions: int) -> bool:
        """Check if new position can be opened"""
        # Check position count limit
        if current_positions >= self.max_positions:
            self.logger.warning(f"⚠️ Max positions limit reached: {current_positions}")
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            self.logger.warning(f"⚠️ Daily loss limit reached: ${self.daily_pnl:.2f}")
            return False
        
        # Check position size limit
        max_position_size = self.current_balance * self.max_position_size_pct
        if position_size_usd > max_position_size:
            self.logger.warning(f"⚠️ Position size too large: ${position_size_usd:.2f} > ${max_position_size:.2f}")
            return False
        
        # Check drawdown limit
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        if current_drawdown > self.max_drawdown_pct:
            self.logger.warning(f"⚠️ Max drawdown exceeded: {current_drawdown:.2%}")
            return False
        
        return True
    
    def update_balance(self, pnl: float):
        """Update balance and risk metrics"""
        self.daily_pnl += pnl
        self.total_pnl += pnl
        self.current_balance = self.initial_balance + self.total_pnl
        
        # Update peak balance
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance
    
    def should_emergency_stop(self) -> bool:
        """Check if emergency stop should be triggered"""
        # Emergency stop conditions
        current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        
        if current_drawdown > self.max_drawdown_pct * 1.5:  # 1.5x max drawdown
            return True
        
        if self.daily_pnl <= -self.max_daily_loss * 1.5:  # 1.5x daily loss limit
            return True
        
        return False

class RealTradingSystem:
    """Complete REAL ultra-fast scalping trading system"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get REAL API credentials
        self.api_key = os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_TESTNET_API_SECRET') or os.getenv('BINANCE_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API credentials not found! Please configure .env file")
        
        # Initialize core components
        self.binance = RealBinanceConnector(self.api_key, self.api_secret, self.use_testnet)
        
        # Trading configuration
        self.symbols = os.getenv('TRADING_SYMBOLS', 'BTCUSDT,ETHUSDT,BNBUSDT').split(',')
        self.position_size_usd = float(os.getenv('BASE_POSITION_USD', 50))
        self.max_positions = int(os.getenv('MAX_POSITIONS', 3))
        
        # Initialize engines after getting account info
        self.scalping_engine = None
        self.risk_manager = None
        
        # Trading state
        self.is_trading = False
        self.positions: Dict[str, RealPosition] = {}
        self.trades = []
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.start_time = time.time()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/trading_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔥 REAL Trading System initialized")
        self.logger.info(f"   Environment: {'TESTNET' if self.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
        self.logger.info(f"   Symbols: {self.symbols}")
        self.logger.info(f"   Position Size: ${self.position_size_usd}")
    
    async def initialize(self):
        """Initialize the complete trading system"""
        self.logger.info("🚀 Initializing REAL Trading System...")
        
        # Initialize Binance connection
        await self.binance.initialize()
        
        # Get REAL account information
        account_info = await self.binance.get_account_info()
        account_balance = float(account_info['totalWalletBalance'])
        
        # Initialize engines with real account data
        self.scalping_engine = AdvancedScalpingEngine(self.symbols)
        self.risk_manager = RealRiskManager(
            initial_balance=account_balance,
            max_daily_loss=float(os.getenv('MAX_DAILY_LOSS', 100))
        )
        
        # Set up callbacks
        self.binance.tick_callback = self._on_real_tick
        self.binance.orderbook_callback = self._on_real_orderbook
        
        self.logger.info(f"✅ REAL system initialized")
        self.logger.info(f"   Account Balance: ${account_balance:.2f}")
        self.logger.info(f"   Max Daily Loss: ${self.risk_manager.max_daily_loss:.2f}")
        
        return account_balance
    
    async def _on_real_tick(self, tick: RealTick):
        """Process real tick data from Binance"""
        try:
            # Update existing positions
            if tick.symbol in self.positions:
                self.positions[tick.symbol].update_pnl(tick.price)
            
            # Generate trading signals if actively trading
            if self.is_trading:
                signal = self.scalping_engine.process_tick(tick)
                
                if signal and signal['strength'] > 0.6:  # High-confidence signals only
                    await self._process_signal(tick.symbol, signal, tick.price)
                    
        except Exception as e:
            self.logger.error(f"❌ Error processing tick for {tick.symbol}: {e}")
    
    async def _on_real_orderbook(self, symbol: str, orderbook_data: Dict):
        """Process real order book data"""
        try:
            # Extract bid/ask data for spread analysis
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if bids and asks:
                best_bid = float(bids[0][0])
                best_ask = float(asks[0][0])
                spread = best_ask - best_bid
                
                # Log tight spreads for scalping opportunities
                if spread < best_bid * 0.0001:  # Very tight spread
                    self.logger.debug(f"📊 Tight spread on {symbol}: {spread:.6f}")
                    
        except Exception as e:
            self.logger.error(f"❌ Error processing orderbook for {symbol}: {e}")
    
    async def _process_signal(self, symbol: str, signal: Dict, current_price: float):
        """Process trading signal and execute if conditions are met"""
        try:
            # Skip if already in position for this symbol
            if symbol in self.positions:
                return
            
            # Risk management check
            if not self.risk_manager.can_open_position(self.position_size_usd, len(self.positions)):
                return
            
            # Calculate position size
            quantity = self.position_size_usd / current_price
            quantity = round(quantity, 3)  # Round to 3 decimal places
            
            if quantity < 0.001:  # Minimum quantity check
                self.logger.warning(f"⚠️ Position size too small for {symbol}: {quantity}")
                return
            
            self.logger.info(f"🚀 EXECUTING REAL ORDER: {symbol} {signal['signal_type']} {quantity}")
            self.logger.info(f"   Signal Strength: {signal['strength']:.3f}")
            self.logger.info(f"   Reasoning: {', '.join(signal['reasoning'])}")
            
            # Execute REAL order on Binance
            order = await self.binance.place_market_order(
                symbol=symbol,
                side=signal['signal_type'],
                quantity=quantity
            )
            
            if order.status in ['FILLED', 'PARTIALLY_FILLED']:
                # Create real position
                position = RealPosition(
                    symbol=symbol,
                    side='LONG' if signal['signal_type'] == 'BUY' else 'SHORT',
                    quantity=order.quantity,
                    entry_price=current_price,
                    current_price=current_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    entry_time=datetime.now(),
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit'],
                    order_ids=[order.order_id]
                )
                
                self.positions[symbol] = position
                self.total_trades += 1
                
                self.logger.info(f"✅ REAL POSITION OPENED:")
                self.logger.info(f"   Symbol: {symbol}")
                self.logger.info(f"   Side: {position.side}")
                self.logger.info(f"   Quantity: {position.quantity}")
                self.logger.info(f"   Entry Price: ${position.entry_price:.4f}")
                self.logger.info(f"   Stop Loss: ${position.stop_loss:.4f}")
                self.logger.info(f"   Take Profit: ${position.take_profit:.4f}")
                self.logger.info(f"   Order ID: {order.order_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Signal processing failed for {symbol}: {e}")
    
    async def _check_exit_conditions(self):
        """Check exit conditions for all open positions"""
        try:
            for symbol, position in list(self.positions.items()):
                should_close = False
                exit_reason = ""
                
                current_price = position.current_price
                
                # Stop loss check
                if ((position.side == 'LONG' and current_price <= position.stop_loss) or
                    (position.side == 'SHORT' and current_price >= position.stop_loss)):
                    should_close = True
                    exit_reason = "Stop loss triggered"
                
                # Take profit check
                elif ((position.side == 'LONG' and current_price >= position.take_profit) or
                      (position.side == 'SHORT' and current_price <= position.take_profit)):
                    should_close = True
                    exit_reason = "Take profit triggered"
                
                # Time-based exit (scalping - quick in/out)
                elif datetime.now() - position.entry_time > timedelta(minutes=10):
                    should_close = True
                    exit_reason = "Time limit exceeded (10 min)"
                
                # Emergency risk management
                elif self.risk_manager.should_emergency_stop():
                    should_close = True
                    exit_reason = "Emergency risk stop"
                
                if should_close:
                    await self._close_position(symbol, exit_reason)
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking exit conditions: {e}")
    
    async def _close_position(self, symbol: str, reason: str):
        """Close a real position"""
        try:
            position = self.positions[symbol]
            close_side = 'SELL' if position.side == 'LONG' else 'BUY'
            
            self.logger.info(f"🔒 CLOSING REAL POSITION: {symbol} - {reason}")
            
            # Execute real close order
            order = await self.binance.place_market_order(
                symbol=symbol,
                side=close_side,
                quantity=position.quantity
            )
            
            if order.status in ['FILLED', 'PARTIALLY_FILLED']:
                # Calculate final P&L
                final_pnl = position.unrealized_pnl
                
                # Update risk manager
                self.risk_manager.update_balance(final_pnl)
                
                # Track winning trades
                if final_pnl > 0:
                    self.winning_trades += 1
                
                # Remove position
                del self.positions[symbol]
                
                self.logger.info(f"✅ REAL POSITION CLOSED:")
                self.logger.info(f"   Symbol: {symbol}")
                self.logger.info(f"   P&L: ${final_pnl:.2f}")
                self.logger.info(f"   Reason: {reason}")
                self.logger.info(f"   Total P&L: ${self.risk_manager.total_pnl:.2f}")
                self.logger.info(f"   Account Balance: ${self.risk_manager.current_balance:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Position close failed for {symbol}: {e}")
    
    async def start_real_trading(self):
        """Start the real trading system"""
        self.logger.info("🚀 STARTING REAL TRADING SYSTEM")
        
        # Safety confirmation for live trading
        if not self.use_testnet:
            print("\n🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK! 🚨")
            print(f"Account Balance: ${self.risk_manager.current_balance:.2f}")
            print(f"Max Daily Loss: ${self.risk_manager.max_daily_loss:.2f}")
            print(f"Position Size: ${self.position_size_usd:.2f}")
            
            confirm = input("Type 'YES' to confirm live trading with real money: ")
            if confirm != 'YES':
                self.logger.info("❌ Live trading cancelled by user")
                return
        
        self.is_trading = True
        self.binance.is_connected = True
        
        try:
            # Start WebSocket streams for all symbols
            websocket_tasks = []
            for symbol in self.symbols:
                # Ticker stream
                ticker_task = asyncio.create_task(
                    self.binance.start_ticker_stream(symbol)
                )
                websocket_tasks.append(ticker_task)
                
                # Depth stream
                depth_task = asyncio.create_task(
                    self.binance.start_depth_stream(symbol)
                )
                websocket_tasks.append(depth_task)
            
            # Start monitoring tasks
            async def exit_monitor():
                """Monitor exit conditions"""
                while self.is_trading:
                    await self._check_exit_conditions()
                    await asyncio.sleep(2)  # Check every 2 seconds
            
            async def performance_monitor():
                """Monitor and log performance"""
                while self.is_trading:
                    await asyncio.sleep(60)  # Log every minute
                    
                    uptime = time.time() - self.start_time
                    win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
                    
                    self.logger.info(f"📊 REAL PERFORMANCE UPDATE:")
                    self.logger.info(f"   Uptime: {uptime/60:.1f} minutes")
                    self.logger.info(f"   Total Trades: {self.total_trades}")
                    self.logger.info(f"   Winning Trades: {self.winning_trades}")
                    self.logger.info(f"   Win Rate: {win_rate:.1f}%")
                    self.logger.info(f"   Daily P&L: ${self.risk_manager.daily_pnl:.2f}")
                    self.logger.info(f"   Total P&L: ${self.risk_manager.total_pnl:.2f}")
                    self.logger.info(f"   Active Positions: {len(self.positions)}")
                    self.logger.info(f"   Signals Generated: {self.scalping_engine.signal_count}")
            
            async def risk_monitor():
                """Monitor risk conditions"""
                while self.is_trading:
                    if self.risk_manager.should_emergency_stop():
                        self.logger.critical("🚨 EMERGENCY STOP TRIGGERED!")
                        self.is_trading = False
                        break
                    await asyncio.sleep(10)  # Check every 10 seconds
            
            # Combine all tasks
            monitoring_tasks = [
                asyncio.create_task(exit_monitor()),
                asyncio.create_task(performance_monitor()),
                asyncio.create_task(risk_monitor())
            ]
            
            all_tasks = websocket_tasks + monitoring_tasks
            
            # Run all tasks
            await asyncio.gather(*all_tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ REAL trading stopped by user")
        finally:
            await self._shutdown_system()
    
    async def _shutdown_system(self):
        """Safely shutdown the trading system"""
        self.logger.info("🔒 Shutting down REAL trading system...")
        
        self.is_trading = False
        
        # Close all open positions
        if self.positions:
            self.logger.info(f"🔒 Closing {len(self.positions)} open positions...")
            for symbol in list(self.positions.keys()):
                await self._close_position(symbol, "System shutdown")
        
        # Close Binance connections
        await self.binance.close()
        
        # Print final report
        self._print_final_report()
    
    def _print_final_report(self):
        """Print comprehensive final trading report"""
        uptime = time.time() - self.start_time
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        
        print("\n" + "="*80)
        print("📊 FINAL REAL TRADING REPORT")
        print("="*80)
        print(f"Environment: {'TESTNET' if self.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
        print(f"Trading Session Duration: {uptime/60:.1f} minutes ({uptime/3600:.2f} hours)")
        print(f"Symbols Traded: {', '.join(self.symbols)}")
        print()
        print("TRADING PERFORMANCE:")
        print(f"  Total Trades Executed: {self.total_trades}")
        print(f"  Winning Trades: {self.winning_trades}")
        print(f"  Losing Trades: {self.total_trades - self.winning_trades}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print()
        print("FINANCIAL RESULTS:")
        print(f"  Initial Balance: ${self.risk_manager.initial_balance:.2f}")
        print(f"  Final Balance: ${self.risk_manager.current_balance:.2f}")
        print(f"  Daily P&L: ${self.risk_manager.daily_pnl:.2f}")
        print(f"  Total P&L: ${self.risk_manager.total_pnl:.2f}")
        print(f"  Return: {(self.risk_manager.total_pnl/self.risk_manager.initial_balance)*100:.2f}%")
        print()
        print("SIGNAL ANALYSIS:")
        print(f"  Total Signals Generated: {self.scalping_engine.signal_count}")
        print(f"  Signal-to-Trade Ratio: {(self.total_trades/max(self.scalping_engine.signal_count, 1))*100:.1f}%")
        print()
        print("RISK MANAGEMENT:")
        print(f"  Max Daily Loss Limit: ${self.risk_manager.max_daily_loss:.2f}")
        print(f"  Peak Balance: ${self.risk_manager.peak_balance:.2f}")
        print(f"  Max Drawdown: {((self.risk_manager.peak_balance - min(self.risk_manager.current_balance, self.risk_manager.peak_balance))/self.risk_manager.peak_balance)*100:.2f}%")
        print("="*80)
    
    async def test_connection(self):
        """Test real API connection"""
        try:
            account_info = await self.binance.get_account_info()
            balance = float(account_info['totalWalletBalance'])
            
            print("✅ REAL API CONNECTION TEST PASSED")
            print(f"   Account Balance: ${balance:.2f}")
            print(f"   Environment: {'Testnet' if self.use_testnet else 'Live Production'}")
            print(f"   API Endpoint: {self.binance.base_url}")
            print(f"   WebSocket Endpoint: {self.binance.ws_base}")
            
            return True
            
        except Exception as e:
            print(f"❌ REAL API CONNECTION FAILED: {e}")
            print("\n🔧 TROUBLESHOOTING STEPS:")
            print("   1. Verify API keys in .env file")
            print("   2. Check API key permissions (futures trading required)")
            print("   3. Verify IP whitelist settings (if enabled)")
            print("   4. Confirm testnet vs live environment")
            print("   5. Check internet connection")
            
            return False
    
    async def monitor_data_only(self):
        """Monitor real market data without trading"""
        print("📊 Starting REAL market data monitoring...")
        print("   Live data from Binance WebSocket streams")
        print("   Signal analysis enabled (no trading)")
        print("   Press Ctrl+C to stop")
        
        self.binance.is_connected = True
        
        # Enhanced monitoring callback
        async def monitoring_callback(tick: RealTick):
            print(f"📊 REAL: {tick.symbol} = ${tick.price:.4f} | Vol: {tick.volume:.0f} | Spread: ${tick.spread:.6f}")
            
            # Show signal analysis
            signal = self.scalping_engine.process_tick(tick)
            if signal:
                print(f"   ⚡ SIGNAL: {signal['signal_type']} | Strength: {signal['strength']:.3f} | {', '.join(signal['reasoning'][:2])}")
        
        self.binance.tick_callback = monitoring_callback
        
        try:
            # Start WebSocket streams
            tasks = []
            for symbol in self.symbols:
                task = asyncio.create_task(self.binance.start_ticker_stream(symbol))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            print("⏹️ Market data monitoring stopped")
        finally:
            await self.binance.close()