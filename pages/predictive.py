from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.predictive import forecast_summary
from components.ui import page_header, empty_state


def predictive_page():
    repo = st.session_state.get("current_repo")
    if not repo:
        page_header("Intelligence", "Predictive Risk", "Estimate near-term maintenance risk from historical repository behaviour.")
        empty_state("No repository loaded", "Analyze a repository and build a few historical snapshots before using predictive intelligence.", "◌")
        return
    try:
        from data.history import get_snapshots
        snapshots = get_snapshots(repo, limit=30)
    except Exception:
        snapshots = []
    page_header("Intelligence", "Predictive Risk", "A directional forecast built from the repository's historical RepoPulse snapshots.")
    result = forecast_summary(snapshots)
    pred = result["prediction"]
    tone = "danger" if pred.label == "High" else "warning" if pred.label == "Moderate" else "good"

    left, right = st.columns([1, 1.6])
    with left:
        st.markdown(f'<div class="assessment-score"><div class="score-ring">{pred.probability:.0f}</div><div class="assessment-status {tone}">{pred.label} risk</div><div class="assessment-caption">Estimated probability / directional score</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### Near-term repository outlook")
        st.write(f"**Method:** {pred.method} · **Confidence:** {pred.confidence} · **Horizon:** {pred.horizon}")
        st.write(f"RepoPulse currently estimates **{pred.label.lower()} maintenance risk** for **{repo}**.")
        st.caption(f"Historical snapshots available: {result['snapshots']}")

    c1, c2 = st.columns(2)
    c1.metric("Health trend", f"{result['health_trend']:+.1f} pts / snapshot")
    c2.metric("Activity trend", f"{result['activity_trend']:+.1f} commits / snapshot")

    st.markdown("### Evidence")
    if pred.evidence:
        for item in pred.evidence:
            st.markdown(f"- {item}")
    else:
        st.info("No strong directional signal has emerged yet.")

    st.markdown("### Historical health")
    if snapshots:
        rows = [{"Captured": x.get("captured_at", ""), "Health": x.get("health_score", 0), "Commits": x.get("recent_commits", 0), "Contributors": x.get("contributors", 0)} for x in reversed(snapshots)]
        st.line_chart(pd.DataFrame(rows).set_index("Captured"), use_container_width=True)

    st.markdown("### Model limitations")
    for item in pred.limitations:
        st.caption(f"• {item}")
