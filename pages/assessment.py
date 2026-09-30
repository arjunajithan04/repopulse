from __future__ import annotations

import streamlit as st

from components.ui import page_header, empty_state
from components.cinematic import render_health_orb, render_spotlight

from analysis.intelligence import assessment


def assessment_page():
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        page_header("Intelligence", "Repository Assessment", "A plain-language assessment built from measured RepoPulse signals.")
        empty_state("No repository loaded", "Analyze a repository from the Repository page to generate an automated assessment.", "◈")
        return

    repo = analysis.repository
    result = assessment(analysis.metrics or {}, st.session_state.get("previous_snapshot"))
    tone = "good" if result["status"] == "Healthy" else "warning" if result["status"] == "Moderate" else "danger"

    page_header("Intelligence", "Repository Assessment", "A plain-language assessment built from measured RepoPulse signals.")
    st.caption(f"Automated, explainable assessment based on RepoPulse metrics for {repo.full_name}.")

    previous = st.session_state.get("previous_snapshot") or {}
    delta_score = result["score"] - float(previous.get("health", result["score"])) if previous else None
    left, right = st.columns([.9, 1.6])
    with left:
        render_health_orb(result["score"], result["status"], delta_score)
    with right:
        render_spotlight(
            result["status"],
            result["intro"],
            f"Weakest measured dimension: {result['weakest_dimension']}",
            tone,
            "Executive signal",
        )

    report_lines = [
        f"# RepoPulse Assessment — {repo.full_name}",
        "",
        f"**Health score:** {result['score']:.1f}/100 · **Status:** {result['status']}",
        "",
        "## Executive summary",
        result["intro"],
        "",
        f"**Weakest measured dimension:** {result['weakest_dimension']}",
        "",
        "## Strengths",
        *[f"- {item}" for item in result["strengths"]],
        "",
        "## Priority actions",
        *[f"- {item}" for item in result["priorities"]],
        "",
        "## Risk summary",
    ]
    if result["risks"]:
        report_lines.extend(f"- **{risk.severity}: {risk.title}** — {risk.detail}" for risk in result["risks"][:6])
    else:
        report_lines.append("- No major risks detected.")
    report_text = "\n".join(report_lines)
    st.html('<div class="report-toolbar"><div class="report-toolbar-copy"><strong>Executive report</strong>Export this assessment as Markdown for project documentation or review.</div></div>')
    st.download_button(
        "Download assessment report",
        data=report_text,
        file_name=f"repopulse-{repo.full_name.replace('/', '-')}-assessment.md",
        mime="text/markdown",
        use_container_width=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Strengths")
        for item in result["strengths"]:
            st.markdown(f"- ✅ {item}")
    with c2:
        st.markdown("### Priority actions")
        for item in result["priorities"]:
            st.markdown(f"- 🎯 {item}")

    if result["trends"]:
        st.markdown("### What changed since the previous scan")
        for trend in result["trends"]:
            if trend["change"] == 0:
                continue
            pct = f" ({trend['pct']:+.1f}%)" if trend["pct"] is not None else ""
            symbol = "↑" if trend["direction"] == "up" else "↓"
            tone_text = "positive" if trend["interpretation"] == "improved" else "negative"
            st.html(f'<div class="change-row"><span class="change-symbol {tone_text}">{symbol}</span><strong>{trend["label"]}</strong><span>{trend["previous"]:,.1f} → {trend["current"]:,.1f}{pct}</span></div>')

    st.markdown("### Risk summary")
    if result["risks"]:
        for risk in result["risks"][:6]:
            st.markdown(f"- **{risk.severity}: {risk.title}** — {risk.detail}")
    else:
        st.success("No major risks detected.")
