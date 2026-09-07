from __future__ import annotations

import pandas as pd
import streamlit as st


def _fmt(value: int | float) -> str:
    value = value or 0
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,}"


def _delta(current, previous, inverse=False):
    if previous in (None, 0):
        return "—", "neutral"
    change = ((current - previous) / abs(previous)) * 100
    if inverse:
        good = change <= 0
    else:
        good = change >= 0
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}% vs last snapshot", "good" if good else "bad"


def _health_breakdown(metrics):
    health = int(metrics.get("repository_health_score", 0) or 0)
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    contributors = int(metrics.get("total_contributors", 0) or 0)
    commits = int(metrics.get("recent_commit_count", 0) or 0)

    activity = min(100, commits * 8 + contributors * 4)
    community = min(100, contributors * 10 + (25 if metrics.get("top_contributor") else 0))
    maintenance = max(0, min(100, 100 - issues * 2 - prs))
    issue_pressure = max(0, min(100, 100 - issues * 3))
    return {
        "Overall health": health,
        "Activity": activity,
        "Community": community,
        "Maintenance": maintenance,
        "Issue pressure": issue_pressure,
    }


def _risk(metrics):
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    contributors = int(metrics.get("total_contributors", 0) or 0)
    health = int(metrics.get("repository_health_score", 0) or 0)

    reasons = []
    if issues > 50:
        reasons.append(f"High open-issue pressure ({issues})")
    elif issues > 20:
        reasons.append(f"Elevated open-issue pressure ({issues})")
    if prs > 25:
        reasons.append(f"Large PR backlog ({prs})")
    if contributors <= 2:
        reasons.append("Contributor concentration is high")
    if health < 60:
        reasons.append("Overall health score is below 60")

    if len(reasons) >= 3 or health < 50:
        level = "HIGH"
    elif reasons:
        level = "MEDIUM"
    else:
        level = "LOW"
    return level, reasons or ["No major risk signals detected from the available metrics."]


def dashboard_page():
    st.subheader("Executive overview", divider="violet")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate the executive overview.")
        return

    repo = analysis.repository
    metrics = analysis.metrics or {}
    current_repo = repo.full_name or repo.name
    stars = int(repo.stars or 0)
    forks = int(repo.forks or 0)
    issues = int(metrics.get("open_issue_count", 0) or 0)
    contributors = int(metrics.get("total_contributors", 0) or 0)
    health = int(metrics.get("repository_health_score", 0) or 0)

    snapshots = st.session_state.get("repo_snapshots", {})
    current_snapshot = snapshots.get(current_repo)
    previous_snapshot = None
    if snapshots:
        names = list(snapshots.keys())
        if current_repo in names:
            idx = names.index(current_repo)
            if idx > 0:
                previous_snapshot = snapshots[names[idx - 1]]

    st.markdown(f"**{current_repo}** · repository pulse")
    c1, c2, c3, c4 = st.columns(4)
    d1, v1 = _delta(stars, previous_snapshot.get("stars") if previous_snapshot else None)
    d2, v2 = _delta(forks, previous_snapshot.get("forks") if previous_snapshot else None)
    d3, v3 = _delta(issues, previous_snapshot.get("issues") if previous_snapshot else None, inverse=True)
    d4, v4 = _delta(health, previous_snapshot.get("health") if previous_snapshot else None)
    with c1:
        st.metric("Stars", _fmt(stars), d1 if d1 != "—" else None)
    with c2:
        st.metric("Forks", _fmt(forks), d2 if d2 != "—" else None)
    with c3:
        st.metric("Open issues", _fmt(issues), d3 if d3 != "—" else None)
    with c4:
        st.metric("Health", f"{health}/100", d4 if d4 != "—" else None)

    st.markdown("### Repository pulse")
    pulse = _health_breakdown(metrics)
    pulse_df = pd.DataFrame({"Dimension": list(pulse.keys()), "Score": list(pulse.values())})
    st.bar_chart(pulse_df, x="Dimension", y="Score")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### What changed?")
        if previous_snapshot:
            changes = []
            for label, key in [("Stars", "stars"), ("Forks", "forks"), ("Open issues", "issues"), ("Health", "health")]:
                old = previous_snapshot.get(key, 0)
                new = current_snapshot.get(key, 0) if current_snapshot else 0
                if new != old:
                    direction = "increased" if new > old else "decreased"
                    changes.append(f"- **{label}** {direction} from {old:,} to {new:,}")
            st.markdown("\n".join(changes) if changes else "- No changes between the available session snapshots.")
        else:
            st.info("Analyze this repository again in a later session to build persistent historical trends. Current comparisons are session-based.")

    with right:
        level, reasons = _risk(metrics)
        st.markdown("### Repository risk")
        if level == "HIGH":
            st.error(f"**{level} risk**")
        elif level == "MEDIUM":
            st.warning(f"**{level} risk**")
        else:
            st.success(f"**{level} risk**")
        for reason in reasons:
            st.markdown(f"- {reason}")

    st.markdown("### Key signals")
    signals = []
    if health >= 80:
        signals.append(("Healthy", "The repository has a strong overall health score."))
    elif health >= 60:
        signals.append(("Watch", "Health is acceptable but has room for improvement."))
    else:
        signals.append(("Needs attention", "Health is low enough to justify a maintenance review."))
    if contributors >= 10:
        signals.append(("Community", f"{contributors} contributors indicate broad participation."))
    elif contributors <= 2:
        signals.append(("Bus factor", "Only a small contributor base is visible; knowledge concentration may be a risk."))
    if issues > 50:
        signals.append(("Issue pressure", f"{issues} open issues suggest backlog pressure."))
    elif issues < 10:
        signals.append(("Maintenance", "Open issue volume is relatively low."))
    if metrics.get("recent_commit_count", 0) > 10:
        signals.append(("Activity", "Recent commit volume suggests active development."))

    cols = st.columns(min(4, len(signals)))
    for col, (title, text) in zip(cols, signals):
        with col:
            st.markdown(f'<div class="insight-card"><div class="insight-title">{title}</div><div class="insight-text">{text}</div></div>', unsafe_allow_html=True)

    st.markdown("### Recommended actions")
    actions = []
    if issues > 20:
        actions.append("Review and triage the oldest open issues.")
    if metrics.get("open_pull_request_count", 0) > 15:
        actions.append("Audit the pull-request backlog and prioritize stale PRs.")
    if contributors <= 2:
        actions.append("Reduce contributor concentration by documenting ownership and onboarding contributors.")
    if health < 70:
        actions.append("Open Code Insights and address the weakest quality signals first.")
    if not actions:
        actions.append("Maintain the current development cadence and periodically re-analyze the repository.")
    for action in actions:
        st.markdown(f"- {action}")
