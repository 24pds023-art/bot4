"""
Ultra-Fast Scalping Trading System
==================================
High-performance cryptocurrency scalping system with institutional-grade optimizations.
"""

__version__ = "2.0.0"
__author__ = "Ultra-Fast Trading Systems"
__description__ = "Institutional-grade scalping system with nanosecond precision"

from .core.main_trading_system import UltimateTradingSystem
from .engines.ultra_scalping_engine import UltraScalpingEngine
from .optimizations.memory_pool_optimizer import AdvancedMemoryManager

__all__ = [
    'UltimateTradingSystem',
    'UltraScalpingEngine', 
    'AdvancedMemoryManager'
]