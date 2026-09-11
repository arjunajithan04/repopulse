from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.models import ContributorStats, RepositoryStats


def _score_inverse(count: int, threshold: int) -> float:
    if threshold <= 0:
        return 100.0
    return round(max(0.0, min(100.0, 100.0 - (count / threshold) * 100.0)), 1)


def _recency_score(updated_at: str | None) -> float:
    if not updated_at:
        return 50.0
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        days = max(0, (datetime.now(timezone.utc) - dt).days)
        if days <= 7:
            return 100.0
        if days <= 30:
            return 90.0
        if days <= 90:
            return 75.0
        if days <= 180:
            return 55.0
        return 30.0
    except ValueError:
        return 50.0


def compute_health_dimensions(
    repo: RepositoryStats,
    contributors: List[ContributorStats],
    open_issues: int,
    open_prs: int,
    recent_commits: int,
) -> Dict[str, float]:
    contributor_count = len(contributors)
    activity = min(100.0, recent_commits * 8 + contributor_count * 3)
    community = min(100.0, contributor_count * 7 + min(repo.stars / 5000, 25))
    maintenance = round((_recency_score(repo.updated_at) * 0.55) + (_score_inverse(open_prs, 30) * 0.25) + (_score_inverse(open_issues, 50) * 0.20), 1)
    issue_health = _score_inverse(open_issues, 50)
    pr_health = _score_inverse(open_prs, 30)
    contributor_health = min(100.0, contributor_count * 10.0)
    return {
        "activity": round(activity, 1),
        "community": round(community, 1),
        "maintenance": maintenance,
        "issue_health": issue_health,
        "pr_health": pr_health,
        "contributor_health": round(contributor_health, 1),
    }


def compute_repository_health(dimensions: Dict[str, float]) -> float:
    weights = {"activity": 0.20, "community": 0.10, "maintenance": 0.20, "issue_health": 0.15, "pr_health": 0.15, "contributor_health": 0.20}
    return round(sum(dimensions.get(key, 0) * weight for key, weight in weights.items()), 1)


def compute_repository_metrics(repo: RepositoryStats) -> Dict[str, Any]:
    return {"stars": repo.stars, "forks": repo.forks, "open_issues": repo.open_issues, "watchers": repo.watchers}


def compute_contributor_metrics(contributors: List[ContributorStats]) -> Dict[str, Any]:
    total_contributions = sum(max(0, c.contributions) for c in contributors)
    if not contributors:
        return {"total_contributors": 0, "total_contributions": 0, "top_contributor": None, "top_contributor_contributions": 0, "bus_factor": 0, "contributor_concentration": 0.0, "active_contributors": 0}

    ranked = sorted(contributors, key=lambda c: (c.contributions, c.pull_requests, c.issues), reverse=True)
    top = ranked[0]
    cumulative = 0
    bus_factor = 0
    target = total_contributions * 0.5
    for contributor in ranked:
        cumulative += max(0, contributor.contributions)
        bus_factor += 1
        if cumulative >= target:
            break
    concentration = (top.contributions / total_contributions * 100) if total_contributions else 0
    active = sum(1 for c in contributors if c.contributions or c.pull_requests or c.issues)
    return {
        "total_contributors": len(contributors),
        "active_contributors": active,
        "total_contributions": total_contributions,
        "top_contributor": top.login,
        "top_contributor_contributions": top.contributions,
        "bus_factor": bus_factor,
        "contributor_concentration": round(concentration, 1),
    }
