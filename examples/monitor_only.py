#!/usr/bin/env python3
"""
🔥 MARKET DATA MONITOR
=====================
Monitor live market data without trading
Perfect for learning and analysis
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.improved_trading_system import ImprovedTradingSystem as RealTradingSystem

async def main():
    """Monitor market data only"""
    print("🔥 ULTRA-FAST SCALPING SYSTEM - MONITOR MODE")
    print("=" * 50)
    print("📊 Live market data monitoring")
    print("⚡ Real-time signal analysis")
    print("🚫 NO TRADING - MONITORING ONLY")
    print("=" * 50)
    
    try:
        # Initialize system
        system = RealTradingSystem()
        balance = await system.initialize()
        
        print(f"✅ System initialized")
        print(f"   Account Balance: ${balance:.2f}")
        print(f"   Environment: {'TESTNET' if system.use_testnet else 'LIVE'}")
        print(f"   Monitoring: {', '.join(system.symbols)}")
        print("\n📊 Starting live data monitoring...")
        print("   Press Ctrl+C to stop\n")
        
        # Start monitoring
        await system.monitor_data_only()
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)