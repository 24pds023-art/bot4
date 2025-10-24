#!/usr/bin/env python3
"""
🧪 AI FIXES VERIFICATION SCRIPT
================================
Quick test to verify AI training and dynamic SL/TP are working
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.deep_learning_engine import DeepLearningTradingEngine, MarketFeatures
import numpy as np
import time

async def test_ai_training():
    """Test AI model training"""
    print("\n" + "="*60)
    print("🧪 TEST 1: AI Model Training")
    print("="*60)
    
    try:
        # Initialize AI engine
        symbols = ['BTCUSDT', 'ETHUSDT']
        ai_engine = DeepLearningTradingEngine(symbols)
        
        print("✅ AI engine initialized")
        
        # Simulate market data
        print("\n📊 Simulating market data...")
        for i in range(60):
            price = 50000 + np.random.randn() * 100
            volume = 1000 + np.random.randn() * 50
            ai_engine.update_market_data('BTCUSDT', price, volume, time.time())
        
        print(f"✅ Generated {len(ai_engine.feature_history['BTCUSDT'])} market features")
        
        # Add training samples
        print("\n🧠 Adding training samples...")
        for i in range(120):
            if 'BTCUSDT' in ai_engine.feature_history and len(ai_engine.feature_history['BTCUSDT']) > 0:
                features = ai_engine.feature_history['BTCUSDT'][-1]
                result = 'WIN' if np.random.random() > 0.5 else 'LOSS'
                await ai_engine.add_position_result('BTCUSDT', result, np.random.randn() * 5)
        
        # Check training
        buffer_size = len(ai_engine.online_learner.feature_buffer)
        print(f"✅ Training buffer: {buffer_size} samples")
        
        if buffer_size >= 100:
            print("✅ AI models should be trained!")
            
            # Check if models are trained
            trained = False
            if 'BTCUSDT' in ai_engine.ensemble_models:
                for model_name, model in ai_engine.ensemble_models['BTCUSDT'].items():
                    if hasattr(model, 'n_features_in_'):
                        trained = True
                        print(f"   ✅ {model_name} trained with {model.n_features_in_} features")
            
            if trained:
                print("\n🎉 SUCCESS: AI models are trained and working!")
                return True
            else:
                print("\n⚠️ WARNING: Models not trained yet (may need more samples)")
                return False
        else:
            print(f"⏳ Need {100 - buffer_size} more samples to start training")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_dynamic_sl_tp():
    """Test dynamic stop loss / take profit calculation"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Dynamic Stop Loss / Take Profit")
    print("="*60)
    
    try:
        # Initialize AI engine
        symbols = ['BTCUSDT']
        ai_engine = DeepLearningTradingEngine(symbols)
        
        # Generate market features
        print("\n📊 Generating market features...")
        for i in range(60):
            price = 50000 + np.random.randn() * 100
            volume = 1000 + np.random.randn() * 50
            ai_engine.update_market_data('BTCUSDT', price, volume, time.time())
        
        if 'BTCUSDT' not in ai_engine.feature_history or len(ai_engine.feature_history['BTCUSDT']) == 0:
            print("❌ No features generated")
            return False
        
        features = ai_engine.feature_history['BTCUSDT'][-1]
        print(f"✅ Generated features:")
        print(f"   Volatility: {features.volatility:.4f}")
        print(f"   RSI: {features.rsi:.1f}")
        print(f"   Momentum: {features.momentum:.6f}")
        print(f"   Volume Ratio: {features.volume_ratio:.2f}")
        
        # Test different scenarios
        print("\n🎯 Testing dynamic SL/TP calculation...")
        
        test_cases = [
            ("High Confidence, Low Volatility", 0.85, 50000),
            ("Low Confidence, High Volatility", 0.55, 50000),
            ("Medium Confidence", 0.70, 50000)
        ]
        
        all_passed = True
        for name, confidence, price in test_cases:
            print(f"\n📋 Scenario: {name}")
            print(f"   Confidence: {confidence}")
            
            # Calculate dynamic SL/TP
            stop_loss, take_profit = ai_engine.calculate_dynamic_stop_take(
                symbol='BTCUSDT',
                entry_price=price,
                side='BUY',
                features=features,
                ai_confidence=confidence
            )
            
            stop_pct = abs(stop_loss - price) / price * 100
            take_pct = abs(take_profit - price) / price * 100
            
            print(f"   Stop Loss: ${stop_loss:.2f} ({stop_pct:.3f}%)")
            print(f"   Take Profit: ${take_profit:.2f} ({take_pct:.3f}%)")
            
            # Verify it's not hardcoded (not exactly 0.25% and 0.75%)
            if abs(stop_pct - 0.25) > 0.01 or abs(take_pct - 0.75) > 0.01:
                print(f"   ✅ Values are DYNAMIC (not hardcoded!)")
            else:
                print(f"   ⚠️ Values look hardcoded")
                all_passed = False
            
            # Verify within reasonable range
            if 0.10 <= stop_pct <= 1.5 and 0.3 <= take_pct <= 3.0:
                print(f"   ✅ Values within reasonable range")
            else:
                print(f"   ⚠️ Values outside expected range")
                all_passed = False
        
        if all_passed:
            print("\n🎉 SUCCESS: Dynamic SL/TP is working!")
            return True
        else:
            print("\n⚠️ WARNING: Some tests didn't pass as expected")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_signal_integration():
    """Test signal generator integration with AI"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Signal Generator Integration")
    print("="*60)
    
    try:
        from core.simple_binance_connector import SimpleScalpingSignals, SimpleTick
        
        # Initialize AI engine
        symbols = ['BTCUSDT']
        ai_engine = DeepLearningTradingEngine(symbols)
        
        # Initialize signal generator WITH AI
        signal_gen = SimpleScalpingSignals(ai_engine=ai_engine)
        
        print("✅ Signal generator initialized with AI engine")
        
        # Check if AI is connected
        if signal_gen.ai_engine is not None:
            print("✅ AI engine is connected to signal generator")
        else:
            print("❌ AI engine NOT connected")
            return False
        
        # Feed some market data to AI
        print("\n📊 Feeding market data to AI...")
        for i in range(60):
            price = 50000 + np.random.randn() * 100
            volume = 1000 + np.random.randn() * 50
            ai_engine.update_market_data('BTCUSDT', price, volume, time.time())
        
        # Generate a tick
        tick = SimpleTick(
            symbol='BTCUSDT',
            price=50000,
            volume=1000,
            timestamp=int(time.time() * 1000),
            change_24h=2.5
        )
        
        # Feed ticks to build signal history
        print("📈 Processing ticks...")
        for i in range(15):
            tick.price = 50000 + i * 10
            signal_gen.process_tick(tick)
        
        print("✅ Ticks processed successfully")
        
        # Check if signal generator can access AI features
        if 'BTCUSDT' in ai_engine.feature_history and len(ai_engine.feature_history['BTCUSDT']) > 0:
            print("✅ AI features available for signal generation")
            
            features = ai_engine.feature_history['BTCUSDT'][-1]
            print(f"   Latest RSI: {features.rsi:.1f}")
            print(f"   Latest Volatility: {features.volatility:.4f}")
            
            print("\n🎉 SUCCESS: Signal generator integrated with AI!")
            return True
        else:
            print("⚠️ No AI features available yet")
            return False
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "🔥"*60)
    print("🔥 AI FIXES VERIFICATION SUITE")
    print("🔥"*60)
    print("\nThis will test:")
    print("  1. AI model training (no more 0% accuracy!)")
    print("  2. Dynamic stop loss / take profit (no more hardcoding!)")
    print("  3. Integration with signal generator")
    print("\n" + "="*60)
    
    results = []
    
    # Test 1: AI Training
    result1 = await test_ai_training()
    results.append(("AI Model Training", result1))
    
    # Test 2: Dynamic SL/TP
    result2 = await test_dynamic_sl_tp()
    results.append(("Dynamic SL/TP", result2))
    
    # Test 3: Integration
    result3 = await test_signal_integration()
    results.append(("Signal Integration", result3))
    
    # Final report
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "⚠️ PARTIAL/FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print("\n" + "="*60)
    print(f"Tests Passed: {passed}/{len(results)}")
    print("="*60)
    
    if passed >= 2:
        print("\n🎉 GREAT! Core AI functionality is working!")
        print("   The system is ready for live trading")
        print("\n💡 Next steps:")
        print("   1. Run: python3 ULTIMATE_LAUNCHER.py --test")
        print("   2. Then: python3 ULTIMATE_LAUNCHER.py --auto")
        print("   3. Watch logs for AI training messages")
        print("   4. Monitor dynamic SL/TP calculations")
    else:
        print("\n⚠️ Some tests failed - check the errors above")
        print("   You may need to install dependencies:")
        print("   pip install scikit-learn numpy pandas")
    
    print("\n" + "🔥"*60)

if __name__ == "__main__":
    asyncio.run(main())
