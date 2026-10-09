from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

import math

FEATURES = [
    "health_score",
    "activity_score",
    "engineering_score",
    "documentation_score",
    "testing_score",
    "contributors",
    "recent_commits",
    "open_issues",
    "open_pull_requests",
]


@dataclass(frozen=True)
class RiskFactor:
    name: str
    severity: str
    score: float
    trend: str
    evidence: str
    recommendation: str


@dataclass(frozen=True)
class Prediction:
    label: str
    probability: float
    confidence: str
    method: str
    horizon: str
    evidence: list[str]
    limitations: list[str]
    factors: list[RiskFactor]
    recommendation: str


def _num(row: Mapping[str, Any], key: str) -> float:
    # Snapshot history contains a few legacy aliases; accept both forms.
    aliases = {
        "health_score": ("health_score", "health"),
        "open_pull_requests": ("open_pull_requests", "open_prs"),
        "recent_commits": ("recent_commits", "commits"),
    }
    for candidate in aliases.get(key, (key,)):
        value = row.get(candidate)
        if value is not None:
            try:
                return float(value or 0)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def _timestamp(row: Mapping[str, Any]) -> float:
    raw = str(row.get("captured_at", ""))
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError, OverflowError):
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


def _pct_change(previous: float, current: float) -> float:
    if abs(previous) < 1e-9:
        return 0.0 if abs(current) < 1e-9 else 100.0
    return (current - previous) / abs(previous) * 100.0


def _sigmoid(x: float) -> float:
    x = max(-20.0, min(20.0, x))
    return 1.0 / (1.0 + math.exp(-x))


def _severity(score: float) -> str:
    return "Critical" if score >= 75 else "High" if score >= 55 else "Moderate" if score >= 30 else "Low"


def _factor(name: str, score: float, trend: str, evidence: str, recommendation: str) -> RiskFactor:
    return RiskFactor(name, _severity(score), round(max(0.0, min(100.0, score)), 1), trend, evidence, recommendation)


def _build_factors(snapshots: Sequence[Mapping[str, Any]]) -> list[RiskFactor]:
    if not snapshots:
        return []
    recent = list(snapshots[:8])
    chronological = list(reversed(recent))
    latest = recent[0]
    factors: list[RiskFactor] = []

    health = [_num(x, "health_score") for x in chronological]
    activity = [_num(x, "recent_commits") for x in chronological]
    contributors = [_num(x, "contributors") for x in chronological]
    issues = [_num(x, "open_issues") for x in chronological]
    prs = [_num(x, "open_pull_requests") for x in chronological]
    testing = [_num(x, "testing_score") for x in chronological]
    docs = [_num(x, "documentation_score") for x in chronological]

    if len(health) >= 2:
        slope = _linear_slope(health)
        delta = health[-1] - health[0]
        score = min(100.0, max(0.0, (-slope) * 13 + max(0.0, -delta) * 0.35))
        if slope < -0.5:
            factors.append(_factor(
                "Health trajectory", score, "Declining",
                f"Health moved {delta:+.1f} points across the observed window ({slope:+.1f} points per snapshot).",
                "Prioritize the weakest health dimension and re-scan after the corrective change.",
            ))
        elif slope > 0.5:
            factors.append(_factor("Health trajectory", 5.0, "Improving", f"Health is improving at {slope:+.1f} points per snapshot.", "Preserve the current operating pattern and keep collecting snapshots."))

    if len(activity) >= 3:
        slope = _linear_slope(activity)
        pct = _pct_change(activity[0], activity[-1])
        score = min(100.0, max(0.0, (-slope) * 9 + max(0.0, -pct) * 0.25))
        if slope < -0.5:
            factors.append(_factor(
                "Development activity", score, "Declining",
                f"Recent commit activity has fallen {abs(pct):.0f}% across the observed snapshots.",
                "Check for stalled work, inactive maintainers, or blocked delivery paths before the slowdown compounds.",
            ))

    if len(contributors) >= 2:
        slope = _linear_slope(contributors)
        if slope < -0.2:
            score = min(100.0, 35 + abs(slope) * 20)
            factors.append(_factor(
                "Contributor breadth", score, "Contracting",
                f"Contributor breadth is trending down ({slope:+.1f} contributors per snapshot).",
                "Spread ownership, improve onboarding, and document critical repository knowledge.",
            ))

    latest_contributors = _num(latest, "contributors")
    if latest_contributors <= 1:
        factors.append(_factor(
            "Maintainer dependency", 82.0, "Concentrated",
            "The latest snapshot contains one or fewer measured contributors.",
            "Establish a second maintainer and document ownership of critical areas.",
        ))
    elif latest_contributors == 2:
        factors.append(_factor(
            "Maintainer dependency", 58.0, "Concentrated",
            "Only two contributors are represented in the latest snapshot.",
            "Reduce single-person ownership and build a broader maintainer path.",
        ))

    def pressure_factor(name: str, values: list[float], threshold: float, multiplier: float, recommendation: str):
        if len(values) < 3:
            return
        slope = _linear_slope(values)
        latest_value = values[-1]
        if slope > 0.2 and latest_value >= threshold:
            score = min(100.0, 30 + slope * multiplier + max(0.0, latest_value - threshold) * 1.2)
            factors.append(_factor(name, score, "Increasing", f"Open work is increasing ({slope:+.1f} items per snapshot) and is currently {latest_value:.0f}.", recommendation))

    pressure_factor("Issue pressure", issues, 10, 10, "Triage stale and blocked issues and keep the backlog from becoming a maintenance queue.")
    pressure_factor("Review pressure", prs, 6, 12, "Prioritize review throughput and identify PRs that are stale, blocked, or obsolete.")

    latest_testing = _num(latest, "testing_score")
    if latest_testing < 45:
        factors.append(_factor("Testing posture", 62.0, "Weak", f"The latest structural testing signal is {latest_testing:.0f}/100.", "Add or strengthen automated tests around the repository's highest-risk paths."))
    latest_docs = _num(latest, "documentation_score")
    if latest_docs < 50:
        factors.append(_factor("Documentation posture", 45.0, "Weak", f"The latest documentation signal is {latest_docs:.0f}/100.", "Improve onboarding and operational documentation before knowledge gaps become ownership risks."))

    return sorted(factors, key=lambda item: item.score, reverse=True)


def _trend_risk(snapshots: Sequence[Mapping[str, Any]]) -> tuple[float, list[str]]:
    factors = _build_factors(snapshots)
    if not factors:
        return 0.0, []
    # The highest factor matters most; additional independent signals add evidence
    # without allowing many correlated symptoms to inflate risk indefinitely.
    top = factors[0].score
    supporting = sum(f.score * 0.18 for f in factors[1:4])
    risk = min(100.0, top * 0.72 + supporting)
    evidence = [f"{f.name}: {f.evidence}" for f in factors[:4] if f.score >= 20]
    return risk, evidence


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


def _confidence(snapshot_count: int, factors: Sequence[RiskFactor]) -> str:
    if snapshot_count >= 16 and len(factors) >= 2:
        return "High"
    if snapshot_count >= 8 and factors:
        return "Medium"
    if snapshot_count >= 4:
        return "Low"
    return "Very low"


def predict_repository_risk(snapshots: Sequence[Mapping[str, Any]]) -> Prediction:
    """Estimate near-term maintenance risk from historical repository behaviour.

    The forecast is intentionally framed as a directional estimate. With enough
    sequential observations, a small supervised model supplements the explainable
    trend engine; otherwise the trend engine remains the primary signal.
    """
    ordered = sorted(snapshots, key=_timestamp, reverse=True)
    if not ordered:
        return Prediction("Insufficient data", 0.0, "None", "No history", "Next 30 days", [], ["Run repository scans over time to build a historical series."], [], "Collect more historical scans before acting on a forecast.")

    factors = _build_factors(ordered)
    trend_probability, evidence = _trend_risk(ordered)
    method = "Explainable trend model"
    probability = trend_probability
    horizon = "Next 30 days"
    limitations = [
        f"The forecast is based on {len(ordered)} persisted RepoPulse snapshots rather than external repository outcomes.",
        "Risk probability is a model estimate, not a statistical guarantee of future repository behaviour.",
        "Structural testing and engineering signals do not represent runtime test coverage or security vulnerability data.",
    ]

    if len(ordered) >= 10:
        rows = list(reversed(ordered))
        X, y = [], []
        for i in range(len(rows) - 1):
            X.append(_feature(rows[i]))
            y.append(1 if _num(rows[i + 1], "health_score") - _num(rows[i], "health_score") <= -8 else 0)
        if len(set(y)) >= 2:
            try:
                ml_probability = _logistic_probability(X, y, _feature(rows[-1]))
                probability = round(ml_probability * 0.65 + trend_probability * 0.35, 1)
                method = "Hybrid logistic + trend model"
                horizon = "Next observed scan / near-term"
                limitations.append("The supervised component is trained only on this repository's historical transitions, so it can be unstable with sparse or irregular sampling.")
            except (ValueError, OverflowError, ZeroDivisionError):
                pass

    probability = round(max(0.0, min(100.0, probability)), 1)
    label = "High" if probability >= 65 else "Moderate" if probability >= 35 else "Low"
    confidence = _confidence(len(ordered), factors)
    recommendation = factors[0].recommendation if factors else "Continue collecting snapshots; no dominant predictive risk signal is currently visible."
    return Prediction(label, probability, confidence, method, horizon, evidence, limitations, factors, recommendation)


def forecast_summary(snapshots: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(snapshots, key=_timestamp, reverse=True)
    prediction = predict_repository_risk(ordered)
    if not ordered:
        return {"prediction": prediction, "health_trend": 0.0, "activity_trend": 0.0, "snapshots": 0, "risk_timeline": [], "dimension_trends": {}}

    recent = ordered[:8]
    chronological = list(reversed(recent))
    health = [_num(x, "health_score") for x in chronological]
    activity = [_num(x, "recent_commits") for x in chronological]
    dimensions = {
        "Health": health,
        "Activity": [_num(x, "activity_score") for x in chronological],
        "Engineering": [_num(x, "engineering_score") for x in chronological],
        "Documentation": [_num(x, "documentation_score") for x in chronological],
        "Testing": [_num(x, "testing_score") for x in chronological],
    }
    dimension_trends = {name: round(_linear_slope(values), 2) for name, values in dimensions.items() if len(values) >= 2}

    timeline = []
    for idx in range(len(chronological)):
        history = chronological[: idx + 1]
        if len(history) < 2:
            risk_score = 0.0
        else:
            risk_score, _ = _trend_risk(list(reversed(history)))
        timeline.append({
            "captured_at": chronological[idx].get("captured_at", ""),
            "health_score": round(_num(chronological[idx], "health_score"), 1),
            "risk_score": round(risk_score, 1),
        })

    return {
        "prediction": prediction,
        "health_trend": round(_linear_slope(health), 2),
        "activity_trend": round(_linear_slope(activity), 2),
        "snapshots": len(ordered),
        "risk_timeline": timeline,
        "dimension_trends": dimension_trends,
    }
