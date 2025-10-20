#!/usr/bin/env python3
"""
Test Real-Time Dashboard
========================
Verifies dashboard functionality and real-time updates
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def test_dashboard():
    """Test dashboard with mock trading system"""
    print("🧪 Testing Real-Time Dashboard...")
    
    try:
        # Import required modules
        from core.improved_trading_system import ImprovedTradingSystem
        from utils.real_time_dashboard import start_dashboard
        
        print("\n1️⃣ Creating mock trading system...")
        
        # Create a simple mock system for testing
        class MockTradingSystem:
            def __init__(self):
                self.positions = {}
                self.is_trading = False
                self.use_testnet = True
                self.total_trades = 0
                self.winning_trades = 0
                self.symbols = ['BTCUSDT', 'ETHUSDT']
                self.position_size_usd = 50
                
                # Create mock scalping engine
                class MockEngine:
                    def __init__(self):
                        self.signal_count = 0
                
                self.scalping_engine = MockEngine()
                
                # Create mock risk manager
                class MockRiskManager:
                    def __init__(self):
                        self.current_balance = 10000.0
                        self.daily_pnl = 0.0
                        self.total_pnl = 0.0
                
                self.risk_manager = MockRiskManager()
        
        system = MockTradingSystem()
        print("✅ Mock system created")
        
        print("\n2️⃣ Starting dashboard...")
        dashboard, runner, update_task = await start_dashboard(system, port=8081)
        print("✅ Dashboard started at http://localhost:8081")
        
        print("\n3️⃣ Simulating trading activity...")
        
        # Simulate some signals
        for i in range(5):
            signal = {
                'symbol': 'BTCUSDT',
                'signal_type': 'BUY' if i % 2 == 0 else 'SELL',
                'strength': 0.7 + (i * 0.05),
                'timestamp': asyncio.get_event_loop().time()
            }
            dashboard.signal_history.append({
                **signal,
                'timestamp': f"2025-10-20T12:{i:02d}:00"
            })
            system.scalping_engine.signal_count += 1
        
        print(f"✅ Generated {system.scalping_engine.signal_count} mock signals")
        
        # Simulate some trades
        system.total_trades = 10
        system.winning_trades = 7
        system.risk_manager.total_pnl = 125.50
        system.risk_manager.daily_pnl = 45.25
        
        print("✅ Simulated trading activity")
        
        print("\n4️⃣ Dashboard is running!")
        print("=" * 60)
        print("📊 Dashboard URL: http://localhost:8081")
        print("🔌 WebSocket: ws://localhost:8081/ws")
        print("📡 API Status: http://localhost:8081/api/status")
        print("=" * 60)
        print("\n✨ Features to test:")
        print("  • Open dashboard in browser")
        print("  • Check real-time metrics update")
        print("  • Verify signals appear")
        print("  • Test emergency stop button")
        print("  • Monitor WebSocket connection")
        print("\n⏹️  Press Ctrl+C to stop...")
        
        # Keep running
        try:
            await update_task
        except KeyboardInterrupt:
            print("\n\n⏹️  Shutting down dashboard...")
        finally:
            await runner.cleanup()
            print("✅ Dashboard stopped")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure dependencies are installed:")
        print("   pip install aiohttp aiohttp-cors")
        return 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    print("🔥 Real-Time Dashboard Test Suite")
    print("=" * 60)
    
    try:
        exit_code = asyncio.run(test_dashboard())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Test stopped by user")
        sys.exit(0)
