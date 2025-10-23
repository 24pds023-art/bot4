#!/usr/bin/env python3
"""
Quick test to verify the fix works
"""

print("🧪 Testing if ImprovedTradingSystem accepts symbols parameter...")

try:
    from src.core.improved_trading_system import ImprovedTradingSystem
    
    # Test 1: Without symbols (should use default)
    print("\n1. Testing without symbols (default)...")
    system1 = ImprovedTradingSystem(ai_engine=None)
    print(f"   ✅ Created system with {len(system1.symbols)} symbols")
    print(f"   Default symbols: {', '.join(system1.symbols[:5])}...")
    
    # Test 2: With custom symbols
    print("\n2. Testing with custom symbols...")
    custom_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    system2 = ImprovedTradingSystem(ai_engine=None, symbols=custom_symbols)
    print(f"   ✅ Created system with {len(system2.symbols)} symbols")
    print(f"   Custom symbols: {', '.join(system2.symbols)}")
    
    # Test 3: With many symbols
    print("\n3. Testing with 50 symbols...")
    many_symbols = [f'SYM{i}USDT' for i in range(50)]
    system3 = ImprovedTradingSystem(ai_engine=None, symbols=many_symbols)
    print(f"   ✅ Created system with {len(system3.symbols)} symbols")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ ImprovedTradingSystem now accepts symbols parameter")
    print("✅ ULTIMATE_LAUNCHER should work now")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
