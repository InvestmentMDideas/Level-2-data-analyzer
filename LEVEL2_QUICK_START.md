# Level 2 System - Quick Start

**Get up and running in 10 minutes**

---

## Prerequisites Checklist

Before starting, make sure you have:

- [ ] Interactive Brokers account (paper or live)
- [ ] Level 2 market data subscription (~$10/month)
- [ ] TWS or IB Gateway installed
- [ ] Python 3.8 or higher

---

## 5-Step Setup

### Step 1: Subscribe to Level 2 Data (2 min)

1. Go to https://www.interactivebrokers.com
2. Login → Settings → Market Data Subscriptions
3. Add: "US Securities Snapshot and Futures Value Bundle"
4. Wait 24 hours for activation

### Step 2: Configure TWS/Gateway (2 min)

1. Launch TWS or IB Gateway
2. Go to: File → Global Configuration → API → Settings
3. Enable these:
   - ✅ Enable ActiveX and Socket Clients
   - ✅ Allow connections from localhost
4. Note the port:
   - **7497** for paper trading ⭐ (recommended)
   - **7496** for live trading
5. Click OK and restart

### Step 3: Install Python Packages (2 min)

```bash
pip install ib_insync pandas numpy pytz dash plotly
```

### Step 4: Test Connection (1 min)

```python
# Save as test.py
from ib_insync import IB

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
print("✅ Connected!")
ib.disconnect()
```

Run it:
```bash
python test.py
```

### Step 5: Launch Dashboard (3 min)

**Windows:**
```bash
# Double-click RUN_DASHBOARD.bat
# OR run manually:
python unified_dashboard.py AAPL
```

**Mac/Linux:**
```bash
python unified_dashboard.py AAPL
```

**Open browser:**
```
http://127.0.0.1:8050
```

---

## What You'll See

### Dashboard Components

1. **Order Book** (left) - Live bids and asks
2. **Trading Signal** (right) - BUY/SELL/NEUTRAL with confidence
3. **Hidden Orders** - Alert box showing big player activity
4. **Heatmap** - Visual liquidity map
5. **Charts** - Price, spread, and imbalance over time

### Reading Signals

```
🟢 BUY (75% confidence)
   • Strong queue imbalance
   • Hidden buyer detected
   • Volume surge
```

**What this means:**
- System sees buying pressure
- 75% confidence = fairly reliable
- Multiple confirming factors

**What to do:**
1. Check if aligns with your analysis
2. Look at higher timeframe trend
3. Enter only if it fits your strategy
4. Use proper stop loss

---

## Common Issues

### "Connection refused"
**Fix:** Make sure TWS/Gateway is running and API is enabled

### "No market data"
**Fix:** Wait 24 hours after subscribing to Level 2 data

### "Dashboard won't open"
**Fix:** 
1. Look for "Running on http://127.0.0.1:8050" in terminal
2. Copy/paste that URL into browser
3. Try different browser if needed

### Only see a few levels
**Fix:** This is normal for low-volume stocks or extended hours

---

## Best Practices

✅ **DO:**
- Start with paper trading (port 7497)
- Use liquid stocks (AAPL, TSLA, SPY, QQQ)
- Trade during regular hours (9:30 AM - 4:00 PM ET)
- Wait for 60%+ confidence signals
- Use stop losses always

❌ **DON'T:**
- Blindly follow signals without confirmation
- Trade in extended hours initially
- Use illiquid stocks (<1M daily volume)
- Overtrade on low confidence signals
- Risk more than you can afford to lose

---

## Quick Command Reference

**Start dashboard:**
```bash
python unified_dashboard.py AAPL
```

**Stop dashboard:**
```bash
Ctrl+C
```

**Change symbol:**
```bash
python unified_dashboard.py TSLA
```

**Run without dashboard (console only):**
```bash
python level2_unified_system.py AAPL
```

---

## Understanding Confidence Levels

| Confidence | Meaning | Action |
|-----------|---------|--------|
| 80%+ | Very Strong | High probability - consider entry |
| 60-79% | Strong | Good signal - verify with analysis |
| 40-59% | Moderate | Weak - wait for confirmation |
| <40% | Weak | Ignore - market unclear |

---

## Costs

**One-time:**
- $0 (all software is free)

**Monthly:**
- Level 2 Data: ~$10-15/month
- Trading commissions: Varies by activity

**Total to get started:** ~$10-15/month

---

## Next Steps

1. **Week 1:** Just observe - don't trade
2. **Week 2:** Paper trade 1-share positions
3. **Week 3:** Track win rate and adjust parameters
4. **Week 4:** If profitable, consider going live with small size

---

## Support Resources

📖 **Full Guide:** See LEVEL2_SETUP_GUIDE.md  
🔧 **Troubleshooting:** See the detailed guide  
📚 **IBKR API:** https://interactivebrokers.github.io/tws-api/  
💬 **ib_insync:** https://ib-insync.readthedocs.io/  

---

## Safety Reminder

⚠️ This is educational software. Not financial advice.  
⚠️ Always use stop losses and proper risk management.  
⚠️ Only trade with money you can afford to lose.  
⚠️ Past performance doesn't guarantee future results.

**Start small. Learn first. Trade later.**

---

**Ready to start?** Launch TWS and run the dashboard! 🚀
