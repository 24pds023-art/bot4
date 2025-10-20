#!/usr/bin/env python3
"""
🧪 WEBSOCKET CONNECTION TEST
===========================
Test the improved WebSocket connection
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.improved_trading_system import ImprovedTradingSystem

async def test_websocket():
    """Test WebSocket connection"""
    print("🧪 Testing improved WebSocket connection...")
    
    try:
        # Initialize system
        system = ImprovedTradingSystem()
        balance = await system.initialize()
        
        print(f"✅ System initialized - Balance: ${balance:.2f}")
        
        # Test connection
        connection_ok = await system.test_connection()
        
        if connection_ok:
            print("✅ Connection test passed")
            
            # Test short data monitoring
            print("📊 Testing data stream for 30 seconds...")
            
            # Set up monitoring
            message_count = 0
            
            async def count_messages(tick):
                nonlocal message_count
                message_count += 1
                if message_count <= 5:  # Show first 5 messages
                    print(f"📊 {tick.symbol}: ${tick.price:.4f} | 24h: {tick.change_24h:+.2f}%")
            
            system.binance.tick_callback = count_messages
            system.binance.is_connected = True
            
            # Run for 30 seconds
            try:
                await asyncio.wait_for(
                    system.binance.start_simple_stream(system.symbols),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                print(f"✅ WebSocket test completed - Received {message_count} messages")
            
            await system.binance.close()
            
            if message_count > 0:
                print("✅ WebSocket connection working properly!")
                return True
            else:
                print("❌ No messages received")
                return False
        else:
            print("❌ Connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_websocket())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test stopped by user")
        sys.exit(0)