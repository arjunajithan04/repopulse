from analysis.causal import build_change_explanation


def _metrics():
    return {
        "repository_health_score": 68,
        "recent_commit_count": 10,
        "total_contributors": 4,
        "open_issue_count": 18,
        "open_pull_request_count": 9,
        "health_dimensions": {
            "activity": 50,
            "community": 65,
            "maintenance": 70,
            "issue_health": 55,
            "pr_health": 60,
            "contributor_health": 52,
        },
    }


def test_no_previous_snapshot_returns_explicit_unavailable_state():
    result = build_change_explanation(_metrics(), None)
    assert result["available"] is False
    assert result["drivers"] == []


def test_change_explanation_identifies_weighted_dimension_drivers():
    previous = {
        "health_score": 76,
        "commits": 16,
        "contributors": 5,
        "issues": 10,
        "pull_requests": 6,
        "health_dimensions": {
            "activity": 80,
            "community": 72,
            "maintenance": 78,
            "issue_health": 75,
            "pr_health": 70,
            "contributor_health": 70,
        },
    }
    result = build_change_explanation(_metrics(), previous)
    assert result["available"] is True
    assert result["health_delta"] == -8
    assert result["negative_drivers"]
    assert result["negative_drivers"][0]["name"] == "Activity"
    assert result["telemetry"]
    assert "not proof of causation" in result["basis"]


def test_stable_dimensions_do_not_create_fake_drivers():
    metrics = _metrics()
    metrics["repository_health_score"] = 70
    previous = {
        "health_score": 70,
        "health_dimensions": metrics["health_dimensions"].copy(),
    }
    result = build_change_explanation(metrics, previous)
    assert result["health_delta"] == 0
    assert result["drivers"] == []
    assert result["telemetry"] == []
