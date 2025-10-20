#!/usr/bin/env python3
"""
🔥 REAL-TIME TRADING DASHBOARD
=============================
⚡ Integrated dashboard for the ImprovedTradingSystem
💰 Real-time monitoring of live trading
📊 WebSocket-based updates with zero latency
🎯 Professional-grade visualization
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Any, Optional
from aiohttp import web, WSMsgType
import aiohttp_cors
import weakref

class RealTimeTradingDashboard:
    """Real-time dashboard for the improved trading system"""
    
    def __init__(self, trading_system, port: int = 8080):
        self.trading_system = trading_system
        self.port = port
        self.app = web.Application()
        self.websocket_connections = set()
        
        # Performance tracking
        self.update_count = 0
        self.last_update_time = time.time()
        self.start_time = datetime.now()
        
        # Data history for charts
        self.price_history = deque(maxlen=100)
        self.pnl_history = deque(maxlen=100)
        self.signal_history = deque(maxlen=50)
        
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup HTTP routes"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Routes
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/api/status', self.status_api)
        self.app.router.add_post('/api/emergency-stop', self.emergency_stop_api)
        
        # Add CORS
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def dashboard_handler(self, request):
        """Serve the dashboard HTML"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Real-Time Trading Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-card: #21262d;
            --accent-green: #238636;
            --accent-blue: #1f6feb;
            --accent-red: #da3633;
            --accent-yellow: #d29922;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --border-color: #30363d;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: var(--accent-blue);
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px 20px;
            background: var(--bg-card);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-active { background: var(--accent-green); }
        .status-inactive { background: var(--accent-red); }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        .positive { color: var(--accent-green); }
        .negative { color: var(--accent-red); }
        .neutral { color: var(--text-primary); }
        
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        
        .chart-section {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }
        
        .side-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .panel-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }
        
        .panel-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--accent-blue);
        }
        
        .positions-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .positions-table th {
            background: var(--bg-secondary);
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        .positions-table td {
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .signal-item {
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid var(--accent-blue);
        }
        
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .signal-type {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .signal-buy { background: var(--accent-green); color: white; }
        .signal-sell { background: var(--accent-red); color: white; }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .btn-primary {
            background: var(--accent-blue);
            color: white;
        }
        
        .btn-danger {
            background: var(--accent-red);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            opacity: 0.9;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Real-Time Trading Dashboard</h1>
            <p>Ultra-Fast Scalping System - Live Monitoring</p>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="status-indicator status-active" id="connectionStatus"></span>
                <span id="connectionText">Connected</span>
            </div>
            <div class="status-item">
                <span>Environment: <strong id="environment">TESTNET</strong></span>
            </div>
            <div class="status-item">
                <span>Uptime: <strong id="uptime">00:00:00</strong></span>
            </div>
            <div class="status-item">
                <span>Last Update: <strong id="lastUpdate">--:--:--</strong></span>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value neutral" id="balance">$0.00</div>
                <div class="metric-label">💰 Account Balance</div>
            </div>
            <div class="metric-card">
                <div class="metric-value neutral" id="totalPnl">$0.00</div>
                <div class="metric-label">📈 Total P&L</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="activePositions">0</div>
                <div class="metric-label">📊 Active Positions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="signalsGenerated">0</div>
                <div class="metric-label">⚡ Signals Generated</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="totalTrades">0</div>
                <div class="metric-label">🎯 Total Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="winRate">0%</div>
                <div class="metric-label">🏆 Win Rate</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="chart-section">
                <h3>📈 Performance Chart</h3>
                <canvas id="performanceChart" width="400" height="200"></canvas>
            </div>
            
            <div class="side-panel">
                <div class="panel-card">
                    <div class="panel-title">📊 Active Positions</div>
                    <div style="max-height: 300px; overflow-y: auto;">
                        <table class="positions-table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Side</th>
                                    <th>P&L</th>
                                </tr>
                            </thead>
                            <tbody id="positionsTableBody">
                                <tr><td colspan="3" style="text-align: center; color: var(--text-secondary);">No active positions</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="panel-card">
                    <div class="panel-title">⚡ Recent Signals</div>
                    <div id="signalsContainer" style="max-height: 300px; overflow-y: auto;">
                        <div style="text-align: center; color: var(--text-secondary);">No signals yet</div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <div class="panel-title">🎮 Controls</div>
                    <div class="controls">
                        <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh</button>
                        <button class="btn btn-danger" onclick="emergencyStop()">🚨 Emergency Stop</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let chart = null;
        let startTime = Date.now();
        
        document.addEventListener('DOMContentLoaded', function() {
            initializeChart();
            connectWebSocket();
            setInterval(updateUptime, 1000);
        });
        
        function initializeChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'P&L ($)',
                        data: [],
                        borderColor: '#238636',
                        backgroundColor: 'rgba(35, 134, 54, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: { unit: 'minute' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { color: '#8b949e' }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { 
                                color: '#8b949e',
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                updateConnectionStatus(true);
            };
            
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                } catch (e) {
                    console.error('WebSocket message error:', e);
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                updateConnectionStatus(false);
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function updateConnectionStatus(connected) {
            const indicator = document.getElementById('connectionStatus');
            const text = document.getElementById('connectionText');
            
            if (connected) {
                indicator.className = 'status-indicator status-active';
                text.textContent = 'Connected';
            } else {
                indicator.className = 'status-indicator status-inactive';
                text.textContent = 'Disconnected';
            }
        }
        
        function updateDashboard(data) {
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
            // Update metrics
            updateMetric('balance', data.balance || 0, '$');
            updateMetric('totalPnl', data.total_pnl || 0, '$');
            updateMetric('activePositions', data.active_positions || 0);
            updateMetric('signalsGenerated', data.signals_generated || 0);
            updateMetric('totalTrades', data.total_trades || 0);
            updateMetric('winRate', ((data.win_rate || 0) * 100).toFixed(1), '%');
            
            // Update environment
            document.getElementById('environment').textContent = data.environment || 'UNKNOWN';
            
            // Update positions
            updatePositionsTable(data.positions || []);
            
            // Update signals
            updateSignalsPanel(data.recent_signals || []);
            
            // Update chart
            updateChart(data.total_pnl || 0);
        }
        
        function updateMetric(id, value, prefix = '') {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = prefix + (typeof value === 'number' ? value.toFixed(2) : value);
                
                if (id === 'totalPnl') {
                    element.className = 'metric-value ' + (value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral');
                }
            }
        }
        
        function updatePositionsTable(positions) {
            const tbody = document.getElementById('positionsTableBody');
            
            if (positions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-secondary);">No active positions</td></tr>';
                return;
            }
            
            tbody.innerHTML = positions.map(pos => {
                const pnlClass = pos.pnl >= 0 ? 'positive' : 'negative';
                return `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td>${pos.side}</td>
                        <td class="${pnlClass}">$${pos.pnl.toFixed(2)}</td>
                    </tr>
                `;
            }).join('');
        }
        
        function updateSignalsPanel(signals) {
            const container = document.getElementById('signalsContainer');
            
            if (signals.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary);">No signals yet</div>';
                return;
            }
            
            container.innerHTML = signals.slice(-10).reverse().map(signal => {
                const typeClass = signal.signal_type === 'BUY' ? 'signal-buy' : 'signal-sell';
                const time = new Date(signal.timestamp).toLocaleTimeString();
                
                return `
                    <div class="signal-item">
                        <div class="signal-header">
                            <span><strong>${signal.symbol}</strong></span>
                            <span class="signal-type ${typeClass}">${signal.signal_type}</span>
                        </div>
                        <div style="font-size: 0.9em; color: var(--text-secondary);">
                            ${time} | Strength: ${(signal.strength * 100).toFixed(1)}%
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function updateChart(pnl) {
            const now = new Date();
            
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(pnl);
            
            // Keep only last 50 points
            if (chart.data.labels.length > 50) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.update('none');
        }
        
        function updateUptime() {
            const uptimeMs = Date.now() - startTime;
            const hours = Math.floor(uptimeMs / 3600000);
            const minutes = Math.floor((uptimeMs % 3600000) / 60000);
            const seconds = Math.floor((uptimeMs % 60000) / 1000);
            
            document.getElementById('uptime').textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(console.error);
        }
        
        function emergencyStop() {
            if (confirm('⚠️ This will stop all trading and close positions. Continue?')) {
                fetch('/api/emergency-stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert('Emergency stop executed: ' + (data.message || 'System stopped'));
                        location.reload();
                    })
                    .catch(error => {
                        console.error('Emergency stop failed:', error);
                        alert('Emergency stop failed. Check console.');
                    });
            }
        }
    </script>
</body>
</html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        self.logger.info(f"Dashboard client connected. Total: {len(self.websocket_connections)}")
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.websocket_connections.discard(ws)
            self.logger.info(f"Client disconnected. Remaining: {len(self.websocket_connections)}")
        
        return ws
    
    async def status_api(self, request):
        """API endpoint for current status"""
        try:
            status = await self._get_system_status()
            return web.json_response(status, default=self._json_serializer)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def emergency_stop_api(self, request):
        """Emergency stop endpoint"""
        try:
            # Stop trading
            self.trading_system.is_trading = False
            
            # Close all positions
            closed_positions = 0
            for symbol in list(self.trading_system.positions.keys()):
                try:
                    await self.trading_system._close_position(symbol, "Emergency stop")
                    closed_positions += 1
                except Exception as e:
                    self.logger.error(f"Error closing position {symbol}: {e}")
            
            return web.json_response({
                'success': True,
                'message': f'Emergency stop executed. Closed {closed_positions} positions.',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            # Get basic system info
            positions = []
            total_pnl = 0.0
            
            for symbol, position in self.trading_system.positions.items():
                pnl = position.pnl
                total_pnl += pnl
                
                positions.append({
                    'symbol': symbol,
                    'side': position.side,
                    'entry_price': position.entry_price,
                    'current_price': position.current_price,
                    'pnl': pnl,
                    'quantity': position.quantity,
                    'entry_time': position.entry_time.isoformat()
                })
            
            # Get recent signals from history
            recent_signals = list(self.signal_history)
            
            # Calculate win rate
            win_rate = 0.0
            if self.trading_system.total_trades > 0:
                win_rate = self.trading_system.winning_trades / self.trading_system.total_trades
            
            # Get risk manager data
            risk_data = {}
            if self.trading_system.risk_manager:
                risk_data = {
                    'current_balance': self.trading_system.risk_manager.current_balance,
                    'daily_pnl': self.trading_system.risk_manager.daily_pnl,
                    'total_pnl': self.trading_system.risk_manager.total_pnl,
                }
            else:
                risk_data = {
                    'current_balance': 0,
                    'daily_pnl': 0,
                    'total_pnl': total_pnl,
                }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'environment': 'TESTNET' if self.trading_system.use_testnet else 'LIVE',
                'balance': risk_data['current_balance'],
                'total_pnl': risk_data['total_pnl'],
                'daily_pnl': risk_data['daily_pnl'],
                'active_positions': len(positions),
                'positions': positions,
                'signals_generated': self.trading_system.scalping_engine.signal_count if hasattr(self.trading_system.scalping_engine, 'signal_count') else 0,
                'total_trades': self.trading_system.total_trades,
                'winning_trades': self.trading_system.winning_trades,
                'win_rate': win_rate,
                'recent_signals': recent_signals,
                'is_trading': self.trading_system.is_trading,
                'uptime': str(datetime.now() - self.start_time),
                'update_count': self.update_count,
                'connected_clients': len(self.websocket_connections)
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}", exc_info=True)
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'balance': 0,
                'active_positions': 0,
                'positions': [],
                'total_pnl': 0,
                'signals_generated': 0,
                'total_trades': 0
            }
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        if not self.websocket_connections:
            return
        
        try:
            message = json.dumps(data, default=self._json_serializer)
            disconnected = set()
            
            for ws in list(self.websocket_connections):
                try:
                    if ws.closed:
                        disconnected.add(ws)
                        continue
                    await ws.send_str(message)
                except Exception:
                    disconnected.add(ws)
            
            # Remove disconnected clients
            self.websocket_connections -= disconnected
            self.update_count += 1
            
        except Exception as e:
            self.logger.error(f"Error broadcasting update: {e}")
    
    def _json_serializer(self, obj):
        """JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    async def start_server(self):
        """Start the dashboard server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        
        self.logger.info(f"🌐 Real-Time Dashboard started at http://localhost:{self.port}")
        return runner
    
    async def start_update_loop(self):
        """Start the update loop"""
        self.logger.info("📡 Dashboard update loop started")
        
        while True:
            try:
                # Always get status to update history
                status = await self._get_system_status()
                
                # Add to price and P&L history
                if status.get('total_pnl') is not None:
                    self.pnl_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'pnl': status['total_pnl']
                    })
                
                # Add signal history if there are signals
                if status.get('recent_signals'):
                    for signal in status.get('recent_signals', []):
                        if signal not in self.signal_history:
                            self.signal_history.append(signal)
                
                # Broadcast to connected clients
                if self.websocket_connections:
                    await self.broadcast_update(status)
                    self.logger.debug(f"📤 Broadcast to {len(self.websocket_connections)} clients")
                
                # Update every 1 second for real-time feel
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5.0)

# Integration function
async def start_dashboard(trading_system, port: int = 8080):
    """Start the dashboard for a trading system"""
    dashboard = RealTimeTradingDashboard(trading_system, port)
    
    # Link dashboard to trading system for notifications
    trading_system.dashboard = dashboard
    
    # Start server
    runner = await dashboard.start_server()
    
    # Start update loop
    update_task = asyncio.create_task(dashboard.start_update_loop())
    
    dashboard.logger.info(f"✅ Dashboard fully initialized and linked to trading system")
    
    return dashboard, runner, update_task