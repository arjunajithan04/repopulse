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
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        :root {
            --bg: #0b1020;
            --panel: #121a2b;
            --panel-strong: #1a2338;
            --panel-soft: #1f2937;
            --primary: #7c3aed;
            --primary-2: #22c55e;
            --accent: #38bdf8;
            --text: #e5e7eb;
            --muted: #a5b4cf;
            --border: rgba(148, 163, 184, 0.18);
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: linear-gradient(135deg, #0b1020 0%, #111827 42%, #0f172a 100%);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(12px);
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.22), rgba(56, 189, 248, 0.12));
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25);
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0;
        }

        .hero-subtitle {
            color: var(--muted);
            margin-top: 0.4rem;
            font-size: 1rem;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.9), rgba(17, 24, 39, 0.8));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            min-height: 140px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.7rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            color: white;
        }

        .metric-delta {
            margin-top: 0.4rem;
            font-size: 0.82rem;
            font-weight: 600;
        }

        .metric-delta.good { color: var(--success); }
        .metric-delta.bad { color: var(--danger); }
        .metric-delta.neutral { color: var(--accent); }

        .metric-help {
            font-size: 0.8rem;
            color: var(--muted);
            margin-top: 0.35rem;
        }

        div[data-testid="stTabs"] {
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 0.2rem 0.4rem 0;
            margin-bottom: 1.2rem;
        }

        button[kind="tab"] {
            background: transparent;
            border: none;
            border-radius: 12px 12px 0 0;
            color: var(--muted);
            font-weight: 600;
            padding: 0.75rem 1rem;
        }

        button[kind="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.22), rgba(56, 189, 248, 0.18));
            border: 1px solid rgba(124, 58, 237, 0.4);
            color: white;
        }

        .stDataFrame, .stTable {
            border-radius: 16px;
            overflow: hidden;
        }

        .stDataFrame > div > div {
            border: 1px solid var(--border);
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--primary), #4f46e5);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            padding: 0.7rem 1.1rem;
        }

        .stButton > button:hover {
            filter: brightness(1.08);
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input {
            background: rgba(15, 23, 42, 0.8);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 10px;
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


st.markdown(
    """
    <div class="hero-card">
        <p class="hero-title">GHAnalyst</p>
        <div class="hero-subtitle">AI-driven GitHub repository intelligence and engineering insights</div>
    </div>
    """,
    unsafe_allow_html=True,
)


tabs = st.tabs(list(pages.keys()))
for tab, (name, page_fn) in zip(tabs, pages.items()):
    with tab:
        page_fn()
