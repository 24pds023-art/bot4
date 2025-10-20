#!/usr/bin/env python3
"""
🔥 IMPROVED REAL TRADING SYSTEM
===============================
Simplified, reliable trading system with better error handling
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

from .simple_binance_connector import SimpleBinanceConnector, SimpleScalpingSignals, SimpleTick, MockSimpleBinanceConnector

@dataclass
class SimplePosition:
    """Simple position tracking"""
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

class SimpleRiskManager:
    """Simple risk management"""
    
    def __init__(self, initial_balance: float, max_daily_loss: float = 100.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.max_positions = 3
        
    def can_open_position(self, position_size: float, current_positions: int) -> bool:
        """Check if position can be opened"""
        if current_positions >= self.max_positions:
            return False
        if self.daily_pnl <= -self.max_daily_loss:
            return False
        if position_size > self.current_balance * 0.02:  # Max 2% per position
            return False
        return True
    
    def update_balance(self, pnl: float):
        """Update balance"""
        self.daily_pnl += pnl
        self.total_pnl += pnl
        self.current_balance = self.initial_balance + self.total_pnl

class ImprovedTradingSystem:
    """Improved, simplified trading system"""
    
    def __init__(self):
        # Load environment
        load_dotenv()
        
        # Get API credentials
        self.api_key = os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_TESTNET_API_SECRET') or os.getenv('BINANCE_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'

        # Determine offline/mock mode BEFORE enforcing credentials
        offline_mode = (
            os.getenv('NO_NETWORK', 'false').lower() == 'true'
            or os.getenv('OFFLINE', 'false').lower() == 'true'
            or os.getenv('MOCK_BINANCE', 'false').lower() == 'true'
        )

        if (not self.api_key or not self.api_secret) and not offline_mode:
            raise ValueError("❌ API credentials not found! Please configure .env file or set MOCK_BINANCE=true for offline mode")
        
        # Initialize components
        # Allow offline/mock mode when NO_NETWORK or OFFLINE is set, or when explicit
        # MOCK_BINANCE=true. This enables local testing without API keys/connectivity.

        if offline_mode:
            self.binance = MockSimpleBinanceConnector(self.api_key or '', self.api_secret or '', True)
        else:
            self.binance = SimpleBinanceConnector(self.api_key, self.api_secret, self.use_testnet)
        self.scalping_engine = SimpleScalpingSignals()
        
        # Trading configuration
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.position_size_usd = float(os.getenv('BASE_POSITION_USD', 50))
        
        # Trading state
        self.is_trading = False
        self.positions: Dict[str, SimplePosition] = {}
        self.risk_manager = None
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.start_time = time.time()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/improved_trading.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔥 Improved Trading System initialized")
        self.logger.info(f"   Environment: {'TESTNET' if self.use_testnet else 'LIVE'}")
        self.logger.info(f"   Symbols: {self.symbols}")
        self.logger.info(f"   Position Size: ${self.position_size_usd}")
    
    async def initialize(self):
        """Initialize the system"""
        self.logger.info("🚀 Initializing Improved Trading System...")
        
        # Initialize Binance connector
        await self.binance.initialize()
        
        # Get account balance
        balance = await self.binance.get_account_balance()
        
        # Initialize risk manager
        self.risk_manager = SimpleRiskManager(
            initial_balance=balance,
            max_daily_loss=float(os.getenv('MAX_DAILY_LOSS', 100))
        )
        
        # Set tick callback
        self.binance.tick_callback = self._on_tick
        
        self.logger.info(f"✅ System initialized - Balance: ${balance:.2f}")
        return balance
    
    async def _on_tick(self, tick: SimpleTick):
        """Process incoming tick data"""
        try:
            # Update positions
            if tick.symbol in self.positions:
                self.positions[tick.symbol].update_pnl(tick.price)
            
            # Generate signals if trading
            if self.is_trading:
                signal = self.scalping_engine.process_tick(tick)
                
                if signal and signal['strength'] > 0.6:
                    await self._process_signal(tick.symbol, signal, tick.price)
                    
        except Exception as e:
            self.logger.error(f"❌ Error processing tick for {tick.symbol}: {e}")
    
    async def _process_signal(self, symbol: str, signal: Dict, current_price: float):
        """Process trading signal"""
        try:
            # Skip if already in position
            if symbol in self.positions:
                return
            
            # Risk check
            if not self.risk_manager.can_open_position(self.position_size_usd, len(self.positions)):
                return
            
            # Calculate quantity
            quantity = self.position_size_usd / current_price
            quantity = round(quantity, 3)
            
            if quantity < 0.001:
                return
            
            self.logger.info(f"🚀 EXECUTING ORDER: {symbol} {signal['signal_type']} {quantity}")
            self.logger.info(f"   Signal: {signal['strength']:.3f} | {', '.join(signal['reasoning'][:2])}")
            
            # Execute order
            order_result = await self.binance.place_market_order(
                symbol=symbol,
                side=signal['signal_type'],
                quantity=quantity
            )
            
            if order_result:
                # Create position
                position = SimplePosition(
                    symbol=symbol,
                    side='LONG' if signal['signal_type'] == 'BUY' else 'SHORT',
                    quantity=quantity,
                    entry_price=current_price,
                    current_price=current_price,
                    pnl=0.0,
                    entry_time=datetime.now(),
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit']
                )
                
                self.positions[symbol] = position
                self.total_trades += 1
                
                self.logger.info(f"✅ POSITION OPENED: {symbol}")
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
                
                # Stop loss
                if ((position.side == 'LONG' and position.current_price <= position.stop_loss) or
                    (position.side == 'SHORT' and position.current_price >= position.stop_loss)):
                    should_close = True
                    reason = "Stop loss"
                
                # Take profit
                elif ((position.side == 'LONG' and position.current_price >= position.take_profit) or
                      (position.side == 'SHORT' and position.current_price <= position.take_profit)):
                    should_close = True
                    reason = "Take profit"
                
                # Time limit
                elif datetime.now() - position.entry_time > timedelta(minutes=15):
                    should_close = True
                    reason = "Time limit"
                
                if should_close:
                    await self._close_position(symbol, reason)
                    
        except Exception as e:
            self.logger.error(f"❌ Error checking exits: {e}")
    
    async def _close_position(self, symbol: str, reason: str):
        """Close position with better error handling"""
        try:
            position = self.positions[symbol]
            close_side = 'SELL' if position.side == 'LONG' else 'BUY'
            
            self.logger.info(f"🔒 CLOSING POSITION: {symbol} - {reason}")
            
            # Execute close order
            order_result = await self.binance.place_market_order(
                symbol=symbol,
                side=close_side,
                quantity=position.quantity
            )
            
            if order_result:
                # Update metrics
                final_pnl = position.pnl
                self.risk_manager.update_balance(final_pnl)
                
                if final_pnl > 0:
                    self.winning_trades += 1
                
                # Remove position
                del self.positions[symbol]
                
                self.logger.info(f"✅ POSITION CLOSED: {symbol}")
                self.logger.info(f"   P&L: ${final_pnl:.2f}")
                self.logger.info(f"   Reason: {reason}")
                self.logger.info(f"   Total P&L: ${self.risk_manager.total_pnl:.2f}")
                
            else:
                # Order failed but we still need to handle the position
                self.logger.warning(f"⚠️ Close order failed for {symbol}, but continuing...")
                
                # For critical situations (like emergency stop), force remove position
                if "emergency" in reason.lower() or "shutdown" in reason.lower():
                    final_pnl = position.pnl
                    self.risk_manager.update_balance(final_pnl)
                    del self.positions[symbol]
                    self.logger.warning(f"⚠️ POSITION FORCE CLOSED: {symbol} (P&L: ${final_pnl:.2f})")
                
        except Exception as e:
            self.logger.error(f"❌ Position close failed for {symbol}: {e}")
            
            # For critical situations, force close position to prevent stuck positions
            if symbol in self.positions and ("emergency" in reason.lower() or "shutdown" in reason.lower()):
                position = self.positions[symbol]
                final_pnl = position.pnl
                self.risk_manager.update_balance(final_pnl)
                del self.positions[symbol]
                self.logger.warning(f"⚠️ POSITION EMERGENCY CLOSED: {symbol} (P&L: ${final_pnl:.2f})")
    
    async def start_trading(self):
        """Start trading"""
        self.logger.info("🚀 STARTING IMPROVED TRADING SYSTEM")
        
        if not self.use_testnet:
            print("\n🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK! 🚨")
            confirm = input("Type 'YES' to confirm: ")
            if confirm != 'YES':
                return
        
        self.is_trading = True
        self.binance.is_connected = True
        
        try:
            # Start WebSocket stream
            stream_task = asyncio.create_task(
                self.binance.start_simple_stream(self.symbols)
            )
            
            # Start monitoring tasks
            async def exit_monitor():
                while self.is_trading:
                    await self._check_exits()
                    await asyncio.sleep(5)
            
            async def performance_monitor():
                while self.is_trading:
                    await asyncio.sleep(60)
                    
                    uptime = time.time() - self.start_time
                    win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
                    
                    self.logger.info(f"📊 PERFORMANCE UPDATE:")
                    self.logger.info(f"   Uptime: {uptime/60:.1f} min")
                    self.logger.info(f"   Trades: {self.total_trades}")
                    self.logger.info(f"   Win Rate: {win_rate:.1f}%")
                    self.logger.info(f"   P&L: ${self.risk_manager.total_pnl:.2f}")
                    self.logger.info(f"   Active: {len(self.positions)}")
                    self.logger.info(f"   Signals: {self.scalping_engine.signal_count}")
            
            # Run all tasks
            await asyncio.gather(
                stream_task,
                asyncio.create_task(exit_monitor()),
                asyncio.create_task(performance_monitor()),
                return_exceptions=True
            )
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Trading stopped by user")
        finally:
            await self._shutdown()
    
    async def _shutdown(self):
        """Shutdown system"""
        self.logger.info("🔒 Shutting down system...")
        
        self.is_trading = False
        
        # Close positions
        for symbol in list(self.positions.keys()):
            await self._close_position(symbol, "System shutdown")
        
        # Close connections
        await self.binance.close()
        
        # Final report
        self._print_final_report()
    
    def _print_final_report(self):
        """Print final report"""
        uptime = time.time() - self.start_time
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        
        print("\n" + "="*60)
        print("📊 IMPROVED TRADING SYSTEM REPORT")
        print("="*60)
        print(f"Environment: {'TESTNET' if self.use_testnet else 'LIVE'}")
        print(f"Session Duration: {uptime/60:.1f} minutes")
        print(f"Total Trades: {self.total_trades}")
        print(f"Winning Trades: {self.winning_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${self.risk_manager.total_pnl:.2f}")
        print(f"Signals Generated: {self.scalping_engine.signal_count}")
        print("="*60)
    
    async def test_connection(self):
        """Test connection"""
        try:
            balance = await self.binance.get_account_balance()
            
            print("✅ IMPROVED SYSTEM CONNECTION TEST PASSED")
            print(f"   Balance: ${balance:.2f}")
            print(f"   Environment: {'TESTNET' if self.use_testnet else 'LIVE'}")
            print(f"   Symbols: {', '.join(self.symbols)}")
            
            return True
            
        except Exception as e:
            print(f"❌ CONNECTION TEST FAILED: {e}")
            return False
    
    async def monitor_data_only(self):
        """Monitor data without trading"""
        print("📊 Starting improved data monitoring...")
        print("   Press Ctrl+C to stop")
        
        self.binance.is_connected = True
        
        # Set monitoring callback
        async def monitor_callback(tick: SimpleTick):
            print(f"📊 {tick.symbol}: ${tick.price:.4f} | Vol: {tick.volume:.0f} | 24h: {tick.change_24h:+.2f}%")
            
            # Show signals
            signal = self.scalping_engine.process_tick(tick)
            if signal:
                print(f"   ⚡ SIGNAL: {signal['signal_type']} | {signal['strength']:.3f} | {', '.join(signal['reasoning'][:2])}")
        
        self.binance.tick_callback = monitor_callback
        
        try:
            await self.binance.start_simple_stream(self.symbols)
        except KeyboardInterrupt:
            print("⏹️ Monitoring stopped")
        finally:
            await self.binance.close()