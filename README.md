# Level 2 Order Book System 📊

**Real-time market depth visualization and trading signal generation for Interactive Brokers**

---

## What is This?

A comprehensive Level 2 order book analysis system that:

- 📈 Visualizes real-time bid/ask depth from IBKR
- 🎯 Generates BUY/SELL/NEUTRAL trading signals
- 🔍 Detects hidden buyers, sellers, and iceberg orders
- 🗺️ Shows liquidity heatmaps and support/resistance
- ⏰ Works during premarket, regular hours, and afterhours
- 🌐 Web-based dashboard accessible from any browser

**Perfect for:** Day traders, scalpers, swing traders analyzing order flow and institutional activity.

---

## Quick Start

### 1. Prerequisites

- ✅ Interactive Brokers account (paper or live)
- ✅ Level 2 market data subscription (~$10/month)
- ✅ Python 3.8+
- ✅ TWS or IB Gateway

### 2. Install

```bash
pip install ib_insync pandas numpy pytz dash plotly
```

### 3. Configure IBKR

1. Launch TWS/Gateway
2. Enable API: File → Global Configuration → API → Settings
3. Check "Enable ActiveX and Socket Clients"
4. Note port: 7497 (paper) or 7496 (live)

### 4. Run

```bash
python unified_dashboard.py AAPL
```

### 5. View

Open browser to: `http://127.0.0.1:8050`

**That's it!** 🚀

---

## Documentation

### For New Users

1. **[Quick Start Guide](LEVEL2_QUICK_START.md)** - Get running in 10 minutes
2. **[Full Setup Guide](LEVEL2_SETUP_GUIDE.md)** - Complete walkthrough
3. **[Troubleshooting](LEVEL2_TROUBLESHOOTING.md)** - Fix common issues

### For Advanced Users

4. **[Configuration Examples](LEVEL2_CONFIG_EXAMPLES.md)** - Customize for your style
5. **System Files:**
   - `level2_unified_system.py` - Core engine
   - `unified_dashboard.py` - Web interface
   - `RUN_DASHBOARD.bat` - Windows launcher

---

## Features

### Core Features

✅ **Real-time Order Book**
- Live bid/ask depth (up to 20 levels)
- Aggregated across exchanges
- Best bid/ask highlighting
- Volume at each price level

✅ **Trading Signals**
- BUY/SELL/NEUTRAL with confidence scores
- Multiple factor analysis
- Queue imbalance calculation
- Microprice-based signals

✅ **Hidden Order Detection**
- Hidden buyers (absorbing sells)
- Hidden sellers (absorbing buys)
- Iceberg order identification
- Accumulation/distribution alerts

✅ **Visual Analytics**
- Liquidity heatmap
- Support/resistance levels
- Price movement charts
- Spread and imbalance tracking
- Volume pressure gauges

✅ **Extended Hours Support**
- Premarket (4:00 AM - 9:30 AM ET)
- Regular hours (9:30 AM - 4:00 PM ET)
- Afterhours (4:00 PM - 8:00 PM ET)
- Session indicator and warnings

### Dashboard Components

1. **Order Book** - Visual bid/ask depth
2. **Signal Panel** - Current trading recommendation
3. **Hidden Orders** - Alert box for unusual activity
4. **Heatmap** - Liquidity visualization
5. **Charts** - Price, spread, imbalance over time
6. **Stats** - Spread (bps), microprice, session info

---

## System Requirements

### Minimum

- Python 3.8+
- 2GB RAM
- IBKR account with Level 2 data
- Internet connection (5+ Mbps)

### Recommended

- Python 3.10+
- 4GB+ RAM
- Dual monitors
- Fast internet (10+ Mbps)
- Liquid stocks (SPY, AAPL, TSLA, QQQ)

### Costs

- **Software:** Free
- **IBKR Account:** Free (with minimum balance)
- **Level 2 Data:** ~$10-15/month
- **Total:** ~$10-15/month

---

## How It Works

### Signal Generation

The system analyzes multiple factors:

1. **Queue Position Imbalance**
   - Weighted bid vs ask volume
   - Distance-adjusted pressure
   - Top-level size comparison

2. **Hidden Order Detection**
   - Volume vs price movement divergence
   - Order book refresh patterns
   - Absorption analysis

3. **Spread Analysis**
   - Tight spread = confidence
   - Wide spread = uncertainty
   - BPS calculation for standardization

4. **Confluence Scoring**
   - Multiple factors agreeing = higher confidence
   - Contradicting factors = lower confidence

### Confidence Levels

| Score | Meaning | Reliability |
|-------|---------|-------------|
| 80%+ | Very Strong | High - consider entry |
| 60-79% | Strong | Good - verify with analysis |
| 40-59% | Moderate | Weak - wait for confirmation |
| <40% | Weak | Low - likely ignore |

---

## Understanding Signals

### BUY Signal 🟢

```
🟢 BUY (75% confidence)
Reasons:
• Strong queue imbalance: +0.45
• Hidden buyer detected at $150.25
• Volume surge at best bid
• Tight spread (5 bps)
```

**What this means:**
- More buyers than sellers in queue
- Large player absorbing sells
- Bullish pressure building

**What to do:**
1. Verify with your strategy
2. Check higher timeframe trend
3. Look for confirmation (volume, momentum)
4. Enter with stop loss if appropriate

### SELL Signal 🔴

```
🔴 SELL (68% confidence)
Reasons:
• Heavy selling pressure
• Queue imbalance: -0.52
• Breaking support level
• Hidden seller at $150.30
```

**What this means:**
- More sellers than buyers in queue
- Large player distributing
- Bearish pressure building

**What to do:**
1. Consider exiting longs
2. Wait for better entry if planning to buy
3. Or short if that fits your strategy

### NEUTRAL Signal ⚪

```
⚪ NEUTRAL (35% confidence)
Reasons:
• Balanced order book
• Low volume
• No clear direction
```

**What this means:**
- Market is balanced
- Wait for clearer setup

**What to do:**
- Don't force trades
- Wait for BUY or SELL signal

---

## Hidden Order Detection

### Hidden Buyers

**Pattern:** Heavy selling, but price stable or rising

**Interpretation:** 
- Large buyer absorbing all sells
- Not showing full size on order book
- Accumulation happening

**Trading Action:**
- Bullish signal
- Good time to buy
- Big player building position

### Hidden Sellers

**Pattern:** Heavy buying, but price stable or falling

**Interpretation:**
- Large seller absorbing all buys
- Distribution happening
- Supply overwhelming demand

**Trading Action:**
- Bearish signal
- Avoid buying
- Consider selling

### Iceberg Orders

**Pattern:** Order at price level keeps refreshing

**Example:**
```
10:30:00 → 500 shares at $150.00
10:30:05 → Filled
10:30:06 → 500 shares at $150.00 (refreshed!)
10:30:11 → Filled
10:30:12 → 500 shares at $150.00 (refreshed again!)
```

**Interpretation:**
- Large order hiding true size
- Shows only small piece at a time
- Strong support (if bid) or resistance (if ask)

**Trading Action:**
- Hard to move through that price
- If bid iceberg = support level
- If ask iceberg = resistance level

---

## Best Practices

### ✅ DO

1. **Start with paper trading** (port 7497)
2. **Use liquid stocks** (SPY, AAPL, TSLA, QQQ, MSFT)
3. **Trade regular hours** initially (9:30 AM - 4:00 PM ET)
4. **Wait for 60%+ confidence** signals
5. **Verify with other analysis** (charts, indicators, news)
6. **Always use stop losses**
7. **Track your results** over time
8. **Start small** and scale gradually

### ❌ DON'T

1. **Don't blindly follow signals** - verify first
2. **Don't trade illiquid stocks** (<1M daily volume)
3. **Don't overtrade** on low confidence signals
4. **Don't ignore spreads** - wide spreads = risky
5. **Don't fight the trend** - check higher timeframe
6. **Don't use without stops** - always protect capital
7. **Don't expect perfection** - no system is 100%

---

## Common Use Cases

### Day Trading
- Fast entries/exits based on order flow
- Scalp spreads and imbalances
- Catch momentum shifts early

### Swing Trading
- Find optimal entry points
- Identify accumulation/distribution
- Confirm support/resistance levels

### Options Trading
- Spot hedging activity in underlying
- Detect pin risk near strikes
- Time entries around order flow

### Market Making
- Monitor spread dynamics
- Track queue position
- Identify liquidity gaps

---

## Troubleshooting

### Quick Fixes

**Can't connect?**
→ Start TWS/Gateway, enable API, check port

**No data?**
→ Subscribe to Level 2, wait 24hrs activation

**Dashboard won't open?**
→ Check terminal for URL, copy to browser

**Only see 2-3 levels?**
→ Normal for low liquidity or extended hours

**Signals seem wrong?**
→ Remember: suggestions not facts. Always verify.

**See [Troubleshooting Guide](LEVEL2_TROUBLESHOOTING.md) for detailed solutions**

---

## File Structure

```
level2_system/
├── level2_unified_system.py      # Core engine
├── unified_dashboard.py          # Web dashboard
├── RUN_DASHBOARD.bat            # Windows launcher
│
├── LEVEL2_SETUP_GUIDE.md        # Full setup guide
├── LEVEL2_QUICK_START.md        # 10-minute quickstart
├── LEVEL2_TROUBLESHOOTING.md    # Problem solutions
├── LEVEL2_CONFIG_EXAMPLES.md    # Configuration examples
└── README.md                     # This file
```

---

## Examples

### Running Different Symbols

```bash
# SPY (very liquid, tight spreads)
python unified_dashboard.py SPY

# TSLA (volatile, good for signals)
python unified_dashboard.py TSLA

# QQQ (tech ETF, consistent)
python unified_dashboard.py QQQ

# Custom symbol
python unified_dashboard.py YOUR_SYMBOL
```

### Different Trading Sessions

```python
# Regular hours only (default)
system = UnifiedLevel2System(
    symbol='AAPL',
    use_extended_hours=False
)

# Include premarket/afterhours
system = UnifiedLevel2System(
    symbol='AAPL',
    use_extended_hours=True
)
```

### Live vs Paper Trading

```python
# Paper trading (safe for testing)
port=7497

# Live trading (use with caution!)
port=7496
```

---

## Technical Details

### Data Flow

```
IBKR TWS/Gateway
      ↓
  Level 2 API
      ↓
level2_unified_system.py
      ↓
Signal Generation & Detection
      ↓
unified_dashboard.py
      ↓
Web Browser Dashboard
```

### Update Frequency

- **Market Data:** Real-time (milliseconds)
- **Dashboard:** Configurable (default 1 second)
- **Signals:** Generated on every update
- **Hidden Orders:** Analyzed every update

### Data Retention

- **Order Book:** Current state only
- **Price History:** 200 points (configurable)
- **Signals:** 200 historical (configurable)
- **Imbalances:** 200 points (configurable)

---

## Customization

### Change Update Speed

In `unified_dashboard.py`:
```python
dcc.Interval(
    interval=1000,  # Change to 500 for faster, 2000 for slower
    n_intervals=0
)
```

### Change Hidden Order Sensitivity

In `level2_unified_system.py`:
```python
detector = HiddenOrderDetector(
    lookback_seconds=60,    # How far back to look
    sensitivity='medium'    # low, medium, or high
)
```

### Change Price Levels Shown

In `level2_unified_system.py`:
```python
self.ib.reqMktDepth(
    contract,
    numRows=20,     # Max 20, try 10 for faster updates
    isSmartDepth=True
)
```

**See [Configuration Examples](LEVEL2_CONFIG_EXAMPLES.md) for more**

---

## Safety & Disclaimers

### ⚠️ Important Warnings

1. **Educational Software**
   - This is for learning and analysis
   - Not financial advice
   - Not guaranteed to be profitable

2. **Market Risks**
   - Trading involves substantial risk
   - You can lose more than you invest
   - Past performance ≠ future results

3. **System Limitations**
   - Signals are suggestions, not facts
   - Hidden orders can disappear instantly
   - Large players can spoof the book
   - No system is 100% accurate

4. **Your Responsibility**
   - Test thoroughly in paper first
   - Understand what you're trading
   - Use proper risk management
   - Never risk more than you can afford to lose
   - Comply with all regulations (PDT rules, etc.)

### Recommended Approach

1. **Month 1:** Paper trade only - learn the system
2. **Month 2:** Paper trade - develop strategy
3. **Month 3:** Paper trade - verify consistency
4. **Month 4:** If profitable, start live with 1-share positions
5. **Month 5+:** Gradually increase size based on results

---

## Support

### Documentation

- 📖 **Quick Start:** Fast setup in 10 minutes
- 📚 **Full Guide:** Complete walkthrough
- 🔧 **Troubleshooting:** Fix common problems
- ⚙️ **Configuration:** Customize for your needs

### Resources

- **IBKR API:** https://interactivebrokers.github.io/tws-api/
- **ib_insync:** https://ib-insync.readthedocs.io/
- **Dash:** https://dash.plotly.com/

### Getting Help

1. Check [Troubleshooting Guide](LEVEL2_TROUBLESHOOTING.md)
2. Enable debug logging (see guide)
3. Check TWS logs for errors
4. Verify Level 2 subscription is active
5. Contact IBKR support for account issues

---

## Contributing

Found a bug? Have a suggestion? Want to improve the docs?

Feel free to:
- Report issues you encounter
- Suggest feature improvements
- Share configuration optimizations
- Contribute code enhancements

---

## License

This software is provided as-is for educational purposes.

**No warranty of any kind.** Use at your own risk.

Not affiliated with Interactive Brokers or any financial institution.

---

## Version History

**Current Version:** 1.0

**Features:**
- ✅ Real-time Level 2 data
- ✅ Signal generation
- ✅ Hidden order detection
- ✅ Web dashboard
- ✅ Extended hours support
- ✅ Support/resistance detection
- ✅ Comprehensive documentation

---

## Acknowledgments

Built with:
- **ib_insync** - IBKR API wrapper
- **Dash/Plotly** - Web dashboard
- **Python** - Core language

Thanks to the open-source community!

---

## Final Notes

**Remember:**
- 🎯 Signals are tools, not guarantees
- 📊 Always verify with your own analysis
- 💰 Use proper risk management
- 📈 Start small and scale gradually
- 🧠 Keep learning and improving
- ⚠️ Never risk more than you can afford to lose

**Trade safe. Trade smart. Good luck! 🚀**

---

*For detailed setup instructions, see [LEVEL2_SETUP_GUIDE.md](LEVEL2_SETUP_GUIDE.md)*

*For quick start, see [LEVEL2_QUICK_START.md](LEVEL2_QUICK_START.md)*
