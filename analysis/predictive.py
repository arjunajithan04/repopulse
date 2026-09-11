from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

import math

FEATURES = [
    "health", "activity_score", "engineering_score", "documentation_score",
    "testing_score", "contributors", "recent_commits", "open_issues", "open_prs",
]


@dataclass(frozen=True)
class Prediction:
    label: str
    probability: float
    confidence: str
    method: str
    horizon: str
    evidence: list[str]
    limitations: list[str]


def _num(row: Mapping[str, Any], key: str) -> float:
    return float(row.get(key, 0) or 0)


def _timestamp(row: Mapping[str, Any]) -> float:
    raw = str(row.get("captured_at", ""))
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return 0.0


def _feature(row: Mapping[str, Any]) -> list[float]:
    return [_num(row, k) for k in FEATURES]


def _linear_slope(values: Sequence[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(values) / n
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, values)) / den if den else 0.0


def _sigmoid(x: float) -> float:
    x = max(-20.0, min(20.0, x))
    return 1.0 / (1.0 + math.exp(-x))


def _trend_risk(snapshots: Sequence[Mapping[str, Any]]) -> tuple[float, list[str]]:
    recent = list(snapshots[:6])
    evidence: list[str] = []
    score = 0.0
    health = [_num(x, "health_score") for x in reversed(recent)]
    activity = [_num(x, "recent_commits") for x in reversed(recent)]
    testing = [_num(x, "testing_score") for x in reversed(recent)]
    docs = [_num(x, "documentation_score") for x in reversed(recent)]
    if len(health) >= 2:
        hs = _linear_slope(health)
        if hs < -2:
            score += min(35, abs(hs) * 5)
            evidence.append(f"Health is trending downward ({hs:+.1f} points per snapshot).")
        elif hs > 2:
            score -= min(20, hs * 3)
            evidence.append(f"Health is trending upward ({hs:+.1f} points per snapshot).")
    if len(activity) >= 3:
        ac = _linear_slope(activity)
        if ac < -2:
            score += min(30, abs(ac) * 4)
            evidence.append("Recent commit activity is trending downward.")
    if testing and testing[-1] < 45:
        score += 8
        evidence.append("Testing signals remain limited.")
    if docs and docs[-1] < 50:
        score += 5
        evidence.append("Documentation signals remain weak.")
    latest = recent[0] if recent else {}
    if _num(latest, "contributors") <= 1:
        score += 18
        evidence.append("The latest snapshot shows very limited contributor breadth.")
    return max(0.0, min(100.0, score)), evidence



def _logistic_probability(X: Sequence[Sequence[float]], y: Sequence[int], latest: Sequence[float], epochs: int = 700, lr: float = 0.04) -> float:
    """Small dependency-free logistic regression with standardized features."""
    n, m = len(X), len(X[0])
    means = [sum(row[j] for row in X) / n for j in range(m)]
    stds = []
    for j in range(m):
        variance = sum((row[j] - means[j]) ** 2 for row in X) / n
        stds.append(math.sqrt(variance) or 1.0)
    Z = [[(row[j] - means[j]) / stds[j] for j in range(m)] for row in X]
    z_latest = [(latest[j] - means[j]) / stds[j] for j in range(m)]
    weights = [0.0] * m
    bias = 0.0
    for _ in range(epochs):
        grad_w = [0.0] * m
        grad_b = 0.0
        for row, target in zip(Z, y):
            p = _sigmoid(bias + sum(w * x for w, x in zip(weights, row)))
            err = p - target
            for j in range(m):
                grad_w[j] += err * row[j]
            grad_b += err
        for j in range(m):
            weights[j] -= lr * grad_w[j] / n
        bias -= lr * grad_b / n
    return _sigmoid(bias + sum(w * x for w, x in zip(weights, z_latest))) * 100

def predict_repository_risk(snapshots: Sequence[Mapping[str, Any]]) -> Prediction:
    """Estimate near-term maintenance risk from historical snapshots.

    Uses an optional supervised model only when enough sequential observations exist.
    With sparse history it deliberately falls back to an explainable trend model.
    """
    ordered = sorted(snapshots, key=_timestamp, reverse=True)
    if not ordered:
        return Prediction("Insufficient data", 0.0, "None", "No history", "Next 30 days", [], ["Run repository scans over time to build a historical series."])

    # Supervised target: whether the next observed snapshot loses >= 8 health points.
    # A tiny dependency-free logistic regression is used once enough sequential
    # observations exist, so RepoPulse remains easy to deploy on Streamlit.
    if len(ordered) >= 10:
        rows = list(reversed(ordered))
        X, y = [], []
        for i in range(len(rows) - 1):
            X.append(_feature(rows[i]))
            y.append(1 if _num(rows[i + 1], "health_score") - _num(rows[i], "health_score") <= -8 else 0)
        if len(set(y)) >= 2:
            try:
                probability = _logistic_probability(X, y, _feature(rows[-1]))
                label = "High" if probability >= 65 else "Moderate" if probability >= 35 else "Low"
                return Prediction(label, probability, "Medium", "Logistic regression", "Next observed scan", [f"Trained on {len(X)} sequential historical transitions.", "Target = health decline of 8+ points between consecutive snapshots."], ["Historical observations are user-generated repository snapshots, not a universal benchmark.", "Predictions improve as more evenly spaced scans are collected."])
            except (ValueError, OverflowError):
                pass

    risk, evidence = _trend_risk(ordered)
    label = "High" if risk >= 65 else "Moderate" if risk >= 35 else "Low"
    confidence = "Low" if len(ordered) < 4 else "Moderate"
    return Prediction(label, risk, confidence, "Explainable trend model", "Next 30 days", evidence, [f"Only {len(ordered)} historical snapshots are available; supervised ML activates at 10+ snapshots with both outcome classes.", "This is a directional risk estimate, not a guarantee of future repository behaviour."])


def forecast_summary(snapshots: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(snapshots, key=_timestamp, reverse=True)
    prediction = predict_repository_risk(ordered)
    if not ordered:
        return {"prediction": prediction, "health_trend": 0.0, "activity_trend": 0.0, "snapshots": 0}
    health = [_num(x, "health_score") for x in reversed(ordered[:8])]
    activity = [_num(x, "recent_commits") for x in reversed(ordered[:8])]
    return {"prediction": prediction, "health_trend": _linear_slope(health), "activity_trend": _linear_slope(activity), "snapshots": len(ordered)}
