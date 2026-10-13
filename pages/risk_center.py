from __future__ import annotations

import html

import streamlit as st

from components.ui import page_header, empty_state, section_header, callout
from components.cards import metric_card
from components.interaction import set_focus
from analysis.intelligence import detect_risks


_SEVERITY_TONE = {
    "Critical": "danger",
    "High": "danger",
    "Medium": "warning",
    "Low": "good",
}
_SEVERITY_ORDER = ("Critical", "High", "Medium", "Low")


def risk_center_page():
    analysis = st.session_state.get("repo_analysis")
    page_header(
        "Intelligence",
        "Risk Center",
        "Prioritized, explainable signals that deserve attention.",
    )
    if analysis is None:
        empty_state(
            "No repository loaded",
            "Analyze a repository from the Repository page to generate live risk signals.",
            "⚠",
        )
        return

    repo = analysis.repository
    metrics = analysis.metrics or {}
    risks = detect_risks(metrics)
    st.caption(
        f"Explainable risk signals for {repo.full_name}. "
        "Signals are derived from the latest measured repository metrics."
    )

    counts = {level: 0 for level in _SEVERITY_ORDER}
    for risk in risks:
        if risk.severity in counts:
            counts[risk.severity] += 1

    section_header(
        "Risk overview",
        "A severity-first summary of the issues detected in this scan.",
        "At a glance",
    )
    cols = st.columns(4, gap="medium")
    descriptions = {
        "Critical": "Immediate attention",
        "High": "Prioritize next",
        "Medium": "Plan an improvement",
        "Low": "Monitor over time",
    }
    for col, level in zip(cols, _SEVERITY_ORDER):
        with col:
            metric_card(
                level,
                str(counts[level]),
                delta=descriptions[level],
                help_text="Detected risk signals",
                variant="bad" if level in {"Critical", "High"} and counts[level] else "neutral",
                icon={"Critical": "!", "High": "↑", "Medium": "•", "Low": "↓"}[level],
            )

    if not risks:
        callout(
            "No major risk signals detected",
            "The current measured metrics did not produce any risk items. Continue monitoring the repository as new activity is recorded.",
            "good",
            "✓",
        )
        return

    critical_high = counts["Critical"] + counts["High"]
    if critical_high:
        callout(
            f"{critical_high} high-priority signal{'s' if critical_high != 1 else ''} need attention",
            "Start with Critical and High items below; each card includes the measured evidence and a recommended next action.",
            "danger",
            "!",
        )
    else:
        callout(
            "No Critical or High signals",
            "The current scan contains Medium or Low signals. Review the recommendations and address them according to impact.",
            "warning",
            "i",
        )

    section_header(
        "Risk drill-down",
        "Filter by severity, inspect the evidence, and send a risk to your current focus.",
        "Evidence & action",
    )
    severity_filter = st.multiselect(
        "Severity",
        list(_SEVERITY_ORDER),
        default=list(_SEVERITY_ORDER),
        key="phase5_risk_severity",
    )
    filtered = [risk for risk in risks if risk.severity in severity_filter]
    if not filtered:
        empty_state(
            "No risks match these filters",
            "Choose another severity level or reset the filter to see detected risk signals.",
            "⌕",
        )
        return

    for idx, risk in enumerate(filtered):
        tone = _SEVERITY_TONE.get(risk.severity, "neutral")
        safe_severity = html.escape(str(risk.severity))
        safe_title = html.escape(str(risk.title))
        safe_detail = html.escape(str(risk.detail))
        safe_recommendation = html.escape(str(risk.recommendation))
        with st.container(border=False):
            st.html(
                f'<article class="risk-card {tone}">'
                f'<div class="risk-card-top">'
                f'<span class="status-badge {tone}"><span class="status-dot"></span>{safe_severity}</span>'
                f'<strong>{safe_title}</strong>'
                f'</div>'
                f'<div class="risk-detail"><span class="risk-field-label">Evidence</span>{safe_detail}</div>'
                f'<div class="risk-action"><span class="risk-field-label">Recommended action</span>{safe_recommendation}</div>'
                '</article>'
            )
            if st.button(
                "Focus this risk",
                key=f"focus_risk_{idx}_{risk.severity}_{risk.title}",
                help="Add this risk to the current focus context.",
            ):
                set_focus("risk", risk.title, "Risk Center")
                st.rerun()
