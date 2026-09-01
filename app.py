import streamlit as st

from config.settings import settings
from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page


st.set_page_config(
    page_title="GHAnalyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            --bg: #0b1020;
            --panel: #111827;
            --panel-strong: #172033;
            --panel-soft: #1d2940;
            --primary: #8b5cf6;
            --primary-2: #3b82f6;
            --accent: #22c55e;
            --warning: #f59e0b;
            --danger: #f87171;
            --text: #e5e7eb;
            --muted: #a5b4cf;
            --border: rgba(148, 163, 184, 0.16);
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: linear-gradient(135deg, #07101d 0%, #0f172a 30%, #111827 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(17, 24, 39, 0.96));
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebarContent"] {
            padding: 1rem 0.8rem;
        }

        .sidebar-header {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0.4rem 0 1rem 0.3rem;
            color: white;
        }

        .sidebar-subtitle {
            color: var(--muted);
            font-size: 0.75rem;
            margin: 0 0 1rem 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.24), rgba(59, 130, 246, 0.14));
            border-radius: 22px;
            border: 1px solid var(--border);
            padding: 1.4rem 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.28);
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0;
            color: white;
        }

        .hero-subtitle {
            margin-top: 0.5rem;
            color: var(--muted);
            font-size: 0.98rem;
        }

        .stRadio > div {
            gap: 0.45rem;
        }

        .stRadio [role="radio"] {
            border-radius: 12px;
            padding: 0.6rem 0.75rem;
            background: transparent;
            border: 1px solid transparent;
            color: var(--muted);
        }

        .stRadio [role="radio"][aria-checked="true"] {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(59, 130, 246, 0.14));
            border: 1px solid rgba(139, 92, 246, 0.45);
            color: white;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.95), rgba(17, 24, 39, 0.86));
            border: 1px solid var(--border);
            border-radius: 18px;
            min-height: 150px;
            padding: 1rem 1.1rem;
            box-shadow: 0 16px 30px rgba(15, 23, 42, 0.2);
        }

        .metric-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            margin-bottom: 0.75rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: white;
            line-height: 1.1;
        }

        .metric-delta {
            font-size: 0.8rem;
            font-weight: 700;
            margin-top: 0.45rem;
        }

        .metric-delta.good { color: #34d399; }
        .metric-delta.bad { color: #f87171; }
        .metric-delta.neutral { color: #60a5fa; }

        .metric-help {
            margin-top: 0.45rem;
            font-size: 0.78rem;
            color: var(--muted);
        }

        .stDataFrame, .stTable {
            border-radius: 14px;
            overflow: hidden;
        }

        .stDataFrame > div > div {
            border: 1px solid var(--border);
        }

        .stButton > button {
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.7rem 1.1rem;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div > div {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = {
    "Dashboard": dashboard_page,
    "Repository": repository_page,
    "Contributors": contributors_page,
    "Code Insights": code_insights_page,
}

with st.sidebar:
    st.markdown('<div class="sidebar-header">GHAnalyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">GitHub intelligence</div>', unsafe_allow_html=True)
    selected_page = st.radio("", list(pages.keys()), index=0)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Repository intelligence dashboard</div>
        <div class="hero-subtitle">Monitor repo health, contributor momentum, and code quality in one place.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

pages[selected_page]()
