#!/usr/bin/env python3
"""
🔥 COMPLETE REAL TRADING SYSTEM
==============================
⚡ 100% REAL - NO SIMULATIONS
💰 REAL Binance API integration
📊 REAL market data & order execution
🎯 FULLY INTEGRATED SYSTEM
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

# Set high precision
getcontext().prec = 18

# Load environment
load_dotenv()

@dataclass
class RealTick:
    """Real tick data"""
    symbol: str
    price: float
    volume: float
    timestamp: int
    event_time: int

@dataclass
class RealOrder:
    """Real order result"""
    symbol: str
    order_id: int
    side: str
    quantity: float
    price: float
    status: str
    execution_time: float

@dataclass
class RealPosition:
    """Real position"""
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    
    def update_pnl(self, current_price: float):
        self.current_price = current_price
        if self.side == 'LONG':
            self.pnl = (current_price - self.entry_price) * self.quantity
        else:
            self.pnl = (self.entry_price - current_price) * self.quantity

class RealBinanceAPI:
    """REAL Binance API connector"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.ws_base = "wss://stream.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
            self.ws_base = "wss://fstream.binance.com"
        
        self.session = None
        self.is_connected = False
        self.tick_callback = None
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize API connection"""
        self.session = aiohttp.ClientSession(
            headers={'X-MBX-APIKEY': self.api_key},
            timeout=aiohttp.ClientTimeout(total=10)
        )
        
        # Test connection
        await self._test_connection()
        self.logger.info("✅ REAL Binance API initialized")
    
    async def _test_connection(self):
        """Test API connection"""
        url = f"{self.base_url}/fapi/v1/ping"
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"API test failed: {response.status}")
    
    def _create_signature(self, params: Dict) -> str:
        """Create API signature"""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def get_account_balance(self) -> float:
        """Get REAL account balance"""
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
                    raise Exception(f"API Error: {error}")
        except Exception as e:
            self.logger.error(f"❌ Error getting balance: {e}")
            raise
    
    async def place_market_order(self, symbol: str, side: str, quantity: float) -> RealOrder:
        """Place REAL market order"""
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
                        side=data['side'],
                        quantity=float(data['origQty']),
                        price=float(data.get('avgPrice', 0)),
                        status=data['status'],
                        execution_time=execution_time
                    )
                else:
                    error = await response.json()
                    raise Exception(f"Order failed: {error}")
                    
        except Exception as e:
            self.logger.error(f"❌ Order execution failed: {e}")
            raise
    
    async def start_websocket(self, symbol: str):
        """Start REAL WebSocket stream"""
        stream_name = f"{symbol.lower()}@ticker"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20) as ws:
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        data = json.loads(message)
                        tick = RealTick(
                            symbol=data['s'],
                            price=float(data['c']),
                            volume=float(data['v']),
                            timestamp=int(time.time() * 1000),
                            event_time=data['E']
                        )
                        
                        if self.tick_callback:
                            await self.tick_callback(tick)
                            
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ WebSocket error: {e}")
                    await asyncio.sleep(5)
    
    async def close(self):
        """Close connections"""
        self.is_connected = False
        if self.session:
            await self.session.close()

class SimpleScalpingSignals:
    """Simple but effective scalping signals"""
    
    def __init__(self):
        self.price_history = defaultdict(lambda: deque(maxlen=50))
        self.volume_history = defaultdict(lambda: deque(maxlen=20))
        self.signal_count = 0
    
    def process_tick(self, tick: RealTick) -> Optional[Dict]:
        """Generate REAL scalping signals"""
        symbol = tick.symbol
        price = tick.price
        volume = tick.volume
        
        # Store history
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)
        
        if len(self.price_history[symbol]) < 20:
            return None
        
        prices = list(self.price_history[symbol])
        volumes = list(self.volume_history[symbol])
        
        # Calculate indicators
        current_price = prices[-1]
        sma_5 = sum(prices[-5:]) / 5
        sma_10 = sum(prices[-10:]) / 10
        sma_20 = sum(prices[-20:]) / 20
        
        # Price momentum
        momentum = (current_price - prices[-10]) / prices[-10]
        
        # Volume analysis
        avg_volume = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else volume
        volume_spike = volume > avg_volume * 1.5
        
        # Generate signals
        signal = None
        
        # Momentum + Moving Average Signal
        if current_price > sma_5 > sma_10 and momentum > 0.001:  # 0.1% momentum
            signal = {
                'signal_type': 'BUY',
                'strength': min(abs(momentum) * 500, 1.0),
                'confidence': 0.7,
                'entry_price': current_price,
                'stop_loss': current_price * 0.998,  # 0.2% stop
                'take_profit': current_price * 1.004,  # 0.4% profit
                'reasoning': f'Momentum: {momentum:.4f}, MA alignment'
            }
        
        elif current_price < sma_5 < sma_10 and momentum < -0.001:
            signal = {
                'signal_type': 'SELL',
                'strength': min(abs(momentum) * 500, 1.0),
                'confidence': 0.7,
                'entry_price': current_price,
                'stop_loss': current_price * 1.002,  # 0.2% stop
                'take_profit': current_price * 0.996,  # 0.4% profit
                'reasoning': f'Momentum: {momentum:.4f}, MA alignment'
            }
        
        # Volume spike confirmation
        if signal and volume_spike:
            signal['strength'] = min(signal['strength'] * 1.2, 1.0)
            signal['confidence'] = min(signal['confidence'] * 1.1, 1.0)
            signal['reasoning'] += ', Volume spike'
        
        if signal:
            self.signal_count += 1
        
        return signal

class RealTradingSystem:
    """COMPLETE REAL TRADING SYSTEM"""
    
    def __init__(self):
        # Get REAL API credentials
        self.api_key = os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_TESTNET_API_SECRET') or os.getenv('BINANCE_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API credentials not found in .env file!")
        
        # Initialize components
        self.binance = RealBinanceAPI(self.api_key, self.api_secret, self.use_testnet)
        self.scalping_engine = SimpleScalpingSignals()
        
        # Trading state
        self.is_trading = False
        self.positions: Dict[str, RealPosition] = {}
        self.trades = []
        
        # Configuration
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.position_size_usd = float(os.getenv('BASE_POSITION_USD', 50))
        self.max_positions = int(os.getenv('MAX_POSITIONS', 3))
        
        # Risk management
        self.account_balance = 0.0
        self.total_pnl = 0.0
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 100))
        self.daily_pnl = 0.0
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.start_time = time.time()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        print("🔥 REAL Trading System initialized")
        print(f"   Environment: {'TESTNET' if self.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
        print(f"   API Key: {self.api_key[:8]}...")
        print(f"   Symbols: {self.symbols}")
        print(f"   Position Size: ${self.position_size_usd}")
    
    async def initialize(self):
        """Initialize REAL system"""
        self.logger.info("🚀 Initializing REAL Trading System...")
        
        # Initialize Binance API
        await self.binance.initialize()
        
        # Get REAL account balance
        self.account_balance = await self.binance.get_account_balance()
        
        # Set tick callback
        self.binance.tick_callback = self._on_real_tick
        
        self.logger.info(f"✅ REAL system initialized - Balance: ${self.account_balance:.2f}")
    
    async def _on_real_tick(self, tick: RealTick):
        """Process REAL tick data"""
        try:
            # Update position P&L
            if tick.symbol in self.positions:
                self.positions[tick.symbol].update_pnl(tick.price)
            
            # Generate REAL signals
            if self.is_trading and len(self.positions) < self.max_positions:
                signal = self.scalping_engine.process_tick(tick)
                
                if signal and signal['strength'] > 0.5:
                    await self._execute_real_trade(tick.symbol, signal, tick.price)
                    
        except Exception as e:
            self.logger.error(f"❌ Error processing tick: {e}")
    
    async def _execute_real_trade(self, symbol: str, signal: Dict, current_price: float):
        """Execute REAL trade"""
        try:
            # Skip if already in position
            if symbol in self.positions:
                return
            
            # Calculate position size
            quantity = self.position_size_usd / current_price
            quantity = round(quantity, 3)  # Round to 3 decimals
            
            if quantity < 0.001:  # Minimum quantity
                return
            
            # Risk check
            if self.daily_pnl < -self.max_daily_loss:
                self.logger.warning("⚠️ Daily loss limit reached")
                return
            
            self.logger.info(f"🚀 EXECUTING REAL ORDER: {symbol} {signal['signal_type']} {quantity}")
            
            # Place REAL order
            order = await self.binance.place_market_order(
                symbol=symbol,
                side=signal['signal_type'],
                quantity=quantity
            )
            
            if order.status in ['FILLED', 'PARTIALLY_FILLED']:
                # Create REAL position
                position = RealPosition(
                    symbol=symbol,
                    side='LONG' if signal['signal_type'] == 'BUY' else 'SHORT',
                    quantity=order.quantity,
                    entry_price=current_price,
                    current_price=current_price,
                    pnl=0.0,
                    entry_time=datetime.now(),
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit']
                )
                
                self.positions[symbol] = position
                self.total_trades += 1
                
                self.logger.info(f"✅ REAL POSITION OPENED:")
                self.logger.info(f"   Symbol: {symbol}")
                self.logger.info(f"   Side: {position.side}")
                self.logger.info(f"   Quantity: {position.quantity}")
                self.logger.info(f"   Entry: ${position.entry_price:.4f}")
                self.logger.info(f"   Stop: ${position.stop_loss:.4f}")
                self.logger.info(f"   Target: ${position.take_profit:.4f}")
                self.logger.info(f"   Reasoning: {signal['reasoning']}")
                
        except Exception as e:
            self.logger.error(f"❌ REAL trade execution failed: {e}")
    
    async def _check_exits(self):
        """Check REAL exit conditions"""
        try:
            for symbol, position in list(self.positions.items()):
                should_close = False
                reason = ""
                
                # Stop loss
                if ((position.side == 'LONG' and position.current_price <= position.stop_loss) or
                    (position.side == 'SHORT' and position.current_price >= position.stop_loss)):
                    should_close = True
                    reason = "Stop loss triggered"
                
                # Take profit
                elif ((position.side == 'LONG' and position.current_price >= position.take_profit) or
                      (position.side == 'SHORT' and position.current_price <= position.take_profit)):
                    should_close = True
                    reason = "Take profit triggered"
                
                # Time limit (5 minutes for scalping)
                elif datetime.now() - position.entry_time > timedelta(minutes=5):
                    should_close = True
                    reason = "Time limit exceeded"
                
                if should_close:
                    await self._close_real_position(symbol, reason)
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking exits: {e}")
    
    async def _close_real_position(self, symbol: str, reason: str):
        """Close REAL position"""
        try:
            position = self.positions[symbol]
            close_side = 'SELL' if position.side == 'LONG' else 'BUY'
            
            self.logger.info(f"🔒 CLOSING REAL POSITION: {symbol} - {reason}")
            
            # Execute REAL close order
            order = await self.binance.place_market_order(
                symbol=symbol,
                side=close_side,
                quantity=position.quantity
            )
            
            if order.status in ['FILLED', 'PARTIALLY_FILLED']:
                # Record final P&L
                final_pnl = position.pnl
                self.total_pnl += final_pnl
                self.daily_pnl += final_pnl
                
                if final_pnl > 0:
                    self.winning_trades += 1
                
                # Remove position
                del self.positions[symbol]
                
                self.logger.info(f"✅ REAL POSITION CLOSED:")
                self.logger.info(f"   P&L: ${final_pnl:.2f}")
                self.logger.info(f"   Reason: {reason}")
                self.logger.info(f"   Total P&L: ${self.total_pnl:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Position close failed: {e}")
    
    async def start_real_trading(self):
        """Start REAL trading system"""
        self.logger.info("🚀 STARTING REAL TRADING SYSTEM")
        
        if not self.use_testnet:
            print("\n🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK! 🚨")
            confirm = input("Type 'YES' to confirm live trading with real money: ")
            if confirm != 'YES':
                print("❌ Live trading cancelled")
                return
        
        self.is_trading = True
        self.binance.is_connected = True
        
        try:
            # Start WebSocket streams
            websocket_tasks = [
                asyncio.create_task(self.binance.start_websocket(symbol))
                for symbol in self.symbols
            ]
            
            # Start exit monitoring
            async def exit_monitor():
                while self.is_trading:
                    await self._check_exits()
                    await asyncio.sleep(5)  # Check every 5 seconds
            
            # Start performance monitoring
            async def performance_monitor():
                while self.is_trading:
                    await asyncio.sleep(60)  # Log every minute
                    
                    win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
                    uptime = time.time() - self.start_time
                    
                    self.logger.info(f"📊 REAL PERFORMANCE:")
                    self.logger.info(f"   Uptime: {uptime/60:.1f} minutes")
                    self.logger.info(f"   Trades: {self.total_trades}")
                    self.logger.info(f"   Win Rate: {win_rate:.1f}%")
                    self.logger.info(f"   P&L: ${self.total_pnl:.2f}")
                    self.logger.info(f"   Active Positions: {len(self.positions)}")
                    self.logger.info(f"   Signals Generated: {self.scalping_engine.signal_count}")
            
            # Run all tasks
            all_tasks = websocket_tasks + [
                asyncio.create_task(exit_monitor()),
                asyncio.create_task(performance_monitor())
            ]
            
            await asyncio.gather(*all_tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ REAL trading stopped by user")
        finally:
            await self._shutdown()
    
    async def _shutdown(self):
        """Shutdown system"""
        self.is_trading = False
        
        # Close all positions
        if self.positions:
            self.logger.info("🔒 Closing all positions...")
            for symbol in list(self.positions.keys()):
                await self._close_real_position(symbol, "System shutdown")
        
        # Close connections
        await self.binance.close()
        
        # Final report
        self._print_final_report()
    
    def _print_final_report(self):
        """Print final trading report"""
        uptime = time.time() - self.start_time
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        
        print("\n" + "="*60)
        print("📊 FINAL REAL TRADING REPORT")
        print("="*60)
        print(f"Environment: {'TESTNET' if self.use_testnet else 'LIVE PRODUCTION'}")
        print(f"Uptime: {uptime/60:.1f} minutes")
        print(f"Total Trades: {self.total_trades}")
        print(f"Winning Trades: {self.winning_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${self.total_pnl:.2f}")
        print(f"Daily P&L: ${self.daily_pnl:.2f}")
        print(f"Signals Generated: {self.scalping_engine.signal_count}")
        print("="*60)
    
    async def test_connection(self):
        """Test REAL API connection"""
        try:
            balance = await self.binance.get_account_balance()
            
            print("✅ REAL API CONNECTION TEST PASSED")
            print(f"   Account Balance: ${balance:.2f}")
            print(f"   Environment: {'Testnet' if self.use_testnet else 'Live Production'}")
            print(f"   API Endpoint: {self.binance.base_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ REAL API CONNECTION FAILED: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Check your API keys in .env file")
            print("   2. Ensure API keys have futures trading permissions")
            print("   3. Check if IP is whitelisted (if enabled)")
            print("   4. Verify testnet vs live environment settings")
            
            return False
    
    async def monitor_data_only(self):
        """Monitor REAL market data only (no trading)"""
        print("📊 Starting REAL market data monitoring...")
        print("   This will show live price data from Binance")
        print("   No trades will be executed")
        
        self.binance.is_connected = True
        
        # Enhanced tick callback for monitoring
        async def monitor_callback(tick: RealTick):
            print(f"📊 REAL DATA: {tick.symbol} = ${tick.price:.4f} (Volume: {tick.volume:.0f})")
            
            # Show signal analysis
            signal = self.scalping_engine.process_tick(tick)
            if signal:
                print(f"   ⚡ SIGNAL: {signal['signal_type']} | Strength: {signal['strength']:.3f} | {signal['reasoning']}")
        
        self.binance.tick_callback = monitor_callback
        
        try:
            # Start WebSocket streams
            tasks = [
                asyncio.create_task(self.binance.start_websocket(symbol))
                for symbol in self.symbols
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            print("⏹️ Market data monitoring stopped")
        finally:
            await self.binance.close()

def print_banner():
    """Print system banner"""
    print("\n" + "🔥"*50)
    print("🔥 COMPLETE REAL ULTRA-FAST SCALPING SYSTEM 🔥")
    print("🔥"*50)
    print("✅ REAL Binance WebSocket connections")
    print("✅ REAL order execution with live API")
    print("✅ REAL market data processing")
    print("✅ REAL risk management")
    print("✅ REAL P&L tracking")
    print("✅ NO SIMULATIONS - 100% LIVE TRADING")
    print("🔥"*50)

def check_setup():
    """Check system setup"""
    print("🔍 Checking system setup...")
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("\n🔧 Quick fix:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env with your Binance API keys")
        return False
    
    # Check API keys
    load_dotenv()
    api_key = os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
    if not api_key or 'your_' in api_key:
        print("❌ API keys not configured!")
        print("\n🔧 Please edit .env file with your real Binance API keys")
        return False
    
    print("✅ System setup looks good")
    return True

async def main():
    """Main function"""
    print_banner()
    
    # Check setup
    if not check_setup():
        return 1
    
    try:
        # Initialize REAL system
        system = RealTradingSystem()
        await system.initialize()
        
        # Show menu
        while True:
            print(f"\n🎯 REAL TRADING SYSTEM MENU:")
            print(f"   Current Balance: ${system.account_balance:.2f}")
            print(f"   Environment: {'TESTNET' if system.use_testnet else '🚨 LIVE 🚨'}")
            print()
            print("1. 🔥 Start REAL Trading (Execute real orders)")
            print("2. 📊 Monitor Data Only (Live prices, no trading)")
            print("3. 🧪 Test API Connection")
            print("4. ❌ Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                print(f"\n⚠️  This will execute REAL trades!")
                print(f"   Environment: {'TESTNET (Safe)' if system.use_testnet else '🚨 LIVE PRODUCTION (Real Money!) 🚨'}")
                print(f"   Position Size: ${system.position_size_usd}")
                print(f"   Max Positions: {system.max_positions}")
                
                confirm = input("Continue? (y/N): ").strip().lower()
                if confirm == 'y':
                    await system.start_real_trading()
                else:
                    print("❌ Trading cancelled")
            
            elif choice == '2':
                await system.monitor_data_only()
            
            elif choice == '3':
                await system.test_connection()
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option")
        
        return 0
        
    except Exception as e:
        print(f"❌ System error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
        sys.exit(0)