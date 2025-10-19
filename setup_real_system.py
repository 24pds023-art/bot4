#!/usr/bin/env python3
"""
REAL SYSTEM SETUP
================
Quick setup for the real trading system
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install minimal dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "aiohttp", "websockets", "python-dotenv", "pyyaml"
        ])
        print("✅ Dependencies installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_env_file():
    """Setup environment file"""
    print("⚙️ Setting up environment...")
    
    if Path('.env').exists():
        print("✅ .env file already exists")
        return True
    
    # Create .env from template
    env_content = """# REAL TRADING SYSTEM CONFIGURATION
# =================================

# TESTNET (RECOMMENDED FOR TESTING)
BINANCE_TESTNET_API_KEY=your_testnet_api_key_here
BINANCE_TESTNET_API_SECRET=your_testnet_api_secret_here

# LIVE PRODUCTION (⚠️ REAL MONEY)
BINANCE_API_KEY=your_live_api_key_here
BINANCE_API_SECRET=your_live_api_secret_here

# ENVIRONMENT
USE_TESTNET=true

# TRADING PARAMETERS
BASE_POSITION_USD=50
LEVERAGE=5
MAX_POSITIONS=3

# RISK MANAGEMENT
STOP_LOSS_PCT=0.002
TAKE_PROFIT_PCT=0.004
MAX_DAILY_LOSS=100
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("⚠️  Please edit .env file with your real API keys!")
    return True

def main():
    """Main setup"""
    print("🔥 REAL TRADING SYSTEM SETUP")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Setup environment
    if not setup_env_file():
        return 1
    
    print("\n✅ SETUP COMPLETE!")
    print("\n🎯 NEXT STEPS:")
    print("1. Edit .env file with your Binance API keys")
    print("2. Run: python run_real_system.py")
    print("3. Select option 3 to test connection first")
    print("4. Start with testnet trading")
    
    print("\n⚠️  IMPORTANT:")
    print("• Always test on testnet first")
    print("• Start with small position sizes")
    print("• Monitor the system closely")
    
    return 0

if __name__ == "__main__":
    exit(main())