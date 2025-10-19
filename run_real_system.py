#!/usr/bin/env python3
"""
🔥 REAL TRADING SYSTEM LAUNCHER
==============================
⚡ SIMPLIFIED LAUNCHER WITH PROPER IMPORTS
💰 REAL BINANCE API INTEGRATION
📊 HANDLES ALL IMPORT ISSUES
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Any
import json
import time
import hmac
import hashlib
import aiohttp
import websockets
from urllib.parse import urlencode
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, getcontext
import yaml
from dotenv import load_dotenv

# Set high precision for financial calculations
getcontext().prec = 18

# Load environment variables
load_dotenv()

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
    order_ids: List[int]
    
    def update_pnl(self, current_price: float):
        """Update position P&L with current price"""
        self.current_price = current_price
        
        if self.side == 'LONG':
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:  # SHORT
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity

class SimpleBinanceConnector:
    """Simplified REAL Binance connector"""
    
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
        
        self.session = None
        self.is_connected = False
        self.tick_callback = None
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize connection"""
        self.logger.info("🚀 Initializing REAL Binance connection...")
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'X-MBX-APIKEY': self.api_key}
        )
        
        # Test connectivity
        await self._test_connectivity()
        self.logger.info("✅ REAL Binance connection initialized")
    
    async def _test_connectivity(self):
        """Test API connectivity"""
        try:
            url = f"{self.base_url}/fapi/v1/ping"
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"API test failed: {response.status}")
                self.logger.info("✅ API connectivity test passed")
        except Exception as e:
            self.logger.error(f"❌ API connectivity test failed: {e}")
            raise
    
    def set_tick_callback(self, callback):
        """Set tick data callback"""
        self.tick_callback = callback
    
    async def start_websocket(self, symbol: str):
        """Start REAL WebSocket for symbol"""
        stream_name = f"{symbol.lower()}@ticker"
        url = f"{self.ws_base}/ws/{stream_name}"
        
        while self.is_connected:
            try:
                self.logger.info(f"🔗 Connecting to REAL ticker stream: {symbol}")
                
                async with websockets.connect(url, ping_interval=20) as ws:
                    async for message in ws:
                        if not self.is_connected:
                            break
                        
                        data = json.loads(message)
                        tick_data = RealTickData(
                            symbol=data['s'],
                            price=float(data['c']),
                            quantity=float(data['v']),
                            timestamp=int(time.time() * 1000),
                            is_buyer_maker=False,
                            trade_id=0,
                            event_time=data['E']
                        )
                        
                        if self.tick_callback:
                            await self.tick_callback(tick_data)
                            
            except Exception as e:
                if self.is_connected:
                    self.logger.error(f"❌ WebSocket error for {symbol}: {e}")
                    await asyncio.sleep(5)
    
    def _create_signature(self, params: Dict[str, Any]) -> str:
        """Create HMAC signature"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def place_order(self, symbol: str, side: str, quantity: float) -> RealOrderResult:
        """Place REAL order"""
        try:
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
                if response.status == 200:
                    data = await response.json()
                    
                    return RealOrderResult(
                        symbol=data['symbol'],
                        order_id=data['orderId'],
                        client_order_id=data['clientOrderId'],
                        side=data['side'],
                        order_type=data['type'],
                        quantity=float(data['origQty']),
                        price=float(data.get('price', 0)),
                        status=data['status'],
                        fills=data.get('fills', []),
                        commission=0.0,
                        commission_asset='',
                        execution_time=0.0
                    )
                else:
                    error_data = await response.json()
                    raise Exception(f"Order failed: {error_data}")
                    
        except Exception as e:
            self.logger.error(f"❌ Order execution failed: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            params = {'timestamp': int(time.time() * 1000)}
            params['signature'] = self._create_signature(params)
            
            url = f"{self.base_url}/fapi/v2/account"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise Exception(f"Failed to get account info: {error_data}")
        except Exception as e:
            self.logger.error(f"❌ Error getting account info: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        self.is_connected = False
        if self.session:
            await self.session.close()

class SimpleScalpingEngine:
    """Simple scalping signal generator"""
    
    def __init__(self):
        self.price_history = {}
        self.signal_count = 0
    
    def process_tick(self, tick_data: RealTickData):
        """Process tick and generate signals"""
        symbol = tick_data.symbol
        price = tick_data.price
        
        # Store price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        if len(self.price_history[symbol]) > 20:
            self.price_history[symbol].pop(0)
        
        # Simple signal generation
        if len(self.price_history[symbol]) >= 10:
            recent_prices = self.price_history[symbol][-10:]
            
            # Simple momentum signal
            if recent_prices[-1] > recent_prices[-5] * 1.001:  # 0.1% move up
                self.signal_count += 1
                return {
                    'signal_type': 'BUY',
                    'strength': 0.6,
                    'confidence': 0.7,
                    'entry_price': price,
                    'stop_loss': price * 0.998,
                    'take_profit': price * 1.004
                }
            elif recent_prices[-1] < recent_prices[-5] * 0.999:  # 0.1% move down
                self.signal_count += 1
                return {
                    'signal_type': 'SELL',
                    'strength': 0.6,
                    'confidence': 0.7,
                    'entry_price': price,
                    'stop_loss': price * 1.002,
                    'take_profit': price * 0.996
                }
        
        return None

class RealTradingSystem:
    """Complete REAL trading system"""
    
    def __init__(self):
        # Get API credentials
        self.api_key = os.getenv('BINANCE_API_KEY') or os.getenv('BINANCE_TESTNET_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET') or os.getenv('BINANCE_TESTNET_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API credentials not found! Please set them in .env file")
        
        # Initialize components
        self.binance = SimpleBinanceConnector(self.api_key, self.api_secret, self.use_testnet)
        self.scalping_engine = SimpleScalpingEngine()
        
        # Trading state
        self.is_trading = False
        self.positions = {}
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        # Configuration
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.position_size_usd = 50.0  # Start small
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print("🔥 REAL Trading System initialized")
        print(f"   Environment: {'TESTNET' if self.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
    
    async def initialize(self):
        """Initialize system"""
        await self.binance.initialize()
        
        # Set tick callback
        self.binance.set_tick_callback(self._on_tick)
        
        # Get account info
        account_info = await self.binance.get_account_info()
        balance = float(account_info['totalWalletBalance'])
        
        self.logger.info(f"✅ Account Balance: ${balance:.2f}")
    
    async def _on_tick(self, tick_data: RealTickData):
        """Process real tick data"""
        try:
            # Update position P&L
            if tick_data.symbol in self.positions:
                self.positions[tick_data.symbol].update_pnl(tick_data.price)
            
            # Generate signals
            if self.is_trading:
                signal = self.scalping_engine.process_tick(tick_data)
                if signal:
                    await self._process_signal(tick_data.symbol, signal, tick_data.price)
                    
        except Exception as e:
            self.logger.error(f"❌ Error processing tick: {e}")
    
    async def _process_signal(self, symbol: str, signal: dict, current_price: float):
        """Process trading signal"""
        try:
            # Check if already in position
            if symbol in self.positions:
                return
            
            # Calculate position size
            quantity = self.position_size_usd / current_price
            quantity = round(quantity, 3)  # Round to 3 decimals
            
            if quantity < 0.001:  # Minimum quantity
                return
            
            self.logger.info(f"🚀 EXECUTING REAL ORDER: {symbol} {signal['signal_type']} {quantity}")
            
            # Execute REAL order
            order_result = await self.binance.place_order(
                symbol=symbol,
                side=signal['signal_type'],
                quantity=quantity
            )
            
            if order_result.status in ['FILLED', 'PARTIALLY_FILLED']:
                # Create position
                position = RealPosition(
                    symbol=symbol,
                    side='LONG' if signal['signal_type'] == 'BUY' else 'SHORT',
                    quantity=order_result.quantity,
                    entry_price=current_price,
                    current_price=current_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    entry_time=datetime.now(),
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit'],
                    order_ids=[order_result.order_id]
                )
                
                self.positions[symbol] = position
                self.total_trades += 1
                
                self.logger.info(f"✅ REAL POSITION OPENED: {symbol}")
                self.logger.info(f"   Side: {position.side}")
                self.logger.info(f"   Entry: ${position.entry_price:.4f}")
                self.logger.info(f"   Stop: ${position.stop_loss:.4f}")
                self.logger.info(f"   Target: ${position.take_profit:.4f}")
                
        except Exception as e:
            self.logger.error(f"❌ Signal processing failed: {e}")
    
    async def _check_exits(self):
        """Check exit conditions"""
        try:
            for symbol, position in list(self.positions.items()):
                should_close = False
                reason = ""
                
                # Stop loss check
                if position.side == 'LONG' and position.current_price <= position.stop_loss:
                    should_close = True
                    reason = "Stop loss"
                elif position.side == 'SHORT' and position.current_price >= position.stop_loss:
                    should_close = True
                    reason = "Stop loss"
                
                # Take profit check
                if position.side == 'LONG' and position.current_price >= position.take_profit:
                    should_close = True
                    reason = "Take profit"
                elif position.side == 'SHORT' and position.current_price <= position.take_profit:
                    should_close = True
                    reason = "Take profit"
                
                # Time-based exit
                hold_time = datetime.now() - position.entry_time
                if hold_time > timedelta(minutes=5):
                    should_close = True
                    reason = "Time limit"
                
                if should_close:
                    await self._close_position(symbol, reason)
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking exits: {e}")
    
    async def _close_position(self, symbol: str, reason: str):
        """Close position"""
        try:
            position = self.positions[symbol]
            close_side = 'SELL' if position.side == 'LONG' else 'BUY'
            
            self.logger.info(f"🔒 CLOSING POSITION: {symbol} - {reason}")
            
            # Execute close order
            order_result = await self.binance.place_order(
                symbol=symbol,
                side=close_side,
                quantity=position.quantity
            )
            
            if order_result.status in ['FILLED', 'PARTIALLY_FILLED']:
                # Calculate P&L
                pnl = position.unrealized_pnl
                self.total_pnl += pnl
                
                if pnl > 0:
                    self.winning_trades += 1
                
                # Remove position
                del self.positions[symbol]
                
                self.logger.info(f"✅ POSITION CLOSED: {symbol}")
                self.logger.info(f"   P&L: ${pnl:.2f}")
                self.logger.info(f"   Total P&L: ${self.total_pnl:.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Position close failed: {e}")
    
    async def start_trading(self):
        """Start REAL trading"""
        self.logger.info("🚀 STARTING REAL TRADING")
        
        if not self.use_testnet:
            print("\n🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK! 🚨")
            confirm = input("Type 'YES' to confirm live trading: ")
            if confirm != 'YES':
                return
        
        self.is_trading = True
        self.binance.is_connected = True
        
        try:
            # Start WebSocket connections
            tasks = []
            for symbol in self.symbols:
                task = asyncio.create_task(self.binance.start_websocket(symbol))
                tasks.append(task)
            
            # Start exit checking
            async def exit_checker():
                while self.is_trading:
                    await self._check_exits()
                    await asyncio.sleep(5)
            
            tasks.append(asyncio.create_task(exit_checker()))
            
            # Start performance monitoring
            async def performance_monitor():
                while self.is_trading:
                    await asyncio.sleep(60)
                    win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
                    self.logger.info(f"📊 Performance: {self.total_trades} trades, {win_rate:.1f}% win rate, ${self.total_pnl:.2f} P&L")
            
            tasks.append(asyncio.create_task(performance_monitor()))
            
            # Run all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Trading stopped by user")
        finally:
            await self.stop_trading()
    
    async def stop_trading(self):
        """Stop trading"""
        self.is_trading = False
        
        # Close all positions
        for symbol in list(self.positions.keys()):
            await self._close_position(symbol, "System shutdown")
        
        await self.binance.close()
        
        # Final report
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        print(f"\n📊 FINAL REPORT:")
        print(f"   Total Trades: {self.total_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total P&L: ${self.total_pnl:.2f}")
    
    async def test_connection(self):
        """Test API connection"""
        try:
            account_info = await self.binance.get_account_info()
            balance = float(account_info['totalWalletBalance'])
            
            print("✅ API CONNECTION TEST PASSED")
            print(f"   Balance: ${balance:.2f}")
            print(f"   Environment: {'Testnet' if self.use_testnet else 'Live'}")
            return True
        except Exception as e:
            print(f"❌ API CONNECTION FAILED: {e}")
            return False
    
    async def monitor_data_only(self):
        """Monitor market data only"""
        print("📊 Starting market data monitoring...")
        
        self.binance.is_connected = True
        
        async def data_monitor(symbol):
            await self.binance.start_websocket(symbol)
        
        try:
            tasks = [asyncio.create_task(data_monitor(symbol)) for symbol in self.symbols]
            await asyncio.gather(*tasks, return_exceptions=True)
        except KeyboardInterrupt:
            print("⏹️ Monitoring stopped")
        finally:
            await self.binance.close()

def print_banner():
    """Print banner"""
    print("\n" + "🔥"*30)
    print("🔥 REAL ULTRA-FAST SCALPING SYSTEM 🔥")
    print("🔥"*30)
    print("✅ REAL Binance API integration")
    print("✅ REAL WebSocket connections")
    print("✅ REAL order execution")
    print("✅ REAL risk management")
    print("✅ NO SIMULATIONS - 100% LIVE")
    print("🔥"*30)

async def main():
    """Main function"""
    print_banner()
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure your API keys")
        return 1
    
    try:
        # Initialize system
        system = RealTradingSystem()
        await system.initialize()
        
        # Show menu
        while True:
            print("\n🎯 REAL TRADING SYSTEM:")
            print("1. 🔥 Start REAL Trading")
            print("2. 📊 Monitor Data Only")
            print("3. 🧪 Test Connection")
            print("4. ❌ Exit")
            
            choice = input("\nSelect (1-4): ").strip()
            
            if choice == '1':
                await system.start_trading()
                break
            elif choice == '2':
                await system.monitor_data_only()
                break
            elif choice == '3':
                await system.test_connection()
            elif choice == '4':
                break
            else:
                print("❌ Invalid choice")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)