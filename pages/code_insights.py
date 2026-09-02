from __future__ import annotations

import streamlit as st
import pandas as pd


def code_insights_page():
    st.subheader("Code insights", divider="orange")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate code quality insights.")
        return

    language_breakdown = analysis.metrics.get("language_breakdown", {}) or {}
    files = [
        {"Metric": "Repository", "Value": analysis.repository.full_name or analysis.repository.name},
        {"Metric": "Primary language", "Value": analysis.repository.language or "N/A"},
        {"Metric": "Health score", "Value": f"{analysis.metrics.get('repository_health_score', 0)}/100"},
        {"Metric": "Open issues", "Value": analysis.metrics.get("open_issue_count", 0)},
        {"Metric": "Open PRs", "Value": analysis.metrics.get("open_pull_request_count", 0)},
        {"Metric": "Recent commits", "Value": analysis.metrics.get("recent_commit_count", 0)},
    ]

    language_rows = [{"Language": key, "Size": value} for key, value in language_breakdown.items()]
    if language_rows:
        st.dataframe(pd.DataFrame(language_rows), use_container_width=True)
    else:
        st.dataframe(pd.DataFrame(files), use_container_width=True)

    st.markdown("### Quality signals")
    st.markdown(
        f"- Repository health score: {analysis.metrics.get('repository_health_score', 0)}/100\n"
        f"- Contributor traction: {analysis.metrics.get('total_contributors', 0)} contributors\n"
        f"- Current repo: {analysis.repository.full_name or analysis.repository.name}\n"
        f"- Open issues: {analysis.metrics.get('open_issue_count', 0)}\n"
        f"- Open pull requests: {analysis.metrics.get('open_pull_request_count', 0)}"
    )
