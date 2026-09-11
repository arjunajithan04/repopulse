from analysis.predictive import forecast_summary, predict_repository_risk


def _snap(i, health, commits):
    return {"captured_at": f"2026-09-{i:02d}T10:00:00", "health_score": health, "recent_commits": commits, "contributors": 4, "testing_score": 70, "documentation_score": 80, "activity_score": 80, "engineering_score": 75, "open_issues": 5, "open_prs": 2}


def test_prediction_needs_history():
    p = predict_repository_risk([])
    assert p.label == "Insufficient data"


def test_trend_prediction_detects_decline():
    snaps = [_snap(i, 90 - i * 6, 30 - i * 3) for i in range(1, 7)]
    result = forecast_summary(snaps)
    assert result["prediction"].label in {"Moderate", "High"}
    assert result["health_trend"] < 0
