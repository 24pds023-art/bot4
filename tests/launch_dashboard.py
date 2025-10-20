#!/usr/bin/env python3
"""
🔥 DASHBOARD LAUNCHER
====================
Launch the real-time trading dashboard
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.improved_trading_system import ImprovedTradingSystem
from utils.real_time_dashboard import start_dashboard

async def main():
    """Launch dashboard with trading system"""
    print("🔥 LAUNCHING REAL-TIME TRADING DASHBOARD")
    print("=" * 50)
    
    try:
        # Initialize trading system
        print("🚀 Initializing trading system...")
        system = ImprovedTradingSystem()
        await system.initialize()
        
        print(f"✅ Trading system initialized")
        print(f"   Environment: {'TESTNET' if system.use_testnet else 'LIVE'}")
        print(f"   Balance: ${system.risk_manager.current_balance:.2f}")
        
        # Start dashboard
        print("🌐 Starting dashboard server...")
        dashboard, runner, update_task = await start_dashboard(system, port=8080)
        
        print("✅ Dashboard launched successfully!")
        print(f"   URL: http://localhost:8080")
        print(f"   WebSocket: ws://localhost:8080/ws")
        print()
        print("🎯 Dashboard Features:")
        print("   • Real-time P&L tracking")
        print("   • Live position monitoring")
        print("   • Signal visualization")
        print("   • Performance charts")
        print("   • Emergency stop controls")
        print()
        print("Press Ctrl+C to stop...")
        
        # Keep running
        try:
            await update_task
        except KeyboardInterrupt:
            print("\n⏹️ Dashboard stopped by user")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)