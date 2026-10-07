from analysis.resilience import build_resilience_intelligence, simulate_scenario


def _metrics():
    return {
        "repository_health_score": 82,
        "contributor_concentration": 72,
        "bus_factor": 1,
        "open_issue_count": 12,
        "health_dimensions": {
            "activity": 86,
            "maintenance": 84,
            "issue_health": 76,
            "pr_health": 80,
            "contributor_health": 58,
        },
    }


def test_resilience_separates_health_from_resilience_and_detects_dependency():
    result = build_resilience_intelligence(_metrics(), [
        {"captured_at": "2026-09-01", "health_score": 75, "recent_commits": 20},
        {"captured_at": "2026-10-01", "health_score": 82, "recent_commits": 24},
    ])
    assert result["health"] == 82
    assert result["resilience"] < result["health"]
    assert result["state"] == "MAINTAINER DEPENDENT"
    assert result["recommendation"]["title"] == "Broaden ownership"


def test_maintainer_scenario_reduces_resilience():
    result = simulate_scenario(_metrics(), "maintainer_inactive")
    assert result["direction"] == "negative"
    assert result["projected_resilience"] < result["base_resilience"]
    assert result["projected_health"] < result["base_health"]


def test_broaden_ownership_improves_resilience():
    result = simulate_scenario(_metrics(), "broaden_ownership")
    assert result["direction"] == "positive"
    assert result["projected_resilience"] > result["base_resilience"]


def test_empty_history_uses_neutral_momentum():
    result = build_resilience_intelligence({"repository_health_score": 70, "health_dimensions": {}})
    assert result["momentum"] == 50
    assert 0 <= result["resilience"] <= 100
