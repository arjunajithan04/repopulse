from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.intelligence import assessment, detect_risks, trend_summary
from components.cards import metric_card, status_badge
from components.ui import page_header, section_header, insight_card, empty_state
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


def _health_status(score: float):
    if score >= 80:
        return "HEALTHY", "good"
    if score >= 60:
        return "MODERATE", "warning"
    return "AT RISK", "danger"


def _history_frame(repo_name: str) -> pd.DataFrame:
    snapshots = list(reversed(get_snapshots(repo_name, limit=30)))
    return pd.DataFrame(snapshots) if snapshots else pd.DataFrame()


def _current_snapshot(analysis) -> dict:
    metrics = analysis.metrics or {}
    return {
        "stars": analysis.repository.stars,
        "forks": analysis.repository.forks,
        "issues": metrics.get("open_issue_count", 0),
        "pull_requests": metrics.get("open_pull_request_count", 0),
        "contributors": metrics.get("total_contributors", 0),
        "commits": metrics.get("recent_commit_count", 0),
        "health": metrics.get("repository_health_score", 0),
    }


def _render_what_changed(analysis, previous):
    st.markdown("### What changed")
    if not previous:
        st.info("This is the first comparison point. Re-scan the repository later to unlock change intelligence.")
        return
    trends = trend_summary(_current_snapshot(analysis), previous)
    changed = [t for t in trends if t["change"] != 0]
    if not changed:
        st.success("No measured metrics changed since the previous scan.")
        return
    for t in changed:
        symbol = "↑" if t["direction"] == "up" else "↓"
        cls = "positive" if t["interpretation"] == "improved" else "negative"
        pct = f"{t['pct']:+.1f}%" if t["pct"] is not None else "new"
        st.markdown(f'<div class="change-row"><span class="change-symbol {cls}">{symbol}</span><strong>{t["label"]}</strong><span>{t["previous"]:,.1f} → {t["current"]:,.1f} · {pct}</span></div>', unsafe_allow_html=True)


def _render_history(repo_name: str):
    df = _history_frame(repo_name)
    if df.empty:
        st.info("No persistent history yet. Analyze this repository again later to build trends.")
        return

    st.markdown("### Live history")
    st.caption("Every analysis creates a timestamped snapshot. Re-scan the repository to extend these trends.")
    chart_df = df.copy()
    chart_df["captured_at"] = pd.to_datetime(chart_df["captured_at"])
    chart_df = chart_df.set_index("captured_at")
    tab1, tab2, tab3 = st.tabs(["Health", "Development", "Community"])
    with tab1:
        st.line_chart(chart_df[["health_score"]].rename(columns={"health_score": "Health"}), use_container_width=True)
    with tab2:
        dev = chart_df[["recent_commits", "open_pull_requests", "open_issues"]].rename(columns={"recent_commits": "Recent commits", "open_pull_requests": "Open PRs", "open_issues": "Open issues"})
        st.line_chart(dev, use_container_width=True)
    with tab3:
        community = chart_df[["stars", "forks", "contributors"]].copy()
        for col in community.columns:
            base = community[col].iloc[0]
            community[col] = (community[col] / base * 100) if base else 0
        community.columns = ["Stars index", "Forks index", "Contributors index"]
        st.line_chart(community, use_container_width=True)
        st.caption("Community trends are indexed to the first stored snapshot (100 = starting level).")


def dashboard_page():
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        page_header("Workspace", "Repository intelligence", "Connect a GitHub repository to turn raw activity into a clear health and risk picture.")
        empty_state("Your command center is waiting", "Analyze a repository from the Repository page. Once data is loaded, this view becomes your live health, trend and risk workspace.", "◈")
        return

    repo = analysis.repository
    metrics = analysis.metrics or {}
    previous = st.session_state.get("previous_snapshot") or {}
    score = float(metrics.get("repository_health_score", 0) or 0)
    status, tone = _health_status(score)
    result = assessment(metrics, previous)

    page_header("Live repository", "Repository command center", f"{repo.full_name} · scanned from GitHub telemetry")
    top1, top2 = st.columns([4, 1])
    with top1:
        st.markdown(f'<div class="hero-card"><div class="hero-title">{repo.full_name}</div><div class="hero-subtitle">{repo.description or "No repository description provided."}</div></div>', unsafe_allow_html=True)
    with top2:
        status_badge(status, tone)
        st.metric("Health", f"{score:.1f}/100", delta=(f"{score - float(previous.get('health', score)):+.1f} pts" if previous else None))

    cards = [
        ("Stars", _fmt(repo.stars), _delta(repo.stars, previous.get("stars")), "GitHub popularity"),
        ("Forks", _fmt(repo.forks), _delta(repo.forks, previous.get("forks")), "Repository copies"),
        ("Open issues", _fmt(metrics.get("open_issue_count", 0)), _delta(metrics.get("open_issue_count", 0), previous.get("issues"), True), "Lower backlog is healthier"),
        ("Open PRs", _fmt(metrics.get("open_pull_request_count", 0)), _delta(metrics.get("open_pull_request_count", 0), previous.get("pull_requests"), True), "Lower backlog is healthier"),
    ]
    cols = st.columns(4)
    for col, (title, value, delta, help_text) in zip(cols, cards):
        with col:
            metric_card(title, value, delta[0] if delta else None, help_text, delta[1] if delta else "neutral")

    left, right = st.columns([1.05, 1])
    with left:
        section_header("Health breakdown", "Six dimensions combine into the overall repository score.")
        dimensions = metrics.get("health_dimensions", {}) or {}
        if dimensions:
            health_df = pd.DataFrame({"Dimension": list(dimensions.keys()), "Score": list(dimensions.values())}).set_index("Dimension")
            st.bar_chart(health_df, use_container_width=True)
    with right:
        section_header("Risk radar", "Signals that deserve attention before they become problems.")
        risks = detect_risks(metrics)
        if risks:
            for risk in risks[:5]:
                st.markdown(f'<div class="risk-row">⚠️ <strong>{risk.severity}</strong> · {risk.title}</div>', unsafe_allow_html=True)
            if len(risks) > 5:
                st.caption(f"{len(risks) - 5} additional signals available in Risk Center.")
        else:
            st.success("No major risk signals detected from the current metrics.")

    _render_what_changed(analysis, previous)

    activity = metrics.get("activity_intelligence", {}) or {}
    engineering = metrics.get("engineering_intelligence", {}) or {}
    section_header("Engineering & activity pulse", "Recent development behaviour and engineering hygiene.")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Activity", activity.get("status", "Unknown"), f"{activity.get('commit_trend_pct', 0):+.1f}% commit trend")
    p2.metric("Engineering", f"{engineering.get('engineering_score', 0):.1f}/100")
    p3.metric("Testing", f"{engineering.get('testing_score', 0):.1f}/100")
    p4.metric("Documentation", f"{engineering.get('documentation_score', 0):.1f}/100")
    st.caption(f"Last commit: {activity.get('last_commit_days_ago', 0)} days ago · {engineering.get('dependencies_observed', 0)} observed dependencies · {engineering.get('test_files', 0)} test files")

    c1, c2 = st.columns(2)
    with c1:
        section_header("Assessment", "A plain-language interpretation of the latest scan.")
        st.write(result["intro"])
        insight_card("Primary improvement area", f"{result['weakest_dimension']}. {result["priorities"][0]}", "warning", "Priority")
    with c2:
        section_header("Repository pulse", "The core numbers behind this scan.")
        st.metric("Contributors", f"{metrics.get('total_contributors', 0):,}")
        st.metric("Bus factor", f"{metrics.get('bus_factor', 0):,}")
        st.metric("Recent commits", f"{metrics.get('recent_commit_count', 0):,}")

    _render_history(repo.full_name)
