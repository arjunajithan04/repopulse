from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping


@dataclass(frozen=True)
class Risk:
    severity: str
    title: str
    detail: str
    recommendation: str


_DIMENSION_LABELS = {
    "activity": "Activity",
    "community": "Community",
    "maintenance": "Maintenance",
    "issue_health": "Issue health",
    "pr_health": "PR health",
    "contributor_health": "Contributor health",
}


def _severity_rank(value: str) -> int:
    return {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}.get(value, 0)


def detect_risks(metrics: Mapping[str, Any]) -> List[Risk]:
    """Generate explainable repository risks from measured RepoPulse metrics."""
    risks: List[Risk] = []
    issues = int(metrics.get("open_issue_count", 0) or 0)
    prs = int(metrics.get("open_pull_request_count", 0) or 0)
    contributors = int(metrics.get("total_contributors", 0) or 0)
    active = int(metrics.get("active_contributors", 0) or 0)
    bus_factor = int(metrics.get("bus_factor", 0) or 0)
    concentration = float(metrics.get("contributor_concentration", 0) or 0)
    health = float(metrics.get("repository_health_score", 0) or 0)
    dimensions = metrics.get("health_dimensions", {}) or {}
    code = metrics.get("code_analysis") or {}

    if health < 50:
        risks.append(Risk("Critical", "Overall health is low", f"The repository health score is {health:.1f}/100.", "Address the weakest health dimensions first and re-scan after changes."))
    elif health < 65:
        risks.append(Risk("High", "Overall health needs attention", f"The repository health score is {health:.1f}/100.", "Focus on the lowest-scoring maintenance, activity, or community signals."))

    if issues > 50:
        risks.append(Risk("High", "High issue backlog", f"{issues:,} open issues indicate substantial triage pressure.", "Triage stale, duplicate, and blocked issues before adding more scope."))
    elif issues > 20:
        risks.append(Risk("Medium", "Issue backlog needs attention", f"There are {issues:,} open issues.", "Review issue age and prioritize the highest-impact backlog items."))

    if prs > 30:
        risks.append(Risk("High", "Large pull-request backlog", f"{prs:,} open PRs may indicate review or merge bottlenecks.", "Prioritize reviews and close obsolete or blocked PRs."))
    elif prs > 15:
        risks.append(Risk("Medium", "PR backlog needs attention", f"There are {prs:,} open pull requests.", "Reduce review latency and identify blocked PRs."))

    if contributors and bus_factor <= 1:
        risks.append(Risk("Critical", "Single-contributor dependency", "At least half of measured contributions are concentrated in one contributor.", "Document ownership and actively onboard another maintainer."))
    elif contributors and bus_factor <= 2:
        risks.append(Risk("High", "Low bus factor", f"A small number of contributors account for at least half of measured contributions (bus factor {bus_factor}).", "Spread ownership across more maintainers and improve contributor onboarding."))

    if concentration >= 75 and contributors > 1:
        risks.append(Risk("High", "High contribution concentration", f"The top contributor accounts for {concentration:.1f}% of measured contributions.", "Create review ownership, documentation, and onboarding paths for additional contributors."))
    elif concentration >= 55 and contributors > 1:
        risks.append(Risk("Medium", "Contribution concentration", f"The top contributor accounts for {concentration:.1f}% of measured contributions.", "Encourage broader participation in commits, issues, and pull requests."))

    if contributors and active < max(1, contributors // 2):
        risks.append(Risk("Medium", "Low active-contributor ratio", f"Only {active} of {contributors} measured contributors are currently active in the fetched activity window.", "Reconnect inactive contributors or simplify contribution pathways."))

    weakest = sorted(((float(v), k) for k, v in dimensions.items()), key=lambda x: x[0])
    if weakest and weakest[0][0] < 55:
        score, key = weakest[0]
        risks.append(Risk("High" if score < 40 else "Medium", f"Weak { _DIMENSION_LABELS.get(key, key) } signal", f"{_DIMENSION_LABELS.get(key, key)} is scored at {score:.1f}/100.", _dimension_action(key)))

    activity = metrics.get("activity_intelligence") or {}
    if activity:
        days = int(activity.get("last_commit_days_ago", 0) or 0)
        trend = float(activity.get("commit_trend_pct", 0) or 0)
        if days > 90:
            risks.append(Risk("High", "Repository activity is stale", f"The latest observed commit is {days} days old.", "Confirm whether the repository is intentionally dormant; otherwise resume maintenance activity."))
        elif trend <= -50:
            risks.append(Risk("Medium", "Commit activity is declining", f"Observed 30-day commit activity is down {abs(trend):.1f}% versus the preceding window.", "Investigate whether development has slowed because of blockers, release cycles, or reduced maintenance capacity."))

    engineering = metrics.get("engineering_intelligence") or {}
    if engineering:
        testing = float(engineering.get("testing_score", 0) or 0)
        documentation = float(engineering.get("documentation_score", 0) or 0)
        if testing < 40:
            risks.append(Risk("Medium", "Limited testing signals", "No strong test-file presence was detected in the repository inventory.", "Add or strengthen automated tests around critical functionality."))
        if documentation < 50:
            risks.append(Risk("Medium", "Documentation signals are weak", f"The documentation score is {documentation:.1f}/100.", "Improve the README and add contributor or project documentation where appropriate."))

    if code:
        quality = float(code.get("quality_score", 0) or 0)
        avg_complexity = float(code.get("avg_complexity", 0) or 0)
        if quality < 55:
            risks.append(Risk("High", "Code quality signal is low", f"The bounded code scan produced a quality score of {quality:.1f}/100.", "Inspect the flagged and highest-complexity files and break down hotspots."))
        elif quality < 70:
            risks.append(Risk("Medium", "Code quality could improve", f"The bounded code scan produced a quality score of {quality:.1f}/100.", "Review quality flags and prioritize the largest or most complex files."))
        if avg_complexity >= 10:
            risks.append(Risk("Medium", "Complexity hotspots detected", f"Average measured complexity is {avg_complexity:.1f} in the bounded scan.", "Refactor the highest-complexity functions/files into smaller units."))

    return sorted(risks, key=lambda r: (-_severity_rank(r.severity), r.title))


def _dimension_action(key: str) -> str:
    return {
        "activity": "Increase development cadence or investigate whether the repository is becoming inactive.",
        "community": "Improve contributor onboarding, documentation, and discoverability.",
        "maintenance": "Prioritize stale maintenance work, unresolved PRs, and repository upkeep.",
        "issue_health": "Triage the issue backlog and close stale or duplicate issues.",
        "pr_health": "Review open pull requests and reduce review or merge bottlenecks.",
        "contributor_health": "Reduce ownership concentration and strengthen contributor onboarding.",
    }.get(key, "Review the weakest health dimension and re-scan after changes.")


def trend_summary(current: Mapping[str, Any], previous: Mapping[str, Any] | None) -> List[Dict[str, Any]]:
    if not previous:
        return []
    definitions = [
        ("Stars", "stars", False),
        ("Forks", "forks", False),
        ("Open issues", "issues", True),
        ("Open PRs", "pull_requests", True),
        ("Contributors", "contributors", False),
        ("Recent commits", "commits", False),
        ("Health", "health", False),
    ]
    result = []
    for label, key, inverse in definitions:
        now = float(current.get(key, 0) or 0)
        old = float(previous.get(key, 0) or 0)
        change = now - old
        pct = (change / abs(old) * 100) if old else None
        if change == 0:
            direction = "flat"
            interpretation = "unchanged"
        else:
            direction = "up" if change > 0 else "down"
            positive = change < 0 if inverse else change > 0
            interpretation = "improved" if positive else "declined"
        result.append({"label": label, "key": key, "current": now, "previous": old, "change": change, "pct": pct, "direction": direction, "interpretation": interpretation})
    return result


def assessment(metrics: Mapping[str, Any], previous: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    score = float(metrics.get("repository_health_score", 0) or 0)
    dimensions = metrics.get("health_dimensions", {}) or {}
    risks = detect_risks(metrics)
    trends = trend_summary({
        "stars": metrics.get("stars", 0),
        "forks": metrics.get("forks", 0),
        "issues": metrics.get("open_issue_count", 0),
        "pull_requests": metrics.get("open_pull_request_count", 0),
        "contributors": metrics.get("total_contributors", 0),
        "commits": metrics.get("recent_commit_count", 0),
        "health": score,
    }, previous)
    if score >= 80:
        status = "Healthy"
        intro = "The repository currently shows a strong overall health profile."
    elif score >= 60:
        status = "Moderate"
        intro = "The repository is functional but has measurable areas that could be strengthened."
    else:
        status = "At Risk"
        intro = "The repository has several signals that deserve attention."

    weakest = min(((float(v), k) for k, v in dimensions.items()), default=(score, "health"))
    strengths = [f"{_DIMENSION_LABELS.get(k, k)} is strong at {v:.1f}/100" for k, v in dimensions.items() if float(v) >= 80]
    if not strengths:
        strengths = ["No health dimension currently exceeds 80/100; improvement opportunities are distributed across the profile."]
    priorities = [r.recommendation for r in risks[:3]]
    if not priorities:
        priorities = [_dimension_action(weakest[1])]

    return {
        "status": status,
        "score": score,
        "intro": intro,
        "strengths": strengths[:3],
        "risks": risks,
        "priorities": priorities,
        "weakest_dimension": _DIMENSION_LABELS.get(weakest[1], weakest[1]),
        "trends": trends,
    }


def compare_snapshots(a_name: str, a: Mapping[str, Any], b_name: str, b: Mapping[str, Any]) -> Dict[str, Any]:
    definitions = [
        ("Health", "health", False),
        ("Recent commits", "commits", False),
        ("Contributors", "contributors", False),
        ("Stars", "stars", False),
        ("Forks", "forks", False),
        ("Open issues", "issues", True),
        ("Open PRs", "pull_requests", True),
        ("Engineering", "engineering", False),
        ("Documentation", "documentation", False),
        ("Testing", "testing", False),
    ]
    rows = []
    scores = {a_name: 0, b_name: 0}
    for label, key, inverse in definitions:
        av = float(a.get(key, 0) or 0)
        bv = float(b.get(key, 0) or 0)
        if av == bv:
            leader = "Tie"
        else:
            leader = a_name if (av < bv if inverse else av > bv) else b_name
            scores[leader] += 1
        rows.append({"Metric": label, a_name: av, b_name: bv, "Leader": leader})
    winner = a_name if scores[a_name] > scores[b_name] else b_name if scores[b_name] > scores[a_name] else "Tie"
    return {"rows": rows, "scores": scores, "winner": winner}
