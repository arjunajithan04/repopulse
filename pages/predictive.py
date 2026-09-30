from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.predictive import forecast_summary
from components.ui import page_header, empty_state
from components.cinematic import render_health_orb, render_spotlight
from components.charts import render_health_trajectory


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

    left, right = st.columns([.9, 1.6])
    with left:
        render_health_orb(pred.probability, f"{pred.label} risk", None)
    with right:
        render_spotlight(
            f"{pred.label} maintenance signal",
            f"RepoPulse currently estimates {pred.label.lower()} maintenance risk for {repo}.",
            f"Method: {pred.method} · Confidence: {pred.confidence} · Horizon: {pred.horizon} · {result['snapshots']} snapshots",
            tone,
            "Directional outlook",
        )

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
        rows = [{"captured_at": x.get("captured_at", ""), "health_score": x.get("health_score", 0)} for x in reversed(snapshots)]
        render_health_trajectory(pd.DataFrame(rows), height=320)

    st.markdown("### Model limitations")
    for item in pred.limitations:
        st.caption(f"• {item}")
