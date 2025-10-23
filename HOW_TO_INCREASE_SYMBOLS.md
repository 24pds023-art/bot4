# 🚀 How to Increase Trading Symbols

## Quick Answer

### Option 1: Command Line (Easiest)
```bash
# Use 50 symbols
python3 ULTIMATE_LAUNCHER.py --symbols 50 --auto

# Use 80 symbols
python3 ULTIMATE_LAUNCHER.py --symbols 80 --auto

# Use any number
python3 ULTIMATE_LAUNCHER.py --symbols 100 --auto
```

### Option 2: Edit Configuration File

Edit `config/trading_pairs.yaml`:

```yaml
# Change the default_symbols list
default_symbols:
  - BTCUSDT
  - ETHUSDT
  - BNBUSDT
  # ... add more symbols here
```

---

## Detailed Instructions

### Method 1: Command Line (Recommended)

The easiest way is to use the `--symbols` flag:

```bash
# 30 symbols (default)
python3 ULTIMATE_LAUNCHER.py --auto

# 50 symbols
python3 ULTIMATE_LAUNCHER.py --symbols 50 --auto

# 80 symbols
python3 ULTIMATE_LAUNCHER.py --symbols 80 --auto

# 100 symbols
python3 ULTIMATE_LAUNCHER.py --symbols 100 --auto
```

**How it works:**
- System automatically selects the best symbols
- Prioritizes high-liquidity pairs
- Stays within API rate limits

---

### Method 2: Edit Configuration File

1. **Open the configuration file:**
```bash
nano config/trading_pairs.yaml
```

2. **Find the `default_symbols` section**

3. **Add more symbols:**
```yaml
default_symbols:
  # High Priority (Top Market Cap)
  - BTCUSDT
  - ETHUSDT
  - BNBUSDT
  - SOLUSDT
  - XRPUSDT
  
  # Add more from medium_priority
  - ADAUSDT
  - AVAXUSDT
  - DOGEUSDT
  - DOTUSDT
  - MATICUSDT
  - TRXUSDT
  - LINKUSDT
  - ATOMUSDT
  - UNIUSDT
  - LTCUSDT
  
  # Add more from low_priority
  - ARBUSDT
  - OPUSDT
  - APTUSDT
  - NEARUSDT
  - FILUSDT
  - INJUSDT
  - SUIUSDT
  - AAVEUSDT
  - IMXUSDT
  
  # Add DeFi tokens
  - CRVUSDT
  - COMPUSDT
  - MKRUSDT
  - SUSHIUSDT
  
  # Add AI tokens
  - FETUSDT
  - AGIXUSDT
  - OCEANUSDT
  - RENDERUSDT
  
  # Add Gaming/Metaverse
  - AXSUSDT
  - SANDUSDT
  - MANAUSDT
  - APEUSDT
  - GALAUSDT
  
  # Add Meme coins (if desired)
  - PEPEUSDT
  - SHIBUSDT
  - FLOKIUSDT
  
  # Add more as needed...
```

4. **Save and run:**
```bash
python3 ULTIMATE_LAUNCHER.py --auto
```

---

### Method 3: Use Pre-defined Categories

You can combine categories in `config/trading_pairs.yaml`:

```yaml
# Use all high priority
default_symbols: !include high_priority

# Or combine multiple categories manually
default_symbols:
  # Include high priority
  - BTCUSDT
  - ETHUSDT
  - BNBUSDT
  - SOLUSDT
  - XRPUSDT
  
  # Include medium priority
  - ADAUSDT
  - AVAXUSDT
  # ... (copy from medium_priority section)
  
  # Include DeFi
  - UNIUSDT
  - AAVEUSDT
  # ... (copy from defi_tokens section)
```

---

## Available Categories

The system has these pre-configured categories:

### High Priority (5 pairs)
Top market cap, highest liquidity
```
BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT
```

### Medium Priority (15 pairs)
Large cap altcoins
```
ADAUSDT, AVAXUSDT, DOGEUSDT, DOTUSDT, MATICUSDT,
TRXUSDT, LINKUSDT, ATOMUSDT, UNIUSDT, LTCUSDT, etc.
```

### DeFi Tokens (8 pairs)
```
UNIUSDT, AAVEUSDT, CRVUSDT, COMPUSDT,
MKRUSDT, SUSHIUSDT, SNXUSDT, YFIUSDT
```

### Layer 2 (5 pairs)
```
ARBUSDT, OPUSDT, MATICUSDT, IMXUSDT, ZKUSDT
```

### AI Tokens (4 pairs)
```
FETUSDT, AGIXUSDT, OCEANUSDT, RENDERUSDT
```

### Gaming/Metaverse (5 pairs)
```
AXSUSDT, SANDUSDT, MANAUSDT, APEUSDT, GALAUSDT
```

### Meme Coins (4 pairs)
```
DOGEUSDT, SHIBUSDT, PEPEUSDT, FLOKIUSDT
```

---

## Recommended Configurations

### Conservative (20-30 pairs)
**Best for:** Stable operation, learning
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 25 --auto
```
- API usage: ~75-90 requests/min
- WebSocket connections: ~75-90
- Resource usage: Low
- Recommended for: Beginners, testing

### Balanced (30-50 pairs) ⭐ RECOMMENDED
**Best for:** Good diversification, moderate risk
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 40 --auto
```
- API usage: ~120-150 requests/min
- WebSocket connections: ~120-150
- Resource usage: Medium
- Recommended for: Most users

### Aggressive (50-80 pairs)
**Best for:** Maximum coverage, experienced users
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 60 --auto
```
- API usage: ~180-240 requests/min
- WebSocket connections: ~180-240
- Resource usage: High
- Recommended for: Advanced users

### Maximum (80-100 pairs)
**Best for:** Professional use, high-end systems
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 100 --auto
```
- API usage: ~300-400 requests/min
- WebSocket connections: ~300-400
- Resource usage: Very High
- Recommended for: Professionals only

---

## API Rate Limits

### Binance Limits
- **Futures API:** ~1,200 requests/minute (weight-based)
- **WebSocket:** Unlimited (but connection limits apply)

### Our System Usage
| Symbols | API Requests/min | WebSocket Connections | Safe? |
|---------|------------------|----------------------|-------|
| 20 | ~60-80 | ~60-80 | ✅ Very Safe |
| 30 | ~90-120 | ~90-120 | ✅ Safe (Default) |
| 50 | ~150-200 | ~150-200 | ✅ Safe |
| 80 | ~240-320 | ~240-320 | ⚠️ Monitor |
| 100+ | ~300-400+ | ~300-400+ | ⚠️ Advanced Only |

**Built-in Protection:**
- ✅ Automatic rate limiting
- ✅ Request prioritization
- ✅ Connection pooling
- ✅ Burst handling

---

## System Requirements

### For 30 Symbols (Default)
- **RAM:** 512MB-1GB
- **CPU:** 2 cores, 15-20% usage
- **Network:** Stable internet

### For 50 Symbols
- **RAM:** 1-2GB
- **CPU:** 4 cores, 20-30% usage
- **Network:** Stable, fast internet

### For 80 Symbols
- **RAM:** 2-3GB
- **CPU:** 4-6 cores, 30-40% usage
- **Network:** Very stable, fast internet

### For 100+ Symbols
- **RAM:** 3-4GB
- **CPU:** 8+ cores, 40-50% usage
- **Network:** Dedicated, very fast internet

---

## Examples

### Example 1: Start with 50 Symbols
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 50 --auto
```

Expected output:
```
🚀 Initializing system with 50 symbols...
📊 Loading 50 trading pairs...
   Symbols: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT...
✅ Trading system initialized
✅ AI engine initialized
✅ Dashboard initialized on port 8080
```

### Example 2: Test with 80 Symbols
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 80 --test
```

This will test the system with 80 symbols without starting trading.

### Example 3: Dashboard Only with 100 Symbols
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 100 --dashboard-only
```

Monitor 100 symbols without executing trades.

---

## Monitoring Performance

### Check System Resources
```bash
# Monitor CPU and memory
top

# Or use htop
htop

# Check network connections
netstat -an | grep ESTABLISHED | wc -l
```

### Check Logs
```bash
# Watch logs in real-time
tail -f logs/improved_trading.log

# Check for errors
grep ERROR logs/improved_trading.log

# Check API rate usage
grep "rate" logs/improved_trading.log
```

### Dashboard Metrics
Open http://localhost:8080 and check:
- **Active Symbols:** Should match your configuration
- **WebSocket Status:** Should be green
- **API Usage:** Should be below 1,000 requests/min
- **Error Rate:** Should be near 0%

---

## Troubleshooting

### Too Many Symbols Causing Issues?

**Symptoms:**
- High CPU usage (>60%)
- High memory usage (>4GB)
- Slow response times
- WebSocket disconnections
- API rate limit warnings

**Solutions:**

1. **Reduce symbol count:**
```bash
python3 ULTIMATE_LAUNCHER.py --symbols 30 --auto
```

2. **Check system resources:**
```bash
free -h  # Check memory
top      # Check CPU
```

3. **Increase system limits (Linux):**
```bash
# Increase file descriptor limit
ulimit -n 4096

# Check current limit
ulimit -n
```

4. **Optimize configuration:**
Edit `config/system_config.yaml`:
```yaml
websocket_connections:
  max_per_symbol: 3  # Reduce from 5
  
api_rate_limiting:
  enabled: true
  requests_per_minute: 1000  # Stay well below limit
```

---

## Best Practices

### Starting Out
1. **Start small:** Begin with 20-30 symbols
2. **Monitor:** Watch system performance for 24 hours
3. **Scale up:** Gradually increase if stable
4. **Test:** Use `--test` flag before going live

### Production Use
1. **Stable symbols:** Focus on high-liquidity pairs
2. **Monitor resources:** Set up alerts for high usage
3. **Backup plan:** Have fallback configuration ready
4. **Regular checks:** Review performance weekly

### Optimization
1. **Remove low-volume pairs:** Focus on liquid markets
2. **Adjust categories:** Use categories that match your strategy
3. **Time-based:** Different symbols for different times
4. **A/B testing:** Compare performance with different counts

---

## Quick Reference

```bash
# Show help
python3 ULTIMATE_LAUNCHER.py --help

# Default (30 symbols)
python3 ULTIMATE_LAUNCHER.py --auto

# 50 symbols
python3 ULTIMATE_LAUNCHER.py --symbols 50 --auto

# 80 symbols  
python3 ULTIMATE_LAUNCHER.py --symbols 80 --auto

# Test mode
python3 ULTIMATE_LAUNCHER.py --symbols 50 --test

# Dashboard only
python3 ULTIMATE_LAUNCHER.py --symbols 50 --dashboard-only
```

---

## Summary

**To increase symbols:**

1. **Easiest:** `python3 ULTIMATE_LAUNCHER.py --symbols 50 --auto`
2. **Config:** Edit `config/trading_pairs.yaml`
3. **Categories:** Combine multiple categories

**Recommended:**
- **Beginners:** 20-30 symbols
- **Most users:** 30-50 symbols ⭐
- **Advanced:** 50-80 symbols
- **Professional:** 80-100+ symbols

**Always:**
- ✅ Monitor system resources
- ✅ Check API rate usage
- ✅ Start small, scale gradually
- ✅ Test before going live

---

**Need help?** See `README.md` or `IMPLEMENTATION_COMPLETE.md`
