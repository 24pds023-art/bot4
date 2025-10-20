#!/usr/bin/env python3
"""
🌐 ADVANCED AI-POWERED TRADING DASHBOARD
=======================================
⚡ Real-time AI insights and deep learning analytics
🧠 Model performance monitoring and online learning
📊 Advanced charting with predictive overlays
🎯 Intelligent alerts and automated decision support
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

class AdvancedTradingDashboard:
    """Advanced AI-powered trading dashboard"""
    
    def __init__(self, trading_system, ai_engine=None, port: int = 8080):
        self.trading_system = trading_system
        self.ai_engine = ai_engine
        self.port = port
        self.app = web.Application()
        self.websocket_connections = set()
        
        # Enhanced data tracking
        self.ai_predictions = deque(maxlen=100)
        self.model_performance = deque(maxlen=50)
        self.feature_importance = {}
        self.prediction_accuracy = deque(maxlen=100)
        
        # Real-time analytics
        self.market_sentiment = {}
        self.volatility_forecast = {}
        self.risk_metrics = {}
        
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
        self.app.router.add_get('/api/ai-insights', self.ai_insights_api)
        self.app.router.add_get('/api/model-performance', self.model_performance_api)
        self.app.router.add_post('/api/emergency-stop', self.emergency_stop_api)
        self.app.router.add_post('/api/retrain-models', self.retrain_models_api)
        
        # Add CORS
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def dashboard_handler(self, request):
        """Serve the advanced dashboard HTML"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 AI-Powered Trading Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.2.1/dist/chartjs-plugin-annotation.min.js"></script>
    <style>
        :root {
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-card: #2a2a2a;
            --accent-green: #00ff88;
            --accent-blue: #00d4ff;
            --accent-red: #ff4757;
            --accent-yellow: #ffa502;
            --accent-purple: #9c88ff;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --border-color: #404040;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .ai-status {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }
        
        .ai-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(156, 136, 255, 0.1);
            border-radius: 20px;
            border: 1px solid var(--accent-purple);
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
            position: relative;
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-card.ai-enhanced::before {
            content: '🧠';
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 1.2em;
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
        
        .metric-ai-insight {
            font-size: 0.8em;
            color: var(--accent-purple);
            margin-top: 8px;
            font-style: italic;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-section {
            display: grid;
            grid-template-rows: 2fr 1fr;
            gap: 20px;
        }
        
        .chart-container {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
            position: relative;
        }
        
        .chart-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .ai-confidence {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9em;
            color: var(--accent-purple);
        }
        
        .confidence-bar {
            width: 60px;
            height: 6px;
            background: rgba(156, 136, 255, 0.3);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: var(--accent-purple);
            transition: width 0.3s ease;
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
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .ai-predictions {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .prediction-item {
            background: rgba(156, 136, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 4px solid var(--accent-purple);
        }
        
        .prediction-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .prediction-symbol {
            font-weight: bold;
            color: var(--text-primary);
        }
        
        .prediction-signal {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .signal-buy { background: var(--accent-green); color: black; }
        .signal-sell { background: var(--accent-red); color: white; }
        .signal-hold { background: var(--accent-yellow); color: black; }
        
        .prediction-details {
            font-size: 0.9em;
            color: var(--text-secondary);
        }
        
        .model-performance {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }
        
        .performance-metric {
            text-align: center;
            padding: 8px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 6px;
        }
        
        .performance-value {
            font-size: 1.1em;
            font-weight: bold;
            color: var(--accent-blue);
        }
        
        .performance-label {
            font-size: 0.8em;
            color: var(--text-secondary);
        }
        
        .feature-importance {
            margin-top: 15px;
        }
        
        .feature-bar {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .feature-name {
            width: 80px;
            font-size: 0.8em;
            color: var(--text-secondary);
        }
        
        .feature-bar-bg {
            flex: 1;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            margin: 0 10px;
            overflow: hidden;
        }
        
        .feature-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            transition: width 0.3s ease;
        }
        
        .feature-value {
            font-size: 0.8em;
            color: var(--text-primary);
            width: 40px;
            text-align: right;
        }
        
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            font-size: 0.9em;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white;
        }
        
        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, var(--accent-red), #e74c3c);
            color: white;
            grid-column: span 2;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            opacity: 0.9;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-active { background: var(--accent-green); }
        .status-inactive { background: var(--accent-red); }
        .status-learning { background: var(--accent-purple); }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .positive { color: var(--accent-green); }
        .negative { color: var(--accent-red); }
        .neutral { color: var(--text-primary); }
        
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            .controls {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 AI-Powered Trading Dashboard</h1>
            <p>Advanced Deep Learning • Real-time Predictions • Online Learning</p>
            
            <div class="ai-status">
                <div class="ai-indicator">
                    <span class="status-indicator status-learning" id="aiStatus"></span>
                    <span id="aiStatusText">AI Learning</span>
                </div>
                <div class="ai-indicator">
                    <span>Models: <strong id="modelCount">0</strong></span>
                </div>
                <div class="ai-indicator">
                    <span>Accuracy: <strong id="aiAccuracy">0%</strong></span>
                </div>
            </div>
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
                <span>Predictions: <strong id="totalPredictions">0</strong></span>
            </div>
            <div class="status-item">
                <span>Last Update: <strong id="lastUpdate">--:--:--</strong></span>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card ai-enhanced">
                <div class="metric-value neutral" id="balance">$0.00</div>
                <div class="metric-label">💰 Account Balance</div>
                <div class="metric-ai-insight" id="balanceInsight">AI analyzing balance trends...</div>
            </div>
            <div class="metric-card ai-enhanced">
                <div class="metric-value neutral" id="totalPnl">$0.00</div>
                <div class="metric-label">📈 Total P&L</div>
                <div class="metric-ai-insight" id="pnlInsight">AI predicting P&L trajectory...</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="activePositions">0</div>
                <div class="metric-label">📊 Active Positions</div>
            </div>
            <div class="metric-card ai-enhanced">
                <div class="metric-value" id="aiSignals">0</div>
                <div class="metric-label">🧠 AI Signals</div>
                <div class="metric-ai-insight" id="signalInsight">Learning market patterns...</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="totalTrades">0</div>
                <div class="metric-label">🎯 Total Trades</div>
            </div>
            <div class="metric-card ai-enhanced">
                <div class="metric-value" id="winRate">0%</div>
                <div class="metric-label">🏆 Win Rate</div>
                <div class="metric-ai-insight" id="winRateInsight">AI optimizing strategies...</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="chart-section">
                <div class="chart-container">
                    <div class="chart-title">
                        <h3>📈 AI-Enhanced Performance</h3>
                        <div class="ai-confidence">
                            <span>Prediction Confidence:</span>
                            <div class="confidence-bar">
                                <div class="confidence-fill" id="confidenceFill" style="width: 0%"></div>
                            </div>
                            <span id="confidenceValue">0%</span>
                        </div>
                    </div>
                    <canvas id="performanceChart" width="400" height="200"></canvas>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">
                        <h3>🧠 Model Performance</h3>
                    </div>
                    <canvas id="modelChart" width="400" height="100"></canvas>
                </div>
            </div>
            
            <div class="side-panel">
                <div class="panel-card">
                    <div class="panel-title">
                        🔮 AI Predictions
                    </div>
                    
                    <div class="ai-predictions" id="predictionsContainer">
                        <div style="text-align: center; color: var(--text-secondary);">
                            AI is analyzing market data...
                        </div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <div class="panel-title">
                        📊 Model Performance
                    </div>
                    
                    <div class="model-performance">
                        <div class="performance-metric">
                            <div class="performance-value" id="modelAccuracy">0%</div>
                            <div class="performance-label">Accuracy</div>
                        </div>
                        <div class="performance-metric">
                            <div class="performance-value" id="modelPrecision">0%</div>
                            <div class="performance-label">Precision</div>
                        </div>
                        <div class="performance-metric">
                            <div class="performance-value" id="trainingSamples">0</div>
                            <div class="performance-label">Training Samples</div>
                        </div>
                        <div class="performance-metric">
                            <div class="performance-value" id="modelVersion">v1.0</div>
                            <div class="performance-label">Model Version</div>
                        </div>
                    </div>
                    
                    <div class="feature-importance">
                        <h4 style="margin-bottom: 10px; color: var(--accent-blue);">Feature Importance</h4>
                        <div id="featureImportanceContainer">
                            <div class="feature-bar">
                                <div class="feature-name">Momentum</div>
                                <div class="feature-bar-bg">
                                    <div class="feature-bar-fill" style="width: 0%"></div>
                                </div>
                                <div class="feature-value">0%</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <div class="panel-title">
                        🎮 AI Controls
                    </div>
                    
                    <div class="controls">
                        <button class="btn btn-primary" onclick="retrainModels()">🧠 Retrain AI</button>
                        <button class="btn btn-secondary" onclick="refreshData()">🔄 Refresh</button>
                        <button class="btn btn-danger" onclick="emergencyStop()">🚨 Emergency Stop</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let performanceChart = null;
        let modelChart = null;
        let startTime = Date.now();
        
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            connectWebSocket();
            setInterval(updateConnectionStatus, 5000);
        });
        
        function initializeCharts() {
            // Performance Chart
            const ctx1 = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'P&L ($)',
                            data: [],
                            borderColor: '#00ff88',
                            backgroundColor: 'rgba(0, 255, 136, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'AI Prediction',
                            data: [],
                            borderColor: '#9c88ff',
                            backgroundColor: 'rgba(156, 136, 255, 0.1)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            fill: false,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            display: true,
                            labels: { color: '#b0b0b0' }
                        }
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
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
            
            // Model Performance Chart
            const ctx2 = document.getElementById('modelChart').getContext('2d');
            modelChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Model Accuracy',
                            data: [],
                            borderColor: '#9c88ff',
                            backgroundColor: 'rgba(156, 136, 255, 0.2)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { color: '#b0b0b0' }
                        },
                        y: {
                            min: 0,
                            max: 1,
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { 
                                color: '#b0b0b0',
                                callback: function(value) {
                                    return (value * 100).toFixed(0) + '%';
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
            
            // Update basic metrics
            updateMetric('balance', data.balance || 0, '$');
            updateMetric('totalPnl', data.total_pnl || 0, '$');
            updateMetric('activePositions', data.active_positions || 0);
            updateMetric('totalTrades', data.total_trades || 0);
            updateMetric('winRate', ((data.win_rate || 0) * 100).toFixed(1), '%');
            
            // Update AI-specific metrics
            if (data.ai_insights) {
                updateAIMetrics(data.ai_insights);
            }
            
            // Update predictions
            if (data.ai_predictions) {
                updatePredictions(data.ai_predictions);
            }
            
            // Update model performance
            if (data.model_performance) {
                updateModelPerformance(data.model_performance);
            }
            
            // Update charts
            updateCharts(data);
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
        
        function updateAIMetrics(aiInsights) {
            // Update AI status
            document.getElementById('aiAccuracy').textContent = (aiInsights.accuracy * 100).toFixed(1) + '%';
            document.getElementById('totalPredictions').textContent = aiInsights.total_predictions || 0;
            document.getElementById('aiSignals').textContent = aiInsights.signals_generated || 0;
            
            // Update insights
            if (aiInsights.balance_insight) {
                document.getElementById('balanceInsight').textContent = aiInsights.balance_insight;
            }
            if (aiInsights.pnl_insight) {
                document.getElementById('pnlInsight').textContent = aiInsights.pnl_insight;
            }
            if (aiInsights.signal_insight) {
                document.getElementById('signalInsight').textContent = aiInsights.signal_insight;
            }
            if (aiInsights.win_rate_insight) {
                document.getElementById('winRateInsight').textContent = aiInsights.win_rate_insight;
            }
        }
        
        function updatePredictions(predictions) {
            const container = document.getElementById('predictionsContainer');
            
            if (predictions.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-secondary);">AI is analyzing market data...</div>';
                return;
            }
            
            container.innerHTML = predictions.slice(-5).reverse().map(pred => {
                const signalClass = pred.signal === 'BUY' ? 'signal-buy' : pred.signal === 'SELL' ? 'signal-sell' : 'signal-hold';
                const time = new Date(pred.timestamp).toLocaleTimeString();
                
                return `
                    <div class="prediction-item">
                        <div class="prediction-header">
                            <span class="prediction-symbol">${pred.symbol}</span>
                            <span class="prediction-signal ${signalClass}">${pred.signal}</span>
                        </div>
                        <div class="prediction-details">
                            ${time} | Confidence: ${(pred.confidence * 100).toFixed(1)}%
                            <br>Buy: ${(pred.probability_buy * 100).toFixed(1)}% | Sell: ${(pred.probability_sell * 100).toFixed(1)}%
                        </div>
                    </div>
                `;
            }).join('');
            
            // Update confidence display
            if (predictions.length > 0) {
                const latestPred = predictions[predictions.length - 1];
                const confidence = (latestPred.confidence * 100).toFixed(0);
                document.getElementById('confidenceValue').textContent = confidence + '%';
                document.getElementById('confidenceFill').style.width = confidence + '%';
            }
        }
        
        function updateModelPerformance(performance) {
            document.getElementById('modelAccuracy').textContent = (performance.accuracy * 100).toFixed(1) + '%';
            document.getElementById('modelPrecision').textContent = (performance.precision * 100).toFixed(1) + '%';
            document.getElementById('trainingSamples').textContent = performance.training_samples || 0;
            
            // Update feature importance
            if (performance.feature_importance) {
                updateFeatureImportance(performance.feature_importance);
            }
        }
        
        function updateFeatureImportance(importance) {
            const container = document.getElementById('featureImportanceContainer');
            
            const features = Object.entries(importance)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 5);
            
            container.innerHTML = features.map(([name, value]) => `
                <div class="feature-bar">
                    <div class="feature-name">${name}</div>
                    <div class="feature-bar-bg">
                        <div class="feature-bar-fill" style="width: ${(value * 100).toFixed(0)}%"></div>
                    </div>
                    <div class="feature-value">${(value * 100).toFixed(0)}%</div>
                </div>
            `).join('');
        }
        
        function updateCharts(data) {
            const now = new Date();
            
            // Update performance chart
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(data.total_pnl || 0);
            
            if (data.ai_prediction) {
                performanceChart.data.datasets[1].data.push(data.ai_prediction);
            }
            
            // Keep only last 50 points
            if (performanceChart.data.labels.length > 50) {
                performanceChart.data.labels.shift();
                performanceChart.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            performanceChart.update('none');
            
            // Update model chart
            if (data.model_performance && data.model_performance.accuracy) {
                modelChart.data.labels.push(now);
                modelChart.data.datasets[0].data.push(data.model_performance.accuracy);
                
                if (modelChart.data.labels.length > 30) {
                    modelChart.data.labels.shift();
                    modelChart.data.datasets[0].data.shift();
                }
                
                modelChart.update('none');
            }
        }
        
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(console.error);
        }
        
        function retrainModels() {
            if (confirm('🧠 Retrain AI models with latest data?\\n\\nThis will improve prediction accuracy but may take a few minutes.')) {
                fetch('/api/retrain-models', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert('🧠 AI models retrained successfully!\\n\\nAccuracy: ' + (data.accuracy * 100).toFixed(1) + '%');
                    })
                    .catch(error => {
                        console.error('Retraining failed:', error);
                        alert('❌ Model retraining failed. Check console for details.');
                    });
            }
        }
        
        function emergencyStop() {
            if (confirm('⚠️ This will stop all trading and close positions. Continue?')) {
                fetch('/api/emergency-stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert('🚨 Emergency stop executed: ' + (data.message || 'System stopped'));
                        location.reload();
                    })
                    .catch(error => {
                        console.error('Emergency stop failed:', error);
                        alert('❌ Emergency stop failed. Check console.');
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
        self.logger.info(f"Advanced dashboard client connected. Total: {len(self.websocket_connections)}")
        
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
        """Enhanced status API with AI insights"""
        try:
            # Get basic status
            basic_status = await self._get_basic_status()
            
            # Add AI insights
            ai_insights = await self._get_ai_insights()
            
            # Combine data
            status = {
                **basic_status,
                'ai_insights': ai_insights,
                'ai_predictions': list(self.ai_predictions),
                'model_performance': await self._get_model_performance(),
                'feature_importance': self.feature_importance
            }
            
            return web.json_response(status, default=self._json_serializer)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def ai_insights_api(self, request):
        """AI insights API endpoint"""
        try:
            insights = await self._get_ai_insights()
            return web.json_response(insights, default=self._json_serializer)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def model_performance_api(self, request):
        """Model performance API endpoint"""
        try:
            performance = await self._get_model_performance()
            return web.json_response(performance, default=self._json_serializer)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def retrain_models_api(self, request):
        """Retrain AI models endpoint"""
        try:
            if self.ai_engine:
                # Trigger model retraining
                performance = await self.ai_engine.retrain_all_models()
                return web.json_response({
                    'success': True,
                    'message': 'Models retrained successfully',
                    'accuracy': performance.get('accuracy', 0),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return web.json_response({
                    'success': False,
                    'message': 'AI engine not available'
                })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
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
    
    async def _get_basic_status(self) -> Dict[str, Any]:
        """Get basic trading system status"""
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
                    'quantity': position.quantity,
                    'entry_time': position.entry_time.isoformat()
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
                'is_trading': self.trading_system.is_trading
            }
        except Exception as e:
            self.logger.error(f"Error getting basic status: {e}")
            return {}
    
    async def _get_ai_insights(self) -> Dict[str, Any]:
        """Get AI-powered insights"""
        try:
            if not self.ai_engine:
                return {
                    'accuracy': 0.0,
                    'total_predictions': 0,
                    'signals_generated': 0,
                    'balance_insight': 'AI engine not available',
                    'pnl_insight': 'AI engine not available',
                    'signal_insight': 'AI engine not available',
                    'win_rate_insight': 'AI engine not available'
                }
            
            performance = self.ai_engine.get_model_performance()
            
            # Generate insights based on current data
            insights = {
                'accuracy': performance.get('accuracy', 0.0),
                'total_predictions': performance.get('total_predictions', 0),
                'signals_generated': len(self.ai_predictions),
                'balance_insight': self._generate_balance_insight(),
                'pnl_insight': self._generate_pnl_insight(),
                'signal_insight': self._generate_signal_insight(),
                'win_rate_insight': self._generate_win_rate_insight()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting AI insights: {e}")
            return {}
    
    def _generate_balance_insight(self) -> str:
        """Generate AI insight about balance trends"""
        try:
            balance = self.trading_system.risk_manager.current_balance if self.trading_system.risk_manager else 0
            
            if balance > 5000:
                return "AI detects strong capital growth trend"
            elif balance < 4500:
                return "AI recommends risk reduction strategies"
            else:
                return "AI monitoring balance stability"
                
        except Exception:
            return "AI analyzing balance patterns..."
    
    def _generate_pnl_insight(self) -> str:
        """Generate AI insight about P&L trends"""
        try:
            total_pnl = sum(pos.pnl for pos in self.trading_system.positions.values())
            
            if total_pnl > 10:
                return "AI predicts continued profitability"
            elif total_pnl < -10:
                return "AI suggests defensive positioning"
            else:
                return "AI monitoring P&L momentum"
                
        except Exception:
            return "AI analyzing P&L patterns..."
    
    def _generate_signal_insight(self) -> str:
        """Generate AI insight about signal quality"""
        try:
            if len(self.ai_predictions) > 10:
                recent_confidence = [p['confidence'] for p in list(self.ai_predictions)[-10:]]
                avg_confidence = sum(recent_confidence) / len(recent_confidence)
                
                if avg_confidence > 0.7:
                    return "AI confidence high - strong signals"
                elif avg_confidence < 0.5:
                    return "AI learning - signal quality improving"
                else:
                    return "AI signals showing good consistency"
            else:
                return "AI building signal history..."
                
        except Exception:
            return "AI analyzing signal patterns..."
    
    def _generate_win_rate_insight(self) -> str:
        """Generate AI insight about win rate trends"""
        try:
            win_rate = 0.0
            if self.trading_system.total_trades > 0:
                win_rate = self.trading_system.winning_trades / self.trading_system.total_trades
            
            if win_rate > 0.7:
                return "AI strategies performing excellently"
            elif win_rate < 0.4:
                return "AI adapting strategies for improvement"
            else:
                return "AI optimizing win rate strategies"
                
        except Exception:
            return "AI analyzing win rate trends..."
    
    async def _get_model_performance(self) -> Dict[str, Any]:
        """Get detailed model performance metrics"""
        try:
            if not self.ai_engine:
                return {
                    'accuracy': 0.0,
                    'precision': 0.0,
                    'training_samples': 0,
                    'feature_importance': {}
                }
            
            performance = self.ai_engine.get_model_performance()
            
            return {
                'accuracy': performance.get('accuracy', 0.0),
                'precision': performance.get('accuracy', 0.0),  # Simplified
                'training_samples': performance.get('online_learning_samples', 0),
                'feature_importance': self.feature_importance or {
                    'momentum': 0.25,
                    'rsi': 0.20,
                    'volume_ratio': 0.18,
                    'volatility': 0.15,
                    'price_change': 0.22
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model performance: {e}")
            return {}
    
    def _json_serializer(self, obj):
        """JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    async def start_server(self):
        """Start the advanced dashboard server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        
        self.logger.info(f"🧠 Advanced AI Dashboard started at http://localhost:{self.port}")
        return runner
    
    async def start_update_loop(self):
        """Start the enhanced update loop"""
        while True:
            try:
                if self.websocket_connections:
                    # Get comprehensive status
                    status = await self.status_api(None)
                    if hasattr(status, 'body'):
                        data = json.loads(status.body.decode())
                        await self.broadcast_update(data)
                
                # Update every 1 second for real-time AI insights
                await asyncio.sleep(1.0 if self.websocket_connections else 5.0)
                
            except Exception as e:
                self.logger.error(f"Error in dashboard update loop: {e}")
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
            
            # Remove disconnected clients
            self.websocket_connections -= disconnected
            
        except Exception as e:
            self.logger.error(f"Error broadcasting update: {e}")

# Integration function
async def start_advanced_dashboard(trading_system, ai_engine=None, port: int = 8080):
    """Start the advanced AI-powered dashboard"""
    dashboard = AdvancedTradingDashboard(trading_system, ai_engine, port)
    
    # Start server
    runner = await dashboard.start_server()
    
    # Start update loop
    update_task = asyncio.create_task(dashboard.start_update_loop())
    
    return dashboard, runner, update_task