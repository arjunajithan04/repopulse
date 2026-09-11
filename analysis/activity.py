from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List


def _commit_date(commit: Dict[str, Any]) -> datetime | None:
    raw = ((commit.get("commit") or {}).get("author") or {}).get("date")
    if not raw:
        raw = ((commit.get("commit") or {}).get("committer") or {}).get("date")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def analyze_activity(commits: Iterable[Dict[str, Any]], prs: Iterable[Dict[str, Any]] = (), issues: Iterable[Dict[str, Any]] = ()) -> Dict[str, Any]:
    commits = list(commits)
    prs = list(prs)
    issues = list(issues)
    dates = [d for d in (_commit_date(c) for c in commits) if d]
    if dates:
        dates.sort()
        now = datetime.now(timezone.utc)
        days_span = max(1, (now - dates[0].astimezone(timezone.utc)).days + 1)
        active_days = len({d.astimezone(timezone.utc).date() for d in dates})
        commits_per_active_day = len(dates) / active_days if active_days else 0
        last_commit_days = max(0, (now - dates[-1].astimezone(timezone.utc)).days)
        weekday_counts = Counter(d.strftime("%A") for d in dates)
        peak_day = weekday_counts.most_common(1)[0][0] if weekday_counts else None
    else:
        days_span = active_days = commits_per_active_day = last_commit_days = 0
        peak_day = None

    recent_window = [d for d in dates if (datetime.now(timezone.utc) - d.astimezone(timezone.utc)).days <= 30]
    previous_window = [d for d in dates if 30 < (datetime.now(timezone.utc) - d.astimezone(timezone.utc)).days <= 60]
    if previous_window:
        trend_pct = (len(recent_window) - len(previous_window)) / len(previous_window) * 100
    elif recent_window:
        trend_pct = 100.0
    else:
        trend_pct = 0.0

    if last_commit_days <= 7 and len(recent_window) >= 5:
        activity_status = "Active"
    elif last_commit_days <= 30:
        activity_status = "Steady"
    elif last_commit_days <= 90:
        activity_status = "Cooling"
    else:
        activity_status = "Stale"

    return {
        "commit_count": len(commits),
        "active_days": active_days,
        "days_span": days_span,
        "commits_per_active_day": round(commits_per_active_day, 2),
        "last_commit_days_ago": last_commit_days,
        "recent_30d_commits": len(recent_window),
        "previous_30d_commits": len(previous_window),
        "commit_trend_pct": round(trend_pct, 1),
        "peak_commit_weekday": peak_day,
        "pull_requests_observed": len(prs),
        "issues_observed": len(issues),
        "status": activity_status,
    }
