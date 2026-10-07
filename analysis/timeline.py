from __future__ import annotations

from datetime import datetime
from typing import Any


def _num(snapshot: dict[str, Any], key: str) -> float:
    try:
        return float(snapshot.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _pct(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / abs(previous) * 100


def _date(snapshot: dict[str, Any]) -> str:
    value = snapshot.get("captured_at") or snapshot.get("timestamp") or ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _event(date: str, kind: str, title: str, detail: str, score: float, severity: str = "info") -> dict[str, Any]:
    return {
        "date": date,
        "kind": kind,
        "title": title,
        "detail": detail,
        "health": round(score, 1),
        "severity": severity,
    }


def build_milestones(snapshots: list[dict[str, Any]], max_events: int = 12) -> list[dict[str, Any]]:
    """Turn sequential repository snapshots into explainable historical milestones.

    This is deliberately conservative: milestones are only emitted when a measurable
    change crosses a meaningful threshold. It does not infer events that are absent
    from stored telemetry.
    """
    if len(snapshots) < 2:
        return []

    ordered = sorted(snapshots, key=lambda item: _date(item))
    events: list[dict[str, Any]] = []

    for previous, current in zip(ordered, ordered[1:]):
        date = _date(current)
        health = _num(current, "health_score")
        prev_health = _num(previous, "health_score")
        health_delta = health - prev_health

        commits = _num(current, "recent_commits")
        prev_commits = _num(previous, "recent_commits")
        commit_change = _pct(commits, prev_commits)

        contributors = _num(current, "contributors")
        prev_contributors = _num(previous, "contributors")
        contributor_delta = contributors - prev_contributors

        issues = _num(current, "open_issues")
        prev_issues = _num(previous, "open_issues")
        issue_change = _pct(issues, prev_issues)

        prs = _num(current, "open_pull_requests")
        prev_prs = _num(previous, "open_pull_requests")
        pr_change = _pct(prs, prev_prs)

        # Health movements are the highest-value historical events.
        if abs(health_delta) >= 8:
            if health_delta > 0:
                events.append(_event(date, "health", "Health recovery", f"Repository health recovered by {health_delta:.1f} points.", health, "positive"))
            else:
                events.append(_event(date, "health", "Health decline", f"Repository health declined by {abs(health_delta):.1f} points.", health, "negative"))

        if commit_change is not None and abs(commit_change) >= 40:
            if commit_change > 0:
                events.append(_event(date, "activity", "Activity surge", f"Recent commit activity increased {commit_change:.0f}% versus the previous scan.", health, "positive"))
            else:
                events.append(_event(date, "activity", "Activity slowdown", f"Recent commit activity decreased {abs(commit_change):.0f}% versus the previous scan.", health, "negative"))

        if contributor_delta >= 2:
            events.append(_event(date, "community", "Contributor expansion", f"{int(contributor_delta)} additional contributors were visible in the latest scan.", health, "positive"))
        elif contributor_delta <= -2:
            events.append(_event(date, "community", "Contributor contraction", f"Visible contributors decreased by {abs(int(contributor_delta))}.", health, "negative"))

        if issue_change is not None and issue_change >= 50:
            events.append(_event(date, "issues", "Issue pressure spike", f"Open issues increased {issue_change:.0f}% versus the previous scan.", health, "negative"))
        elif issue_change is not None and issue_change <= -40:
            events.append(_event(date, "issues", "Issue backlog relief", f"Open issues decreased {abs(issue_change):.0f}%.", health, "positive"))

        if pr_change is not None and pr_change >= 60:
            events.append(_event(date, "review", "Review pressure increased", f"Open pull requests increased {pr_change:.0f}%.", health, "negative"))
        elif pr_change is not None and pr_change <= -50:
            events.append(_event(date, "review", "PR backlog relief", f"Open pull requests decreased {abs(pr_change):.0f}%.", health, "positive"))

        # Absolute score thresholds create useful first-entry milestones without
        # pretending to know why the threshold was crossed.
        if prev_health < 80 <= health:
            events.append(_event(date, "threshold", "Healthy territory reached", "Health crossed the 80/100 healthy threshold.", health, "positive"))
        elif prev_health >= 60 > health:
            events.append(_event(date, "threshold", "At-risk territory reached", "Health crossed below the 60/100 attention threshold.", health, "negative"))

    # Keep the most recent event for duplicate titles on the same date, then rank
    # by severity and recency. This keeps the UI useful even with noisy histories.
    severity_rank = {"negative": 3, "positive": 2, "info": 1}
    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for item in events:
        key = (item["date"], item["title"])
        deduped[key] = item

    events = list(deduped.values())
    events.sort(key=lambda item: (_date(item), severity_rank.get(item["severity"], 0)), reverse=True)
    return events[:max_events]


def timeline_summary(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a compact narrative summary for the repository's recent evolution."""
    if not snapshots:
        return {"status": "insufficient", "events": [], "headline": "No historical telemetry yet."}
    events = build_milestones(snapshots)
    if len(snapshots) < 2:
        return {"status": "insufficient", "events": events, "headline": "Run another scan to establish the first comparison point."}

    ordered = sorted(snapshots, key=lambda item: _date(item))
    first, latest = ordered[0], ordered[-1]
    health_delta = _num(latest, "health_score") - _num(first, "health_score")
    activity_delta = _num(latest, "recent_commits") - _num(first, "recent_commits")

    if health_delta >= 5:
        headline = f"Repository health improved {health_delta:.1f} points across the stored history."
    elif health_delta <= -5:
        headline = f"Repository health declined {abs(health_delta):.1f} points across the stored history."
    elif activity_delta > 0:
        headline = "Health is broadly stable while development activity has strengthened."
    elif activity_delta < 0:
        headline = "Health is broadly stable while development activity has softened."
    else:
        headline = "Repository health and development activity have remained broadly stable."

    return {
        "status": "ready",
        "events": events,
        "headline": headline,
        "health_delta": round(health_delta, 1),
        "activity_delta": round(activity_delta, 1),
        "snapshot_count": len(snapshots),
    }
