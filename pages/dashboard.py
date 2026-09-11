from __future__ import annotations

import pandas as pd
import streamlit as st

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
    return f"{sign}{change:.1f}% vs previous snapshot", "good" if good else "bad"


def _risk(metrics):
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    bus_factor = int(metrics.get("bus_factor", 0) or 0)
    health = float(metrics.get("repository_health_score", 0) or 0)
    reasons = []
    if issues > 50:
        reasons.append(f"High open-issue pressure ({issues})")
    elif issues > 20:
        reasons.append(f"Elevated open-issue pressure ({issues})")
    if prs > 25:
        reasons.append(f"Large PR backlog ({prs})")
    if bus_factor <= 1:
        reasons.append("High contributor concentration")
    elif bus_factor <= 3:
        reasons.append("Moderate contributor concentration")
    if health < 60:
        reasons.append("Overall health score is below 60")
    if len(reasons) >= 3 or health < 50:
        return "HIGH", reasons
    if reasons:
        return "MEDIUM", reasons
    return "LOW", ["No major risk signals detected from the available metrics."]


def dashboard_page():
    st.subheader("Executive overview", divider="violet")
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate the executive overview.")
        return

    repo = analysis.repository
    metrics = analysis.metrics or {}
    current_repo = repo.full_name or repo.name
    history = get_snapshots(current_repo, limit=30)
    previous = history[1] if len(history) > 1 else None

    st.markdown(f"**{current_repo}** · repository pulse")
    c1, c2, c3, c4 = st.columns(4)
    values = [(repo.stars or 0, previous.get("stars") if previous else None, False), (repo.forks or 0, previous.get("forks") if previous else None, False), (metrics.get("open_issue_count", 0), previous.get("open_issues") if previous else None, True), (metrics.get("repository_health_score", 0), previous.get("health_score") if previous else None, False)]
    labels = ["Stars", "Forks", "Open issues", "Health"]
    for col, label, (current, old, inverse) in zip((c1, c2, c3, c4), labels, values):
        delta = _delta(current, old, inverse)
        with col:
            col.metric(label, f"{_fmt(current) if label != 'Health' else current} {'/100' if label == 'Health' else ''}", delta[0] if delta else None)

    st.markdown("### Repository health")
    dimensions = metrics.get("health_dimensions", {})
    if dimensions:
        rows = [{"Dimension": key.replace("_", " ").title(), "Score": value} for key, value in dimensions.items()]
        st.bar_chart(pd.DataFrame(rows), x="Dimension", y="Score")
    else:
        st.info("Health dimensions are unavailable for this analysis.")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Historical trend")
        if len(history) >= 2:
            trend = pd.DataFrame(list(reversed(history)))
            trend["Captured"] = pd.to_datetime(trend["captured_at"])
            trend = trend.set_index("Captured")[["stars", "forks", "open_issues", "open_pull_requests", "health_score"]]
            st.line_chart(trend)
        else:
            st.info("Run this repository analysis again later to populate a persistent trend line.")
    with right:
        st.markdown("### Repository risk")
        level, reasons = _risk(metrics)
        if level == "HIGH":
            st.error(f"**{level} risk**")
        elif level == "MEDIUM":
            st.warning(f"**{level} risk**")
        else:
            st.success(f"**{level} risk**")
        for reason in reasons:
            st.markdown(f"- {reason}")

    st.markdown("### What changed?")
    if previous:
        changes = []
        fields = [("Stars", "stars"), ("Forks", "forks"), ("Open issues", "open_issues"), ("Open PRs", "open_pull_requests"), ("Contributors", "contributors"), ("Health", "health_score")]
        current_values = {"stars": repo.stars or 0, "forks": repo.forks or 0, "open_issues": metrics.get("open_issue_count", 0), "open_pull_requests": metrics.get("open_pull_request_count", 0), "contributors": metrics.get("total_contributors", 0), "health_score": metrics.get("repository_health_score", 0)}
        for label, key in fields:
            old, new = previous.get(key, 0), current_values[key]
            if old != new:
                direction = "increased" if new > old else "decreased"
                changes.append(f"- **{label}** {direction} from {old:,} to {new:,}")
        st.markdown("\n".join(changes) if changes else "- No metric changes since the previous persistent snapshot.")
    else:
        st.info("This is the first persistent snapshot for this repository.")

    st.markdown("### Recommended actions")
    actions = []
    if metrics.get("open_issue_count", 0) > 20:
        actions.append("Triage the oldest open issues and identify stale backlog items.")
    if metrics.get("open_pull_request_count", 0) > 15:
        actions.append("Audit the pull-request backlog and prioritize stale PRs.")
    if metrics.get("bus_factor", 0) <= 2:
        actions.append("Reduce contributor concentration through documentation, ownership sharing, and onboarding.")
    if metrics.get("repository_health_score", 0) < 70:
        actions.append("Open Code Insights and address the weakest health dimensions first.")
    if not actions:
        actions.append("Maintain the current development cadence and re-analyze periodically to monitor change.")
    for action in dict.fromkeys(actions):
        st.markdown(f"- {action}")
