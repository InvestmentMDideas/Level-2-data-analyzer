"""
IBKR Level 2 UNIFIED TRADING SYSTEM - ALL FEATURES COMBINED
============================================================

This is a consolidated version combining ALL features from:
- level2_collector_improved.py
- level2_collector_premarket.py  
- level2_collector_with_trades.py
- hidden_order_detector.py
- signal_generator (improved + premarket)
- All visualizers

Features:
✅ Thread-safe operations with locks
✅ Proper price level aggregation (no duplicates)
✅ Microprice calculation
✅ Queue position imbalance
✅ UTC timestamps
✅ Extended hours support (premarket/afterhours)
✅ Multi-exchange fallback
✅ Adaptive to market sessions
✅ Time & Sales (trade tracking)
✅ Hidden order detection (buyers/sellers/icebergs)
✅ Signal generation (BUY/NEUTRAL/SELL)
✅ Support/resistance detection
✅ Reconnection logic with exponential backoff
✅ Comprehensive logging

Usage:
    # Basic usage
    system = UnifiedLevel2System('AAPL')
    system.start()
    
    # With custom options
    system = UnifiedLevel2System(
        symbol='TSLA',
        use_extended_hours=True,
        detect_hidden_orders=True,
        port=7497
    )
    system.start()
"""

from ib_insync import IB, Stock, util
import pandas as pd
import numpy as np
from datetime import datetime, timezone, time, timedelta
from collections import deque, defaultdict
import json
import logging
import threading
import time as time_module
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HiddenOrderDetector:
    """
    Integrated hidden order detector for Level 2 data
    Detects: hidden buyers, hidden sellers, iceberg orders
    """
    
    def __init__(self, lookback_seconds=60, sensitivity='medium'):
        self.lookback_seconds = lookback_seconds
        self.sensitivity = sensitivity
        
        # Time & Sales tracking
        self.trades = deque(maxlen=1000)
        self.trade_timestamps = deque(maxlen=1000)
        
        # Order book snapshots
        self.order_book_snapshots = deque(maxlen=100)
        self.price_level_history = defaultdict(lambda: deque(maxlen=50))
        
        # Price movement tracking
        self.price_history = deque(maxlen=200)
        self.timestamp_history = deque(maxlen=200)
        
        # Detection state
        self.hidden_buyers = []
        self.hidden_sellers = []
        self.iceberg_orders = {}
        
        # Thresholds
        self.thresholds = self._get_thresholds(sensitivity)
        
    def _get_thresholds(self, sensitivity):
        """Get detection thresholds based on sensitivity"""
        thresholds = {
            'low': {
                'volume_threshold': 5.0,
                'price_movement_min': 0.02,
                'refresh_count': 5,
                'divergence_ratio': 4.0,
            },
            'medium': {
                'volume_threshold': 3.0,
                'price_movement_min': 0.015,
                'refresh_count': 3,
                'divergence_ratio': 3.0,
            },
            'high': {
                'volume_threshold': 2.0,
                'price_movement_min': 0.01,
                'refresh_count': 2,
                'divergence_ratio': 2.0,
            }
        }
        return thresholds.get(sensitivity, thresholds['medium'])
    
    def add_trade(self, price, size, side, timestamp=None):
        """Add a trade from time & sales"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        self.trades.append({
            'price': price,
            'size': size,
            'side': side,
            'timestamp': timestamp
        })
        self.trade_timestamps.append(timestamp)
    
    def add_price_update(self, price, timestamp=None):
        """Track price movement"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        self.price_history.append(price)
        self.timestamp_history.append(timestamp)
    
    def add_order_book_snapshot(self, bids, asks, timestamp=None):
        """Track order book for iceberg detection"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        snapshot = {
            'timestamp': timestamp,
            'bids': dict(bids) if isinstance(bids, list) else bids,
            'asks': dict(asks) if isinstance(asks, list) else asks
        }
        
        self.order_book_snapshots.append(snapshot)
        
        # Track individual price levels
        for price, size in (bids if isinstance(bids, list) else bids.items()):
            self.price_level_history[('bid', price)].append({
                'timestamp': timestamp,
                'size': size
            })
        
        for price, size in (asks if isinstance(asks, list) else asks.items()):
            self.price_level_history[('ask', price)].append({
                'timestamp': timestamp,
                'size': size
            })
    
    def detect_hidden_orders(self):
        """Main detection method - returns detected patterns"""
        results = {
            'hidden_buyer': None,
            'hidden_seller': None,
            'icebergs': [],
            'analysis': {}
        }
        
        # Need enough data
        if len(self.trades) < 10 or len(self.price_history) < 10:
            return results
        
        # Detect hidden buyers/sellers
        volume_metrics = self.calculate_volume_metrics(seconds=30)
        price_change = self.calculate_price_change(seconds=30)
        
        if volume_metrics and price_change is not None:
            results['analysis'] = {
                'buy_volume': volume_metrics['buy_volume'],
                'sell_volume': volume_metrics['sell_volume'],
                'price_change_pct': price_change * 100
            }
            
            # Hidden buyer detection
            if (volume_metrics['sell_volume'] > volume_metrics['buy_volume'] * 1.5 and 
                price_change > -0.005):  # Sells but price stable/up
                results['hidden_buyer'] = {
                    'strength': 'HIGH' if price_change > 0 else 'MEDIUM',
                    'sell_volume': volume_metrics['sell_volume'],
                    'price_change': price_change
                }
            
            # Hidden seller detection
            if (volume_metrics['buy_volume'] > volume_metrics['sell_volume'] * 1.5 and 
                price_change < 0.005):  # Buys but price stable/down
                results['hidden_seller'] = {
                    'strength': 'HIGH' if price_change < 0 else 'MEDIUM',
                    'buy_volume': volume_metrics['buy_volume'],
                    'price_change': price_change
                }
        
        # Detect icebergs
        results['icebergs'] = self.detect_iceberg_orders()
        
        return results
    
    def calculate_volume_metrics(self, seconds=30):
        """Calculate buy/sell volume"""
        if not self.trades:
            return None
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=seconds)
        recent_trades = [t for t in self.trades if t['timestamp'] >= cutoff_time]
        
        if not recent_trades:
            return None
        
        buy_volume = sum(t['size'] for t in recent_trades if t['side'] == 'buy')
        sell_volume = sum(t['size'] for t in recent_trades if t['side'] == 'sell')
        
        return {
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'net_volume': buy_volume - sell_volume,
            'buy_trades': len([t for t in recent_trades if t['side'] == 'buy']),
            'sell_trades': len([t for t in recent_trades if t['side'] == 'sell'])
        }
    
    def calculate_price_change(self, seconds=30):
        """Calculate price change percentage"""
        if len(self.price_history) < 2:
            return None
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=seconds)
        
        # Get prices within timeframe
        recent_indices = [i for i, ts in enumerate(self.timestamp_history) if ts >= cutoff_time]
        
        if len(recent_indices) < 2:
            return None
        
        start_price = self.price_history[recent_indices[0]]
        end_price = self.price_history[recent_indices[-1]]
        
        return (end_price - start_price) / start_price
    
    def detect_iceberg_orders(self):
        """Detect iceberg orders (orders that keep refilling)"""
        icebergs = []
        
        if len(self.order_book_snapshots) < 5:
            return icebergs
        
        # Check each price level for refill behavior
        for (side, price), history in self.price_level_history.items():
            if len(history) < 5:
                continue
            
            # Look for disappearing and reappearing pattern
            sizes = [h['size'] for h in history]
            
            # Iceberg signature: size drops then refills to similar level
            refills = 0
            for i in range(1, len(sizes) - 1):
                if sizes[i] < sizes[i-1] * 0.5 and sizes[i+1] > sizes[i-1] * 0.8:
                    refills += 1
            
            if refills >= self.thresholds['refresh_count']:
                avg_size = np.mean(sizes)
                icebergs.append({
                    'price': price,
                    'side': side,
                    'avg_size': avg_size,
                    'refills': refills,
                    'strength': 'HIGH' if refills >= 5 else 'MEDIUM'
                })
        
        return icebergs


class SignalGenerator:
    """
    Integrated signal generator with support/resistance detection
    """
    
    def __init__(self, lookback_window=50):
        self.lookback_window = lookback_window
        self.price_history = deque(maxlen=lookback_window)
        self.feature_history = deque(maxlen=lookback_window)
        
        # Support/resistance tracking
        self.support_levels = []
        self.resistance_levels = []
        
    def add_features(self, features):
        """Add features for analysis"""
        if 'microprice' in features:
            self.price_history.append(features['microprice'])
        self.feature_history.append(features)
    
    def find_support_resistance(self):
        """Find support and resistance levels"""
        if len(self.price_history) < 20:
            return [], []
        
        prices = list(self.price_history)
        
        # Find local minima (support) and maxima (resistance)
        support = []
        resistance = []
        
        for i in range(2, len(prices) - 2):
            # Local minimum = support
            if prices[i] < prices[i-1] and prices[i] < prices[i-2] and \
               prices[i] < prices[i+1] and prices[i] < prices[i+2]:
                support.append(prices[i])
            
            # Local maximum = resistance
            if prices[i] > prices[i-1] and prices[i] > prices[i-2] and \
               prices[i] > prices[i+1] and prices[i] > prices[i+2]:
                resistance.append(prices[i])
        
        # Cluster nearby levels
        self.support_levels = self._cluster_levels(support) if support else []
        self.resistance_levels = self._cluster_levels(resistance) if resistance else []
        
        return self.support_levels, self.resistance_levels
    
    def _cluster_levels(self, levels, tolerance=0.01):
        """Cluster nearby price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        if current_cluster:
            clusters.append(np.mean(current_cluster))
        
        return clusters
    
    def generate_signal(self, features, hidden_order_results=None):
        """
        Generate BUY/NEUTRAL/SELL signal with reasoning
        
        Returns: dict with 'signal', 'confidence', 'reasons'
        """
        if not features:
            return {'signal': 'NEUTRAL', 'confidence': 0, 'reasons': ['No data']}
        
        signal_score = 0
        reasons = []
        
        # Get current price
        current_price = features.get('microprice', features.get('mid_price', 0))
        
        # 1. Queue imbalance (strongest indicator)
        queue_imb = features.get('queue_imbalance', 0)
        if queue_imb > 0.3:
            signal_score += 3
            reasons.append(f"Strong buy pressure (queue: {queue_imb:.2f})")
        elif queue_imb > 0.15:
            signal_score += 1
            reasons.append(f"Moderate buy pressure (queue: {queue_imb:.2f})")
        elif queue_imb < -0.3:
            signal_score -= 3
            reasons.append(f"Strong sell pressure (queue: {queue_imb:.2f})")
        elif queue_imb < -0.15:
            signal_score -= 1
            reasons.append(f"Moderate sell pressure (queue: {queue_imb:.2f})")
        
        # 2. Weighted imbalance
        weighted_imb = features.get('weighted_imbalance', 0)
        if weighted_imb > 0.2:
            signal_score += 1
            reasons.append(f"Weighted buy imbalance: {weighted_imb:.2f}")
        elif weighted_imb < -0.2:
            signal_score -= 1
            reasons.append(f"Weighted sell imbalance: {weighted_imb:.2f}")
        
        # 3. Spread analysis
        spread_bps = features.get('spread_bps', 0)
        if spread_bps > 50:
            reasons.append(f"⚠️ Wide spread ({spread_bps:.0f} bps)")
            signal_score = signal_score * 0.7  # Reduce confidence
        
        # 4. Support/resistance
        support, resistance = self.find_support_resistance()
        if support and resistance:
            nearest_support = min(support, key=lambda x: abs(x - current_price))
            nearest_resistance = min(resistance, key=lambda x: abs(x - current_price))
            
            # Near support = potential buy
            if abs(current_price - nearest_support) / current_price < 0.005:
                signal_score += 2
                reasons.append(f"Near support at ${nearest_support:.2f}")
            
            # Near resistance = potential sell
            if abs(current_price - nearest_resistance) / current_price < 0.005:
                signal_score -= 2
                reasons.append(f"Near resistance at ${nearest_resistance:.2f}")
        
        # 5. Hidden orders (if available)
        if hidden_order_results:
            if hidden_order_results.get('hidden_buyer'):
                signal_score += 2
                strength = hidden_order_results['hidden_buyer']['strength']
                reasons.append(f"🔍 Hidden buyer detected ({strength})")
            
            if hidden_order_results.get('hidden_seller'):
                signal_score -= 2
                strength = hidden_order_results['hidden_seller']['strength']
                reasons.append(f"🔍 Hidden seller detected ({strength})")
            
            icebergs = hidden_order_results.get('icebergs', [])
            if icebergs:
                for ice in icebergs[:2]:  # Top 2
                    if ice['side'] == 'bid':
                        signal_score += 1
                        reasons.append(f"🧊 Iceberg buy at ${ice['price']:.2f}")
                    else:
                        signal_score -= 1
                        reasons.append(f"🧊 Iceberg sell at ${ice['price']:.2f}")
        
        # 6. Market session adjustment
        session = features.get('session', 'REGULAR')
        if session in ['PREMARKET', 'AFTERHOURS']:
            reasons.append(f"⏰ {session} session - use caution")
            signal_score = signal_score * 0.8
        
        # Generate final signal
        if signal_score >= 3:
            signal = 'BUY'
            confidence = min(signal_score / 8 * 100, 100)
        elif signal_score <= -3:
            signal = 'SELL'
            confidence = min(abs(signal_score) / 8 * 100, 100)
        else:
            signal = 'NEUTRAL'
            confidence = 30
        
        return {
            'signal': signal,
            'confidence': round(confidence, 1),
            'reasons': reasons,
            'score': signal_score,
            'price': current_price
        }


class UnifiedLevel2System:
    """
    Complete unified Level 2 trading system with all features
    """
    
    def __init__(self, symbol, exchange='SMART', max_history=1000, 
                 use_extended_hours=True, detect_hidden_orders=False,
                 host='127.0.0.1', port=7497, client_id=1):
        """
        Initialize unified system
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (SMART, ISLAND, ARCA, etc.)
            max_history: Max history to keep
            use_extended_hours: Enable premarket/afterhours
            detect_hidden_orders: Enable hidden order detection
            host: IBKR host
            port: IBKR port (7497=TWS paper, 7496=TWS live, 4002=Gateway paper, 4001=Gateway live)
            client_id: Client ID
        """
        self.ib = IB()
        self.symbol = symbol
        self.exchange = exchange
        self.max_history = max_history
        self.use_extended_hours = use_extended_hours
        self.detect_hidden_orders = detect_hidden_orders
        
        # Connection settings
        self.host = host
        self.port = port
        self.client_id = client_id
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Data storage
        self.order_book_history = deque(maxlen=max_history)
        self.trade_history = deque(maxlen=max_history)
        
        # Current order book
        self.current_order_book = {
            'bids': {},
            'asks': {}
        }
        
        # Components
        self.hidden_detector = HiddenOrderDetector() if detect_hidden_orders else None
        self.signal_generator = SignalGenerator()
        
        self.contract = None
        self.callbacks = []
        self.ticker = None
        
        # Trade tracking
        self.last_price = None
        self.last_trade_time = None
        
        # Connection state
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        # Market session
        self.current_session = self.get_market_session()
        
    def get_market_session(self):
        """Determine current market session"""
        et_tz = pytz.timezone('US/Eastern')
        now_et = datetime.now(et_tz)
        current_time = now_et.time()
        weekday = now_et.weekday()
        
        if weekday >= 5:
            return "CLOSED"
        
        premarket_start = time(4, 0)
        market_open = time(9, 30)
        market_close = time(16, 0)
        afterhours_end = time(20, 0)
        
        if current_time < premarket_start:
            return "CLOSED"
        elif premarket_start <= current_time < market_open:
            return "PREMARKET"
        elif market_open <= current_time < market_close:
            return "REGULAR"
        elif market_close <= current_time < afterhours_end:
            return "AFTERHOURS"
        else:
            return "CLOSED"
    
    def connect(self):
        """Connect to IBKR with auto port detection"""
        # Try multiple ports automatically
        ports_to_try = [self.port, 7497, 7496, 4002, 4001]
        
        for port in ports_to_try:
            try:
                logger.info(f"Trying to connect to {self.host}:{port}...")
                self.ib.connect(self.host, port, clientId=self.client_id, timeout=20, readonly=False)
                
                self.is_connected = True
                self.reconnect_attempts = 0
                self.port = port  # Save successful port
                
                # Setup for extended hours
                if self.use_extended_hours:
                    self.ib.reqMarketDataType(4)  # Delayed frozen
                else:
                    self.ib.reqMarketDataType(1)  # Live
                
                session = self.get_market_session()
                logger.info(f"✅ Connected to IBKR on {self.host}:{port}")
                logger.info(f"📊 Market session: {session}")
                logger.info(f"⏰ Extended hours: {'ENABLED' if self.use_extended_hours else 'DISABLED'}")
                logger.info(f"🔍 Hidden orders: {'ENABLED' if self.detect_hidden_orders else 'DISABLED'}")
                
                time_module.sleep(1)
                return True
                
            except Exception as e:
                logger.warning(f"Port {port} failed: {e}")
                try:
                    self.ib.disconnect()
                except:
                    pass
                continue
        
        logger.error("❌ Failed to connect on any port")
        self.is_connected = False
        return False
    
    def reconnect(self):
        """Attempt to reconnect with exponential backoff"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            wait_time = min(5 * (2 ** (self.reconnect_attempts - 1)), 60)
            
            logger.warning(f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} in {wait_time}s...")
            time_module.sleep(wait_time)
            
            try:
                self.ib.disconnect()
                time_module.sleep(2)
            except:
                pass
            
            if self.connect():
                logger.info("✅ Reconnection successful!")
                if self.contract:
                    self.subscribe_market_depth()
                return True
        
        logger.error("❌ Max reconnection attempts reached")
        return False
    
    def get_best_exchanges_for_session(self):
        """Get best exchanges for current session"""
        session = self.get_market_session()
        
        if session == "PREMARKET":
            return ['ISLAND', 'ARCA', 'EDGEA', 'BYX', 'BZX', 'SMART']
        elif session == "AFTERHOURS":
            return ['ISLAND', 'ARCA', 'EDGEA', 'SMART']
        elif session == "REGULAR":
            return ['ISLAND', 'SMART', 'ARCA']
        else:
            return ['SMART']
    
    def subscribe_market_depth(self, num_rows=20):
        """Subscribe to Level 2 market depth with multi-exchange fallback"""
        try:
            session = self.get_market_session()
            logger.info(f"📊 Current session: {session}")
            
            # Adjust rows for extended hours
            if session in ["PREMARKET", "AFTERHOURS"]:
                num_rows = min(num_rows, 10)
            
            # Try multiple exchanges
            exchanges_to_try = self.get_best_exchanges_for_session()
            
            for exchange in exchanges_to_try:
                try:
                    logger.info(f"Trying {self.symbol} on {exchange}...")
                    
                    self.contract = Stock(self.symbol, exchange, 'USD')
                    self.ib.qualifyContracts(self.contract)
                    
                    # Request market depth
                    self.ticker = self.ib.reqMktDepth(
                        self.contract, 
                        numRows=num_rows, 
                        isSmartDepth=False
                    )
                    
                    # Set up callback
                    self.ticker.updateEvent += self._on_ticker_update
                    
                    # If detecting hidden orders, also get time & sales
                    if self.detect_hidden_orders:
                        self.ticker.tickByTickAllLast += self._on_trade
                        self.ib.reqTickByTickData(
                            self.contract,
                            'AllLast',  # All trades
                            0,
                            False
                        )
                    
                    logger.info(f"✅ Subscribed to Level 2 on {exchange}")
                    self.exchange = exchange
                    return True
                    
                except Exception as e:
                    logger.warning(f"Exchange {exchange} failed: {e}")
                    continue
            
            logger.error("❌ Failed to subscribe on any exchange")
            return False
            
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            return False
    
    def _on_trade(self, ticker, tick):
        """Handle trade tick (time & sales) for hidden order detection"""
        if not self.detect_hidden_orders or not self.hidden_detector:
            return
        
        try:
            # Determine trade side based on price vs last
            side = 'buy'  # Default
            if self.last_price is not None:
                if tick.price > self.last_price:
                    side = 'buy'
                elif tick.price < self.last_price:
                    side = 'sell'
            
            self.last_price = tick.price
            self.last_trade_time = tick.time
            
            # Add to hidden detector
            with self.lock:
                self.hidden_detector.add_trade(
                    price=tick.price,
                    size=tick.size,
                    side=side,
                    timestamp=tick.time
                )
                self.hidden_detector.add_price_update(
                    price=tick.price,
                    timestamp=tick.time
                )
            
        except Exception as e:
            logger.error(f"Trade processing error: {e}")
    
    def _on_ticker_update(self, ticker):
        """Handle ticker updates - THREAD SAFE"""
        timestamp = datetime.now(timezone.utc)
        
        with self.lock:
            # Update order book
            if hasattr(ticker, 'domBids') and hasattr(ticker, 'domAsks'):
                self.current_order_book['bids'] = {}
                self.current_order_book['asks'] = {}
                
                # Aggregate bids
                for level in ticker.domBids:
                    if level.price > 0 and level.size > 0:
                        price = round(level.price, 2)
                        if price in self.current_order_book['bids']:
                            self.current_order_book['bids'][price] += level.size
                        else:
                            self.current_order_book['bids'][price] = level.size
                
                # Aggregate asks
                for level in ticker.domAsks:
                    if level.price > 0 and level.size > 0:
                        price = round(level.price, 2)
                        if price in self.current_order_book['asks']:
                            self.current_order_book['asks'][price] += level.size
                        else:
                            self.current_order_book['asks'][price] = level.size
                
                # Create snapshot
                if self.current_order_book['bids'] and self.current_order_book['asks']:
                    bids = sorted(self.current_order_book['bids'].items(), reverse=True)[:20]
                    asks = sorted(self.current_order_book['asks'].items())[:20]
                    
                    snapshot = {
                        'timestamp': timestamp,
                        'bids': dict(bids),
                        'asks': dict(asks),
                    }
                    
                    self.order_book_history.append(snapshot)
                    
                    # Update hidden detector
                    if self.hidden_detector:
                        self.hidden_detector.add_order_book_snapshot(bids, asks, timestamp)
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(snapshot)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
    
    def get_current_snapshot(self):
        """Get current order book snapshot - THREAD SAFE"""
        with self.lock:
            if not self.current_order_book['bids'] or not self.current_order_book['asks']:
                return None
            
            bids = sorted(self.current_order_book['bids'].items(), reverse=True)[:20]
            asks = sorted(self.current_order_book['asks'].items())[:20]
            
            if not bids or not asks:
                return None
            
            session = self.get_market_session()
            
            return {
                'timestamp': datetime.now(timezone.utc),
                'session': session,
                'bids': bids,
                'asks': asks,
                'best_bid': bids[0][0],
                'best_ask': asks[0][0],
                'spread': asks[0][0] - bids[0][0],
                'bid_count': len(bids),
                'ask_count': len(asks)
            }
    
    def calculate_microprice(self, best_bid, best_ask, bid_size, ask_size):
        """Calculate microprice"""
        total_size = bid_size + ask_size
        if total_size == 0:
            return (best_bid + best_ask) / 2
        return (best_bid * ask_size + best_ask * bid_size) / total_size
    
    def calculate_queue_imbalance(self, bids, asks, levels=5):
        """Calculate queue position imbalance"""
        if not bids or not asks:
            return 0
        
        session = self.get_market_session()
        if session in ["PREMARKET", "AFTERHOURS"]:
            levels = min(levels, min(len(bids), len(asks)))
        
        bid_pressure = sum(size / (i + 1) for i, (_, size) in enumerate(bids[:levels]))
        ask_pressure = sum(size / (i + 1) for i, (_, size) in enumerate(asks[:levels]))
        
        total_pressure = bid_pressure + ask_pressure
        if total_pressure == 0:
            return 0
        
        return (bid_pressure - ask_pressure) / total_pressure
    
    def get_order_book_features(self):
        """Extract comprehensive features from order book"""
        snapshot = self.get_current_snapshot()
        if not snapshot:
            return None
        
        bids = snapshot['bids']
        asks = snapshot['asks']
        session = snapshot['session']
        
        if not bids or not asks:
            return None
        
        # Basic metrics
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        best_bid_size = bids[0][1]
        best_ask_size = asks[0][1]
        
        # Microprice
        microprice = self.calculate_microprice(best_bid, best_ask, best_bid_size, best_ask_size)
        
        # Depth calculations
        depth_5 = min(5, len(bids), len(asks))
        depth_10 = min(10, len(bids), len(asks))
        
        # Volume calculations
        bid_volume_5 = sum(size for _, size in bids[:depth_5])
        ask_volume_5 = sum(size for _, size in asks[:depth_5])
        
        # Weighted imbalance
        weighted_bid = sum(size * (depth_5+1-i) for i, (_, size) in enumerate(bids[:depth_5]))
        weighted_ask = sum(size * (depth_5+1-i) for i, (_, size) in enumerate(asks[:depth_5]))
        
        # Queue imbalance
        queue_imbalance = self.calculate_queue_imbalance(bids, asks, levels=depth_5)
        
        features = {
            'timestamp': snapshot['timestamp'],
            'session': session,
            'microprice': microprice,
            'mid_price': (best_bid + best_ask) / 2,
            'spread': snapshot['spread'],
            'spread_bps': (snapshot['spread'] / microprice) * 10000,
            
            # Volume features
            'total_bid_volume_5': bid_volume_5,
            'total_ask_volume_5': ask_volume_5,
            'volume_imbalance': (bid_volume_5 - ask_volume_5) / (bid_volume_5 + ask_volume_5) if (bid_volume_5 + ask_volume_5) > 0 else 0,
            
            # Weighted features
            'weighted_bid_pressure': weighted_bid,
            'weighted_ask_pressure': weighted_ask,
            'weighted_imbalance': (weighted_bid - weighted_ask) / (weighted_bid + weighted_ask) if (weighted_bid + weighted_ask) > 0 else 0,
            
            # Queue position
            'queue_imbalance': queue_imbalance,
            
            # Depth features
            'bid_depth_10': sum(size for _, size in bids[:depth_10]),
            'ask_depth_10': sum(size for _, size in asks[:depth_10]),
            
            # Level counts
            'bid_levels': len(bids),
            'ask_levels': len(asks),
            
            # Level sizes
            'best_bid': best_bid,
            'best_ask': best_ask,
            'best_bid_size': best_bid_size,
            'best_ask_size': best_ask_size,
            'size_imbalance_top': (best_bid_size - best_ask_size) / (best_bid_size + best_ask_size) if (best_bid_size + best_ask_size) > 0 else 0,
        }
        
        # Add individual levels
        for i in range(min(5, len(bids))):
            features[f'bid_price_{i}'] = bids[i][0]
            features[f'bid_size_{i}'] = bids[i][1]
        
        for i in range(min(5, len(asks))):
            features[f'ask_price_{i}'] = asks[i][0]
            features[f'ask_size_{i}'] = asks[i][1]
        
        # Session warnings
        if session == "PREMARKET":
            features['session_warning'] = "Premarket - Lower liquidity"
        elif session == "AFTERHOURS":
            features['session_warning'] = "After hours - Limited depth"
        elif session == "CLOSED":
            features['session_warning'] = "Market closed"
        else:
            features['session_warning'] = None
        
        return features
    
    def get_trading_signal(self):
        """Get current trading signal with all analysis"""
        features = self.get_order_book_features()
        if not features:
            return None
        
        # Add features to signal generator
        self.signal_generator.add_features(features)
        
        # Get hidden order analysis if enabled
        hidden_results = None
        if self.hidden_detector:
            hidden_results = self.hidden_detector.detect_hidden_orders()
        
        # Generate signal
        signal = self.signal_generator.generate_signal(features, hidden_results)
        
        # Add additional context
        signal['features'] = features
        signal['hidden_orders'] = hidden_results
        
        return signal
    
    def register_callback(self, callback):
        """Register callback for order book updates"""
        self.callbacks.append(callback)
    
    def start(self, duration_seconds=None):
        """
        Start the system
        
        Args:
            duration_seconds: How long to run (None = indefinitely)
        """
        logger.info(f"🚀 Starting Unified Level 2 System for {self.symbol}")
        logger.info(f"⚙️  Extended hours: {self.use_extended_hours}")
        logger.info(f"⚙️  Hidden orders: {self.detect_hidden_orders}")
        
        if not self.connect():
            logger.error("Failed to connect")
            return False
        
        if not self.subscribe_market_depth():
            logger.error("Failed to subscribe to market depth")
            return False
        
        logger.info("✅ System started successfully")
        logger.info("=" * 60)
        
        # Setup status update callback
        def print_status(snapshot):
            features = self.get_order_book_features()
            signal = self.get_trading_signal()
            
            if features and signal:
                # Session icon
                session_icons = {
                    "PREMARKET": "🌅",
                    "REGULAR": "☀️",
                    "AFTERHOURS": "🌆",
                    "CLOSED": "🌙"
                }
                session_icon = session_icons.get(features['session'], "❓")
                
                # Signal color
                signal_icons = {
                    'BUY': '🟢',
                    'SELL': '🔴',
                    'NEUTRAL': '⚪'
                }
                signal_icon = signal_icons.get(signal['signal'], '⚪')
                
                logger.info(f"\n{'='*60}")
                logger.info(f"{session_icon} {features['session']} | {features['timestamp'].strftime('%H:%M:%S')}")
                logger.info(f"💰 Price: ${features['microprice']:.2f} | Spread: {features['spread_bps']:.1f} bps")
                logger.info(f"📊 Queue Imbalance: {features['queue_imbalance']:.3f}")
                logger.info(f"📊 Weighted Imbalance: {features['weighted_imbalance']:.3f}")
                logger.info(f"{signal_icon} SIGNAL: {signal['signal']} ({signal['confidence']:.1f}% confidence)")
                
                if signal['reasons']:
                    logger.info("📋 Reasons:")
                    for reason in signal['reasons']:
                        logger.info(f"   • {reason}")
                
                if signal.get('hidden_orders'):
                    ho = signal['hidden_orders']
                    if ho.get('hidden_buyer'):
                        logger.info(f"🔍 Hidden BUYER detected ({ho['hidden_buyer']['strength']})")
                    if ho.get('hidden_seller'):
                        logger.info(f"🔍 Hidden SELLER detected ({ho['hidden_seller']['strength']})")
                    if ho.get('icebergs'):
                        for ice in ho['icebergs'][:2]:
                            logger.info(f"🧊 Iceberg {ice['side']} at ${ice['price']:.2f}")
                
                if features.get('session_warning'):
                    logger.info(f"⚠️  {features['session_warning']}")
        
        self.register_callback(print_status)
        
        # Run for specified duration
        if duration_seconds:
            logger.info(f"Running for {duration_seconds} seconds...")
            start_time = time_module.time()
            while time_module.time() - start_time < duration_seconds:
                self.ib.sleep(1)
        else:
            logger.info("Running indefinitely (Ctrl+C to stop)...")
            try:
                while True:
                    self.ib.sleep(1)
            except KeyboardInterrupt:
                logger.info("\n⏹️  Stopping...")
        
        self.disconnect()
        return True
    
    def disconnect(self):
        """Disconnect from IBKR"""
        try:
            self.is_connected = False
            self.ib.disconnect()
            logger.info("👋 Disconnected from IBKR")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Get symbol from command line or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    # Create unified system with all features enabled
    system = UnifiedLevel2System(
        symbol=symbol,
        use_extended_hours=True,      # Enable premarket/afterhours
        detect_hidden_orders=True,    # Enable hidden order detection
        port=7497                      # TWS paper trading
    )
    
    # Start the system
    system.start(duration_seconds=120)  # Run for 2 minutes
