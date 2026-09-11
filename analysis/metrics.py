from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from core.models import ContributorStats, RepositoryStats


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return round(max(low, min(high, value)), 2)


def _inverse_pressure(value: float, healthy_limit: float, critical_limit: float) -> float:
    if value <= healthy_limit:
        return 100.0
    if value >= critical_limit:
        return 0.0
    return 100 * (critical_limit - value) / (critical_limit - healthy_limit)


def compute_health_metrics(
    repo: RepositoryStats,
    open_issues: int,
    open_prs: int,
    recent_commits: int,
    contributor_count: int,
    total_contributions: int,
) -> Dict[str, Any]:
    """Compute interpretable health dimensions from observable repository signals."""
    activity = _clamp(recent_commits * 4)
    maintenance = _clamp(100 - (open_issues * 1.5) + min(recent_commits, 20) * 1.5)
    issue_health = _inverse_pressure(open_issues, 10, 100)
    pr_health = _inverse_pressure(open_prs, 5, 50)
    community = _clamp(contributor_count * 8 + min(repo.stars / 1000, 20) * 2)

    if contributor_count:
        average_contributions = total_contributions / contributor_count
        contributor_health = _clamp(50 + min(average_contributions, 50))
    else:
        contributor_health = 0

    overall = (
        activity * 0.20
        + maintenance * 0.20
        + issue_health * 0.15
        + pr_health * 0.15
        + community * 0.15
        + contributor_health * 0.15
    )

    return {
        "activity_score": _clamp(activity),
        "maintenance_score": _clamp(maintenance),
        "issue_health_score": _clamp(issue_health),
        "pr_health_score": _clamp(pr_health),
        "community_score": _clamp(community),
        "contributor_health_score": _clamp(contributor_health),
        "repository_health_score": _clamp(overall),
    }


def compute_repository_metrics(repo: RepositoryStats) -> Dict[str, Any]:
    return {
        "stars": repo.stars,
        "forks": repo.forks,
        "open_issues": repo.open_issues,
        "watchers": repo.watchers,
    }


def compute_contributor_metrics(contributors: List[ContributorStats]) -> Dict[str, Any]:
    total_contributions = sum(c.contributions for c in contributors)
    if not contributors:
        return {
            "total_contributors": 0,
            "total_contributions": 0,
            "top_contributor": None,
            "top_contributor_contributions": 0,
            "contribution_concentration": 0,
            "bus_factor": 0,
        }

    ranked = sorted(contributors, key=lambda c: c.contributions, reverse=True)
    top = ranked[0]
    concentration = (top.contributions / total_contributions * 100) if total_contributions else 0

    running = 0
    bus_factor = 0
    target = total_contributions * 0.5
    for contributor in ranked:
        running += contributor.contributions
        bus_factor += 1
        if running >= target:
            break

    return {
        "total_contributors": len(contributors),
        "total_contributions": total_contributions,
        "top_contributor": top.login,
        "top_contributor_contributions": top.contributions,
        "contribution_concentration": round(concentration, 2),
        "bus_factor": bus_factor,
    }


def enrich_contributor_activity(
    contributors: List[ContributorStats],
    pull_requests: List[Dict[str, Any]],
    issues: List[Dict[str, Any]],
) -> List[ContributorStats]:
    """Attach PR and issue activity to contributors where GitHub exposes an author."""
    pr_counts = Counter(
        item.get("user", {}).get("login")
        for item in pull_requests
        if item.get("user", {}).get("login")
    )
    issue_counts = Counter(
        item.get("user", {}).get("login")
        for item in issues
        if item.get("user", {}).get("login") and "pull_request" not in item
    )

    for contributor in contributors:
        contributor.pull_requests = pr_counts.get(contributor.login, 0)
        contributor.issues = issue_counts.get(contributor.login, 0)
    return contributors
