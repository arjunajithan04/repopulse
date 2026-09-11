import streamlit as st

from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page
from pages.risk_center import risk_center_page
from pages.assessment import assessment_page
from pages.compare import compare_page
from pages.predictive import predictive_page


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
      --bg:#080a0f; --surface:#10131a; --surface-2:#141923; --surface-3:#1b202b;
      --line:rgba(255,255,255,.075); --line-strong:rgba(255,255,255,.13);
      --text:#f5f7fb; --muted:#8c97a8; --muted-2:#657083;
      --primary:#8b5cf6; --primary-2:#6366f1; --success:#34d399; --warning:#fbbf24; --danger:#fb7185;
      --shadow:0 18px 55px rgba(0,0,0,.20);
    }
    html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:var(--bg);color:var(--text)}
    .stApp{background:radial-gradient(circle at 8% -4%,rgba(139,92,246,.12),transparent 25%),radial-gradient(circle at 95% 5%,rgba(99,102,241,.07),transparent 22%),linear-gradient(180deg,#080a0f 0%,#0a0d13 100%)}
    [data-testid="stHeader"]{background:transparent}
    [data-testid="stSidebar"]{background:rgba(9,12,17,.96);backdrop-filter:blur(18px);border-right:1px solid var(--line);width:245px!important;min-width:245px!important;max-width:245px!important}
    [data-testid="stSidebarContent"]{padding:1.25rem .85rem}
    .sidebar-brand{display:flex;align-items:center;gap:.65rem;font-size:1.12rem;font-weight:850;letter-spacing:-.045em;margin:.2rem .35rem .1rem}
    .sidebar-logo{width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--primary),var(--primary-2));box-shadow:0 8px 24px rgba(99,102,241,.25);font-size:.72rem;font-weight:900;color:white}
    .sidebar-subtitle{font-size:.61rem;color:var(--muted-2);letter-spacing:.14em;text-transform:uppercase;margin:.1rem .4rem 1.3rem}
    .sidebar-section{font-size:.59rem;color:#596476;text-transform:uppercase;letter-spacing:.14em;margin:1.1rem .45rem .4rem}
    .stRadio>div{gap:.2rem}.stRadio [role="radio"]{border:1px solid transparent;border-radius:10px;padding:.55rem .68rem;color:var(--muted);transition:all .2s ease}.stRadio [role="radio"]:hover{background:rgba(255,255,255,.035);border-color:var(--line);transform:translateX(2px)}.stRadio [role="radio"][aria-checked="true"]{color:#fff;background:linear-gradient(90deg,rgba(139,92,246,.16),rgba(99,102,241,.07));border-color:rgba(139,92,246,.25);box-shadow:inset 2px 0 0 var(--primary)}
    .sidebar-status{margin-top:1rem;padding:.75rem;border:1px solid var(--line);border-radius:12px;background:linear-gradient(145deg,rgba(255,255,255,.035),rgba(255,255,255,.012));animation:fadeUp .45s ease both}.sidebar-status-label{font-size:.57rem;color:var(--muted-2);text-transform:uppercase;letter-spacing:.12em}.sidebar-status-name{font-size:.76rem;font-weight:700;margin-top:.3rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.sidebar-live{display:flex;align-items:center;gap:.38rem;font-size:.67rem;color:var(--success);margin-top:.65rem}.live-dot{width:6px;height:6px;border-radius:50%;background:var(--success);box-shadow:0 0 0 4px rgba(52,211,153,.09);animation:livePulse 2s infinite}
    .topbar{display:flex;justify-content:space-between;align-items:center;padding:.2rem 0 .85rem;border-bottom:1px solid var(--line);margin-bottom:1rem}.eyebrow{font-size:.62rem;font-weight:800;color:#8f9bad;text-transform:uppercase;letter-spacing:.15em;margin-bottom:.25rem}.page-title{font-size:2.05rem!important;letter-spacing:-.06em;margin:0!important;line-height:1.08}.page-description{color:var(--muted);font-size:.84rem;margin-top:.38rem;line-height:1.55;max-width:800px}
    .global-hero{position:relative;overflow:hidden;padding:1.15rem 1.35rem;border:1px solid var(--line);border-radius:16px;background:linear-gradient(135deg,rgba(17,21,29,.96),rgba(12,15,21,.94));margin-bottom:1.25rem;animation:fadeUp .45s ease both}.global-hero:after{content:"";position:absolute;width:220px;height:220px;right:-100px;top:-130px;background:radial-gradient(circle,rgba(139,92,246,.20),transparent 68%);pointer-events:none}.hero-kicker{font-size:.58rem;text-transform:uppercase;letter-spacing:.14em;color:var(--muted-2)}.hero-title{font-size:1.3rem;font-weight:780;letter-spacing:-.045em;margin-top:.18rem}.hero-subtitle{color:var(--muted);font-size:.78rem;margin-top:.3rem;line-height:1.45}.hero-meta{display:flex;gap:.5rem;align-items:center;margin-top:.75rem}.hero-meta-pill{font-size:.61rem;color:#b6c0cf;border:1px solid var(--line);border-radius:999px;padding:.28rem .5rem;background:rgba(255,255,255,.025)}
    .hero-card{padding:1.3rem 1.4rem;border:1px solid var(--line-strong);border-radius:18px;background:linear-gradient(135deg,rgba(18,22,30,.98),rgba(13,16,22,.96));box-shadow:var(--shadow);margin-bottom:1.05rem;animation:fadeUp .45s ease both}
    .metric-card{position:relative;overflow:hidden;background:linear-gradient(145deg,var(--surface),#0e1117);border:1px solid var(--line);border-radius:14px;padding:1rem;min-height:124px;box-shadow:0 10px 30px rgba(0,0,0,.12);transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;animation:fadeUp .42s ease both}.metric-card:before{content:"";position:absolute;inset:0;background:linear-gradient(120deg,rgba(139,92,246,.055),transparent 42%);pointer-events:none}.metric-card:hover{transform:translateY(-4px);border-color:rgba(139,92,246,.32);box-shadow:0 18px 42px rgba(0,0,0,.24)}.metric-top{display:flex;justify-content:space-between;align-items:center}.metric-label{font-size:.62rem;color:#7d8999;text-transform:uppercase;letter-spacing:.1em}.metric-icon{font-size:.75rem;color:#687486;width:24px;height:24px;border:1px solid var(--line);border-radius:7px;display:flex;align-items:center;justify-content:center}.metric-value{font-size:1.75rem;font-weight:800;letter-spacing:-.05em;margin-top:.42rem}.metric-delta{font-size:.72rem;font-weight:750;margin-top:.18rem}.metric-delta.good{color:var(--success)}.metric-delta.bad{color:var(--danger)}.metric-delta.neutral{color:var(--muted)}.metric-help{font-size:.64rem;color:#687486;margin-top:.45rem}
    .section-head{margin:.85rem 0 .7rem;animation:fadeUp .4s ease both}.section-eyebrow{font-size:.55rem;color:var(--primary);font-weight:800;text-transform:uppercase;letter-spacing:.14em;margin-bottom:.2rem}.section-title{font-size:1rem;font-weight:750;letter-spacing:-.025em}.section-subtitle{font-size:.72rem;color:var(--muted);margin-top:.16rem;line-height:1.45}.rp-divider{height:1px;background:var(--line);margin:1.3rem 0}
    .insight-card,.risk-card,.assessment-score{background:linear-gradient(145deg,var(--surface),#0e1117);border:1px solid var(--line);border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,.11);transition:transform .22s ease,border-color .22s ease;animation:fadeUp .42s ease both}.insight-card:hover,.risk-card:hover{transform:translateY(-3px);border-color:rgba(255,255,255,.13)}.insight-card{padding:.95rem 1rem;min-height:112px}.insight-card.good{border-color:rgba(52,211,153,.17)}.insight-card.warning{border-color:rgba(251,191,36,.17)}.insight-card.danger{border-color:rgba(251,113,133,.2)}.insight-top{display:flex;justify-content:space-between;align-items:center;min-height:22px}.insight-icon{font-size:.72rem;color:#748095}.insight-label{display:inline-block;font-size:.55rem;text-transform:uppercase;letter-spacing:.1em;padding:.2rem .43rem;border-radius:999px;background:rgba(255,255,255,.045);color:var(--muted)}.insight-label.good{color:var(--success);background:rgba(52,211,153,.07)}.insight-label.warning{color:var(--warning);background:rgba(251,191,36,.07)}.insight-label.danger{color:var(--danger);background:rgba(251,113,133,.07)}.insight-title{font-weight:720;margin-top:.5rem}.insight-text{color:var(--muted);font-size:.75rem;line-height:1.5;margin-top:.22rem}
    .status-badge{display:inline-flex;align-items:center;gap:.38rem;padding:.34rem .58rem;border-radius:999px;font-size:.58rem;font-weight:850;letter-spacing:.08em;border:1px solid var(--line)}.status-dot{width:5px;height:5px;border-radius:50%;background:currentColor}.status-badge.good{color:var(--success);background:rgba(52,211,153,.08);border-color:rgba(52,211,153,.2)}.status-badge.warning{color:var(--warning);background:rgba(251,191,36,.08);border-color:rgba(251,191,36,.2)}.status-badge.danger{color:var(--danger);background:rgba(251,113,133,.08);border-color:rgba(251,113,133,.2)}.status-badge.neutral{color:var(--muted)}
    .risk-card{padding:1rem 1.1rem;margin:.55rem 0}.risk-card.danger{border-color:rgba(251,113,133,.25)}.risk-card.warning{border-color:rgba(251,191,36,.22)}.risk-card.good{border-color:rgba(52,211,153,.2)}.risk-card-top{display:flex;align-items:center;gap:.55rem}.risk-detail{color:var(--muted);font-size:.79rem;line-height:1.5;margin:.5rem 0}.risk-action{font-size:.7rem;padding:.58rem .7rem;border-radius:9px;background:rgba(255,255,255,.035);color:#d8dee7}
    .change-row{display:grid;grid-template-columns:26px 1fr auto;gap:.65rem;align-items:center;padding:.62rem .72rem;margin:.35rem 0;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.018);font-size:.75rem;transition:background .18s ease,transform .18s ease}.change-row:hover{background:rgba(255,255,255,.035);transform:translateX(2px)}.change-symbol{font-weight:850}.change-symbol.positive{color:var(--success)}.change-symbol.negative{color:var(--danger)}
    .assessment-score{padding:1.1rem}.score-ring{width:132px;height:132px;margin:0 auto .65rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2.35rem;font-weight:850;background:radial-gradient(circle at center,#10131a 58%,transparent 59%),conic-gradient(var(--primary),var(--primary-2) 300deg,rgba(255,255,255,.08) 300deg);box-shadow:0 0 35px rgba(99,102,241,.10);animation:scoreIn .9s cubic-bezier(.2,.8,.2,1) both}.assessment-status{text-align:center;font-weight:800;font-size:.8rem}.assessment-caption{text-align:center;color:var(--muted);font-size:.65rem;margin-top:.2rem}
    .empty-state{text-align:center;padding:3.5rem 1rem;border:1px dashed var(--line-strong);border-radius:16px;background:rgba(255,255,255,.012);animation:fadeUp .5s ease both}.empty-icon{font-size:2rem;color:#657083}.empty-title{font-weight:720;margin-top:.5rem}.empty-text{color:var(--muted);font-size:.78rem;max-width:540px;margin:.35rem auto;line-height:1.55}.rp-callout{display:flex;gap:.7rem;padding:.8rem .9rem;border-radius:12px;border:1px solid var(--line);background:rgba(255,255,255,.025);margin:.5rem 0}.rp-callout.good{border-color:rgba(52,211,153,.18)}.rp-callout.warning{border-color:rgba(251,191,36,.18)}.rp-callout.danger{border-color:rgba(251,113,133,.2)}.rp-callout-icon{font-weight:850;color:var(--muted)}.rp-callout-title{font-size:.76rem;font-weight:750}.rp-callout-body{font-size:.7rem;color:var(--muted);margin-top:.12rem;line-height:1.45}
    .stButton>button{border-radius:9px;font-weight:700;border:1px solid var(--line-strong);transition:all .2s ease}.stButton>button:hover{border-color:rgba(139,92,246,.45);transform:translateY(-1px);box-shadow:0 8px 22px rgba(0,0,0,.16)}.stButton>button:active{transform:translateY(0)}.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"]{background:#0f131a!important;border-radius:9px!important;border-color:var(--line)!important}.stProgress>div>div{border-radius:999px}.main .block-container{max-width:1450px;padding-top:1rem;padding-bottom:3rem}.stTabs [data-baseweb="tab-list"]{gap:.25rem;border-bottom:1px solid var(--line)}.stTabs [data-baseweb="tab"]{font-size:.72rem;color:var(--muted);padding:.55rem .75rem}.stTabs [aria-selected="true"]{color:white}.stDataFrame{border:1px solid var(--line);border-radius:12px;overflow:hidden}.stAlert{border-radius:11px}
    @keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}@keyframes scoreIn{from{opacity:0;transform:scale(.86) rotate(-12deg)}to{opacity:1;transform:scale(1) rotate(0)}}@keyframes livePulse{0%,100%{box-shadow:0 0 0 3px rgba(52,211,153,.08)}50%{box-shadow:0 0 0 6px rgba(52,211,153,.02)}}
    @media(max-width:900px){[data-testid="stSidebar"],[data-testid="stSidebar"]:hover{width:215px!important;min-width:215px!important;max-width:215px!important}.page-title{font-size:1.65rem!important}.metric-card{min-height:110px}}
    @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
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
    "Predictive Risk": predictive_page,
}

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="sidebar-logo">RP</span> RepoPulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Repository intelligence</div>', unsafe_allow_html=True)

    icon_options = ["📊", "📁", "👥", "🧠", "🚨", "🤖", "⚖️", "🔮"]
    icon_page_map = {"📊": "Dashboard", "📁": "Repository", "👥": "Contributors", "🧠": "Code Insights", "🚨": "Risk Center", "🤖": "Assessment", "⚖️": "Compare", "🔮": "Predictive Risk"}
    selected_icon = st.radio(
        "Navigation",
        icon_options,
        index=0,
        label_visibility="collapsed",
    )
    selected_page = icon_page_map.get(selected_icon, "Dashboard")

    st.markdown("<hr style='border-color:rgba(255,255,255,.06)'>", unsafe_allow_html=True)
    if st.session_state.current_repo:
        st.markdown(f'''<div class="sidebar-status"><div class="sidebar-status-label">Active repository</div><div class="sidebar-status-name">{st.session_state.current_repo}</div><div class="sidebar-live"><span class="live-dot"></span>Telemetry connected</div></div>''', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-status"><div class="sidebar-status-label">Workspace</div><div class="sidebar-status-name">No repository selected</div></div>', unsafe_allow_html=True)
    st.caption(f"{st.session_state.repo_session_count}/10 analyses this session")
    if st.session_state.get("last_refresh"):
        st.caption(f"Last scan · {st.session_state.last_refresh}")

current_repo = st.session_state.get("current_repo")
hero_title = f"{current_repo} intelligence" if current_repo else "Repository Intelligence Dashboard"
hero_subtitle = (
    "Live repository telemetry is loaded. Re-scan to update metrics, compare against history, and surface what changed."
    if current_repo
    else "Analyze a GitHub repository to unlock live health, contributor, code-quality, trend, and risk intelligence."
)
st.markdown(
    f"""
    <div class="global-hero">
        <div class="hero-kicker">RepoPulse workspace</div>
        <div class="hero-title">{hero_title}</div>
        <div class="hero-subtitle">{hero_subtitle}</div>
        <div class="hero-meta">
            <span class="hero-meta-pill">Live analytics</span>
            <span class="hero-meta-pill">Historical snapshots</span>
            <span class="hero-meta-pill">Explainable intelligence</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pages[selected_page]()
