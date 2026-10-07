from analysis.predictive import forecast_summary, predict_repository_risk


def _snap(i, health, commits, contributors=4, issues=5, prs=2):
    return {
        "captured_at": f"2026-09-{i:02d}T10:00:00",
        "health_score": health,
        "recent_commits": commits,
        "contributors": contributors,
        "testing_score": 70,
        "documentation_score": 80,
        "activity_score": 80,
        "engineering_score": 75,
        "open_issues": issues,
        "open_prs": prs,
    }


def test_prediction_needs_history():
    p = predict_repository_risk([])
    assert p.label == "Insufficient data"
    assert p.factors == []


def test_trend_prediction_detects_decline():
    snaps = [_snap(i, 90 - i * 6, 30 - i * 3) for i in range(1, 7)]
    result = forecast_summary(snaps)
    assert result["prediction"].label in {"Moderate", "High"}
    assert result["health_trend"] < 0
    assert result["prediction"].factors
    assert result["risk_timeline"]


def test_predictive_engine_detects_issue_and_review_pressure():
    snaps = [_snap(i, 78, 20, issues=4 + i * 3, prs=2 + i) for i in range(1, 7)]
    prediction = predict_repository_risk(snaps)
    names = {factor.name for factor in prediction.factors}
    assert "Issue pressure" in names
    assert "Review pressure" in names


def test_predictive_engine_flags_maintainer_dependency():
    snaps = [_snap(i, 70, 10, contributors=1) for i in range(1, 5)]
    prediction = predict_repository_risk(snaps)
    assert any(f.name == "Maintainer dependency" for f in prediction.factors)
