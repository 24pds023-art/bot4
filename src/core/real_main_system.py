#!/usr/bin/env python3
"""
REAL MAIN TRADING SYSTEM
========================
🔥 COMPLETE REAL TRADING SYSTEM - NO SIMULATIONS
⚡ REAL Binance API integration
📊 REAL market data processing
💰 REAL order execution
🎯 REAL risk management
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from .real_trading_engine import RealTradingEngine
from .real_binance_connector import RealBinanceConnector

class RealTradingSystem:
    """COMPLETE REAL TRADING SYSTEM"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get REAL API credentials
        self.api_key = os.getenv('BINANCE_API_KEY') or os.getenv('BINANCE_TESTNET_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET') or os.getenv('BINANCE_TESTNET_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API credentials not found! Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env file")
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.trading_engine = None
        
        # Setup logging
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        
        print("🔥 REAL TRADING SYSTEM INITIALIZED")
        print(f"   Environment: {'TESTNET' if self.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
        print(f"   API Key: {self.api_key[:8]}...")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML files"""
        config = {}
        
        config_dir = Path(__file__).parent.parent.parent / 'config'
        
        # Load all config files
        config_files = [
            'trading_config.yaml',
            'risk_config.yaml', 
            'system_config.yaml'
        ]
        
        for config_file in config_files:
            config_path = config_dir / config_file
            if config_path.exists():
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    config.update(file_config)
                    print(f"✅ Loaded config: {config_file}")
            else:
                print(f"⚠️ Config file not found: {config_file}")
        
        return config
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'real_trading.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    async def initialize(self):
        """Initialize REAL trading system"""
        self.logger.info("🚀 Initializing REAL Trading System...")
        
        # Initialize trading engine with REAL credentials
        self.trading_engine = RealTradingEngine(
            api_key=self.api_key,
            api_secret=self.api_secret,
            testnet=self.use_testnet
        )
        
        # Apply configuration
        if 'trading' in self.config:
            trading_config = self.config['trading']
            self.trading_engine.symbols = trading_config.get('symbols', self.trading_engine.symbols)
            self.trading_engine.position_size_usd = trading_config.get('base_position_usd', 100.0)
            self.trading_engine.leverage = trading_config.get('leverage', 10)
        
        if 'position_risk' in self.config:
            risk_config = self.config['position_risk']
            self.trading_engine.risk_manager.max_daily_loss = risk_config.get('max_daily_loss', 1000.0)
        
        # Initialize trading engine
        await self.trading_engine.initialize()
        
        self.logger.info("✅ REAL Trading System initialized")
    
    async def run_real_trading(self):
        """Run REAL trading system"""
        self.logger.info("🚀 STARTING REAL TRADING")
        
        if not self.use_testnet:
            self.logger.warning("🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK! 🚨")
        
        try:
            # Start REAL trading
            await self.trading_engine.start_real_trading()
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Trading stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Trading system error: {e}")
            raise
        finally:
            if self.trading_engine:
                await self.trading_engine.stop_real_trading()
    
    async def run_market_data_only(self):
        """Run market data monitoring only (no trading)"""
        self.logger.info("📊 Starting REAL market data monitoring (no trading)")
        
        # Initialize Binance connector
        connector = RealBinanceConnector(self.api_key, self.api_secret, self.use_testnet)
        await connector.initialize()
        
        # Set up data callbacks
        async def on_tick(tick_data):
            print(f"📊 {tick_data.symbol}: ${tick_data.price:.4f}")
        
        async def on_orderbook(orderbook_data):
            if orderbook_data.bids and orderbook_data.asks:
                spread = orderbook_data.asks[0][0] - orderbook_data.bids[0][0]
                print(f"📈 {orderbook_data.symbol} Spread: ${spread:.4f}")
        
        connector.set_callbacks(tick_callback=on_tick, orderbook_callback=on_orderbook)
        
        try:
            # Start market data streams
            symbols = self.config.get('trading', {}).get('symbols', ['BTCUSDT', 'ETHUSDT'])
            await connector.start_real_websockets(symbols)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ Market data monitoring stopped")
        finally:
            await connector.close()
    
    async def test_connection(self):
        """Test REAL API connection"""
        self.logger.info("🧪 Testing REAL API connection...")
        
        try:
            # Test connection
            connector = RealBinanceConnector(self.api_key, self.api_secret, self.use_testnet)
            await connector.initialize()
            
            # Get account info
            account_info = await connector.get_account_info()
            balance = float(account_info['totalWalletBalance'])
            
            self.logger.info("✅ API CONNECTION TEST PASSED")
            self.logger.info(f"   Account Balance: ${balance:.2f}")
            self.logger.info(f"   Environment: {'Testnet' if self.use_testnet else 'Live Production'}")
            
            await connector.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ API CONNECTION TEST FAILED: {e}")
            return False

def print_banner():
    """Print system banner"""
    print("\n" + "="*80)
    print("🔥 REAL ULTRA-FAST SCALPING TRADING SYSTEM")
    print("="*80)
    print("⚡ REAL Binance WebSocket connections")
    print("📊 REAL market data processing")
    print("💰 REAL order execution")
    print("🎯 REAL risk management")
    print("🚀 NO SIMULATIONS - 100% LIVE TRADING")
    print("="*80)

async def main():
    """Main entry point"""
    print_banner()
    
    # Check for required files
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
            print("\n🎯 REAL TRADING SYSTEM MENU:")
            print("1. 🔥 Start REAL Trading (Execute real trades)")
            print("2. 📊 Market Data Only (Monitor prices)")
            print("3. 🧪 Test API Connection")
            print("4. ❌ Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                print("\n⚠️  WARNING: This will execute REAL trades with REAL money!")
                if system.use_testnet:
                    print("✅ Using TESTNET - Safe to proceed")
                else:
                    print("🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK!")
                
                confirm = input("Continue? (y/N): ").strip().lower()
                if confirm == 'y':
                    await system.run_real_trading()
                else:
                    print("❌ Trading cancelled")
            
            elif choice == '2':
                await system.run_market_data_only()
            
            elif choice == '3':
                await system.test_connection()
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option")
    
    except Exception as e:
        print(f"❌ System error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
        sys.exit(0)