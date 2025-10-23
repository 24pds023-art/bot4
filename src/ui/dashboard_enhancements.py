"""
DASHBOARD ENHANCEMENTS v3.0
===========================
📊 Per-symbol profit tracking
✅ Precision validation display
💰 Enhanced metrics
📈 Better visualizations
"""

from typing import Dict, List, Any
from collections import defaultdict, deque
from decimal import Decimal
import time


class DashboardEnhancements:
    """Enhanced dashboard features for v3.0"""
    
    def __init__(self):
        # Per-symbol tracking
        self.symbol_profits = defaultdict(lambda: {
            'realized_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'avg_loss': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'last_trade_time': None
        })
        
        # Precision validation tracking
        self.precision_stats = {
            'total_orders': 0,
            'valid_orders': 0,
            'fixed_orders': 0,
            'failed_orders': 0,
            'precision_errors_prevented': 0
        }
        
        # Enhanced metrics
        self.performance_history = deque(maxlen=1000)
        self.symbol_performance = defaultdict(lambda: deque(maxlen=100))
        
        # Real-time stats
        self.current_stats = {
            'total_symbols': 0,
            'active_symbols': 0,
            'top_performer': None,
            'worst_performer': None,
            'total_volume': 0.0,
            'avg_precision_compliance': 100.0
        }
    
    def record_trade(self, symbol: str, pnl: float, is_win: bool):
        """Record a completed trade"""
        stats = self.symbol_profits[symbol]
        
        stats['realized_pnl'] += pnl
        stats['total_trades'] += 1
        
        if is_win:
            stats['winning_trades'] += 1
            if pnl > stats.get('best_trade', 0):
                stats['best_trade'] = pnl
        else:
            stats['losing_trades'] += 1
            if pnl < stats.get('worst_trade', 0):
                stats['worst_trade'] = pnl
        
        # Update win rate
        if stats['total_trades'] > 0:
            stats['win_rate'] = stats['winning_trades'] / stats['total_trades']
        
        # Update averages
        if stats['winning_trades'] > 0:
            winning_trades_pnl = [t for t in self.symbol_performance[symbol] if t > 0]
            if winning_trades_pnl:
                stats['avg_profit'] = sum(winning_trades_pnl) / len(winning_trades_pnl)
        
        if stats['losing_trades'] > 0:
            losing_trades_pnl = [t for t in self.symbol_performance[symbol] if t < 0]
            if losing_trades_pnl:
                stats['avg_loss'] = sum(losing_trades_pnl) / len(losing_trades_pnl)
        
        stats['last_trade_time'] = time.time()
        
        # Store in history
        self.symbol_performance[symbol].append(pnl)
        self.performance_history.append({
            'symbol': symbol,
            'pnl': pnl,
            'time': time.time(),
            'is_win': is_win
        })
    
    def update_unrealized_pnl(self, symbol: str, unrealized_pnl: float):
        """Update unrealized P&L for a symbol"""
        self.symbol_profits[symbol]['unrealized_pnl'] = unrealized_pnl
    
    def record_precision_validation(self, success: bool, was_fixed: bool = False):
        """Record precision validation event"""
        self.precision_stats['total_orders'] += 1
        
        if success:
            self.precision_stats['valid_orders'] += 1
            if was_fixed:
                self.precision_stats['fixed_orders'] += 1
                self.precision_stats['precision_errors_prevented'] += 1
        else:
            self.precision_stats['failed_orders'] += 1
        
        # Update compliance rate
        if self.precision_stats['total_orders'] > 0:
            compliance = (self.precision_stats['valid_orders'] / 
                         self.precision_stats['total_orders']) * 100
            self.current_stats['avg_precision_compliance'] = compliance
    
    def get_symbol_stats(self, symbol: str) -> Dict[str, Any]:
        """Get statistics for a specific symbol"""
        stats = self.symbol_profits[symbol]
        
        return {
            'symbol': symbol,
            'realized_pnl': round(stats['realized_pnl'], 2),
            'unrealized_pnl': round(stats['unrealized_pnl'], 2),
            'total_pnl': round(stats['realized_pnl'] + stats['unrealized_pnl'], 2),
            'total_trades': stats['total_trades'],
            'winning_trades': stats['winning_trades'],
            'losing_trades': stats['losing_trades'],
            'win_rate': round(stats['win_rate'] * 100, 1),
            'avg_profit': round(stats['avg_profit'], 2),
            'avg_loss': round(stats['avg_loss'], 2),
            'best_trade': round(stats['best_trade'], 2),
            'worst_trade': round(stats['worst_trade'], 2),
            'profit_factor': self._calculate_profit_factor(stats),
            'last_trade_time': stats['last_trade_time']
        }
    
    def _calculate_profit_factor(self, stats: Dict) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if stats['losing_trades'] == 0 or stats['avg_loss'] == 0:
            return float('inf') if stats['winning_trades'] > 0 else 0.0
        
        gross_profit = stats['winning_trades'] * stats['avg_profit']
        gross_loss = abs(stats['losing_trades'] * stats['avg_loss'])
        
        if gross_loss == 0:
            return float('inf')
        
        return round(gross_profit / gross_loss, 2)
    
    def get_top_performers(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get top performing symbols"""
        symbols_stats = []
        
        for symbol in self.symbol_profits.keys():
            stats = self.get_symbol_stats(symbol)
            if stats['total_trades'] > 0:
                symbols_stats.append(stats)
        
        # Sort by total P&L
        symbols_stats.sort(key=lambda x: x['total_pnl'], reverse=True)
        
        return symbols_stats[:count]
    
    def get_worst_performers(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get worst performing symbols"""
        symbols_stats = []
        
        for symbol in self.symbol_profits.keys():
            stats = self.get_symbol_stats(symbol)
            if stats['total_trades'] > 0:
                symbols_stats.append(stats)
        
        # Sort by total P&L (ascending)
        symbols_stats.sort(key=lambda x: x['total_pnl'])
        
        return symbols_stats[:count]
    
    def get_all_symbols_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all symbols"""
        all_stats = []
        
        for symbol in self.symbol_profits.keys():
            stats = self.get_symbol_stats(symbol)
            all_stats.append(stats)
        
        # Sort by total P&L
        all_stats.sort(key=lambda x: x['total_pnl'], reverse=True)
        
        return all_stats
    
    def get_precision_stats(self) -> Dict[str, Any]:
        """Get precision validation statistics"""
        return {
            'total_orders': self.precision_stats['total_orders'],
            'valid_orders': self.precision_stats['valid_orders'],
            'fixed_orders': self.precision_stats['fixed_orders'],
            'failed_orders': self.precision_stats['failed_orders'],
            'errors_prevented': self.precision_stats['precision_errors_prevented'],
            'compliance_rate': round(self.current_stats['avg_precision_compliance'], 1),
            'fix_rate': round(
                (self.precision_stats['fixed_orders'] / 
                 max(1, self.precision_stats['total_orders'])) * 100, 1
            )
        }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get complete dashboard summary"""
        all_stats = self.get_all_symbols_stats()
        
        # Calculate totals
        total_realized = sum(s['realized_pnl'] for s in all_stats)
        total_unrealized = sum(s['unrealized_pnl'] for s in all_stats)
        total_trades = sum(s['total_trades'] for s in all_stats)
        total_wins = sum(s['winning_trades'] for s in all_stats)
        total_losses = sum(s['losing_trades'] for s in all_stats)
        
        # Find top and worst
        top_performer = all_stats[0] if all_stats else None
        worst_performer = all_stats[-1] if all_stats else None
        
        return {
            'totals': {
                'realized_pnl': round(total_realized, 2),
                'unrealized_pnl': round(total_unrealized, 2),
                'total_pnl': round(total_realized + total_unrealized, 2),
                'total_trades': total_trades,
                'winning_trades': total_wins,
                'losing_trades': total_losses,
                'overall_win_rate': round(
                    (total_wins / max(1, total_trades)) * 100, 1
                )
            },
            'symbols': {
                'total_symbols': len(all_stats),
                'active_symbols': sum(1 for s in all_stats if s['total_trades'] > 0),
                'top_performer': top_performer,
                'worst_performer': worst_performer
            },
            'precision': self.get_precision_stats(),
            'top_5': self.get_top_performers(5),
            'worst_5': self.get_worst_performers(5),
            'all_symbols': all_stats
        }
    
    def get_enhanced_html_section(self) -> str:
        """Get HTML section for enhanced dashboard features"""
        return """
        <!-- Per-Symbol Performance Section -->
        <div class="dashboard-section">
            <h2>📊 Per-Symbol Performance</h2>
            <div class="symbol-grid" id="symbolGrid">
                <!-- Populated by JavaScript -->
            </div>
        </div>
        
        <!-- Precision Validation Section -->
        <div class="dashboard-section">
            <h2>✅ Precision Validation Status</h2>
            <div class="precision-stats">
                <div class="stat-card">
                    <div class="stat-label">Compliance Rate</div>
                    <div class="stat-value" id="complianceRate">100%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Orders Validated</div>
                    <div class="stat-value" id="ordersValidated">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Auto-Fixed</div>
                    <div class="stat-value" id="ordersFixed">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Errors Prevented</div>
                    <div class="stat-value green" id="errorsPrevented">0</div>
                </div>
            </div>
        </div>
        
        <!-- Top/Worst Performers -->
        <div class="dashboard-section">
            <div class="performers-container">
                <div class="top-performers">
                    <h3>🏆 Top 5 Performers</h3>
                    <div id="topPerformers"></div>
                </div>
                <div class="worst-performers">
                    <h3>📉 Bottom 5 Performers</h3>
                    <div id="worstPerformers"></div>
                </div>
            </div>
        </div>
        """
    
    def get_enhanced_js_section(self) -> str:
        """Get JavaScript section for enhanced dashboard features"""
        return """
        function updateEnhancedDashboard(data) {
            // Update precision stats
            if (data.precision) {
                document.getElementById('complianceRate').textContent = 
                    data.precision.compliance_rate + '%';
                document.getElementById('ordersValidated').textContent = 
                    data.precision.total_orders;
                document.getElementById('ordersFixed').textContent = 
                    data.precision.fixed_orders;
                document.getElementById('errorsPrevented').textContent = 
                    data.precision.errors_prevented;
            }
            
            // Update symbol grid
            if (data.all_symbols) {
                updateSymbolGrid(data.all_symbols);
            }
            
            // Update top/worst performers
            if (data.top_5) {
                updatePerformers('topPerformers', data.top_5, true);
            }
            if (data.worst_5) {
                updatePerformers('worstPerformers', data.worst_5, false);
            }
        }
        
        function updateSymbolGrid(symbols) {
            const grid = document.getElementById('symbolGrid');
            grid.innerHTML = '';
            
            symbols.slice(0, 12).forEach(symbol => {
                const card = document.createElement('div');
                card.className = 'symbol-card';
                card.innerHTML = `
                    <div class="symbol-name">${symbol.symbol}</div>
                    <div class="symbol-pnl ${symbol.total_pnl >= 0 ? 'positive' : 'negative'}">
                        $${symbol.total_pnl.toFixed(2)}
                    </div>
                    <div class="symbol-stats">
                        <span>Win Rate: ${symbol.win_rate}%</span>
                        <span>Trades: ${symbol.total_trades}</span>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
        
        function updatePerformers(elementId, performers, isTop) {
            const container = document.getElementById(elementId);
            container.innerHTML = '';
            
            performers.forEach((perf, index) => {
                const item = document.createElement('div');
                item.className = 'performer-item';
                item.innerHTML = `
                    <span class="rank">${index + 1}</span>
                    <span class="symbol">${perf.symbol}</span>
                    <span class="pnl ${perf.total_pnl >= 0 ? 'positive' : 'negative'}">
                        $${perf.total_pnl.toFixed(2)}
                    </span>
                    <span class="win-rate">${perf.win_rate}%</span>
                `;
                container.appendChild(item);
            });
        }
        """
    
    def get_enhanced_css_section(self) -> str:
        """Get CSS section for enhanced dashboard features"""
        return """
        .symbol-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .symbol-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            transition: transform 0.2s;
        }
        
        .symbol-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }
        
        .symbol-name {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        
        .symbol-pnl {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .symbol-pnl.positive { color: var(--accent-green); }
        .symbol-pnl.negative { color: var(--accent-red); }
        
        .symbol-stats {
            font-size: 12px;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
        }
        
        .precision-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .performers-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }
        
        .performer-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: var(--bg-card);
            border-radius: 6px;
            margin-bottom: 8px;
        }
        
        .performer-item .rank {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: var(--accent-blue);
            color: var(--text-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
        }
        
        .performer-item .symbol {
            flex: 1;
            font-weight: 600;
        }
        
        .performer-item .pnl {
            font-weight: 700;
            margin-right: 10px;
        }
        
        .performer-item .win-rate {
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .symbol-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }
            
            .performers-container {
                grid-template-columns: 1fr;
            }
        }
        """


# Export for easy import
__all__ = ['DashboardEnhancements']
