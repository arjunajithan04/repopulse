import streamlit as st

from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page


st.set_page_config(
    page_title="RepoPulse | GitHub Intelligence",
    page_icon="assets/final-logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Global design system
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
        :root {
            --bg: #0a0d12;
            --bg-2: #0f141b;
            --panel: rgba(17, 21, 28, 0.92);
            --panel-soft: rgba(22, 27, 35, 0.82);
            --line: rgba(255,255,255,0.08);
            --line-strong: rgba(255,255,255,0.14);
            --text: #f5f7fb;
            --muted: #9aa7b5;
            --primary: #8b5cf6;
            --primary-2: #5b8ef7;
            --accent: #8be9fd;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --shadow: 0 18px 50px rgba(0,0,0,0.28);
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: var(--bg);
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(139,92,246,0.18), transparent 27%),
                radial-gradient(circle at bottom right, rgba(91,142,247,0.16), transparent 25%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
        }

        [data-testid="stSidebar"] {
            background: rgba(10,13,18,0.97);
            border-right: 1px solid var(--line);
            width: 84px !important;
            min-width: 84px !important;
            max-width: 84px !important;
            transition: width .25s ease, min-width .25s ease, max-width .25s ease;
            overflow: hidden;
        }
        [data-testid="stSidebar"]:hover {
            width: 292px !important;
            min-width: 292px !important;
            max-width: 292px !important;
        }
        [data-testid="stSidebarContent"] { padding: 1rem .7rem; }

        .sidebar-brand {
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -.06em;
            margin: .2rem 0 .15rem .35rem;
            white-space: nowrap;
        }
        .sidebar-subtitle {
            color: var(--muted);
            font-size: .67rem;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin: 0 0 1rem .35rem;
            opacity: 0;
            transition: opacity .2s ease;
            white-space: nowrap;
        }
        [data-testid="stSidebar"]:hover .sidebar-subtitle { opacity: 1; }

        .stRadio > div { gap: .45rem; }
        .stRadio [role="radio"] {
            border-radius: 12px;
            padding: .72rem .7rem;
            color: var(--muted);
            border: 1px solid transparent;
            transition: all .2s ease;
            white-space: nowrap;
            overflow: hidden;
        }
        .stRadio [role="radio"]:hover {
            background: rgba(255,255,255,.025);
            border-color: var(--line);
        }
        .stRadio [role="radio"][aria-checked="true"] {
            color: var(--text);
            background: linear-gradient(180deg, rgba(139,92,246,.18), rgba(91,142,247,.08));
            border-color: rgba(139,92,246,.4);
        }

        .hero-card {
            position: relative;
            background: linear-gradient(180deg, rgba(20,25,31,.97), rgba(15,19,26,.95));
            border: 1px solid var(--line-strong);
            border-radius: 22px;
            padding: 1.45rem 1.55rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 0 0 1px rgba(139,92,246,.12), var(--shadow);
            overflow: hidden;
        }
        .hero-card:after {
            content: "";
            position: absolute;
            width: 260px;
            height: 260px;
            left: -80px;
            top: -100px;
            background: radial-gradient(circle, rgba(139,92,246,.2), transparent 65%);
            pointer-events: none;
        }
        .hero-title {
            position: relative;
            z-index: 1;
            font-size: clamp(2rem, 3vw, 2.75rem);
            font-weight: 750;
            letter-spacing: -.065em;
            line-height: 1.05;
            margin: 0;
        }
        .hero-subtitle {
            position: relative;
            z-index: 1;
            color: var(--muted);
            margin-top: .55rem;
            line-height: 1.6;
        }

        .section-card {
            background: linear-gradient(180deg, rgba(17,21,28,.9), rgba(11,14,19,.9));
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow);
        }
        .insight-card {
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: .9rem 1rem;
            background: rgba(17,21,28,.72);
            min-height: 100px;
        }
        .insight-title { font-weight: 700; margin-bottom: .35rem; }
        .insight-text { color: var(--muted); font-size: .88rem; line-height: 1.5; }
        .metric-card {
            background: linear-gradient(180deg, rgba(18,23,30,.95), rgba(12,16,22,.92));
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 1rem;
            min-height: 132px;
            box-shadow: var(--shadow);
            transition: transform .2s ease, border-color .2s ease, background .2s ease;
        }
        .metric-card:hover { transform: translateY(-2px); border-color: rgba(139,92,246,.35); }
        .metric-label { color: var(--muted); font-size: .76rem; text-transform: uppercase; letter-spacing: .08em; }
        .metric-value { font-size: 1.7rem; font-weight: 760; letter-spacing: -.04em; margin-top: .3rem; }
        .metric-delta { font-size: .78rem; font-weight: 700; margin-top: .25rem; }
        .metric-delta.good { color: var(--success); }
        .metric-delta.bad { color: var(--danger); }
        .metric-delta.neutral { color: var(--muted); }
        .metric-help { color: var(--muted); font-size: .7rem; margin-top: .55rem; }
        .status-badge { display:inline-block; padding:.32rem .65rem; border-radius:999px; font-size:.68rem; font-weight:800; letter-spacing:.08em; border:1px solid var(--line); margin-bottom:.45rem; }
        .status-badge.good { color: var(--success); background: rgba(52,211,153,.09); border-color: rgba(52,211,153,.28); }
        .status-badge.warning { color: var(--warning); background: rgba(251,191,36,.09); border-color: rgba(251,191,36,.28); }
        .status-badge.danger { color: var(--danger); background: rgba(248,113,113,.09); border-color: rgba(248,113,113,.28); }
        .status-badge.neutral { color: var(--muted); background: rgba(255,255,255,.04); }
        .risk-row { padding:.65rem .8rem; margin:.4rem 0; border:1px solid rgba(248,113,113,.16); background:rgba(248,113,113,.05); border-radius:10px; color:#f5f7fb; }
        .score-pill {
            display: inline-block;
            padding: .28rem .6rem;
            border-radius: 999px;
            font-size: .74rem;
            font-weight: 700;
            background: rgba(139,92,246,.13);
            border: 1px solid rgba(139,92,246,.28);
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--primary), var(--primary-2));
            border: 0;
            border-radius: 10px;
            color: white;
            font-weight: 650;
            box-shadow: 0 12px 24px rgba(91,142,247,.16);
            transition: transform .2s ease, filter .2s ease;
        }
        .stButton > button:hover { transform: translateY(-1px); filter: brightness(1.06); }
        .stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea {
            background: rgba(15,18,24,.86) !important;
            border-radius: 10px !important;
        }
        .stDataFrame { border-radius: 14px; overflow: hidden; }
        .main .block-container { max-width: 1480px; padding-top: 1.35rem; padding-bottom: 2.5rem; }

        @media (max-width: 900px) {
            [data-testid="stSidebar"], [data-testid="stSidebar"]:hover {
                width: 68px !important; min-width: 68px !important; max-width: 68px !important;
            }
            .sidebar-subtitle { display: none; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Shared session state
# -----------------------------------------------------------------------------
def _init_state():
    defaults = {
        "repo_analysis": None,
        "current_repo": None,
        "repo_session_count": 0,
        "repo_session_history": [],
        "repo_snapshots": {},
        "comparison_result": None,
        "previous_snapshot": None,
        "api_rate_limit": None,
        "last_refresh": None,
        "auto_refresh": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_state()

pages = {
    "Dashboard": dashboard_page,
    "Repository": repository_page,
    "Contributors": contributors_page,
    "Code Insights": code_insights_page,
}

with st.sidebar:
    st.markdown('<div class="sidebar-brand">RP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">GitHub Intelligence</div>', unsafe_allow_html=True)

    icon_options = ["📊", "📁", "👥", "🧠"]
    icon_page_map = {"📊": "Dashboard", "📁": "Repository", "👥": "Contributors", "🧠": "Code Insights"}
    selected_icon = st.radio(
        "Navigation",
        icon_options,
        index=0,
        label_visibility="collapsed",
    )
    selected_page = icon_page_map.get(selected_icon, "Dashboard")

    st.markdown("<hr style='border-color:rgba(255,255,255,.06)'>", unsafe_allow_html=True)
    if st.session_state.current_repo:
        st.caption("ACTIVE REPOSITORY")
        st.markdown(f"**{st.session_state.current_repo}**")
    st.caption(f"Analyses this session: {st.session_state.repo_session_count}/10")
    if st.session_state.get("last_refresh"):
        st.caption(f"Last scan: {st.session_state.last_refresh}")

current_repo = st.session_state.get("current_repo")
hero_title = f"{current_repo} intelligence" if current_repo else "Repository Intelligence Dashboard"
hero_subtitle = (
    "Live repository telemetry is loaded. Re-scan to update metrics, compare against history, and surface what changed."
    if current_repo
    else "Analyze a GitHub repository to unlock live health, contributor, code-quality, trend, and risk intelligence."
)
st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">{hero_title}</div>
        <div class="hero-subtitle">{hero_subtitle}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

pages[selected_page]()
