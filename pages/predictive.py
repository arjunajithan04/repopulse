from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.predictive import forecast_summary
from components.ui import page_header, empty_state, callout, section_header
from components.cinematic import render_health_orb, render_spotlight, render_telemetry_strip
from components.charts import render_health_trajectory, render_history_chart


def _tone(label: str) -> str:
    return {"High": "danger", "Moderate": "warning", "Low": "good"}.get(label, "neutral")


def predictive_page():
    repo = st.session_state.get("current_repo")
    if not repo:
        page_header("Intelligence", "Predictive Risk", "Estimate near-term maintenance risk from historical repository behaviour.")
        empty_state("No repository loaded", "Analyze a repository and build historical snapshots before using predictive intelligence.", "◌")
        return

    try:
        from data.history import get_snapshots
        snapshots = get_snapshots(repo, limit=30)
    except Exception:
        snapshots = []

    page_header(
        "Intelligence",
        "Predictive Risk",
        "Evidence-based near-term risk forecasting from the repository's historical behaviour.",
    )

    result = forecast_summary(snapshots)
    pred = result["prediction"]
    tone = _tone(pred.label)

    if pred.label == "Insufficient data":
        callout("Build the signal first", "RepoPulse needs multiple historical scans before predictive intelligence can establish a meaningful trajectory.", "warning", "◌")
        st.metric("Historical snapshots", result["snapshots"])
        return

    left, right = st.columns([0.85, 1.65])
    with left:
        render_health_orb(pred.probability, f"{pred.label} risk", None)
    with right:
        render_spotlight(
            f"{pred.label} near-term maintenance risk",
            f"RepoPulse estimates a {pred.probability:.0f}% directional risk signal for {repo} over the {pred.horizon.lower()}.",
            f"Method: {pred.method} · Confidence: {pred.confidence} · {result['snapshots']} snapshots",
            tone,
            "Predictive outlook",
        )

    render_telemetry_strip([
        ("Risk probability", f"{pred.probability:.0f}%", tone),
        ("Confidence", pred.confidence, "good" if pred.confidence == "High" else "warning"),
        ("Health trend", f"{result['health_trend']:+.1f}/scan", "good" if result["health_trend"] >= 0 else "danger"),
        ("Activity trend", f"{result['activity_trend']:+.1f}/scan", "good" if result["activity_trend"] >= 0 else "danger"),
    ])

    section_header("What is driving the forecast", "The model separates observed risk factors from the final directional estimate.", "Evidence")
    if pred.factors:
        for idx, factor in enumerate(pred.factors):
            factor_tone = _tone("High" if factor.severity in {"Critical", "High"} else "Moderate" if factor.severity == "Moderate" else "Low")
            with st.expander(f"{factor.severity} · {factor.name} · {factor.score:.0f}/100", expanded=idx == 0):
                st.markdown(f"**Trend:** {factor.trend}")
                st.markdown(f"**Evidence:** {factor.evidence}")
                st.markdown(f"**Recommended action:** {factor.recommendation}")
    else:
        st.info("No dominant predictive risk factor has emerged yet.")

    if pred.recommendation:
        callout("Priority action", pred.recommendation, tone, "→")

    st.markdown("### Risk trajectory")
    timeline = result.get("risk_timeline", [])
    if len(timeline) >= 2:
        risk_df = pd.DataFrame(timeline)
        risk_df["captured_at"] = pd.to_datetime(risk_df["captured_at"], errors="coerce")
        risk_df = risk_df.dropna(subset=["captured_at"])
        if not risk_df.empty:
            render_history_chart(risk_df, "risk_score", "Predicted risk signal", height=300)
    else:
        st.info("A risk trajectory will appear after additional scans.")

    st.markdown("### Health trajectory")
    if snapshots:
        rows = [{"captured_at": x.get("captured_at", ""), "health_score": x.get("health_score", 0)} for x in reversed(snapshots[:12])]
        render_health_trajectory(pd.DataFrame(rows), height=300)

    section_header("Dimension momentum", "Positive values indicate improvement per snapshot; negative values indicate deterioration.", "Trend intelligence")
    cols = st.columns(len(result.get("dimension_trends", {})) or 1)
    for col, (name, slope) in zip(cols, result.get("dimension_trends", {}).items()):
        col.metric(name, f"{slope:+.1f}", delta="improving" if slope > 0.2 else "declining" if slope < -0.2 else "stable")

    section_header("Model transparency", "Why RepoPulse is not presenting the forecast as certainty.", "Method")
    st.caption(f"Primary method: {pred.method}. Confidence: {pred.confidence}. Forecast horizon: {pred.horizon}.")
    for item in pred.limitations:
        st.caption(f"• {item}")
