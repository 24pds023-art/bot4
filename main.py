#!/usr/bin/env python3
"""
🔥 ULTRA-FAST SCALPING TRADING SYSTEM
====================================
⚡ Main entry point for the real trading system
💰 Professional-grade cryptocurrency scalping
📊 Institutional-level optimizations

Usage:
    python main.py              # Interactive menu
    python main.py --trade      # Start trading directly
    python main.py --monitor    # Monitor data only
    python main.py --test       # Test API connection
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import with error handling
try:
    from core.improved_trading_system import ImprovedTradingSystem as RealTradingSystem
except ImportError as e:
    try:
        # Fallback to original system
        from core.real_trading_system import RealTradingSystem
    except ImportError:
        print(f"❌ Import error: {e}")
        print("🔧 Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)

def print_banner():
    """Print system banner"""
    print("\n" + "🔥" * 60)
    print("🔥 ULTRA-FAST SCALPING TRADING SYSTEM 🔥")
    print("🔥" * 60)
    print("✅ REAL Binance WebSocket connections")
    print("✅ REAL order execution with live API")
    print("✅ REAL market data processing")
    print("✅ REAL risk management")
    print("✅ REAL P&L tracking")
    print("✅ Advanced scalping algorithms")
    print("✅ NO SIMULATIONS - 100% LIVE TRADING")
    print("🔥" * 60)

def check_setup():
    """Check system setup and requirements"""
    print("🔍 Checking system setup...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check .env file
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("\n🔧 Quick setup:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env with your Binance API keys")
        print("3. Run: python main.py")
        return False
    
    # Check API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
    if not api_key or 'your_' in api_key.lower():
        print("❌ API keys not configured!")
        print("\n🔧 Please edit .env file with your real Binance API keys")
        return False
    
    # Check required directories
    required_dirs = ['logs', 'data', 'config']
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ System setup verified")
    return True

async def interactive_menu():
    """Show interactive menu"""
    try:
        # Initialize system
        system = RealTradingSystem()
        balance = await system.initialize()
        
        while True:
            print(f"\n🎯 REAL TRADING SYSTEM MENU")
            print(f"   Account Balance: ${balance:.2f}")
            print(f"   Environment: {'TESTNET (Safe)' if system.use_testnet else '🚨 LIVE PRODUCTION 🚨'}")
            print(f"   Symbols: {', '.join(system.symbols)}")
            print(f"   Position Size: ${system.position_size_usd}")
            print()
            print("1. 🔥 Start REAL Trading (Execute live orders)")
            print("2. 📊 Monitor Data Only (Live prices, no trading)")
            print("3. 🧪 Test API Connection")
            print("4. ⚙️  System Information")
            print("5. ❌ Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                print(f"\n⚠️  This will execute REAL trades!")
                print(f"   Environment: {'TESTNET (Safe)' if system.use_testnet else '🚨 LIVE PRODUCTION (Real Money!) 🚨'}")
                print(f"   Max Positions: {system.risk_manager.max_positions if system.risk_manager else 'Not initialized'}")
                print(f"   Max Daily Loss: ${system.risk_manager.max_daily_loss if system.risk_manager else 'Not initialized'}")
                
                confirm = input("Continue? (y/N): ").strip().lower()
                if confirm == 'y':
                    await system.start_trading()
                    break
                else:
                    print("❌ Trading cancelled")
            
            elif choice == '2':
                await system.monitor_data_only()
            
            elif choice == '3':
                await system.test_connection()
            
            elif choice == '4':
                print_system_info(system)
            
            elif choice == '5':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option")
        
    except Exception as e:
        print(f"❌ System error: {e}")
        return 1
    
    return 0

def print_system_info(system):
    """Print detailed system information"""
    print("\n" + "="*50)
    print("⚙️  SYSTEM INFORMATION")
    print("="*50)
    print(f"Environment: {'TESTNET' if system.use_testnet else 'LIVE PRODUCTION'}")
    print(f"API Endpoint: {system.binance.base_url}")
    print(f"WebSocket: {system.binance.ws_base}")
    print(f"Trading Symbols: {', '.join(system.symbols)}")
    print(f"Position Size: ${system.position_size_usd}")
    
    if system.risk_manager:
        print(f"Max Positions: {system.risk_manager.max_positions}")
        print(f"Max Daily Loss: ${system.risk_manager.max_daily_loss}")
        print(f"Current Balance: ${system.risk_manager.current_balance:.2f}")
        print(f"Daily P&L: ${system.risk_manager.daily_pnl:.2f}")
        print(f"Total P&L: ${system.risk_manager.total_pnl:.2f}")
    else:
        print("Risk Manager: Not initialized")
    
    print("="*50)

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Ultra-Fast Scalping Trading System')
    parser.add_argument('--trade', action='store_true', help='Start trading directly')
    parser.add_argument('--monitor', action='store_true', help='Monitor data only')
    parser.add_argument('--test', action='store_true', help='Test API connection')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check setup
    if not check_setup():
        return 1
    
    try:
        if args.trade:
            # Direct trading mode
            system = RealTradingSystem()
            await system.initialize()
            await system.start_trading()
            
        elif args.monitor:
            # Monitor only mode
            system = RealTradingSystem()
            await system.initialize()
            await system.monitor_data_only()
            
        elif args.test:
            # Test connection mode
            system = RealTradingSystem()
            await system.initialize()
            await system.test_connection()
            
        else:
            # Interactive menu mode
            return await interactive_menu()
        
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
        print("\n👋 Goodbye!")
        sys.exit(0)