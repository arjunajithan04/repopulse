from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from core.models import AnalysisResult, ContributorStats, RepositoryStats
from analysis.metrics import compute_contributor_metrics, compute_repository_metrics


def parse_repository_input(repo_value: str) -> Tuple[str, str]:
    candidate = (repo_value or "").strip().replace(".git", "").rstrip("/")
    if not candidate:
        raise ValueError("Please provide a GitHub repository in the format owner/repo or a GitHub URL.")

    candidate = candidate.replace("https://github.com/", "")
    candidate = candidate.replace("http://github.com/", "")
    candidate = candidate.replace("www.github.com/", "")
    candidate = candidate.replace("github.com/", "")

    if "/" not in candidate:
        raise ValueError("Repository must include both owner and repo, for example: microsoft/vscode")

    owner, repo = candidate.split("/", 1)
    owner = owner.strip()
    repo = repo.strip()

    if not owner or not repo:
        raise ValueError("Repository must include both owner and repo, for example: microsoft/vscode")

    return owner, repo


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
            pull_requests=0,
            issues=0,
            avatar_url=item.get("avatar_url"),
        )
        for item in contributors_data
    ]

    languages = languages_data or {}
    open_issues = issues_data or []
    open_prs = [pr for pr in (pull_requests_data or []) if pr.get("state") == "open"]
    recent_commits = commits_data or []

    metrics = {
        **compute_repository_metrics(repo),
        **compute_contributor_metrics(contributors),
        "language_breakdown": languages,
        "languages_total": len(languages),
        "open_issue_count": len(open_issues),
        "open_pull_request_count": len(open_prs),
        "recent_commit_count": len(recent_commits),
        "repository_health_score": min(100, max(0, round((repo.stars * 0.35 + repo.forks * 0.4 + max(0, 100 - repo.open_issues) * 0.25), 2))),
    }

    summary = (
        f"{repo.full_name} has {repo.stars} stars, {repo.forks} forks, {len(contributors)} contributors, "
        f"{len(open_prs)} open pull requests, and {len(open_issues)} open issues."
    )

    return AnalysisResult(
        repository=repo,
        contributors=contributors,
        metrics=metrics,
        summary=summary,
    )
