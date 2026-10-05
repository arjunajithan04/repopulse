import streamlit as st
import base64
import html

from pages.dashboard import dashboard_page
from pages.repository import repository_page
from pages.contributors import contributors_page
from pages.code_insights import code_insights_page
from pages.risk_center import risk_center_page
from pages.assessment import assessment_page
from pages.compare import compare_page
from pages.predictive import predictive_page
from components.interaction import init_interaction_state, render_focus_bar
from components.loading import scan_styles


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
      --bg: #080a0f;
      --surface: #10131a;
      --surface-2: #141923;
      --surface-3: #1b202b;
      --line: rgba(255, 255, 255, 0.075);
      --line-strong: rgba(255, 255, 255, 0.13);
      --text: #f5f7fb;
      --muted: #8c97a8;
      --muted-2: #657083;
      --primary: #8b5cf6;
      --primary-2: #6366f1;
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #fb7185;
      --shadow: 0 18px 55px rgba(0, 0, 0, 0.2);
    }
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
      background: var(--bg);
      color: var(--text);
    }
    .stApp {
      background:
        radial-gradient(
          circle at 8% -4%,
          rgba(139, 92, 246, 0.12),
          transparent 25%
        ),
        radial-gradient(
          circle at 95% 5%,
          rgba(99, 102, 241, 0.07),
          transparent 22%
        ),
        linear-gradient(180deg, #080a0f 0%, #0a0d13 100%);
    }
    [data-testid="stHeader"] {
      background: transparent;
    }
    [data-testid="stSidebarNav"] {
      display: none !important;
    }
    [data-testid="stSidebar"] {
      background: rgba(9, 12, 17, 0.96);
      backdrop-filter: blur(18px);
      border-right: 1px solid var(--line);
      width: 245px !important;
      min-width: 245px !important;
      max-width: 245px !important;
    }
    [data-testid="stSidebarContent"] {
      padding: 1.25rem 0.85rem;
    }
    .sidebar-brand {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      font-size: 1.12rem;
      font-weight: 850;
      letter-spacing: -0.045em;
      margin: 0.2rem 0.35rem 0.1rem;
    }
    .sidebar-logo {
      width: 34px;
      height: 34px;
      flex: 0 0 34px;
      display: block;
      object-fit: contain;
      border-radius: 10px;
      filter: drop-shadow(0 6px 14px rgba(99, 102, 241, 0.28));
      transition: transform 0.22s ease, filter 0.22s ease;
    }
    .sidebar-brand:hover .sidebar-logo {
      transform: scale(1.06) rotate(-2deg);
      filter: drop-shadow(0 8px 20px rgba(139, 92, 246, 0.4));
    }
    .sidebar-lock-card { margin-top:.8rem; padding:.85rem .78rem; border:1px solid rgba(139,92,246,.18); border-radius:12px; background:linear-gradient(145deg,rgba(139,92,246,.08),rgba(255,255,255,.015)); }
    .sidebar-lock-title { font-size:.68rem; font-weight:800; color:#e8e2ff; }
    .sidebar-lock-copy { margin-top:.28rem; font-size:.62rem; line-height:1.45; color:var(--muted); }
    .sidebar-locked-item { display:flex; align-items:center; gap:.55rem; padding:.48rem .55rem; color:#566173; font-size:.72rem; font-weight:650; border-radius:9px; }
    .sidebar-locked-item + .sidebar-locked-item { margin-top:.12rem; }
    .sidebar-locked-icon { width:17px; height:17px; display:inline-flex; align-items:center; justify-content:center; border:1px solid rgba(255,255,255,.08); border-radius:50%; font-size:.52rem; color:#697486; }
    .onboarding-shell { position:relative; overflow:hidden; padding:2rem 2rem 1.8rem; border:1px solid var(--line); border-radius:20px; background:linear-gradient(145deg,rgba(17,21,29,.97),rgba(10,13,19,.98)); box-shadow:var(--shadow); animation:fadeUp .5s ease both; }
    .onboarding-shell:before { content:''; position:absolute; width:360px; height:360px; right:-160px; top:-190px; background:radial-gradient(circle,rgba(139,92,246,.18),transparent 68%); pointer-events:none; }
    .onboarding-kicker { color:var(--primary); font-size:.62rem; font-weight:850; text-transform:uppercase; letter-spacing:.16em; }
    .onboarding-title { margin-top:.35rem; font-size:2.1rem; font-weight:820; letter-spacing:-.06em; max-width:760px; }
    .onboarding-copy { margin-top:.55rem; color:var(--muted); font-size:.86rem; line-height:1.6; max-width:760px; }
    .onboarding-steps { display:grid; grid-template-columns:repeat(3,1fr); gap:.7rem; margin-top:1.35rem; }
    .onboarding-step { padding:.85rem; border:1px solid var(--line); border-radius:12px; background:rgba(255,255,255,.018); }
    .onboarding-step-num { color:var(--primary); font:700 .62rem ui-monospace,SFMono-Regular,Menlo,monospace; }
    .onboarding-step-title { margin-top:.32rem; font-size:.73rem; font-weight:750; color:#e7ebf2; }
    .onboarding-step-copy { margin-top:.22rem; font-size:.62rem; line-height:1.45; color:var(--muted-2); }
    @media(max-width:700px){ .onboarding-shell{padding:1.35rem}.onboarding-title{font-size:1.65rem}.onboarding-steps{grid-template-columns:1fr} }
    .sidebar-subtitle {
      font-size: 0.61rem;
      color: var(--muted-2);
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin: 0.1rem 0.4rem 1.3rem;
    }
    .sidebar-section {
      font-size: 0.59rem;
      color: #596476;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      margin: 1.1rem 0.45rem 0.4rem;
    }
    .stRadio > div {
      gap: 0.2rem;
    }
    .stRadio [role="radio"] {
      display: flex;
      align-items: center;
      width: 100%;
      box-sizing: border-box;
      border: 1px solid transparent;
      border-radius: 10px;
      padding: 0.55rem 0.68rem;
      color: var(--muted);
      transition: all 0.2s ease;
      font-size: 0.76rem;
      font-weight: 650;
    }
    .stRadio [role="radio"]:hover {
      background: rgba(255, 255, 255, 0.035);
      border-color: var(--line);
      transform: translateX(2px);
    }
    .stRadio [role="radio"][aria-checked="true"] {
      color: #fff;
      background: linear-gradient(
        90deg,
        rgba(139, 92, 246, 0.18),
        rgba(99, 102, 241, 0.07)
      );
      border-color: rgba(139, 92, 246, 0.27);
      box-shadow:
        inset 2px 0 0 var(--primary),
        0 8px 24px rgba(0, 0, 0, 0.1);
    }
    .sidebar-status {
      margin-top: 1rem;
      padding: 0.75rem;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: linear-gradient(
        145deg,
        rgba(255, 255, 255, 0.035),
        rgba(255, 255, 255, 0.012)
      );
      animation: fadeUp 0.45s ease both;
    }
    .sidebar-status-label {
      font-size: 0.57rem;
      color: var(--muted-2);
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    .sidebar-status-name {
      font-size: 0.76rem;
      font-weight: 700;
      margin-top: 0.3rem;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .sidebar-live {
      display: flex;
      align-items: center;
      gap: 0.38rem;
      font-size: 0.67rem;
      color: var(--success);
      margin-top: 0.65rem;
    }
    .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.09);
      animation: livePulse 2s infinite;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.2rem 0 0.85rem;
      border-bottom: 1px solid var(--line);
      margin-bottom: 1rem;
    }
    .eyebrow {
      font-size: 0.62rem;
      font-weight: 800;
      color: #8f9bad;
      text-transform: uppercase;
      letter-spacing: 0.15em;
      margin-bottom: 0.25rem;
    }
    .page-title {
      font-size: 2.05rem !important;
      letter-spacing: -0.06em;
      margin: 0 !important;
      line-height: 1.08;
    }
    .page-description {
      color: var(--muted);
      font-size: 0.84rem;
      margin-top: 0.38rem;
      line-height: 1.55;
      max-width: 800px;
    }
    .global-hero {
      position: relative;
      overflow: hidden;
      padding: 1.15rem 1.35rem;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: linear-gradient(
        135deg,
        rgba(17, 21, 29, 0.96),
        rgba(12, 15, 21, 0.94)
      );
      margin-bottom: 1.25rem;
      animation: fadeUp 0.45s ease both;
    }
    .global-hero:after {
      content: "";
      position: absolute;
      width: 220px;
      height: 220px;
      right: -100px;
      top: -130px;
      background: radial-gradient(circle, rgba(139, 92, 246, 0.2), transparent 68%);
      pointer-events: none;
    }
    .hero-kicker {
      font-size: 0.58rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--muted-2);
    }
    .hero-title {
      font-size: 1.3rem;
      font-weight: 780;
      letter-spacing: -0.045em;
      margin-top: 0.18rem;
    }
    .hero-subtitle {
      color: var(--muted);
      font-size: 0.78rem;
      margin-top: 0.3rem;
      line-height: 1.45;
    }
    .hero-meta {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      margin-top: 0.75rem;
    }
    .hero-meta-pill {
      font-size: 0.61rem;
      color: #b6c0cf;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 0.28rem 0.5rem;
      background: rgba(255, 255, 255, 0.025);
    }
    .hero-card {
      padding: 1.3rem 1.4rem;
      border: 1px solid var(--line-strong);
      border-radius: 18px;
      background: linear-gradient(
        135deg,
        rgba(18, 22, 30, 0.98),
        rgba(13, 16, 22, 0.96)
      );
      box-shadow: var(--shadow);
      margin-bottom: 1.05rem;
      animation: fadeUp 0.45s ease both;
    }
    .metric-card {
      position: relative;
      overflow: hidden;
      background: linear-gradient(145deg, var(--surface), #0e1117);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1rem;
      min-height: 124px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
      transition:
        transform 0.22s ease,
        border-color 0.22s ease,
        box-shadow 0.22s ease;
      animation: fadeUp 0.42s ease both;
    }
    .metric-card:before {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(
        120deg,
        rgba(139, 92, 246, 0.055),
        transparent 42%
      );
      pointer-events: none;
    }
    .metric-card:hover {
      transform: translateY(-4px);
      border-color: rgba(139, 92, 246, 0.32);
      box-shadow: 0 18px 42px rgba(0, 0, 0, 0.24);
    }
    .metric-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .metric-label {
      font-size: 0.62rem;
      color: #7d8999;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .metric-icon {
      font-size: 0.75rem;
      color: #687486;
      width: 24px;
      height: 24px;
      border: 1px solid var(--line);
      border-radius: 7px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .metric-value {
      font-size: 1.75rem;
      font-weight: 800;
      letter-spacing: -0.05em;
      margin-top: 0.42rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      min-width: 0;
    }
    .metric-delta {
      font-size: 0.72rem;
      font-weight: 750;
      margin-top: 0.18rem;
    }
    .metric-delta.good {
      color: var(--success);
    }
    .metric-delta.bad {
      color: var(--danger);
    }
    .metric-delta.neutral {
      color: var(--muted);
    }
    .metric-help {
      font-size: 0.64rem;
      color: #687486;
      margin-top: 0.45rem;
    }
    .section-head {
      margin: 0.85rem 0 0.7rem;
      animation: fadeUp 0.4s ease both;
    }
    .section-eyebrow {
      font-size: 0.55rem;
      color: var(--primary);
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      margin-bottom: 0.2rem;
    }
    .section-title {
      font-size: 1rem;
      font-weight: 750;
      letter-spacing: -0.025em;
    }
    .section-subtitle {
      font-size: 0.72rem;
      color: var(--muted);
      margin-top: 0.16rem;
      line-height: 1.45;
    }
    .rp-divider {
      height: 1px;
      background: var(--line);
      margin: 1.3rem 0;
    }
    .insight-card,
    .risk-card,
    .assessment-score {
      background: linear-gradient(145deg, var(--surface), #0e1117);
      border: 1px solid var(--line);
      border-radius: 15px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.11);
      transition:
        transform 0.22s ease,
        border-color 0.22s ease;
      animation: fadeUp 0.42s ease both;
    }
    .insight-card:hover,
    .risk-card:hover {
      transform: translateY(-3px);
      border-color: rgba(255, 255, 255, 0.13);
    }
    .insight-card {
      padding: 0.95rem 1rem;
      min-height: 112px;
    }
    .insight-card.good {
      border-color: rgba(52, 211, 153, 0.17);
    }
    .insight-card.warning {
      border-color: rgba(251, 191, 36, 0.17);
    }
    .insight-card.danger {
      border-color: rgba(251, 113, 133, 0.2);
    }
    .insight-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      min-height: 22px;
    }
    .insight-icon {
      font-size: 0.72rem;
      color: #748095;
    }
    .insight-label {
      display: inline-block;
      font-size: 0.55rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      padding: 0.2rem 0.43rem;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.045);
      color: var(--muted);
    }
    .insight-label.good {
      color: var(--success);
      background: rgba(52, 211, 153, 0.07);
    }
    .insight-label.warning {
      color: var(--warning);
      background: rgba(251, 191, 36, 0.07);
    }
    .insight-label.danger {
      color: var(--danger);
      background: rgba(251, 113, 133, 0.07);
    }
    .insight-title {
      font-weight: 720;
      margin-top: 0.5rem;
    }
    .insight-text {
      color: var(--muted);
      font-size: 0.75rem;
      line-height: 1.5;
      margin-top: 0.22rem;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.38rem;
      padding: 0.34rem 0.58rem;
      border-radius: 999px;
      font-size: 0.58rem;
      font-weight: 850;
      letter-spacing: 0.08em;
      border: 1px solid var(--line);
    }
    .status-dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: currentColor;
    }
    .status-badge.good {
      color: var(--success);
      background: rgba(52, 211, 153, 0.08);
      border-color: rgba(52, 211, 153, 0.2);
    }
    .status-badge.warning {
      color: var(--warning);
      background: rgba(251, 191, 36, 0.08);
      border-color: rgba(251, 191, 36, 0.2);
    }
    .status-badge.danger {
      color: var(--danger);
      background: rgba(251, 113, 133, 0.08);
      border-color: rgba(251, 113, 133, 0.2);
    }
    .status-badge.neutral {
      color: var(--muted);
    }
    .risk-card {
      padding: 1rem 1.1rem;
      margin: 0.55rem 0;
    }
    .risk-card.danger {
      border-color: rgba(251, 113, 133, 0.25);
    }
    .risk-card.warning {
      border-color: rgba(251, 191, 36, 0.22);
    }
    .risk-card.good {
      border-color: rgba(52, 211, 153, 0.2);
    }
    .risk-card-top {
      display: flex;
      align-items: center;
      gap: 0.55rem;
    }
    .risk-detail {
      color: var(--muted);
      font-size: 0.79rem;
      line-height: 1.5;
      margin: 0.5rem 0;
    }
    .risk-action {
      font-size: 0.7rem;
      padding: 0.58rem 0.7rem;
      border-radius: 9px;
      background: rgba(255, 255, 255, 0.035);
      color: #d8dee7;
    }
    .change-row {
      display: grid;
      grid-template-columns: 26px 1fr auto;
      gap: 0.65rem;
      align-items: center;
      padding: 0.62rem 0.72rem;
      margin: 0.35rem 0;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.018);
      font-size: 0.75rem;
      transition:
        background 0.18s ease,
        transform 0.18s ease;
    }
    .change-row:hover {
      background: rgba(255, 255, 255, 0.035);
      transform: translateX(2px);
    }
    .change-symbol {
      font-weight: 850;
    }
    .change-symbol.positive {
      color: var(--success);
    }
    .change-symbol.negative {
      color: var(--danger);
    }
    .assessment-score {
      padding: 1.1rem;
    }
    .score-ring {
      width: 132px;
      height: 132px;
      margin: 0 auto 0.65rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.35rem;
      font-weight: 850;
      background:
        radial-gradient(circle at center, #10131a 58%, transparent 59%),
        conic-gradient(
          var(--primary),
          var(--primary-2) 300deg,
          rgba(255, 255, 255, 0.08) 300deg
        );
      box-shadow: 0 0 35px rgba(99, 102, 241, 0.1);
      animation: scoreIn 0.9s cubic-bezier(0.2, 0.8, 0.2, 1) both;
    }
    .assessment-status {
      text-align: center;
      font-weight: 800;
      font-size: 0.8rem;
    }
    .assessment-caption {
      text-align: center;
      color: var(--muted);
      font-size: 0.65rem;
      margin-top: 0.2rem;
    }
    .empty-state {
      text-align: center;
      padding: 3.5rem 1rem;
      border: 1px dashed var(--line-strong);
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.012);
      animation: fadeUp 0.5s ease both;
    }
    .empty-icon {
      font-size: 2rem;
      color: #657083;
    }
    .empty-title {
      font-weight: 720;
      margin-top: 0.5rem;
    }
    .empty-text {
      color: var(--muted);
      font-size: 0.78rem;
      max-width: 540px;
      margin: 0.35rem auto;
      line-height: 1.55;
    }
    .rp-callout {
      display: flex;
      gap: 0.7rem;
      padding: 0.8rem 0.9rem;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.025);
      margin: 0.5rem 0;
    }
    .rp-callout.good {
      border-color: rgba(52, 211, 153, 0.18);
    }
    .rp-callout.warning {
      border-color: rgba(251, 191, 36, 0.18);
    }
    .rp-callout.danger {
      border-color: rgba(251, 113, 133, 0.2);
    }
    .rp-callout-icon {
      font-weight: 850;
      color: var(--muted);
    }
    .rp-callout-title {
      font-size: 0.76rem;
      font-weight: 750;
    }
    .rp-callout-body {
      font-size: 0.7rem;
      color: var(--muted);
      margin-top: 0.12rem;
      line-height: 1.45;
    }
    .stButton > button {
      border-radius: 9px;
      font-weight: 700;
      border: 1px solid var(--line-strong);
      transition: all 0.2s ease;
    }
    .stButton > button:hover {
      border-color: rgba(139, 92, 246, 0.45);
      transform: translateY(-1px);
      box-shadow: 0 8px 22px rgba(0, 0, 0, 0.16);
    }
    .stButton > button:active {
      transform: translateY(0);
    }
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] {
      background: #0f131a !important;
      border-radius: 9px !important;
      border-color: var(--line) !important;
    }
    .stProgress > div > div {
      border-radius: 999px;
    }
    .main .block-container {
      max-width: 1450px;
      padding-top: 1rem;
      padding-bottom: 3rem;
    }
    .stTabs [data-baseweb="tab-list"] {
      gap: 0.25rem;
      border-bottom: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
      font-size: 0.72rem;
      color: var(--muted);
      padding: 0.55rem 0.75rem;
    }
    .stTabs [aria-selected="true"] {
      color: white;
    }
    .stDataFrame {
      border: 1px solid var(--line);
      border-radius: 12px;
      overflow: hidden;
    }
    .stAlert {
      border-radius: 11px;
    }
    @keyframes fadeUp {
      from {
        opacity: 0;
        transform: translateY(8px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    @keyframes scoreIn {
      from {
        opacity: 0;
        transform: scale(0.86) rotate(-12deg);
      }
      to {
        opacity: 1;
        transform: scale(1) rotate(0);
      }
    }
    @keyframes livePulse {
      0%,
      100% {
        box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.08);
      }
      50% {
        box-shadow: 0 0 0 6px rgba(52, 211, 153, 0.02);
      }
    }
    @media (max-width: 900px) {
      [data-testid="stSidebar"],
      [data-testid="stSidebar"]:hover {
        width: 215px !important;
        min-width: 215px !important;
        max-width: 215px !important;
      }
      .page-title {
        font-size: 1.65rem !important;
      }
      .metric-card {
        min-height: 110px;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
    }

    .rp-focus-bar {
      display: flex;
      align-items: center;
      padding: 0.55rem 0.8rem;
      margin: -0.35rem 0 1rem;
      border: 1px solid rgba(139, 92, 246, 0.22);
      border-radius: 10px;
      background: linear-gradient(
        90deg,
        rgba(139, 92, 246, 0.1),
        rgba(99, 102, 241, 0.035)
      );
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      animation: fadeUp 0.35s ease both;
    }
    .rp-focus-kicker {
      font-size: 0.54rem;
      color: var(--primary);
      font-weight: 850;
      letter-spacing: 0.14em;
      margin-right: 0.55rem;
    }
    .rp-focus-label {
      font-size: 0.64rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-right: 0.35rem;
    }
    .rp-focus-value {
      font-size: 0.72rem;
      color: #fff;
      font-weight: 750;
    }
    .rp-focus-source {
      font-size: 0.59rem;
      color: var(--muted-2);
      margin-left: 0.45rem;
    }
    /* 1. Visual integrity layer: styles for the cinematic and repository components. */
    [data-testid="stMetric"] {
      padding: 0.9rem 1rem;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: linear-gradient(145deg, var(--surface), #0e1117);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      transition:
        transform 0.2s ease,
        border-color 0.2s ease;
    }
    .stMetricLabel {
      font-size: 0.62rem !important;
      color: #7d8999 !important;
      text-transform: uppercase;
      letter-spacing: 0.09em;
    }
    .stMetricValue {
      font-size: 1.55rem !important;
      font-weight: 820 !important;
      letter-spacing: -0.05em;
    }
    .stMetricDelta {
      font-size: 0.68rem !important;
    }
    .stDownloadButton > button {
      border-radius: 9px;
      font-weight: 750;
      border: 1px solid rgba(139, 92, 246, 0.28);
      background: linear-gradient(
        90deg,
        rgba(139, 92, 246, 0.14),
        rgba(99, 102, 241, 0.08)
      );
      color: #f4f1ff;
    }
    .stDownloadButton > button:hover {
      border-color: rgba(139, 92, 246, 0.48);
      background: linear-gradient(
        90deg,
        rgba(139, 92, 246, 0.2),
        rgba(99, 102, 241, 0.12)
      );
    }
    .sidebar-meta {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.65rem;
      margin-top: 0.52rem;
      font-size: 0.61rem;
      color: var(--muted-2);
      line-height: 1.35;
    }
    .sidebar-count {
      color: #cbd3df;
      font-weight: 750;
      text-align: right;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .sidebar-status + .stCaption {
      color: var(--muted-2);
    }
    .metric-value-row {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 0.65rem;
      min-width: 0;
    }
    .metric-value-row .metric-value {
      min-width: 0;
    }
    .metric-spark {
      width: 76px;
      height: 24px;
      flex: 0 0 76px;
      overflow: visible;
      opacity: 0.85;
      margin-bottom: 0.18rem;
    }
    .metric-spark polyline {
      fill: none;
      stroke: var(--primary);
      stroke-width: 2.2;
      stroke-linecap: round;
      stroke-linejoin: round;
      vector-effect: non-scaling-stroke;
    }
    .metric-card.good .metric-spark polyline {
      stroke: var(--success);
    }
    .metric-card.bad .metric-spark polyline {
      stroke: var(--danger);
    }
    .metric-progress {
      height: 4px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.055);
      overflow: hidden;
      margin-top: 0.58rem;
    }
    .metric-progress span {
      display: block;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--primary), var(--primary-2));
      transition: width 0.65s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    .metric-card.good .metric-progress span {
      background: linear-gradient(90deg, #10b981, var(--success));
    }
    .metric-card.bad .metric-progress span {
      background: linear-gradient(90deg, #f43f5e, var(--danger));
    }
    .health-dimension {
      margin: 0.62rem 0;
    }
    .health-dimension-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.69rem;
      color: #aeb7c5;
    }
    .health-dimension-top strong {
      font-size: 0.69rem;
    }
    .health-dimension-top strong.good {
      color: var(--success);
    }
    .health-dimension-top strong.warning {
      color: var(--warning);
    }
    .health-dimension-top strong.danger {
      color: var(--danger);
    }
    .health-track {
      height: 5px;
      background: rgba(255, 255, 255, 0.055);
      border-radius: 999px;
      overflow: hidden;
      margin-top: 0.35rem;
    }
    .health-track span {
      display: block;
      height: 100%;
      border-radius: inherit;
      transition: width 0.65s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    .health-track span.good {
      background: linear-gradient(90deg, #10b981, var(--success));
    }
    .health-track span.warning {
      background: linear-gradient(90deg, #d97706, var(--warning));
    }
    .health-track span.danger {
      background: linear-gradient(90deg, #e11d48, var(--danger));
    }
    .health-panel {
      padding: 1rem;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: linear-gradient(
        145deg,
        rgba(16, 19, 26, 0.92),
        rgba(12, 15, 21, 0.78)
      );
      box-shadow: 0 14px 38px rgba(0, 0, 0, 0.14);
    }
    .mini-risk {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      padding: 0.75rem 0.8rem;
      margin-bottom: 0.55rem;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.018);
      transition:
        transform 0.18s ease,
        border-color 0.18s ease,
        background 0.18s ease;
    }
    .mini-risk:hover {
      transform: translateX(3px);
      background: rgba(255, 255, 255, 0.03);
    }
    .mini-risk.danger {
      border-color: rgba(251, 113, 133, 0.2);
    }
    .mini-risk.warning {
      border-color: rgba(251, 191, 36, 0.18);
    }
    .mini-risk-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--warning);
      box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.08);
      flex: 0 0 auto;
    }
    .mini-risk.danger .mini-risk-dot {
      background: var(--danger);
      box-shadow: 0 0 0 4px rgba(251, 113, 133, 0.08);
    }
    .mini-risk strong {
      display: block;
      font-size: 0.72rem;
      color: #e9edf4;
    }
    .mini-risk span {
      display: block;
      font-size: 0.59rem;
      color: var(--muted-2);
      margin-top: 0.15rem;
    }
    .repo-hero {
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 220px;
      gap: 1.2rem;
      overflow: hidden;
      padding: 1.35rem 1.4rem;
      margin-bottom: 1rem;
      border: 1px solid var(--line-strong);
      border-radius: 18px;
      background: linear-gradient(
        135deg,
        rgba(18, 22, 30, 0.98),
        rgba(11, 14, 20, 0.96)
      );
      box-shadow: var(--shadow);
      animation: fadeUp 0.45s ease both;
    }
    .repo-hero-glow {
      position: absolute;
      width: 320px;
      height: 320px;
      right: -140px;
      top: -190px;
      border-radius: 50%;
      background: radial-gradient(
        circle,
        rgba(139, 92, 246, 0.18),
        transparent 68%
      );
      pointer-events: none;
    }
    .repo-hero-main,
    .repo-hero-side {
      position: relative;
      z-index: 1;
    }
    .repo-kicker,
    .repo-health-label {
      font-size: 0.56rem;
      color: var(--muted-2);
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }
    .repo-name {
      font-size: 1.55rem;
      font-weight: 820;
      letter-spacing: -0.055em;
      margin-top: 0.28rem;
      overflow-wrap: anywhere;
    }
    .repo-description {
      max-width: 760px;
      color: #b5bfcd;
      font-size: 0.79rem;
      line-height: 1.55;
      margin-top: 0.4rem;
    }
    .repo-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      margin-top: 0.8rem;
    }
    .repo-hero-side {
      padding-left: 1.1rem;
      border-left: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
    }
    .repo-health-score {
      font-size: 2.45rem;
      font-weight: 880;
      letter-spacing: -0.07em;
      line-height: 1;
      margin: 0.3rem 0 0.5rem;
    }
    .repo-health-score span {
      font-size: 0.72rem;
      color: var(--muted);
      font-weight: 650;
      letter-spacing: 0;
      margin-left: 0.18rem;
    }
    .repo-health-delta {
      font-size: 0.63rem;
      color: var(--muted);
      margin-top: 0.5rem;
    }
    .repo-link {
      display: inline-flex;
      margin-top: 0.75rem;
      color: #c4b5fd;
      text-decoration: none;
      font-size: 0.68rem;
      font-weight: 750;
    }
    .repo-link:hover {
      text-decoration: underline;
      color: #ddd6fe;
    }
    .risk-stack {
      padding: 0.1rem 0;
    }
    .health-panel .js-plotly-plot {
      margin-bottom: 0.35rem;
    }
    .health-orb-card {
      position: relative;
      min-height: 330px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      padding: 1rem;
      border: 1px solid var(--line-strong);
      border-radius: 18px;
      background:
        radial-gradient(
          circle at 50% 45%,
          rgba(139, 92, 246, 0.055),
          transparent 42%
        ),
        linear-gradient(145deg, rgba(16, 19, 26, 0.96), rgba(10, 13, 18, 0.92));
      box-shadow: var(--shadow);
      isolation: isolate;
      animation: fadeUp 0.55s ease both;
    }
    .health-orb-glow {
      position: absolute;
      width: 210px;
      height: 210px;
      border-radius: 50%;
      filter: blur(26px);
      opacity: 0.18;
      z-index: -1;
    }
    .health-orb-glow.good {
      background: var(--success);
    }
    .health-orb-glow.warning {
      background: var(--warning);
    }
    .health-orb-glow.danger {
      background: var(--danger);
    }
    .health-orb {
      width: min(270px, 72%);
      height: auto;
      display: block;
      overflow: visible;
      filter: drop-shadow(0 0 18px rgba(139, 92, 246, 0.12));
      transform: rotate(-90deg);
      animation: scoreIn 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) both;
    }
    .orb-track,
    .orb-value {
      fill: none;
      stroke-width: 7;
      vector-effect: non-scaling-stroke;
    }
    .orb-track {
      stroke: rgba(255, 255, 255, 0.075);
    }
    .orb-value {
      stroke-linecap: round;
    }
    .orb-value.good {
      stroke: var(--success);
    }
    .orb-value.warning {
      stroke: var(--warning);
    }
    .orb-value.danger {
      stroke: var(--danger);
    }
    .health-orb-content {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      pointer-events: none;
    }
    .health-orb-score {
      font-size: 3.2rem;
      font-weight: 900;
      letter-spacing: -0.08em;
      line-height: 1;
    }
    .health-orb-label {
      font-size: 0.56rem;
      color: var(--muted-2);
      letter-spacing: 0.13em;
      margin-top: 0.22rem;
    }
    .health-orb-status {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      margin-top: 0.55rem;
      padding: 0.28rem 0.5rem;
      border-radius: 999px;
      font-size: 0.56rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      border: 1px solid var(--line);
    }
    .health-orb-status.good {
      color: var(--success);
      background: rgba(52, 211, 153, 0.07);
      border-color: rgba(52, 211, 153, 0.18);
    }
    .health-orb-status.warning {
      color: var(--warning);
      background: rgba(251, 191, 36, 0.07);
      border-color: rgba(251, 191, 36, 0.18);
    }
    .health-orb-status.danger {
      color: var(--danger);
      background: rgba(251, 113, 133, 0.07);
      border-color: rgba(251, 113, 133, 0.18);
    }
    .health-orb-delta {
      position: absolute;
      bottom: 0.9rem;
      left: 0;
      right: 0;
      text-align: center;
      color: var(--muted);
      font-size: 0.63rem;
    }
    .cinematic-spotlight {
      position: relative;
      min-height: 330px;
      overflow: hidden;
      padding: 1.45rem;
      border: 1px solid var(--line-strong);
      border-radius: 18px;
      background: linear-gradient(
        145deg,
        rgba(17, 21, 29, 0.98),
        rgba(11, 14, 20, 0.94)
      );
      box-shadow: var(--shadow);
      animation: fadeUp 0.62s ease both;
    }
    .cinematic-spotlight:after {
      content: "";
      position: absolute;
      right: -90px;
      bottom: -110px;
      width: 250px;
      height: 250px;
      border-radius: 50%;
      background: radial-gradient(
        circle,
        rgba(139, 92, 246, 0.14),
        transparent 68%
      );
      pointer-events: none;
    }
    .cinematic-spotlight.good {
      border-color: rgba(52, 211, 153, 0.2);
    }
    .cinematic-spotlight.warning {
      border-color: rgba(251, 191, 36, 0.2);
    }
    .cinematic-spotlight.danger {
      border-color: rgba(251, 113, 133, 0.23);
    }
    .spotlight-orbit {
      position: absolute;
      right: 28px;
      top: 28px;
      width: 90px;
      height: 90px;
      border: 1px solid rgba(139, 92, 246, 0.16);
      border-radius: 50%;
      box-shadow: 0 0 35px rgba(139, 92, 246, 0.07);
    }
    .spotlight-orbit:after {
      content: "";
      position: absolute;
      inset: 14px;
      border: 1px dashed rgba(255, 255, 255, 0.08);
      border-radius: 50%;
      animation: orbitSpin 10s linear infinite;
    }
    .cinematic-kicker {
      font-size: 0.57rem;
      color: var(--primary);
      font-weight: 850;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }
    .cinematic-title {
      font-size: 1.55rem;
      font-weight: 820;
      letter-spacing: -0.055em;
      margin-top: 0.65rem;
      max-width: 70%;
    }
    .cinematic-body {
      color: #b8c1ce;
      font-size: 0.82rem;
      line-height: 1.65;
      max-width: 650px;
      margin-top: 0.55rem;
    }
    .cinematic-detail {
      position: absolute;
      left: 1.45rem;
      right: 1.45rem;
      bottom: 1.25rem;
      padding: 0.7rem 0.8rem;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.025);
      color: #d5dbe5;
      font-size: 0.68rem;
      line-height: 1.45;
    }
    .telemetry-strip {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.55rem;
      margin: 0 0 1.1rem;
      padding: 0.55rem;
      border: 1px solid var(--line);
      border-radius: 13px;
      background: rgba(255, 255, 255, 0.018);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
      animation: fadeUp 0.48s ease both;
    }
    .telemetry-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      padding: 0.6rem 0.7rem;
      border-radius: 9px;
      background: rgba(255, 255, 255, 0.018);
      min-width: 0;
    }
    .telemetry-label {
      font-size: 0.57rem;
      color: var(--muted-2);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .telemetry-value {
      font-size: 0.7rem;
      font-weight: 800;
      color: #dbe1ea;
      white-space: nowrap;
    }
    .telemetry-value.good {
      color: var(--success);
    }
    .telemetry-value.warning {
      color: var(--warning);
    }
    .telemetry-value.danger {
      color: var(--danger);
    }
    .telemetry-value.neutral {
      color: #c8d0dc;
    }
    .report-toolbar {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 0.9rem;
      margin: 0.65rem 0;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: linear-gradient(
        90deg,
        rgba(139, 92, 246, 0.07),
        rgba(255, 255, 255, 0.018)
      );
    }
    .report-toolbar-copy {
      font-size: 0.69rem;
      color: var(--muted);
      line-height: 1.45;
    }
    .report-toolbar-copy strong {
      display: block;
      color: #e8ecf3;
      font-size: 0.74rem;
      margin-bottom: 0.08rem;
    }
    @keyframes orbitSpin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }
    @media (max-width: 900px) {
      .repo-hero {
        grid-template-columns: 1fr;
      }
      .repo-hero-side {
        border-left: 0;
        border-top: 1px solid var(--line);
        padding-left: 0;
        padding-top: 1rem;
      }
      .health-orb-card,
      .cinematic-spotlight {
        min-height: 290px;
      }
      .telemetry-strip {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    @media (max-width: 600px) {
      .telemetry-strip {
        grid-template-columns: 1fr;
      }
      .repo-name {
        font-size: 1.25rem;
      }
      .cinematic-title {
        max-width: 100%;
        font-size: 1.25rem;
      }
      .spotlight-orbit {
        opacity: 0.45;
      }
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Shared session state
# -----------------------------------------------------------------------------


st.markdown(
    """
    <style>
    .rp-scan-screen {
      position: relative; min-height: 78vh; margin: -1rem -1rem 0;
      overflow: hidden; display:flex; align-items:center; justify-content:center;
      background: radial-gradient(circle at 50% 40%,rgba(112,88,255,.14),transparent 30%),
                  radial-gradient(circle at 20% 80%,rgba(65,105,225,.08),transparent 28%),#07070b;
      border:1px solid rgba(255,255,255,.07); border-radius:24px; isolation:isolate;
    }
    .rp-scan-grid { position:absolute; inset:0; opacity:.22;
      background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),
                       linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);
      background-size:42px 42px; mask-image:radial-gradient(circle at center,#000,transparent 78%);
      animation:rp-grid-drift 12s linear infinite;
    }
    .rp-scan-content { position:relative; z-index:2; width:min(620px,88%); text-align:center;
      animation:rp-fade-up .7s ease both;
    }
    .rp-scan-brand { font-size:1.65rem; font-weight:800; letter-spacing:.24em; color:#f6f5ff; }
    .rp-scan-kicker { margin-top:.35rem; font-size:.68rem; letter-spacing:.28em; color:rgba(190,185,255,.62); }
    .rp-pulse-orb { position:relative; width:150px; height:150px; margin:2.5rem auto 1.7rem;
      display:grid; place-items:center; }
    .rp-pulse-core { position:relative; z-index:4; width:46px; height:46px; display:grid;
      place-items:center; border-radius:50%; color:#fff; background:radial-gradient(circle at 35% 30%,#c9c2ff,#7765ff 48%,#3f2fa5);
      box-shadow:0 0 36px rgba(116,97,255,.65),0 0 90px rgba(116,97,255,.2);
      animation:rp-core-pulse 1.8s ease-in-out infinite;
    }
    .rp-pulse-ring { position:absolute; inset:25px; border:1px solid rgba(139,124,255,.5);
      border-radius:50%; animation:rp-ring 2.4s ease-out infinite; }
    .rp-ring-2 { animation-delay:.8s; } .rp-ring-3 { animation-delay:1.6s; }
    .rp-scan-title { font-size:.76rem; letter-spacing:.22em; font-weight:700; color:#f0eff8; }
    .rp-scan-repo { margin-top:.55rem; font: .85rem ui-monospace,SFMono-Regular,Menlo,monospace;
      color:rgba(224,222,240,.56); overflow:hidden; text-overflow:ellipsis; }
    .rp-scan-progress { width:100%; height:3px; margin:1.7rem auto .8rem; overflow:hidden;
      border-radius:99px; background:rgba(255,255,255,.07); }
    .rp-scan-progress span { display:block; width:46%; height:100%; border-radius:inherit;
      background:linear-gradient(90deg,#6554ff,#9a8fff,#6554ff); background-size:180% 100%;
      box-shadow:0 0 18px rgba(111,91,255,.55); animation:rp-progress 2.2s ease-in-out infinite; }
    .rp-scan-stage { display:flex; justify-content:center; align-items:center; gap:.55rem;
      min-height:22px; color:rgba(235,233,247,.78); font-size:.76rem; }
    .rp-scan-stage i { width:6px; height:6px; border-radius:50%; background:#8d7dff;
      box-shadow:0 0 12px rgba(141,125,255,.9); animation:rp-dot 1s ease-in-out infinite; }
    .rp-scan-steps { margin:1.5rem auto 0; display:grid; grid-template-columns:repeat(2,1fr);
      gap:.55rem; text-align:left; }
    .rp-scan-steps div { padding:.62rem .75rem; border:1px solid rgba(255,255,255,.055);
      border-radius:10px; background:rgba(255,255,255,.018); color:rgba(221,219,235,.52);
      font-size:.63rem; letter-spacing:.08em; }
    .rp-scan-steps b { color:rgba(151,139,255,.72); font: .58rem ui-monospace,monospace; margin-right:.55rem; }
    .rp-scan-terminal { margin:1.2rem auto 0; padding:.8rem .95rem; text-align:left;
      border:1px solid rgba(255,255,255,.055); border-radius:12px; background:rgba(0,0,0,.22);
      font:.65rem/1.65 ui-monospace,SFMono-Regular,Menlo,monospace; color:rgba(170,165,195,.48); }
    @keyframes rp-ring { 0%{transform:scale(.65);opacity:.8} 80%,100%{transform:scale(1.55);opacity:0} }
    @keyframes rp-core-pulse { 0%,100%{transform:scale(.94)} 50%{transform:scale(1.08)} }
    @keyframes rp-progress { 0%{transform:translateX(-110%)} 50%{transform:translateX(70%)} 100%{transform:translateX(190%)} }
    @keyframes rp-dot { 0%,100%{opacity:.35;transform:scale(.8)} 50%{opacity:1;transform:scale(1.15)} }
    @keyframes rp-grid-drift { from{transform:translate(0,0)} to{transform:translate(42px,42px)} }
    @keyframes rp-fade-up { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
    @media(max-width:700px){ .rp-scan-screen{min-height:84vh;border-radius:18px}.rp-scan-steps{grid-template-columns:1fr} }
    @media(prefers-reduced-motion:reduce){
      .rp-scan-grid,.rp-pulse-core,.rp-pulse-ring,.rp-scan-progress span,.rp-scan-stage i,.rp-scan-content{animation:none!important}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def maybe_show_scan_preview():
    try:
        if st.query_params.get("scan_preview") == "1":
            render_repository_scan_loader("github.com/owner/repository")
            st.stop()
    except Exception:
        pass

def render_repository_scan_loader(repository: str = "", refresh: bool = False):
    """RepoPulse cinematic repository-scan loading experience."""
    import html as _html
    repo_label = _html.escape(repository or "repository")
    mode_label = "REFRESHING REPOSITORY" if refresh else "INITIALIZING REPOSITORY"
    st.markdown(
        f"""
        <div class="rp-scan-screen" role="status" aria-live="polite">
          <div class="rp-scan-grid"></div>
          <div class="rp-scan-content">
            <div class="rp-scan-brand">REPOPULSE</div>
            <div class="rp-scan-kicker">REPOSITORY INTELLIGENCE</div>
            <div class="rp-pulse-orb">
              <div class="rp-pulse-ring rp-ring-1"></div>
              <div class="rp-pulse-ring rp-ring-2"></div>
              <div class="rp-pulse-ring rp-ring-3"></div>
              <div class="rp-pulse-core">●</div>
            </div>
            <div class="rp-scan-title">{mode_label}</div>
            <div class="rp-scan-repo">{repo_label}</div>
            <div class="rp-scan-progress"><span></span></div>
            <div class="rp-scan-stage"><i></i><span id="rp-stage-text">Connecting to GitHub</span></div>
            <div class="rp-scan-steps">
              <div><b>01</b> CONNECTING TO GITHUB</div>
              <div><b>02</b> FETCHING REPOSITORY SIGNALS</div>
              <div><b>03</b> ANALYZING ACTIVITY</div>
              <div><b>04</b> MAPPING ENGINEERING HEALTH</div>
              <div><b>05</b> IDENTIFYING RISKS</div>
              <div><b>06</b> GENERATING INTELLIGENCE</div>
            </div>
            <div class="rp-scan-terminal">
              <div>&gt; repopulse.init()</div>
              <div>&gt; establishing telemetry channel...</div>
              <div>&gt; preparing repository intelligence...</div>
            </div>
          </div>
        </div>
        <script>
        (() => {{
          const stages = [
            "Connecting to GitHub",
            "Fetching repository signals",
            "Analyzing activity",
            "Mapping engineering health",
            "Identifying risks",
            "Generating intelligence"
          ];
          let i = 0, el = document.getElementById("rp-stage-text");
          if (!el) return;
          setInterval(() => {{
            i = (i + 1) % stages.length;
            el.style.opacity = "0";
            setTimeout(() => {{
              el.textContent = stages[i];
              el.style.opacity = "1";
            }}, 160);
          }}, 900);
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )

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
        "pending_scan": None,
        "scan_active": False,
        "scan_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_state()
init_interaction_state()

# A repository scan is a dedicated application state.  Do this before the
# sidebar and normal page navigation are rendered so the user sees a true
# full-screen scan experience rather than a loader embedded in Repository.
if st.session_state.get("scan_active"):
    from pages.repository import run_active_scan
    st.markdown(scan_styles(), unsafe_allow_html=True)
    st.markdown(
        """<style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        [data-testid="stAppViewContainer"] { margin: 0 !important; }
        [data-testid="stMainBlockContainer"] { max-width: none !important; padding: 0 !important; }
        </style>""",
        unsafe_allow_html=True,
    )
    run_active_scan()
    st.stop()

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
    with open("assets/final-logo.png", "rb") as _logo_file:
        _logo_b64 = base64.b64encode(_logo_file.read()).decode()

    st.markdown(
        f'<div class="sidebar-brand"><img class="sidebar-logo" src="data:image/png;base64,{_logo_b64}" alt="RepoPulse logo"><span>RepoPulse</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-subtitle">Repository intelligence</div>', unsafe_allow_html=True)

    workspace_unlocked = bool(st.session_state.get("current_repo") and st.session_state.get("repo_analysis"))
    st.session_state.setdefault("nav_page", "Repository")

    def _set_nav(widget_key: str):
        value = st.session_state.get(widget_key, "")
        if value:
            page = value.split("  ", 1)[1] if "  " in value else value
            st.session_state.nav_page = page

    command_options = ["📊  Dashboard", "📁  Repository", "👥  Contributors", "🧠  Code Insights"]
    intelligence_options = ["🚨  Risk Center", "🤖  Assessment", "⚖️  Compare", "🔮  Predictive Risk"]

    if not workspace_unlocked:
        st.session_state.nav_page = "Repository"
        st.markdown('<div class="sidebar-section">Get started</div>', unsafe_allow_html=True)
        st.radio("Get started", ["📁  Repository"], index=0, label_visibility="collapsed", key="locked_repository_nav")
        st.markdown(
            '<div class="sidebar-lock-card"><div class="sidebar-lock-title">🔒 Workspace locked</div>'
            '<div class="sidebar-lock-copy">Analyze a GitHub repository first to unlock the intelligence workspace.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-section">Locked features</div>', unsafe_allow_html=True)
        for label in ["📊  Dashboard", "👥  Contributors", "🧠  Code Insights", "🚨  Risk Center", "🤖  Assessment", "⚖️  Compare", "🔮  Predictive Risk"]:
            icon, text = label.split("  ", 1)
            st.markdown(
                f'<div class="sidebar-locked-item"><span class="sidebar-locked-icon">{icon}</span><span>{html.escape(text)}</span><span style="margin-left:auto;opacity:.65">⌕</span></div>',
                unsafe_allow_html=True,
            )
        selected_page = "Repository"
    else:
        if st.session_state.get("nav_page") not in pages:
            st.session_state.nav_page = "Dashboard"
        current_page = st.session_state.nav_page
        st.markdown('<div class="sidebar-section">Command center</div>', unsafe_allow_html=True)
        command_index = next((i for i, item in enumerate(command_options) if item.endswith(current_page)), 0)
        st.radio("Command center", command_options, index=command_index, label_visibility="collapsed", key="command_nav", on_change=_set_nav, args=("command_nav",))
        current_page = st.session_state.nav_page
        st.markdown('<div class="sidebar-section">Intelligence</div>', unsafe_allow_html=True)
        intel_index = next((i for i, item in enumerate(intelligence_options) if item.endswith(current_page)), 0)
        st.radio("Intelligence", intelligence_options, index=intel_index, label_visibility="collapsed", key="intel_nav", on_change=_set_nav, args=("intel_nav",))
        selected_page = st.session_state.nav_page

    st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)
    if workspace_unlocked:
        repo_label = html.escape(st.session_state.current_repo)
        scans = st.session_state.repo_session_count
        last_scan = st.session_state.get("last_refresh")
        last_scan_html = f'<div class="sidebar-meta"><span>Last scan</span><span class="sidebar-count">{html.escape(str(last_scan))}</span></div>' if last_scan else ""
        st.markdown(
            f'<div class="sidebar-status"><div class="sidebar-status-label">Active repository</div><div class="sidebar-status-name">{repo_label}</div><div class="sidebar-live"><span class="live-dot"></span>Telemetry connected</div><div class="sidebar-meta"><span>Session scans</span><span class="sidebar-count">{scans}/10</span></div>{last_scan_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="sidebar-status"><div class="sidebar-status-label">Setup required</div><div class="sidebar-status-name">No repository connected</div><div class="sidebar-meta"><span>Workspace</span><span class="sidebar-count">LOCKED</span></div></div>',
            unsafe_allow_html=True,
        )


current_repo = st.session_state.get("current_repo")
workspace_unlocked = bool(current_repo and st.session_state.get("repo_analysis"))

if not workspace_unlocked:
    st.markdown(
        """
        <div class="onboarding-shell">
          <div class="onboarding-kicker">RepoPulse workspace</div>
          <div class="onboarding-title">Connect a repository to unlock RepoPulse.</div>
          <div class="onboarding-copy">Start by providing a public GitHub repository URL or an <strong>owner/repository</strong> name. Once the repository is successfully analyzed, the dashboard, contributor intelligence, code insights, risk analysis, assessment, comparison and predictive features become available.</div>
          <div class="onboarding-steps">
            <div class="onboarding-step"><div class="onboarding-step-num">01</div><div class="onboarding-step-title">Connect</div><div class="onboarding-step-copy">Enter the GitHub repository you want RepoPulse to understand.</div></div>
            <div class="onboarding-step"><div class="onboarding-step-num">02</div><div class="onboarding-step-title">Analyze</div><div class="onboarding-step-copy">RepoPulse gathers repository, activity and engineering signals.</div></div>
            <div class="onboarding-step"><div class="onboarding-step-num">03</div><div class="onboarding-step-title">Explore</div><div class="onboarding-step-copy">Your intelligence workspace unlocks after a successful scan.</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_focus_bar()
    pages["Repository"]()
else:
    hero_title = f"{html.escape(str(current_repo))} intelligence"
    hero_subtitle = "Live repository telemetry is loaded. Re-scan to update metrics, compare against history, and surface what changed."
    st.markdown(
        f"""
        <div class="global-hero"><div class="hero-kicker">RepoPulse workspace</div><div class="hero-title">{hero_title}</div><div class="hero-subtitle">{hero_subtitle}</div><div class="hero-meta"><span class="hero-meta-pill">Live analytics</span><span class="hero-meta-pill">Historical snapshots</span><span class="hero-meta-pill">Explainable intelligence</span></div></div>
        """,
        unsafe_allow_html=True,
    )
    render_focus_bar()
    pages[selected_page]()

