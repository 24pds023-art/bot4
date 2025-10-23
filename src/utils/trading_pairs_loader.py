"""
TRADING PAIRS LOADER
===================
Load and manage trading pairs from configuration
"""

import yaml
import os
from typing import List, Dict, Any


class TradingPairsLoader:
    """Load trading pairs from configuration file"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'trading_pairs.yaml')
        
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Loaded trading pairs configuration from {self.config_path}")
        except FileNotFoundError:
            print(f"⚠️ Configuration file not found: {self.config_path}")
            print("   Using default pairs")
            self.config = self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file not found"""
        return {
            'default_symbols': [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
                'ADAUSDT', 'AVAXUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT',
                'TRXUSDT', 'LINKUSDT', 'ATOMUSDT', 'UNIUSDT', 'LTCUSDT',
                'ARBUSDT', 'OPUSDT', 'APTUSDT', 'NEARUSDT', 'FILUSDT'
            ]
        }
    
    def get_default_symbols(self) -> List[str]:
        """Get default symbol list (recommended balanced approach)"""
        return self.config.get('default_symbols', [])
    
    def get_high_priority(self) -> List[str]:
        """Get high priority symbols (top market cap)"""
        return self.config.get('high_priority', [])
    
    def get_medium_priority(self) -> List[str]:
        """Get medium priority symbols"""
        return self.config.get('medium_priority', [])
    
    def get_low_priority(self) -> List[str]:
        """Get low priority symbols"""
        return self.config.get('low_priority', [])
    
    def get_category(self, category: str) -> List[str]:
        """Get symbols by category (defi_tokens, layer2_tokens, etc.)"""
        return self.config.get(category, [])
    
    def get_all_symbols(self) -> List[str]:
        """Get all available symbols from all categories"""
        all_symbols = set()
        
        # Add all categories
        for key, value in self.config.items():
            if isinstance(value, list):
                all_symbols.update(value)
        
        return sorted(list(all_symbols))
    
    def get_custom_selection(self, count: int = 30, prioritize_high: bool = True) -> List[str]:
        """
        Get custom symbol selection
        
        Args:
            count: Number of symbols to return
            prioritize_high: If True, prefer high priority symbols
        
        Returns:
            List of symbols
        """
        symbols = []
        
        if prioritize_high:
            # Start with high priority
            symbols.extend(self.get_high_priority())
            
            # Add medium priority if needed
            if len(symbols) < count:
                symbols.extend(self.get_medium_priority())
            
            # Add low priority if needed
            if len(symbols) < count:
                symbols.extend(self.get_low_priority())
            
            # Add DeFi tokens if needed
            if len(symbols) < count:
                symbols.extend(self.get_category('defi_tokens'))
            
            # Add other categories
            for category in ['layer2_tokens', 'ai_tokens', 'gaming_tokens']:
                if len(symbols) < count:
                    symbols.extend(self.get_category(category))
        else:
            # Just use all symbols
            symbols = self.get_all_symbols()
        
        # Remove duplicates and limit to count
        symbols = list(dict.fromkeys(symbols))  # Preserve order, remove dupes
        return symbols[:count]
    
    def get_summary(self) -> str:
        """Get configuration summary"""
        summary = "Trading Pairs Configuration Summary:\n"
        summary += "=" * 60 + "\n"
        
        default = self.get_default_symbols()
        summary += f"Default Symbols: {len(default)} pairs\n"
        
        high = self.get_high_priority()
        summary += f"High Priority: {len(high)} pairs\n"
        
        medium = self.get_medium_priority()
        summary += f"Medium Priority: {len(medium)} pairs\n"
        
        low = self.get_low_priority()
        summary += f"Low Priority: {len(low)} pairs\n"
        
        categories = ['defi_tokens', 'layer2_tokens', 'ai_tokens', 'gaming_tokens', 'meme_coins']
        for cat in categories:
            items = self.get_category(cat)
            if items:
                summary += f"{cat.replace('_', ' ').title()}: {len(items)} pairs\n"
        
        all_symbols = self.get_all_symbols()
        summary += f"\nTotal Available: {len(all_symbols)} pairs\n"
        
        return summary


# Global loader instance
_loader = None


def get_loader() -> TradingPairsLoader:
    """Get global trading pairs loader"""
    global _loader
    if _loader is None:
        _loader = TradingPairsLoader()
    return _loader


def get_default_symbols() -> List[str]:
    """Convenience function to get default symbols"""
    return get_loader().get_default_symbols()


def get_custom_symbols(count: int = 30) -> List[str]:
    """Convenience function to get custom symbol selection"""
    return get_loader().get_custom_selection(count)


if __name__ == "__main__":
    print("🔍 Trading Pairs Loader - Demo\n")
    
    loader = TradingPairsLoader()
    
    print(loader.get_summary())
    print("\n📊 Default Symbols (30):")
    for symbol in loader.get_default_symbols():
        print(f"  - {symbol}")
    
    print("\n🎯 Custom Selection (50 symbols):")
    custom = loader.get_custom_selection(50)
    print(f"  Total: {len(custom)} symbols")
    print(f"  Sample: {', '.join(custom[:10])}...")
