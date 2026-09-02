import streamlit as st

from config.settings import settings
from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page


st.set_page_config(
    page_title="RepoPulse",
    page_icon="assets/final-icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            --bg: #0a0d12;
            --bg-2: #0f141b;
            --panel: rgba(17, 21, 28, 0.9);
            --panel-soft: rgba(22, 27, 35, 0.82);
            --panel-strong: rgba(13, 16, 22, 0.96);
            --line: rgba(255, 255, 255, 0.08);
            --line-strong: rgba(255, 255, 255, 0.12);
            --text: #f5f7fb;
            --muted: #9aa7b5;
            --primary: #8b5cf6;
            --primary-2: #5b8ef7;
            --primary-soft: rgba(139, 92, 246, 0.15);
            --accent: #8be9fd;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
            --glow: 0 0 0 1px rgba(139, 92, 246, 0.18), 0 18px 40px rgba(89, 124, 255, 0.12);
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: var(--bg);
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(139, 92, 246, 0.18), transparent 26%),
                radial-gradient(circle at bottom right, rgba(91, 142, 247, 0.16), transparent 24%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
        }

        [data-testid="stSidebar"] {
            background: rgba(10, 13, 18, 0.96);
            border-right: 1px solid var(--line);
            box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.02);
            width: 80px !important;
            min-width: 80px !important;
            max-width: 80px !important;
            transition: width 0.25s ease, min-width 0.25s ease, max-width 0.25s ease;
            overflow: hidden;
        }

        [data-testid="stSidebar"]:hover {
            width: 290px !important;
            min-width: 290px !important;
            max-width: 290px !important;
        }

        [data-testid="stSidebar"]:hover .sidebar-header,
        [data-testid="stSidebar"]:hover .sidebar-subtitle {
            opacity: 1;
        }

        [data-testid="stSidebarContent"] {
            padding: 1rem 0.7rem;
            opacity: 0.9;
            transition: opacity 0.18s ease;
        }

        .stRadio > div {
            gap: 0.45rem;
            margin-top: 0.2rem;
        }

        .stRadio [role="radio"] {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 42px;
            border-radius: 12px;
            padding: 0.55rem 0.6rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: clip;
            width: 100%;
            color: transparent;
        }

        .stRadio [role="radio"] > div {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.2rem;
            min-width: 0;
            width: 100%;
        }

        .stRadio [role="radio"] > div > span:first-child {
            font-size: 1.3rem;
            line-height: 1;
            display: inline-block;
            min-width: 1.3rem;
            text-align: center;
        }

        .stRadio [role="radio"] > div > span:last-child {
            opacity: 0;
            width: 0;
            overflow: hidden;
            transition: opacity 0.15s ease, width 0.15s ease;
            white-space: nowrap;
        }

        [data-testid="stSidebar"]:hover .stRadio [role="radio"] {
            justify-content: flex-start;
            color: var(--text);
        }

        [data-testid="stSidebar"]:hover .stRadio [role="radio"] > div {
            justify-content: flex-start;
            gap: 0.7rem;
        }

        [data-testid="stSidebar"]:hover .stRadio [role="radio"] > div > span:last-child {
            opacity: 1;
            width: auto;
        }

        .sidebar-header {
            font-size: 1.24rem;
            font-weight: 700;
            letter-spacing: -0.06em;
            margin: 0.25rem 0 0.2rem 0.3rem;
            color: var(--text);
            opacity: 0.7;
            transition: opacity 0.2s ease;
        }

        .sidebar-subtitle {
            color: var(--muted);
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin: 0 0 1.1rem 0.3rem;
            opacity: 0;
            transition: opacity 0.2s ease;
            white-space: nowrap;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.7rem;
            max-width: 1460px;
        }

        .hero-card {
            position: relative;
            background: linear-gradient(180deg, rgba(20, 25, 31, 0.96), rgba(15, 19, 26, 0.94));
            border: 1px solid var(--line-strong);
            border-radius: 20px;
            padding: 1.4rem 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--glow);
            overflow: hidden;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            inset: 0 auto auto 0;
            width: 220px;
            height: 220px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.18), transparent 60%);
            pointer-events: none;
        }

        .hero-title {
            position: relative;
            z-index: 1;
            font-size: clamp(2rem, 2.8vw, 2.8rem);
            font-weight: 700;
            letter-spacing: -0.06em;
            line-height: 1.1;
            margin: 0;
            color: var(--text);
        }

        .hero-subtitle {
            position: relative;
            z-index: 1;
            margin-top: 0.5rem;
            color: var(--muted);
            font-size: 0.97rem;
            line-height: 1.6;
        }

        .stRadio > div {
            gap: 0.5rem;
        }

        .stRadio [role="radio"] {
            border-radius: 12px;
            padding: 0.72rem 0.8rem;
            background: transparent;
            border: 1px solid transparent;
            color: var(--muted);
            transition: all 0.2s ease;
        }

        .stRadio [role="radio"]:hover {
            border-color: rgba(255, 255, 255, 0.06);
            background: rgba(255, 255, 255, 0.015);
        }

        .stRadio [role="radio"][aria-checked="true"] {
            background: linear-gradient(180deg, rgba(139, 92, 246, 0.16), rgba(91, 142, 247, 0.08));
            border: 1px solid rgba(139, 92, 246, 0.38);
            box-shadow: inset 0 0 0 1px rgba(139, 92, 246, 0.12);
            color: var(--text);
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(17, 21, 28, 0.98), rgba(11, 14, 19, 0.98));
            border: 1px solid var(--line);
            border-radius: 18px;
            min-height: 150px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: var(--line-strong);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.32);
        }

        .metric-label {
            color: var(--muted);
            letter-spacing: 0.12em;
            font-size: 0.7rem;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.06em;
            color: var(--text);
            line-height: 1.08;
        }

        .metric-delta {
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }

        .metric-delta.good { color: var(--success); }
        .metric-delta.bad { color: var(--danger); }
        .metric-delta.neutral { color: var(--accent); }

        .metric-help {
            margin-top: 0.5rem;
            font-size: 0.76rem;
            color: var(--muted);
            line-height: 1.5;
        }

        .stDataFrame, .stTable {
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
        }

        .stDataFrame > div > div {
            border: 1px solid var(--line);
            background: rgba(17, 21, 28, 0.72);
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--primary), var(--primary-2));
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            padding: 0.7rem 1rem;
            box-shadow: 0 12px 24px rgba(91, 142, 247, 0.18);
            transition: transform 0.2s ease, filter 0.2s ease, box-shadow 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            filter: brightness(1.06);
            box-shadow: 0 16px 28px rgba(91, 142, 247, 0.22);
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: rgba(15, 18, 24, 0.86);
            border: 1px solid var(--line);
            border-radius: 10px;
            color: var(--text);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: var(--muted);
        }

        div[data-testid="stMetric"] {
            background: transparent;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid transparent;
        }

        .css-1d391kg, .css-1v0mbdj, .css-1y4p8pa {
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
    st.markdown('<div class="sidebar-header">RP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">GitHub Intelligence</div>', unsafe_allow_html=True)

    icon_options = ["📊", "📁", "👥", "🧠"]
    icon_page_map = {
        "📊": "Dashboard",
        "📁": "Repository",
        "👥": "Contributors",
        "🧠": "Code Insights",
    }

    selected_icon = st.radio(
        "",
        icon_options,
        index=0,
        horizontal=False,
        label_visibility="collapsed",
    )
    selected_page = icon_page_map.get(selected_icon or "📊", "Dashboard")

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Repository Intelligence Dashboard</div>
        <div class="hero-subtitle">Monitor repo health, contributor momentum, and code quality in one place.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

pages[selected_page]()
