# Level 2 System - Troubleshooting Cheat Sheet

Quick solutions to common problems.

---

## Connection Errors

### "ConnectionRefusedError: [Errno 61] Connection refused"

**Cause:** TWS/Gateway not running or API not enabled

**Fix:**
```
1. ✅ Launch TWS or IB Gateway
2. ✅ Wait for it to fully load (30-60 seconds)
3. ✅ File → Global Configuration → API → Settings
4. ✅ Enable "ActiveX and Socket Clients"
5. ✅ Restart TWS/Gateway
6. ✅ Try again
```

---

### "Error 504: Not connected"

**Cause:** Wrong port or clientId conflict

**Fix:**
```
1. Check port number:
   • Paper trading = 7497
   • Live trading = 7496
2. In level2_unified_system.py, change:
   port=7497  (or 7496 for live)
3. If still failing, change clientId:
   clientId=2  (try different numbers)
```

---

### "Market data farm connection is inactive"

**Cause:** No Level 2 data subscription

**Fix:**
```
1. Go to https://www.interactivebrokers.com
2. Login → Account Management
3. Settings → Market Data Subscriptions
4. Verify Level 2 subscription is ACTIVE
5. If just subscribed, wait 24 hours
6. Contact IBKR support if still inactive
```

---

## Data Issues

### "No data appearing in dashboard"

**Check these in order:**

```
1. ✅ Is TWS/Gateway connected? (check terminal for errors)
2. ✅ Is market open? (9:30 AM - 4:00 PM ET for regular hours)
3. ✅ Is symbol correct? (AAPL not APPL)
4. ✅ Wait 30 seconds for initial data
5. ✅ Check terminal for error messages
6. ✅ Try a different symbol (SPY always has data)
```

---

### Only seeing 2-3 price levels

**This is normal when:**
- Extended hours (premarket/afterhours)
- Low liquidity stock
- Market closed

**Fix:**
```
• Use during regular hours (9:30 AM - 4:00 PM ET)
• Use liquid stocks (SPY, AAPL, TSLA, QQQ)
• Check market calendar (market open today?)
```

---

### Spread is very wide (>50 bps)

**This is expected for:**
- Small cap stocks
- Extended hours
- Low volume periods

**Not an error - just market conditions**

To get tighter spreads:
```
• Trade during regular hours
• Use large cap stocks
• Avoid first/last 5 minutes of trading
```

---

## Dashboard Issues

### Dashboard won't open in browser

**Cause:** Port conflict or server didn't start

**Fix:**
```
1. Look in terminal for:
   "Running on http://127.0.0.1:8050"
2. Copy that EXACT URL to browser
3. If no URL shown:
   • Check for error messages in terminal
   • Try: pip install --upgrade dash plotly
4. If port 8050 busy:
   • Windows: netstat -ano | findstr :8050
   • Mac/Linux: lsof -i :8050
   • Kill that process or change port in code
```

---

### Dashboard shows but no updates

**Fix:**
```
1. Check "Connection Status" in dashboard header
2. Should say "Connected" - if not:
   • Check TWS/Gateway is running
   • Restart the system
3. If "Connected" but still no updates:
   • Refresh browser (F5)
   • Check browser console (F12) for errors
   • Restart system
```

---

### Charts frozen/not updating

**Fix:**
```
1. Refresh page (F5)
2. Check terminal for errors
3. Restart system
4. Try different browser (Chrome works best)
5. Clear browser cache
```

---

## Package/Import Errors

### "ModuleNotFoundError: No module named 'ib_insync'"

**Fix:**
```bash
pip install ib_insync
# Or if that fails:
pip install --upgrade ib_insync
```

---

### "ModuleNotFoundError: No module named 'dash'"

**Fix:**
```bash
pip install dash plotly
```

---

### "ImportError: DLL load failed" (Windows)

**Fix:**
```
1. Reinstall Visual C++ Redistributables
2. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
3. Install and restart computer
4. Try again
```

---

## Signal/Detection Issues

### No trading signals appearing

**Causes:**
- Not enough data yet (wait 1-2 minutes)
- Market closed
- Very balanced order book (NEUTRAL is correct)

**Fix:**
```
1. Wait 2-3 minutes for data accumulation
2. Check market is open
3. Try more volatile stock (TSLA vs KO)
4. NEUTRAL is valid - means no clear direction
```

---

### No hidden orders detected

**This is normal when:**
- Not much trading activity
- Balanced market
- Stock not being accumulated/distributed

**Not an error** - hidden orders are rare!

Only appears when:
```
• Large player absorbing orders
• Iceberg orders present
• Accumulation/distribution happening
```

---

### Signal seems wrong

**Remember:**
- Signals are suggestions, not facts
- Level 2 shows intent, not certainty
- Large orders can be pulled instantly
- Always verify with your own analysis

**If consistently wrong:**
```
1. Adjust sensitivity in config
2. Track win rate over 100+ signals
3. May need parameter tuning for your stocks
```

---

## Performance Issues

### High CPU usage

**Fix:**
```
1. Reduce update frequency:
   In unified_dashboard.py:
   interval=2000  # Change from 1000 to 2000
2. Reduce price levels:
   In level2_unified_system.py:
   numRows=10  # Change from 20 to 10
3. Close other applications
4. Use Chrome/Edge (not Firefox)
```

---

### System slow/laggy

**Fix:**
```
1. Restart TWS/Gateway (can have memory leaks)
2. Reduce update interval in dashboard
3. Use fewer charts (comment out in layout)
4. Check internet speed (need 5+ Mbps)
5. Use better computer if possible
```

---

### Dashboard crashes after a while

**Cause:** Memory accumulation

**Fix:**
```
1. Restart system every few hours
2. Reduce maxlen in deques:
   In unified_dashboard.py:
   deque(maxlen=100)  # Change from 200
3. Close and restart browser periodically
```

---

## TWS/Gateway Specific

### "TWS not started" error

**Fix:**
```
1. Launch TWS or IB Gateway
2. Wait for full startup (watch for "Ready")
3. Login if prompted
4. Try connecting again
```

---

### "Session disconnected" during use

**Fix:**
```
1. Check internet connection
2. Restart TWS/Gateway
3. System should auto-reconnect (wait 30 sec)
4. If not, restart the dashboard
```

---

### "No security definition found"

**Cause:** Symbol doesn't exist or wrong format

**Fix:**
```
1. Verify ticker symbol (AAPL not APPLE)
2. Use SMART exchange routing
3. Try with exchange suffix:
   AAPL.NASDAQ or AAPL.ARCA
4. Check stock is trading today
```

---

## Quick Diagnostic Commands

### Test IBKR Connection
```python
from ib_insync import IB
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
print("✅ Connected!" if ib.isConnected() else "❌ Failed")
ib.disconnect()
```

### Check Python Packages
```bash
pip list | grep ib-insync
pip list | grep dash
pip list | grep plotly
```

### Check Port Usage (Windows)
```cmd
netstat -ano | findstr :7497
netstat -ano | findstr :8050
```

### Check Port Usage (Mac/Linux)
```bash
lsof -i :7497
lsof -i :8050
```

---

## When All Else Fails

### Nuclear Option (Reset Everything)

```bash
# 1. Close everything
#    - Close browser
#    - Ctrl+C in terminal
#    - Close TWS/Gateway

# 2. Reinstall packages
pip uninstall ib_insync dash plotly -y
pip install ib_insync dash plotly

# 3. Restart TWS/Gateway
#    - Wait for full startup
#    - Verify API enabled

# 4. Restart dashboard
python unified_dashboard.py AAPL

# 5. Fresh browser window
#    - Open NEW incognito window
#    - Go to http://127.0.0.1:8050
```

---

## Getting More Help

### Enable Debug Logging

In `level2_unified_system.py` and `unified_dashboard.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

This will show MUCH more detail about what's happening.

### Check TWS Logs

**Location:**
- Windows: `C:\Users\<username>\Jts\<version>\log.xxx.txt`
- Mac: `~/Jts/<version>/log.xxx.txt`

Look for errors related to API or market data.

---

## Error Code Reference

| Code | Meaning | Fix |
|------|---------|-----|
| 200 | No security definition | Wrong symbol or exchange |
| 354 | Requested market data not subscribed | Need Level 2 subscription |
| 504 | Not connected | Start TWS/Gateway |
| 1100 | Lost connection | Internet issue - will reconnect |
| 2104 | Market data OK | Normal - not an error |
| 2106 | HMDS data OK | Normal - not an error |

---

## Still Stuck?

1. **Re-read full guide:** LEVEL2_SETUP_GUIDE.md
2. **Check IBKR status:** https://www.interactivebrokers.com/status
3. **Try with paper account first** (port 7497)
4. **Test with SPY** (always has data)
5. **Contact IBKR support** for account/data issues

---

## Quick Tips

💡 **Most issues are solved by:**
1. Restarting TWS/Gateway
2. Checking market hours
3. Verifying Level 2 subscription
4. Using liquid stocks
5. Waiting 30-60 seconds for data

💡 **Remember:**
- System needs 1-2 minutes to accumulate data
- Extended hours have less data (normal)
- Low volume stocks show fewer levels (normal)
- Market closed = no data (normal)

---

**Last Resort:** Delete everything, redownload, and start fresh with the Quick Start guide.
