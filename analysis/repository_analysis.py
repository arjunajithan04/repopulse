from __future__ import annotations

from typing import Any, Dict, List

from core.models import AnalysisResult, ContributorStats, RepositoryStats
from analysis.metrics import compute_contributor_metrics, compute_repository_metrics


def analyze_repository(repo_data: Dict[str, Any], contributors_data: List[Dict[str, Any]]) -> AnalysisResult:
    repo = RepositoryStats(
        name=repo_data.get("name", ""),
        full_name=repo_data.get("full_name", ""),
        stars=repo_data.get("stargazers_count", 0),
        forks=repo_data.get("forks_count", 0),
        open_issues=repo_data.get("open_issues_count", 0),
        watchers=repo_data.get("subscribers_count", 0),
        default_branch=repo_data.get("default_branch", "main"),
        created_at=repo_data.get("created_at"),
        updated_at=repo_data.get("updated_at"),
        language=repo_data.get("language"),
        description=repo_data.get("description"),
    )

    contributors = [
        ContributorStats(
            login=item.get("login", "unknown"),
            contributions=item.get("contributions", 0),
            commits=item.get("contributions", 0),
            pull_requests=0,
            issues=0,
            avatar_url=item.get("avatar_url"),
        )
        for item in contributors_data
    ]

    metrics = {
        **compute_repository_metrics(repo),
        **compute_contributor_metrics(contributors),
    }

    summary = (
        f"{repo.full_name} has {repo.stars} stars, {repo.forks} forks, "
        f"and {len(contributors)} contributors."
    )

    return AnalysisResult(
        repository=repo,
        contributors=contributors,
        metrics=metrics,
        summary=summary,
    )
