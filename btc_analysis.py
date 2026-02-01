"""
🚀 Quick Start Script - Bitcoin Technical Analysis
==================================================
A standalone script demonstrating OpenBB's capabilities
for Bitcoin analysis with professional charts.

Run: python btc_analysis.py
"""

import warnings
warnings.filterwarnings('ignore')

from openbb import obb
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.precision', 4)

print("=" * 60)
print("₿  BITCOIN TECHNICAL ANALYSIS DASHBOARD")
print("   Powered by OpenBB - Your Free Bloomberg Alternative")
print("=" * 60)

# Fetch BTC data
print("\n📊 Fetching Bitcoin data...")
btc = obb.crypto.price.historical(
    symbol="BTCUSD",
    provider="yfinance",
    start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
).to_df()

print(f"✅ Loaded {len(btc)} days of Bitcoin data")

# Calculate advanced indicators
print("🔧 Calculating technical indicators...")

# Moving Averages
btc['SMA_20'] = btc['close'].rolling(20).mean()
btc['SMA_50'] = btc['close'].rolling(50).mean()
btc['SMA_200'] = btc['close'].rolling(200).mean()

# Bollinger Bands
btc['BB_middle'] = btc['close'].rolling(20).mean()
btc['BB_std'] = btc['close'].rolling(20).std()
btc['BB_upper'] = btc['BB_middle'] + (btc['BB_std'] * 2)
btc['BB_lower'] = btc['BB_middle'] - (btc['BB_std'] * 2)
btc['BB_width'] = (btc['BB_upper'] - btc['BB_lower']) / btc['BB_middle']

# RSI
delta = btc['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
btc['RSI'] = 100 - (100 / (1 + rs))

# MACD
exp1 = btc['close'].ewm(span=12).mean()
exp2 = btc['close'].ewm(span=26).mean()
btc['MACD'] = exp1 - exp2
btc['MACD_signal'] = btc['MACD'].ewm(span=9).mean()
btc['MACD_hist'] = btc['MACD'] - btc['MACD_signal']

# ATR (Average True Range)
btc['TR'] = np.maximum(
    btc['high'] - btc['low'],
    np.maximum(
        abs(btc['high'] - btc['close'].shift()),
        abs(btc['low'] - btc['close'].shift())
    )
)
btc['ATR'] = btc['TR'].rolling(14).mean()

# Identify support/resistance levels using peaks
try:
    from scipy.signal import find_peaks
    peaks_high, _ = find_peaks(btc['high'], distance=20, prominence=btc['high'].std())
    peaks_low, _ = find_peaks(-btc['low'], distance=20, prominence=btc['low'].std())
    resistance_levels = btc['high'].iloc[peaks_high].nlargest(3).values
    support_levels = btc['low'].iloc[peaks_low].nsmallest(3).values
except ImportError:
    print("⚠️  scipy not installed - skipping support/resistance detection")
    resistance_levels = []
    support_levels = []

# Print analysis summary
print("\n" + "=" * 60)
print("📊 BITCOIN ANALYSIS SUMMARY")
print("=" * 60)

current_price = btc['close'].iloc[-1]
rsi_value = btc['RSI'].iloc[-1]
macd_bullish = btc['MACD'].iloc[-1] > btc['MACD_signal'].iloc[-1]

print(f"\n🎯 Current BTC Price: ${current_price:,.2f}")

# RSI interpretation
if rsi_value > 70:
    rsi_status = "(Overbought ⚠️)"
elif rsi_value < 30:
    rsi_status = "(Oversold 🔥)"
else:
    rsi_status = "(Neutral)"
print(f"📊 RSI (14): {rsi_value:.2f} {rsi_status}")

print(f"📈 MACD: {'🟢 Bullish' if macd_bullish else '🔴 Bearish'}")
print(f"💪 Volatility (BB Width): {btc['BB_width'].iloc[-1]:.4f}")
print(f"📏 ATR (14): ${btc['ATR'].iloc[-1]:,.2f}")

if len(resistance_levels) > 0:
    print(f"\n🔴 Resistance Levels: {', '.join([f'${x:,.0f}' for x in resistance_levels])}")
if len(support_levels) > 0:
    print(f"🟢 Support Levels: {', '.join([f'${x:,.0f}' for x in support_levels])}")

# Performance metrics
print(f"\n📈 Performance:")
year_return = ((current_price - btc['close'].iloc[0]) / btc['close'].iloc[0]) * 100
print(f"   1-Year Return: {year_return:+.2f}%")
print(f"   52-Week High: ${btc['high'].max():,.2f}")
print(f"   52-Week Low: ${btc['low'].min():,.2f}")

# Trading signals
print(f"\n🎯 Trading Signals:")
if btc['close'].iloc[-1] > btc['SMA_20'].iloc[-1]:
    print("   ✅ Price above SMA 20 (Bullish)")
else:
    print("   ❌ Price below SMA 20 (Bearish)")

if btc['close'].iloc[-1] > btc['SMA_50'].iloc[-1]:
    print("   ✅ Price above SMA 50 (Bullish)")
else:
    print("   ❌ Price below SMA 50 (Bearish)")

if not pd.isna(btc['SMA_200'].iloc[-1]):
    if btc['close'].iloc[-1] > btc['SMA_200'].iloc[-1]:
        print("   ✅ Price above SMA 200 (Bullish)")
    else:
        print("   ❌ Price below SMA 200 (Bearish)")

print("\n" + "=" * 60)
print("📊 Creating interactive dashboard...")
print("=" * 60)

# Create comprehensive chart
fig = make_subplots(
    rows=5, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
    subplot_titles=(
        'BTC Price Action with Bollinger Bands',
        'Volume',
        'RSI (Relative Strength Index)',
        'MACD',
        'ATR (Volatility)'
    )
)

# Row 1: Price + Bollinger Bands + Moving Averages
fig.add_trace(go.Candlestick(
    x=btc.index,
    open=btc['open'],
    high=btc['high'],
    low=btc['low'],
    close=btc['close'],
    name='BTC',
    increasing_line_color='#00ff41',
    decreasing_line_color='#ff4444'
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=btc.index, y=btc['SMA_20'],
    name='SMA 20', line=dict(color='cyan', width=1)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=btc.index, y=btc['SMA_50'],
    name='SMA 50', line=dict(color='yellow', width=1)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=btc.index, y=btc['SMA_200'],
    name='SMA 200', line=dict(color='red', width=2)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=btc.index, y=btc['BB_upper'],
    name='BB Upper', line=dict(color='gray', dash='dash', width=1)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=btc.index, y=btc['BB_lower'],
    name='BB Lower', line=dict(color='gray', dash='dash', width=1),
    fill='tonexty', fillcolor='rgba(128,128,128,0.1)'
), row=1, col=1)

# Add support/resistance lines
for level in resistance_levels:
    fig.add_hline(y=level, line_dash="dot", line_color="red", opacity=0.5, row=1, col=1)
for level in support_levels:
    fig.add_hline(y=level, line_dash="dot", line_color="green", opacity=0.5, row=1, col=1)

# Row 2: Volume
colors = ['#00ff41' if btc['close'].iloc[i] >= btc['open'].iloc[i] else '#ff4444' 
          for i in range(len(btc))]
fig.add_trace(go.Bar(
    x=btc.index, y=btc['volume'],
    name='Volume', marker_color=colors, opacity=0.7
), row=2, col=1)

# Row 3: RSI
fig.add_trace(go.Scatter(
    x=btc.index, y=btc['RSI'],
    name='RSI', line=dict(color='orange', width=2)
), row=3, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)

# Row 4: MACD
fig.add_trace(go.Scatter(
    x=btc.index, y=btc['MACD'],
    name='MACD', line=dict(color='blue', width=1.5)
), row=4, col=1)

fig.add_trace(go.Scatter(
    x=btc.index, y=btc['MACD_signal'],
    name='Signal', line=dict(color='red', width=1.5)
), row=4, col=1)

hist_colors = ['#00ff41' if val >= 0 else '#ff4444' for val in btc['MACD_hist']]
fig.add_trace(go.Bar(
    x=btc.index, y=btc['MACD_hist'],
    name='Histogram', marker_color=hist_colors, opacity=0.5
), row=4, col=1)

# Row 5: ATR
fig.add_trace(go.Scatter(
    x=btc.index, y=btc['ATR'],
    name='ATR', line=dict(color='purple', width=2),
    fill='tozeroy', fillcolor='rgba(128,0,128,0.2)'
), row=5, col=1)

# Update layout
fig.update_layout(
    title='₿ Bitcoin Complete Technical Analysis Dashboard',
    template='plotly_dark',
    height=1400,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_rangeslider_visible=False
)

fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
fig.update_yaxes(title_text="Volume", row=2, col=1)
fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
fig.update_yaxes(title_text="MACD", row=4, col=1)
fig.update_yaxes(title_text="ATR", row=5, col=1)

print("\n✅ Dashboard ready! Opening in browser...")
fig.show()

print("\n" + "=" * 60)
print("🎉 Analysis Complete!")
print("=" * 60)
print("\n💡 Tips:")
print("   • Hover over the chart for detailed values")
print("   • Use the toolbar to zoom, pan, and save")
print("   • RSI > 70 = Overbought, RSI < 30 = Oversold")
print("   • MACD above signal line = Bullish momentum")
print("\n📚 Keep learning with the CAS Financial Literacy App!")
