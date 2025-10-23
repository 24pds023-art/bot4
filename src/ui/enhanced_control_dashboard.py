#!/usr/bin/env python3
"""
🎮 ENHANCED CONTROL DASHBOARD
============================
⚡ Full remote control capabilities
🎯 Dynamic symbol management
💰 Risk management controls
🔄 Bot lifecycle management
🌐 Network accessible
"""

import asyncio
import json
import time
import logging
import yaml
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Any, Optional
from aiohttp import web, WSMsgType
import aiohttp_cors
from pathlib import Path

class EnhancedControlDashboard:
    """Enhanced trading dashboard with full control capabilities"""
    
    def __init__(self, trading_system, ai_engine=None, port: int = 8080, host: str = "0.0.0.0"):
        self.trading_system = trading_system
        self.ai_engine = ai_engine
        self.port = port
        self.host = host  # 0.0.0.0 for network access
        self.app = web.Application()
        self.websocket_connections = set()
        
        # Control state
        self.bot_state = "running"  # running, paused, stopped
        self.settings = self._load_settings()
        
        # Data tracking
        self.ai_predictions = deque(maxlen=100)
        self.performance_history = deque(maxlen=100)
        
        self.logger = logging.getLogger(__name__)
        self.setup_routes()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load or create default settings"""
        settings_file = Path("config/dashboard_settings.yaml")
        
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        # Default settings
        return {
            'take_profit': 1.5,  # %
            'stop_loss': 0.8,    # %
            'max_concurrent': 5,
            'leverage': 1,
            'position_size': 100,  # USDT
            'symbols': list(self.trading_system.symbols) if self.trading_system else []
        }
    
    def _save_settings(self):
        """Save settings to file"""
        settings_file = Path("config/dashboard_settings.yaml")
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(settings_file, 'w') as f:
            yaml.dump(self.settings, f, default_flow_style=False)
    
    def setup_routes(self):
        """Setup HTTP routes with CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Page routes
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # API routes - Status
        self.app.router.add_get('/api/status', self.status_api)
        self.app.router.add_get('/api/settings', self.get_settings_api)
        
        # API routes - Controls
        self.app.router.add_post('/api/bot/start', self.bot_start_api)
        self.app.router.add_post('/api/bot/pause', self.bot_pause_api)
        self.app.router.add_post('/api/bot/restart', self.bot_restart_api)
        self.app.router.add_post('/api/bot/stop', self.bot_stop_api)
        
        # API routes - Settings
        self.app.router.add_post('/api/settings/symbols', self.update_symbols_api)
        self.app.router.add_post('/api/settings/take-profit', self.update_take_profit_api)
        self.app.router.add_post('/api/settings/stop-loss', self.update_stop_loss_api)
        self.app.router.add_post('/api/settings/max-concurrent', self.update_max_concurrent_api)
        self.app.router.add_post('/api/settings/leverage', self.update_leverage_api)
        self.app.router.add_post('/api/settings/position-size', self.update_position_size_api)
        self.app.router.add_post('/api/settings/update-all', self.update_all_settings_api)
        
        # API routes - Symbols
        self.app.router.add_post('/api/symbols/add', self.add_symbol_api)
        self.app.router.add_post('/api/symbols/remove', self.remove_symbol_api)
        self.app.router.add_post('/api/symbols/update', self.update_symbols_api)
        self.app.router.add_get('/api/symbols/available', self.get_available_symbols_api)
        
        # API routes - Positions
        self.app.router.add_post('/api/positions/close', self.close_position_api)
        self.app.router.add_post('/api/positions/close-all', self.close_all_positions_api)
        
        # Add CORS
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def dashboard_handler(self, request):
        """Serve the enhanced dashboard HTML"""
        html_content = self._get_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML with control panel"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Enhanced Trading Control Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #1a1f3a;
            --bg-card: #252b48;
            --accent-green: #00ff88;
            --accent-blue: #00d4ff;
            --accent-red: #ff4757;
            --accent-yellow: #ffa502;
            --accent-purple: #9c88ff;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --border-color: #3a4160;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1920px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
            border-radius: 16px;
            border: 2px solid var(--border-color);
        }
        
        .header h1 {
            font-size: 2.8em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Status Bar */
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .status-item {
            background: var(--bg-card);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-active { background: var(--accent-green); }
        .status-paused { background: var(--accent-yellow); }
        .status-stopped { background: var(--accent-red); }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Control Panel */
        .control-panel {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            border: 2px solid var(--accent-blue);
        }
        
        .control-panel h2 {
            margin-bottom: 20px;
            color: var(--accent-blue);
            font-size: 1.5em;
        }
        
        .control-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }
        
        .control-section {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .control-section h3 {
            margin-bottom: 15px;
            font-size: 1.1em;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-group {
            margin-bottom: 15px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        input[type="number"], input[type="text"], select {
            width: 100%;
            padding: 10px;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 1em;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent-blue);
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95em;
            transition: all 0.2s ease;
            width: 100%;
            margin-top: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white;
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #00cc6a);
            color: #0a0e27;
        }
        
        .btn-warning {
            background: linear-gradient(135deg, var(--accent-yellow), #ff8c00);
            color: #0a0e27;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, var(--accent-red), #e74c3c);
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            opacity: 0.9;
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        /* Symbol Manager */
        .symbol-list {
            max-height: 200px;
            overflow-y: auto;
            background: var(--bg-primary);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .symbol-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin-bottom: 5px;
            background: var(--bg-secondary);
            border-radius: 6px;
        }
        
        .symbol-remove {
            background: var(--accent-red);
            border: none;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
            text-align: center;
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
        
        /* Main Content */
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        
        .chart-container {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }
        
        .chart-container h3 {
            margin-bottom: 15px;
            color: var(--accent-blue);
        }
        
        .positions-panel {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }
        
        .position-list {
            max-height: 500px;
            overflow-y: auto;
        }
        
        .position-item {
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .position-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .position-symbol {
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .position-side-buy {
            background: var(--accent-green);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            color: #0a0e27;
            font-weight: bold;
        }
        
        .position-side-sell {
            background: var(--accent-red);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            color: white;
            font-weight: bold;
        }
        
        .position-details {
            font-size: 0.9em;
            color: var(--text-secondary);
        }
        
        .position-close {
            background: var(--accent-red);
            border: none;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 10px;
            width: 100%;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-blue);
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .control-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        .input-group input {
            flex: 1;
        }
        
        .input-group button {
            flex: 0 0 80px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🎮 Enhanced Trading Control Dashboard</h1>
            <p>Full Remote Control • Dynamic Management • Real-time Monitoring</p>
        </div>
        
        <!-- Status Bar -->
        <div class="status-bar">
            <div class="status-item">
                <span class="status-indicator status-active" id="botStatusIndicator"></span>
                <span>Bot: <strong id="botStatus">Running</strong></span>
            </div>
            <div class="status-item">
                <span class="status-indicator status-active" id="connectionIndicator"></span>
                <span id="connectionText">Connected</span>
            </div>
            <div class="status-item">
                <span>Environment: <strong id="environment">TESTNET</strong></span>
            </div>
            <div class="status-item">
                <span>Symbols: <strong id="symbolCount">0</strong></span>
            </div>
            <div class="status-item">
                <span>Active Positions: <strong id="activePositions">0</strong></span>
            </div>
            <div class="status-item">
                <span>Last Update: <strong id="lastUpdate">--:--:--</strong></span>
            </div>
        </div>
        
        <!-- Control Panel -->
        <div class="control-panel">
            <h2>🎮 Control Panel</h2>
            
            <div class="control-grid">
                <!-- Bot Controls -->
                <div class="control-section">
                    <h3>🤖 Bot Controls</h3>
                    <div class="btn-grid">
                        <button class="btn btn-success" onclick="botControl('start')">▶ Start</button>
                        <button class="btn btn-warning" onclick="botControl('pause')">⏸ Pause</button>
                        <button class="btn btn-primary" onclick="botControl('restart')">🔄 Restart</button>
                        <button class="btn btn-danger" onclick="botControl('stop')">⏹ Stop</button>
                    </div>
                </div>
                
                <!-- Risk Settings -->
                <div class="control-section">
                    <h3>⚡ Risk Management</h3>
                    <div class="control-group">
                        <label>Take Profit (%)</label>
                        <input type="number" id="takeProfit" step="0.1" value="1.5" onchange="updateSetting('take-profit', this.value)">
                    </div>
                    <div class="control-group">
                        <label>Stop Loss (%)</label>
                        <input type="number" id="stopLoss" step="0.1" value="0.8" onchange="updateSetting('stop-loss', this.value)">
                    </div>
                </div>
                
                <!-- Position Settings -->
                <div class="control-section">
                    <h3>💰 Position Settings</h3>
                    <div class="control-group">
                        <label>Max Concurrent Trades</label>
                        <input type="number" id="maxConcurrent" min="1" max="20" value="5" onchange="updateSetting('max-concurrent', this.value)">
                    </div>
                    <div class="control-group">
                        <label>Position Size (USDT)</label>
                        <input type="number" id="positionSize" min="10" step="10" value="100" onchange="updateSetting('position-size', this.value)">
                    </div>
                    <div class="control-group">
                        <label>Leverage</label>
                        <input type="number" id="leverage" min="1" max="10" value="1" onchange="updateSetting('leverage', this.value)">
                    </div>
                </div>
                
                <!-- Symbol Manager -->
                <div class="control-section">
                    <h3>📊 Symbol Manager</h3>
                    <div class="control-group">
                        <label>Active Symbols (<span id="activeSymbolCount">0</span>)</label>
                        <div class="symbol-list" id="symbolList">
                            <div style="text-align: center; color: var(--text-secondary);">Loading...</div>
                        </div>
                    </div>
                    <div class="input-group">
                        <input type="text" id="newSymbol" placeholder="e.g., BTCUSDT">
                        <button class="btn btn-success" onclick="addSymbol()">Add</button>
                    </div>
                </div>
            </div>
            
            <button class="btn btn-primary" onclick="applyAllSettings()" style="margin-top: 20px;">💾 Save All Settings</button>
        </div>
        
        <!-- Metrics Grid -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value neutral" id="balance">$0.00</div>
                <div class="metric-label">💰 Balance</div>
            </div>
            <div class="metric-card">
                <div class="metric-value neutral" id="totalPnl">$0.00</div>
                <div class="metric-label">📈 Total P&L</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="totalTrades">0</div>
                <div class="metric-label">🎯 Total Trades</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="winRate">0%</div>
                <div class="metric-label">🏆 Win Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="activeTrades">0</div>
                <div class="metric-label">🔄 Active Trades</div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="chart-container">
                <h3>📈 Performance Chart</h3>
                <canvas id="performanceChart" width="400" height="200"></canvas>
            </div>
            
            <div class="positions-panel">
                <h3>📊 Active Positions</h3>
                <button class="btn btn-danger" onclick="closeAllPositions()" style="margin-bottom: 15px;">Close All Positions</button>
                <div class="position-list" id="positionList">
                    <div style="text-align: center; color: var(--text-secondary);">No active positions</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let performanceChart = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initializeChart();
            connectWebSocket();
            loadSettings();
        });
        
        function initializeChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'P&L ($)',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
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
                            ticks: { color: '#b0b0b0' }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { 
                                color: '#b0b0b0',
                                callback: value => '$' + value.toFixed(2)
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
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                updateConnectionStatus(true);
            };
            
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                } catch (e) {
                    console.error('WebSocket error:', e);
                }
            };
            
            ws.onclose = () => {
                console.log('WebSocket disconnected');
                updateConnectionStatus(false);
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        function updateConnectionStatus(connected) {
            const indicator = document.getElementById('connectionIndicator');
            const text = document.getElementById('connectionText');
            
            if (connected) {
                indicator.className = 'status-indicator status-active';
                text.textContent = 'Connected';
            } else {
                indicator.className = 'status-indicator status-stopped';
                text.textContent = 'Disconnected';
            }
        }
        
        async function loadSettings() {
            try {
                const response = await fetch('/api/settings');
                const settings = await response.json();
                
                document.getElementById('takeProfit').value = settings.take_profit || 1.5;
                document.getElementById('stopLoss').value = settings.stop_loss || 0.8;
                document.getElementById('maxConcurrent').value = settings.max_concurrent || 5;
                document.getElementById('positionSize').value = settings.position_size || 100;
                document.getElementById('leverage').value = settings.leverage || 1;
                
                updateSymbolList(settings.symbols || []);
            } catch (e) {
                console.error('Error loading settings:', e);
            }
        }
        
        function updateSymbolList(symbols) {
            const list = document.getElementById('symbolList');
            document.getElementById('activeSymbolCount').textContent = symbols.length;
            document.getElementById('symbolCount').textContent = symbols.length;
            
            if (symbols.length === 0) {
                list.innerHTML = '<div style="text-align: center; color: var(--text-secondary);">No symbols</div>';
                return;
            }
            
            list.innerHTML = symbols.map(symbol => `
                <div class="symbol-item">
                    <span>${symbol}</span>
                    <button class="symbol-remove" onclick="removeSymbol('${symbol}')">Remove</button>
                </div>
            `).join('');
        }
        
        async function botControl(action) {
            try {
                const response = await fetch(`/api/bot/${action}`, { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    updateBotStatus(result.state);
                    alert(`✅ Bot ${action}ed successfully!`);
                } else {
                    alert(`❌ Error: ${result.message}`);
                }
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }
        
        function updateBotStatus(state) {
            const indicator = document.getElementById('botStatusIndicator');
            const text = document.getElementById('botStatus');
            
            text.textContent = state.charAt(0).toUpperCase() + state.slice(1);
            
            if (state === 'running') {
                indicator.className = 'status-indicator status-active';
            } else if (state === 'paused') {
                indicator.className = 'status-indicator status-paused';
            } else {
                indicator.className = 'status-indicator status-stopped';
            }
        }
        
        async function updateSetting(setting, value) {
            try {
                const response = await fetch(`/api/settings/${setting}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ value: parseFloat(value) })
                });
                
                const result = await response.json();
                if (!result.success) {
                    console.error('Setting update failed:', result.message);
                }
            } catch (e) {
                console.error('Error updating setting:', e);
            }
        }
        
        async function addSymbol() {
            const input = document.getElementById('newSymbol');
            const symbol = input.value.trim().toUpperCase();
            
            if (!symbol) return;
            
            try {
                const response = await fetch('/api/symbols/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol })
                });
                
                const result = await response.json();
                if (result.success) {
                    input.value = '';
                    loadSettings();
                    alert(`✅ ${symbol} added successfully!`);
                } else {
                    alert(`❌ Error: ${result.message}`);
                }
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }
        
        async function removeSymbol(symbol) {
            if (!confirm(`Remove ${symbol}?`)) return;
            
            try {
                const response = await fetch('/api/symbols/remove', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol })
                });
                
                const result = await response.json();
                if (result.success) {
                    loadSettings();
                    alert(`✅ ${symbol} removed!`);
                } else {
                    alert(`❌ Error: ${result.message}`);
                }
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }
        
        async function applyAllSettings() {
            const settings = {
                take_profit: parseFloat(document.getElementById('takeProfit').value),
                stop_loss: parseFloat(document.getElementById('stopLoss').value),
                max_concurrent: parseInt(document.getElementById('maxConcurrent').value),
                position_size: parseFloat(document.getElementById('positionSize').value),
                leverage: parseInt(document.getElementById('leverage').value)
            };
            
            try {
                const response = await fetch('/api/settings/update-all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(settings)
                });
                
                const result = await response.json();
                if (result.success) {
                    alert('✅ All settings saved successfully!');
                } else {
                    alert(`❌ Error: ${result.message}`);
                }
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }
        
        async function closeAllPositions() {
            if (!confirm('⚠️ Close ALL positions? This cannot be undone!')) return;
            
            try {
                const response = await fetch('/api/positions/close-all', { method: 'POST' });
                const result = await response.json();
                
                alert(`✅ Closed ${result.closed} position(s)`);
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }
        
        async function closePosition(symbol) {
            if (!confirm(`Close position for ${symbol}?`)) return;
            
            try {
                const response = await fetch('/api/positions/close', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol })
                });
                
                const result = await response.json();
                if (result.success) {
                    alert(`✅ Position closed for ${symbol}`);
                } else {
                    alert(`❌ Error: ${result.message}`);
                }
            } catch (e) {
                alert(`❌ Error: ${e.message}`);
            }
        }
        
        function updateDashboard(data) {
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            
            // Update metrics
            document.getElementById('balance').textContent = '$' + (data.balance || 0).toFixed(2);
            document.getElementById('totalPnl').textContent = '$' + (data.total_pnl || 0).toFixed(2);
            document.getElementById('activePositions').textContent = data.active_positions || 0;
            document.getElementById('totalTrades').textContent = data.total_trades || 0;
            document.getElementById('winRate').textContent = ((data.win_rate || 0) * 100).toFixed(1) + '%';
            document.getElementById('activeTrades').textContent = data.active_positions || 0;
            
            // Update P&L color
            const pnlElement = document.getElementById('totalPnl');
            const pnl = data.total_pnl || 0;
            pnlElement.className = 'metric-value ' + (pnl > 0 ? 'positive' : pnl < 0 ? 'negative' : 'neutral');
            
            // Update environment
            document.getElementById('environment').textContent = data.environment || 'TESTNET';
            
            // Update bot status
            if (data.bot_state) {
                updateBotStatus(data.bot_state);
            }
            
            // Update positions
            updatePositions(data.positions || []);
            
            // Update chart
            updateChart(data.total_pnl || 0);
        }
        
        function updatePositions(positions) {
            const list = document.getElementById('positionList');
            
            if (positions.length === 0) {
                list.innerHTML = '<div style="text-align: center; color: var(--text-secondary);">No active positions</div>';
                return;
            }
            
            list.innerHTML = positions.map(pos => {
                const sideClass = pos.side === 'BUY' ? 'position-side-buy' : 'position-side-sell';
                const pnlClass = pos.pnl > 0 ? 'positive' : pos.pnl < 0 ? 'negative' : 'neutral';
                
                return `
                    <div class="position-item">
                        <div class="position-header">
                            <span class="position-symbol">${pos.symbol}</span>
                            <span class="${sideClass}">${pos.side}</span>
                        </div>
                        <div class="position-details">
                            Entry: $${pos.entry_price?.toFixed(4) || '0.0000'}<br>
                            Current: $${pos.current_price?.toFixed(4) || '0.0000'}<br>
                            Quantity: ${pos.quantity || 0}<br>
                            P&L: <span class="${pnlClass}">$${pos.pnl?.toFixed(2) || '0.00'}</span>
                        </div>
                        <button class="position-close" onclick="closePosition('${pos.symbol}')">Close Position</button>
                    </div>
                `;
            }).join('');
        }
        
        function updateChart(pnl) {
            const now = new Date();
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(pnl);
            
            if (performanceChart.data.labels.length > 50) {
                performanceChart.data.labels.shift();
                performanceChart.data.datasets[0].data.shift();
            }
            
            performanceChart.update('none');
        }
    </script>
</body>
</html>
        """
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.add(ws)
        self.logger.info(f"Client connected from {request.remote}. Total: {len(self.websocket_connections)}")
        
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
    
    # API Endpoints
    async def status_api(self, request):
        """Get current status"""
        try:
            status = await self._get_status()
            return web.json_response(status, default=self._json_serializer)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_settings_api(self, request):
        """Get current settings"""
        return web.json_response(self.settings)
    
    async def bot_start_api(self, request):
        """Start the bot"""
        try:
            self.trading_system.is_trading = True
            self.bot_state = "running"
            self.logger.info("Bot started via dashboard")
            return web.json_response({'success': True, 'state': self.bot_state})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def bot_pause_api(self, request):
        """Pause the bot"""
        try:
            self.trading_system.is_trading = False
            self.bot_state = "paused"
            self.logger.info("Bot paused via dashboard")
            return web.json_response({'success': True, 'state': self.bot_state})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def bot_restart_api(self, request):
        """Restart the bot"""
        try:
            self.trading_system.is_trading = False
            await asyncio.sleep(1)
            self.trading_system.is_trading = True
            self.bot_state = "running"
            self.logger.info("Bot restarted via dashboard")
            return web.json_response({'success': True, 'state': self.bot_state})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def bot_stop_api(self, request):
        """Stop the bot"""
        try:
            self.trading_system.is_trading = False
            self.bot_state = "stopped"
            self.logger.info("Bot stopped via dashboard")
            return web.json_response({'success': True, 'state': self.bot_state})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_take_profit_api(self, request):
        """Update take profit"""
        try:
            data = await request.json()
            self.settings['take_profit'] = float(data['value'])
            self._save_settings()
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_stop_loss_api(self, request):
        """Update stop loss"""
        try:
            data = await request.json()
            self.settings['stop_loss'] = float(data['value'])
            self._save_settings()
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_max_concurrent_api(self, request):
        """Update max concurrent trades"""
        try:
            data = await request.json()
            self.settings['max_concurrent'] = int(data['value'])
            self._save_settings()
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_leverage_api(self, request):
        """Update leverage"""
        try:
            data = await request.json()
            self.settings['leverage'] = int(data['value'])
            self._save_settings()
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_position_size_api(self, request):
        """Update position size"""
        try:
            data = await request.json()
            self.settings['position_size'] = float(data['value'])
            self._save_settings()
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_all_settings_api(self, request):
        """Update all settings at once"""
        try:
            data = await request.json()
            self.settings.update(data)
            self._save_settings()
            self.logger.info(f"Settings updated via dashboard: {data}")
            return web.json_response({'success': True})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def update_symbols_api(self, request):
        """Update symbols list (bulk update)"""
        try:
            data = await request.json()
            new_symbols = data.get('symbols', [])
            
            if not new_symbols:
                return web.json_response({'success': False, 'message': 'No symbols provided'})
            
            # Update settings
            self.settings['symbols'] = new_symbols
            self.trading_system.symbols = new_symbols
            self._save_settings()
            
            self.logger.info(f"Symbols updated to: {len(new_symbols)} pairs")
            return web.json_response({'success': True, 'count': len(new_symbols)})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def add_symbol_api(self, request):
        """Add a trading symbol"""
        try:
            data = await request.json()
            symbol = data['symbol'].upper()
            
            if symbol not in self.settings['symbols']:
                self.settings['symbols'].append(symbol)
                self.trading_system.symbols.append(symbol)
                self._save_settings()
                self.logger.info(f"Symbol added: {symbol}")
                return web.json_response({'success': True})
            else:
                return web.json_response({'success': False, 'message': 'Symbol already exists'})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def remove_symbol_api(self, request):
        """Remove a trading symbol"""
        try:
            data = await request.json()
            symbol = data['symbol'].upper()
            
            if symbol in self.settings['symbols']:
                self.settings['symbols'].remove(symbol)
                if symbol in self.trading_system.symbols:
                    self.trading_system.symbols.remove(symbol)
                self._save_settings()
                self.logger.info(f"Symbol removed: {symbol}")
                return web.json_response({'success': True})
            else:
                return web.json_response({'success': False, 'message': 'Symbol not found'})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def get_available_symbols_api(self, request):
        """Get list of available symbols"""
        try:
            # Load from trading pairs config
            config_file = Path("config/trading_pairs.yaml")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    pairs = yaml.safe_load(f)
                    return web.json_response(pairs.get('default_symbols', []))
            return web.json_response([])
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def close_position_api(self, request):
        """Close a specific position"""
        try:
            data = await request.json()
            symbol = data['symbol']
            
            if symbol in self.trading_system.positions:
                await self.trading_system._close_position(symbol, "Manual close from dashboard")
                self.logger.info(f"Position closed via dashboard: {symbol}")
                return web.json_response({'success': True})
            else:
                return web.json_response({'success': False, 'message': 'Position not found'})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def close_all_positions_api(self, request):
        """Close all positions"""
        try:
            closed = 0
            for symbol in list(self.trading_system.positions.keys()):
                try:
                    await self.trading_system._close_position(symbol, "Bulk close from dashboard")
                    closed += 1
                except Exception as e:
                    self.logger.error(f"Error closing {symbol}: {e}")
            
            self.logger.info(f"All positions closed via dashboard: {closed} positions")
            return web.json_response({'success': True, 'closed': closed})
        except Exception as e:
            return web.json_response({'success': False, 'message': str(e)})
    
    async def _get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
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
                    'quantity': position.quantity
                })
            
            win_rate = 0.0
            if self.trading_system.total_trades > 0:
                win_rate = self.trading_system.winning_trades / self.trading_system.total_trades
            
            return {
                'timestamp': datetime.now().isoformat(),
                'environment': 'TESTNET' if self.trading_system.use_testnet else 'LIVE',
                'balance': self.trading_system.risk_manager.current_balance if self.trading_system.risk_manager else 0,
                'total_pnl': total_pnl,
                'active_positions': len(positions),
                'positions': positions,
                'total_trades': self.trading_system.total_trades,
                'winning_trades': self.trading_system.winning_trades,
                'win_rate': win_rate,
                'is_trading': self.trading_system.is_trading,
                'bot_state': self.bot_state,
                'settings': self.settings
            }
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {}
    
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
        
        # Bind to 0.0.0.0 for network access
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"🎮 Enhanced Control Dashboard started")
        self.logger.info(f"   Local access: http://localhost:{self.port}")
        self.logger.info(f"   Network access: http://{self._get_local_ip()}:{self.port}")
        self.logger.info(f"   Accessible from any device on your network!")
        
        return runner
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "your-local-ip"
    
    async def start_update_loop(self):
        """Start the update loop"""
        while True:
            try:
                if self.websocket_connections:
                    status = await self._get_status()
                    await self.broadcast_update(status)
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5.0)
    
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
            
            self.websocket_connections -= disconnected
            
        except Exception as e:
            self.logger.error(f"Error broadcasting: {e}")

# Integration function
async def start_enhanced_dashboard(trading_system, ai_engine=None, port: int = 8080, host: str = "0.0.0.0"):
    """Start the enhanced control dashboard"""
    dashboard = EnhancedControlDashboard(trading_system, ai_engine, port, host)
    
    runner = await dashboard.start_server()
    update_task = asyncio.create_task(dashboard.start_update_loop())
    
    return dashboard, runner, update_task
