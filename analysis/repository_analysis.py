from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from analysis.metrics import (
    compute_contributor_metrics,
    compute_health_metrics,
    compute_repository_metrics,
    enrich_contributor_activity,
)
from core.models import AnalysisResult, ContributorStats, RepositoryStats


def parse_repository_input(repo_value: str) -> Tuple[str, str]:
    candidate = (repo_value or "").strip().replace(".git", "").rstrip("/")
    if not candidate:
        raise ValueError("Please provide a GitHub repository in the format owner/repo or a GitHub URL.")

    for prefix in ("https://github.com/", "http://github.com/", "www.github.com/", "github.com/"):
        if candidate.startswith(prefix):
            candidate = candidate[len(prefix):]
            break

    parts = [part.strip() for part in candidate.split("/") if part.strip()]
    if len(parts) != 2:
        raise ValueError("Repository must include both owner and repo, for example: microsoft/vscode")
    return parts[0], parts[1]


def limit_repo_batch(repos: Sequence[str], max_repos: int = 10) -> List[str]:
    seen = set()
    limited = []
    for repo in repos:
        try:
            owner, name = parse_repository_input(repo)
        except ValueError:
            continue
        normalized = f"{owner}/{name}".lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        limited.append(f"{owner}/{name}")
        if len(limited) >= max_repos:
            break
    return limited


def analyze_repository(
    repo_data: Dict[str, Any],
    contributors_data: List[Dict[str, Any]],
    languages_data: Dict[str, Any] | None = None,
    issues_data: List[Dict[str, Any]] | None = None,
    pull_requests_data: List[Dict[str, Any]] | None = None,
    commits_data: List[Dict[str, Any]] | None = None,
) -> AnalysisResult:
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
            avatar_url=item.get("avatar_url"),
        )
        for item in contributors_data
    ]

    languages = languages_data or {}
    all_issues = issues_data or []
    all_prs = pull_requests_data or []
    open_issues = [issue for issue in all_issues if issue.get("state") == "open" and "pull_request" not in issue]
    open_prs = [pr for pr in all_prs if pr.get("state") == "open"]
    recent_commits = commits_data or []

    enrich_contributor_activity(contributors, all_prs, all_issues)
    contributor_metrics = compute_contributor_metrics(contributors)
    health_metrics = compute_health_metrics(
        repo,
        open_issues=len(open_issues),
        open_prs=len(open_prs),
        recent_commits=len(recent_commits),
        contributor_count=len(contributors),
        total_contributions=contributor_metrics["total_contributions"],
    )

    metrics = {
        **compute_repository_metrics(repo),
        **contributor_metrics,
        **health_metrics,
        "language_breakdown": languages,
        "languages_total": len(languages),
        "open_issue_count": len(open_issues),
        "open_pull_request_count": len(open_prs),
        "recent_commit_count": len(recent_commits),
        "analysis_coverage": {
            "contributors": len(contributors),
            "pull_requests": len(all_prs),
            "issues": len(all_issues),
            "commits": len(recent_commits),
        },
    }

    health = health_metrics["repository_health_score"]
    status = "Healthy" if health >= 80 else "Moderate" if health >= 60 else "At risk"
    summary = (
        f"{repo.full_name} is {status.lower()} at {health}/100. "
        f"It has {repo.stars} stars, {repo.forks} forks, {len(contributors)} contributors, "
        f"{len(open_prs)} open pull requests, and {len(open_issues)} open issues."
    )

    return AnalysisResult(repository=repo, contributors=contributors, metrics=metrics, summary=summary)
