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
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
import os
import re

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
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Reset */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* App Background */
    .stApp {
        background: #08090d;
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(56, 189, 248, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(139, 92, 246, 0.04) 0%, transparent 50%);
        background-attachment: fixed;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* ── Kill the Streamlit Community Cloud viewer bar ────────────────────
       The "Built with Streamlit 🎈 / Fullscreen ⤢" strip at the bottom of the
       page is injected by the Community Cloud host. Its "Fullscreen" control is
       a link to the BARE app URL (no ?embed), so inside the finlitpro.org
       iframe clicking it navigates the user out to finlitpro.streamlit.app.
       Hide the whole strip — badge + fullscreen link — by every selector it
       is known to use across Streamlit versions. */
    [data-testid="stStatusWidget"],
    [data-testid="stAppViewBadge"],
    [data-testid="stBottomBlockContainer"] [class*="viewerBadge"],
    [class*="viewerBadge"],
    [class*="ViewerBadge"],
    [class*="stViewerBadge"],
    a[href*="streamlit.io"],
    a[href*="share.streamlit.io"],
    a[href*="streamlit.app"],
    a[title="Fullscreen"],
    a[aria-label="Fullscreen"],
    button[title="Fullscreen"],
    button[aria-label="Fullscreen"],
    button[title="Enter Fullscreen"],
    button[title="Exit Fullscreen"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Double-clicking UI chrome should not text-select it — on the gradient
       titles the selection box exposes the solid text and looks broken.
       Real content (paragraphs, glossary, tables, inputs) stays selectable. */
    .hero-title, .hero-subtitle, .hero-badge, .section-header,
    .sidebar-brand, .sidebar-title, .sidebar-logo,
    .feature-title, .feature-desc, .feature-icon,
    .metric-label, .metric-value, .metric-change,
    [data-testid="stSidebar"] .stRadio,
    .stButton button,
    .stTabs [data-baseweb="tab"] {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        user-select: none !important;
    }

    /* On-brand selection color for the content that IS selectable */
    ::selection { background: rgba(99, 102, 241, 0.35); color: #ffffff; }
    ::-moz-selection { background: rgba(99, 102, 241, 0.35); color: #ffffff; }

    [data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none;
    }

    /* Sidebar collapse button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        color: #94a3b8 !important;
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(12px) !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover {
        background: rgba(30, 41, 59, 0.9) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* HERO SECTION */
    /* ═══════════════════════════════════════════════════════════ */

    .hero-container {
        text-align: center;
        padding: 4rem 0 3rem 0;
        margin-bottom: 2rem;
        position: relative;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 50px;
        padding: 0.4rem 1.2rem;
        font-size: 0.7rem;
        color: #818cf8;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        letter-spacing: -3px;
        line-height: 1.05;
        margin: 0;
        padding: 0;
        background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 40%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #475569;
        font-weight: 400;
        margin-top: 1rem;
        letter-spacing: 0.3px;
        line-height: 1.6;
    }

    .hero-glow {
        position: absolute;
        top: -100px;
        left: 50%;
        transform: translateX(-50%);
        width: 800px;
        height: 500px;
        background: radial-gradient(ellipse, rgba(99, 102, 241, 0.06) 0%, transparent 70%);
        pointer-events: none;
        z-index: -1;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* PREMIUM CARDS */
    /* ═══════════════════════════════════════════════════════════ */

    .premium-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-radius: 16px;
        padding: 1.75rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
    }

    .premium-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                    0 0 0 1px rgba(99, 102, 241, 0.1);
    }

    /* Feature Card */
    .feature-card {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-radius: 16px;
        padding: 2rem;
        height: 100%;
        transition: all 0.3s ease;
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
        background: radial-gradient(circle, rgba(99, 102, 241, 0.06) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
    }

    .feature-card:hover::after {
        opacity: 1;
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }

    .feature-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.7;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* METRIC CARDS */
    /* ═══════════════════════════════════════════════════════════ */

    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-radius: 14px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7);
        opacity: 0.7;
    }

    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }

    .metric-label {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #f1f5f9;
        letter-spacing: -1px;
        font-family: 'JetBrains Mono', 'Inter', monospace;
    }

    .metric-change {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.3rem;
        font-family: 'JetBrains Mono', 'Inter', monospace;
    }

    .metric-positive { color: #34d399; }
    .metric-negative { color: #f87171; }

    /* ═══════════════════════════════════════════════════════════ */
    /* SIDEBAR */
    /* ═══════════════════════════════════════════════════════════ */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1120 0%, #0a0f1e 100%);
        border-right: 1px solid rgba(51, 65, 85, 0.3);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1.25rem;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(51, 65, 85, 0.3);
        margin-bottom: 1.5rem;
    }

    .sidebar-logo {
        font-size: 2rem;
    }

    .sidebar-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f1f5f9;
        letter-spacing: -0.5px;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* BUTTONS */
    /* ═══════════════════════════════════════════════════════════ */

    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.75rem;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* INPUTS */
    /* ═══════════════════════════════════════════════════════════ */

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        padding: 0.7rem 1rem !important;
        transition: all 0.25s ease !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.12) !important;
    }

    /* Selectbox selected value — make the chosen number/text visible.
       BaseWeb collapses the value element to height:0 (overflow:hidden), so the
       text is present but clipped to nothing; restore its height + color. */
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] div[role="button"],
    .stSelectbox div[data-baseweb="select"] span {
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
    }
    .stSelectbox div[data-baseweb="select"] div[value] {
        height: auto !important;
        min-height: 1.4em !important;
        line-height: 1.4 !important;
        overflow: visible !important;
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
    }

    /* Dropdown menu popover — replace BaseWeb's default grey with the app theme */
    div[data-baseweb="popover"] ul[role="listbox"],
    ul[data-baseweb="menu"],
    div[data-baseweb="menu"] {
        background: #0f172a !important;
        border: 1px solid rgba(99, 102, 241, 0.30) !important;
        border-radius: 10px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55) !important;
        padding: 4px !important;
    }
    li[role="option"],
    ul[data-baseweb="menu"] li {
        background: transparent !important;
        color: #cbd5e1 !important;
        border-radius: 8px !important;
        transition: background 0.15s ease !important;
    }
    li[role="option"]:hover,
    ul[data-baseweb="menu"] li:hover,
    li[role="option"][aria-selected="true"],
    li[aria-selected="true"] {
        background: rgba(99, 102, 241, 0.20) !important;
        color: #ffffff !important;
    }

    /* Hide Plotly's grey modebar toolbar on every chart for a cleaner look */
    .js-plotly-plot .modebar,
    .modebar-container {
        display: none !important;
    }

    /* Chat input styling */
    .stChatInput > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(51, 65, 85, 0.5) !important;
        border-radius: 12px !important;
    }

    .stChatMessage {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(51, 65, 85, 0.3) !important;
        border-radius: 12px !important;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* SECTION HEADERS */
    /* ═══════════════════════════════════════════════════════════ */

    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 2rem 0 1.25rem 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        letter-spacing: -0.5px;
    }

    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(51, 65, 85, 0.5), transparent);
        margin: 1.5rem 0;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* SIGNAL BADGES */
    /* ═══════════════════════════════════════════════════════════ */

    .signal-bullish {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34d399;
        padding: 0.4rem 0.9rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.8rem;
        margin: 0.2rem;
    }

    .signal-bearish {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.25);
        color: #f87171;
        padding: 0.4rem 0.9rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.8rem;
        margin: 0.2rem;
    }

    .signal-neutral {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(251, 191, 36, 0.08);
        border: 1px solid rgba(251, 191, 36, 0.25);
        color: #fbbf24;
        padding: 0.4rem 0.9rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.8rem;
        margin: 0.2rem;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* TABS */
    /* ═══════════════════════════════════════════════════════════ */

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: transparent;
        padding: 0.25rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        border: 1px solid rgba(51, 65, 85, 0.3);
        color: #94a3b8;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.25s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.06);
        border-color: rgba(99, 102, 241, 0.2);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.12) !important;
        border-color: rgba(99, 102, 241, 0.4) !important;
        color: #e2e8f0 !important;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* QUIZ STYLING */
    /* ═══════════════════════════════════════════════════════════ */

    .quiz-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-radius: 14px;
        padding: 1.75rem;
        margin: 0.75rem 0;
    }

    .quiz-question {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }

    .quiz-correct {
        background: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
    }

    .quiz-wrong {
        background: rgba(239, 68, 68, 0.06);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
    }

    .quiz-score {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* PROGRESS BAR */
    /* ═══════════════════════════════════════════════════════════ */

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
        border-radius: 8px;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* SCROLLBAR */
    /* ═══════════════════════════════════════════════════════════ */

    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.5);
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* RADIO BUTTONS (NAV) */
    /* ═══════════════════════════════════════════════════════════ */

    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 0.55rem 0.9rem;
        margin: 0;
        transition: all 0.2s ease;
        cursor: pointer;
        font-size: 0.9rem;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(99, 102, 241, 0.06);
        border-color: rgba(51, 65, 85, 0.3);
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
    }

    /* Glass Effect */
    .glass {
        background: rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-radius: 16px;
    }

    /* Data Table */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(15, 23, 42, 0.5) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(51, 65, 85, 0.3) !important;
    }

    /* Stat row for dashboard */
    .stat-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(51, 65, 85, 0.2);
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-ticker {
        font-weight: 700;
        color: #f1f5f9;
        font-size: 0.95rem;
        min-width: 60px;
        font-family: 'JetBrains Mono', monospace;
    }
    .stat-name {
        color: #64748b;
        font-size: 0.8rem;
        flex: 1;
    }
    .stat-price {
        font-weight: 700;
        color: #e2e8f0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
    }

    /* ── Glossary hover tooltips (Grammarly-style popup) ── */
    .gloss {
        position: relative;
        border-bottom: 1.5px dashed rgba(99, 102, 241, 0.7);
        color: #c7d2fe;
        cursor: help;
        font-weight: 600;
        white-space: nowrap;
    }
    .gloss .gloss-pop {
        visibility: hidden;
        opacity: 0;
        transform: translateX(-50%) translateY(6px);
        position: absolute;
        bottom: 150%;
        left: 50%;
        width: max-content;
        max-width: 320px;
        background: #0b1120;
        border: 1px solid rgba(99, 102, 241, 0.45);
        border-radius: 12px;
        padding: 0.7rem 0.85rem;
        font-size: 0.8rem;
        font-weight: 400;
        line-height: 1.5;
        color: #cbd5e1;
        white-space: normal;
        text-align: left;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
        z-index: 10000;
        transition: opacity 0.15s ease, transform 0.15s ease;
        pointer-events: none;
    }
    .gloss .gloss-pop::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: rgba(99, 102, 241, 0.45);
    }
    .gloss-pop-term {
        display: block;
        font-weight: 700;
        font-size: 0.82rem;
        color: #a5b4fc;
        margin-bottom: 0.25rem;
        letter-spacing: 0.2px;
    }
    .gloss:hover .gloss-pop {
        visibility: visible;
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }
    /* Let popups escape container clipping */
    [data-testid="stMarkdownContainer"],
    [data-testid="stVerticalBlock"],
    .element-container { overflow: visible !important; }

    /* ── Glossary reference page cards ── */
    .gloss-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 0.9rem;
        margin-top: 1rem;
    }
    .gloss-card {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(51, 65, 85, 0.4);
        border-left: 3px solid #6366f1;
        border-radius: 12px;
        padding: 0.9rem 1.05rem;
        transition: all 0.2s ease;
    }
    .gloss-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.06);
        transform: translateY(-2px);
    }
    .gloss-card-term {
        font-weight: 700;
        color: #f1f5f9;
        font-size: 0.98rem;
        margin-bottom: 0.35rem;
    }
    .gloss-card-def {
        color: #94a3b8;
        font-size: 0.84rem;
        line-height: 1.5;
    }
    .gloss-cat {
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #818cf8;
        background: rgba(99, 102, 241, 0.12);
        padding: 0.15rem 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
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

# ═══════════════════════════════════════════════════════════
# GLOSSARY  —  hover-to-define terms (Grammarly-style popups)
# ═══════════════════════════════════════════════════════════
GLOSSARY = {
    # ── Markets ──
    "Bull Market": "A prolonged period of rising prices, typically 20%+ up from recent lows. Signals optimism and economic expansion.",
    "Bear Market": "A prolonged period of falling prices, typically 20%+ down from recent highs. Signals pessimism and fear — named for how a bear swipes its paws downward.",
    "Bullish": "An optimistic view that a price will go UP. If you are bullish on Apple, you expect Apple stock to rise.",
    "Bearish": "A pessimistic view that a price will go DOWN. If you are bearish on a stock, you expect it to fall.",
    "Volatility": "How much and how fast a price swings up and down. High volatility means bigger, riskier swings — it is the main measure of risk.",
    "Liquidity": "How quickly an asset can be turned into cash without losing value. Cash is highly liquid; real estate is illiquid.",
    "Market Cap": "Market capitalization = share price × total shares outstanding. The total dollar value of a company.",
    "IPO": "Initial Public Offering — the first time a private company sells shares to the public on a stock exchange.",
    "Ticker Symbol": "A short unique code for a security, e.g. AAPL for Apple, MSFT for Microsoft.",
    "Shareholder": "Someone who owns shares (stock) in a company and therefore owns a piece of it.",
    "Stock Exchange": "A marketplace where stocks are bought and sold, such as the NYSE or NASDAQ.",
    "S&P 500": "An index of 500 of the largest US public companies — the most common benchmark for the US stock market.",
    "Benchmark": "A standard you measure performance against, e.g. comparing your portfolio's return to the S&P 500.",
    "Concentration Risk": "The danger of putting too much money in one investment. If that single bet fails, the whole portfolio collapses.",

    # ── Technical Analysis ──
    "Moving Average": "The average closing price over a set number of days, recalculated daily to smooth out noise and reveal the trend.",
    "SMA": "Simple Moving Average — the average price over a set period, giving each day equal weight. Smooths price to show the trend.",
    "SMA 20": "The 20-day simple moving average (average close of the last 20 days). Tracks the SHORT-term trend; price above it is short-term bullish.",
    "SMA 50": "The 50-day simple moving average (average close of the last 50 days). Tracks the MEDIUM-term trend.",
    "SMA 200": "The 200-day simple moving average (average close of the last 200 days). Tracks the LONG-term trend; widely watched as the dividing line between bull and bear.",
    "RSI": "Relative Strength Index — a momentum gauge from 0 to 100. Above 70 = overbought (may fall); below 30 = oversold (may rise).",
    "MACD": "Moving Average Convergence Divergence — a momentum indicator. MACD line above its signal line = bullish momentum; below = bearish.",
    "Golden Cross": "A bullish signal where the 50-day moving average crosses ABOVE the 200-day moving average, often marking the start of an uptrend.",
    "Death Cross": "A bearish signal where the 50-day moving average crosses BELOW the 200-day moving average, often warning of a downtrend.",
    "Overbought": "When a price has risen so fast it may be due for a pullback. Often flagged by RSI above 70.",
    "Oversold": "When a price has fallen so fast it may be due to bounce back. Often flagged by RSI below 30.",
    "Support": "A price level where buying tends to halt a decline — a 'floor' under the price.",
    "Resistance": "A price level where selling tends to cap a rise — a 'ceiling' over the price.",
    "Breakout": "When price pushes above a resistance level, often signaling further gains.",

    # ── Valuation ──
    "P/E Ratio": "Price-to-Earnings = share price ÷ EPS. How many dollars investors pay for $1 of earnings. A high P/E means pricey or high growth expected.",
    "EPS": "Earnings Per Share = (net income − preferred dividends) ÷ shares outstanding. The profit assigned to each share; a primary driver of stock price.",
    "EBITDA": "Earnings Before Interest, Taxes, Depreciation and Amortization. Core operating profit that strips out financing and accounting effects so companies can be compared fairly.",
    "Dividend": "A cash payment a company distributes to shareholders out of its profits, often quarterly.",
    "Dividend Yield": "Annual dividend ÷ share price, as a %. Example: a $2.28 dividend giving a 2.41% yield. Shows the income a stock pays.",
    "Payout Ratio": "The share of earnings paid out as dividends. A 64% payout ratio means 64% of profit is returned to shareholders.",

    # ── Financial Statements ──
    "Balance Sheet": "A snapshot of what a company OWNS vs OWES at one moment. Follows Assets = Liabilities + Equity. Called the investor's X-ray.",
    "Income Statement": "Also called the P&L. Shows profitability over a period: revenue minus costs and expenses, ending in net income.",
    "Cash Flow Statement": "Tracks actual cash moving in and out across operating, investing, and financing activities. Net income is an opinion; cash flow is a fact.",
    "Assets": "Everything a company owns that has value — cash, inventory, property, equipment, intellectual property.",
    "Liabilities": "Everything a company owes — debt, loans, and bills (payables).",
    "Equity": "What is left for owners after subtracting liabilities from assets — the company's net worth, including retained earnings.",
    "Retained Earnings": "Profits a company has kept and reinvested rather than paying out as dividends.",
    "Revenue": "The top line — total money earned from sales before any costs are subtracted.",
    "COGS": "Cost of Goods Sold — the direct costs of producing what a company sells (materials, labor).",
    "Gross Profit": "Revenue minus COGS — profit before overhead and other expenses.",
    "Operating Income": "Profit from core operations after subtracting operating expenses (SG&A, R&D) from gross profit.",
    "Net Income": "The bottom line — final profit after ALL costs, including taxes and interest, are subtracted.",
    "Gross Margin": "Gross profit ÷ revenue. Measures production efficiency — how much of each sales dollar survives direct costs.",
    "Operating Margin": "Operating income ÷ revenue. Profitability from core operations after overhead.",
    "Net Margin": "Net income ÷ revenue. The share of every sales dollar that becomes final profit. Revenue is vanity, margin is sanity.",
    "Debt": "Borrowed money that must be repaid, usually with interest.",
    "Leverage": "Using borrowed money to invest. It magnifies gains but also magnifies losses — and the debt must always be repaid.",

    # ── Ratios ──
    "Current Ratio": "Current assets ÷ current liabilities. Can the company pay its short-term bills now? Above 1 is healthier.",
    "Quick Ratio": "(Current assets − inventory) ÷ current liabilities. A stricter liquidity test using only cash and near-cash.",
    "Net Debt to EBITDA": "Total debt minus cash, divided by EBITDA. Roughly how many years of earnings to pay off debt. Lower is safer.",
    "Receivables Days": "Average number of days a company takes to collect payment from customers. Faster (fewer days) is better.",
    "Debt-to-Equity": "Total debt ÷ shareholder equity. How much a company relies on borrowing vs owners' money. High = riskier.",

    # ── Funds ──
    "Mutual Fund": "A pooled fund that gathers money from many investors to buy a diversified mix of assets. Priced once per day at NAV; often actively managed.",
    "ETF": "Exchange-Traded Fund — a fund that trades on an exchange like a stock throughout the day. Usually passive and low-cost, tracking an index.",
    "NAV": "Net Asset Value — the price per share of a fund: (total assets − liabilities) ÷ shares outstanding.",
    "Expense Ratio": "The annual fee a fund charges as a % of your investment. A 0.50% ratio costs $5/year per $1,000. Fees compound and eat returns.",
    "Index Fund": "A passive fund that simply tracks a market index (like the S&P 500). Low fees — the 'autopilot' approach.",
    "Active Management": "A manager hand-picks investments trying to beat the market, charging higher fees for that expertise.",
    "Passive Investing": "Tracking an index instead of trying to beat it. Lower cost and broad diversification.",
    "Capital Gains Distribution": "Profits a fund passes to investors after selling assets within the fund at a gain.",
    "Target Date Fund": "A fund that automatically shifts from risky to safe assets as a target year (like retirement) approaches.",
    "Money Market Fund": "A very low-risk fund holding short-term cash-like instruments. Low return, high liquidity.",
    "Bond Fund": "A fund that invests mainly in bonds, aiming for steady income with moderate risk.",

    # ── Rates & Yields ──
    "Interest Rate": "The price you PAY to borrow money, as a % of the loan. Think of it as an expense.",
    "Yield": "The income you EARN on an investment per year, as a %. Think of it as the 'rent' your money collects — it excludes price gains.",
    "Total Return": "Total Return = Yield + Capital Appreciation. The full gain from an investment: income received PLUS the change in its price.",
    "Capital Appreciation": "The increase in an asset's price. It is 'paper' (unrealized) wealth until you actually sell.",
    "Federal Funds Rate": "The interest rate US banks charge each other overnight, set in a target range by the Federal Reserve. The baseline for nearly all other rates.",
    "EFFR": "Effective Federal Funds Rate — the actual average overnight rate banks lend to each other. The closest thing to a risk-free baseline rate.",
    "Risk-Free Rate": "The return on an essentially riskless investment, usually a US Treasury. The baseline all other returns are compared to.",
    "Yield Curve": "A graph of bond yields across maturities (3-month to 30-year). Its shape signals market expectations for the economy.",
    "Inverted Yield Curve": "When short-term bonds yield MORE than long-term bonds — unusual, and a classic warning sign of economic uncertainty or recession.",
    "Risk Premium": "The extra yield investors demand for taking on more risk. A riskier borrower must pay a higher rate.",
    "Spread": "The difference between two rates or yields — e.g. a risky corporate bond vs a safe Treasury. The strategy: grow your yields, shrink your rates.",
    "Credit Score": "A number (like a FICO score, 300–850) summarizing how reliably you repay debt. A higher score earns you lower interest rates.",
    "FICO Score": "The most widely used credit score (300–850). Lenders use it to set your rate: higher score = lower APR.",
    "APR": "Annual Percentage Rate — the yearly cost of borrowing, including interest and fees, as a %.",
    "Treasury": "A bond issued by the US government. Considered the safest investment and the basis for the risk-free rate.",
    "Corporate Bond": "A bond issued by a company. Pays more than Treasuries to compensate for higher default risk; riskier issuers pay even more.",
    "Coupon": "The fixed interest payment a bond pays its holder, usually expressed as an annual rate.",
    "Default Risk": "The chance a borrower fails to pay interest or repay principal. Higher default risk demands a higher yield.",
    "Interest Rate Risk": "The risk that rising rates lower the value of bonds you already hold — new bonds pay more, so yours are worth less.",
    "Inflation Risk": "The risk that rising prices erode your money's purchasing power, so low returns may not keep up with the cost of living.",

    # ── Asset Classes ──
    "Cash Equivalents": "The safest, most liquid assets — savings, money market funds, CDs. Low risk and low return.",
    "Fixed Income": "Investments that pay regular set payments and return principal at maturity — mainly bonds. Steady income, moderate risk.",
    "Bonds": "Loans you make to a government or company. They pay you interest (coupons) and return your principal at maturity.",
    "Equities": "Another word for stocks — ownership shares in companies. Higher risk, driven by capital appreciation and dividends.",
    "Stock": "A share of ownership in a company. Owning stock makes you a part-owner entitled to a slice of profits.",
    "Real Estate": "Property (homes, commercial buildings) held for rental income and price appreciation; a tangible inflation hedge.",
    "Real Assets": "Tangible assets like real estate and commodities (oil, gold) that hold physical value and hedge inflation.",
    "Alternative Investments": "Non-traditional assets — hedge funds, private equity, commodities, crypto. High complexity, low liquidity, high risk/reward.",
    "Commodities": "Physical goods like gold, silver, oil and corn that trade on markets and often hedge inflation.",
    "Hedge Fund": "A lightly regulated, high-fee fund using complex strategies for wealthy and institutional investors. High risk, low liquidity.",
    "Private Equity": "Investing directly in private companies not traded on public exchanges. Illiquid and long-term.",
    "CDs": "Certificates of Deposit — bank deposits locked for a fixed term in exchange for a guaranteed rate. Safe but illiquid until maturity.",
    "Crypto": "Cryptocurrency like Bitcoin — a digital asset known for very high volatility; classed as an alternative investment.",

    # ── Strategy ──
    "Asset Allocation": "Dividing your portfolio across asset classes (stocks, bonds, real estate, cash). The single biggest driver of long-term risk and return.",
    "Diversification": "Spreading money across many investments so no single loss can sink you. Don't put all your eggs in one basket.",
    "Rebalancing": "Periodically selling winners and buying laggards to return to your target allocation, since winners grow and skew your risk.",
    "Risk Tolerance": "How much volatility you can stomach without panic-selling — the 'sleep factor.' Can you handle a 20% drop calmly?",
    "Time Horizon": "How long until you need the money. Longer horizons let you take more risk and ride out volatility.",
    "Financial Goals": "What the money is for — retirement, a house, education. Goals drive how you invest.",
    "IPS": "Investment Policy Statement — a written 'constitution' for a portfolio. Defines goals, risk, allocation, roles, constraints and benchmarks to enforce discipline.",
    "Risk-Adjusted Return": "How much return you earn for the risk you take. Good allocation optimizes return for your specific risk tolerance.",
    "Capital Preservation": "A strategy focused on protecting your money rather than growing it — prioritizing safety and liquidity over returns.",
    "Compound Interest": "Earning interest on your interest as well as your principal, so growth accelerates over time. Einstein called it the eighth wonder of the world.",
    "Rule of 72": "A shortcut: 72 ÷ interest rate ≈ years to double your money. At 8%, money doubles in about 9 years.",
    "Dollar-Cost Averaging": "Investing a fixed amount on a regular schedule regardless of price, which smooths out your average cost over time.",
    "Principal": "The original amount of money you invest or borrow, before any interest or returns.",
    "Beta": "A measure of a stock's volatility relative to the overall market. Beta of 1 moves with the market; above 1 is more volatile.",
    "Stop-Loss": "An order that automatically sells a position once it falls to a preset price, capping your loss.",
}

# Case-insensitive lookup index
_GLOSSARY_LC = {k.lower(): (k, v) for k, v in GLOSSARY.items()}


def g(term, label=None):
    """Return an inline HTML span that shows a hover popup definition."""
    label = label or term
    hit = _GLOSSARY_LC.get(term.lower())
    if not hit:
        return label
    canonical, definition = hit
    safe = definition.replace("<", "&lt;").replace(">", "&gt;").replace("$", "&#36;")
    return (
        f'<span class="gloss">{label}'
        f'<span class="gloss-pop"><span class="gloss-pop-term">{canonical}</span>{safe}</span></span>'
    )


def glossify(text):
    """Replace [[term]] or [[term|label]] markers in markdown with hover spans."""
    def _repl(m):
        key = m.group(1).strip()
        lab = m.group(2).strip() if m.group(2) else None
        return g(key, lab)
    return re.sub(r"\[\[([^\]|]+?)(?:\|([^\]]+))?\]\]", _repl, text)


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

🐂 **[[Bull Market]]**
- Prices rising 20%+ from recent lows
- Investor optimism & confidence
- Economic expansion

🐻 **[[Bear Market]]**
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

### Growth of &#36;10,000 at 10% Annual Return

| Years | Value | Total Growth |
|-------|-------|--------------|
| 5 | &#36;16,105 | +61% |
| 10 | &#36;25,937 | +159% |
| 20 | &#36;67,275 | +573% |
| 30 | **&#36;174,494** | +1,645% |

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

#### [[Moving Average|Moving Averages]] (MA)
- **[[SMA 20]]**: Short-term trend (20-day average)
- **[[SMA 50]]**: Medium-term trend
- **[[SMA 200]]**: Long-term trend
- Price > MA = **[[Bullish]]** ✅
- Price < MA = **[[Bearish]]** ❌

#### [[RSI]] (Relative Strength Index)
Measures momentum on a scale of 0-100:
- **RSI > 70**: Overbought 🔴 (potential reversal down)
- **RSI < 30**: Oversold 🟢 (potential reversal up)
- **RSI 30-70**: Neutral zone

#### [[MACD]] (Moving Average Convergence Divergence)
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
- Stock ABC trades at &#36;100
- You buy a &#36;105 CALL for &#36;2 (premium)
- If stock rises to &#36;115 → You profit &#36;8 (&#36;115 - &#36;105 - &#36;2)
- If stock stays below &#36;105 → You lose &#36;2 (premium only)

**PUT Option Example:**
- Stock ABC trades at &#36;100
- You buy a &#36;95 PUT for &#36;2 (premium)
- If stock falls to &#36;85 → You profit &#36;8 (&#36;95 - &#36;85 - &#36;2)
- If stock stays above &#36;95 → You lose &#36;2 (premium only)

---

### The Greeks (Option Sensitivity)

| Greek | What It Measures |
|-------|------------------|
| **Delta (Δ)** | Price change per &#36;1 stock move |
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

# ── Curriculum modules (DIME Level 2) — added as extra Learn tabs ──
EDUCATION_MODULES["🩺 Financial Statements"] = r"""
## Financial Statements & Diagnostics

Financial statements are the **investor's X-ray** — they reveal a company's quantitative health (profit, debt) even when the story sounds great.

---

### The Three Core Statements

**1. The [[Income Statement]] (P&L)** — tracks profitability over a period. It flows from the top line to the bottom line:

- [[Revenue]] *(top line)* — total money earned from sales
- − [[COGS]] — direct production costs
- = [[Gross Profit]]
- − Operating Expenses (SG&A, R&D, overhead)
- = [[Operating Income]]
- − Taxes & Interest
- = [[Net Income]] *(bottom line — the final profit)*

**2. The [[Balance Sheet]]** — a snapshot at one instant of what a company owns vs owes:

> **[[Assets]] = [[Liabilities]] + [[Equity]]**

High [[Equity]] (owns more than it owes) = stable. High [[Liabilities]] (owes more than it owns) = high-risk and [[Leverage|leveraged]].

**3. The [[Cash Flow Statement]]** — tracks the actual cash moving in and out (Operating, Investing, Financing). A company can show a profit on paper and still go bankrupt if it runs out of cash. *Net income is an opinion; cash flow is a fact.*

---

### Measuring Efficiency: Margins
> *"It's not just what you make, it's what you keep."*

- [[Gross Margin]] = Gross Profit ÷ Revenue → production efficiency
- [[Operating Margin]] = Operating Income ÷ Revenue → core-business efficiency
- [[Net Margin]] = Net Income ÷ Revenue → the true bottom line

*Revenue is vanity, margin is sanity.*

---

### The Analyst's Toolkit: Critical Ratios

| Ratio | Formula | What it tells you |
|-------|---------|-------------------|
| Current Ratio | Current Assets ÷ Current Liabilities | Can they pay bills NOW? |
| Quick Ratio | (Current Assets − Inventory) ÷ Current Liabilities | Liquidity using only cash-like assets |
| Net Debt to EBITDA | (Debt − Cash) ÷ EBITDA | Years to pay off debt (lower is better) |
| Receivables Days | Avg days to collect | Speed of collecting payments (faster is better) |

*Hover for definitions:* [[Current Ratio]] · [[Quick Ratio]] · [[Net Debt to EBITDA]] · [[Receivables Days]]

> *Ratios remove emotion. Never trust a story; trust the math.*

---

### Case Study — Leverage Kills: Nordstrom vs JCPenney
- **Nordstrom (survivor):** Net Debt \$1.6bn, Net-Debt/EBITDA ≈ **1.0x** (safe). Survived COVID-19 on a strong balance sheet.
- **JCPenney (casualty):** Net Debt \$3.6bn, ratio ≈ **3.6x** (critical). Went bankrupt.

*"JCPenney didn't die from bad clothes; they died from bad debt."* [[Leverage]] magnifies gains but guarantees losses.

---

### Case Study — Efficiency: FedEx vs UPS
| Metric | FedEx | UPS |
|--------|-------|-----|
| Revenue | \$87.4B | \$90.7B |
| Gross Margin | **21.30%** | 17.54% |
| Operating Margin | 6.72% | **8.84%** |
| Net Margin | 4.44% | **6.25%** |

FedEx wins on production efficiency (gross margin), but UPS runs leaner overhead → better operating and net margins. *Revenue is vanity, margin is sanity.*

---

### The "Buy" Decision Matrix — Kohl's (KSS): a **NO**
- Revenue Growth **−4.20%** (shrinking) · Profit Margin **1.66%** (low)
- [[Debt-to-Equity]] **195%** (high risk) · [[Current Ratio]] **1.08** (barely liquid)

High debt + shrinking revenue + low margin = high risk. *Sometimes the best trade is the one you don't make.*
"""

EDUCATION_MODULES["🧮 Valuation Metrics"] = r"""
## Valuation Metrics

How do we decide if a company is a **'Buy'**? We turn financial statements into comparable numbers.

---

### [[EPS]] — Earnings Per Share
**EPS = (Net Income − Preferred Dividends) ÷ Shares Outstanding.** The slice of profit attached to each share — a primary driver of stock price.

### [[EBITDA]]
*Earnings Before Interest, Taxes, Depreciation & Amortization.* Isolates **core operational profitability** by removing financing and accounting effects, so you can fairly compare companies with different tax and debt structures.

### [[P/E Ratio]] — Price-to-Earnings
**P/E = Price ÷ EPS.** How many dollars investors pay for \$1 of earnings. High P/E = expensive, or high growth expected.

### [[Market Cap]]
Share price × shares outstanding = the company's total market value.

---

### The Diagnostic Conflict (UPS vs FedEx)
- **UPS:** earnings growing **+37%**, but the stock price **fell −10%**.
- **FedEx:** earnings shrinking **−14%**, but the stock price **rose +14%**.

Which signal do you trust — market sentiment or fundamentals?

> *"The market is a voting machine in the short run, but a weighing machine in the long run."* — Benjamin Graham

Short term, prices follow emotion (voting). Long term, they follow real earnings (weighing).
"""

EDUCATION_MODULES["📜 Investment Policy (IPS)"] = r"""
## The Investment Policy Statement (IPS)

> *"Successful investing is 10% picking stocks and 90% discipline."*

An [[IPS]] is the **constitution** for your portfolio — the governing law every decision must obey. It enforces:
- **Discipline** — prevents emotional reactions to [[Volatility|market volatility]].
- **Accountability** — clearly defines who is responsible for what.
- **Alignment** — every analyst agrees on the goal *before* trading begins.

---

### The Six Pillars of an Effective IPS
1. **[[Financial Goals|Goals & Objectives]]** — what the investor wants (retirement, growth) and the [[Time Horizon]].
2. **[[Risk Tolerance]]** — how much volatility is acceptable.
3. **[[Asset Allocation]]** — guidelines for splitting money among stocks, bonds, etc.
4. **Roles & Responsibilities** — who does what (client, advisor, custodian).
5. **Constraints** — limits such as [[Liquidity]] needs or ethical screens.
6. **Performance [[Benchmark|Benchmarks]]** — how success is measured (e.g. vs the [[S&P 500]]).

---

### The \$100,000 Portfolio Challenge
You manage a shared **\$100,000 virtual portfolio** on Personal Finance Lab. The constraint: justify each investment with at least **three** financial metrics (e.g. [[P/E Ratio]], [[EPS]] growth, [[Debt-to-Equity]]).

> *"You are not gambling. You are allocating capital based on data. If you can't explain the 'Why' with numbers, don't buy it."*

**Team roles:** Lead Analyst (reads the X-ray) · Strategy Manager (buy/sell calls) · Data Tracker (performance) · Communications Lead (reporting).

---

### IPS Development Process
**Gather Info → Define Objectives → Formulate Strategy → Draft Document → Review & Sign-Off.**
It is iterative — the team agrees the rules *before* the first trade is placed.
"""

EDUCATION_MODULES["⚖️ Asset Allocation"] = r"""
## Asset Allocation & Diversification

### Winners Rotate
The top asset class one year is frequently at the bottom the next — the winner of 2023 was often the loser of 2022. Because we **cannot predict** the winner, we [[Diversification|diversify]] across classes to capture growth while limiting losses.

### What is [[Asset Allocation]]?
Dividing a portfolio among different asset classes — stocks, bonds, real estate, cash. It:
- Reduces [[Volatility]] (smooths the highs and lows)
- Improves [[Risk-Adjusted Return|risk-adjusted returns]]
- Provides stability (prevents collapse from a single crash)

---

### The Risk vs Reward Spectrum *(low → high)*
1. **[[Cash Equivalents]]** — money market, [[CDs]]. Least risky, highly liquid, low return.
2. **[[Fixed Income]] ([[Bonds]])** — Treasuries, corporates. Regular interest, relatively stable.
3. **[[Real Estate]]** — rental income, but subject to market swings.
4. **[[Equities]]** *(stocks)* — ownership; value fluctuates with company and market performance.
5. **[[Alternative Investments]]** — [[Hedge Fund|hedge funds]], [[Crypto]], [[Commodities]]. Riskiest, complex, illiquid.

**Risks to know:** [[Inflation Risk]] erodes cash; bonds carry [[Default Risk]] and [[Interest Rate Risk]].

---

### The Three Pillars of Decision-Making
- **[[Financial Goals]] (the What)** — retirement, education, preservation.
- **[[Time Horizon]] (the When)** — longer horizons allow more risk.
- **[[Risk Tolerance]] (the How)** — the 'sleep factor': can you withstand a 20% drop without panic-selling?

---

### Strategy & Maintenance
- **Strategic:** long-term target, strict adherence.
- **Tactical:** short-term tilts for opportunity.
- **Dynamic:** rules-based automatic adjustments.

The crucial step is **[[Rebalancing]]** — sell high, buy low to reset to your target, because winners grow and skew your risk.

---

### Two Scenarios
- **Short-term goal** (\$50,000 tuition in 2 years): [[Capital Preservation]] — ~45% cash, 45% govt bonds, 10% stocks. You can't afford crypto's ~50% volatility.
- **Long-term goal** (house down payment in 10 years): balanced growth — heavier in [[Equities]], using time to ride out volatility and beat inflation.

> *"It is not about picking the best stock; it is about selecting the right balance for your life."*
"""

EDUCATION_MODULES["🧺 Mutual Funds & ETFs"] = r"""
## Mutual Funds & ETFs

### The Temptation — and the Trap
A single hot stock (Nvidia surged ~90% in a year) is tempting, but it carries **[[Concentration Risk]]**: if that one company stumbles, the whole portfolio collapses. The fix is **pooled capital**.

---

### The Two Vehicles

**[[Mutual Fund]]**
- Trades **once daily** after market close
- Priced at end-of-day [[NAV]]
- Often **[[Active Management|actively managed]]**

**[[ETF]] — Exchange-Traded Fund**
- Trades **like a stock** all day at real-time prices
- Typically **[[Passive Investing|passive]] / [[Index Fund|index-tracking]]**

---

### Key Metrics (KPIs)
- **[[NAV]]** — price per share = (assets − liabilities) ÷ shares.
- **[[Expense Ratio]]** — the annual fee. High fees compound and quietly eat returns, so an [[Active Management|active]] fee must be justified.
- **[[Index Fund]]** — tracks an index automatically; low-fee 'autopilot.'
- Returns come from **[[Dividend|dividends]]**, **[[Capital Gains Distribution|capital gains distributions]]**, and a rising [[NAV]].

---

### Calibrating Risk / Return *(low → high)*
[[Money Market Fund]] → [[Bond Fund]] → [[S&P 500]] [[Index Fund]] → Emerging-Markets Equity.
Other categories: balanced funds, specialty funds, [[Target Date Fund|target-date funds]].

---

### The Investment Committee Simulation
Manage a shared **\$50,000** portfolio — *no individual stock picking.*
**Driving question:** how do investors choose funds to balance cost, diversification, and risk?
**Roles:** Fund Research Analyst · Cost & Expense Analyst · Portfolio Manager · Communications Lead.

Define a strategy (Growth / Stability / Income, a risk level, and a diversification rule like *'no more than 40% in one fund'*), research **2 funds + 2 ETFs**, then justify every dollar by [[NAV]], [[Expense Ratio]], and fund type.
"""

EDUCATION_MODULES["💵 Rates, Yields & Spread"] = r"""
## Rates, Yields & the Spread

### The Core Dichotomy: paying vs earning
- **[[Interest Rate]]** = the *cost of capital* — the price you **pay** for debt (an EXPENSE).
- **[[Yield]]** = the *return on capital* — the income you **earn** (the 'rent' your money collects).

---

### Total Return
> **[[Total Return]] = [[Yield]] + [[Capital Appreciation]]**

[[Yield]] is real, cash-in-hand income (dividends, coupons). [[Capital Appreciation]] is the unrealized rise in price — paper wealth until you sell. Historically, dividend yield made up ~**31.6%** of the S&P 500's total return.

**Example — Starbucks (SBUX):** annual [[Dividend]] \$2.28 → [[Dividend Yield]] **2.41%** (dividend ÷ price), paid quarterly, with a [[Payout Ratio]] of ~64%.

---

### The Pacesetter: the [[Federal Funds Rate]]
The Fed's [[EFFR]] is the [[Risk-Free Rate|risk-free]] baseline. It sets borrowing costs, bank liquidity, and the interest on national debt — it ripples all the way into your wallet.

---

### The Risk Ladder
Safer borrowers pay less; riskier borrowers pay a higher [[Risk Premium]]:

| Rating | Yield | |
|--------|-------|--|
| US Corporate AAA | 4.39% | safest |
| US Corporate AA | 4.52% | |
| US Corporate A | 4.82% | |
| US Corporate BBB | 5.12% | riskier |

The yield gap is the [[Spread]] that compensates for [[Default Risk]].

### The [[Yield Curve]]
Normally, longer-term debt pays more (you demand more to lock money away). An **[[Inverted Yield Curve]]** — short-term yields ABOVE long-term — is a classic signal of economic uncertainty.

---

### Your Personal Rates
Your rate = **Fed baseline + your credit risk.** Mortgages, auto, student, and revolving (credit-card) debt all key off the baseline. A higher **[[FICO Score|credit score]]** earns a lower [[APR]] — and a 1.6% difference over a 30-year mortgage equals tens of thousands of dollars.

---

### The Winning Strategy: manage the [[Spread]]
**Grow these yields:** stocks · bonds · real estate · a business.
**Shrink these rates:** credit cards · auto loans · mortgages · student loans.
Your financial health = maximize the left column, minimize the right.
"""

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
    _pages = ["🏠 Dashboard", "📚 Learn", "📖 Glossary", "📈 Stock Analysis", "🤖 AI Predictor", "💬 AI Advisor", "⚖️ Compare", "🧮 Calculator", "🎭 Risk Profile", "🪙 Crypto", "💼 Portfolio", "🎯 Quiz", "ℹ️ About"]
    _slugs = ["dashboard", "learn", "glossary", "stock-analysis", "ai-predictor", "ai-advisor", "compare", "calculator", "risk-profile", "crypto", "portfolio", "quiz", "about"]
    _slug_to_idx = {s: i for i, s in enumerate(_slugs)}
    _url_slug = st.query_params.get("page", "dashboard")
    _default_idx = _slug_to_idx.get(_url_slug, 0)

    # Seed the radio's state from the URL exactly once. After that the widget
    # owns its own state via the key, so a single click switches pages (passing
    # index= every rerun while writing query_params caused a double-click lag).
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = _pages[_default_idx]

    page = st.radio(
        "Navigation",
        _pages,
        key="nav_page",
        label_visibility="collapsed"
    )

    # Keep the URL slug in sync for deep-linking / refresh, without re-seeding the widget.
    _target_slug = _slugs[_pages.index(page)]
    if st.query_params.get("page") != _target_slug:
        st.query_params["page"] = _target_slug
    
    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 0.75rem 0;">
        <p style="color: #334155; font-size: 0.7rem; margin: 0; letter-spacing: 0.5px;">IB CAS Project 2026</p>
        <p style="color: #475569; font-size: 0.7rem; margin: 0.25rem 0 0 0; font-weight: 600;">Krish Modi</p>
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
        <div class="hero-badge">Financial Literacy Platform</div>
        <h1 class="hero-title">FinLit Pro</h1>
        <p class="hero-subtitle">Real-time market intelligence, AI-powered analysis, and interactive education — built for the next generation of investors.</p>
    </div>
    """, unsafe_allow_html=True)

    # Market Overview first — more professional to lead with data
    st.markdown('<div class="section-header">Live Markets</div>', unsafe_allow_html=True)

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
                    change_symbol = "+" if change >= 0 else ""

                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{icon} {name}</div>
                        <div class="metric-value">${price:,.2f}</div>
                        <div class="metric-change {change_class}">{change_symbol}{change:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{icon} {name}</div>
                        <div class="metric-value">--</div>
                        <div style="color: #475569; font-size: 0.8rem;">Loading</div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{icon} {name}</div>
                    <div class="metric-value">--</div>
                    <div style="color: #475569; font-size: 0.8rem;">Unavailable</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Feature Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📚</span>
            <div class="feature-title">Learn</div>
            <div class="feature-desc">Interactive modules on stocks, technical analysis, options, and risk management.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📊</span>
            <div class="feature-title">Analyze</div>
            <div class="feature-desc">Professional charts with indicators, signals, and multi-stock comparison tools.</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">AI Tools</div>
            <div class="feature-desc">Monte Carlo predictions, multi-signal scoring, and a GPT-powered financial advisor.</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <div class="feature-title">Practice</div>
            <div class="feature-desc">Knowledge quizzes, portfolio tracking, and risk profiling to test your skills.</div>
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
            st.markdown(glossify(content), unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.info("💡 Hover any underlined term to see its definition. Want the full list? Open the **📖 Glossary** page from the sidebar.")

# ═══════════════════════════════════════════════════════════
# PAGE: GLOSSARY
# ═══════════════════════════════════════════════════════════

elif page == "📖 Glossary":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">📖 Glossary</h1>
        <p class="hero-subtitle">Every term in the app, defined. Hover any underlined word in a lesson to see these instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    # Live hover demo so users discover the feature
    st.markdown(
        glossify(
            "**Try it →** hover these: a [[Bull Market]] vs a [[Bear Market]], "
            "the [[SMA 50]] crossing the [[SMA 200]] (a [[Golden Cross]]), "
            "an [[ETF]]'s [[Expense Ratio]], or an [[Inverted Yield Curve]]."
        ),
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search terms",
        placeholder="Search e.g. 'RSI', 'yield', 'EBITDA', 'bull'...",
        label_visibility="collapsed",
    )

    items = sorted(GLOSSARY.items(), key=lambda kv: kv[0].lower())
    if query:
        q = query.lower()
        items = [(t, d) for t, d in items if q in t.lower() or q in d.lower()]

    st.markdown(
        f'<p style="color:#64748b;font-size:0.85rem;margin:0.75rem 0 0.25rem;">'
        f'{len(items)} term{"s" if len(items) != 1 else ""}</p>',
        unsafe_allow_html=True,
    )

    if not items:
        st.info("No terms match your search.")
    else:
        cards = '<div class="gloss-grid">'
        for t, d in items:
            safe_d = d.replace("<", "&lt;").replace(">", "&gt;").replace("$", "&#36;")
            cards += (
                f'<div class="gloss-card"><div class="gloss-card-term">{t}</div>'
                f'<div class="gloss-card-def">{safe_d}</div></div>'
            )
        cards += "</div>"
        st.markdown(cards, unsafe_allow_html=True)

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
# PAGE: AI PREDICTOR
# ═══════════════════════════════════════════════════════════

elif page == "🤖 AI Predictor":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">🤖 AI Market Predictor</h1>
        <p class="hero-subtitle">Monte Carlo simulation, trend regression & multi-signal intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Controls ---
    col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
    with col_input1:
        ai_symbol = st.text_input("Enter ticker symbol", value="AAPL", key="ai_ticker").upper().strip()
    with col_input2:
        forecast_days = st.selectbox("Forecast horizon", [7, 14, 30, 60, 90], index=2, key="ai_horizon")
    with col_input3:
        num_simulations = st.selectbox("Simulations", [500, 1000, 5000, 10000], index=1, key="ai_sims")

    if st.button("🚀 Run AI Prediction", use_container_width=True, type="primary"):
        with st.spinner("🧠 AI engine analyzing data..."):
            # Fetch extended history for better predictions
            raw = fetch_stock_data(ai_symbol, 730)

            if raw is None or len(raw) < 60:
                st.error("❌ Not enough data for this ticker. Try a major stock like AAPL, MSFT, or GOOGL.")
            else:
                data = calculate_indicators(raw)
                closes = data['close'].dropna().values
                current_price = closes[-1]

                # ══════════════════════════════════════════════
                # 1. MONTE CARLO SIMULATION
                # ══════════════════════════════════════════════
                log_returns = np.diff(np.log(closes))
                mu = log_returns.mean()
                sigma = log_returns.std()

                np.random.seed(42)
                simulation_results = np.zeros((num_simulations, forecast_days))
                for sim in range(num_simulations):
                    prices = [current_price]
                    for d in range(forecast_days):
                        shock = np.random.normal(mu, sigma)
                        prices.append(prices[-1] * np.exp(shock))
                    simulation_results[sim] = prices[1:]

                mc_median = np.median(simulation_results[:, -1])
                mc_p10 = np.percentile(simulation_results[:, -1], 10)
                mc_p25 = np.percentile(simulation_results[:, -1], 25)
                mc_p75 = np.percentile(simulation_results[:, -1], 75)
                mc_p90 = np.percentile(simulation_results[:, -1], 90)
                mc_mean = np.mean(simulation_results[:, -1])
                prob_up = np.mean(simulation_results[:, -1] > current_price) * 100

                # Percentile bands over time
                median_path = np.median(simulation_results, axis=0)
                p10_path = np.percentile(simulation_results, 10, axis=0)
                p25_path = np.percentile(simulation_results, 25, axis=0)
                p75_path = np.percentile(simulation_results, 75, axis=0)
                p90_path = np.percentile(simulation_results, 90, axis=0)

                # ══════════════════════════════════════════════
                # 2. LINEAR REGRESSION TREND
                # ══════════════════════════════════════════════
                from scipy import stats as scipy_stats
                lookback = min(120, len(closes))
                recent = closes[-lookback:]
                x_hist = np.arange(lookback)
                slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x_hist, recent)

                x_future = np.arange(lookback, lookback + forecast_days)
                trend_forecast = slope * x_future + intercept
                trend_target = trend_forecast[-1]
                r_squared = r_value ** 2

                # ══════════════════════════════════════════════
                # 3. EXPONENTIAL MOVING AVERAGE FORECAST
                # ══════════════════════════════════════════════
                ema_12 = pd.Series(closes).ewm(span=12).mean().iloc[-1]
                ema_26 = pd.Series(closes).ewm(span=26).mean().iloc[-1]
                ema_50 = pd.Series(closes).ewm(span=50).mean().iloc[-1]

                # Project EMA trend
                ema_momentum = (ema_12 - ema_26) / ema_26
                ema_target = current_price * (1 + ema_momentum * forecast_days / 12)

                # ══════════════════════════════════════════════
                # 4. MULTI-SIGNAL SCORING ENGINE
                # ══════════════════════════════════════════════
                signals = {}
                score = 0
                max_score = 0

                # Signal 1: RSI
                rsi_val = data['RSI'].dropna().iloc[-1]
                if rsi_val < 30:
                    signals['RSI'] = ('🟢 Oversold — Strong Buy', 2)
                    score += 2
                elif rsi_val < 40:
                    signals['RSI'] = ('🟢 Approaching Oversold — Buy', 1)
                    score += 1
                elif rsi_val > 70:
                    signals['RSI'] = ('🔴 Overbought — Strong Sell', -2)
                    score -= 2
                elif rsi_val > 60:
                    signals['RSI'] = ('🟡 Approaching Overbought — Caution', -1)
                    score -= 1
                else:
                    signals['RSI'] = ('⚪ Neutral', 0)
                max_score += 2

                # Signal 2: MACD
                macd_val = data['MACD'].dropna().iloc[-1]
                macd_sig = data['MACD_signal'].dropna().iloc[-1]
                macd_hist = data['MACD_hist'].dropna().iloc[-1]
                macd_hist_prev = data['MACD_hist'].dropna().iloc[-2]
                if macd_val > macd_sig and macd_hist > macd_hist_prev:
                    signals['MACD'] = ('🟢 Bullish Crossover + Accelerating', 2)
                    score += 2
                elif macd_val > macd_sig:
                    signals['MACD'] = ('🟢 Bullish', 1)
                    score += 1
                elif macd_val < macd_sig and macd_hist < macd_hist_prev:
                    signals['MACD'] = ('🔴 Bearish Crossover + Accelerating', -2)
                    score -= 2
                elif macd_val < macd_sig:
                    signals['MACD'] = ('🔴 Bearish', -1)
                    score -= 1
                else:
                    signals['MACD'] = ('⚪ Neutral', 0)
                max_score += 2

                # Signal 3: SMA Trend (price vs SMA 20/50)
                sma20 = data['SMA_20'].dropna().iloc[-1]
                sma50 = data['SMA_50'].dropna().iloc[-1]
                if current_price > sma20 > sma50:
                    signals['Moving Averages'] = ('🟢 Strong Uptrend — Price > SMA20 > SMA50', 2)
                    score += 2
                elif current_price > sma20:
                    signals['Moving Averages'] = ('🟢 Above SMA20 — Short-term Bullish', 1)
                    score += 1
                elif current_price < sma20 < sma50:
                    signals['Moving Averages'] = ('🔴 Strong Downtrend — Price < SMA20 < SMA50', -2)
                    score -= 2
                elif current_price < sma20:
                    signals['Moving Averages'] = ('🔴 Below SMA20 — Short-term Bearish', -1)
                    score -= 1
                else:
                    signals['Moving Averages'] = ('⚪ Mixed', 0)
                max_score += 2

                # Signal 4: Bollinger Band Position
                bb_upper = data['BB_upper'].dropna().iloc[-1]
                bb_lower = data['BB_lower'].dropna().iloc[-1]
                bb_mid = data['BB_middle'].dropna().iloc[-1]
                bb_pct = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                if bb_pct > 0.95:
                    signals['Bollinger Bands'] = ('🔴 At Upper Band — Overbought', -2)
                    score -= 2
                elif bb_pct > 0.8:
                    signals['Bollinger Bands'] = ('🟡 Near Upper Band — Caution', -1)
                    score -= 1
                elif bb_pct < 0.05:
                    signals['Bollinger Bands'] = ('🟢 At Lower Band — Oversold', 2)
                    score += 2
                elif bb_pct < 0.2:
                    signals['Bollinger Bands'] = ('🟢 Near Lower Band — Opportunity', 1)
                    score += 1
                else:
                    signals['Bollinger Bands'] = ('⚪ Within Bands — Neutral', 0)
                max_score += 2

                # Signal 5: Volume Trend
                vol_avg = data['volume'].rolling(20).mean().dropna().iloc[-1]
                vol_now = data['volume'].iloc[-1]
                vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1
                price_up = closes[-1] > closes[-2]
                if vol_ratio > 1.5 and price_up:
                    signals['Volume'] = ('🟢 High Volume Rally — Confirmed', 2)
                    score += 2
                elif vol_ratio > 1.5 and not price_up:
                    signals['Volume'] = ('🔴 High Volume Selloff — Distribution', -2)
                    score -= 2
                elif vol_ratio > 1.2 and price_up:
                    signals['Volume'] = ('🟢 Above-Average Volume + Up', 1)
                    score += 1
                elif vol_ratio < 0.6:
                    signals['Volume'] = ('🟡 Low Volume — Weak Conviction', 0)
                else:
                    signals['Volume'] = ('⚪ Normal Volume', 0)
                max_score += 2

                # Signal 6: Momentum (Rate of Change)
                roc_10 = ((closes[-1] - closes[-10]) / closes[-10]) * 100 if len(closes) >= 10 else 0
                roc_30 = ((closes[-1] - closes[-30]) / closes[-30]) * 100 if len(closes) >= 30 else 0
                if roc_10 > 5 and roc_30 > 10:
                    signals['Momentum'] = (f'🟢 Strong Momentum — 10d: +{roc_10:.1f}%, 30d: +{roc_30:.1f}%', 2)
                    score += 2
                elif roc_10 > 2:
                    signals['Momentum'] = (f'🟢 Positive Momentum — 10d: +{roc_10:.1f}%', 1)
                    score += 1
                elif roc_10 < -5 and roc_30 < -10:
                    signals['Momentum'] = (f'🔴 Strong Negative — 10d: {roc_10:.1f}%, 30d: {roc_30:.1f}%', -2)
                    score -= 2
                elif roc_10 < -2:
                    signals['Momentum'] = (f'🔴 Negative Momentum — 10d: {roc_10:.1f}%', -1)
                    score -= 1
                else:
                    signals['Momentum'] = (f'⚪ Flat — 10d: {roc_10:.1f}%', 0)
                max_score += 2

                # ══════════════════════════════════════════════
                # 5. COMPOSITE PREDICTION
                # ══════════════════════════════════════════════
                # Weighted average of all models
                composite_target = (mc_median * 0.40 + trend_target * 0.30 + ema_target * 0.30)
                composite_change = ((composite_target - current_price) / current_price) * 100

                # AI Confidence (based on model agreement)
                model_predictions = [mc_median, trend_target, ema_target]
                model_std = np.std(model_predictions) / current_price * 100
                if model_std < 2:
                    confidence = "🟢 HIGH"
                    confidence_pct = min(95, 90 - model_std)
                elif model_std < 5:
                    confidence = "🟡 MEDIUM"
                    confidence_pct = min(80, 75 - model_std)
                else:
                    confidence = "🔴 LOW"
                    confidence_pct = max(30, 60 - model_std)

                # Overall signal
                if score >= 4:
                    overall_signal = "STRONG BUY"
                    signal_color = "#10b981"
                    signal_icon = "🚀"
                elif score >= 2:
                    overall_signal = "BUY"
                    signal_color = "#34d399"
                    signal_icon = "📈"
                elif score <= -4:
                    overall_signal = "STRONG SELL"
                    signal_color = "#ef4444"
                    signal_icon = "🔻"
                elif score <= -2:
                    overall_signal = "SELL"
                    signal_color = "#f87171"
                    signal_icon = "📉"
                else:
                    overall_signal = "HOLD"
                    signal_color = "#f59e0b"
                    signal_icon = "⏸️"

                # ══════════════════════════════════════════════
                # DISPLAY RESULTS
                # ══════════════════════════════════════════════

                # --- Top: Overall Signal ---
                st.markdown(f"""
                <div class="premium-card" style="text-align: center; border-color: {signal_color}40;">
                    <div style="font-size: 3.5rem; margin-bottom: 0.5rem;">{signal_icon}</div>
                    <div style="font-size: 2.5rem; font-weight: 900; color: {signal_color}; letter-spacing: 3px;">{overall_signal}</div>
                    <div style="color: #9ca3af; font-size: 1.1rem; margin-top: 0.5rem;">
                        {ai_symbol} • {forecast_days}-Day Forecast • Signal Score: {score}/{max_score}
                    </div>
                    <div style="margin-top: 1rem;">
                        <span style="background: {signal_color}20; color: {signal_color}; padding: 0.5rem 1.5rem; border-radius: 50px; font-weight: 700; font-size: 1.3rem;">
                            Target: ${composite_target:,.2f} ({'+' if composite_change >= 0 else ''}{composite_change:.2f}%)
                        </span>
                    </div>
                    <div style="color: #6b7280; font-size: 0.85rem; margin-top: 1rem;">
                        Confidence: {confidence} ({confidence_pct:.0f}%) • Probability of going up: {prob_up:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- Price Targets Row ---
                st.markdown('<div class="section-header">🎯 Price Targets by Model</div>', unsafe_allow_html=True)

                tc1, tc2, tc3, tc4 = st.columns(4)
                with tc1:
                    mc_change = ((mc_median - current_price) / current_price) * 100
                    mc_color = "#10b981" if mc_change >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">🎲 Monte Carlo</div>
                        <div class="metric-value">${mc_median:,.2f}</div>
                        <div style="color: {mc_color}; font-weight: 700;">{'+' if mc_change >= 0 else ''}{mc_change:.2f}%</div>
                        <div style="color: #6b7280; font-size: 0.75rem;">{num_simulations:,} simulations</div>
                    </div>
                    """, unsafe_allow_html=True)
                with tc2:
                    tr_change = ((trend_target - current_price) / current_price) * 100
                    tr_color = "#10b981" if tr_change >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📐 Regression Trend</div>
                        <div class="metric-value">${trend_target:,.2f}</div>
                        <div style="color: {tr_color}; font-weight: 700;">{'+' if tr_change >= 0 else ''}{tr_change:.2f}%</div>
                        <div style="color: #6b7280; font-size: 0.75rem;">R² = {r_squared:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with tc3:
                    ema_change = ((ema_target - current_price) / current_price) * 100
                    ema_color = "#10b981" if ema_change >= 0 else "#ef4444"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">〰️ EMA Momentum</div>
                        <div class="metric-value">${ema_target:,.2f}</div>
                        <div style="color: {ema_color}; font-weight: 700;">{'+' if ema_change >= 0 else ''}{ema_change:.2f}%</div>
                        <div style="color: #6b7280; font-size: 0.75rem;">EMA 12/26 projection</div>
                    </div>
                    """, unsafe_allow_html=True)
                with tc4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📊 Current Price</div>
                        <div class="metric-value">${current_price:,.2f}</div>
                        <div style="color: #6366f1; font-weight: 700;">{ai_symbol}</div>
                        <div style="color: #6b7280; font-size: 0.75rem;">Live</div>
                    </div>
                    """, unsafe_allow_html=True)

                # --- Monte Carlo Fan Chart ---
                st.markdown('<div class="section-header">🎲 Monte Carlo Probability Forecast</div>', unsafe_allow_html=True)

                future_dates = pd.bdate_range(start=data.index[-1] + timedelta(days=1), periods=forecast_days)

                # Build the chart
                fig_mc = go.Figure()

                # Show a sample of simulation paths (transparent)
                sample_count = min(100, num_simulations)
                for i in range(sample_count):
                    fig_mc.add_trace(go.Scatter(
                        x=future_dates, y=simulation_results[i],
                        mode='lines',
                        line=dict(color='rgba(99, 102, 241, 0.04)', width=0.8),
                        showlegend=False, hoverinfo='skip'
                    ))

                # 10th-90th percentile band
                fig_mc.add_trace(go.Scatter(
                    x=future_dates, y=p90_path,
                    mode='lines', line=dict(color='rgba(239, 68, 68, 0.0)', width=0),
                    showlegend=False, hoverinfo='skip'
                ))
                fig_mc.add_trace(go.Scatter(
                    x=future_dates, y=p10_path,
                    mode='lines', line=dict(color='rgba(239, 68, 68, 0.0)', width=0),
                    fill='tonexty', fillcolor='rgba(99, 102, 241, 0.08)',
                    name='10th-90th Percentile', hoverinfo='skip'
                ))

                # 25th-75th percentile band
                fig_mc.add_trace(go.Scatter(
                    x=future_dates, y=p75_path,
                    mode='lines', line=dict(color='rgba(99, 102, 241, 0.0)', width=0),
                    showlegend=False, hoverinfo='skip'
                ))
                fig_mc.add_trace(go.Scatter(
                    x=future_dates, y=p25_path,
                    mode='lines', line=dict(color='rgba(99, 102, 241, 0.0)', width=0),
                    fill='tonexty', fillcolor='rgba(99, 102, 241, 0.18)',
                    name='25th-75th Percentile', hoverinfo='skip'
                ))

                # Median path
                fig_mc.add_trace(go.Scatter(
                    x=future_dates, y=median_path,
                    mode='lines', line=dict(color='#6366f1', width=3),
                    name='Median Forecast'
                ))

                # Regression trend line
                fig_mc.add_trace(go.Scatter(
                    x=future_dates, y=trend_forecast,
                    mode='lines', line=dict(color='#f59e0b', width=2, dash='dash'),
                    name='Regression Trend'
                ))

                # Historical tail (last 60 days)
                hist_tail = data['close'].iloc[-60:]
                fig_mc.add_trace(go.Scatter(
                    x=hist_tail.index, y=hist_tail.values,
                    mode='lines', line=dict(color='#9ca3af', width=2),
                    name='Historical Price'
                ))

                # Current price marker
                fig_mc.add_trace(go.Scatter(
                    x=[data.index[-1]], y=[current_price],
                    mode='markers', marker=dict(color='#fff', size=10, symbol='diamond',
                                                 line=dict(color='#6366f1', width=2)),
                    name='Current Price'
                ))

                fig_mc.update_layout(
                    template='plotly_dark',
                    height=550,
                    showlegend=True,
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                        bgcolor="rgba(0,0,0,0)", font=dict(size=11, color='#9ca3af')
                    ),
                    margin=dict(l=0, r=10, t=40, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#9ca3af'),
                    yaxis_title="Price ($)",
                    xaxis_title=""
                )
                fig_mc.update_xaxes(gridcolor='rgba(55, 65, 81, 0.3)', showgrid=True, zeroline=False)
                fig_mc.update_yaxes(gridcolor='rgba(55, 65, 81, 0.3)', showgrid=True, zeroline=False)

                st.plotly_chart(fig_mc, use_container_width=True)

                # --- Probability Distribution ---
                st.markdown('<div class="section-header">📊 Price Distribution at Forecast End</div>', unsafe_allow_html=True)

                final_prices = simulation_results[:, -1]

                fig_dist = go.Figure()
                fig_dist.add_trace(go.Histogram(
                    x=final_prices,
                    nbinsx=80,
                    marker=dict(
                        color='rgba(99, 102, 241, 0.6)',
                        line=dict(color='rgba(99, 102, 241, 0.8)', width=1)
                    ),
                    name='Simulated Outcomes'
                ))

                # Add vertical lines for key levels
                fig_dist.add_vline(x=current_price, line_dash="solid", line_color="#ffffff",
                                   annotation_text=f"Current ${current_price:,.0f}", annotation_position="top")
                fig_dist.add_vline(x=mc_median, line_dash="dash", line_color="#6366f1",
                                   annotation_text=f"Median ${mc_median:,.0f}", annotation_position="top left")
                fig_dist.add_vline(x=mc_p10, line_dash="dot", line_color="#ef4444",
                                   annotation_text=f"10th pctl ${mc_p10:,.0f}", annotation_position="bottom left")
                fig_dist.add_vline(x=mc_p90, line_dash="dot", line_color="#10b981",
                                   annotation_text=f"90th pctl ${mc_p90:,.0f}", annotation_position="bottom right")

                fig_dist.update_layout(
                    template='plotly_dark',
                    height=350,
                    showlegend=False,
                    margin=dict(l=0, r=10, t=40, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#9ca3af'),
                    xaxis_title="Price ($)",
                    yaxis_title="Frequency"
                )
                fig_dist.update_xaxes(gridcolor='rgba(55, 65, 81, 0.3)', showgrid=True, zeroline=False)
                fig_dist.update_yaxes(gridcolor='rgba(55, 65, 81, 0.3)', showgrid=True, zeroline=False)

                st.plotly_chart(fig_dist, use_container_width=True)

                # --- Probability stats ---
                prob_cols = st.columns(5)
                prob_data = [
                    ("📉 Bear Case (10th)", f"${mc_p10:,.2f}", f"{((mc_p10 - current_price)/current_price)*100:+.1f}%", "#ef4444"),
                    ("📊 Low Est (25th)", f"${mc_p25:,.2f}", f"{((mc_p25 - current_price)/current_price)*100:+.1f}%", "#f87171"),
                    ("🎯 Median (50th)", f"${mc_median:,.2f}", f"{((mc_median - current_price)/current_price)*100:+.1f}%", "#6366f1"),
                    ("📈 High Est (75th)", f"${mc_p75:,.2f}", f"{((mc_p75 - current_price)/current_price)*100:+.1f}%", "#34d399"),
                    ("🚀 Bull Case (90th)", f"${mc_p90:,.2f}", f"{((mc_p90 - current_price)/current_price)*100:+.1f}%", "#10b981"),
                ]
                for i, (label, price, pct, color) in enumerate(prob_data):
                    with prob_cols[i]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">{label}</div>
                            <div class="metric-value" style="font-size: 1.3rem;">{price}</div>
                            <div style="color: {color}; font-weight: 700;">{pct}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # --- Signal Breakdown ---
                st.markdown('<div class="section-header">🧠 AI Signal Breakdown</div>', unsafe_allow_html=True)

                signal_cols = st.columns(3)
                signal_items = list(signals.items())
                for i, (sig_name, (sig_desc, sig_score)) in enumerate(signal_items):
                    with signal_cols[i % 3]:
                        if sig_score >= 2:
                            s_border = "#10b981"
                        elif sig_score >= 1:
                            s_border = "#34d399"
                        elif sig_score <= -2:
                            s_border = "#ef4444"
                        elif sig_score <= -1:
                            s_border = "#f87171"
                        else:
                            s_border = "#4b5563"

                        score_display = f"+{sig_score}" if sig_score > 0 else str(sig_score)
                        st.markdown(f"""
                        <div class="premium-card" style="border-color: {s_border}40; padding: 1.2rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #fff; font-weight: 700; font-size: 1rem;">{sig_name}</span>
                                <span style="background: {s_border}30; color: {s_border}; padding: 0.2rem 0.6rem; border-radius: 8px; font-weight: 800; font-size: 0.9rem;">{score_display}</span>
                            </div>
                            <div style="color: #9ca3af; font-size: 0.9rem; margin-top: 0.5rem;">{sig_desc}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # --- Key Stats Table ---
                st.markdown('<div class="section-header">📋 Prediction Summary</div>', unsafe_allow_html=True)

                summary_data = {
                    "Metric": [
                        "Current Price", "Composite Target", "Expected Change",
                        "Monte Carlo Median", "Regression Target", "EMA Target",
                        "Prob. of Increase", "Model Spread", "Regression R²",
                        "RSI", "MACD Histogram", "Volatility (Annual)"
                    ],
                    "Value": [
                        f"${current_price:,.2f}",
                        f"${composite_target:,.2f}",
                        f"{composite_change:+.2f}%",
                        f"${mc_median:,.2f}",
                        f"${trend_target:,.2f}",
                        f"${ema_target:,.2f}",
                        f"{prob_up:.1f}%",
                        f"${max(model_predictions) - min(model_predictions):,.2f}",
                        f"{r_squared:.4f}",
                        f"{rsi_val:.1f}",
                        f"{macd_hist:.4f}",
                        f"{sigma * np.sqrt(252) * 100:.1f}%"
                    ]
                }

                st.dataframe(
                    pd.DataFrame(summary_data).set_index("Metric"),
                    use_container_width=True
                )

                # --- Disclaimer ---
                st.markdown("""
                <div class="premium-card" style="border-color: rgba(239, 68, 68, 0.3); margin-top: 1rem;">
                    <h3 style="color: #ef4444; margin-bottom: 0.5rem;">⚠️ Important Disclaimer</h3>
                    <p style="color: #9ca3af; font-size: 0.9rem; line-height: 1.7;">
                        This AI Predictor uses <strong style="color: #fff;">Monte Carlo simulations</strong>,
                        <strong style="color: #fff;">linear regression</strong>, and <strong style="color: #fff;">technical indicators</strong>
                        to model possible future outcomes. These are <strong style="color: #ef4444;">NOT guaranteed predictions</strong>.
                        Markets are influenced by news, earnings, macroeconomics, and unpredictable events that no model can foresee.
                        This tool is for <strong style="color: #fff;">educational purposes only</strong>. Never invest based solely on algorithmic predictions.
                    </p>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE: AI ADVISOR (GPT-Powered Chatbot)
# ═══════════════════════════════════════════════════════════

elif page == "💬 AI Advisor":
    st.markdown("""
    <div class="hero-container" style="padding: 2rem 0;">
        <h1 class="hero-title" style="font-size: 3rem;">💬 AI Financial Advisor</h1>
        <p class="hero-subtitle">Ask anything about stocks, investing, markets, or financial concepts — powered by GPT</p>
    </div>
    """, unsafe_allow_html=True)

    if not OPENAI_AVAILABLE:
        st.error("The `openai` package is not installed. Run `pip install openai` to enable the AI Advisor.")
        st.stop()

    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

    # API key handling — check secrets first, then sidebar input
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
    except:
        pass
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", None)

    if not api_key:
        st.markdown("""
        <div class="premium-card" style="border-color: rgba(99, 102, 241, 0.3);">
            <h3 style="color: #f1f5f9; margin-bottom: 0.75rem;">🔑 Setup Required</h3>
            <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.7; margin-bottom: 0.5rem;">
                To use the AI Advisor, enter your OpenAI API key below. Your key stays in your browser session and is never stored.
            </p>
            <p style="color: #64748b; font-size: 0.8rem;">
                Get a key at <strong style="color: #818cf8;">platform.openai.com/api-keys</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

    if api_key:
        # System prompt for financial advisor
        SYSTEM_PROMPT = """You are FinLit Pro's AI Financial Advisor — an expert, friendly financial educator built into a student financial literacy platform (IB CAS project).

Your role:
- Explain financial concepts clearly for high school and university students
- Answer questions about stocks, crypto, ETFs, bonds, options, technical analysis, fundamental analysis, portfolio management, and macroeconomics
- When asked about a specific stock, provide balanced educational analysis (not financial advice)
- Use real examples and analogies to make concepts accessible
- Keep responses concise but thorough (2-4 paragraphs max unless asked for detail)
- Use markdown formatting for readability (bold, bullet points, tables when helpful)

Rules:
- ALWAYS include a brief disclaimer when discussing specific investment decisions: "This is educational analysis, not financial advice."
- Never recommend specific buy/sell actions — instead explain the factors a student should consider
- Be encouraging about financial learning
- If asked something outside finance, politely redirect to financial topics"""

        # Display chat history
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask me anything about finance, stocks, or investing..."):
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        client = OpenAI(api_key=api_key)
                        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                        # Include last 10 messages for context
                        for msg in st.session_state.chat_messages[-10:]:
                            messages.append({"role": msg["role"], "content": msg["content"]})

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            max_tokens=1000,
                            temperature=0.7
                        )
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        error_msg = str(e)
                        if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                            st.error("Invalid API key. Please check your OpenAI API key and try again.")
                        else:
                            st.error(f"Error: {error_msg}")

        # Suggested questions
        if not st.session_state.chat_messages:
            st.markdown('<div class="section-header">Try asking</div>', unsafe_allow_html=True)

            suggest_cols = st.columns(2)
            suggestions = [
                ("What is a P/E ratio and why does it matter?", "📊"),
                ("Explain dollar-cost averaging like I'm 15", "💡"),
                ("How do I read a candlestick chart?", "📈"),
                ("What's the difference between ETFs and mutual funds?", "⚖️"),
            ]
            for i, (suggestion, icon) in enumerate(suggestions):
                with suggest_cols[i % 2]:
                    if st.button(f"{icon} {suggestion}", key=f"suggest_{i}", use_container_width=True):
                        st.session_state.chat_messages.append({"role": "user", "content": suggestion})
                        st.rerun()

        # Clear chat button
        if st.session_state.chat_messages:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
    else:
        st.info("Enter your OpenAI API key above to start chatting with the AI Financial Advisor.")

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
