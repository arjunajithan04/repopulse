from __future__ import annotations

import pandas as pd
import streamlit as st


def code_insights_page():
    st.subheader("Code insights", divider="orange")
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate code quality insights.")
        return

    metrics = analysis.metrics or {}
    code = metrics.get("code_analysis")
    languages = metrics.get("language_breakdown", {}) or {}

    if languages:
        total_bytes = sum(languages.values()) or 1
        lang_rows = [{"Language": lang, "Bytes": size, "Share": round(size / total_bytes * 100, 1)} for lang, size in sorted(languages.items(), key=lambda x: x[1], reverse=True)]
        st.markdown("### Language profile")
        st.bar_chart(pd.DataFrame(lang_rows).head(10), x="Language", y="Share")

    st.markdown("### Repository quality signals")
    dimensions = metrics.get("health_dimensions", {})
    if dimensions:
        rows = [{"Dimension": key.replace("_", " ").title(), "Score": value} for key, value in dimensions.items()]
        st.bar_chart(pd.DataFrame(rows), x="Dimension", y="Score")
    else:
        st.info("Health dimensions are not available for this analysis.")

    if code:
        st.markdown("### Static code scan")
        a, b, c, d = st.columns(4)
        a.metric("Files", code.get("files_analyzed", 0))
        b.metric("Lines", f"{code.get('total_lines', 0):,}")
        c.metric("Functions", code.get("functions", 0))
        d.metric("Classes", code.get("classes", 0))
        st.caption(f"Average complexity: {code.get('avg_complexity', 0)} · Scan status: {code.get('status', 'Unknown')}")
        files = code.get("files", [])
        if files:
            st.markdown("### Largest / highest-complexity files")
            table = pd.DataFrame(files).head(15)
            st.dataframe(table, use_container_width=True, hide_index=True)
    else:
        st.markdown("### Deep code analysis")
        st.info("Run **Deep code scan** from the Repository page to calculate file count, LOC, Python complexity, functions, classes, and largest files.")

    st.markdown("### Recommendations")
    recommendations = []
    health = float(metrics.get("repository_health_score", 0) or 0)
    if health < 70:
        recommendations.append("Review the weakest health dimensions and prioritize maintenance work.")
    if metrics.get("open_issue_count", 0) > 20:
        recommendations.append("Triage the open-issue backlog and identify stale or duplicate issues.")
    if metrics.get("open_pull_request_count", 0) > 15:
        recommendations.append("Review the pull-request backlog and prioritize stale PRs.")
    if code and code.get("avg_complexity", 0) > 8:
        recommendations.append("Inspect the highest-complexity files and consider decomposing large functions.")
    if not recommendations:
        recommendations.append("No major quality action is indicated by the currently available signals.")
    for item in dict.fromkeys(recommendations):
        st.markdown(f"- {item}")

    st.caption("RepoPulse only displays static-analysis metrics when it actually scanned repository files. It does not fabricate test coverage, duplication, vulnerability, or language-level complexity metrics that were not measured.")
