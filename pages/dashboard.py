from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import metric_card
from components.charts import render_bar_chart


def _delta(current: float, previous: float | None, inverse: bool = False) -> tuple[str, str]:
    if previous is None:
        return "First snapshot", "neutral"
    if previous == 0:
        return "New", "good" if current > 0 else "neutral"
    change = ((current - previous) / abs(previous)) * 100
    if inverse:
        change = -change
    variant = "good" if change > 0 else "bad" if change < 0 else "neutral"
    return f"{change:+.1f}% since last analysis", variant


def dashboard_page():
    st.subheader("Executive overview", divider="violet")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate the executive overview.")
        return

    repo = analysis.repository
    metrics = analysis.metrics
    repo_name = repo.full_name or repo.name
    snapshots = st.session_state.get("repo_snapshots", {}).get(repo_name, [])
    previous = snapshots[-2] if len(snapshots) >= 2 else None

    health = metrics.get("repository_health_score", 0)
    status = "Healthy" if health >= 80 else "Moderate" if health >= 60 else "At risk"
    st.markdown(f"### {repo_name} · {status}")
    if repo.description:
        st.caption(repo.description)

    cols = st.columns(4)
    values = [
        ("Stars", repo.stars, "stars", False),
        ("Forks", repo.forks, "forks", False),
        ("Open issues", metrics.get("open_issue_count", 0), "issue pressure", True),
        ("Health", health, "repository health", False),
    ]
    for col, (label, value, help_text, inverse) in zip(cols, values):
        with col:
            old = previous.get({"Stars": "stars", "Forks": "forks", "Open issues": "issues", "Health": "health"}[label]) if previous else None
            delta, variant = _delta(value, old, inverse=inverse)
            display = f"{value}/100" if label == "Health" else str(value)
            metric_card(label, display, delta, help_text, variant=variant)

    st.write("")
    chart_data = {
        "Stars": repo.stars,
        "Forks": repo.forks,
        "Issues": metrics.get("open_issue_count", 0),
        "Contributors": metrics.get("total_contributors", 0),
    }
    render_bar_chart(chart_data, title="Repository snapshot")

    st.markdown("### Health breakdown")
    health_rows = pd.DataFrame(
        [
            {"Signal": "Activity", "Score": metrics.get("activity_score", 0)},
            {"Signal": "Maintenance", "Score": metrics.get("maintenance_score", 0)},
            {"Signal": "Issue health", "Score": metrics.get("issue_health_score", 0)},
            {"Signal": "PR health", "Score": metrics.get("pr_health_score", 0)},
            {"Signal": "Community", "Score": metrics.get("community_score", 0)},
            {"Signal": "Contributor health", "Score": metrics.get("contributor_health_score", 0)},
        ]
    )
    st.bar_chart(health_rows, x="Signal", y="Score")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### Repository risk")
        risks = []
        if metrics.get("open_issue_count", 0) > 50:
            risks.append("⚠ Elevated open-issue pressure")
        if metrics.get("open_pull_request_count", 0) > 20:
            risks.append("⚠ Elevated pull-request backlog")
        if metrics.get("contribution_concentration", 0) > 50:
            risks.append("⚠ High contributor concentration")
        if metrics.get("bus_factor", 0) <= 2 and metrics.get("total_contributors", 0) > 0:
            risks.append("⚠ Low bus factor")
        if not risks:
            risks.append("✓ No major risk signals detected from the available data")
        st.markdown("\n".join(f"- {r}" for r in risks))

    with col_right:
        st.markdown("### Recommended actions")
        actions = []
        if metrics.get("open_issue_count", 0) > 50:
            actions.append("Prioritize issue triage and stale issue cleanup.")
        if metrics.get("open_pull_request_count", 0) > 20:
            actions.append("Review the pull-request backlog and stale PRs.")
        if metrics.get("contribution_concentration", 0) > 50:
            actions.append("Spread ownership across more contributors.")
        if metrics.get("recent_commit_count", 0) < 5:
            actions.append("Investigate whether development activity has slowed.")
        if not actions:
            actions.append("Continue monitoring activity, maintenance and contributor distribution.")
        for action in actions:
            st.markdown(f"- {action}")

    if previous:
        st.markdown("### What changed?")
        changes = [
            ("Stars", previous["stars"], repo.stars),
            ("Forks", previous["forks"], repo.forks),
            ("Open issues", previous["issues"], metrics.get("open_issue_count", 0)),
            ("Health", previous["health"], health),
        ]
        st.dataframe(
            [{"Metric": name, "Previous": old, "Current": new, "Change": new - old} for name, old, new in changes],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.caption("Run the same repository again later to unlock snapshot-to-snapshot change tracking.")
