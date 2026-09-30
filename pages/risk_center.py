from __future__ import annotations

import streamlit as st

from components.ui import page_header, empty_state
from components.interaction import set_focus
from analysis.intelligence import detect_risks


def risk_center_page():
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        page_header("Intelligence", "Risk Center", "Prioritized, explainable signals that deserve attention.")
        empty_state("No repository loaded", "Analyze a repository from the Repository page to generate live risk signals.", "⚠")
        return

    repo = analysis.repository
    metrics = analysis.metrics or {}
    risks = detect_risks(metrics)
    page_header("Intelligence", "Risk Center", "Prioritized, explainable signals that deserve attention.")
    st.caption(f"Explainable risk signals for {repo.full_name}. Signals are derived from the latest measured repository metrics.")

    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for risk in risks:
        counts[risk.severity] = counts.get(risk.severity, 0) + 1
    cols = st.columns(4)
    for col, level in zip(cols, ["Critical", "High", "Medium", "Low"]):
        col.metric(level, counts[level])

    if not risks:
        st.success("No major risk signals were detected from the current metrics.")
        return

    st.markdown("### Risk drill-down")
    severity_filter = st.multiselect("Severity", ["Critical", "High", "Medium", "Low"], default=["Critical", "High", "Medium", "Low"], key="phase5_risk_severity")
    filtered = [r for r in risks if r.severity in severity_filter]
    if not filtered:
        st.info("No risks match the selected severity filters.")
        return

    for idx, risk in enumerate(filtered):
        tone = {"Critical": "danger", "High": "danger", "Medium": "warning", "Low": "good"}.get(risk.severity, "neutral")
        with st.expander(f"{risk.severity} · {risk.title}", expanded=idx == 0):
            st.html(f'<div class="risk-card {tone}"><div class="risk-card-top"><span class="status-badge {tone}">{risk.severity}</span><strong>{risk.title}</strong></div><div class="risk-detail">{risk.detail}</div><div class="risk-action">Recommended action: {risk.recommendation}</div></div>')
            if st.button("Focus this risk", key=f"focus_risk_{idx}"):
                set_focus("risk", risk.title, "Risk Center")
                st.rerun()
