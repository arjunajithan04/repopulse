from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from analysis.metrics import compute_contributor_metrics, compute_health_dimensions, compute_repository_health, compute_repository_metrics
from analysis.activity import analyze_activity
from analysis.engineering import analyze_engineering
from core.models import AnalysisResult, ContributorStats, RepositoryStats


def parse_repository_input(repo_value: str) -> Tuple[str, str]:
    candidate = (repo_value or "").strip().replace(".git", "").rstrip("/")
    if not candidate:
        raise ValueError("Please provide a GitHub repository in the format owner/repo or a GitHub URL.")
    for prefix in ("https://github.com/", "http://github.com/", "www.github.com/", "github.com/"):
        candidate = candidate.replace(prefix, "")
    if "/" not in candidate:
        raise ValueError("Repository must include both owner and repo, for example: microsoft/vscode")
    owner, repo = candidate.split("/", 1)
    owner, repo = owner.strip(), repo.strip()
    if not owner or not repo or "/" in repo:
        raise ValueError("Please provide a valid GitHub repository such as microsoft/vscode")
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


def _aggregate_contributor_activity(
    contributors_data: List[Dict[str, Any]],
    pull_requests_data: List[Dict[str, Any]],
    issues_data: List[Dict[str, Any]],
) -> List[ContributorStats]:
    by_login: Dict[str, ContributorStats] = {}
    for item in contributors_data:
        login = item.get("login", "unknown")
        by_login[login] = ContributorStats(
            login=login,
            contributions=int(item.get("contributions", 0) or 0),
            commits=int(item.get("contributions", 0) or 0),
            avatar_url=item.get("avatar_url"),
        )
    for pr in pull_requests_data:
        user = (pr.get("user") or {}).get("login")
        if user:
            by_login.setdefault(user, ContributorStats(login=user, avatar_url=(pr.get("user") or {}).get("avatar_url")))
            by_login[user].pull_requests += 1
    for issue in issues_data:
        if "pull_request" in issue:
            continue
        user = (issue.get("user") or {}).get("login")
        if user:
            by_login.setdefault(user, ContributorStats(login=user, avatar_url=(issue.get("user") or {}).get("avatar_url")))
            by_login[user].issues += 1
    return sorted(by_login.values(), key=lambda c: c.contributions, reverse=True)


def analyze_repository(
    repo_data: Dict[str, Any],
    contributors_data: List[Dict[str, Any]],
    languages_data: Dict[str, Any] | None = None,
    issues_data: List[Dict[str, Any]] | None = None,
    pull_requests_data: List[Dict[str, Any]] | None = None,
    commits_data: List[Dict[str, Any]] | None = None,
    tree_data: List[Dict[str, Any]] | None = None,
    scanned_files: List[Dict[str, str]] | None = None,
) -> AnalysisResult:
    repo = RepositoryStats(
        name=repo_data.get("name", ""),
        full_name=repo_data.get("full_name", ""),
        stars=int(repo_data.get("stargazers_count", 0) or 0),
        forks=int(repo_data.get("forks_count", 0) or 0),
        open_issues=int(repo_data.get("open_issues_count", 0) or 0),
        watchers=int(repo_data.get("subscribers_count", 0) or 0),
        default_branch=repo_data.get("default_branch", "main"),
        created_at=repo_data.get("created_at"),
        updated_at=repo_data.get("updated_at"),
        language=repo_data.get("language"),
        description=repo_data.get("description"),
    )

    issues = [item for item in (issues_data or []) if "pull_request" not in item and item.get("state") == "open"]
    all_prs = pull_requests_data or []
    open_prs = [pr for pr in all_prs if pr.get("state") == "open"]
    commits = commits_data or []
    contributors = _aggregate_contributor_activity(contributors_data, all_prs, issues_data or [])

    dimensions = compute_health_dimensions(repo, contributors, len(issues), len(open_prs), len(commits))
    health = compute_repository_health(dimensions)

    activity = analyze_activity(commits, all_prs, issues_data or [])
    engineering = analyze_engineering(tree_data or [], scanned_files or [])

    metrics = {
        **compute_repository_metrics(repo),
        **compute_contributor_metrics(contributors),
        "language_breakdown": languages_data or {},
        "languages_total": len(languages_data or {}),
        "open_issue_count": len(issues),
        "open_pull_request_count": len(open_prs),
        "recent_commit_count": len(commits),
        "health_dimensions": dimensions,
        "repository_health_score": health,
        "activity_intelligence": activity,
        "engineering_intelligence": engineering,
    }

    summary = (
        f"{repo.full_name} has {repo.stars:,} stars, {repo.forks:,} forks, {len(contributors)} contributors, "
        f"{len(open_prs)} open pull requests, and {len(issues)} open issues."
    )
    return AnalysisResult(repository=repo, contributors=contributors, metrics=metrics, summary=summary)
