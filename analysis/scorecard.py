from __future__ import annotations

from typing import Any


def _clamp(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 1)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _tone(score: float) -> str:
    if score >= 80:
        return "good"
    if score >= 60:
        return "warning"
    return "danger"


def build_scorecard(metrics: dict[str, Any], snapshots: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build an executive repository scorecard from already-observed RepoPulse signals.

    This layer intentionally does not create new engineering measurements. It translates
    existing health dimensions and stored history into a small, decision-oriented view.
    """
    dimensions = metrics.get("health_dimensions", {}) or {}
    activity = _clamp(_num(dimensions.get("activity", metrics.get("activity_score", 0))))
    community = _clamp((
        _num(dimensions.get("community", 0)) + _num(dimensions.get("contributor_health", 0))
    ) / 2)
    stability = _clamp((
        _num(dimensions.get("maintenance", 0)) * 0.45
        + _num(dimensions.get("issue_health", 0)) * 0.30
        + _num(dimensions.get("pr_health", 0)) * 0.25
    ))
    health = _clamp(_num(metrics.get("repository_health_score", 0)))

    ordered = sorted(snapshots or [], key=lambda item: str(item.get("captured_at", "")))
    momentum = 50.0
    momentum_note = "Baseline — historical movement is not available yet."
    if len(ordered) >= 2:
        previous = _num(ordered[-2].get("health_score"))
        current = _num(ordered[-1].get("health_score"))
        delta = current - previous
        # 10 health points of movement maps to the full 0–100 momentum span.
        momentum = _clamp(50.0 + delta * 5.0)
        if delta > 0:
            momentum_note = f"Health is moving upward by {delta:.1f} points since the previous scan."
        elif delta < 0:
            momentum_note = f"Health is moving downward by {abs(delta):.1f} points since the previous scan."
        else:
            momentum_note = "Health is unchanged since the previous scan."

    cards = {
        "Health": health,
        "Activity": activity,
        "Community": community,
        "Stability": stability,
        "Momentum": momentum,
    }

    dimension_labels = {
        "activity": "Activity",
        "community": "Community",
        "maintenance": "Maintenance",
        "issue_health": "Issue health",
        "pr_health": "PR health",
        "contributor_health": "Contributor health",
    }
    dimension_values = {
        label: _clamp(_num(dimensions.get(key))) for key, label in dimension_labels.items()
    }
    weakest = min(dimension_values, key=dimension_values.get) if dimension_values else "Activity"
    strongest = max(dimension_values, key=dimension_values.get) if dimension_values else "Activity"

    return {
        "status": "HEALTHY" if health >= 80 else "MODERATE" if health >= 60 else "AT RISK",
        "tone": _tone(health),
        "cards": cards,
        "tones": {key: _tone(value) for key, value in cards.items()},
        "strongest_dimension": strongest,
        "weakest_dimension": weakest,
        "dimension_values": dimension_values,
        "momentum_note": momentum_note,
        "history_available": len(ordered) >= 2,
    }
