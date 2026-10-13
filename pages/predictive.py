from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from analysis.predictive import forecast_summary
from components.ui import page_header, empty_state, callout, section_header
from components.cinematic import render_health_orb, render_spotlight, render_telemetry_strip
from components.charts import render_health_trajectory, render_history_chart


def _tone(label: str) -> str:
    return {"High": "danger", "Moderate": "warning", "Low": "good"}.get(label, "neutral")


def _render_forecast_card(label: str, value: str, detail: str, tone: str = "neutral"):
    palette = {
        "danger": ("#fb7185", "rgba(244, 63, 94, .10)", "rgba(251, 113, 133, .30)"),
        "warning": ("#fbbf24", "rgba(245, 158, 11, .10)", "rgba(251, 191, 36, .28)"),
        "good": ("#a78bfa", "rgba(139, 92, 246, .12)", "rgba(167, 139, 250, .30)"),
        "neutral": ("#c4b5fd", "rgba(124, 58, 237, .08)", "rgba(167, 139, 250, .20)"),
    }
    accent, background, border = palette.get(tone, palette["neutral"])
    st.html(
        f"""
        <div style="height:100%;min-height:116px;padding:16px 17px;border-radius:16px;
                    background:{background};border:1px solid {border};">
          <div style="font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;
                      color:#a9a4bc;font-weight:700;margin-bottom:10px;">{html.escape(str(label))}</div>
          <div style="font-size:1.45rem;line-height:1.2;font-weight:750;color:{accent};
                      overflow-wrap:anywhere;margin-bottom:8px;">{html.escape(str(value))}</div>
          <div style="font-size:.82rem;line-height:1.45;color:#c7c2d6;">{html.escape(str(detail))}</div>
        </div>
        """
    )


def _confidence_detail(confidence: str) -> str:
    return {
        "High": "More snapshots and multiple signals support this estimate.",
        "Medium": "Several observations support the direction; keep monitoring for confirmation.",
        "Low": "Early signal only. Treat this as provisional and collect more scans.",
        "Very low": "Very limited history. Avoid making major decisions from this estimate alone.",
        "None": "No historical evidence is available yet.",
    }.get(confidence, "Confidence depends on the available historical evidence.")


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
        _render_forecast_card("Historical snapshots", str(result["snapshots"]), "Persisted scans available to the model", "warning")
        _render_forecast_card("Confidence", pred.confidence, _confidence_detail(pred.confidence), "neutral")
        st.caption("Collect multiple scans over time to establish a useful trend. A single scan is a baseline, not a forecast.")
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

    metric_cols = st.columns(4)
    with metric_cols[0]:
        _render_forecast_card("Risk signal", f"{pred.probability:.0f}%", "Directional model estimate, not a guarantee", tone)
    with metric_cols[1]:
        _render_forecast_card("Confidence", pred.confidence, _confidence_detail(pred.confidence),
                              "good" if pred.confidence == "High" else "warning" if pred.confidence in {"Medium", "Low", "Very low"} else "neutral")
    with metric_cols[2]:
        health_tone = "good" if result["health_trend"] > 0.2 else "danger" if result["health_trend"] < -0.2 else "neutral"
        _render_forecast_card("Health momentum", f"{result['health_trend']:+.1f}/scan",
                              "Improving" if health_tone == "good" else "Declining" if health_tone == "danger" else "Relatively stable",
                              health_tone)
    with metric_cols[3]:
        activity_tone = "good" if result["activity_trend"] > 0.2 else "danger" if result["activity_trend"] < -0.2 else "neutral"
        _render_forecast_card("Commit momentum", f"{result['activity_trend']:+.1f}/scan",
                              "Increasing" if activity_tone == "good" else "Decreasing" if activity_tone == "danger" else "Relatively stable",
                              activity_tone)

    section_header("What is driving the forecast", "The model separates observed risk factors from the final directional estimate.", "Evidence")
    if pred.factors:
        for idx, factor in enumerate(pred.factors):
            factor_tone = _tone("High" if factor.severity in {"Critical", "High"} else "Moderate" if factor.severity == "Moderate" else "Low")
            severity_color = {"danger": "#fb7185", "warning": "#fbbf24", "good": "#a78bfa", "neutral": "#c4b5fd"}.get(factor_tone, "#c4b5fd")
            with st.expander(f"{factor.severity} · {factor.name} · {factor.score:.0f}/100", expanded=idx == 0):
                st.markdown(f"**Trend:** {factor.trend}")
                st.markdown(f"**Evidence:** {factor.evidence}")
                st.markdown(f"**Recommended action:** {factor.recommendation}")
                st.progress(max(0.0, min(1.0, float(factor.score) / 100.0)), text=f"Relative factor score · {factor.score:.0f}/100")
    else:
        st.info("No dominant predictive risk factor has emerged yet. Continue collecting snapshots so the forecast can detect meaningful changes.")

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
    dimension_trends = result.get("dimension_trends", {})
    if dimension_trends:
        cols = st.columns(min(3, len(dimension_trends)))
        for idx, (name, slope) in enumerate(dimension_trends.items()):
            col = cols[idx % len(cols)]
            with col:
                trend_tone = "good" if slope > 0.2 else "danger" if slope < -0.2 else "neutral"
                _render_forecast_card(name, f"{slope:+.2f}/scan",
                                      "Improving" if trend_tone == "good" else "Declining" if trend_tone == "danger" else "Stable",
                                      trend_tone)
    else:
        st.info("Dimension momentum needs at least two valid historical snapshots.")

    section_header("Model transparency", "Why RepoPulse is not presenting the forecast as certainty.", "Method")
    st.caption(f"Primary method: {pred.method}. Confidence: {pred.confidence}. Forecast horizon: {pred.horizon}.")
    for item in pred.limitations:
        st.caption(f"• {item}")
