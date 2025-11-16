"""
UNIFIED LEVEL 2 DASHBOARD - ALL FEATURES COMBINED
==================================================

This dashboard combines ALL visualization features from:
- simple_visualizer_improved.py
- simple_visualizer_premarket.py
- simple_visualizer_with_hidden_orders.py

Features:
✅ Real-time order book visualization
✅ Liquidity heatmap
✅ Signal display with confidence
✅ Hidden order detection indicators
✅ Support/resistance levels
✅ Spread and imbalance charts
✅ Time & Sales (if enabled)
✅ Market session indicator
✅ Iceberg order alerts
✅ Price history chart
✅ Volume pressure gauges

Usage:
    python unified_dashboard.py AAPL
    
    Then open browser to: http://127.0.0.1:8050
"""

from level2_unified_system import UnifiedLevel2System
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timezone
from collections import deque
import threading
import time
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, update_title=None)
app.title = "Unified Level 2 Dashboard"

# Global data storage (thread-safe access via locks)
data_lock = threading.Lock()
data_store = {
    'timestamps': deque(maxlen=200),
    'prices': deque(maxlen=200),
    'imbalances': deque(maxlen=200),
    'spreads': deque(maxlen=200),
    'signals': deque(maxlen=200),
    'signal_confidence': deque(maxlen=200),
    'current_snapshot': None,
    'current_signal': None,
    'current_features': None,
    'hidden_orders': None,
    'is_running': False,
    'error_message': None,
    'connection_status': 'disconnected',
    'current_session': 'UNKNOWN',
    'support_levels': [],
    'resistance_levels': [],
}

system = None
data_thread = None


def create_layout(default_symbol='AAPL'):
    """Create dashboard layout with default symbol"""
    return html.Div([
    # Header
    html.Div([
        html.H1("🚀 Unified Level 2 Trading Dashboard", 
               style={'display': 'inline-block', 'margin-right': '30px'}),
        html.Div([
            html.Label("Symbol: ", style={'margin-right': '10px', 'font-weight': 'bold'}),
            dcc.Input(id='symbol-input', type='text', value=default_symbol, 
                     style={'width': '100px', 'margin-right': '10px', 'padding': '5px'}),
            
            html.Label("Exchange: ", style={'margin-right': '10px', 'margin-left': '20px', 'font-weight': 'bold'}),
            dcc.Dropdown(
                id='exchange-input',
                options=[
                    {'label': 'SMART (Auto)', 'value': 'SMART'},
                    {'label': 'ISLAND', 'value': 'ISLAND'},
                    {'label': 'ARCA', 'value': 'ARCA'},
                    {'label': 'EDGEA', 'value': 'EDGEA'},
                    {'label': 'IEX', 'value': 'IEX'},
                ],
                value='SMART',
                style={'width': '150px', 'display': 'inline-block', 'margin-right': '20px'}
            ),
            
            html.Button('▶ Start', id='start-button', n_clicks=0, 
                       style={'background-color': '#4CAF50', 'color': 'white', 
                             'border': 'none', 'padding': '8px 16px', 'margin-right': '10px',
                             'cursor': 'pointer', 'border-radius': '4px'}),
            html.Button('⏸ Stop', id='stop-button', n_clicks=0,
                       style={'background-color': '#f44336', 'color': 'white',
                             'border': 'none', 'padding': '8px 16px',
                             'cursor': 'pointer', 'border-radius': '4px'}),
        ], style={'display': 'inline-block'}),
    ], style={'background-color': '#1e1e1e', 'padding': '20px', 'color': 'white'}),
    
    # Status Bar
    html.Div([
        html.Div(id='connection-status', style={'display': 'inline-block', 'margin-right': '30px'}),
        html.Div(id='session-indicator', style={'display': 'inline-block', 'margin-right': '30px'}),
        html.Div(id='status-display', style={'display': 'inline-block'}),
        html.Div(id='error-display', style={'display': 'inline-block', 'margin-left': '30px', 'color': '#f44336'}),
    ], style={'background-color': '#2e2e2e', 'padding': '10px', 'color': 'white'}),
    
    # Configuration Row
    html.Div([
        html.Div([
            dcc.Checklist(
                id='feature-toggles',
                options=[
                    {'label': ' Extended Hours', 'value': 'extended'},
                    {'label': ' Hidden Orders', 'value': 'hidden'},
                ],
                value=['extended', 'hidden'],
                inline=True,
                style={'color': 'white'}
            )
        ], style={'display': 'inline-block', 'margin-right': '30px'}),
    ], style={'background-color': '#2e2e2e', 'padding': '10px', 'border-top': '1px solid #444'}),
    
    # Main Content - 3 Column Layout
    html.Div([
        # Left Column - Signal & Metrics
        html.Div([
            # Signal Card
            html.Div([
                html.H3("🎯 Trading Signal", style={'margin-bottom': '15px'}),
                html.Div(id='signal-card'),
            ], style={'background-color': '#2e2e2e', 'padding': '25px', 
                     'border-radius': '10px', 'margin-bottom': '20px', 'min-height': '280px'}),
            
            # Hidden Orders Card
            html.Div([
                html.H3("🔍 Hidden Order Detection", style={'margin-bottom': '15px'}),
                html.Div(id='hidden-orders-card'),
            ], style={'background-color': '#2e2e2e', 'padding': '25px', 
                     'border-radius': '10px', 'margin-bottom': '20px', 'min-height': '200px'}),
            
            # Support/Resistance Levels
            html.Div([
                html.H3("📊 Key Levels", style={'margin-bottom': '15px'}),
                html.Div(id='levels-card'),
            ], style={'background-color': '#2e2e2e', 'padding': '25px', 
                     'border-radius': '10px', 'min-height': '200px'}),
        ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '10px'}),
        
        # Middle Column - Order Book
        html.Div([
            html.Div([
                html.H3("📖 Order Book", style={'margin-bottom': '15px'}),
                dcc.Graph(id='order-book-graph', style={'height': '700px'}),
            ], style={'background-color': '#2e2e2e', 'padding': '25px', 
                     'border-radius': '10px'}),
        ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '10px'}),
        
        # Right Column - Charts
        html.Div([
            # Price & Imbalance Chart
            html.Div([
                html.H3("📈 Price & Queue Imbalance", style={'margin-bottom': '15px'}),
                dcc.Graph(id='price-imbalance-graph', style={'height': '320px'}),
            ], style={'background-color': '#2e2e2e', 'padding': '25px', 
                     'border-radius': '10px', 'margin-bottom': '20px'}),
            
            # Spread Chart
            html.Div([
                html.H3("📊 Spread Analysis", style={'margin-bottom': '15px'}),
                dcc.Graph(id='spread-graph', style={'height': '320px'}),
            ], style={'background-color': '#2e2e2e', 'padding': '25px', 
                     'border-radius': '10px'}),
        ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '10px'}),
    ], style={'margin-top': '20px'}),
    
    # Auto-update interval
    dcc.Interval(
        id='interval-component',
        interval=500,  # Update every 500ms
        n_intervals=0
    ),
    
], style={'background-color': '#1e1e1e', 'min-height': '100vh', 'color': 'white', 'font-family': 'Arial'})


# Initialize with default layout
app.layout = create_layout()


# Callback for Start button
@app.callback(
    Output('start-button', 'disabled'),
    Output('stop-button', 'disabled'),
    Input('start-button', 'n_clicks'),
    Input('stop-button', 'n_clicks'),
    State('symbol-input', 'value'),
    State('exchange-input', 'value'),
    State('feature-toggles', 'value'),
    prevent_initial_call=True
)
def handle_start_stop(start_clicks, stop_clicks, symbol, exchange, features):
    global system, data_thread
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, True
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'start-button':
        # Start the system
        try:
            with data_lock:
                data_store['is_running'] = True
                data_store['error_message'] = None
                data_store['connection_status'] = 'connecting'
            
            use_extended = 'extended' in features
            detect_hidden = 'hidden' in features
            
            logger.info(f"Starting system for {symbol} on {exchange}")
            logger.info(f"Extended hours: {use_extended}, Hidden orders: {detect_hidden}")
            
            system = UnifiedLevel2System(
                symbol=symbol,
                exchange=exchange,
                use_extended_hours=use_extended,
                detect_hidden_orders=detect_hidden,
                port=7497
            )
            
            # Register callback to update data store
            def update_data(snapshot):
                try:
                    features = system.get_order_book_features()
                    signal = system.get_trading_signal()
                    
                    if features and signal:
                        with data_lock:
                            timestamp = features['timestamp']
                            data_store['timestamps'].append(timestamp)
                            data_store['prices'].append(features['microprice'])
                            data_store['imbalances'].append(features.get('queue_imbalance', 0))
                            data_store['spreads'].append(features.get('spread_bps', 0))
                            
                            # Convert signal to numeric for plotting
                            signal_value = 1 if signal['signal'] == 'BUY' else (-1 if signal['signal'] == 'SELL' else 0)
                            data_store['signals'].append(signal_value)
                            data_store['signal_confidence'].append(signal['confidence'])
                            
                            data_store['current_snapshot'] = snapshot
                            data_store['current_signal'] = signal
                            data_store['current_features'] = features
                            data_store['hidden_orders'] = signal.get('hidden_orders')
                            data_store['current_session'] = features.get('session', 'UNKNOWN')
                            
                            # Get support/resistance
                            if system.signal_generator:
                                support, resistance = system.signal_generator.find_support_resistance()
                                data_store['support_levels'] = support
                                data_store['resistance_levels'] = resistance
                            
                            data_store['connection_status'] = 'connected'
                except Exception as e:
                    logger.error(f"Error in update callback: {e}")
            
            system.register_callback(update_data)
            
            # Start system in background thread
            def run_system():
                try:
                    if system.connect():
                        system.subscribe_market_depth()
                        # Run indefinitely
                        while data_store['is_running']:
                            system.ib.sleep(0.1)
                except Exception as e:
                    logger.error(f"System error: {e}")
                    with data_lock:
                        data_store['error_message'] = str(e)
                        data_store['connection_status'] = 'error'
            
            data_thread = threading.Thread(target=run_system, daemon=True)
            data_thread.start()
            
            return True, False  # Disable start, enable stop
            
        except Exception as e:
            logger.error(f"Failed to start: {e}")
            with data_lock:
                data_store['error_message'] = str(e)
                data_store['is_running'] = False
            return False, True
    
    elif button_id == 'stop-button':
        # Stop the system
        with data_lock:
            data_store['is_running'] = False
            data_store['connection_status'] = 'disconnected'
        
        if system:
            try:
                system.disconnect()
            except:
                pass
        
        return False, True  # Enable start, disable stop
    
    return False, True


# Update connection status
@app.callback(
    Output('connection-status', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_connection_status(n):
    with data_lock:
        status = data_store['connection_status']
    
    status_colors = {
        'disconnected': '#888',
        'connecting': '#FFA500',
        'connected': '#4CAF50',
        'error': '#f44336'
    }
    
    status_icons = {
        'disconnected': '⚫',
        'connecting': '🟡',
        'connected': '🟢',
        'error': '🔴'
    }
    
    return html.Div([
        html.Span(status_icons.get(status, '⚫'), 
                 style={'font-size': '20px', 'margin-right': '10px'}),
        html.Span(status.upper(), 
                 style={'color': status_colors.get(status, '#888'), 'font-weight': 'bold'})
    ])


# Update session indicator
@app.callback(
    Output('session-indicator', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_session_indicator(n):
    with data_lock:
        session = data_store['current_session']
    
    session_icons = {
        'PREMARKET': '🌅',
        'REGULAR': '☀️',
        'AFTERHOURS': '🌆',
        'CLOSED': '🌙',
        'UNKNOWN': '❓'
    }
    
    session_colors = {
        'PREMARKET': '#FFA500',
        'REGULAR': '#4CAF50',
        'AFTERHOURS': '#9C27B0',
        'CLOSED': '#888',
        'UNKNOWN': '#888'
    }
    
    return html.Div([
        html.Span(session_icons.get(session, '❓'), 
                 style={'font-size': '20px', 'margin-right': '10px'}),
        html.Span(session, 
                 style={'color': session_colors.get(session, '#888'), 'font-weight': 'bold'})
    ])


# Update status display
@app.callback(
    Output('status-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_status_display(n):
    with data_lock:
        features = data_store['current_features']
        is_running = data_store['is_running']
    
    if not is_running or not features:
        return "Not running"
    
    return html.Div([
        html.Span(f"Price: ${features['microprice']:.2f} | ", 
                 style={'margin-right': '15px'}),
        html.Span(f"Spread: {features['spread_bps']:.1f} bps | ", 
                 style={'margin-right': '15px'}),
        html.Span(f"Queue: {features['queue_imbalance']:.3f}", 
                 style={'margin-right': '15px'}),
    ])


# Update error display
@app.callback(
    Output('error-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_error_display(n):
    with data_lock:
        error = data_store['error_message']
    
    if error:
        return f"⚠️ Error: {error}"
    return ""


# Update signal card
@app.callback(
    Output('signal-card', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_signal_card(n):
    with data_lock:
        signal = data_store['current_signal']
        features = data_store['current_features']
    
    if not signal:
        return html.Div("Waiting for data...", style={'color': '#888'})
    
    # Signal colors and icons
    signal_colors = {
        'BUY': '#4CAF50',
        'SELL': '#f44336',
        'NEUTRAL': '#888'
    }
    
    signal_icons = {
        'BUY': '🟢',
        'SELL': '🔴',
        'NEUTRAL': '⚪'
    }
    
    signal_type = signal['signal']
    confidence = signal['confidence']
    
    return html.Div([
        # Signal indicator
        html.Div([
            html.Span(signal_icons[signal_type], style={'font-size': '50px'}),
            html.Div([
                html.H2(signal_type, 
                       style={'color': signal_colors[signal_type], 'margin': '5px 0'}),
                html.P(f"{confidence:.1f}% Confidence", 
                      style={'font-size': '18px', 'margin': '0', 'color': '#ccc'}),
            ], style={'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': '20px'}),
        ], style={'text-align': 'center', 'margin-bottom': '20px'}),
        
        # Confidence bar
        html.Div([
            html.Div(style={
                'width': f'{confidence}%',
                'height': '20px',
                'background-color': signal_colors[signal_type],
                'border-radius': '10px',
                'transition': 'width 0.3s ease'
            })
        ], style={
            'background-color': '#1e1e1e',
            'border-radius': '10px',
            'margin-bottom': '20px'
        }),
        
        # Reasons
        html.Div([
            html.H4("Reasons:", style={'margin-bottom': '10px', 'color': '#ccc'}),
            html.Ul([
                html.Li(reason, style={'margin-bottom': '5px'}) 
                for reason in signal.get('reasons', [])
            ], style={'padding-left': '20px'})
        ]) if signal.get('reasons') else None,
        
        # Current metrics
        html.Div([
            html.Hr(style={'border-color': '#444', 'margin': '20px 0'}),
            html.Div([
                html.Div([
                    html.Strong("Queue Imbalance:"),
                    html.Span(f" {features['queue_imbalance']:.3f}" if features else " --")
                ], style={'margin-bottom': '8px'}),
                html.Div([
                    html.Strong("Weighted Imbalance:"),
                    html.Span(f" {features['weighted_imbalance']:.3f}" if features else " --")
                ], style={'margin-bottom': '8px'}),
                html.Div([
                    html.Strong("Spread:"),
                    html.Span(f" {features['spread_bps']:.1f} bps" if features else " --")
                ])
            ])
        ]) if features else None
    ])


# Update hidden orders card
@app.callback(
    Output('hidden-orders-card', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_hidden_orders_card(n):
    with data_lock:
        hidden = data_store['hidden_orders']
    
    if not hidden:
        return html.Div("Hidden order detection disabled or no data", 
                       style={'color': '#888'})
    
    elements = []
    
    # Hidden buyer
    if hidden.get('hidden_buyer'):
        hb = hidden['hidden_buyer']
        elements.append(html.Div([
            html.Div([
                html.Span("🔍 ", style={'font-size': '24px'}),
                html.Strong("HIDDEN BUYER", style={'color': '#4CAF50'}),
                html.Span(f" ({hb['strength']})", style={'color': '#ccc', 'margin-left': '10px'})
            ], style={'margin-bottom': '8px'}),
            html.Div([
                html.Span(f"Sell Volume: {hb.get('sell_volume', 0):.0f}"),
                html.Span(f" | Price Change: {hb.get('price_change', 0)*100:.2f}%", 
                         style={'margin-left': '10px'})
            ], style={'font-size': '14px', 'color': '#ccc'})
        ], style={'margin-bottom': '15px', 'padding': '10px', 
                 'background-color': 'rgba(76, 175, 80, 0.1)', 'border-radius': '5px'}))
    
    # Hidden seller
    if hidden.get('hidden_seller'):
        hs = hidden['hidden_seller']
        elements.append(html.Div([
            html.Div([
                html.Span("🔍 ", style={'font-size': '24px'}),
                html.Strong("HIDDEN SELLER", style={'color': '#f44336'}),
                html.Span(f" ({hs['strength']})", style={'color': '#ccc', 'margin-left': '10px'})
            ], style={'margin-bottom': '8px'}),
            html.Div([
                html.Span(f"Buy Volume: {hs.get('buy_volume', 0):.0f}"),
                html.Span(f" | Price Change: {hs.get('price_change', 0)*100:.2f}%", 
                         style={'margin-left': '10px'})
            ], style={'font-size': '14px', 'color': '#ccc'})
        ], style={'margin-bottom': '15px', 'padding': '10px', 
                 'background-color': 'rgba(244, 67, 54, 0.1)', 'border-radius': '5px'}))
    
    # Icebergs
    icebergs = hidden.get('icebergs', [])
    if icebergs:
        for ice in icebergs[:3]:  # Show top 3
            color = '#4CAF50' if ice['side'] == 'bid' else '#f44336'
            elements.append(html.Div([
                html.Div([
                    html.Span("🧊 ", style={'font-size': '20px'}),
                    html.Strong(f"ICEBERG {ice['side'].upper()}", style={'color': color}),
                ], style={'margin-bottom': '5px'}),
                html.Div([
                    html.Span(f"Price: ${ice['price']:.2f}"),
                    html.Span(f" | Avg Size: {ice['avg_size']:.0f}", style={'margin-left': '10px'}),
                    html.Span(f" | Refills: {ice['refills']}", style={'margin-left': '10px'})
                ], style={'font-size': '13px', 'color': '#ccc'})
            ], style={'margin-bottom': '10px', 'padding': '8px', 
                     'background-color': 'rgba(156, 39, 176, 0.1)', 'border-radius': '5px'}))
    
    if not elements:
        return html.Div("No hidden orders detected", style={'color': '#888'})
    
    return html.Div(elements)


# Update levels card
@app.callback(
    Output('levels-card', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_levels_card(n):
    with data_lock:
        support = data_store['support_levels']
        resistance = data_store['resistance_levels']
        features = data_store['current_features']
    
    current_price = features['microprice'] if features else None
    
    elements = []
    
    # Resistance levels
    if resistance:
        elements.append(html.Div([
            html.H4("🔴 Resistance", style={'color': '#f44336', 'margin-bottom': '10px'}),
            html.Ul([
                html.Li(f"${level:.2f}" + 
                       (f" ({abs(level-current_price)/current_price*100:.2f}% away)" 
                        if current_price else ""),
                       style={'margin-bottom': '5px'})
                for level in sorted(resistance, reverse=True)[:5]
            ], style={'padding-left': '20px'})
        ], style={'margin-bottom': '20px'}))
    
    # Current price
    if current_price:
        elements.append(html.Div([
            html.H4("💰 Current", style={'color': '#FFA500', 'margin-bottom': '5px'}),
            html.P(f"${current_price:.2f}", 
                  style={'font-size': '20px', 'font-weight': 'bold', 'margin': '5px 0 20px 0'})
        ]))
    
    # Support levels
    if support:
        elements.append(html.Div([
            html.H4("🟢 Support", style={'color': '#4CAF50', 'margin-bottom': '10px'}),
            html.Ul([
                html.Li(f"${level:.2f}" + 
                       (f" ({abs(level-current_price)/current_price*100:.2f}% away)" 
                        if current_price else ""),
                       style={'margin-bottom': '5px'})
                for level in sorted(support, reverse=True)[:5]
            ], style={'padding-left': '20px'})
        ]))
    
    if not elements:
        return html.Div("Calculating levels...", style={'color': '#888'})
    
    return html.Div(elements)


# Update order book graph
@app.callback(
    Output('order-book-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_order_book(n):
    with data_lock:
        snapshot = data_store['current_snapshot']
    
    if not snapshot:
        # Empty plot
        fig = go.Figure()
        fig.update_layout(
            title="Waiting for data...",
            template='plotly_dark',
            paper_bgcolor='#2e2e2e',
            plot_bgcolor='#2e2e2e',
        )
        return fig
    
    bids = snapshot['bids']
    asks = snapshot['asks']
    
    # Convert to lists for plotting
    bid_prices = [p for p, _ in list(bids.items())] if isinstance(bids, dict) else [p for p, _ in bids]
    bid_sizes = [s for _, s in list(bids.items())] if isinstance(bids, dict) else [s for _, s in bids]
    ask_prices = [p for p, _ in list(asks.items())] if isinstance(asks, dict) else [p for p, _ in asks]
    ask_sizes = [s for _, s in list(asks.items())] if isinstance(asks, dict) else [s for _, s in asks]
    
    # Create figure with liquidity heatmap style
    fig = go.Figure()
    
    # Bids (green bars going left)
    fig.add_trace(go.Bar(
        y=bid_prices,
        x=[-s for s in bid_sizes],  # Negative for left side
        orientation='h',
        name='Bids',
        marker=dict(
            color=bid_sizes,
            colorscale=[[0, '#1e4620'], [1, '#4CAF50']],
            showscale=False,
            line=dict(color='#4CAF50', width=1)
        ),
        text=[f'{s:.0f}' for s in bid_sizes],
        textposition='inside',
        hovertemplate='Price: $%{y:.2f}<br>Size: %{text}<extra></extra>'
    ))
    
    # Asks (red bars going right)
    fig.add_trace(go.Bar(
        y=ask_prices,
        x=ask_sizes,
        orientation='h',
        name='Asks',
        marker=dict(
            color=ask_sizes,
            colorscale=[[0, '#4a1e1e'], [1, '#f44336']],
            showscale=False,
            line=dict(color='#f44336', width=1)
        ),
        text=[f'{s:.0f}' for s in ask_sizes],
        textposition='inside',
        hovertemplate='Price: $%{y:.2f}<br>Size: %{text}<extra></extra>'
    ))
    
    # Add mid-price line
    if bid_prices and ask_prices:
        mid_price = (bid_prices[0] + ask_prices[0]) / 2
        max_size = max(max(bid_sizes, default=0), max(ask_sizes, default=0))
        fig.add_shape(
            type='line',
            x0=-max_size, x1=max_size,
            y0=mid_price, y1=mid_price,
            line=dict(color='#FFA500', width=2, dash='dash')
        )
    
    fig.update_layout(
        title=f"Order Book Depth - Spread: ${snapshot.get('spread', 0):.4f}",
        xaxis_title="Size (shares)",
        yaxis_title="Price ($)",
        template='plotly_dark',
        paper_bgcolor='#2e2e2e',
        plot_bgcolor='#2e2e2e',
        showlegend=True,
        hovermode='closest',
        bargap=0.1,
        font=dict(size=12)
    )
    
    return fig


# Update price and imbalance graph
@app.callback(
    Output('price-imbalance-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_price_imbalance(n):
    with data_lock:
        timestamps = list(data_store['timestamps'])
        prices = list(data_store['prices'])
        imbalances = list(data_store['imbalances'])
        signals = list(data_store['signals'])
    
    if not timestamps:
        fig = go.Figure()
        fig.update_layout(
            title="Waiting for data...",
            template='plotly_dark',
            paper_bgcolor='#2e2e2e',
            plot_bgcolor='#2e2e2e',
        )
        return fig
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
        subplot_titles=('Price', 'Queue Imbalance')
    )
    
    # Price line
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=prices,
            mode='lines',
            name='Microprice',
            line=dict(color='#FFA500', width=2),
            hovertemplate='%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add signal markers
    buy_times = [timestamps[i] for i, s in enumerate(signals) if s == 1]
    buy_prices = [prices[i] for i, s in enumerate(signals) if s == 1]
    sell_times = [timestamps[i] for i, s in enumerate(signals) if s == -1]
    sell_prices = [prices[i] for i, s in enumerate(signals) if s == -1]
    
    if buy_times:
        fig.add_trace(
            go.Scatter(
                x=buy_times,
                y=buy_prices,
                mode='markers',
                name='BUY Signal',
                marker=dict(color='#4CAF50', size=12, symbol='triangle-up'),
                hovertemplate='BUY<extra></extra>'
            ),
            row=1, col=1
        )
    
    if sell_times:
        fig.add_trace(
            go.Scatter(
                x=sell_times,
                y=sell_prices,
                mode='markers',
                name='SELL Signal',
                marker=dict(color='#f44336', size=12, symbol='triangle-down'),
                hovertemplate='SELL<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Imbalance bars
    colors = ['#4CAF50' if i > 0 else '#f44336' for i in imbalances]
    fig.add_trace(
        go.Bar(
            x=timestamps,
            y=imbalances,
            name='Queue Imbalance',
            marker=dict(color=colors),
            hovertemplate='%{y:.3f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add zero line for imbalance
    fig.add_hline(y=0, line=dict(color='white', width=1, dash='dash'), row=2, col=1)
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#2e2e2e',
        plot_bgcolor='#2e2e2e',
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=50, r=20, t=40, b=40)
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Imbalance", row=2, col=1)
    
    return fig


# Update spread graph
@app.callback(
    Output('spread-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_spread_graph(n):
    with data_lock:
        timestamps = list(data_store['timestamps'])
        spreads = list(data_store['spreads'])
    
    if not timestamps:
        fig = go.Figure()
        fig.update_layout(
            title="Waiting for data...",
            template='plotly_dark',
            paper_bgcolor='#2e2e2e',
            plot_bgcolor='#2e2e2e',
        )
        return fig
    
    fig = go.Figure()
    
    # Spread area
    colors = ['#4CAF50' if s < 30 else ('#FFA500' if s < 50 else '#f44336') for s in spreads]
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=spreads,
        mode='lines',
        name='Spread (bps)',
        line=dict(color='#9C27B0', width=2),
        fill='tozeroy',
        fillcolor='rgba(156, 39, 176, 0.2)',
        hovertemplate='%{y:.1f} bps<extra></extra>'
    ))
    
    # Add threshold lines
    fig.add_hline(y=30, line=dict(color='#FFA500', width=1, dash='dash'), 
                  annotation_text="Wide")
    fig.add_hline(y=50, line=dict(color='#f44336', width=1, dash='dash'), 
                  annotation_text="Very Wide")
    
    fig.update_layout(
        title="Spread (basis points)",
        yaxis_title="Spread (bps)",
        template='plotly_dark',
        paper_bgcolor='#2e2e2e',
        plot_bgcolor='#2e2e2e',
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=50, r=20, t=40, b=40)
    )
    
    return fig


if __name__ == '__main__':
    import sys
    
    # Get symbol from command line
    default_symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    
    # Set layout with default symbol
    app.layout = create_layout(default_symbol)
    
    print("\n" + "="*60)
    print("🚀 UNIFIED LEVEL 2 DASHBOARD")
    print("="*60)
    print(f"\n📊 Default Symbol: {default_symbol}")
    print("\n🌐 Dashboard URL: http://127.0.0.1:8050")
    print("\n⚙️  Features:")
    print("   ✅ Real-time order book visualization")
    print("   ✅ Trading signals with confidence")
    print("   ✅ Hidden order detection")
    print("   ✅ Support/resistance levels")
    print("   ✅ Extended hours support")
    print("   ✅ Interactive charts")
    print("\n💡 Tip: You can change symbol and settings in the dashboard")
    print("\n" + "="*60)
    print("\nStarting dashboard...")
    print("Press Ctrl+C to stop\n")
    
    # Run the dashboard
    app.run(
        debug=False,
        host='127.0.0.1',
        port=8050
    )
