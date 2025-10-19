"""
Core Trading System Components
==============================
Core components for the ultra-fast scalping trading system.
"""

# Only import what's actually needed and available
__all__ = [
    'RealTradingSystem',
]

def get_real_trading_system():
    """Get RealTradingSystem with lazy loading"""
    from .real_trading_system import RealTradingSystem
    return RealTradingSystem