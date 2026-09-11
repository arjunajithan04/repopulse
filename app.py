import streamlit as st

from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page
from pages.risk_center import risk_center_page
from pages.assessment import assessment_page
from pages.compare import compare_page


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
      --bg:#080a0f; --surface:#10131a; --surface-2:#151922; --surface-3:#1a1f29;
      --line:rgba(255,255,255,.075); --line-strong:rgba(255,255,255,.13);
      --text:#f4f6fa; --muted:#8994a5; --primary:#8b5cf6; --primary-2:#6366f1;
      --success:#34d399; --warning:#fbbf24; --danger:#fb7185;
      --shadow:0 14px 40px rgba(0,0,0,.22);
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:var(--bg);color:var(--text)}
    .stApp{background:radial-gradient(circle at 12% 0%,rgba(139,92,246,.10),transparent 28%),linear-gradient(180deg,#080a0f,#0b0e14)}
    [data-testid="stSidebar"]{background:#0b0e13;border-right:1px solid var(--line);width:236px!important;min-width:236px!important;max-width:236px!important}
    [data-testid="stSidebarContent"]{padding:1.2rem .9rem}
    .sidebar-brand{font-size:1.25rem;font-weight:800;letter-spacing:-.05em;margin:.2rem .4rem .05rem}
    .sidebar-subtitle{font-size:.68rem;color:var(--muted);letter-spacing:.14em;text-transform:uppercase;margin:0 .4rem 1.35rem}
    .sidebar-section{font-size:.63rem;color:#657083;text-transform:uppercase;letter-spacing:.12em;margin:1.15rem .45rem .45rem}
    .stRadio>div{gap:.28rem}.stRadio [role="radio"]{border:1px solid transparent;border-radius:10px;padding:.62rem .7rem;color:var(--muted);transition:.18s}
    .stRadio [role="radio"]:hover{background:rgba(255,255,255,.035);border-color:var(--line)}
    .stRadio [role="radio"][aria-checked="true"]{color:#fff;background:rgba(139,92,246,.12);border-color:rgba(139,92,246,.25)}
    .repo-context{margin-top:1rem;padding:.75rem;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.025)}
    .repo-context-label{font-size:.6rem;color:#687486;text-transform:uppercase;letter-spacing:.12em}.repo-context-name{font-size:.78rem;font-weight:650;margin-top:.3rem;overflow:hidden;text-overflow:ellipsis}
    .topbar{display:flex;justify-content:space-between;align-items:center;padding:.2rem 0 .9rem;border-bottom:1px solid var(--line);margin-bottom:1.1rem}
    .eyebrow{font-size:.68rem;font-weight:750;color:#8f9bad;text-transform:uppercase;letter-spacing:.14em;margin-bottom:.3rem}.page-title{font-size:2rem!important;letter-spacing:-.055em;margin:0!important}.page-description{color:var(--muted);font-size:.88rem;margin-top:.35rem;line-height:1.5}
    .hero-card{padding:1.35rem 1.5rem;border:1px solid var(--line-strong);border-radius:18px;background:linear-gradient(135deg,rgba(18,22,30,.98),rgba(13,16,22,.96));box-shadow:var(--shadow);margin-bottom:1.15rem}
    .hero-title{font-size:1.45rem;font-weight:750;letter-spacing:-.045em}.hero-subtitle{color:var(--muted);font-size:.84rem;margin-top:.35rem}
    .metric-card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:1rem;min-height:120px;box-shadow:var(--shadow);transition:.18s}.metric-card:hover{transform:translateY(-2px);border-color:rgba(139,92,246,.32)}
    .metric-label{font-size:.66rem;color:#7d8999;text-transform:uppercase;letter-spacing:.1em}.metric-value{font-size:1.7rem;font-weight:780;letter-spacing:-.045em;margin-top:.25rem}.metric-delta{font-size:.75rem;font-weight:700;margin-top:.2rem}.metric-delta.good{color:var(--success)}.metric-delta.bad{color:var(--danger)}.metric-delta.neutral{color:var(--muted)}.metric-help{font-size:.67rem;color:#687486;margin-top:.5rem}
    .section-title{font-size:1rem;font-weight:720;letter-spacing:-.02em;margin:.5rem 0 .1rem}.section-subtitle{font-size:.75rem;color:var(--muted);margin-bottom:.65rem}
    .section-card,.insight-card,.risk-card,.assessment-score{background:var(--surface);border:1px solid var(--line);border-radius:15px;box-shadow:var(--shadow)}
    .insight-card{padding:.9rem 1rem;min-height:105px}.insight-card.good{border-color:rgba(52,211,153,.2)}.insight-card.warning{border-color:rgba(251,191,36,.2)}.insight-card.danger{border-color:rgba(251,113,133,.22)}.insight-label{display:inline-block;font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;padding:.2rem .45rem;border-radius:999px;margin-bottom:.45rem;background:rgba(255,255,255,.05);color:var(--muted)}.insight-label.good{color:var(--success)}.insight-label.warning{color:var(--warning)}.insight-label.danger{color:var(--danger)}.insight-title{font-weight:700}.insight-text{color:var(--muted);font-size:.78rem;line-height:1.5;margin-top:.25rem}
    .status-badge{display:inline-block;padding:.3rem .55rem;border-radius:999px;font-size:.62rem;font-weight:800;letter-spacing:.08em;border:1px solid var(--line)}.status-badge.good{color:var(--success);background:rgba(52,211,153,.08);border-color:rgba(52,211,153,.22)}.status-badge.warning{color:var(--warning);background:rgba(251,191,36,.08);border-color:rgba(251,191,36,.22)}.status-badge.danger{color:var(--danger);background:rgba(251,113,133,.08);border-color:rgba(251,113,133,.22)}.status-badge.neutral{color:var(--muted)}
    .risk-card{padding:1rem 1.1rem;margin:.6rem 0}.risk-card.danger{border-color:rgba(251,113,133,.25)}.risk-card.warning{border-color:rgba(251,191,36,.22)}.risk-card.good{border-color:rgba(52,211,153,.22)}.risk-detail{color:var(--muted);font-size:.82rem;line-height:1.5;margin:.45rem 0}.risk-action{font-size:.75rem;padding:.6rem .7rem;border-radius:9px;background:rgba(255,255,255,.035);color:#d8dee7}
    .change-row{display:grid;grid-template-columns:30px 1fr auto;gap:.65rem;align-items:center;padding:.65rem .75rem;margin:.35rem 0;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.018);font-size:.78rem}.change-symbol.positive{color:var(--success)}.change-symbol.negative{color:var(--danger)}
    .assessment-score{padding:1.1rem}.score-ring{width:124px;height:124px;margin:0 auto .6rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2.3rem;font-weight:800;background:radial-gradient(circle at center,#10131a 57%,transparent 58%),conic-gradient(var(--primary),var(--primary-2) 300deg,rgba(255,255,255,.08) 300deg)}
    .empty-state{text-align:center;padding:3rem 1rem;border:1px dashed var(--line-strong);border-radius:16px;background:rgba(255,255,255,.012)}.empty-icon{font-size:2rem;color:#657083}.empty-title{font-weight:700;margin-top:.4rem}.empty-text{color:var(--muted);font-size:.8rem;max-width:500px;margin:.3rem auto;line-height:1.5}
    .stButton>button{border-radius:9px;font-weight:650;border:1px solid var(--line-strong);transition:.18s}.stButton>button:hover{border-color:rgba(139,92,246,.45);transform:translateY(-1px)}
    .stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]{background:#0f131a!important;border-radius:9px!important}.stProgress>div>div{border-radius:999px}.main .block-container{max-width:1450px;padding-top:1.1rem;padding-bottom:3rem}
    @media(max-width:900px){[data-testid="stSidebar"],[data-testid="stSidebar"]:hover{width:210px!important;min-width:210px!important;max-width:210px!important}.page-title{font-size:1.65rem!important}}
    </style>
    """, unsafe_allow_html=True)

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
    "Risk Center": risk_center_page,
    "Assessment": assessment_page,
    "Compare": compare_page,
}

with st.sidebar:
    st.markdown('<div class="sidebar-brand">RP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">GitHub Intelligence</div>', unsafe_allow_html=True)

    icon_options = ["📊", "📁", "👥", "🧠", "🚨", "🤖", "⚖️"]
    icon_page_map = {"📊": "Dashboard", "📁": "Repository", "👥": "Contributors", "🧠": "Code Insights", "🚨": "Risk Center", "🤖": "Assessment", "⚖️": "Compare"}
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
