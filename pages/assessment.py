from __future__ import annotations

import streamlit as st

from analysis.intelligence import assessment


def assessment_page():
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.subheader("Repository Assessment", divider="blue")
        st.info("Analyze a repository to generate its automated assessment.")
        return

    repo = analysis.repository
    result = assessment(analysis.metrics or {}, st.session_state.get("previous_snapshot"))
    tone = "good" if result["status"] == "Healthy" else "warning" if result["status"] == "Moderate" else "danger"

    st.subheader("Repository Assessment", divider="blue")
    st.caption(f"Automated, explainable assessment based on RepoPulse metrics for {repo.full_name}.")

    left, right = st.columns([1, 2])
    with left:
        st.markdown(f'<div class="assessment-score"><div class="score-ring">{result["score"]:.0f}</div><div class="assessment-status {tone}">{result["status"]}</div><div class="assessment-caption">Health score / 100</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### Executive summary")
        st.write(result["intro"])
        st.info(f"Weakest measured dimension: **{result['weakest_dimension']}**")

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
            st.markdown(f'<div class="change-row"><span class="change-symbol {tone_text}">{symbol}</span><strong>{trend["label"]}</strong><span>{trend["previous"]:,.1f} → {trend["current"]:,.1f}{pct}</span></div>', unsafe_allow_html=True)

    st.markdown("### Risk summary")
    if result["risks"]:
        for risk in result["risks"][:6]:
            st.markdown(f"- **{risk.severity}: {risk.title}** — {risk.detail}")
    else:
        st.success("No major risks detected.")
