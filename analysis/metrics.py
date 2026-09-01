from __future__ import annotations

from typing import Any, Dict, List

from core.models import ContributorStats, RepositoryStats


def compute_repository_metrics(repo: RepositoryStats) -> Dict[str, Any]:
    return {
        "stars": repo.stars,
        "forks": repo.forks,
        "open_issues": repo.open_issues,
        "watchers": repo.watchers,
        "health_score": min(100, max(0, round((repo.stars * 0.4 + repo.forks * 0.5 + (100 - repo.open_issues) * 0.1), 2))),
    }


def compute_contributor_metrics(contributors: List[ContributorStats]) -> Dict[str, Any]:
    total_contributions = sum(c.contributions for c in contributors)
    if not contributors:
        return {"total_contributors": 0, "total_contributions": 0, "top_contributor": None}

    top_contributor = max(contributors, key=lambda c: c.contributions)
    return {
        "total_contributors": len(contributors),
        "total_contributions": total_contributions,
        "top_contributor": top_contributor.login,
        "top_contributor_contributions": top_contributor.contributions,
    }
