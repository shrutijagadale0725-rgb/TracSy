"""
main.py  —  Personal Budget Monitor
Premium UI with glassmorphism, animations, micro-interactions.
Every CSS rule is scoped; no raw open/close div pairs split across st calls.
"""

import streamlit as st
from datetime import date
import pandas as pd

from database import init_db
from auth import register_user, login_user
from crud import (add_transaction, get_all_transactions, get_total_by_type,
                  get_expense_by_category, get_transaction_summary, bulk_add_transactions)
from charts import create_expense_pie_chart, create_income_expense_bar_chart, create_summary_chart
from file_parser import parse_csv, parse_pdf, validate_csv_structure, validate_pdf_transactions
from chatbot import get_financial_context, get_chatbot_response, get_quick_insight


# Hide Streamlit default header, footer, and menu
st.markdown("""
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Tracsy - Personal Budget Monitor",
    page_icon="💰",
    layout="wide"
)
# ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Budget Monitor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════ */
:root {
    --clr-bg-0:       #0f0d1a;
    --clr-bg-1:       #16142a;
    --clr-bg-2:       #1e1b3a;
    --clr-surface:    rgba(255,255,255,.055);
    --clr-surface-h:  rgba(255,255,255,.09);
    --clr-border:     rgba(255,255,255,.1);
    --clr-border-h:   rgba(255,255,255,.2);
    --clr-accent:     #635bff;
    --clr-accent-2:   #7c3aed;
    --clr-accent-glow:rgba(99,91,255,.35);
    --clr-income:     #10d48a;
    --clr-expense:    #ff5c6b;
    --clr-text-1:     #fff;
    --clr-text-2:     rgba(255,255,255,.6);
    --clr-text-3:     rgba(255,255,255,.38);
    --radius-sm:      8px;
    --radius-md:      12px;
    --radius-lg:      18px;
    --radius-xl:      24px;
    --ease:           cubic-bezier(.4,0,.2,1);
    --ease-spring:    cubic-bezier(.34,1.56,.64,1);
}

/* ═══════════════════════════════════════════════════
   APP ROOT — multi-layer deep background
   ═══════════════════════════════════════════════════ */
.stApp {
    background: var(--clr-bg-0) !important;
    min-height: 100vh;
    position: relative;
}
/* Ambient gradient orbs */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 70% 50% at 15% 20%,  rgba(99,91,255,.12)  0%, transparent 70%),
        radial-gradient(ellipse 55% 45% at 80% 75%,  rgba(124,58,237,.1)  0%, transparent 70%),
        radial-gradient(ellipse 40% 35% at 50% 50%,  rgba(16,212,138,.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
.stApp > * { position: relative; z-index: 1; }

/* ═══════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--clr-bg-1) 0%, #1a1535 100%) !important;
    border-right: 1px solid var(--clr-border) !important;
}
[data-testid="stSidebar"] * { color: var(--clr-text-1) !important; }

[data-testid="stSidebar"] .stButton > button {
    background: var(--clr-surface) !important;
    border: 1px solid var(--clr-border-h) !important;
    color: var(--clr-text-1) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-size: .82rem !important;
    letter-spacing: .02em !important;
    transition: all .25s var(--ease) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--clr-surface-h) !important;
    border-color: var(--clr-accent) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0,0,0,.3);
}

/* ═══════════════════════════════════════════════════
   GLASSMORPHISM CARD  (.pbm-card)
   ═══════════════════════════════════════════════════ */
.pbm-card {
    background: var(--clr-surface);
    backdrop-filter: blur(20px) saturate(140%);
    -webkit-backdrop-filter: blur(20px) saturate(140%);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-xl);
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
    box-shadow:
        0 1px 2px  rgba(0,0,0,.15),
        0 8px 32px rgba(0,0,0,.2),
        inset 0 1px 0 rgba(255,255,255,.06);
    animation: pbmFadeUp .45s var(--ease) backwards;
    transition: border-color .3s var(--ease), box-shadow .3s var(--ease);
}
.pbm-card:hover {
    border-color: var(--clr-border-h);
    box-shadow:
        0 1px 2px  rgba(0,0,0,.15),
        0 12px 40px rgba(0,0,0,.25),
        inset 0 1px 0 rgba(255,255,255,.08);
}

/* ═══════════════════════════════════════════════════
   HERO  (login page)
   ═══════════════════════════════════════════════════ */
.pbm-hero {
    text-align: center;
    padding: 3.5rem 1rem 1.25rem;
}
.pbm-hero-icon {
    font-size: 3.8rem;
    display: inline-block;
    animation: pbmFloat 3.4s ease-in-out infinite;
    filter: drop-shadow(0 6px 18px rgba(99,91,255,.3));
}
.pbm-hero-title {
    font-size: clamp(2.1rem, 5vw, 3rem);
    font-weight: 800;
    color: var(--clr-text-1);
    letter-spacing: -.04em;
    margin: .7rem 0 .25rem;
    background: linear-gradient(135deg, #fff 30%, rgba(255,255,255,.7));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.pbm-hero-sub {
    font-size: .98rem;
    color: var(--clr-text-3);
    font-weight: 400;
    letter-spacing: .01em;
}

/* ═══════════════════════════════════════════════════
   GLASS PANEL  (login forms)
   ═══════════════════════════════════════════════════ */
.pbm-glass {
    background: rgba(255,255,255,.06);
    backdrop-filter: blur(24px) saturate(160%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: var(--radius-xl);
    padding: 2rem 2.25rem 1.5rem;
    max-width: 440px;
    margin: 1.25rem auto 0;
    box-shadow:
        0 20px 48px rgba(0,0,0,.3),
        inset 0 1px 0 rgba(255,255,255,.07);
    animation: pbmFadeUp .55s var(--ease-spring) .15s backwards;
}
.pbm-glass-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--clr-text-1);
    text-align: center;
    margin-bottom: 1.5rem;
    letter-spacing: -.01em;
}

/* ═══════════════════════════════════════════════════
   SECTION HEADER  (inside tabs)
   ═══════════════════════════════════════════════════ */
.pbm-section-head { margin-bottom: .25rem; }
.pbm-section-head h3 {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--clr-text-1);
    margin: 0 0 .3rem;
    letter-spacing: -.02em;
}
.pbm-section-head h3 .pbm-accent-line {
    display: block;
    width: 36px; height: 3px;
    background: linear-gradient(90deg, var(--clr-accent), #00d4ff);
    border-radius: 99px;
    margin-top: .45rem;
    animation: pbmGrowLine .5s var(--ease-spring) .1s backwards;
}
.pbm-section-head p {
    font-size: .82rem;
    color: var(--clr-text-3);
    margin: .15rem 0 0;
    letter-spacing: .01em;
}

/* ═══════════════════════════════════════════════════
   SIDEBAR METRIC CARD
   ═══════════════════════════════════════════════════ */
.pbm-metric {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-lg);
    padding: .95rem 1.2rem;
    margin-bottom: .5rem;
    transition: all .28s var(--ease);
}
.pbm-metric:hover {
    background: var(--clr-surface-h);
    border-color: var(--clr-border-h);
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(0,0,0,.25);
}
.pbm-metric-label {
    font-size: .7rem;
    font-weight: 600;
    color: var(--clr-text-3);
    text-transform: uppercase;
    letter-spacing: .08em;
}
.pbm-metric-value {
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--clr-text-1);
    letter-spacing: -.025em;
    margin-top: .12rem;
}

/* ═══════════════════════════════════════════════════
   BALANCE BADGE  (sidebar)
   ═══════════════════════════════════════════════════ */
.pbm-balance {
    background: linear-gradient(135deg, rgba(99,91,255,.18), rgba(124,58,237,.18));
    border: 1px solid rgba(99,91,255,.3);
    border-radius: var(--radius-lg);
    padding: 1rem 1.2rem;
    text-align: center;
    margin: .35rem 0 .5rem;
    position: relative; overflow: hidden;
    transition: box-shadow .3s var(--ease);
}
.pbm-balance:hover {
    box-shadow: 0 0 24px rgba(99,91,255,.2);
}
.pbm-balance-label {
    font-size: .7rem; font-weight: 600;
    color: var(--clr-text-3);
    text-transform: uppercase; letter-spacing: .08em;
}
.pbm-balance-value {
    font-size: 1.7rem; font-weight: 800;
    color: var(--clr-text-1); letter-spacing: -.03em;
    margin-top: .1rem;
}
/* Shimmer sweep */
.pbm-balance::after {
    content: '';
    position: absolute; top: 0; left: -100%;
    width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.08), transparent);
    animation: pbmShimmer 3.5s linear infinite;
}

/* ═══════════════════════════════════════════════════
   DASHBOARD HEADER
   ═══════════════════════════════════════════════════ */
.pbm-dash-head {
    text-align: center;
    padding: 1.4rem 0 .8rem;
}
.pbm-dash-head h2 {
    font-size: 1.9rem; font-weight: 800;
    color: var(--clr-text-1); letter-spacing: -.03em; margin: 0;
}
.pbm-dash-head p {
    font-size: .88rem;
    color: var(--clr-text-3);
    margin: .25rem 0 0;
}

/* ═══════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--clr-surface) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    gap: 3px !important;
    border: 1px solid var(--clr-border) !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--clr-text-3) !important;
    border-radius: var(--radius-sm) !important;
    padding: .55rem 1.15rem !important;
    font-weight: 600 !important;
    font-size: .8rem !important;
    letter-spacing: .01em !important;
    background: transparent !important;
    transition: all .2s var(--ease) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: var(--clr-surface-h) !important;
    color: var(--clr-text-2) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--clr-accent), var(--clr-accent-2)) !important;
    color: #fff !important;
    box-shadow: 0 3px 12px var(--clr-accent-glow) !important;
}

/* ═══════════════════════════════════════════════════
   INPUTS & FORM CONTROLS
   ═══════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stDateInput > div > div > input {
    background: var(--clr-surface) !important;
    border: 1px solid var(--clr-border-h) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--clr-text-1) !important;
    font-size: .88rem !important;
    transition: all .2s var(--ease) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stDateInput > div > div > input:focus {
    border-color: var(--clr-accent) !important;
    box-shadow: 0 0 0 3px rgba(99,91,255,.18) !important;
    background: rgba(255,255,255,.08) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--clr-text-3) !important;
}
.stTextInput label, .stNumberInput label,
.stTextArea label, .stDateInput label {
    color: var(--clr-text-2) !important;
    font-weight: 600 !important;
    font-size: .74rem !important;
    letter-spacing: .025em !important;
    text-transform: uppercase !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--clr-surface) !important;
    border: 1px solid var(--clr-border-h) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--clr-text-1) !important;
    transition: border-color .2s !important;
}
.stSelectbox > div > div:hover { border-color: var(--clr-accent) !important; }
.stSelectbox label {
    color: var(--clr-text-2) !important;
    font-weight: 600 !important;
    font-size: .74rem !important;
    letter-spacing: .025em !important;
    text-transform: uppercase !important;
}

/* ═══════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, var(--clr-accent), var(--clr-accent-2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 700 !important;
    font-size: .82rem !important;
    letter-spacing: .02em !important;
    box-shadow: 0 3px 14px var(--clr-accent-glow) !important;
    transition: all .2s var(--ease) !important;
    cursor: pointer;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 22px var(--clr-accent-glow) !important;
}
.stButton > button:active { transform: translateY(0) scale(.96); }

/* ═══════════════════════════════════════════════════
   FILE UPLOADER
   ═══════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: var(--clr-surface) !important;
    border: 2px dashed var(--clr-border-h) !important;
    border-radius: var(--radius-lg) !important;
    transition: all .28s var(--ease) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--clr-accent) !important;
    background: rgba(99,91,255,.06) !important;
    box-shadow: 0 0 20px rgba(99,91,255,.08);
}
[data-testid="stFileUploader"] * { color: var(--clr-text-2) !important; }

/* ═══════════════════════════════════════════════════
   DATAFRAME  (transaction table)
   ═══════════════════════════════════════════════════ */
.stDataFrame {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    border: 1px solid var(--clr-border) !important;
}

/* ═══════════════════════════════════════════════════
   ALERT BANNERS
   ═══════════════════════════════════════════════════ */
.stSuccess {
    background: rgba(16,212,138,.1) !important;
    border-left: 3px solid var(--clr-income) !important;
    border-radius: var(--radius-sm) !important;
}
.stError {
    background: rgba(255,92,107,.1) !important;
    border-left: 3px solid var(--clr-expense) !important;
    border-radius: var(--radius-sm) !important;
}
.stWarning {
    background: rgba(245,158,11,.1) !important;
    border-left: 3px solid #f59e0b !important;
    border-radius: var(--radius-sm) !important;
}
.stInfo {
    background: rgba(99,91,255,.08) !important;
    border-left: 3px solid var(--clr-accent) !important;
    border-radius: var(--radius-sm) !important;
}
.stSuccess *, .stError *, .stWarning *, .stInfo * { color: var(--clr-text-1) !important; }

/* ═══════════════════════════════════════════════════
   TRANSACTION ROW  (CSV preview)
   ═══════════════════════════════════════════════════ */
.pbm-txn-row {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-sm);
    padding: .5rem .75rem;
    margin-bottom: .3rem;
    transition: all .18s var(--ease);
}
.pbm-txn-row:hover {
    background: var(--clr-surface-h);
    transform: translateX(3px);
    border-color: rgba(99,91,255,.28);
    box-shadow: 0 2px 8px rgba(0,0,0,.18);
}

/* ═══════════════════════════════════════════════════
   CHART WRAPPER  (.pbm-chart-wrap)
   ═══════════════════════════════════════════════════ */
.pbm-chart-wrap {
    background: var(--clr-surface);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.2rem 1rem;
    margin-top: .5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,.18);
    animation: pbmFadeUp .45s var(--ease) .08s backwards;
    transition: border-color .3s var(--ease);
}
.pbm-chart-wrap:hover {
    border-color: var(--clr-border-h);
}
.pbm-chart-title {
    font-size: .72rem;
    font-weight: 700;
    color: var(--clr-text-3);
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-bottom: .6rem;
    display: flex;
    align-items: center;
    gap: .5rem;
}
.pbm-chart-title .pbm-chart-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--clr-accent), #00d4ff);
    box-shadow: 0 0 6px var(--clr-accent-glow);
}

/* ═══════════════════════════════════════════════════
   ANALYTICS GRID  (.pbm-analytics-row)
   ═══════════════════════════════════════════════════ */
.pbm-analytics-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}
.pbm-analytics-row > * {
    flex: 1;
}

/* ═══════════════════════════════════════════════════
   STAT PILL  (quick analytics summary)
   ═══════════════════════════════════════════════════ */
.pbm-stat-pill {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    padding: .8rem 1rem;
    text-align: center;
    transition: all .22s var(--ease);
}
.pbm-stat-pill:hover {
    background: var(--clr-surface-h);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0,0,0,.22);
}
.pbm-stat-pill .pbm-stat-val {
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--clr-text-1);
    letter-spacing: -.02em;
}
.pbm-stat-pill .pbm-stat-label {
    font-size: .68rem;
    font-weight: 600;
    color: var(--clr-text-3);
    text-transform: uppercase;
    letter-spacing: .07em;
    margin-top: .15rem;
}
.pbm-stat-pill.pbm-stat--income .pbm-stat-val { color: var(--clr-income); }
.pbm-stat-pill.pbm-stat--expense .pbm-stat-val { color: var(--clr-expense); }
.pbm-stat-pill.pbm-stat--balance .pbm-stat-val { color: #60a5fa; }

/* ═══════════════════════════════════════════════════
   COLUMN HEADERS  (CSV preview table)
   ═══════════════════════════════════════════════════ */
.pbm-col-head {
    font-size: .68rem;
    font-weight: 700;
    color: var(--clr-text-3);
    text-transform: uppercase;
    letter-spacing: .07em;
}

/* ═══════════════════════════════════════════════════
   CHATBOT MESSAGE BUBBLES
   ═══════════════════════════════════════════════════ */
.pbm-chat-msg {
    background: var(--clr-surface);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-lg);
    padding: 1rem 1.25rem;
    margin-bottom: .75rem;
    animation: pbmFadeUp .3s var(--ease);
}
.pbm-chat-msg.user {
    background: linear-gradient(135deg, rgba(99,91,255,.15), rgba(124,58,237,.15));
    border-color: rgba(99,91,255,.3);
    margin-left: 2rem;
}
.pbm-chat-msg.assistant {
    background: var(--clr-surface);
    border-color: var(--clr-border-h);
    margin-right: 2rem;
}
.pbm-chat-msg-header {
    font-size: .7rem;
    font-weight: 700;
    color: var(--clr-text-3);
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: .5rem;
}
.pbm-chat-msg-content {
    font-size: .9rem;
    color: var(--clr-text-1);
    line-height: 1.6;
}

/* ═══════════════════════════════════════════════════
   GENERIC TEXT ON DARK BG
   ═══════════════════════════════════════════════════ */
.main p, .main span, .main small { color: var(--clr-text-2); }
.main h1, .main h2, .main h3     { color: var(--clr-text-1); }
.main .stMarkdown                 { color: var(--clr-text-2); }

/* ═══════════════════════════════════════════════════
   DIVIDER  (.pbm-divider)
   ═══════════════════════════════════════════════════ */
.pbm-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--clr-border), transparent);
    margin: 1rem 0;
    border: none;
}

/* ═══════════════════════════════════════════════════
   KEYFRAMES
   ═══════════════════════════════════════════════════ */
@keyframes pbmFadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0);    }
}
@keyframes pbmFloat {
    0%,100% { transform: translateY(0);     }
    50%     { transform: translateY(-8px);  }
}
@keyframes pbmGrowLine {
    from { width: 0; opacity: 0; }
    to   { width: 36px; opacity: 1; }
}
@keyframes pbmShimmer {
    to { left: 240%; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────
init_db()

if 'logged_in'  not in st.session_state: st.session_state.logged_in  = False
if 'user_id'    not in st.session_state: st.session_state.user_id    = None
if 'username'   not in st.session_state: st.session_state.username   = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

INCOME_CATEGORIES  = ['Salary','Freelance','Investment','Gift','Other']
EXPENSE_CATEGORIES = ['Food','Transport','Shopping','Bills','Entertainment',
                      'Healthcare','Education','Other']


# ═══════════════════════════════════════════════════════════
#  LOGIN PAGE
# ═══════════════════════════════════════════════════════════
def login_page():
    st.markdown("""
        <div class="pbm-hero">
            <div class="pbm-hero-icon">💰</div>
            <div class="pbm-hero-title">Budget Monitor</div>
            <div class="pbm-hero-sub">Smart financial management made simple</div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    # ─── LOGIN ───
    with tab1:
        st.markdown("""
            <div class="pbm-glass">
                <div class="pbm-glass-title">Welcome Back</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_pass")
            submit   = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if username and password:
                    ok, msg, uid, uname = login_user(username, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_id   = uid
                        st.session_state.username  = uname
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter both username and password.")

    # ─── REGISTER ───
    with tab2:
        st.markdown("""
            <div class="pbm-glass">
                <div class="pbm-glass-title">Create Account</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("register_form"):
            new_user = st.text_input("👤 Username", placeholder="Min 3 characters", key="reg_user")
            new_pass = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters", key="reg_pass")
            conf_pass= st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password", key="reg_conf")
            submit   = st.form_submit_button("Create Account", use_container_width=True)

            if submit:
                if new_user and new_pass and conf_pass:
                    if new_pass != conf_pass:
                        st.error("Passwords do not match!")
                    else:
                        ok, msg = register_user(new_user, new_pass)
                        if ok:
                            st.success(msg)
                            st.info("✅ You can now log in with your new credentials.")
                        else:
                            st.error(msg)
                else:
                    st.warning("Please fill in all fields.")


# ═══════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════
def main_app():

    # ─── SIDEBAR ────────────────────────────────────────────
    with st.sidebar:
        summary = get_transaction_summary(st.session_state.user_id)
        bal     = summary['balance']

        st.markdown(f"""
            <div style="text-align:center; padding:.5rem 0 .75rem;">
                <div style="font-size:.95rem; font-weight:700; color:#fff; letter-spacing:.01em;">👤 {st.session_state.username}</div>
            </div>
            <div class="pbm-divider"></div>

            <div class="pbm-balance">
                <div class="pbm-balance-label">{"📈" if bal >= 0 else "📉"} Balance</div>
                <div class="pbm-balance-value">₹{bal:,.2f}</div>
            </div>

            <div class="pbm-metric">
                <div class="pbm-metric-label">💰 Total Income</div>
                <div class="pbm-metric-value">₹{summary['total_income']:,.2f}</div>
            </div>
            <div class="pbm-metric">
                <div class="pbm-metric-label">💸 Total Expense</div>
                <div class="pbm-metric-value">₹{summary['total_expense']:,.2f}</div>
            </div>
            <div class="pbm-metric">
                <div class="pbm-metric-label">📊 Transactions</div>
                <div class="pbm-metric-value">{summary['transaction_count']}</div>
            </div>
            <div class="pbm-divider"></div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id   = None
            st.session_state.username  = None
            st.session_state.chat_history = []
            st.rerun()

    # ─── DASHBOARD HEADER ───────────────────────────────────
    st.markdown(f"""
        <div class="pbm-dash-head">
            <h2>Dashboard</h2>
            <p>Welcome back, {st.session_state.username} 👋</p>
        </div>
    """, unsafe_allow_html=True)

    # ─── TABS ───────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Add Transaction", "📁 Upload Files",
        "📊 Analytics",       "📜 History",
        "🤖 AI Assistant"
    ])

    # ═══════════════════════════════════════════
    # TAB 1 — ADD TRANSACTION
    # ═══════════════════════════════════════════
    with tab1:
        st.markdown("""
            <div class="pbm-card">
                <div class="pbm-section-head">
                    <h3>✨ Add New Transaction<span class="pbm-accent-line"></span></h3>
                    <p>Record your income or expenses with details</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            t_type   = st.selectbox("💼 Transaction Type", ["Income","Expense"])
            category = st.selectbox("🏷️ Category",
                                    INCOME_CATEGORIES if t_type == "Income" else EXPENSE_CATEGORIES)
            amount   = st.number_input("💵 Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
        with col2:
            t_date = st.date_input("📅 Date", value=date.today(), max_value=date.today())
            desc   = st.text_area("📝 Description (Optional)", height=100,
                                  placeholder="Add details about this transaction…")

        if st.button("💾 Save Transaction", use_container_width=True):
            if amount > 0:
                ok, msg = add_transaction(st.session_state.user_id, t_date, amount, category, desc, t_type)
                if ok:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a valid amount.")

    # ═══════════════════════════════════════════
    # TAB 2 — UPLOAD FILES
    # ═══════════════════════════════════════════
    with tab2:
        st.markdown("""
            <div class="pbm-card">
                <div class="pbm-section-head">
                    <h3>📁 Upload Transaction Files<span class="pbm-accent-line"></span></h3>
                    <p>Import from CSV or PDF with smart auto-detection</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("Drop your file here or click to browse", type=['csv','pdf'])

        if uploaded is not None:
            ftype = uploaded.name.split('.')[-1].lower()

            # ──── CSV ────
            if ftype == 'csv':
                df = parse_csv(uploaded)
                if df is not None:
                    valid, vmsg = validate_csv_structure(df)
                    if valid:
                        st.success(vmsg)
                        st.info(f"🎉 Found **{len(df)}** transactions in your CSV file")

                        # detection helpers
                        def detect_type(description):
                            d = str(description).lower()
                            inc = ['salary','freelance','income','payment received','credit',
                                   'refund','bonus','interest','dividend','gift received',
                                   'cashback','reward','commission','investment return','profit','revenue']
                            exp = ['payment','purchase','bill','expense','debit','shopping','food',
                                   'grocery','restaurant','transport','fuel','electricity','water',
                                   'rent','emi','loan','medical','doctor','hospital','medicine',
                                   'entertainment','movie','subscription','education','fee','tuition']
                            for k in inc:
                                if k in d: return 'Income'
                            for k in exp:
                                if k in d: return 'Expense'
                            return 'Expense'

                        def detect_cat(description, ttype):
                            d = str(description).lower()
                            if ttype == 'Income':
                                if any(w in d for w in ['salary','wage','payroll']): return 'Salary'
                                if any(w in d for w in ['freelance','contract','project','commission']): return 'Freelance'
                                if any(w in d for w in ['investment','dividend','interest','stock','mutual fund']): return 'Investment'
                                if any(w in d for w in ['gift','present']): return 'Gift'
                                return 'Other'
                            else:
                                if any(w in d for w in ['food','grocery','restaurant','meal','lunch','dinner','breakfast','cafe','snack']): return 'Food'
                                if any(w in d for w in ['transport','taxi','uber','bus','metro','train','fuel','petrol','diesel','parking']): return 'Transport'
                                if any(w in d for w in ['shopping','clothes','shoes','fashion','mall']): return 'Shopping'
                                if any(w in d for w in ['bill','electricity','water','gas','internet','mobile','phone','utility','rent','emi']): return 'Bills'
                                if any(w in d for w in ['entertainment','movie','cinema','game','sport','concert','show']): return 'Entertainment'
                                if any(w in d for w in ['health','medical','doctor','hospital','medicine','pharmacy','clinic']): return 'Healthcare'
                                if any(w in d for w in ['education','school','college','course','book','tuition','fee','study']): return 'Education'
                                return 'Other'

                        # build / refresh session cache
                        if 'csv_transactions' not in st.session_state:
                            st.session_state.csv_transactions = []
                        if len(st.session_state.csv_transactions) != len(df):
                            st.session_state.csv_transactions = []
                            for _, row in df.iterrows():
                                tt = detect_type(row['description'])
                                st.session_state.csv_transactions.append({
                                    'date': row['date'],
                                    'amount': float(row['amount']),
                                    'description': str(row['description']) if pd.notna(row['description']) else 'Imported',
                                    'transaction_type': tt,
                                    'category': detect_cat(row['description'], tt),
                                    'custom_category': ''
                                })

                        st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)
                        st.markdown("""
                            <div style="margin-bottom:.6rem;">
                                <span style="font-size:1rem; font-weight:700; color:#fff; letter-spacing:-.01em;">📋 Review & Edit Categories</span>
                            </div>
                        """, unsafe_allow_html=True)
                        st.info("✨ Types and categories auto-detected. Edit any row below.")

                        # column headers
                        hc = st.columns([2, 1.5, 3, 1.8, 2.2])
                        for h, label in zip(hc, ["📅 Date","💵 Amount","📝 Description","💼 Type","🏷️ Category"]):
                            h.markdown(f'<span class="pbm-col-head">{label}</span>', unsafe_allow_html=True)

                        st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)

                        # rows
                        for idx, tr in enumerate(st.session_state.csv_transactions[:10]):
                            st.markdown('<div class="pbm-txn-row">', unsafe_allow_html=True)
                            c1,c2,c3,c4,c5 = st.columns([2, 1.5, 3, 1.8, 2.2])
                            c1.text(str(tr['date']))
                            c2.text(f"₹{tr['amount']:,.2f}")
                            c3.text((tr['description'][:36]+'…') if len(tr['description'])>36 else tr['description'])
                            c4.text("🟢 Income" if tr['transaction_type']=='Income' else "🔴 Expense")
                            with c5:
                                opts = INCOME_CATEGORIES if tr['transaction_type']=='Income' else EXPENSE_CATEGORIES
                                cur  = tr['category']
                                sel  = st.selectbox("cat", options=opts,
                                                    index=opts.index(cur) if cur in opts else 0,
                                                    key=f"cat_{idx}", label_visibility="collapsed")
                                st.session_state.csv_transactions[idx]['category'] = sel
                                if sel == 'Other':
                                    cust = st.text_input("custom", placeholder="Type category…",
                                                         value=tr['custom_category'],
                                                         key=f"cust_{idx}", label_visibility="collapsed")
                                    st.session_state.csv_transactions[idx]['custom_category'] = cust
                            st.markdown('</div>', unsafe_allow_html=True)

                        if len(st.session_state.csv_transactions) > 10:
                            st.info(f"📊 Showing 10 of {len(st.session_state.csv_transactions)} — all will be saved.")

                        st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)
                        if st.button("💾 Import All Transactions", key="save_csv", use_container_width=True):
                            to_add = []
                            for tr in st.session_state.csv_transactions:
                                cat = tr['category']
                                if cat == 'Other' and tr['custom_category'].strip():
                                    cat = tr['custom_category'].strip()
                                to_add.append({
                                    'date': tr['date'], 'amount': tr['amount'],
                                    'description': tr['description'],
                                    'transaction_type': tr['transaction_type'],
                                    'category': cat
                                })
                            ok, msg, _ = bulk_add_transactions(st.session_state.user_id, to_add)
                            if ok:
                                st.success(msg); st.balloons()
                                st.session_state.csv_transactions = []
                            else:
                                st.error(msg)
                    else:
                        st.error(vmsg)
                else:
                    st.error("Failed to parse CSV.")
                    st.info("Expected columns: date, amount, description")

            # ──── PDF ────
            elif ftype == 'pdf':
                with st.spinner("🔍 Extracting transactions…"):
                    transactions = parse_pdf(uploaded, max_transactions=20)

                if transactions is not None:
                    valid, vmsg = validate_pdf_transactions(transactions)
                    if valid:
                        st.success(vmsg)
                        if len(transactions) == 20:
                            st.warning("⚠️ Preview limited to 20 transactions")
                        st.markdown("### 📋 Extracted Data")
                        st.dataframe(pd.DataFrame({
                            'Date': [t['date'] for t in transactions],
                            'Amount (₹)': [f"₹{t['amount']:,.2f}" for t in transactions],
                            'Description': [(t['description'][:50]+'…') if len(t['description'])>50 else t['description'] for t in transactions]
                        }), use_container_width=True)

                        st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            pdf_type = st.selectbox("💼 Type for All", ["Income","Expense"], key="pdf_type")
                        with c2:
                            pdf_cat  = st.selectbox("🏷️ Category for All",
                                                    INCOME_CATEGORIES if pdf_type=="Income" else EXPENSE_CATEGORIES,
                                                    key="pdf_cat")

                        if st.button("💾 Import All Transactions", key="save_pdf", use_container_width=True):
                            to_add = [{'date': t['date'], 'amount': t['amount'],
                                       'description': t['description'],
                                       'category': pdf_cat, 'transaction_type': pdf_type}
                                      for t in transactions]
                            ok, msg, _ = bulk_add_transactions(st.session_state.user_id, to_add)
                            if ok:
                                st.success(msg); st.balloons()
                            else:
                                st.error(msg)
                    else:
                        st.error(vmsg)
                else:
                    st.error("Failed to extract transactions from PDF.")
                    st.info("Supported formats: ₹1234.56  $500  Rs. 1234")

    # ═══════════════════════════════════════════
    # TAB 3 — ANALYTICS
    # ═══════════════════════════════════════════
    with tab3:
        st.markdown("""
            <div class="pbm-card">
                <div class="pbm-section-head">
                    <h3>📊 Financial Analytics<span class="pbm-accent-line"></span></h3>
                    <p>Visual insights into your spending and financial health</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        t_inc = get_total_by_type(st.session_state.user_id, 'Income')
        t_exp = get_total_by_type(st.session_state.user_id, 'Expense')
        e_cat = get_expense_by_category(st.session_state.user_id)
        summary_data = get_transaction_summary(st.session_state.user_id)

        # ── Quick-stat pills ──
        st.markdown(f"""
            <div style="display:flex; gap:.75rem; margin-bottom:1.25rem;">
                <div class="pbm-stat-pill pbm-stat--income" style="flex:1;">
                    <div class="pbm-stat-val">₹{t_inc:,.0f}</div>
                    <div class="pbm-stat-label">💰 Income</div>
                </div>
                <div class="pbm-stat-pill pbm-stat--expense" style="flex:1;">
                    <div class="pbm-stat-val">₹{t_exp:,.0f}</div>
                    <div class="pbm-stat-label">💸 Expense</div>
                </div>
                <div class="pbm-stat-pill pbm-stat--balance" style="flex:1;">
                    <div class="pbm-stat-val">₹{summary_data['balance']:,.0f}</div>
                    <div class="pbm-stat-label">📈 Balance</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── Top two charts side by side ──
        c1, c2 = st.columns(2, gap="medium")

        with c1:
            st.markdown("""
                <div class="pbm-chart-wrap">
                    <div class="pbm-chart-title"><span class="pbm-chart-dot"></span>Expense Breakdown</div>
                </div>
            """, unsafe_allow_html=True)
            if e_cat:
                st.pyplot(create_expense_pie_chart(e_cat))
            else:
                st.info("No expense data yet — add some transactions first!")

        with c2:
            st.markdown("""
                <div class="pbm-chart-wrap">
                    <div class="pbm-chart-title"><span class="pbm-chart-dot"></span>Income vs Expense</div>
                </div>
            """, unsafe_allow_html=True)
            st.pyplot(create_income_expense_bar_chart(t_inc, t_exp))

        # ── Full-width summary chart ──
        st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="pbm-chart-wrap">
                <div class="pbm-chart-title"><span class="pbm-chart-dot"></span>Financial Summary</div>
            </div>
        """, unsafe_allow_html=True)
        st.pyplot(create_summary_chart(summary_data))

    # ═══════════════════════════════════════════
    # TAB 4 — HISTORY
    # ═══════════════════════════════════════════
    with tab4:
        st.markdown("""
            <div class="pbm-card">
                <div class="pbm-section-head">
                    <h3>📜 Transaction History<span class="pbm-accent-line"></span></h3>
                    <p>Complete record of all your financial activities</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        transactions = get_all_transactions(st.session_state.user_id)
        if transactions:
            filt = st.selectbox("🔍 Filter by Type", ["All","Income","Expense"])
            rows = []
            for t in transactions:
                if filt == "All" or t.transaction_type == filt:
                    rows.append({
                        'Date': t.date.strftime('%Y-%m-%d'),
                        'Type': t.transaction_type,
                        'Category': t.category,
                        'Amount (₹)': f"₹{t.amount:,.2f}",
                        'Description': t.description if t.description else '—'
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, height=400)
                st.info(f"📊 Showing {len(rows)} transactions")
            else:
                st.info(f"No {filt.lower()} transactions found.")
        else:
            st.info("📭 No transactions yet — start by adding your first one!")

    # ═══════════════════════════════════════════
    # TAB 5 — AI CHATBOT
    # ═══════════════════════════════════════════
    with tab5:
        st.markdown("""
            <div class="pbm-card">
                <div class="pbm-section-head">
                    <h3>🤖 AI Financial Assistant<span class="pbm-accent-line"></span></h3>
                    <p>Get personalized advice and insights about your finances</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Get financial context
        context = get_financial_context(
            st.session_state.user_id,
            get_transaction_summary,
            get_total_by_type,
            get_expense_by_category,
            get_all_transactions
        )

        if context is None or context['transaction_count'] == 0:
            st.info("📊 No transaction data yet. Add some transactions to start chatting with your AI assistant!")
        else:
            # Quick insight card
            with st.expander("💡 Quick Insight", expanded=True):
                insight = get_quick_insight(context)
                st.markdown(f"**{insight}**")

            st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)

            # Chat interface
            st.markdown("### 💬 Chat with Your AI Assistant")
            
            # Display chat history
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                        <div class="pbm-chat-msg user">
                            <div class="pbm-chat-msg-header">👤 You</div>
                            <div class="pbm-chat-msg-content">{msg['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="pbm-chat-msg assistant">
                            <div class="pbm-chat-msg-header">🤖 AI Assistant</div>
                            <div class="pbm-chat-msg-content">{msg['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)

            # Input area
            col1, col2 = st.columns([5, 1])
            with col1:
                user_input = st.text_input(
                    "Ask me anything about your finances...",
                    placeholder="e.g., How can I reduce my expenses? What's my spending pattern?",
                    key="chat_input",
                    label_visibility="collapsed"
                )
            with col2:
                send_button = st.button("Send 📤", use_container_width=True)

            # Quick question buttons
            st.markdown("**Quick Questions:**")
            qcol1, qcol2, qcol3 = st.columns(3)
            with qcol1:
                if st.button("💸 Top expenses?", use_container_width=True):
                    user_input = "What are my top expense categories?"
                    send_button = True
            with qcol2:
                if st.button("💡 Saving tips?", use_container_width=True):
                    user_input = "How can I save more money?"
                    send_button = True
            with qcol3:
                if st.button("📊 Financial health?", use_container_width=True):
                    user_input = "How is my overall financial health?"
                    send_button = True

            # Process message
            if send_button and user_input:
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })

                # Get AI response
                with st.spinner("🤔 Thinking..."):
                    # Prepare conversation history for API
                    api_history = []
                    for msg in st.session_state.chat_history[-6:]:  # Last 3 exchanges
                        api_history.append({
                            'role': msg['role'],
                            'content': msg['content']
                        })
                    
                    # Remove the last user message (we'll add it in the function)
                    api_history = api_history[:-1]
                    
                    response = get_chatbot_response(user_input, context, api_history)
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })

                # Rerun to display new messages
                st.rerun()

            # Clear chat button
            if len(st.session_state.chat_history) > 0:
                st.markdown('<div class="pbm-divider"></div>', unsafe_allow_html=True)
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()


# ─────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()