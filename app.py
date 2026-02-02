"""
📈 FinLit Pro - Professional Financial Literacy App
====================================================
A stunning, professional financial education platform
IB CAS Project | Powered by OpenBB
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG - MUST BE FIRST STREAMLIT COMMAND
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FinLit Pro | Financial Literacy",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# PROFESSIONAL CSS - STUNNING DARK THEME
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Import Premium Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Reset */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* App Background - Stunning Gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #13131a 25%, #1a1a2e 50%, #0f0f1a 100%);
        background-attachment: fixed;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Hide header content but keep sidebar toggle button visible */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    
    /* Style the sidebar collapse button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        color: #a5b4fc !important;
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover {
        background: rgba(99, 102, 241, 0.2) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* HERO SECTION */
    /* ═══════════════════════════════════════════════════════════ */
    
    .hero-container {
        text-align: center;
        padding: 3rem 0;
        margin-bottom: 2rem;
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 50px;
        padding: 0.5rem 1.5rem;
        font-size: 0.85rem;
        color: #a5b4fc;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        letter-spacing: -3px;
        line-height: 1.1;
        margin: 0;
        padding: 0;
        background: linear-gradient(135deg, #fff 0%, #a5b4fc 50%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #6b7280;
        font-weight: 400;
        margin-top: 1rem;
        letter-spacing: 0.5px;
    }
    
    .hero-glow {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 600px;
        height: 400px;
        background: radial-gradient(ellipse, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* PREMIUM CARDS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .premium-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .premium-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent);
    }
    
    .premium-card:hover {
        transform: translateY(-8px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 25px 50px rgba(99, 102, 241, 0.15),
                    0 0 100px rgba(99, 102, 241, 0.05);
    }
    
    /* Feature Card */
    .feature-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.05) 100%);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 20px;
        padding: 2rem;
        height: 100%;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 30px 60px rgba(99, 102, 241, 0.2);
    }
    
    .feature-card:hover::after {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 0.75rem;
    }
    
    .feature-desc {
        color: #9ca3af;
        font-size: 1rem;
        line-height: 1.7;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* METRIC CARDS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .metric-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(31, 41, 55, 0.8) 100%);
        border: 1px solid rgba(55, 65, 81, 0.5);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    }
    
    .metric-card:hover {
        transform: scale(1.03);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #fff;
        letter-spacing: -1px;
    }
    
    .metric-change {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-positive { color: #10b981; }
    .metric-negative { color: #ef4444; }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SIDEBAR */
    /* ═══════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #13131a 50%, #0a0a0f 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1.5rem;
    }
    
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem;
    }
    
    .sidebar-logo {
        font-size: 2.5rem;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* BUTTONS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* INPUTS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(17, 24, 39, 0.8) !important;
        border: 1px solid rgba(55, 65, 81, 0.5) !important;
        border-radius: 12px !important;
        color: #fff !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SECTION HEADERS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .section-header {
        font-size: 1.75rem;
        font-weight: 800;
        color: #fff;
        margin: 2.5rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        letter-spacing: -0.5px;
    }
    
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        margin: 2rem 0;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SIGNAL BADGES */
    /* ═══════════════════════════════════════════════════════════ */
    
    .signal-bullish {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #10b981;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    .signal-bearish {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #ef4444;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    .signal-neutral {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.2) 100%);
        border: 1px solid rgba(251, 191, 36, 0.4);
        color: #fbbf24;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* TABS */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(17, 24, 39, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(55, 65, 81, 0.3);
        color: #9ca3af;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        color: #fff !important;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* QUIZ STYLING */
    /* ═══════════════════════════════════════════════════════════ */
    
    .quiz-card {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(55, 65, 81, 0.5);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .quiz-question {
        font-size: 1.4rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    .quiz-correct {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .quiz-wrong {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .quiz-score {
        font-size: 5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* PROGRESS BAR */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        border-radius: 10px;
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SCROLLBAR */
    /* ═══════════════════════════════════════════════════════════ */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(17, 24, 39, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1 0%, #a855f7 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #818cf8 0%, #c084fc 100%);
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* RADIO BUTTONS (NAV) */
    /* ═══════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(17, 24, 39, 0.5);
        border: 1px solid rgba(55, 65, 81, 0.3);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    /* Glass Effect */
    .glass {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
    }
    
    /* Data Table */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(17, 24, 39, 0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(55, 65, 81, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = None
if 'risk_question' not in st.session_state:
    st.session_state.risk_question = 0

# ═══════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_stock_data(symbol: str, days: int = 365):
    """Fetch stock data using yfinance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=f"{days}d")
        if data.empty:
            return None
        # Rename columns to lowercase for consistency
        data.columns = data.columns.str.lower()
        return data
    except:
        return None

@st.cache_data(ttl=300)
def fetch_crypto_data(symbol: str, days: int = 365):
    """Fetch crypto data using yfinance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol}-USD")
        data = ticker.history(period=f"{days}d")
        if data.empty:
            return None
        # Rename columns to lowercase for consistency
        data.columns = data.columns.str.lower()
        return data
    except:
        return None

def calculate_indicators(df):
    """Calculate all technical indicators"""
    data = df.copy()
    
    # Moving Averages
    data['SMA_20'] = data['close'].rolling(20).mean()
    data['SMA_50'] = data['close'].rolling(50).mean()
    data['SMA_200'] = data['close'].rolling(200).mean()
    
    # Bollinger Bands
    data['BB_middle'] = data['close'].rolling(20).mean()
    data['BB_std'] = data['close'].rolling(20).std()
    data['BB_upper'] = data['BB_middle'] + (data['BB_std'] * 2)
    data['BB_lower'] = data['BB_middle'] - (data['BB_std'] * 2)
    
    # RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = data['close'].ewm(span=12).mean()
    exp2 = data['close'].ewm(span=26).mean()
    data['MACD'] = exp1 - exp2
    data['MACD_signal'] = data['MACD'].ewm(span=9).mean()
    data['MACD_hist'] = data['MACD'] - data['MACD_signal']
    
    return data

def create_professional_chart(data, symbol):
    """Create a stunning professional chart"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.6, 0.2, 0.2],
    )
    
    # Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='Price',
        increasing=dict(line=dict(color='#10b981'), fillcolor='#10b981'),
        decreasing=dict(line=dict(color='#ef4444'), fillcolor='#ef4444')
    ), row=1, col=1)
    
    # Moving Averages
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_20'],
        name='SMA 20', line=dict(color='#6366f1', width=1.5)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_50'],
        name='SMA 50', line=dict(color='#a855f7', width=1.5)
    ), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=data.index, y=data['BB_upper'],
        name='BB Upper', line=dict(color='rgba(99, 102, 241, 0.3)', width=1)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=data.index, y=data['BB_lower'],
        name='BB Lower', line=dict(color='rgba(99, 102, 241, 0.3)', width=1),
        fill='tonexty', fillcolor='rgba(99, 102, 241, 0.05)'
    ), row=1, col=1)
    
    # Volume
    colors = ['#10b981' if data['close'].iloc[i] >= data['open'].iloc[i] else '#ef4444' 
              for i in range(len(data))]
    fig.add_trace(go.Bar(
        x=data.index, y=data['volume'],
        name='Volume', marker_color=colors, opacity=0.5
    ), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(
        x=data.index, y=data['RSI'],
        name='RSI', line=dict(color='#ec4899', width=2)
    ), row=3, col=1)
    
    # RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(239, 68, 68, 0.5)", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(16, 185, 129, 0.5)", row=3, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor="rgba(99, 102, 241, 0.05)", line_width=0, row=3, col=1)
    
    # Layout
    fig.update_layout(
        template='plotly_dark',
        height=650,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color='#9ca3af')
        ),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=10, t=40, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#9ca3af'),
    )
    
    # Grid styling
    fig.update_xaxes(gridcolor='rgba(55, 65, 81, 0.3)', showgrid=True, zeroline=False)
    fig.update_yaxes(gridcolor='rgba(55, 65, 81, 0.3)', showgrid=True, zeroline=False)
    
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    
    return fig

# ═══════════════════════════════════════════════════════════
# EDUCATIONAL CONTENT
# ═══════════════════════════════════════════════════════════

EDUCATION_MODULES = {
    "📊 Stock Market Basics": """
## Understanding the Stock Market

### What is a Stock?
A **stock** (or share) represents **partial ownership** in a company. When you buy shares of Apple (AAPL), you literally own a tiny piece of Apple Inc.

---

### Key Terminology

| Term | Definition |
|------|------------|
| **Share** | A single unit of ownership in a company |
| **Ticker Symbol** | Unique identifier (e.g., AAPL, MSFT, GOOGL) |
| **Market Cap** | Total value of all shares (Price × Shares Outstanding) |
| **Dividend** | Portion of profits paid to shareholders |
| **IPO** | Initial Public Offering - when a company first sells stock |

---

### Market Types

🐂 **Bull Market**
- Prices rising 20%+ from recent lows
- Investor optimism & confidence
- Economic expansion

🐻 **Bear Market**  
- Prices falling 20%+ from recent highs
- Investor pessimism & fear
- Economic contraction

---

### Major Stock Exchanges

- **NYSE** - New York Stock Exchange (largest in world)
- **NASDAQ** - Technology-focused exchange
- **LSE** - London Stock Exchange
- **TSE** - Tokyo Stock Exchange
""",
    
    "💡 Investment Fundamentals": """
## The Principles of Smart Investing

### The Power of Compound Interest

> *"Compound interest is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."* — Albert Einstein

---

### Growth of $10,000 at 10% Annual Return

| Years | Value | Total Growth |
|-------|-------|--------------|
| 5 | $16,105 | +61% |
| 10 | $25,937 | +159% |
| 20 | $67,275 | +573% |
| 30 | **$174,494** | +1,645% |

---

### The Rule of 72

Quick way to estimate doubling time:

**Years to Double = 72 ÷ Interest Rate**

- At 6% → 12 years
- At 8% → 9 years
- At 10% → 7.2 years
- At 12% → 6 years

---

### The 5 Golden Rules of Investing

1. **Start Early** — Time is your greatest asset
2. **Diversify** — Never put all eggs in one basket
3. **Stay Consistent** — Dollar-cost averaging beats timing
4. **Think Long-Term** — Ignore daily market noise
5. **Keep Costs Low** — Fees compound too (negatively)
""",
    
    "📈 Technical Analysis": """
## Technical Analysis Explained

### What is Technical Analysis?
The study of **price patterns and indicators** to predict future movements. It assumes all relevant information is already reflected in the price.

---

### Key Indicators

#### Moving Averages (MA)
- **SMA 20**: Short-term trend (20-day average)
- **SMA 50**: Medium-term trend
- **SMA 200**: Long-term trend
- Price > MA = **Bullish** ✅
- Price < MA = **Bearish** ❌

#### RSI (Relative Strength Index)
Measures momentum on a scale of 0-100:
- **RSI > 70**: Overbought 🔴 (potential reversal down)
- **RSI < 30**: Oversold 🟢 (potential reversal up)
- **RSI 30-70**: Neutral zone

#### MACD (Moving Average Convergence Divergence)
- **MACD > Signal Line** = Bullish momentum
- **MACD < Signal Line** = Bearish momentum
- **Histogram** shows momentum strength

---

### Classic Chart Patterns

| Signal | Pattern | Meaning |
|--------|---------|---------|
| 🟢 | **Golden Cross** | 50 MA crosses ABOVE 200 MA → Buy |
| 🔴 | **Death Cross** | 50 MA crosses BELOW 200 MA → Sell |
| 🟢 | **Bullish Breakout** | Price breaks above resistance |
| 🔴 | **Bearish Breakdown** | Price breaks below support |
""",
    
    "🛡️ Risk Management": """
## Protecting Your Capital

### Warren Buffett's Golden Rules

> *"Rule #1: Never lose money."*
> *"Rule #2: Never forget Rule #1."*

---

### Position Sizing

**Never risk more than you can afford to lose:**

- **5% Rule**: No single stock > 5% of portfolio
- **1% Rule**: Risk max 1% per trade (for active traders)
- **Emergency Fund**: Keep 3-6 months expenses in cash BEFORE investing

---

### Diversification Strategy

**Across Asset Classes:**
- Stocks (60-80%)
- Bonds (10-30%)
- Cash (5-10%)
- Alternative (5-10%)

**Within Stocks:**
- Large Cap (40%)
- Mid Cap (30%)
- Small Cap (20%)
- International (10%)

---

### Risk Management Tools

| Tool | Description |
|------|-------------|
| **Stop-Loss** | Automatic sell at preset loss limit |
| **Take-Profit** | Automatic sell at target gain |
| **Position Sizing** | Limit exposure per trade |
| **Hedging** | Use options/inverse ETFs for protection |

---

### Risk Metrics

- **Beta**: Volatility vs market (β=1 means same as market)
- **Sharpe Ratio**: Return per unit of risk (higher = better)
- **Max Drawdown**: Largest peak-to-trough decline
""",

    "📜 Options Trading": """
## Introduction to Options

### What is an Option?
An **option** is a contract that gives you the **right** (but not obligation) to buy or sell a stock at a specific price before a certain date.

---

### Two Types of Options

| Type | What It Does | When to Use |
|------|--------------|-------------|
| **CALL** 📈 | Right to **BUY** at strike price | You think stock will go UP |
| **PUT** 📉 | Right to **SELL** at strike price | You think stock will go DOWN |

---

### Key Terms

| Term | Definition |
|------|------------|
| **Strike Price** | The price you can buy/sell the stock |
| **Premium** | The cost to buy the option |
| **Expiration** | Date the option expires |
| **In The Money (ITM)** | Option has intrinsic value |
| **Out of The Money (OTM)** | Option has no intrinsic value |
| **At The Money (ATM)** | Strike price = current stock price |

---

### Simple Example

**CALL Option Example:**
- Stock ABC trades at $100
- You buy a $105 CALL for $2 (premium)
- If stock rises to $115 → You profit $8 ($115 - $105 - $2)
- If stock stays below $105 → You lose $2 (premium only)

**PUT Option Example:**
- Stock ABC trades at $100
- You buy a $95 PUT for $2 (premium)
- If stock falls to $85 → You profit $8 ($95 - $85 - $2)
- If stock stays above $95 → You lose $2 (premium only)

---

### The Greeks (Option Sensitivity)

| Greek | What It Measures |
|-------|------------------|
| **Delta (Δ)** | Price change per $1 stock move |
| **Gamma (Γ)** | Rate of delta change |
| **Theta (Θ)** | Time decay (value lost per day) |
| **Vega (ν)** | Sensitivity to volatility |

---

### ⚠️ Options Risks

> **Warning:** Options are complex and risky. You can lose 100% of your investment.

- **Time Decay**: Options lose value every day
- **Leverage**: Small moves = big gains OR losses
- **Complexity**: Requires deep understanding
- **Not for beginners**: Master stocks first!

---

### Basic Strategies

| Strategy | Risk Level | Description |
|----------|------------|-------------|
| **Covered Call** | Low | Own stock + sell call |
| **Protective Put** | Low | Own stock + buy put (insurance) |
| **Long Call/Put** | Medium | Simple directional bet |
| **Spreads** | Medium | Limit risk with multiple options |
| **Naked Options** | ⚠️ HIGH | Don't do this as a beginner! |
"""
}

# Quiz Questions
QUIZ_DATA = [
    {
        "question": "What does a stock represent?",
        "options": ["A loan to a company", "Ownership in a company", "A bond certificate", "A savings account"],
        "correct": 1,
        "explanation": "A stock represents partial ownership (equity) in a company."
    },
    {
        "question": "What characterizes a bull market?",
        "options": ["Falling prices by 20%+", "Rising prices by 20%+", "Stable prices", "High volatility"],
        "correct": 1,
        "explanation": "A bull market is defined by prices rising 20% or more from recent lows, with general optimism."
    },
    {
        "question": "An RSI reading above 70 indicates:",
        "options": ["Oversold conditions", "Overbought conditions", "Neutral territory", "Strong buy signal"],
        "correct": 1,
        "explanation": "RSI > 70 suggests the asset may be overbought and due for a pullback."
    },
    {
        "question": "What is compound interest?",
        "options": ["Interest on principal only", "Interest on interest + principal", "A type of loan", "A stock dividend"],
        "correct": 1,
        "explanation": "Compound interest is earning interest on both your original investment AND accumulated interest."
    },
    {
        "question": "What is diversification?",
        "options": ["Buying one stock", "Spreading investments across assets", "Day trading", "Short selling"],
        "correct": 1,
        "explanation": "Diversification spreads risk across different investments to reduce overall portfolio risk."
    },
    {
        "question": "The Rule of 72 estimates:",
        "options": ["Maximum profit", "Years to double money", "Optimal portfolio size", "Tax rate"],
        "correct": 1,
        "explanation": "Rule of 72: Divide 72 by your interest rate to estimate years to double your money."
    },
    {
        "question": "A Golden Cross occurs when:",
        "options": ["Stock hits all-time high", "50 MA crosses above 200 MA", "RSI hits 100", "Price doubles"],
        "correct": 1,
        "explanation": "A Golden Cross is a bullish signal when the 50-day MA crosses above the 200-day MA."
    },
    {
        "question": "What does P/E ratio measure?",
        "options": ["Profit margin", "Price relative to earnings", "Debt level", "Revenue growth"],
        "correct": 1,
        "explanation": "P/E (Price-to-Earnings) ratio shows how much investors pay per dollar of earnings."
    },
    {
        "question": "What is a stop-loss order?",
        "options": ["Order to buy more", "Auto-sell at preset loss", "Dividend payment", "Tax deduction"],
        "correct": 1,
        "explanation": "A stop-loss automatically sells your position when it falls to a preset price to limit losses."
    },
    {
        "question": "What does beta measure?",
        "options": ["Absolute returns", "Volatility vs market", "Company size", "Dividend yield"],
        "correct": 1,
        "explanation": "Beta measures a stock's volatility relative to the overall market (β=1 means same as market)."
    }
]

# ═══════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════

with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <span class="sidebar-logo">📈</span>
        <span class="sidebar-title">FinLit Pro</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📚 Learn", "📈 Stock Analysis", "⚖️ Compare", "🧮 Calculator", "🎭 Risk Profile", "🪙 Crypto", "💼 Portfolio", "🎯 Quiz", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <p style="color: #4b5563; font-size: 0.75rem; margin: 0;">IB CAS Project 2024</p>
        <p style="color: #6366f1; font-size: 0.7rem; margin: 0.5rem 0 0 0;">Powered by OpenBB</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════

if page == "🏠 Dashboard":
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-glow"></div>
        <div class="hero-badge">IB CAS Project</div>
        <h1 class="hero-title">FinLit Pro</h1>
        <p class="hero-subtitle">Master the art of investing with real market data & professional tools</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📚</span>
            <div class="feature-title">Learn</div>
            <div class="feature-desc">Master stocks, technical analysis, portfolio theory, and risk management through interactive modules.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Analyze</div>
            <div class="feature-desc">Real-time market data with professional charts, indicators, and AI-powered trading signals.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <div class="feature-title">Practice</div>
            <div class="feature-desc">Test your knowledge with quizzes, track virtual portfolios, and apply what you learn.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Market Overview
    st.markdown('<div class="section-header">📊 Live Market Overview</div>', unsafe_allow_html=True)
    
    market_tickers = [
        ("AAPL", "Apple", "🍎"),
        ("MSFT", "Microsoft", "🪟"),
        ("GOOGL", "Google", "🔍"),
        ("TSLA", "Tesla", "⚡"),
        ("BTC", "Bitcoin", "₿")
    ]
    
    cols = st.columns(5)
    
    for i, (symbol, name, icon) in enumerate(market_tickers):
        with cols[i]:
            try:
                if symbol == "BTC":
                    data = fetch_crypto_data(symbol, 7)
                else:
                    data = fetch_stock_data(symbol, 7)
                
                if data is not None and len(data) > 1:
                    price = data['close'].iloc[-1]
                    prev_price = data['close'].iloc[-2]
                    change = ((price - prev_price) / prev_price) * 100
                    change_class = "metric-positive" if change >= 0 else "metric-negative"
                    change_symbol = "↑" if change >= 0 else "↓"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{icon} {name}</div>
                        <div class="metric-value">${price:,.0f}</div>
                        <div class="metric-change {change_class}">{change_symbol} {abs(change):.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{icon} {name}</div>
                        <div class="metric-value">—</div>
                        <div class="metric-change">Loading...</div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{icon} {name}</div>
                    <div class="metric-value">—</div>
                    <div class="metric-change">Unavailable</div>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE: LEARN
# ═══════════════════════════════════════════════════════════

elif page == "📚 Learn":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">📚 Learn</h1>
        <p class="hero-subtitle">Master the fundamentals of investing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Module tabs
    tabs = st.tabs(list(EDUCATION_MODULES.keys()))
    
    for i, (module_name, content) in enumerate(EDUCATION_MODULES.items()):
        with tabs[i]:
            st.markdown(content)

# ═══════════════════════════════════════════════════════════
# PAGE: STOCK ANALYSIS
# ═══════════════════════════════════════════════════════════

elif page == "📈 Stock Analysis":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">📈 Stock Analysis</h1>
        <p class="hero-subtitle">Professional technical analysis powered by OpenBB</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        symbol = st.text_input("Stock Symbol", value="AAPL", placeholder="Enter ticker symbol...").upper()
    
    with col2:
        period = st.selectbox("Time Period", ["1 Month", "3 Months", "6 Months", "1 Year"], index=3)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    days_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365}
    
    if symbol:
        with st.spinner(f"Fetching data for {symbol}..."):
            data = fetch_stock_data(symbol, days_map[period])
        
        if data is not None and not data.empty:
            data = calculate_indicators(data)
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            change = ((latest['close'] - prev['close']) / prev['close']) * 100
            
            # Metrics row
            m1, m2, m3, m4 = st.columns(4)
            
            with m1:
                change_class = "metric-positive" if change >= 0 else "metric-negative"
                change_arrow = "↑" if change >= 0 else "↓"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">💰 Current Price</div>
                    <div class="metric-value">${latest['close']:.2f}</div>
                    <div class="metric-change {change_class}">{change_arrow} {abs(change):.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m2:
                rsi = latest['RSI']
                rsi_status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                rsi_class = "metric-negative" if rsi > 70 else "metric-positive" if rsi < 30 else ""
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📊 RSI (14)</div>
                    <div class="metric-value">{rsi:.1f}</div>
                    <div class="metric-change {rsi_class}">{rsi_status}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📈 52-Week High</div>
                    <div class="metric-value">${data['high'].max():.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📉 52-Week Low</div>
                    <div class="metric-value">${data['low'].min():.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            # Chart
            st.plotly_chart(create_professional_chart(data, symbol), use_container_width=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            # Trading Signals
            st.markdown('<div class="section-header">🎯 Technical Signals</div>', unsafe_allow_html=True)
            
            sig_col1, sig_col2 = st.columns(2)
            
            with sig_col1:
                st.markdown("**Trend Indicators**")
                
                if latest['close'] > latest['SMA_20']:
                    st.markdown('<span class="signal-bullish">✓ Above SMA 20</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="signal-bearish">✗ Below SMA 20</span>', unsafe_allow_html=True)
                
                if latest['close'] > latest['SMA_50']:
                    st.markdown('<span class="signal-bullish">✓ Above SMA 50</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="signal-bearish">✗ Below SMA 50</span>', unsafe_allow_html=True)
                
                if pd.notna(latest['SMA_200']) and latest['close'] > latest['SMA_200']:
                    st.markdown('<span class="signal-bullish">✓ Above SMA 200</span>', unsafe_allow_html=True)
                elif pd.notna(latest['SMA_200']):
                    st.markdown('<span class="signal-bearish">✗ Below SMA 200</span>', unsafe_allow_html=True)
            
            with sig_col2:
                st.markdown("**Momentum Indicators**")
                
                if latest['MACD'] > latest['MACD_signal']:
                    st.markdown('<span class="signal-bullish">✓ MACD Bullish</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="signal-bearish">✗ MACD Bearish</span>', unsafe_allow_html=True)
                
                if rsi > 70:
                    st.markdown('<span class="signal-bearish">⚠ RSI Overbought</span>', unsafe_allow_html=True)
                elif rsi < 30:
                    st.markdown('<span class="signal-bullish">✓ RSI Oversold</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="signal-neutral">○ RSI Neutral</span>', unsafe_allow_html=True)
                
                # Bollinger Band position
                if latest['close'] > latest['BB_upper']:
                    st.markdown('<span class="signal-bearish">⚠ Above Upper BB</span>', unsafe_allow_html=True)
                elif latest['close'] < latest['BB_lower']:
                    st.markdown('<span class="signal-bullish">✓ Below Lower BB</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="signal-neutral">○ Within BB Range</span>', unsafe_allow_html=True)
        else:
            st.error(f"❌ Could not fetch data for '{symbol}'. Please check the symbol and try again.")

# ═══════════════════════════════════════════════════════════
# PAGE: STOCK COMPARISON
# ═══════════════════════════════════════════════════════════

elif page == "⚖️ Compare":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">⚖️ Stock Comparison</h1>
        <p class="hero-subtitle">Compare stocks side-by-side</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input for stocks to compare
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stock1 = st.text_input("Stock 1", value="AAPL", placeholder="Enter ticker...").upper()
    with col2:
        stock2 = st.text_input("Stock 2", value="MSFT", placeholder="Enter ticker...").upper()
    with col3:
        stock3 = st.text_input("Stock 3 (optional)", value="", placeholder="Enter ticker...").upper()
    
    compare_period = st.selectbox("Comparison Period", ["1 Month", "3 Months", "6 Months", "1 Year"], index=3, key="compare_period")
    
    if st.button("📊 Compare Stocks", type="primary"):
        days_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365}
        stocks_to_compare = [s for s in [stock1, stock2, stock3] if s]
        
        if len(stocks_to_compare) >= 2:
            with st.spinner("Fetching data..."):
                stock_data = {}
                for symbol in stocks_to_compare:
                    data = fetch_stock_data(symbol, days_map[compare_period])
                    if data is not None and not data.empty:
                        stock_data[symbol] = data
                
                if len(stock_data) >= 2:
                    # Normalized Performance Chart
                    st.markdown('<div class="section-header">📈 Normalized Performance</div>', unsafe_allow_html=True)
                    
                    fig = go.Figure()
                    colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444']
                    
                    for i, (symbol, data) in enumerate(stock_data.items()):
                        normalized = (data['close'] / data['close'].iloc[0] - 1) * 100
                        fig.add_trace(go.Scatter(
                            x=data.index,
                            y=normalized,
                            name=symbol,
                            line=dict(color=colors[i % len(colors)], width=3)
                        ))
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=450,
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                                   bgcolor="rgba(0,0,0,0)", font=dict(color='#9ca3af')),
                        yaxis_title="Return (%)",
                        margin=dict(l=0, r=0, t=40, b=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='Inter', color='#9ca3af')
                    )
                    fig.update_xaxes(gridcolor='rgba(55, 65, 81, 0.3)')
                    fig.update_yaxes(gridcolor='rgba(55, 65, 81, 0.3)')
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Comparison Metrics
                    st.markdown('<div class="section-header">📊 Key Metrics Comparison</div>', unsafe_allow_html=True)
                    
                    cols = st.columns(len(stock_data))
                    
                    for i, (symbol, data) in enumerate(stock_data.items()):
                        with cols[i]:
                            latest = data['close'].iloc[-1]
                            start = data['close'].iloc[0]
                            returns = ((latest - start) / start) * 100
                            volatility = data['close'].pct_change().std() * np.sqrt(252) * 100
                            high = data['high'].max()
                            low = data['low'].min()
                            avg_volume = data['volume'].mean()
                            
                            return_class = "metric-positive" if returns >= 0 else "metric-negative"
                            
                            st.markdown(f"""
                            <div class="premium-card" style="text-align: center;">
                                <h3 style="color: #fff; font-size: 1.75rem; margin-bottom: 1rem;">{symbol}</h3>
                                <div style="margin: 1rem 0;">
                                    <div class="metric-label">Current Price</div>
                                    <div style="font-size: 1.5rem; font-weight: 700; color: #fff;">${latest:.2f}</div>
                                </div>
                                <div style="margin: 1rem 0;">
                                    <div class="metric-label">Total Return</div>
                                    <div class="{return_class}" style="font-size: 1.3rem; font-weight: 700;">
                                        {'↑' if returns >= 0 else '↓'} {abs(returns):.2f}%
                                    </div>
                                </div>
                                <div style="margin: 1rem 0;">
                                    <div class="metric-label">Volatility (Annual)</div>
                                    <div style="font-size: 1.1rem; color: #f59e0b;">{volatility:.1f}%</div>
                                </div>
                                <div style="margin: 1rem 0;">
                                    <div class="metric-label">High / Low</div>
                                    <div style="font-size: 0.95rem; color: #9ca3af;">
                                        ${high:.2f} / ${low:.2f}
                                    </div>
                                </div>
                                <div style="margin: 1rem 0;">
                                    <div class="metric-label">Avg Volume</div>
                                    <div style="font-size: 0.95rem; color: #9ca3af;">
                                        {avg_volume/1e6:.1f}M
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Winner Summary
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    returns_dict = {sym: ((data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]) * 100 
                                   for sym, data in stock_data.items()}
                    winner = max(returns_dict, key=returns_dict.get)
                    
                    st.markdown(f"""
                    <div class="premium-card" style="text-align: center; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1)); border-color: rgba(16, 185, 129, 0.3);">
                        <h3 style="color: #10b981; margin-bottom: 0.5rem;">🏆 Winner: {winner}</h3>
                        <p style="color: #9ca3af;">Best performing stock with {returns_dict[winner]:.2f}% return</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Could not fetch data for the stocks. Please check the symbols.")
        else:
            st.warning("Please enter at least 2 stock symbols to compare.")

# ═══════════════════════════════════════════════════════════
# PAGE: INVESTMENT CALCULATOR
# ═══════════════════════════════════════════════════════════

elif page == "🧮 Calculator":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">🧮 Investment Calculator</h1>
        <p class="hero-subtitle">See the power of compound interest</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">📝 Your Inputs</div>', unsafe_allow_html=True)
        
        initial = st.number_input("Initial Investment ($)", min_value=0, value=10000, step=1000)
        monthly = st.number_input("Monthly Contribution ($)", min_value=0, value=500, step=100)
        rate = st.slider("Expected Annual Return (%)", min_value=1, max_value=15, value=8)
        years = st.slider("Investment Period (Years)", min_value=1, max_value=40, value=20)
        
        # Calculate results
        months = years * 12
        monthly_rate = rate / 100 / 12
        
        # Future value calculation
        # FV of initial investment
        fv_initial = initial * ((1 + monthly_rate) ** months)
        # FV of monthly contributions (annuity)
        if monthly_rate > 0:
            fv_contributions = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            fv_contributions = monthly * months
        
        total_value = fv_initial + fv_contributions
        total_invested = initial + (monthly * months)
        total_gains = total_value - total_invested
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Results cards
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Future Value</div>
            <div class="metric-value" style="color: #10b981;">${total_value:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📈 Total Gains</div>
            <div class="metric-value" style="color: #6366f1;">${total_gains:,.0f}</div>
            <div class="metric-change metric-positive">+{(total_gains/total_invested*100):.0f}% return</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💵 Total Invested</div>
            <div class="metric-value">${total_invested:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">📊 Growth Projection</div>', unsafe_allow_html=True)
        
        # Generate growth data
        years_range = list(range(0, years + 1))
        invested_values = []
        total_values = []
        
        for y in years_range:
            m = y * 12
            inv = initial + (monthly * m)
            invested_values.append(inv)
            
            fv_i = initial * ((1 + monthly_rate) ** m)
            if monthly_rate > 0:
                fv_c = monthly * (((1 + monthly_rate) ** m - 1) / monthly_rate)
            else:
                fv_c = monthly * m
            total_values.append(fv_i + fv_c)
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years_range, y=total_values,
            name='Total Value',
            fill='tozeroy',
            line=dict(color='#10b981', width=3),
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))
        
        fig.add_trace(go.Scatter(
            x=years_range, y=invested_values,
            name='Amount Invested',
            fill='tozeroy',
            line=dict(color='#6366f1', width=3),
            fillcolor='rgba(99, 102, 241, 0.2)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                       bgcolor="rgba(0,0,0,0)", font=dict(color='#9ca3af')),
            xaxis_title="Years",
            yaxis_title="Value ($)",
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#9ca3af')
        )
        fig.update_xaxes(gridcolor='rgba(55, 65, 81, 0.3)')
        fig.update_yaxes(gridcolor='rgba(55, 65, 81, 0.3)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Milestones
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">🎯 Milestones</div>', unsafe_allow_html=True)
        
        milestones = [100000, 250000, 500000, 1000000]
        milestone_years = []
        
        for milestone in milestones:
            for y in range(1, years + 1):
                m = y * 12
                fv_i = initial * ((1 + monthly_rate) ** m)
                if monthly_rate > 0:
                    fv_c = monthly * (((1 + monthly_rate) ** m - 1) / monthly_rate)
                else:
                    fv_c = monthly * m
                if fv_i + fv_c >= milestone:
                    milestone_years.append((milestone, y))
                    break
            else:
                milestone_years.append((milestone, None))
        
        milestone_cols = st.columns(4)
        milestone_emojis = ["💯", "🌟", "🔥", "🏆"]
        
        for i, (milestone, year) in enumerate(milestone_years):
            with milestone_cols[i]:
                if year:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">{milestone_emojis[i]}</div>
                        <div style="color: #fff; font-weight: 700;">${milestone/1000:.0f}K</div>
                        <div style="color: #10b981; font-size: 0.9rem;">Year {year}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; opacity: 0.5;">
                        <div style="font-size: 2rem;">{milestone_emojis[i]}</div>
                        <div style="color: #fff; font-weight: 700;">${milestone/1000:.0f}K</div>
                        <div style="color: #6b7280; font-size: 0.9rem;">Not reached</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Educational callout
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="premium-card" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)); border-color: rgba(99, 102, 241, 0.3);">
        <h3 style="color: #fff; margin-bottom: 1rem;">💡 The Magic of Compound Interest</h3>
        <p style="color: #9ca3af; line-height: 1.8;">
            In this scenario, you're investing <strong style="color: #fff;">${total_invested:,.0f}</strong> over {years} years, 
            but ending up with <strong style="color: #10b981;">${total_value:,.0f}</strong>!
        </p>
        <p style="color: #9ca3af; line-height: 1.8; margin-top: 1rem;">
            That's <strong style="color: #6366f1;">${total_gains:,.0f}</strong> in pure gains — money that grew while you slept! 
            This is why starting early is the most powerful financial decision you can make.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE: RISK PROFILE QUIZ
# ═══════════════════════════════════════════════════════════

elif page == "🎭 Risk Profile":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">🎭 Risk Profile</h1>
        <p class="hero-subtitle">Discover your investor personality</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Profile Questions
    RISK_QUESTIONS = [
        {
            "question": "How would you react if your investment dropped 20% in one month?",
            "options": [
                ("Sell everything immediately", 1),
                ("Sell some to reduce risk", 2),
                ("Hold and wait it out", 3),
                ("Buy more at the lower price", 4)
            ]
        },
        {
            "question": "What's your investment time horizon?",
            "options": [
                ("Less than 2 years", 1),
                ("2-5 years", 2),
                ("5-10 years", 3),
                ("10+ years", 4)
            ]
        },
        {
            "question": "Which portfolio would you prefer?",
            "options": [
                ("100% safe, 3% return", 1),
                ("Small risk, 5% average return", 2),
                ("Moderate risk, 8% average return", 3),
                ("High risk, 12% potential return", 4)
            ]
        },
        {
            "question": "How much of your income can you invest?",
            "options": [
                ("Less than 5%", 1),
                ("5-10%", 2),
                ("10-20%", 3),
                ("More than 20%", 4)
            ]
        },
        {
            "question": "What's your investment knowledge level?",
            "options": [
                ("Complete beginner", 1),
                ("Know the basics", 2),
                ("Intermediate", 3),
                ("Advanced/Expert", 4)
            ]
        },
        {
            "question": "How would you describe your financial goals?",
            "options": [
                ("Preserve what I have", 1),
                ("Slow and steady growth", 2),
                ("Build significant wealth", 3),
                ("Maximize returns aggressively", 4)
            ]
        }
    ]
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.risk_score = None
            st.session_state.risk_question = 0
            st.rerun()
    
    if st.session_state.risk_score is None:
        # Quiz in progress
        if st.session_state.risk_question < len(RISK_QUESTIONS):
            progress = st.session_state.risk_question / len(RISK_QUESTIONS)
            st.progress(progress)
            st.markdown(f"**Question {st.session_state.risk_question + 1} of {len(RISK_QUESTIONS)}**")
            
            q = RISK_QUESTIONS[st.session_state.risk_question]
            
            st.markdown(f"""
            <div class="quiz-card">
                <div class="quiz-question">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            options_text = [opt[0] for opt in q['options']]
            answer = st.radio("Select your answer:", options_text, key=f"risk_q_{st.session_state.risk_question}", label_visibility="collapsed")
            
            if st.button("Next →", type="primary"):
                # Find the score for selected answer
                for opt_text, opt_score in q['options']:
                    if opt_text == answer:
                        if 'risk_answers' not in st.session_state:
                            st.session_state.risk_answers = []
                        st.session_state.risk_answers.append(opt_score)
                        break
                
                st.session_state.risk_question += 1
                
                # If finished, calculate score
                if st.session_state.risk_question >= len(RISK_QUESTIONS):
                    st.session_state.risk_score = sum(st.session_state.risk_answers)
                    st.session_state.risk_answers = []
                
                st.rerun()
        else:
            # Calculate final score
            if 'risk_answers' in st.session_state and st.session_state.risk_answers:
                st.session_state.risk_score = sum(st.session_state.risk_answers)
                st.session_state.risk_answers = []
                st.rerun()
    else:
        # Show results
        score = st.session_state.risk_score
        
        # Determine profile
        if score <= 8:
            profile = "Conservative"
            emoji = "🛡️"
            color = "#3b82f6"
            desc = "You prefer safety and stability over high returns. Capital preservation is your priority."
            allocation = {"Bonds": 60, "Stocks": 25, "Cash": 15}
            recommendations = [
                "Focus on high-grade bonds and bond funds",
                "Consider dividend-paying blue-chip stocks",
                "Keep 6+ months emergency fund",
                "Look into CDs and Treasury bonds"
            ]
        elif score <= 14:
            profile = "Moderate"
            emoji = "⚖️"
            color = "#10b981"
            desc = "You balance growth with safety. You can handle some volatility for better returns."
            allocation = {"Stocks": 50, "Bonds": 35, "Cash": 10, "Alternative": 5}
            recommendations = [
                "Mix of index funds and bonds",
                "Consider target-date funds",
                "Diversify across sectors",
                "Rebalance portfolio annually"
            ]
        elif score <= 19:
            profile = "Growth"
            emoji = "📈"
            color = "#f59e0b"
            desc = "You're focused on building wealth and can tolerate significant market swings."
            allocation = {"Stocks": 75, "Bonds": 15, "Alternative": 10}
            recommendations = [
                "Heavy allocation to equity index funds",
                "Consider growth stocks and ETFs",
                "Include international exposure",
                "Small allocation to emerging markets"
            ]
        else:
            profile = "Aggressive"
            emoji = "🚀"
            color = "#ef4444"
            desc = "You're a risk-taker seeking maximum returns. You can stomach major volatility."
            allocation = {"Stocks": 90, "Alternative": 10}
            recommendations = [
                "Focus on growth and tech stocks",
                "Consider small-cap opportunities",
                "Explore sector-specific ETFs",
                "May include some crypto exposure"
            ]
        
        # Display results
        st.markdown(f"""
        <div class="premium-card" style="text-align: center; border-color: {color}40;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">{emoji}</div>
            <h2 style="color: {color}; font-size: 2.5rem; margin-bottom: 0.5rem;">{profile} Investor</h2>
            <p style="color: #9ca3af; font-size: 1.1rem; max-width: 500px; margin: 1rem auto;">{desc}</p>
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 12px;">
                <span style="color: #6b7280;">Risk Score:</span>
                <span style="color: #fff; font-weight: 700; font-size: 1.5rem; margin-left: 0.5rem;">{score}/24</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Recommended Allocation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header" style="font-size: 1.25rem;">🥧 Recommended Allocation</div>', unsafe_allow_html=True)
            
            # Pie chart
            fig = go.Figure(data=[go.Pie(
                labels=list(allocation.keys()),
                values=list(allocation.values()),
                hole=0.6,
                marker=dict(colors=['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']),
                textinfo='label+percent',
                textfont=dict(color='#fff', size=14)
            )])
            
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#9ca3af'),
                annotations=[dict(text=profile, x=0.5, y=0.5, font_size=16, font_color='#fff', showarrow=False)]
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header" style="font-size: 1.25rem;">💡 Recommendations</div>', unsafe_allow_html=True)
            
            for rec in recommendations:
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; 
                            background: rgba(255,255,255,0.02); border-radius: 10px; margin: 0.5rem 0;
                            border-left: 3px solid {color};">
                    <span style="color: {color};">✓</span>
                    <span style="color: #d1d5db;">{rec}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Disclaimer
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        st.warning("⚠️ **Disclaimer:** This is a simplified educational tool. Real investment decisions should consider your complete financial situation and consult a licensed financial advisor.")

# ═══════════════════════════════════════════════════════════
# PAGE: CRYPTO
# ═══════════════════════════════════════════════════════════

elif page == "🪙 Crypto":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">🪙 Crypto Analysis</h1>
        <p class="hero-subtitle">Cryptocurrency market insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        crypto = st.selectbox(
            "Select Cryptocurrency",
            ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "DOT"],
            format_func=lambda x: {"BTC": "₿ Bitcoin", "ETH": "Ξ Ethereum", "SOL": "◎ Solana", 
                                  "XRP": "✕ XRP", "ADA": "₳ Cardano", "DOGE": "Ð Dogecoin",
                                  "AVAX": "🔺 Avalanche", "DOT": "● Polkadot"}.get(x, x)
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔄 Refresh", type="primary", use_container_width=True)
    
    with st.spinner(f"Loading {crypto} data..."):
        data = fetch_crypto_data(crypto, 365)
    
    if data is not None and not data.empty:
        data = calculate_indicators(data)
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        change = ((latest['close'] - prev['close']) / prev['close']) * 100
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        
        with m1:
            change_class = "metric-positive" if change >= 0 else "metric-negative"
            change_arrow = "↑" if change >= 0 else "↓"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💰 {crypto} Price</div>
                <div class="metric-value">${latest['close']:,.2f}</div>
                <div class="metric-change {change_class}">{change_arrow} {abs(change):.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📈 52-Week High</div>
                <div class="metric-value">${data['high'].max():,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📉 52-Week Low</div>
                <div class="metric-value">${data['low'].min():,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chart
        st.plotly_chart(create_professional_chart(data, f"{crypto}/USD"), use_container_width=True)
        
        # Warning
        st.warning("⚠️ **Risk Warning:** Cryptocurrency is extremely volatile and speculative. Never invest more than you can afford to lose completely.")
    else:
        st.error(f"Could not fetch data for {crypto}")

# ═══════════════════════════════════════════════════════════
# PAGE: PORTFOLIO
# ═══════════════════════════════════════════════════════════

elif page == "💼 Portfolio":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">💼 Portfolio</h1>
        <p class="hero-subtitle">Track your investments</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">➕ Add Position</div>', unsafe_allow_html=True)
        
        new_symbol = st.text_input("Symbol", placeholder="AAPL").upper()
        new_shares = st.number_input("Shares", min_value=0.0, step=0.1, value=0.0)
        new_cost = st.number_input("Cost per Share ($)", min_value=0.0, step=0.01, value=0.0)
        
        if st.button("➕ Add to Portfolio", type="primary", use_container_width=True):
            if new_symbol and new_shares > 0:
                st.session_state.portfolio[new_symbol] = {
                    'shares': new_shares,
                    'cost': new_cost
                }
                st.success(f"✅ Added {new_shares} shares of {new_symbol}")
                st.rerun()
            else:
                st.error("Please enter valid symbol and shares")
    
    with col2:
        st.markdown('<div class="section-header" style="font-size: 1.25rem;">📊 Your Holdings</div>', unsafe_allow_html=True)
        
        if st.session_state.portfolio:
            total_value = 0
            total_cost = 0
            
            for sym, info in st.session_state.portfolio.items():
                try:
                    data = fetch_stock_data(sym, 5)
                    if data is not None:
                        current_price = data['close'].iloc[-1]
                        value = info['shares'] * current_price
                        cost = info['shares'] * info['cost']
                        gain = value - cost
                        gain_pct = (gain / cost * 100) if cost > 0 else 0
                        
                        total_value += value
                        total_cost += cost
                        
                        gain_class = "metric-positive" if gain >= 0 else "metric-negative"
                        gain_arrow = "↑" if gain >= 0 else "↓"
                        
                        st.markdown(f"""
                        <div class="premium-card" style="padding: 1rem; margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="font-size: 1.25rem; color: #fff;">{sym}</strong>
                                    <span style="color: #6b7280; margin-left: 1rem;">{info['shares']} shares @ ${info['cost']:.2f}</span>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.1rem; color: #fff; font-weight: 600;">${value:,.2f}</div>
                                    <div class="{gain_class}">{gain_arrow} ${abs(gain):,.2f} ({abs(gain_pct):.1f}%)</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Could not fetch data for {sym}")
            
            # Total Summary
            if total_value > 0:
                total_gain = total_value - total_cost
                total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0
                total_class = "metric-positive" if total_gain >= 0 else "metric-negative"
                
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-card" style="margin-top: 1rem;">
                    <div class="metric-label">💰 Total Portfolio Value</div>
                    <div class="metric-value">${total_value:,.2f}</div>
                    <div class="metric-change {total_class}">
                        {'↑' if total_gain >= 0 else '↓'} ${abs(total_gain):,.2f} ({abs(total_gain_pct):.1f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Clear Portfolio"):
                    st.session_state.portfolio = {}
                    st.rerun()
        else:
            st.info("📭 Your portfolio is empty. Add your first position to get started!")

# ═══════════════════════════════════════════════════════════
# PAGE: QUIZ
# ═══════════════════════════════════════════════════════════

elif page == "🎯 Quiz":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">🎯 Quiz</h1>
        <p class="hero-subtitle">Test your financial knowledge</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Reset Quiz", use_container_width=True):
            st.session_state.current_question = 0
            st.session_state.quiz_score = 0
            st.rerun()
    
    # Quiz logic
    if st.session_state.current_question < len(QUIZ_DATA):
        # Progress
        progress = st.session_state.current_question / len(QUIZ_DATA)
        st.progress(progress)
        st.markdown(f"**Question {st.session_state.current_question + 1} of {len(QUIZ_DATA)}**")
        
        q = QUIZ_DATA[st.session_state.current_question]
        
        # Question card
        st.markdown(f"""
        <div class="quiz-card">
            <div class="quiz-question">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Answer options
        answer = st.radio(
            "Select your answer:",
            q['options'],
            key=f"quiz_q_{st.session_state.current_question}",
            label_visibility="collapsed"
        )
        
        # Submit
        if st.button("Submit Answer", type="primary"):
            selected_idx = q['options'].index(answer)
            
            if selected_idx == q['correct']:
                st.session_state.quiz_score += 1
                st.markdown(f"""
                <div class="quiz-correct">
                    <strong>✅ Correct!</strong><br>
                    {q['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="quiz-wrong">
                    <strong>❌ Incorrect</strong><br>
                    The correct answer was: <strong>{q['options'][q['correct']]}</strong><br>
                    {q['explanation']}
                </div>
                """, unsafe_allow_html=True)
            
            st.session_state.current_question += 1
            
            if st.button("Next Question →"):
                st.rerun()
    else:
        # Quiz complete
        st.balloons()
        score_pct = (st.session_state.quiz_score / len(QUIZ_DATA)) * 100
        
        # Rating
        if score_pct >= 90:
            rating = "🏆 Expert!"
        elif score_pct >= 70:
            rating = "⭐ Great Job!"
        elif score_pct >= 50:
            rating = "📚 Keep Learning"
        else:
            rating = "💪 Don't Give Up"
        
        st.markdown(f"""
        <div class="premium-card" style="text-align: center; padding: 3rem;">
            <h2 style="color: #fff; margin-bottom: 1rem;">Quiz Complete!</h2>
            <div class="quiz-score">{st.session_state.quiz_score}/{len(QUIZ_DATA)}</div>
            <p style="color: #9ca3af; font-size: 1.5rem; margin: 1rem 0;">{score_pct:.0f}%</p>
            <p style="color: #fff; font-size: 1.25rem;">{rating}</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════

elif page == "ℹ️ About":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">About</h1>
        <p class="hero-subtitle">IB CAS Financial Literacy Project</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="premium-card">
        <h2 style="color: #fff; margin-bottom: 1.5rem;">🎓 Project Overview</h2>
        <p style="color: #9ca3af; font-size: 1.1rem; line-height: 1.8;">
            This application was developed as an <strong style="color: #fff;">IB CAS (Creativity, Activity, Service)</strong> 
            project to promote financial literacy among high school students. The goal is to make investing 
            knowledge accessible and engaging.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #fff; margin-bottom: 1rem;">🎯 CAS Learning Outcomes</h3>
            <ul style="color: #9ca3af; line-height: 2;">
                <li><strong style="color: #6366f1;">Creativity</strong> — Designing & building a web application</li>
                <li><strong style="color: #a855f7;">Activity</strong> — Active engagement with financial markets</li>
                <li><strong style="color: #ec4899;">Service</strong> — Sharing financial education with peers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="premium-card">
            <h3 style="color: #fff; margin-bottom: 1rem;">🛠️ Technology Stack</h3>
            <ul style="color: #9ca3af; line-height: 2;">
                <li><strong style="color: #fff;">Python</strong> — Core programming</li>
                <li><strong style="color: #fff;">Streamlit</strong> — Web framework</li>
                <li><strong style="color: #fff;">Plotly</strong> — Interactive charts</li>
                <li><strong style="color: #fff;">OpenBB</strong> — Free Bloomberg alternative</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="premium-card" style="margin-top: 1rem;">
        <h3 style="color: #fff; margin-bottom: 1rem;">⚠️ Disclaimer</h3>
        <p style="color: #9ca3af; line-height: 1.8;">
            This application is for <strong style="color: #fff;">educational purposes only</strong>. 
            Nothing in this app constitutes financial advice. Always do your own research and consult 
            with qualified financial advisors before making any investment decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)
