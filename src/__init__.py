"""
Ultra-Fast Scalping Trading System
==================================
Professional-grade cryptocurrency scalping system with institutional optimizations.

This package provides:
- Real Binance API integration
- Ultra-low latency signal generation  
- Advanced risk management
- Professional-grade optimizations
- Complete real trading capabilities
"""

__version__ = "2.0.0"
__author__ = "Ultra-Fast Trading Systems"
__description__ = "Professional-grade scalping system with real Binance integration"

# Core imports - lazy loading to avoid dependency issues
def get_real_trading_system():
    """Get RealTradingSystem class with lazy loading"""
    from .core.real_trading_system import RealTradingSystem
    return RealTradingSystem

# Make key classes available at package level
__all__ = [
    'get_real_trading_system',
]

# Package metadata
PACKAGE_INFO = {
    'name': 'ultra-fast-scalping-system',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'features': [
        'Real Binance API integration',
        'Ultra-low latency execution',
        'Advanced risk management',
        'Professional optimizations',
        'Complete real trading'
    ],
    'requirements': [
        'Python 3.8+',
        'Binance API keys',
        'Stable internet connection'
    ]
}