# Level 2 System - Configuration Examples

Different configurations for different trading styles and needs.

---

## Table of Contents
1. [Basic Configurations](#basic-configurations)
2. [Trading Style Configurations](#trading-style-configurations)
3. [Hardware Optimization](#hardware-optimization)
4. [Market Type Configurations](#market-type-configurations)
5. [Advanced Settings](#advanced-settings)

---

## Basic Configurations

### Default Configuration (Recommended for Beginners)

```python
system = UnifiedLevel2System(
    symbol='AAPL',                  # Liquid stock
    use_extended_hours=False,       # Regular hours only
    detect_hidden_orders=True,      # Enable detection
    port=7497,                      # Paper trading
    host='127.0.0.1',              # Localhost
    clientId=1,                     # Unique ID
)
```

**Best for:**
- Learning the system
- Paper trading
- Regular market hours only
- Standard stocks

---

### Extended Hours Configuration

```python
system = UnifiedLevel2System(
    symbol='TSLA',
    use_extended_hours=True,        # Premarket + Afterhours
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)
```

**Best for:**
- Premarket trading (4:00 AM - 9:30 AM)
- Afterhours trading (4:00 PM - 8:00 PM)
- News/earnings traders
- International market overlap

**Note:** Spreads wider, less liquidity outside regular hours.

---

### Live Trading Configuration

```python
system = UnifiedLevel2System(
    symbol='SPY',
    use_extended_hours=False,
    detect_hidden_orders=True,
    port=7496,                      # LIVE TRADING PORT ⚠️
    host='127.0.0.1',
    clientId=1,
)
```

**⚠️ WARNING:** This connects to LIVE trading account!

**Before using:**
1. Test EXTENSIVELY in paper first
2. Verify risk limits are set
3. Start with small positions
4. Have stop losses ready

---

## Trading Style Configurations

### Day Trader Configuration

```python
# Fast execution, high volume stocks
system = UnifiedLevel2System(
    symbol='SPY',                   # High liquidity
    use_extended_hours=False,       # Regular hours only
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Hidden order detector settings
detector = HiddenOrderDetector(
    lookback_seconds=30,            # Short lookback
    sensitivity='high'              # Catch quick moves
)
```

**Dashboard settings:**
```python
# In unified_dashboard.py, change interval:
dcc.Interval(
    interval=500,                   # Update every 0.5 seconds
    n_intervals=0
)
```

**Best for:**
- Quick scalps (seconds to minutes)
- High frequency signals
- Momentum plays

---

### Swing Trader Configuration

```python
# Longer timeframe, less frequent updates
system = UnifiedLevel2System(
    symbol='AAPL',
    use_extended_hours=False,
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Hidden order detector
detector = HiddenOrderDetector(
    lookback_seconds=120,           # Longer lookback
    sensitivity='low'               # Only major moves
)
```

**Dashboard settings:**
```python
dcc.Interval(
    interval=5000,                  # Update every 5 seconds
    n_intervals=0
)
```

**Best for:**
- Entries for multi-day holds
- Major support/resistance
- Institutional activity

---

### Scalper Configuration

```python
# Maximum speed, minimum delay
system = UnifiedLevel2System(
    symbol='TSLA',                  # Volatile stock
    use_extended_hours=False,
    detect_hidden_orders=False,     # Skip for speed
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Market depth request
# In level2_unified_system.py:
self.ib.reqMktDepth(
    contract,
    numRows=5,                      # Only top 5 levels (faster)
    isSmartDepth=True
)
```

**Dashboard:**
```python
dcc.Interval(
    interval=250,                   # 4x per second
    n_intervals=0
)

# Reduce chart history
data_store = {
    'timestamps': deque(maxlen=50),  # Less history
    'prices': deque(maxlen=50),
    # ... etc
}
```

**Best for:**
- Ultra-fast entries/exits
- Tick-by-tick trading
- Powerful computers only

---

### Options Flow Trader

```python
# Watching for unusual activity
system = UnifiedLevel2System(
    symbol='SPY',                   # Underlying
    use_extended_hours=True,        # Catch pre/post moves
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

detector = HiddenOrderDetector(
    lookback_seconds=60,
    sensitivity='high'              # Catch hedging activity
)
```

**Best for:**
- Spotting option hedge activity
- Unusual order flow
- Pin risk detection
- Expiration day trading

---

## Hardware Optimization

### Low-End PC Configuration

**System:** Old laptop, <4GB RAM

```python
system = UnifiedLevel2System(
    symbol='AAPL',
    use_extended_hours=False,
    detect_hidden_orders=False,     # Disable for speed
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Reduced depth
numRows=5                           # Only 5 levels

# In dashboard
data_store = {
    'timestamps': deque(maxlen=50), # Small history
    'prices': deque(maxlen=50),
    # ...
}

dcc.Interval(
    interval=2000,                  # Slow updates (2 sec)
    n_intervals=0
)
```

**Disable heavy features:**
```python
# Comment out in dashboard layout:
# - Heatmap
# - Multiple charts
# Keep only order book and signal
```

---

### High-End PC Configuration

**System:** Gaming PC, 16GB+ RAM, Fast CPU

```python
system = UnifiedLevel2System(
    symbol='TSLA',
    use_extended_hours=True,
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Maximum depth
numRows=20                          # All 20 levels

detector = HiddenOrderDetector(
    lookback_seconds=120,
    sensitivity='high'
)

# In dashboard
data_store = {
    'timestamps': deque(maxlen=500), # Large history
    'prices': deque(maxlen=500),
    # ...
}

dcc.Interval(
    interval=250,                   # Fast updates
    n_intervals=0
)
```

**Enable all features:**
- Full heatmap
- All charts
- Hidden order detection
- Support/resistance
- Everything!

---

## Market Type Configurations

### High Liquidity Stocks (SPY, AAPL, MSFT)

```python
system = UnifiedLevel2System(
    symbol='SPY',
    use_extended_hours=False,
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Full depth available
numRows=20

# High sensitivity (lots of data)
detector = HiddenOrderDetector(
    lookback_seconds=60,
    sensitivity='medium'
)
```

**Characteristics:**
- Tight spreads (<5 bps)
- 20 full price levels
- Constant updates
- Clear signals

---

### Medium Liquidity Stocks (Mid-caps)

```python
system = UnifiedLevel2System(
    symbol='DKNG',                  # Example mid-cap
    use_extended_hours=False,
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Moderate depth
numRows=15

# Lower sensitivity (less data)
detector = HiddenOrderDetector(
    lookback_seconds=90,
    sensitivity='low'
)
```

**Characteristics:**
- Moderate spreads (5-20 bps)
- 10-15 price levels
- Less frequent updates
- Noisier signals

---

### Low Liquidity / Small Caps

```python
system = UnifiedLevel2System(
    symbol='CLOV',                  # Example small-cap
    use_extended_hours=False,
    detect_hidden_orders=False,     # Not reliable on low volume
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Limited depth anyway
numRows=10

# Skip hidden detection (not enough data)
detect_hidden_orders=False
```

**Warning:** 
- Wide spreads (>50 bps common)
- Only 5-7 levels may show
- Signals less reliable
- Use with caution

**Better approach:** Stick to high liquidity stocks!

---

## Advanced Settings

### Multiple Symbol Monitoring

```python
# Create multiple instances
symbols = ['AAPL', 'TSLA', 'SPY', 'QQQ']

systems = []
for i, symbol in enumerate(symbols):
    system = UnifiedLevel2System(
        symbol=symbol,
        use_extended_hours=False,
        detect_hidden_orders=True,
        port=7497,
        host='127.0.0.1',
        clientId=i+1,               # Unique ID for each!
    )
    systems.append(system)
```

**Note:** Each needs unique clientId!

**Resource usage:** Heavy - max 4-5 stocks simultaneously

---

### Remote Access Configuration

**Warning:** Only do this if you understand security implications!

```python
# On server/remote machine
system = UnifiedLevel2System(
    symbol='AAPL',
    use_extended_hours=True,
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',              # TWS on same machine
    clientId=1,
)

# In unified_dashboard.py
app.run_server(
    host='0.0.0.0',                # Accept external connections
    port=8050,
    debug=False
)
```

**Access from other computer:**
```
http://<server-ip>:8050
```

**Security:**
- Use VPN or SSH tunnel
- Don't expose to internet directly
- Change default port
- Use authentication if possible

---

### Custom Signal Thresholds

Edit in `level2_unified_system.py`, in SignalGenerator class:

```python
# Default thresholds
self.thresholds = {
    'strong_imbalance': 0.3,        # Change to 0.4 for less signals
    'moderate_imbalance': 0.15,     # Change to 0.2
    'spread_threshold_bps': 10,     # Ignore if spread >10 bps
    'min_confidence': 40            # Minimum confidence to show
}

# For conservative signals:
self.thresholds = {
    'strong_imbalance': 0.5,        # Much higher threshold
    'moderate_imbalance': 0.3,
    'spread_threshold_bps': 5,      # Only tight spreads
    'min_confidence': 60            # Higher confidence required
}

# For aggressive signals:
self.thresholds = {
    'strong_imbalance': 0.2,        # Lower threshold
    'moderate_imbalance': 0.1,
    'spread_threshold_bps': 20,     # Allow wider spreads
    'min_confidence': 30            # Show more signals
}
```

---

### Exchange-Specific Configuration

```python
# Force specific exchange
from ib_insync import Stock

contract = Stock(
    symbol='AAPL',
    exchange='ISLAND',              # NASDAQ Island
    currency='USD'
)

# Or try different exchanges
exchanges = ['ISLAND', 'ARCA', 'EDGEA', 'IEX']
for exchange in exchanges:
    contract = Stock(symbol='AAPL', exchange=exchange, currency='USD')
    # Subscribe to each
```

**Use when:**
- SMART routing not working
- Want specific exchange data
- Testing different liquidity pools

---

## Configuration Templates

### Template 1: Safe Beginner

```python
# Copy this for starting out
system = UnifiedLevel2System(
    symbol='SPY',                   # Most liquid
    use_extended_hours=False,       # Regular only
    detect_hidden_orders=True,      # Learn patterns
    port=7497,                      # Paper trading
    host='127.0.0.1',
    clientId=1,
)

# Dashboard: slow updates
interval=2000  # 2 seconds

# Hidden: moderate sensitivity
sensitivity='medium'
```

---

### Template 2: Active Day Trader

```python
system = UnifiedLevel2System(
    symbol='TSLA',
    use_extended_hours=False,
    detect_hidden_orders=True,
    port=7497,                      # Or 7496 when ready
    host='127.0.0.1',
    clientId=1,
)

# Dashboard: fast updates
interval=500  # 0.5 seconds

# Hidden: high sensitivity
sensitivity='high'
lookback_seconds=30
```

---

### Template 3: News Trader

```python
system = UnifiedLevel2System(
    symbol='AAPL',
    use_extended_hours=True,        # Catch pre/post news
    detect_hidden_orders=True,
    port=7497,
    host='127.0.0.1',
    clientId=1,
)

# Dashboard: moderate updates
interval=1000  # 1 second

# Hidden: high sensitivity for accumulation
sensitivity='high'
lookback_seconds=60
```

---

## Testing Your Configuration

After changing settings, test with:

```python
# Run for 2 minutes
system.start(duration_seconds=120)

# Watch for:
# - Connection successful?
# - Data flowing?
# - Signals appearing?
# - Performance acceptable?
```

**Adjust based on:**
- Too many signals → Increase thresholds
- Too few signals → Decrease thresholds
- Too slow → Reduce update frequency
- Too fast/laggy → Increase update interval

---

## Best Practices

1. **Start conservative** - Use default settings first
2. **One change at a time** - Don't modify everything at once
3. **Track results** - Note win rate with each configuration
4. **Match your style** - Scalper ≠ Swing Trader settings
5. **Consider hardware** - Don't overload slow PC
6. **Use paper trading** - Test all configs in paper first

---

## Configuration Checklist

Before going live with a new configuration:

- [ ] Tested in paper trading for 1+ weeks
- [ ] Verified signals make sense
- [ ] Performance is acceptable
- [ ] No errors or crashes
- [ ] Understood all changes made
- [ ] Documented what was changed
- [ ] Have exit plan if signals wrong

---

**Remember:** The default configuration works well for most use cases. 
Only customize if you have a specific need!
