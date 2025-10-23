"""
PRECISION HANDLER - FIX ALL COIN PRECISION ERRORS
=================================================
🎯 Automatic precision detection and handling for all trading pairs
✅ LOT_SIZE, PRICE_FILTER, MIN_NOTIONAL compliance
⚡ Cached precision data for ultra-fast lookups
🔧 Automatic rounding and validation
"""

from decimal import Decimal, getcontext, ROUND_DOWN
from typing import Dict, Any, Optional, Tuple
import math

# Set ultra-high precision for all financial calculations
getcontext().prec = 28


class PrecisionHandler:
    """Handles precision for all Binance trading pairs"""
    
    def __init__(self):
        self.symbol_info: Dict[str, Dict[str, Any]] = {}
        self.precision_cache: Dict[str, Dict[str, Any]] = {}
        
    def load_symbol_info(self, exchange_info: Dict[str, Any]):
        """Load symbol information from Binance exchange info"""
        if 'symbols' not in exchange_info:
            return
        
        for symbol_data in exchange_info['symbols']:
            symbol = symbol_data['symbol']
            
            # Extract precision and filters
            precision_info = {
                'symbol': symbol,
                'status': symbol_data.get('status', 'TRADING'),
                'baseAsset': symbol_data.get('baseAsset', ''),
                'quoteAsset': symbol_data.get('quoteAsset', ''),
                'pricePrecision': symbol_data.get('pricePrecision', 2),
                'quantityPrecision': symbol_data.get('quantityPrecision', 3),
                'baseAssetPrecision': symbol_data.get('baseAssetPrecision', 8),
                'quoteAssetPrecision': symbol_data.get('quoteAssetPrecision', 8),
            }
            
            # Extract filters
            filters = symbol_data.get('filters', [])
            for filter_data in filters:
                filter_type = filter_data.get('filterType', '')
                
                if filter_type == 'LOT_SIZE':
                    # Quantity constraints
                    precision_info['minQty'] = Decimal(str(filter_data.get('minQty', '0')))
                    precision_info['maxQty'] = Decimal(str(filter_data.get('maxQty', '1000000')))
                    precision_info['stepSize'] = Decimal(str(filter_data.get('stepSize', '0.001')))
                    precision_info['quantityPrecision'] = self._get_precision_from_step(
                        precision_info['stepSize']
                    )
                    
                elif filter_type == 'PRICE_FILTER':
                    # Price constraints
                    precision_info['minPrice'] = Decimal(str(filter_data.get('minPrice', '0')))
                    precision_info['maxPrice'] = Decimal(str(filter_data.get('maxPrice', '1000000')))
                    precision_info['tickSize'] = Decimal(str(filter_data.get('tickSize', '0.01')))
                    precision_info['pricePrecision'] = self._get_precision_from_step(
                        precision_info['tickSize']
                    )
                    
                elif filter_type == 'MIN_NOTIONAL':
                    # Minimum order value
                    precision_info['minNotional'] = Decimal(str(filter_data.get('minNotional', '10')))
                    
                elif filter_type == 'MARKET_LOT_SIZE':
                    # Market order constraints
                    precision_info['marketMinQty'] = Decimal(str(filter_data.get('minQty', '0')))
                    precision_info['marketMaxQty'] = Decimal(str(filter_data.get('maxQty', '1000000')))
                    precision_info['marketStepSize'] = Decimal(str(filter_data.get('stepSize', '0.001')))
            
            # Store symbol info
            self.symbol_info[symbol] = symbol_data
            self.precision_cache[symbol] = precision_info
            
        print(f"✅ Loaded precision data for {len(self.precision_cache)} symbols")
    
    def _get_precision_from_step(self, step_size: Decimal) -> int:
        """Calculate precision from step size"""
        if step_size == 0:
            return 0
        
        # Convert to string and count decimal places
        step_str = str(step_size)
        
        if '.' in step_str:
            # Count digits after decimal point
            decimal_part = step_str.split('.')[1]
            # Remove trailing zeros
            decimal_part = decimal_part.rstrip('0')
            return len(decimal_part)
        
        # Check for scientific notation
        if 'E' in step_str or 'e' in step_str:
            # Handle scientific notation like '1E-8'
            return abs(int(step_str.split('E')[-1].split('e')[-1]))
        
        return 0
    
    def round_quantity(self, symbol: str, quantity: float) -> Decimal:
        """Round quantity to comply with LOT_SIZE filter"""
        if symbol not in self.precision_cache:
            # Fallback: round to 3 decimal places
            return Decimal(str(quantity)).quantize(Decimal('0.001'), rounding=ROUND_DOWN)
        
        info = self.precision_cache[symbol]
        step_size = info.get('stepSize', Decimal('0.001'))
        min_qty = info.get('minQty', Decimal('0'))
        max_qty = info.get('maxQty', Decimal('1000000'))
        
        # Convert to Decimal for precise calculations
        qty_decimal = Decimal(str(quantity))
        
        # Round down to nearest step size
        if step_size > 0:
            qty_decimal = (qty_decimal / step_size).quantize(
                Decimal('1'), rounding=ROUND_DOWN
            ) * step_size
        
        # Ensure within bounds
        qty_decimal = max(min_qty, min(qty_decimal, max_qty))
        
        return qty_decimal
    
    def round_price(self, symbol: str, price: float) -> Decimal:
        """Round price to comply with PRICE_FILTER"""
        if symbol not in self.precision_cache:
            # Fallback: round to 2 decimal places
            return Decimal(str(price)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        info = self.precision_cache[symbol]
        tick_size = info.get('tickSize', Decimal('0.01'))
        min_price = info.get('minPrice', Decimal('0'))
        max_price = info.get('maxPrice', Decimal('1000000'))
        
        # Convert to Decimal for precise calculations
        price_decimal = Decimal(str(price))
        
        # Round down to nearest tick size
        if tick_size > 0:
            price_decimal = (price_decimal / tick_size).quantize(
                Decimal('1'), rounding=ROUND_DOWN
            ) * tick_size
        
        # Ensure within bounds
        price_decimal = max(min_price, min(price_decimal, max_price))
        
        return price_decimal
    
    def validate_order(self, symbol: str, quantity: float, price: float) -> Tuple[bool, str, Decimal, Decimal]:
        """
        Validate and fix order parameters
        
        Returns:
            (is_valid, error_message, fixed_quantity, fixed_price)
        """
        if symbol not in self.precision_cache:
            return False, f"Unknown symbol: {symbol}", Decimal('0'), Decimal('0')
        
        info = self.precision_cache[symbol]
        
        # Round to correct precision
        fixed_qty = self.round_quantity(symbol, quantity)
        fixed_price = self.round_price(symbol, price)
        
        # Check minimum quantity
        min_qty = info.get('minQty', Decimal('0'))
        if fixed_qty < min_qty:
            return False, f"Quantity {fixed_qty} below minimum {min_qty}", fixed_qty, fixed_price
        
        # Check maximum quantity
        max_qty = info.get('maxQty', Decimal('1000000'))
        if fixed_qty > max_qty:
            return False, f"Quantity {fixed_qty} above maximum {max_qty}", fixed_qty, fixed_price
        
        # Check minimum price
        min_price = info.get('minPrice', Decimal('0'))
        if fixed_price < min_price:
            return False, f"Price {fixed_price} below minimum {min_price}", fixed_qty, fixed_price
        
        # Check maximum price
        max_price = info.get('maxPrice', Decimal('1000000'))
        if fixed_price > max_price:
            return False, f"Price {fixed_price} above maximum {max_price}", fixed_qty, fixed_price
        
        # Check minimum notional (quantity * price)
        notional = fixed_qty * fixed_price
        min_notional = info.get('minNotional', Decimal('10'))
        if notional < min_notional:
            # Try to fix by adjusting quantity
            suggested_qty = (min_notional / fixed_price).quantize(
                Decimal('1') / (Decimal('10') ** info.get('quantityPrecision', 3)),
                rounding=ROUND_DOWN
            )
            suggested_qty = self.round_quantity(symbol, float(suggested_qty))
            
            return False, f"Notional {notional} below minimum {min_notional}. Try quantity: {suggested_qty}", fixed_qty, fixed_price
        
        # Check step size compliance
        step_size = info.get('stepSize', Decimal('0.001'))
        if step_size > 0:
            remainder = fixed_qty % step_size
            if remainder != 0:
                return False, f"Quantity {fixed_qty} not compliant with step size {step_size}", fixed_qty, fixed_price
        
        # Check tick size compliance
        tick_size = info.get('tickSize', Decimal('0.01'))
        if tick_size > 0:
            remainder = fixed_price % tick_size
            if remainder != 0:
                return False, f"Price {fixed_price} not compliant with tick size {tick_size}", fixed_qty, fixed_price
        
        return True, "Valid", fixed_qty, fixed_price
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        return self.precision_cache.get(symbol)
    
    def get_min_order_size(self, symbol: str, price: float) -> Decimal:
        """Get minimum order size that satisfies all constraints"""
        if symbol not in self.precision_cache:
            return Decimal('0.001')
        
        info = self.precision_cache[symbol]
        
        # Start with minimum quantity
        min_qty = info.get('minQty', Decimal('0.001'))
        
        # Ensure notional is met
        min_notional = info.get('minNotional', Decimal('10'))
        price_decimal = Decimal(str(price))
        
        if price_decimal > 0:
            notional_qty = min_notional / price_decimal
            min_qty = max(min_qty, notional_qty)
        
        # Round to step size
        return self.round_quantity(symbol, float(min_qty))
    
    def format_quantity(self, symbol: str, quantity: Decimal) -> str:
        """Format quantity for API submission"""
        if symbol not in self.precision_cache:
            return f"{float(quantity):.8f}".rstrip('0').rstrip('.')
        
        info = self.precision_cache[symbol]
        precision = info.get('quantityPrecision', 3)
        
        # Format with correct precision
        format_str = f"{{:.{precision}f}}"
        formatted = format_str.format(float(quantity))
        
        # Remove trailing zeros but keep at least one decimal if precision > 0
        if precision > 0:
            formatted = formatted.rstrip('0').rstrip('.')
            if '.' not in formatted and precision > 0:
                formatted += '.0'
        
        return formatted
    
    def format_price(self, symbol: str, price: Decimal) -> str:
        """Format price for API submission"""
        if symbol not in self.precision_cache:
            return f"{float(price):.8f}".rstrip('0').rstrip('.')
        
        info = self.precision_cache[symbol]
        precision = info.get('pricePrecision', 2)
        
        # Format with correct precision
        format_str = f"{{:.{precision}f}}"
        formatted = format_str.format(float(price))
        
        # Remove trailing zeros
        formatted = formatted.rstrip('0').rstrip('.')
        
        return formatted
    
    def get_all_trading_symbols(self, quote_asset: str = 'USDT') -> list:
        """Get all trading symbols for a quote asset"""
        symbols = []
        for symbol, info in self.precision_cache.items():
            if info.get('status') == 'TRADING' and info.get('quoteAsset') == quote_asset:
                symbols.append(symbol)
        return sorted(symbols)
    
    def get_precision_summary(self, symbol: str) -> str:
        """Get human-readable precision summary"""
        if symbol not in self.precision_cache:
            return f"No precision data for {symbol}"
        
        info = self.precision_cache[symbol]
        
        summary = f"""
Symbol: {symbol}
Status: {info.get('status', 'UNKNOWN')}
Base Asset: {info.get('baseAsset', 'N/A')}
Quote Asset: {info.get('quoteAsset', 'N/A')}

Quantity Constraints:
  - Precision: {info.get('quantityPrecision', 'N/A')} decimal places
  - Step Size: {info.get('stepSize', 'N/A')}
  - Min Quantity: {info.get('minQty', 'N/A')}
  - Max Quantity: {info.get('maxQty', 'N/A')}

Price Constraints:
  - Precision: {info.get('pricePrecision', 'N/A')} decimal places
  - Tick Size: {info.get('tickSize', 'N/A')}
  - Min Price: {info.get('minPrice', 'N/A')}
  - Max Price: {info.get('maxPrice', 'N/A')}

Order Constraints:
  - Min Notional: {info.get('minNotional', 'N/A')} {info.get('quoteAsset', 'USDT')}
"""
        return summary.strip()


# Global precision handler instance
_precision_handler = None


def get_precision_handler() -> PrecisionHandler:
    """Get global precision handler instance"""
    global _precision_handler
    if _precision_handler is None:
        _precision_handler = PrecisionHandler()
    return _precision_handler


# Convenience functions
def round_quantity(symbol: str, quantity: float) -> Decimal:
    """Round quantity to correct precision"""
    return get_precision_handler().round_quantity(symbol, quantity)


def round_price(symbol: str, price: float) -> Decimal:
    """Round price to correct precision"""
    return get_precision_handler().round_price(symbol, price)


def validate_order(symbol: str, quantity: float, price: float) -> Tuple[bool, str, Decimal, Decimal]:
    """Validate order parameters"""
    return get_precision_handler().validate_order(symbol, quantity, price)


def get_min_order_size(symbol: str, price: float) -> Decimal:
    """Get minimum order size"""
    return get_precision_handler().get_min_order_size(symbol, price)


# Test/Demo
if __name__ == "__main__":
    print("🎯 Precision Handler - Demo")
    print("=" * 60)
    
    # Create handler
    handler = PrecisionHandler()
    
    # Simulate exchange info
    test_exchange_info = {
        'symbols': [
            {
                'symbol': 'BTCUSDT',
                'status': 'TRADING',
                'baseAsset': 'BTC',
                'quoteAsset': 'USDT',
                'pricePrecision': 2,
                'quantityPrecision': 3,
                'filters': [
                    {
                        'filterType': 'LOT_SIZE',
                        'minQty': '0.001',
                        'maxQty': '1000',
                        'stepSize': '0.001'
                    },
                    {
                        'filterType': 'PRICE_FILTER',
                        'minPrice': '0.01',
                        'maxPrice': '1000000',
                        'tickSize': '0.01'
                    },
                    {
                        'filterType': 'MIN_NOTIONAL',
                        'minNotional': '10'
                    }
                ]
            }
        ]
    }
    
    handler.load_symbol_info(test_exchange_info)
    
    # Test rounding
    print("\n📊 Testing Precision Rounding:")
    print(f"BTC quantity 0.123456 → {handler.round_quantity('BTCUSDT', 0.123456)}")
    print(f"BTC price 45123.456 → {handler.round_price('BTCUSDT', 45123.456)}")
    
    # Test validation
    print("\n✅ Testing Order Validation:")
    valid, msg, qty, price = handler.validate_order('BTCUSDT', 0.001, 45000)
    print(f"Order: {qty} BTC @ ${price}")
    print(f"Valid: {valid} - {msg}")
    
    print("\n🎉 Precision Handler Ready!")
