@echo off
REM ================================================================
REM Unified Level 2 Dashboard Launcher
REM ================================================================
REM 
REM This launches the web-based dashboard with all visualizations
REM 
REM ================================================================

echo.
echo ================================================
echo UNIFIED LEVEL 2 DASHBOARD
echo ================================================
echo.
echo Features:
echo   - Real-time Order Book Visualization
echo   - Trading Signals with Confidence
echo   - Hidden Order Detection
echo   - Support/Resistance Levels  
echo   - Liquidity Heatmap
echo   - Price and Imbalance Charts
echo   - Extended Hours Support
echo.
echo ================================================
echo.

REM Prompt for symbol
set /p SYMBOL="Enter stock symbol (default: AAPL): "
if "%SYMBOL%"=="" set SYMBOL=AAPL

echo.
echo Starting dashboard for %SYMBOL%...
echo.
echo Dashboard will open at: http://127.0.0.1:8050
echo.
echo Press Ctrl+C to stop the dashboard
echo.

REM Run the dashboard
python unified_dashboard.py %SYMBOL%

pause
