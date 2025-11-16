# Level 2 Order Book System - Complete Setup Guide

**Real-time IBKR Level 2 Market Data with Hidden Order Detection**

---

## Table of Contents
1. [What is This System?](#what-is-this-system)
2. [Prerequisites](#prerequisites)
3. [IBKR Account Setup](#ibkr-account-setup)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the System](#running-the-system)
7. [Understanding the Dashboard](#understanding-the-dashboard)
8. [Troubleshooting](#troubleshooting)

---

## What is This System?

This is a **real-time Level 2 order book visualization and analysis system** for Interactive Brokers.

### Features

✅ **Order Book Visualization** - See live bids/asks  
✅ **Hidden Order Detection** - Identify hidden buyers/sellers and iceberg orders  
✅ **Trading Signals** - BUY/SELL/NEUTRAL with confidence scores  
✅ **Liquidity Heatmap** - Visualize where the big orders are  
✅ **Support/Resistance** - Automatically detect key price levels  
✅ **Extended Hours** - Works in premarket and afterhours  
✅ **Price Imbalance** - Queue position analysis  
✅ **Microprice Calculation** - More accurate than mid-price  

### What You'll See

- **Live order book** with all bid/ask levels
- **Real-time signals** telling you when to buy/sell
- **Hidden order alerts** when big players are absorbing orders
- **Price pressure gauges** showing buying vs selling pressure
- **Interactive charts** tracking spread, imbalance, and price movement

---

## Prerequisites

### Required Accounts & Subscriptions

#### 1. Interactive Brokers Account
- **Account Type:** Live or Paper Trading
- **Required Subscription:** Level 2 Market Data
  - US Securities Snapshot and Futures Value Bundle: ~$10/month
  - Or NASDAQ Level II: ~$14.50/month
  - Or NYSE OpenBook: ~$14.50/month

⚠️ **IMPORTANT:** You MUST have Level 2 data subscription to use this system!

**How to Subscribe:**
1. Log into Account Management (https://www.interactivebrokers.com)
2. Go to: Settings → User Settings → Market Data Subscriptions
3. Add: "US Securities Snapshot and Futures Value Bundle"
4. Wait 24 hours for activation

#### 2. Software Requirements

**Required:**
- Python 3.8 or higher
- Interactive Brokers TWS (Trader Workstation) or IB Gateway
- Windows, macOS, or Linux

**Recommended:**
- At least 4GB RAM
- Stable internet connection
- Dual monitors (one for dashboard, one for TWS)

---

## IBKR Account Setup

### Step 1: Download TWS or IB Gateway

**TWS (Full Platform):**
- Download: https://www.interactivebrokers.com/en/trading/tws.php
- Pros: Full trading platform
- Cons: More resource intensive

**IB Gateway (Headless):**
- Download: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
- Pros: Lightweight, API-focused
- Cons: No trading GUI

💡 **Recommendation:** Use IB Gateway if you only need the API

### Step 2: Enable API Access

1. **Launch TWS or IB Gateway**
2. **Log in** with your credentials
3. **Navigate to API Settings:**
   - TWS: File → Global Configuration → API → Settings
   - Gateway: Configure → Settings → API → Settings
4. **Enable the following:**
   - ✅ "Enable ActiveX and Socket Clients"
   - ✅ "Allow connections from localhost only" (uncheck if using remote)
   - ✅ "Read-Only API" (safer for testing)
5. **Note the Socket Port:**
   - **7497** = Paper Trading (recommended for testing)
   - **7496** = Live Trading
6. **Add Trusted IPs:**
   - Add `127.0.0.1` to trusted IP addresses
7. **Click OK and restart TWS/Gateway**

### Step 3: Verify Market Data

1. In TWS, check: Account → Account Settings
2. Verify "Market Data Subscriptions" shows Level 2 as active
3. Test by viewing a stock's order book in TWS:
   - Right-click a stock → BookTrader
   - You should see multiple bid/ask levels

---

## Installation

### Step 1: Install Python Packages

Open terminal/command prompt and run:

```bash
# Core dependencies
pip install ib_insync pandas numpy pytz

# Dashboard dependencies
pip install dash plotly
```

**Verify installation:**
```bash
python -c "import ib_insync; print('ib_insync version:', ib_insync.__version__)"
```

### Step 2: Download System Files

Place these files in the same directory:

```
your_project_folder/
├── level2_unified_system.py    # Core Level 2 engine
├── unified_dashboard.py        # Web dashboard
└── RUN_DASHBOARD.bat          # Windows launcher (optional)
```

### Step 3: Test Connection

Create a test file `test_connection.py`:

```python
"""
Test IBKR connection
"""
from ib_insync import IB

# Connect to IBKR
ib = IB()

try:
    # Connect (paper trading port 7497)
    ib.connect('127.0.0.1', 7497, clientId=1)
    print("✅ Connected to IBKR!")
    print(f"   Account: {ib.managedAccounts()}")
    ib.disconnect()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Is TWS/Gateway running?")
    print("2. Is API enabled in settings?")
    print("3. Is port 7497 correct?")
```

Run it:
```bash
python test_connection.py
```

If you see "✅ Connected to IBKR!", you're ready!

---

## Configuration

### Basic Configuration

The system works out of the box, but you can customize it by editing `level2_unified_system.py`:

```python
# At the end of the file, modify these settings:

system = UnifiedLevel2System(
    symbol='AAPL',                  # Stock to monitor
    use_extended_hours=True,        # Enable premarket/afterhours
    detect_hidden_orders=True,      # Enable hidden order detection
    port=7497,                      # 7497 = Paper, 7496 = Live
    host='127.0.0.1',              # Localhost
    clientId=1,                     # Unique client ID
)
```

### Advanced Settings

#### Market Depth Levels
```python
# In level2_unified_system.py, find subscribe_market_depth()
self.ib.reqMktDepth(
    contract,
    numRows=20,        # Number of price levels (max 20)
    isSmartDepth=True  # Aggregate across exchanges
)
```

#### Hidden Order Detection Sensitivity
```python
# In HiddenOrderDetector class
detector = HiddenOrderDetector(
    lookback_seconds=60,    # How far back to analyze
    sensitivity='medium'    # 'low', 'medium', or 'high'
)
```

**Sensitivity levels:**
- `low` - Only very obvious hidden orders
- `medium` - Balanced (recommended)
- `high` - More sensitive, may have false positives

#### Dashboard Update Frequency
```python
# In unified_dashboard.py, find dcc.Interval
dcc.Interval(
    id='interval-component',
    interval=1000,    # Update every 1 second (in milliseconds)
    n_intervals=0
)
```

---

## Running the System

### Method 1: Command Line (All Platforms)

**Start the Dashboard:**
```bash
python unified_dashboard.py AAPL
```

Replace `AAPL` with any stock symbol.

**The dashboard will:**
1. Connect to IBKR
2. Subscribe to Level 2 data
3. Start analyzing order flow
4. Launch web server at `http://127.0.0.1:8050`

**Open your browser to:**
```
http://127.0.0.1:8050
```

### Method 2: Windows Batch File

**Double-click:** `RUN_DASHBOARD.bat`

The script will:
1. Prompt you for a symbol
2. Start the dashboard
3. Display the URL to open

### Method 3: Standalone (No Dashboard)

If you just want console output without the web dashboard:

```python
python level2_unified_system.py AAPL
```

This will print updates to the terminal without launching a browser.

### Stopping the System

- **Keyboard:** Press `Ctrl+C` in the terminal
- **Browser:** Refresh won't stop it - must close terminal
- **TWS:** Disconnecting TWS will auto-stop the system

---

## Understanding the Dashboard

### Main Components

#### 1. Order Book Visualization (Top Left)
- **Green bars** = Bid orders (buyers)
- **Red bars** = Ask orders (sellers)
- **Thicker bars** = More volume at that price
- **Best bid/ask** = Highlighted in bold

#### 2. Trading Signal Panel (Top Right)
```
🟢 BUY (75% confidence)
   • Strong buyer absorption at $150.25
   • Queue imbalance: +0.45
   • Volume surge detected
```

**Signal Types:**
- `BUY` 🟢 - Buying pressure detected
- `SELL` 🔴 - Selling pressure detected
- `NEUTRAL` ⚪ - Balanced or unclear

**Confidence:**
- 80%+ = Very strong signal
- 60-79% = Strong signal
- 40-59% = Moderate signal
- <40% = Weak signal (be cautious)

#### 3. Hidden Order Detection (Alert Box)
```
🔍 Hidden BUYER detected (HIGH strength)
   Absorbing sells at $150.25
   
🧊 Iceberg order at $150.20 (BID)
   Refreshed 4 times
```

**What This Means:**
- **Hidden Buyer** = Someone absorbing all sells without showing their full size
- **Hidden Seller** = Someone absorbing all buys without showing their full size
- **Iceberg Order** = Large order showing only small pieces at a time

#### 4. Market Session Indicator
- 🌅 **PREMARKET** (4:00 AM - 9:30 AM ET)
- ☀️ **REGULAR** (9:30 AM - 4:00 PM ET)
- 🌆 **AFTERHOURS** (4:00 PM - 8:00 PM ET)
- 🌙 **CLOSED** (8:00 PM - 4:00 AM ET)

⚠️ Spreads are wider and liquidity is lower outside regular hours!

#### 5. Liquidity Heatmap (Middle)
Visual representation of where large orders sit:
- **Darker colors** = More volume
- **Vertical line** = Current price
- **Horizontal clusters** = Support/Resistance

#### 6. Price & Imbalance Chart (Bottom)
- **Blue line** = Microprice over time
- **Orange area** = Queue imbalance (positive = bullish)
- **Spikes** = Sudden order flow changes

#### 7. Support/Resistance Levels
Automatically detected price levels where orders cluster:
- **Green dashed lines** = Support (buying pressure)
- **Red dashed lines** = Resistance (selling pressure)

---

## Understanding Trading Signals

### Signal Generation Logic

The system combines multiple factors:

1. **Queue Imbalance** (weighted heavily)
   - Measures bid vs ask volume at each level
   - Positive = more buyers, Negative = more sellers

2. **Volume Pressure**
   - Weighted by distance from best bid/ask
   - Closer levels have more influence

3. **Hidden Order Detection**
   - Identifies absorption patterns
   - Detects iceberg orders

4. **Spread Analysis**
   - Wide spreads = uncertainty
   - Tight spreads = confidence

### How to Use Signals

#### BUY Signal Example:
```
🟢 BUY (75% confidence)
Reasons:
• Strong queue imbalance: +0.45
• Hidden buyer detected
• Volume surge at best bid
• Tight spread (5 bps)
```

**What to do:**
1. ✅ Verify in your trading platform
2. ✅ Check if price is at support
3. ✅ Look for confirmation (volume, momentum)
4. ✅ Enter ONLY if it aligns with your strategy
5. ❌ Don't blindly follow - use as confirmation

#### SELL Signal Example:
```
🔴 SELL (68% confidence)
Reasons:
• Heavy selling pressure
• Queue imbalance: -0.52
• Breaking support level
```

**What to do:**
1. Consider exiting longs
2. Or wait for better entry if planning to buy
3. Don't chase - let it stabilize

#### NEUTRAL Signal:
```
⚪ NEUTRAL (35% confidence)
Reasons:
• Balanced order book
• Low volume
```

**What to do:**
- Wait for clearer setup
- Don't force trades

---

## Advanced Features

### Support/Resistance Detection

The system automatically finds price levels where orders cluster:

**How it works:**
1. Tracks where large orders sit over time
2. Identifies levels that get repeatedly defended
3. Marks these as support (buying) or resistance (selling)

**On the dashboard:**
- Green dashed lines = Support
- Red dashed lines = Resistance
- Thicker lines = Stronger levels

**Trading with S/R:**
- Enter longs near support
- Enter shorts near resistance
- Watch for breakouts when price crosses these levels

### Hidden Order Detection Explained

#### Hidden Buyers
**Pattern:** Lots of selling, but price doesn't drop

**What's happening:** A large buyer is absorbing all sells without showing their full size on the order book.

**Trading implication:** 
- Bullish - big player accumulating
- Price likely to move up once selling exhausted
- Good time to buy

#### Hidden Sellers
**Pattern:** Lots of buying, but price doesn't rise

**What's happening:** A large seller is absorbing all buys without showing their full size.

**Trading implication:**
- Bearish - big player distributing
- Price likely to move down once buying exhausted
- Avoid buying, consider selling

#### Iceberg Orders
**Pattern:** Order at a price level keeps "refreshing" with same size

**What's happening:** Large order showing only a small portion. When filled, it automatically refreshes.

**Example:**
```
10:30:00 - 500 shares at $150.00
10:30:05 - Filled
10:30:06 - 500 shares at $150.00 (refreshed)
10:30:11 - Filled
10:30:12 - 500 shares at $150.00 (refreshed again!)
```

**Trading implication:**
- Strong support/resistance at that price
- Difficult to move through that level
- If it's a bid iceberg = support
- If it's an ask iceberg = resistance

### Extended Hours Trading

The system works during:
- **Premarket** (4:00 AM - 9:30 AM ET)
- **Regular** (9:30 AM - 4:00 PM ET)
- **Afterhours** (4:00 PM - 8:00 PM ET)

**Extended Hours Considerations:**
⚠️ Lower liquidity = wider spreads  
⚠️ Fewer price levels visible  
⚠️ More volatile movements  
⚠️ Use larger position sizing caution  

**Dashboard indicators:**
- 🌅 PREMARKET warning shown
- 🌆 AFTERHOURS warning shown
- Spread BPS highlighted if >10

---

## Troubleshooting

### Connection Issues

**Error: "ConnectionRefusedError"**

```
Causes:
- TWS/Gateway not running
- Wrong port number
- API not enabled

Fix:
1. Start TWS or IB Gateway
2. Verify it's fully loaded (not still initializing)
3. Check API settings (File → Global Configuration → API)
4. Ensure port matches (7497 for paper, 7496 for live)
```

**Error: "Market data farm connection is inactive"**

```
Cause:
- No Level 2 data subscription
- Subscription not activated yet

Fix:
1. Log into Account Management
2. Go to Market Data Subscriptions
3. Verify Level 2 is active
4. Wait 24 hours if just subscribed
5. Contact IBKR support if issue persists
```

**Error: "No market data permissions"**

```
Cause:
- Missing data subscription
- Using live port with paper account (or vice versa)

Fix:
1. Verify account type matches port
2. Check market data subscriptions
3. Paper accounts need separate subscriptions
```

### Dashboard Issues

**Dashboard won't open in browser**

```
Fix:
1. Verify dashboard started without errors
2. Look for "Running on http://127.0.0.1:8050"
3. Try different browser
4. Check if port 8050 is already in use:
   - Windows: netstat -ano | findstr :8050
   - Mac/Linux: lsof -i :8050
5. Change port in unified_dashboard.py if needed
```

**Dashboard shows "No Data"**

```
Causes:
- Market closed and not using extended hours
- Symbol not found
- Not subscribed to that exchange's data

Fix:
1. Check market hours
2. Verify symbol is correct (AAPL not APPL)
3. Wait 30 seconds for initial data
4. Check terminal for error messages
```

**Charts not updating**

```
Fix:
1. Check browser console for errors (F12)
2. Verify "Connection Status: Connected" in dashboard
3. Refresh the page (F5)
4. Restart the system
```

### Data Quality Issues

**Only seeing a few price levels**

```
Causes:
- Low liquidity stock
- Extended hours (normal)
- Wrong exchange

Fix:
1. Check if using high-volume stock
2. Verify market session (regular hours has most depth)
3. Try SMART exchange routing
```

**Spread very wide (>50 bps)**

```
This is normal for:
- Small cap stocks
- Extended hours
- Low liquidity moments

Not an error - just market conditions
```

**No hidden order detection**

```
Causes:
- Not enough historical data yet (wait 1-2 minutes)
- Low trading activity
- Feature disabled

Fix:
1. Verify detect_hidden_orders=True in config
2. Wait for more data accumulation
3. Use more liquid stocks
```

### Performance Issues

**High CPU usage**

```
Fix:
1. Reduce update frequency in dashboard
2. Reduce number of price levels (numRows in config)
3. Close other applications
4. Use lighter browser (Chrome/Edge better than Firefox)
```

**Delayed updates**

```
Fix:
1. Check internet connection
2. Reduce dashboard update interval
3. Use fewer charts (comment out in layout)
4. Restart TWS/Gateway (memory leak)
```

### Common Errors

**"Symbol not found"**

```
Fix:
1. Use correct ticker (AAPL not APPLE)
2. Include exchange if needed (AAPL on SMART)
3. Verify stock is trading today
```

**"clientId already in use"**

```
Fix:
1. Change clientId in config to different number
2. Or close other API connections using same ID
```

**"Duplicate ticker ID"**

```
Fix:
Restart the system - this is a race condition
```

---

## Best Practices

### 1. Start With Paper Trading
- Use port 7497
- Test strategies without risk
- Verify signals make sense

### 2. Use Liquid Stocks
Best results with:
- AAPL, TSLA, SPY, QQQ, MSFT, NVDA
- Stocks with >10M average daily volume
- Tight spreads (<10 bps)

### 3. Regular Hours Are Best
- Most liquidity 9:30 AM - 4:00 PM ET
- Clearer signals
- Tighter spreads

### 4. Don't Overtrade Signals
- Signals are suggestions, not guarantees
- Wait for 60%+ confidence
- Confirm with your own analysis
- Use proper risk management

### 5. Monitor Multiple Timeframes
- Level 2 is short-term (seconds to minutes)
- Check higher timeframe trend
- Don't fight the daily trend

### 6. Set Reasonable Expectations
- Level 2 shows intent, not certainty
- Large orders can be pulled instantly
- Hidden orders can disappear
- Always use stops

---

## System Requirements Summary

### Minimum Requirements
- Python 3.8+
- 2GB RAM
- IBKR account with Level 2 subscription
- TWS or IB Gateway
- Internet connection

### Recommended Setup
- Python 3.10+
- 4GB+ RAM
- Dual monitors
- Fast internet (10+ Mbps)
- SMART routing with multi-exchange data

### Cost Summary
- **IBKR Account:** Free (minimum $0-$10k depending on age)
- **Level 2 Data:** ~$10-15/month
- **Software:** Free (Python, TWS, this system)

**Total recurring cost:** ~$10-15/month for data

---

## Getting Help

### Check Logs
The system creates detailed logs in the terminal. Look for:
- `ERROR` messages for problems
- `WARN` messages for issues
- `INFO` messages for status

### Common Resources
- **IBKR API Docs:** https://interactivebrokers.github.io/tws-api/
- **ib_insync Docs:** https://ib-insync.readthedocs.io/
- **Dash Docs:** https://dash.plotly.com/

### Debug Mode
Enable verbose logging by editing the file:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Safety & Disclaimers

⚠️ **Important Warnings:**

1. **This is educational software** - Not financial advice
2. **Start with paper trading** - Test thoroughly before using real money
3. **Signals are not guarantees** - Markets are unpredictable
4. **Use proper risk management** - Always use stops
5. **Level 2 can be spoofed** - Large orders can disappear instantly
6. **Check costs** - Active trading incurs commissions
7. **Follow regulations** - Pattern day trader rules apply

**The developers are not responsible for:**
- Trading losses
- Data accuracy
- System failures
- Missed opportunities
- Any financial outcomes

**Use at your own risk. Only trade with money you can afford to lose.**

---

## Next Steps

Once you have the system running:

1. **📊 Observe** - Watch for 1-2 weeks without trading
2. **📝 Take notes** - Track which signals work vs don't
3. **🔧 Tune parameters** - Adjust sensitivity for your style
4. **📈 Backtest** - Compare signals to actual price movements
5. **💰 Start small** - Trade 1-share positions initially
6. **📚 Keep learning** - Study order flow and market microstructure

---

## Quick Reference Card

**Start System:**
```bash
python unified_dashboard.py AAPL
```

**Open Dashboard:**
```
http://127.0.0.1:8050
```

**Stop System:**
```
Ctrl+C in terminal
```

**Ports:**
- 7497 = Paper Trading
- 7496 = Live Trading
- 8050 = Dashboard

**Signal Confidence:**
- 80%+ = Very Strong
- 60-79% = Strong  
- 40-59% = Moderate
- <40% = Weak

**Market Hours (ET):**
- Premarket: 4:00 AM - 9:30 AM
- Regular: 9:30 AM - 4:00 PM
- Afterhours: 4:00 PM - 8:00 PM

---

*Last Updated: 2025*
*Compatible with: Interactive Brokers API, Python 3.8+, ib_insync*
