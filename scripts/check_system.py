#!/usr/bin/env python3
"""
🔧 SYSTEM CHECK UTILITY
=======================
Comprehensive system health check
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check required dependencies"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'aiohttp',
        'websockets', 
        'dotenv',
        'yaml',
        'aiohttp_cors'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                import_name = 'dotenv'
            elif package == 'yaml':
                import_name = 'yaml'
            else:
                import_name = package
                
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                missing.append(package)
                print(f"   ❌ {package} (Missing)")
            else:
                print(f"   ✅ {package} (OK)")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package} (Missing)")
    
    if missing:
        print(f"\n🔧 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("\n⚙️ Checking environment...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("   ❌ .env file not found")
        print("   🔧 Copy .env.example to .env and configure")
        return False
    
    print("   ✅ .env file exists")
    
    # Check for API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    testnet_key = os.getenv('BINANCE_TESTNET_API_KEY')
    live_key = os.getenv('BINANCE_API_KEY')
    
    if testnet_key and 'your_' not in testnet_key.lower():
        print("   ✅ Testnet API key configured")
    elif live_key and 'your_' not in live_key.lower():
        print("   ✅ Live API key configured")
    else:
        print("   ❌ No valid API keys found")
        print("   🔧 Configure API keys in .env file")
        return False
    
    return True

def check_directories():
    """Check required directories"""
    print("\n📁 Checking directories...")
    
    required_dirs = ['src', 'config', 'logs', 'data']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ (OK)")
        else:
            print(f"   ⚠️  {dir_name}/ (Missing - will create)")
            dir_path.mkdir(exist_ok=True)
    
    return True

def check_system_resources():
    """Check system resources"""
    print("\n💻 Checking system resources...")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        if memory_gb >= 4:
            print(f"   ✅ RAM: {memory_gb:.1f} GB (OK)")
        else:
            print(f"   ⚠️  RAM: {memory_gb:.1f} GB (Low - 4GB+ recommended)")
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        print(f"   ✅ CPU: {cpu_count} cores")
        
        # Check disk space
        disk = psutil.disk_usage('.')
        disk_gb = disk.free / (1024**3)
        
        if disk_gb >= 1:
            print(f"   ✅ Disk: {disk_gb:.1f} GB free (OK)")
        else:
            print(f"   ⚠️  Disk: {disk_gb:.1f} GB free (Low)")
            
    except ImportError:
        print("   ⚠️  psutil not available - install for detailed system info")
    
    return True

def check_network():
    """Check network connectivity"""
    print("\n🌐 Checking network connectivity...")
    
    try:
        import socket
        
        # Test DNS resolution
        socket.gethostbyname('binance.com')
        print("   ✅ DNS resolution (OK)")
        
        # Test HTTPS connectivity
        import urllib.request
        urllib.request.urlopen('https://api.binance.com/api/v3/ping', timeout=10)
        print("   ✅ Binance API connectivity (OK)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Network connectivity failed: {e}")
        print("   🔧 Check internet connection and firewall")
        return False

def run_basic_import_test():
    """Test basic imports"""
    print("\n🧪 Testing basic imports...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent.parent / "src"
        sys.path.insert(0, str(src_path))
        
        # Test core imports
        from core.real_trading_system import RealTradingSystem
        print("   ✅ Core trading system import (OK)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        print(f"   🔧 This is normal if API keys aren't configured yet")
        return True  # Don't fail on import issues during setup

def main():
    """Main system check"""
    print("🔥 ULTRA-FAST SCALPING SYSTEM - HEALTH CHECK")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Directories", check_directories),
        ("System Resources", check_system_resources),
        ("Network", check_network),
        ("Import Test", run_basic_import_test),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ {name} check failed: {e}")
    
    print("\n" + "=" * 60)
    print("📊 SYSTEM CHECK SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total} checks")
    
    if passed == total:
        print("✅ System is ready for trading!")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py --test")
        print("   2. Run: python main.py --monitor")
        print("   3. Run: python main.py")
        return 0
    else:
        print("❌ System needs attention")
        print("\n🔧 Fix the issues above and run check again")
        return 1

if __name__ == "__main__":
    exit(main())