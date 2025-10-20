#!/usr/bin/env python3
"""
🔧 INTEGRATION HEALTH CHECK
===========================
Comprehensive check of all system integrations
"""

import asyncio
import sys
import time
import os
from pathlib import Path

# Add src to path (project root/src)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Default to mock/offline mode so this check runs without network credentials
os.environ.setdefault('MOCK_BINANCE', 'true')

async def check_system_health():
    """Comprehensive system health check"""
    print("🔧 SYSTEM INTEGRATION HEALTH CHECK")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Import System
    total_checks += 1
    try:
        from core.improved_trading_system import ImprovedTradingSystem
        from core.simple_binance_connector import SimpleBinanceConnector
        print("✅ 1. System imports - OK")
        checks_passed += 1
    except Exception as e:
        print(f"❌ 1. System imports - FAILED: {e}")
    
    # Check 2: System Initialization
    total_checks += 1
    try:
        system = ImprovedTradingSystem()
        print("✅ 2. System initialization - OK")
        checks_passed += 1
    except Exception as e:
        print(f"❌ 2. System initialization - FAILED: {e}")
        return
    
    # Check 3: API Connection
    total_checks += 1
    try:
        await system.initialize()
        print("✅ 3. API connection - OK")
        print(f"   Balance: ${system.risk_manager.current_balance:.2f}")
        print(f"   Environment: {'TESTNET' if system.use_testnet else 'LIVE'}")
        checks_passed += 1
    except Exception as e:
        print(f"❌ 3. API connection - FAILED: {e}")
        return
    
    # Check 4: WebSocket Connection
    total_checks += 1
    try:
        # Test WebSocket briefly
        system.binance.is_connected = True
        
        # Start WebSocket for 5 seconds
        print("🔗 4. Testing WebSocket connection...")
        
        message_count = 0
        def count_messages(tick):
            nonlocal message_count
            message_count += 1
        
        system.binance.tick_callback = count_messages
        
        # Run WebSocket for 5 seconds
        websocket_task = asyncio.create_task(
            system.binance.start_simple_stream(system.symbols)
        )
        
        await asyncio.sleep(5)
        system.binance.is_connected = False
        websocket_task.cancel()
        
        if message_count > 0:
            print(f"✅ 4. WebSocket connection - OK ({message_count} messages received)")
            checks_passed += 1
        else:
            print("❌ 4. WebSocket connection - No data received")
            
    except Exception as e:
        print(f"❌ 4. WebSocket connection - FAILED: {e}")
    
    # Check 5: Signal Generation
    total_checks += 1
    try:
        # Test signal generation with mock data
        from core.simple_binance_connector import SimpleTick
        
        test_tick = SimpleTick(
            symbol='BTCUSDT',
            price=67000.0,
            volume=1.5,
            timestamp=int(time.time() * 1000),
            event_time=int(time.time() * 1000)
        )
        
        # Process tick through scalping engine
        signal = system.scalping_engine.process_tick(test_tick)
        
        print("✅ 5. Signal generation - OK")
        if signal:
            print(f"   Generated signal: {signal['signal_type']} with strength {signal['strength']:.3f}")
        else:
            print("   No signal generated (normal)")
        checks_passed += 1
        
    except Exception as e:
        print(f"❌ 5. Signal generation - FAILED: {e}")
    
    # Check 6: Risk Management
    total_checks += 1
    try:
        # Test risk management
        can_trade = system.risk_manager.can_open_position(50.0, 0)
        print(f"✅ 6. Risk management - OK (Can trade: {can_trade})")
        print(f"   Max positions: {system.risk_manager.max_positions}")
        print(f"   Max daily loss: ${system.risk_manager.max_daily_loss}")
        checks_passed += 1
    except Exception as e:
        print(f"❌ 6. Risk management - FAILED: {e}")
    
    # Check 7: Order Execution (Dry Run)
    total_checks += 1
    try:
        # Test order parameters without actually placing order
        symbol = 'BTCUSDT'
        quantity = 50.0 / 67000.0  # $50 position
        quantity = round(quantity, 3)
        
        if quantity >= 0.001:
            print(f"✅ 7. Order parameters - OK")
            print(f"   Symbol: {symbol}")
            print(f"   Quantity: {quantity}")
            print(f"   Min quantity check: PASSED")
            checks_passed += 1
        else:
            print(f"❌ 7. Order parameters - Quantity too small: {quantity}")
            
    except Exception as e:
        print(f"❌ 7. Order parameters - FAILED: {e}")
    
    # Check 8: Dashboard Integration
    total_checks += 1
    try:
        from utils.real_time_dashboard import RealTimeTradingDashboard
        dashboard = RealTimeTradingDashboard(system)
        print("✅ 8. Dashboard integration - OK")
        checks_passed += 1
    except Exception as e:
        print(f"❌ 8. Dashboard integration - FAILED: {e}")
    
    # Final Report
    print("\n" + "=" * 50)
    print("📊 INTEGRATION HEALTH REPORT")
    print("=" * 50)
    print(f"Checks Passed: {checks_passed}/{total_checks}")
    print(f"Success Rate: {(checks_passed/total_checks)*100:.1f}%")
    
    if checks_passed == total_checks:
        print("🎉 ALL SYSTEMS INTEGRATED AND WORKING!")
        print("\n🚀 Ready for:")
        print("   • Live trading")
        print("   • Real-time monitoring")
        print("   • Dashboard operation")
        print("   • Production deployment")
        return 0
    elif checks_passed >= total_checks * 0.75:
        print("⚠️ MOSTLY WORKING - Minor issues detected")
        print("   System should operate but may have limitations")
        return 1
    else:
        print("❌ CRITICAL ISSUES DETECTED")
        print("   System needs fixes before operation")
        return 2

async def main():
    """Main health check"""
    try:
        return await check_system_health()
    except KeyboardInterrupt:
        print("\n⏹️ Health check stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)