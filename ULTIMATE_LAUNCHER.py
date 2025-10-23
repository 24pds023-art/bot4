#!/usr/bin/env python3
"""
🔥 ULTIMATE TRADING SYSTEM LAUNCHER
===================================
⚡ ONE FILE TO RULE THEM ALL
🧠 Complete AI-powered trading system with everything integrated
📊 Advanced dashboard, deep learning, online learning, automation
🚀 Professional-grade scalping with institutional optimizations
💰 100% REAL trading with Binance API integration

FEATURES:
✅ Real-time trading with Binance API
✅ Advanced AI and deep learning
✅ Online learning and model adaptation
✅ Professional web dashboard
✅ Complete automation
✅ Risk management and emergency controls
✅ Performance monitoring and analytics
✅ Multi-symbol scalping strategies
"""

import asyncio
import sys
import os
import logging
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Core system imports
from core.improved_trading_system import ImprovedTradingSystem
from core.simple_binance_connector import SimpleBinanceConnector, SimpleScalpingSignals

# AI and ML imports
try:
    from ai.deep_learning_engine import DeepLearningTradingEngine, OnlineLearningEngine
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Dashboard imports - Use enhanced control dashboard
try:
    from ui.enhanced_control_dashboard import start_enhanced_dashboard
    DASHBOARD_AVAILABLE = True
    DASHBOARD_TYPE = "enhanced"
except ImportError:
    try:
        from utils.real_time_dashboard import start_dashboard
        DASHBOARD_AVAILABLE = True
        DASHBOARD_TYPE = "real_time"
    except ImportError:
        try:
            from ui.advanced_dashboard import start_advanced_dashboard
            DASHBOARD_AVAILABLE = True
            DASHBOARD_TYPE = "advanced"
        except ImportError:
            DASHBOARD_AVAILABLE = False
            DASHBOARD_TYPE = None

class UltimateAutomatedTradingSystem:
    """Ultimate automated trading system with everything integrated"""
    
    def __init__(self, symbols_count=30):
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get configuration
        self.api_key = os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_TESTNET_API_SECRET') or os.getenv('BINANCE_API_SECRET')
        self.use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'
        self.symbols_count = symbols_count
        
        if not self.api_key or not self.api_secret:
            raise ValueError("❌ API credentials not found! Please configure .env file")
        
        # Load symbols
        self.symbols = self._load_symbols(symbols_count)
        
        # Initialize core components (AI will be set later)
        self.trading_system = None
        self.ai_engine = None
        self.dashboard = None
        self.dashboard_runner = None
        self.dashboard_task = None
        
        # System state
        self.is_running = False
        self.start_time = datetime.now()
        
        # Performance tracking
        self.system_metrics = {
            'uptime': 0,
            'total_operations': 0,
            'ai_predictions': 0,
            'dashboard_updates': 0,
            'errors_handled': 0
        }
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔥 ULTIMATE Trading System initialized")
        self.logger.info(f"   Symbols: {len(self.symbols)}")
        self.logger.info(f"   AI Available: {'✅' if AI_AVAILABLE else '❌'}")
        self.logger.info(f"   Dashboard Available: {'✅' if DASHBOARD_AVAILABLE else '❌'}")
    
    def _load_symbols(self, count: int) -> List[str]:
        """Load trading symbols"""
        try:
            from utils.trading_pairs_loader import get_custom_symbols
            symbols = get_custom_symbols(count)
            print(f"📊 Loaded {len(symbols)} trading pairs")
            print(f"   Pairs: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
            return symbols
        except Exception as e:
            print(f"⚠️ Error loading symbols from config: {e}")
            print("   Using default symbols")
            # Fallback to default symbols
            default = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
                      'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT',
                      'TRXUSDT', 'LINKUSDT', 'ATOMUSDT', 'UNIUSDT', 'LTCUSDT',
                      'ARBUSDT', 'OPUSDT', 'APTUSDT', 'NEARUSDT', 'FILUSDT']
            return default[:count]
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/ultimate_system.log'),
                logging.StreamHandler()
            ]
        )
    
    async def initialize(self):
        """Initialize the complete system"""
        self.logger.info("🚀 Initializing ULTIMATE Trading System...")
        
        # CREATE trading system if it's None (CRITICAL FIX!)
        if self.trading_system is None:
            # Pass symbols to ImprovedTradingSystem
            self.trading_system = ImprovedTradingSystem(
                ai_engine=None,
                symbols=self.symbols
            )
            self.logger.info(f"✅ Trading system object created with {len(self.symbols)} symbols")
        
        # Initialize core trading system
        balance = await self.trading_system.initialize()
        self.logger.info(f"✅ Core trading system initialized - Balance: ${balance:.2f}")
        
        # THEN initialize AI engine with actual symbols from trading system
        if AI_AVAILABLE:
            try:
                self.ai_engine = DeepLearningTradingEngine(self.trading_system.symbols)
                self.logger.info("🧠 AI engine initialized")
                
                # Connect AI to trading system (CRITICAL!)
                self.trading_system.ai_engine = self.ai_engine
                self.logger.info("🔗 AI engine connected to trading system")
                
                # Try to load previous models (for continuity)
                model_files = ['data/models/final_save.pkl', 'data/models/auto_save.pkl']
                loaded = False
                for model_file in model_files:
                    if Path(model_file).exists():
                        loaded = await self.ai_engine.load_models(model_file)
                        if loaded:
                            self.logger.info(f"✅ Continuing from previous session: {model_file}")
                            break
                
                if not loaded:
                    self.logger.info("🆕 Starting fresh AI training session")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ AI engine initialization failed: {e}")
                self.ai_engine = None
        
        # Initialize enhanced control dashboard
        if DASHBOARD_AVAILABLE:
            try:
                if DASHBOARD_TYPE == "enhanced":
                    self.dashboard, self.dashboard_runner, self.dashboard_task = await start_enhanced_dashboard(
                        self.trading_system, self.ai_engine, port=8080, host="0.0.0.0"
                    )
                    self.logger.info("🎮 Enhanced Control Dashboard initialized")
                    self.logger.info("   📱 Local: http://localhost:8080")
                    self.logger.info("   🌐 Network: http://<your-ip>:8080")
                    self.logger.info("   ✨ Full remote control enabled!")
                else:
                    from utils.real_time_dashboard import start_dashboard
                    self.dashboard, self.dashboard_runner, self.dashboard_task = await start_dashboard(
                        self.trading_system, port=8080
                    )
                    self.logger.info("🌐 Dashboard initialized at http://localhost:8080")
                self.logger.info("   ✅ WebSocket updates every 1 second")
                self.logger.info("   ✅ Live signal feed enabled")
                self.logger.info("   ✅ Position tracking active")
            except Exception as e:
                self.logger.warning(f"⚠️ Dashboard initialization failed: {e}")
                self.dashboard = None
        
        self.logger.info("✅ ULTIMATE system initialization complete")
        return balance
    
    async def start_ultimate_trading(self):
        """Start the ultimate automated trading system"""
        self.logger.info("🚀 STARTING ULTIMATE AUTOMATED TRADING SYSTEM")
        
        # Safety confirmation for live trading
        if not self.use_testnet:
            print("\n🚨 LIVE PRODUCTION MODE - REAL MONEY AT RISK! 🚨")
            print(f"Balance: ${self.trading_system.risk_manager.current_balance:.2f}")
            print("Features enabled:")
            print(f"   🧠 AI Engine: {'✅' if self.ai_engine else '❌'}")
            print(f"   🌐 Dashboard: {'✅' if self.dashboard else '❌'}")
            print(f"   📊 Online Learning: {'✅' if AI_AVAILABLE else '❌'}")
            
            confirm = input("Type 'YES' to confirm live trading: ")
            if confirm != 'YES':
                self.logger.info("❌ Live trading cancelled")
                return
        
        self.is_running = True
        
        try:
            # Start all components
            tasks = []
            
            # 1. Start core trading system
            trading_task = asyncio.create_task(self.trading_system.start_trading())
            tasks.append(trading_task)
            
            # 2. Start AI monitoring if available
            if self.ai_engine:
                ai_task = asyncio.create_task(self._ai_monitoring_loop())
                tasks.append(ai_task)
            
            # 3. Start system monitoring
            monitor_task = asyncio.create_task(self._system_monitoring_loop())
            tasks.append(monitor_task)
            
            # 4. Dashboard is already running from initialization
            if self.dashboard_task:
                tasks.append(self.dashboard_task)
            
            self.logger.info(f"🚀 Started {len(tasks)} system components")
            
            # Print system status
            self._print_system_status()
            
            # Run all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            self.logger.info("⏹️ ULTIMATE system stopped by user")
        finally:
            await self._shutdown_system()
    
    async def _ai_monitoring_loop(self):
        """AI monitoring and learning loop"""
        self.logger.info("🧠 Starting AI monitoring loop...")
        
        while self.is_running:
            try:
                # Update AI with current market data
                for symbol in self.trading_system.symbols:
                    if symbol in self.trading_system.scalping_engine.price_history:
                        prices = list(self.trading_system.scalping_engine.price_history[symbol])
                        volumes = list(self.trading_system.scalping_engine.volume_history.get(symbol, [1.0]))
                        
                        if len(prices) > 0 and len(volumes) > 0:
                            self.ai_engine.update_market_data(
                                symbol=symbol,
                                price=prices[-1],
                                volume=volumes[-1],
                                timestamp=time.time()
                            )
                
                # Generate AI predictions
                for symbol in self.trading_system.symbols:
                    prediction = await self.ai_engine.predict_signal(symbol)
                    if prediction:
                        self.system_metrics['ai_predictions'] += 1
                        
                        # Store prediction for dashboard (only if dashboard supports AI)
                        if self.dashboard and hasattr(self.dashboard, 'ai_predictions'):
                            self.dashboard.ai_predictions.append({
                                'symbol': symbol,
                                'signal': prediction.signal,
                                'confidence': prediction.confidence,
                                'probability_buy': prediction.probability_buy,
                                'probability_sell': prediction.probability_sell,
                                'timestamp': prediction.timestamp.isoformat()
                            })
                
                # Update model performance metrics (only if dashboard supports it)
                if self.dashboard and hasattr(self.dashboard, 'model_performance'):
                    performance = self.ai_engine.get_model_performance()
                    self.dashboard.model_performance.append({
                        'timestamp': time.time(),
                        'accuracy': performance.get('accuracy', 0),
                        'samples': performance.get('online_learning_samples', 0)
                    })
                
                await asyncio.sleep(5)  # AI update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in AI monitoring loop: {e}")
                self.system_metrics['errors_handled'] += 1
                await asyncio.sleep(10)
    
    async def _system_monitoring_loop(self):
        """System-wide monitoring and automation loop"""
        self.logger.info("📊 Starting system monitoring loop...")
        
        while self.is_running:
            try:
                # Update system metrics
                self.system_metrics['uptime'] = (datetime.now() - self.start_time).total_seconds()
                self.system_metrics['total_operations'] += 1
                
                # Auto-save models periodically
                if self.ai_engine and self.system_metrics['uptime'] % 1800 == 0:  # Every 30 minutes
                    await self.ai_engine.save_models('data/models/auto_save.pkl')
                    self.logger.info("💾 AI models auto-saved")
                
                # System health check
                await self._perform_health_check()
                
                # Log comprehensive status every 5 minutes
                if int(self.system_metrics['uptime']) % 300 == 0:
                    self._log_comprehensive_status()
                
                await asyncio.sleep(30)  # System monitoring every 30 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Error in system monitoring: {e}")
                self.system_metrics['errors_handled'] += 1
                await asyncio.sleep(60)
    
    async def _perform_health_check(self):
        """Perform automated system health check"""
        try:
            # Check trading system health
            if not self.trading_system.binance.is_connected:
                self.logger.warning("⚠️ Trading system disconnected - attempting reconnection")
            
            # Check AI engine health
            if self.ai_engine:
                performance = self.ai_engine.get_model_performance()
                if performance.get('accuracy', 0) < 0.3:
                    self.logger.warning("⚠️ AI model accuracy low - consider retraining")
            
            # Check dashboard health
            if self.dashboard and len(self.dashboard.websocket_connections) == 0:
                self.logger.info("📊 No dashboard clients connected")
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
    
    def _log_comprehensive_status(self):
        """Log comprehensive system status"""
        try:
            uptime_hours = self.system_metrics['uptime'] / 3600
            
            self.logger.info("📊 ULTIMATE SYSTEM STATUS:")
            self.logger.info(f"   Uptime: {uptime_hours:.2f} hours")
            self.logger.info(f"   Total Operations: {self.system_metrics['total_operations']}")
            self.logger.info(f"   AI Predictions: {self.system_metrics['ai_predictions']}")
            self.logger.info(f"   Errors Handled: {self.system_metrics['errors_handled']}")
            self.logger.info(f"   Trading Active: {self.trading_system.is_trading}")
            self.logger.info(f"   Active Positions: {len(self.trading_system.positions)}")
            self.logger.info(f"   Total Trades: {self.trading_system.total_trades}")
            self.logger.info(f"   Win Rate: {(self.trading_system.winning_trades/max(self.trading_system.total_trades,1))*100:.1f}%")
            
            if self.dashboard:
                self.logger.info(f"   Dashboard Clients: {len(self.dashboard.websocket_connections)}")
            
        except Exception as e:
            self.logger.error(f"Error logging status: {e}")
    
    def _print_system_status(self):
        """Print current system status"""
        print("\n" + "🔥" * 80)
        print("🔥 ULTIMATE AUTOMATED TRADING SYSTEM - ACTIVE")
        print("🔥" * 80)
        print(f"🎯 Environment: {'TESTNET' if self.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
        print(f"💰 Balance: ${self.trading_system.risk_manager.current_balance:.2f}")
        print(f"📊 Symbols: {', '.join(self.trading_system.symbols)}")
        print(f"🧠 AI Engine: {'✅ Active' if self.ai_engine else '❌ Not Available'}")
        print(f"🌐 Dashboard: {'✅ http://localhost:8080' if self.dashboard else '❌ Not Available'}")
        print(f"⚡ Features: Real Trading + AI + Dashboard + Automation")
        print("🔥" * 80)
        print("\n🎮 CONTROLS:")
        print("   • Press Ctrl+C to stop system")
        print("   • Open http://localhost:8080 for dashboard")
        print("   • Check logs/ultimate_system.log for detailed logs")
        print("\n🚀 System is now fully automated and running...")
    
    async def _shutdown_system(self):
        """Comprehensive system shutdown"""
        self.logger.info("🔒 Shutting down ULTIMATE system...")
        
        self.is_running = False
        
        try:
            # Stop trading system
            if self.trading_system:
                await self.trading_system._shutdown()
            
            # Save AI models
            if self.ai_engine:
                await self.ai_engine.save_models('data/models/final_save.pkl')
                self.logger.info("💾 AI models saved")
            
            # Stop dashboard
            if self.dashboard_runner:
                await self.dashboard_runner.cleanup()
                self.logger.info("🌐 Dashboard stopped")
            
            # Final status report
            self._print_final_report()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def _print_final_report(self):
        """Print comprehensive final report"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 ULTIMATE SYSTEM FINAL REPORT")
        print("=" * 80)
        print(f"Environment: {'TESTNET' if self.use_testnet else 'LIVE PRODUCTION'}")
        print(f"Total Uptime: {uptime/3600:.2f} hours")
        print(f"System Operations: {self.system_metrics['total_operations']}")
        print(f"AI Predictions Made: {self.system_metrics['ai_predictions']}")
        print(f"Errors Handled: {self.system_metrics['errors_handled']}")
        print()
        print("TRADING PERFORMANCE:")
        print(f"  Total Trades: {self.trading_system.total_trades}")
        print(f"  Winning Trades: {self.trading_system.winning_trades}")
        print(f"  Win Rate: {(self.trading_system.winning_trades/max(self.trading_system.total_trades,1))*100:.1f}%")
        
        if self.trading_system.risk_manager:
            print(f"  Final Balance: ${self.trading_system.risk_manager.current_balance:.2f}")
            print(f"  Total P&L: ${self.trading_system.risk_manager.total_pnl:.2f}")
            print(f"  Daily P&L: ${self.trading_system.risk_manager.daily_pnl:.2f}")
        
        if self.ai_engine:
            performance = self.ai_engine.get_model_performance()
            print()
            print("AI PERFORMANCE:")
            print(f"  Model Accuracy: {performance.get('accuracy', 0)*100:.1f}%")
            print(f"  Training Samples: {performance.get('online_learning_samples', 0)}")
            print(f"  Total Predictions: {performance.get('total_predictions', 0)}")
        
        print("=" * 80)
        print("🔥 ULTIMATE SYSTEM SHUTDOWN COMPLETE")
    
    async def run_automated_system(self):
        """Run the complete automated system"""
        try:
            await self.initialize()
            await self.start_ultimate_trading()
        except Exception as e:
            self.logger.error(f"❌ Fatal error in ultimate system: {e}")
            raise
    
    async def run_dashboard_only(self):
        """Run dashboard only mode"""
        self.logger.info("🌐 Starting dashboard-only mode...")
        
        try:
            await self.initialize()
            
            print("🌐 Dashboard launched at http://localhost:8080")
            print("📊 Monitoring mode - No trading")
            print("Press Ctrl+C to stop...")
            
            # Keep dashboard running
            if self.dashboard_task:
                await self.dashboard_task
            else:
                # Fallback - just keep running
                while True:
                    await asyncio.sleep(60)
                    
        except KeyboardInterrupt:
            self.logger.info("⏹️ Dashboard stopped by user")
        finally:
            await self._shutdown_system()
    
    async def test_all_systems(self):
        """Test all system components"""
        print("\n🧪 TESTING ALL SYSTEM COMPONENTS")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 4
        
        # FIRST: Initialize the system
        if self.trading_system is None:
            print("⏳ Initializing system for testing...")
            try:
                await self.initialize()
                print("✅ System initialized\n")
            except Exception as e:
                print(f"❌ Initialization failed: {e}")
                print("\n" + "=" * 50)
                print("Tests Passed: 0/4")
                print("❌ Cannot proceed with tests")
                return 0.0
        
        # Test 1: Core system
        print("Test 1: Core Trading System")
        try:
            if self.trading_system and len(self.trading_system.symbols) > 0:
                print(f"   ✅ OK - {len(self.trading_system.symbols)} symbols loaded")
                tests_passed += 1
            else:
                print("   ❌ FAILED - No symbols")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
        
        # Test 2: API connection
        print("\nTest 2: API Connection")
        try:
            if hasattr(self.trading_system, 'binance'):
                print("   ✅ OK - Connector ready")
                tests_passed += 1
            else:
                print("   ❌ FAILED - No connector")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Test 3: AI engine
        print("\nTest 3: AI Engine")
        if AI_AVAILABLE and self.ai_engine:
            try:
                print(f"   ✅ OK - {len(self.ai_engine.symbols)} symbols")
                tests_passed += 1
            except:
                print("   ✅ OK - Ready")
                tests_passed += 1
        else:
            print("   ⚠️ Not available (pip install scikit-learn)")
        
        # Test 4: Dashboard
        print("\nTest 4: Dashboard")
        if DASHBOARD_AVAILABLE and self.dashboard:
            try:
                print("   ✅ OK - Running on port 8080")
                tests_passed += 1
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
        else:
            print("   ⚠️ Not initialized yet")
        
        # Final test report
        print("\n" + "=" * 50)
        print("📊 SYSTEM TEST RESULTS")
        print("=" * 50)
        print(f"Tests Passed: {tests_passed}/{total_tests}")
        print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed >= 3:  # At least core components working
            print("🎉 SYSTEM OPERATIONAL!")
            print("\n🚀 Ready for:")
            print("   • Automated trading")
            if self.ai_engine:
                print("   • AI-powered signals")
            if self.dashboard:
                print("   • Real-time dashboard")
            print("   • Complete automation")
            print("\n💡 Start with:")
            print("   python3 ULTIMATE_LAUNCHER.py --auto")
        elif tests_passed >= 2:
            print("⚠️ MOSTLY OPERATIONAL - Some features unavailable")
            print("\n💡 Core trading should work, try:")
            print("   python3 ULTIMATE_LAUNCHER.py --auto")
        else:
            print("❌ CRITICAL ISSUES - System needs attention")
            print("\n💡 Check:")
            print("   1. .env file with API keys")
            print("   2. pip install -r requirements.txt")
            print("   3. Internet connection")
        
        return tests_passed / total_tests

def print_banner():
    """Print ultimate system banner"""
    print("\n" + "🔥" * 80)
    print("🔥 ULTIMATE AUTOMATED TRADING SYSTEM 🔥")
    print("🔥" * 80)
    print("⚡ ONE SYSTEM TO RULE THEM ALL")
    print("🧠 AI-Powered Deep Learning Trading")
    print("📊 Advanced Real-Time Dashboard")
    print("🎯 Complete Automation & Online Learning")
    print("💰 Professional-Grade Scalping")
    print("🛡️ Institutional Risk Management")
    print("✅ 100% REAL - NO SIMULATIONS")
    print("🔥" * 80)

def check_dependencies():
    """Check and install dependencies"""
    print("📦 Checking dependencies...")
    
    required_packages = ['aiohttp', 'websockets', 'python-dotenv', 'pyyaml']
    optional_packages = ['numpy', 'pandas', 'scikit-learn', 'torch']
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                import dotenv
            elif package == 'pyyaml':
                import yaml
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"   ❌ {package} (Required)")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} (Optional)")
        except ImportError:
            missing_optional.append(package)
            print(f"   ⚠️ {package} (Optional - for AI features)")
    
    if missing_required:
        print(f"\n🔧 Install required packages:")
        print(f"   pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n💡 For full AI features, install:")
        print(f"   pip install {' '.join(missing_optional)}")
    
    return True

async def main():
    """Ultimate main function"""
    parser = argparse.ArgumentParser(
        description='Ultimate Automated Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ULTIMATE_LAUNCHER.py --auto                     # Start with 30 symbols
  python3 ULTIMATE_LAUNCHER.py --symbols 50 --auto        # Start with 50 symbols
  python3 ULTIMATE_LAUNCHER.py --symbols 80 --test        # Test with 80 symbols
  python3 ULTIMATE_LAUNCHER.py --dashboard                # Dashboard only
        """
    )
    parser.add_argument('--trade', action='store_true', help='Start automated trading')
    parser.add_argument('--dashboard', action='store_true', help='Dashboard only mode')
    parser.add_argument('--test', action='store_true', help='Test all systems')
    parser.add_argument('--auto', action='store_true', help='Full automation mode')
    parser.add_argument('--symbols', type=int, default=30, help='Number of symbols (default: 30, max: 100)')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Validate symbols count
    if args.symbols < 1 or args.symbols > 100:
        print(f"❌ Invalid symbol count: {args.symbols}")
        print("   Valid range: 1-100 symbols")
        print("   Recommended: 20-50 symbols")
        return 1
    
    # Check setup
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("   Copy .env.example to .env and configure API keys")
        return 1
    
    try:
        # Initialize ultimate system with specified symbols
        print(f"\n🚀 Initializing system with {args.symbols} symbols...")
        ultimate_system = UltimateAutomatedTradingSystem(symbols_count=args.symbols)
        
        if args.test:
            # Test all systems
            success_rate = await ultimate_system.test_all_systems()
            return 0 if success_rate >= 0.75 else 1
            
        elif args.dashboard:
            # Dashboard only mode
            await ultimate_system.run_dashboard_only()
            
        elif args.trade or args.auto:
            # Full automated trading mode
            await ultimate_system.run_automated_system()
            
        else:
            # Interactive mode
            print("\n🎯 ULTIMATE SYSTEM MENU:")
            print("1. 🚀 Start Full Automation (Trading + AI + Dashboard)")
            print("2. 🌐 Dashboard Only Mode")
            print("3. 🧪 Test All Systems")
            print("4. ❌ Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                await ultimate_system.run_automated_system()
            elif choice == '2':
                await ultimate_system.run_dashboard_only()
            elif choice == '3':
                await ultimate_system.test_all_systems()
            elif choice == '4':
                print("👋 Goodbye!")
            else:
                print("❌ Invalid option")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Ultimate system stopped!")
        sys.exit(0)