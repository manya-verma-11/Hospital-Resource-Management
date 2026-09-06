"""
🏥 Hospital Resource Management Dashboard
Main Streamlit entry point – run with:  streamlit run app.py
"""

import os
import sys
import time
import streamlit as st
from dotenv import load_dotenv

# ── Path fix so `utils` is importable when running from any CWD ──────────────
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hospital Resource Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (minimal – dark theme polish) ──────────────────────────────────
st.markdown("""
<style>
    /* Dark sidebar */
    [data-testid="stSidebar"] { background: #0f172a; }
    [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
    /* Main background */
    .stApp { background: #0f172a; color: #f1f5f9; }
    /* Metric cards */
    [data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px !important;
    }
    [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 2rem !important; }
    [data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
    /* Tab styling */
    .stTabs [data-baseweb="tab"] { color: #94a3b8; }
    .stTabs [aria-selected="true"] { color: #6366f1 !important; border-bottom-color: #6366f1 !important; }
    /* Dataframe */
    [data-testid="stDataFrame"] { border: 1px solid #334155; border-radius: 8px; }
    /* Section dividers */
    hr { border-color: #334155; }
    /* Alert box */
    .ai-alert {
        background: #1e293b;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        color: #f1f5f9;
        line-height: 1.7;
    }
    /* Status badges */
    .badge-critical { color: #ef4444; font-weight: 700; }
    .badge-high     { color: #f59e0b; font-weight: 700; }
    .badge-normal   { color: #22c55e; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Imports (after path fix) ──────────────────────────────────────────────────
from utils.data_generator import get_kpi_summary, BRANCHES
from pages.bed_occupancy   import render as render_beds
from pages.icu_status      import render as render_icu
from pages.equipment       import render as render_equipment
from pages.ai_assistant    import render as render_ai

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Hospital Resource\n### Management Dashboard")
    st.markdown("---")

    # API Key input
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "🤖 Gemini API Key",
        value=default_key,
        type="password",
        help="Enter your Google Gemini API key to enable AI features.",
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    st.markdown("---")

    # Branch filter
    branch = st.selectbox(
        "🏢 Filter by Branch",
        options=["All"] + BRANCHES,
        index=0,
    )

    st.markdown("---")

    # Auto-refresh
    refresh = st.toggle("🔄 Auto-Refresh (30s)", value=False)
    if refresh:
        st.caption("Data refreshes every 30 seconds")

    st.markdown("---")
    st.caption("Data simulated in real-time. Refresh cadence: 30 s.")
    st.caption(f"© 2025 · IBM Bob · Gemini 3.6 Flash")

# ── Auto-refresh logic ────────────────────────────────────────────────────────
if refresh:
    time.sleep(0.1)          # let the page render first
    st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🏥 Hospital Resource Management Dashboard")
st.caption(
    f"Branch: **{'All Branches' if branch == 'All' else branch}**  |  "
    f"Last updated: **{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**"
)

# ── KPI summary row ───────────────────────────────────────────────────────────
kpi = get_kpi_summary(branch)

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("🛏️ Total Beds",     kpi["total_beds"])
col2.metric("🔴 Occupied",       kpi["occupied_beds"],
            delta=f"{kpi['avg_occupancy']}% avg",
            delta_color="inverse")
col3.metric("🟢 Available",      kpi["available_beds"])
col4.metric("🏥 ICU Total",      kpi["icu_total"])
col5.metric("⚠️ ICU Occupied",   kpi["icu_occupied"],
            delta=f"{kpi['icu_pct']}%",
            delta_color="inverse")
col6.metric("🔧 Equipment Offline", kpi["offline_equip"],
            delta=f"{kpi['maint_equip']} maintenance",
            delta_color="inverse")

if kpi["critical_depts"]:
    st.error(
        f"🚨 **Critical Occupancy (≥ 90%):** "
        + " · ".join(kpi["critical_depts"])
    )

st.markdown("---")

# ── Navigation tabs ────────────────────────────────────────────────────────────
tab_beds, tab_icu, tab_equip, tab_ai = st.tabs([
    "🛏️  Bed Occupancy",
    "🏥  ICU Availability",
    "🔧  Equipment Status",
    "🤖  AI Assistant",
])

with tab_beds:
    render_beds(branch)

with tab_icu:
    render_icu(branch)

with tab_equip:
    render_equipment(branch)

with tab_ai:
    render_ai(branch, kpi)
