#!/usr/bin/env python3
"""
🔥 RUN REAL TRADING SYSTEM
=========================
⚡ COMPLETE REAL TRADING - NO SIMULATIONS
💰 REAL BINANCE API INTEGRATION
📊 REAL MARKET DATA & ORDER EXECUTION
🎯 READY FOR LIVE TRADING
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.core.real_main_system import main

def print_real_trading_banner():
    """Print real trading banner"""
    print("\n" + "🔥"*30)
    print("🔥 REAL ULTRA-FAST SCALPING SYSTEM 🔥")
    print("🔥"*30)
    print()
    print("✅ REAL Binance WebSocket connections")
    print("✅ REAL order execution with live API")  
    print("✅ REAL market data processing")
    print("✅ REAL risk management")
    print("✅ REAL P&L tracking")
    print("✅ NO SIMULATIONS - 100% LIVE")
    print()
    print("⚠️  THIS SYSTEM EXECUTES REAL TRADES")
    print("💰 REAL MONEY WILL BE AT RISK")
    print("🎯 ENSURE YOU HAVE CONFIGURED:")
    print("   • .env file with real API keys")
    print("   • config/*.yaml files")
    print("   • Risk management settings")
    print()

def check_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy .env.real to .env and configure your API keys")
        return False
    
    # Check config files
    config_dir = Path('config')
    required_configs = ['trading_config.yaml', 'risk_config.yaml', 'system_config.yaml']
    
    for config_file in required_configs:
        if not (config_dir / config_file).exists():
            print(f"❌ Config file missing: {config_file}")
            return False
    
    print("✅ All required files found")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required (current: {sys.version_info.major}.{sys.version_info.minor})")
        return False
    
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    
    return True

def show_safety_warning():
    """Show safety warning for real trading"""
    print("\n" + "⚠️ "*20)
    print("⚠️  REAL TRADING SAFETY WARNING")
    print("⚠️ "*20)
    print()
    print("This system will execute REAL trades with REAL money!")
    print()
    print("BEFORE PROCEEDING:")
    print("✅ Test on Binance TESTNET first (USE_TESTNET=true)")
    print("✅ Start with SMALL position sizes")
    print("✅ Set TIGHT risk limits")
    print("✅ Monitor the system CONTINUOUSLY")
    print("✅ Have STOP-LOSS mechanisms in place")
    print()
    print("RISKS:")
    print("❌ You can lose money quickly")
    print("❌ Market conditions can change rapidly")
    print("❌ Technical issues can cause losses")
    print("❌ No trading system is guaranteed to profit")
    print()
    print("By proceeding, you acknowledge these risks.")
    print("⚠️ "*20)

async def main_wrapper():
    """Main wrapper function"""
    print_real_trading_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ System requirements not met")
        print("Please fix the issues above and try again")
        return 1
    
    # Show safety warning
    show_safety_warning()
    
    # Get user confirmation
    print("\nDo you want to proceed with REAL trading? (type 'YES' to confirm)")
    confirmation = input("> ").strip()
    
    if confirmation != 'YES':
        print("❌ Real trading cancelled")
        return 0
    
    print("\n🚀 Starting REAL trading system...")
    
    try:
        # Run the real trading system
        return await main()
        
    except KeyboardInterrupt:
        print("\n⏹️ Real trading stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ System error: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main_wrapper())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)