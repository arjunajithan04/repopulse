from analysis.activity import analyze_activity
from analysis.engineering import analyze_engineering
from analysis.repository_analysis import analyze_repository


def test_activity_detects_recent_commit_trend():
    commits = [
        {"commit": {"author": {"date": "2026-09-10T10:00:00Z"}}},
        {"commit": {"author": {"date": "2026-09-08T10:00:00Z"}}},
        {"commit": {"author": {"date": "2026-08-01T10:00:00Z"}}},
    ]
    result = analyze_activity(commits)
    assert result["commit_count"] == 3
    assert result["active_days"] == 3
    assert result["recent_30d_commits"] >= 2


def test_engineering_detects_docs_tests_and_dependencies():
    tree = [
        {"path": "README.md", "type": "blob"},
        {"path": "LICENSE", "type": "blob"},
        {"path": "CONTRIBUTING.md", "type": "blob"},
        {"path": "tests/test_app.py", "type": "blob"},
        {"path": "app.py", "type": "blob"},
        {"path": "requirements.txt", "type": "blob"},
    ]
    files = [
        {"path": "requirements.txt", "content": "streamlit>=1.0\nrequests>=2.0\npandas>=2.0\n"},
        {"path": "README.md", "content": "# RepoPulse\n"},
    ]
    result = analyze_engineering(tree, files)
    assert result["has_readme"] is True
    assert result["has_license"] is True
    assert result["has_contributing"] is True
    assert result["test_files"] == 1
    assert result["dependencies_observed"] == 3
    assert result["engineering_score"] > 0


def test_repository_analysis_includes_phase5_intelligence():
    result = analyze_repository(
        {"name": "demo", "full_name": "o/demo", "default_branch": "main"},
        [{"login": "alice", "contributions": 5}],
        tree_data=[{"path": "README.md", "type": "blob"}, {"path": "tests/test_a.py", "type": "blob"}],
    )
    assert "activity_intelligence" in result.metrics
    assert "engineering_intelligence" in result.metrics
