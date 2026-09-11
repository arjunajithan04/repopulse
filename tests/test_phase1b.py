from analysis.code_analysis import analyze_files
from analysis.metrics import compute_contributor_metrics, compute_health_dimensions, compute_repository_health
from analysis.repository_analysis import analyze_repository
from core.models import ContributorStats, RepositoryStats


def test_health_score_uses_health_dimensions():
    repo = RepositoryStats(name="demo", full_name="o/demo", stars=100, forks=20, open_issues=2)
    contributors = [ContributorStats(login="alice", contributions=10)]
    dimensions = compute_health_dimensions(repo, contributors, open_issues=2, open_prs=1, recent_commits=10)
    score = compute_repository_health(dimensions)
    assert 0 <= score <= 100
    assert dimensions["activity"] > 0


def test_contributor_bus_factor_and_concentration():
    contributors = [
        ContributorStats(login="alice", contributions=70),
        ContributorStats(login="bob", contributions=20),
        ContributorStats(login="carol", contributions=10),
    ]
    metrics = compute_contributor_metrics(contributors)
    assert metrics["bus_factor"] == 1
    assert metrics["contributor_concentration"] == 70.0


def test_pr_and_issue_activity_is_attributed():
    result = analyze_repository(
        {"name": "demo", "full_name": "o/demo", "default_branch": "main"},
        [{"login": "alice", "contributions": 5}],
        pull_requests_data=[{"state": "open", "user": {"login": "alice"}}],
        issues_data=[{"state": "open", "user": {"login": "alice"}}],
    )
    alice = result.contributors[0]
    assert alice.pull_requests == 1
    assert alice.issues == 1
    assert result.metrics["open_pull_request_count"] == 1
    assert result.metrics["open_issue_count"] == 1


def test_python_code_scan_returns_file_metrics():
    result = analyze_files([
        {"path": "app.py", "content": "def hello(x):\n    if x:\n        return 1\n    return 0\n"}
    ])
    assert result["files_analyzed"] == 1
    assert result["total_lines"] == 4
    assert result["functions"] == 1
    assert result["total_complexity"] >= 1
