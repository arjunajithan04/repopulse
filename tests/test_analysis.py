from analysis.repository_analysis import analyze_repository


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
