#!/usr/bin/env python3
"""
Basic Scalping Example
======================
Simple example demonstrating basic scalping functionality.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.improved_trading_system import ImprovedTradingSystem
from engines.ultra_scalping_engine import UltraScalpingEngine

async def basic_scalping_demo():
    """Basic scalping demonstration"""
    
    print("🚀 Basic Scalping Demo")
    print("=" * 50)
    print("This demo shows basic scalping functionality")
    print("⚠️  This is a simulation - no real trades executed")
    print()
    
    # Initialize basic scalping system
    symbols = ['BTCUSDT', 'ETHUSDT']
    system = ImprovedTradingSystem()
    
    print(f"📊 Monitoring {len(symbols)} symbols for scalping opportunities")
    print("🎯 Looking for:")
    print("   • RSI oversold/overbought conditions")
    print("   • EMA crossovers")
    print("   • Volume spikes")
    print("   • Price momentum")
    print()
    
    try:
        # Run for 30 seconds
        print("🚀 Starting scalping system (30 seconds)...")
        await system.initialize()
        await asyncio.wait_for(system.monitor_data_only(), timeout=30.0)
        
    except asyncio.TimeoutError:
        print("\n⏰ Demo completed")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user")
    
    # Get performance stats
    print("\n📊 Demo Results:")
    print("   This was a simulation demonstrating system capabilities")
    print("   In live trading, the system would:")
    print("   • Process real market data")
    print("   • Generate trading signals")
    print("   • Execute trades automatically")
    print("   • Manage risk dynamically")

async def advanced_scalping_demo():
    """Advanced scalping with multiple signal types"""
    
    print("\n🔥 Advanced Scalping Demo")
    print("=" * 50)
    
    # Initialize advanced scalping engine
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    engine = UltraScalpingEngine(symbols)
    
    print("🎯 Advanced Signal Types:")
    print("   • Tick momentum analysis")
    print("   • Price acceleration detection")
    print("   • Order flow imbalance")
    print("   • Volume spike recognition")
    print("   • Multi-factor validation")
    print()
    
    # Simulate some ticks
    print("📊 Processing sample market data...")
    
    for i in range(100):
        symbol = symbols[i % len(symbols)]
        base_price = 45000 if symbol == 'BTCUSDT' else 3000
        
        # Simulate realistic tick data
        import random
        price = base_price + random.uniform(-base_price*0.001, base_price*0.001)
        size = random.uniform(0.01, 1.0)
        is_buyer = random.random() > 0.5
        
        # Process tick
        signal = engine.process_tick(symbol, price, size, is_buyer, i)
        
        if signal and signal.strength > 0.3:
            print(f"⚡ {signal.signal_type} Signal for {symbol}:")
            print(f"   Strength: {signal.strength:.3f}")
            print(f"   Confidence: {signal.confidence:.3f}")
            print(f"   Reasoning: {', '.join(signal.reasoning[:2])}")  # Show first 2 reasons
    
    # Get performance metrics
    metrics = engine.get_performance_metrics()
    print(f"\n📊 Advanced Engine Performance:")
    print(f"   Signals Generated: {metrics['signals_generated']}")
    print(f"   Processing Rate: {metrics.get('tick_analysis_performance', {}).get('throughput_ticks_per_sec', 0):.0f} ticks/sec")

def main():
    """Main demo function"""
    print("🚀 Ultra-Fast Scalping System - Basic Examples")
    print("=" * 60)
    print()
    
    try:
        # Run basic demo
        asyncio.run(basic_scalping_demo())
        
        # Run advanced demo
        asyncio.run(advanced_scalping_demo())
        
        print("\n✅ All demos completed successfully!")
        print("\n🎯 Next Steps:")
        print("   1. Configure your API keys in .env file")
        print("   2. Test on Binance testnet first")
        print("   3. Run performance benchmarks")
        print("   4. Start with small position sizes")
        print("   5. Monitor performance closely")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())