from analysis.repository_analysis import analyze_repository, limit_repo_batch, parse_repository_input


def test_analyze_repository_returns_summary():
    repo_data = {
        "name": "demo-repo",
        "full_name": "octocat/demo-repo",
        "stargazers_count": 120,
        "forks_count": 30,
        "open_issues_count": 5,
        "subscribers_count": 40,
        "default_branch": "main",
        "language": "Python",
        "description": "A demo repository",
    }
    contributors_data = [
        {"login": "alice", "contributions": 50, "avatar_url": "https://example.com/alice.png"},
        {"login": "bob", "contributions": 25, "avatar_url": "https://example.com/bob.png"},
    ]

    result = analyze_repository(repo_data, contributors_data)

    assert result.repository.name == "demo-repo"
    assert result.repository.stars == 120
    assert result.metrics["total_contributors"] == 2
    assert "demo-repo" in result.summary


def test_parse_repository_input_accepts_url_and_owner_repo():
    assert parse_repository_input("https://github.com/microsoft/vscode") == ("microsoft", "vscode")
    assert parse_repository_input("microsoft/vscode") == ("microsoft", "vscode")


def test_limit_repo_batch_caps_at_ten():
    repos = [f"owner{i}/repo{i}" for i in range(15)]
    limited = limit_repo_batch(repos)
    assert len(limited) == 10
    assert limited[0] == "owner0/repo0"
    assert limited[-1] == "owner9/repo9"


def test_intelligence_detects_concentration_and_backlog():
    from analysis.intelligence import detect_risks

    risks = detect_risks({
        "repository_health_score": 48,
        "open_issue_count": 61,
        "open_pull_request_count": 34,
        "total_contributors": 5,
        "active_contributors": 2,
        "bus_factor": 1,
        "contributor_concentration": 82,
        "health_dimensions": {"activity": 35, "community": 70, "maintenance": 48},
    })
    titles = {risk.title for risk in risks}
    assert "High issue backlog" in titles
    assert "Large pull-request backlog" in titles
    assert "Single-contributor dependency" in titles
    assert "High contribution concentration" in titles


def test_compare_snapshots_prefers_lower_backlogs():
    from analysis.intelligence import compare_snapshots

    result = compare_snapshots(
        "owner/a", {"health": 80, "commits": 10, "contributors": 4, "stars": 100, "forks": 20, "issues": 8, "pull_requests": 3},
        "owner/b", {"health": 70, "commits": 12, "contributors": 5, "stars": 120, "forks": 25, "issues": 20, "pull_requests": 10},
    )
    rows = {row["Metric"]: row for row in result["rows"]}
    assert rows["Health"]["Leader"] == "owner/a"
    assert rows["Open issues"]["Leader"] == "owner/a"
    assert rows["Open PRs"]["Leader"] == "owner/a"
