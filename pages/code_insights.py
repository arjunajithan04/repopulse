from __future__ import annotations

import pandas as pd
import streamlit as st


def _score_quality(metrics: dict) -> dict:
    health = int(metrics.get("repository_health_score", 0) or 0)
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    commits = int(metrics.get("recent_commit_count", 0) or 0)
    contributors = int(metrics.get("total_contributors", 0) or 0)

    maintenance = max(0, min(100, 100 - issues * 2 - prs))
    activity = min(100, commits * 8 + contributors * 4)
    collaboration = min(100, contributors * 12 + prs * 2)
    return {
        "Overall health": health,
        "Maintenance": maintenance,
        "Activity": activity,
        "Collaboration": collaboration,
    }


def _language_df(language_breakdown: dict) -> pd.DataFrame:
    if not language_breakdown:
        return pd.DataFrame(columns=["Language", "Size", "Share"])
    total = sum(language_breakdown.values()) or 1
    rows = [
        {"Language": key, "Size": value, "Share": value / total * 100}
        for key, value in sorted(language_breakdown.items(), key=lambda item: item[1], reverse=True)
    ]
    return pd.DataFrame(rows)


def _quality_flags(metrics: dict) -> list[tuple[str, str, str]]:
    flags = []
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    contributors = int(metrics.get("total_contributors", 0) or 0)
    commits = int(metrics.get("recent_commit_count", 0) or 0)
    health = int(metrics.get("repository_health_score", 0) or 0)

    if health < 60:
        flags.append(("High", "Repository health", "Overall health is below 60. Review maintenance and activity signals."))
    elif health < 80:
        flags.append(("Medium", "Repository health", "Health is moderate. Use the breakdown below to target improvements."))
    else:
        flags.append(("Low", "Repository health", "Overall health is strong."))

    if issues > 50:
        flags.append(("High", "Issue backlog", f"There are {issues} open issues; backlog pressure may be affecting maintainability."))
    elif issues > 20:
        flags.append(("Medium", "Issue backlog", f"There are {issues} open issues; consider triage and stale-issue cleanup."))
    else:
        flags.append(("Low", "Issue backlog", "Open issue volume is currently manageable."))

    if prs > 25:
        flags.append(("High", "PR backlog", f"There are {prs} open pull requests; stale PRs may need attention."))
    elif prs > 15:
        flags.append(("Medium", "PR backlog", f"There are {prs} open pull requests."))
    else:
        flags.append(("Low", "PR backlog", "Pull-request pressure is relatively low."))

    if contributors <= 2:
        flags.append(("Medium", "Ownership concentration", "A small contributor base can increase maintenance and bus-factor risk."))
    else:
        flags.append(("Low", "Ownership concentration", f"The repository has {contributors} contributors in the available analysis."))

    if commits == 0:
        flags.append(("Medium", "Recent activity", "No recent commits were returned by the current analysis window."))
    else:
        flags.append(("Low", "Recent activity", f"{commits} recent commits were returned by the current analysis."))
    return flags


def code_insights_page():
    st.subheader("Code & quality insights", divider="orange")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate code quality insights.")
        return

    metrics = analysis.metrics or {}
    repo = analysis.repository
    language_breakdown = metrics.get("language_breakdown", {}) or {}

    st.markdown(f"**{repo.full_name or repo.name}** · quality intelligence")

    quality = _score_quality(metrics)
    cols = st.columns(4)
    for col, (label, value) in zip(cols, quality.items()):
        with col:
            st.metric(label, f"{int(value)}/100")

    st.markdown("### Quality score breakdown")
    quality_df = pd.DataFrame({"Dimension": list(quality.keys()), "Score": list(quality.values())})
    st.bar_chart(quality_df, x="Dimension", y="Score")

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("### Language profile")
        lang_df = _language_df(language_breakdown)
        if not lang_df.empty:
            display_df = lang_df.copy()
            display_df["Share"] = display_df["Share"].map(lambda x: f"{x:.1f}%")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.bar_chart(lang_df.set_index("Language")["Size"])
        else:
            st.info("Language data was not returned for this repository.")

    with right:
        st.markdown("### Codebase signals")
        signal_rows = [
            {"Signal": "Primary language", "Value": repo.language or "N/A"},
            {"Signal": "Recent commits", "Value": metrics.get("recent_commit_count", 0)},
            {"Signal": "Contributors", "Value": metrics.get("total_contributors", 0)},
            {"Signal": "Open issues", "Value": metrics.get("open_issue_count", 0)},
            {"Signal": "Open PRs", "Value": metrics.get("open_pull_request_count", 0)},
            {"Signal": "Repository health", "Value": f"{metrics.get('repository_health_score', 0)}/100"},
        ]
        st.dataframe(pd.DataFrame(signal_rows), use_container_width=True, hide_index=True)

    st.markdown("### Quality flags")
    flags = _quality_flags(metrics)
    flag_df = pd.DataFrame(flags, columns=["Severity", "Area", "Interpretation"])
    st.dataframe(flag_df, use_container_width=True, hide_index=True)

    st.markdown("### Problem areas & recommendations")
    recommendations = []
    for severity, area, text in flags:
        if severity in ("High", "Medium"):
            if area == "Issue backlog":
                recommendations.append("Prioritize issue triage: close duplicates, label stale issues, and define owners for high-impact bugs.")
            elif area == "PR backlog":
                recommendations.append("Review stale pull requests and shorten the review-to-merge cycle for active work.")
            elif area == "Ownership concentration":
                recommendations.append("Document critical modules and spread code ownership through reviews and contributor onboarding.")
            elif area == "Recent activity":
                recommendations.append("Verify whether the repository is intentionally dormant; if not, identify blocked or abandoned work.")
            elif area == "Repository health":
                recommendations.append("Use the Dashboard risk section to identify the weakest operational signal before making code-quality changes.")

    if not recommendations:
        recommendations.append("No major quality risks were detected from the metrics currently available. Add static-analysis data later for deeper code-level insights.")
    for recommendation in dict.fromkeys(recommendations):
        st.markdown(f"- {recommendation}")

    st.markdown("### Data coverage")
    st.caption(
        "This page deliberately distinguishes repository-level quality signals from true static code analysis. "
        "Metrics such as cyclomatic complexity, test coverage, duplication, LOC, and dependency vulnerabilities "
        "require repository file scanning or external analysis and are not fabricated when the current analysis model does not provide them."
    )
