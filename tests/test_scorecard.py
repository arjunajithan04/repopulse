from analysis.scorecard import build_scorecard


def test_scorecard_maps_existing_dimensions_to_executive_signals():
    result = build_scorecard(
        {
            "repository_health_score": 84,
            "health_dimensions": {
                "activity": 90,
                "community": 80,
                "maintenance": 70,
                "issue_health": 85,
                "pr_health": 75,
                "contributor_health": 90,
            },
        }
    )
    assert result["status"] == "HEALTHY"
    assert result["cards"]["Health"] == 84
    assert result["cards"]["Activity"] == 90
    assert result["cards"]["Community"] == 85
    assert result["cards"]["Stability"] == 75.8
    assert result["weakest_dimension"] == "Maintenance"
    assert result["strongest_dimension"] == "Activity"


def test_scorecard_momentum_uses_previous_snapshot():
    result = build_scorecard(
        {"repository_health_score": 88, "health_dimensions": {"activity": 80, "community": 80}},
        [
            {"captured_at": "2026-09-01", "health_score": 70},
            {"captured_at": "2026-10-01", "health_score": 80},
        ],
    )
    assert result["cards"]["Momentum"] == 100
    assert result["history_available"] is True
    assert "upward" in result["momentum_note"]


def test_scorecard_clamps_low_health():
    result = build_scorecard({"repository_health_score": 35, "health_dimensions": {}})
    assert result["status"] == "AT RISK"
    assert result["tone"] == "danger"
    assert all(0 <= value <= 100 for value in result["cards"].values())
