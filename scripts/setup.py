#!/usr/bin/env python3
"""
System Setup Script
===================
Automated setup and configuration for the ultra-fast scalping system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Install basic requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Basic dependencies installed")
        
        # Check for GPU support
        try:
            import torch
            if torch.cuda.is_available():
                print("🚀 CUDA GPU detected - installing GPU acceleration...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", 
                    "--index-url", "https://download.pytorch.org/whl/cu118"
                ])
                print("✅ GPU acceleration installed")
            else:
                print("ℹ️  No CUDA GPU detected - using CPU only")
        except ImportError:
            print("ℹ️  PyTorch not available - skipping GPU setup")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "logs",
        "data",
        "data/test",
        "backups",
        "config/user"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Setup environment configuration"""
    print("\n⚙️  Setting up environment...")
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your API credentials")
        else:
            print("❌ .env.example not found")
            return False
    else:
        print("ℹ️  .env file already exists")
    
    return True

def check_system_requirements():
    """Check system requirements"""
    print("\n🖥️  Checking system requirements...")
    
    try:
        import psutil
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        print(f"✅ CPU cores: {cpu_count}")
        
        if cpu_count < 4:
            print("⚠️  Recommended: 4+ CPU cores for optimal performance")
        
        # Check memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"✅ RAM: {memory_gb:.1f} GB")
        
        if memory_gb < 8:
            print("⚠️  Recommended: 8+ GB RAM for optimal performance")
        
        # Check disk space
        disk = psutil.disk_usage('.')
        disk_gb = disk.free / (1024**3)
        print(f"✅ Free disk space: {disk_gb:.1f} GB")
        
        if disk_gb < 5:
            print("⚠️  Recommended: 5+ GB free disk space")
        
        return True
        
    except ImportError:
        print("❌ psutil not available - skipping system checks")
        return False

def setup_performance_optimizations():
    """Setup performance optimizations"""
    print("\n⚡ Setting up performance optimizations...")
    
    # Check for CPU affinity support
    try:
        import os
        if hasattr(os, 'sched_setaffinity'):
            print("✅ CPU affinity support available")
        else:
            print("ℹ️  CPU affinity not supported on this platform")
    except:
        pass
    
    # Check for memory optimization support
    try:
        import mmap
        print("✅ Memory mapping support available")
    except ImportError:
        print("❌ Memory mapping not available")
    
    # Check for high-resolution timers
    try:
        import time
        resolution = time.get_clock_info('perf_counter').resolution
        print(f"✅ Timer resolution: {resolution*1e9:.0f} nanoseconds")
    except:
        print("ℹ️  Timer resolution information not available")

def run_basic_tests():
    """Run basic system tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        print("   Testing core imports...")
        sys.path.append('src')
        
        from core.ultra_optimized_trading_system import UltraOptimizedTradingSystem
        print("   ✅ Core system import successful")
        
        from engines.ultra_scalping_engine import UltraScalpingEngine
        print("   ✅ Scalping engine import successful")
        
        from optimizations.memory_pool_optimizer import AdvancedMemoryManager
        print("   ✅ Memory optimizer import successful")
        
        # Test basic functionality
        print("   Testing basic functionality...")
        engine = UltraScalpingEngine(['BTCUSDT'])
        print("   ✅ Engine initialization successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Ultra-Fast Scalping System Setup")
    print("=" * 50)
    
    success = True
    
    # Run setup steps
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Directories", setup_directories),
        ("Environment", setup_environment),
        ("System Requirements", check_system_requirements),
        ("Performance Optimizations", setup_performance_optimizations),
        ("Basic Tests", run_basic_tests),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"❌ {step_name} setup failed")
            success = False
        else:
            print(f"✅ {step_name} setup completed")
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n🎯 Next steps:")
        print("   1. Edit .env file with your API credentials")
        print("   2. Run: python examples/basic_scalping.py")
        print("   3. Run: python tests/performance_benchmark.py")
        print("   4. Start trading: python -m src.core.main_trading_system")
        print("\n⚠️  Important:")
        print("   • Always test on testnet first")
        print("   • Start with small position sizes")
        print("   • Monitor performance closely")
    else:
        print("❌ Setup completed with errors")
        print("   Please resolve the issues above and run setup again")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())