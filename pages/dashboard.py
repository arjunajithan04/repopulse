from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import metric_card, status_badge
from data.history import get_snapshots


def _fmt(value: int | float) -> str:
    value = value or 0
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"


def _delta(current, previous, inverse=False):
    if previous is None or previous == 0:
        return None
    change = ((current - previous) / abs(previous)) * 100
    good = change <= 0 if inverse else change >= 0
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%", "good" if good else "bad"


def _risk(metrics):
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    bus_factor = int(metrics.get("bus_factor", 0) or 0)
    health = float(metrics.get("repository_health_score", 0) or 0)
    reasons = []
    if issues > 50:
        reasons.append("High issue pressure")
    elif issues > 20:
        reasons.append("Growing issue backlog")
    if prs > 30:
        reasons.append("Large PR backlog")
    elif prs > 15:
        reasons.append("PR backlog needs attention")
    if bus_factor <= 1 and metrics.get("total_contributors", 0):
        reasons.append("Single-contributor concentration")
    elif bus_factor <= 3 and metrics.get("total_contributors", 0):
        reasons.append("Low bus factor")
    if health < 60:
        reasons.append("Low overall health")
    return reasons


def _health_status(score: float):
    if score >= 80:
        return "HEALTHY", "good"
    if score >= 60:
        return "MODERATE", "warning"
    return "AT RISK", "danger"


def _history_frame(repo_name: str) -> pd.DataFrame:
    snapshots = list(reversed(get_snapshots(repo_name, limit=30)))
    if not snapshots:
        return pd.DataFrame()
    return pd.DataFrame(snapshots)


def _render_history(repo_name: str):
    df = _history_frame(repo_name)
    if df.empty:
        st.info("No persistent history yet. Analyze this repository again later to build trends.")
        return

    st.markdown("### Live history")
    st.caption("Every analysis creates a timestamped snapshot, so trends update automatically as you re-scan the repository.")
    chart_df = df.copy()
    chart_df["captured_at"] = pd.to_datetime(chart_df["captured_at"])
    chart_df = chart_df.set_index("captured_at")

    tab1, tab2, tab3 = st.tabs(["Health", "Development", "Community"])
    with tab1:
        st.line_chart(chart_df[["health_score"]].rename(columns={"health_score": "Health"}), use_container_width=True)
    with tab2:
        dev = chart_df[["recent_commits", "open_pull_requests", "open_issues"]].rename(
            columns={"recent_commits": "Recent commits", "open_pull_requests": "Open PRs", "open_issues": "Open issues"}
        )
        st.line_chart(dev, use_container_width=True)
    with tab3:
        # Normalize each series to its first observed value so unlike scales remain readable.
        community = chart_df[["stars", "forks", "contributors"]].copy()
        for col in community.columns:
            base = community[col].iloc[0]
            community[col] = ((community[col] / base) * 100) if base else 0
        community.columns = ["Stars index", "Forks index", "Contributors index"]
        st.line_chart(community, use_container_width=True)
        st.caption("Community trends are indexed to the first stored snapshot (100 = starting level).")

    st.dataframe(
        df.rename(
            columns={
                "captured_at": "Captured", "stars": "Stars", "forks": "Forks", "open_issues": "Issues",
                "open_pull_requests": "PRs", "contributors": "Contributors", "recent_commits": "Commits", "health_score": "Health",
            }
        )[["Captured", "Stars", "Forks", "Issues", "PRs", "Contributors", "Commits", "Health"]],
        use_container_width=True,
        hide_index=True,
    )


def _render_comparison():
    st.markdown("### Repository comparison")
    snapshots = st.session_state.get("repo_snapshots", {})
    repos = list(snapshots.keys())
    if len(repos) < 2:
        st.info("Analyze at least two repositories in this session to unlock comparison.")
        return

    c1, c2 = st.columns(2)
    with c1:
        repo_a = st.selectbox("Repository A", repos, key="compare_a")
    with c2:
        repo_b = st.selectbox("Repository B", repos, index=min(1, len(repos) - 1), key="compare_b")
    if repo_a == repo_b:
        st.warning("Choose two different repositories.")
        return

    a, b = snapshots[repo_a], snapshots[repo_b]
    rows = [
        ("Stars", a["stars"], b["stars"], False),
        ("Forks", a["forks"], b["forks"], False),
        ("Open issues", a["issues"], b["issues"], True),
        ("Open PRs", a["pull_requests"], b["pull_requests"], True),
        ("Contributors", a["contributors"], b["contributors"], False),
        ("Health", a["health"], b["health"], False),
        ("Recent commits", a["commits"], b["commits"], False),
    ]
    display = []
    for label, va, vb, inverse in rows:
        if va == vb:
            winner = "Tie"
        else:
            winner = repo_a if (va < vb if inverse else va > vb) else repo_b
        display.append({"Metric": label, repo_a: va, repo_b: vb, "Leader": winner})
    st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)


def dashboard_page():
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.subheader("Dashboard", divider="blue")
        st.info("Analyze a GitHub repository to turn this dashboard into a live intelligence view.")
        st.markdown("#### What becomes dynamic")
        st.markdown("- Health score and risk signals from the latest scan\n- Historical trends from every stored analysis\n- Contributor concentration and activity\n- Code-quality signals when a deep scan is enabled")
        return

    repo = analysis.repository
    metrics = analysis.metrics or {}
    previous = st.session_state.get("previous_snapshot") or {}
    score = float(metrics.get("repository_health_score", 0) or 0)
    status, tone = _health_status(score)

    st.subheader("Repository command center", divider="blue")
    top1, top2 = st.columns([4, 1])
    with top1:
        st.markdown(f"### {repo.full_name}")
        st.caption(repo.description or "No repository description provided.")
    with top2:
        status_badge(status, tone)
        st.metric("Health", f"{score:.1f}/100", delta=(f"{score - float(previous.get('health', score)):+.1f}" if previous else None))

    cards = [
        ("Stars", _fmt(repo.stars), _delta(repo.stars, previous.get("stars")), "GitHub popularity"),
        ("Forks", _fmt(repo.forks), _delta(repo.forks, previous.get("forks")), "Repository copies"),
        ("Open issues", _fmt(metrics.get("open_issue_count", 0)), _delta(metrics.get("open_issue_count", 0), previous.get("issues"), True), "Lower backlog is healthier"),
        ("Open PRs", _fmt(metrics.get("open_pull_request_count", 0)), _delta(metrics.get("open_pull_request_count", 0), previous.get("pull_requests"), True), "Lower backlog is healthier"),
    ]
    cols = st.columns(4)
    for col, (title, value, delta, help_text) in zip(cols, cards):
        with col:
            if delta:
                metric_card(title, value, delta[0], help_text, delta[1])
            else:
                metric_card(title, value, None, help_text)

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("### Health breakdown")
        dimensions = metrics.get("health_dimensions", {}) or {}
        if dimensions:
            health_df = pd.DataFrame({"Dimension": list(dimensions.keys()), "Score": list(dimensions.values())}).set_index("Dimension")
            st.bar_chart(health_df, use_container_width=True)
    with right:
        st.markdown("### Risk radar")
        risks = _risk(metrics)
        if risks:
            for risk in risks:
                st.markdown(f'<div class="risk-row">⚠️ <span>{risk}</span></div>', unsafe_allow_html=True)
        else:
            st.success("No major risk signals detected from the current metrics.")
        st.markdown("### Recommended next action")
        weakest = min((metrics.get("health_dimensions") or {}).items(), key=lambda item: item[1], default=("health", score))
        actions = {
            "activity": "Increase development cadence or investigate whether the repository is becoming inactive.",
            "community": "Broaden participation and improve discoverability/documentation for contributors.",
            "maintenance": "Prioritize stale maintenance work, unresolved PRs, and repository upkeep.",
            "issue_health": "Triage the issue backlog and close stale or duplicate issues.",
            "pr_health": "Review open pull requests and reduce review/merge bottlenecks.",
            "contributor_health": "Reduce ownership concentration and strengthen contributor onboarding.",
        }
        st.info(actions.get(weakest[0], "Review the weakest health dimension."))

    _render_history(repo.full_name)
    _render_comparison()
