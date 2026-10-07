from __future__ import annotations

from typing import Any, Mapping


HEALTH_WEIGHTS = {
    "activity": 0.20,
    "community": 0.10,
    "maintenance": 0.20,
    "issue_health": 0.15,
    "pr_health": 0.15,
    "contributor_health": 0.20,
}

LABELS = {
    "activity": "Activity",
    "community": "Community",
    "maintenance": "Maintenance",
    "issue_health": "Issue health",
    "pr_health": "PR health",
    "contributor_health": "Contributor health",
}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _delta(current: float, previous: float) -> float:
    return current - previous


def _pct(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / abs(previous) * 100.0


def _direction(delta: float) -> str:
    if delta > 0.05:
        return "up"
    if delta < -0.05:
        return "down"
    return "flat"


def _dimension_driver(label: str, current: float, previous: float, weight: float) -> dict[str, Any]:
    delta = _delta(current, previous)
    # This is attribution within the RepoPulse health formula, not causal inference.
    weighted = delta * weight
    direction = _direction(delta)
    if label == "Activity":
        if direction == "down":
            detail = "The activity component weakened and pulled the composite health signal downward."
            action = "Investigate the recent delivery slowdown and whether work is blocked or intentionally paused."
        else:
            detail = "Recent development activity strengthened the composite health signal."
            action = "Protect the current delivery cadence and avoid concentrating work on a single contributor."
    elif label == "Maintenance":
        if direction == "down":
            detail = "Maintenance quality weakened, reducing the repository's operating headroom."
            action = "Prioritize stale maintenance work and restore a predictable upkeep cadence."
        else:
            detail = "Maintenance quality improved and provided a stronger operating baseline."
            action = "Preserve the maintenance cadence that is keeping the repository stable."
    elif label == "Issue health":
        if direction == "down":
            detail = "Issue health deteriorated, indicating more pressure in the open-work queue."
            action = "Triage the highest-impact open issues and remove stale or blocked work."
        else:
            detail = "Issue health improved, reducing backlog pressure on the repository."
            action = "Keep issue triage current so backlog pressure does not rebuild."
    elif label == "PR health":
        if direction == "down":
            detail = "PR health weakened, suggesting increasing review or merge pressure."
            action = "Reduce review latency and identify blocked or obsolete pull requests."
        else:
            detail = "PR health improved, reducing review and merge pressure."
            action = "Maintain review responsiveness and distribute review ownership."
    elif label == "Contributor health":
        if direction == "down":
            detail = "Contributor health weakened, making the repository more exposed to ownership concentration."
            action = "Broaden issue, review and release ownership across additional contributors."
        else:
            detail = "Contributor health improved, increasing the breadth of the active contributor base."
            action = "Keep creating independent contribution paths for secondary contributors."
    else:
        if direction == "down":
            detail = "Community health weakened and reduced the composite score."
            action = "Strengthen contributor participation and repository discoverability."
        else:
            detail = "Community health improved and supported the composite score."
            action = "Continue encouraging broad community participation."

    return {
        "type": "dimension",
        "name": label,
        "current": round(current, 1),
        "previous": round(previous, 1),
        "delta": round(delta, 1),
        "pct": _pct(current, previous),
        "weighted_impact": round(weighted, 2),
        "direction": direction,
        "detail": detail,
        "action": action,
    }


def _telemetry_driver(name: str, current: float, previous: float, inverse: bool, detail_up: str, detail_down: str) -> dict[str, Any]:
    delta = _delta(current, previous)
    direction = _direction(delta)
    improved = (delta < 0) if inverse else (delta > 0)
    if direction == "flat":
        detail = f"{name} was effectively unchanged between the two snapshots."
    elif improved:
        detail = detail_up
    else:
        detail = detail_down
    return {
        "type": "telemetry",
        "name": name,
        "current": round(current, 1),
        "previous": round(previous, 1),
        "delta": round(delta, 1),
        "pct": _pct(current, previous),
        "direction": direction,
        "improved": improved if direction != "flat" else None,
        "detail": detail,
    }


def build_change_explanation(metrics: Mapping[str, Any], previous: Mapping[str, Any] | None) -> dict[str, Any]:
    """Explain a health movement using RepoPulse's measured score composition.

    This is attribution within the existing health model, supported by adjacent
    repository telemetry. It intentionally does not claim that a single metric
    caused the repository's observed change.
    """
    current_health = _num(metrics.get("repository_health_score"))
    previous_health = _num(previous.get("health_score", previous.get("health", 0))) if previous else 0.0
    health_delta = _delta(current_health, previous_health)

    if not previous:
        return {
            "available": False,
            "health_delta": None,
            "headline": "A second snapshot is needed to explain movement.",
            "drivers": [],
            "telemetry": [],
            "implication": "Re-scan this repository to establish a comparison point for causal-style change analysis.",
            "action": "Build another historical snapshot before interpreting movement.",
            "basis": "No previous snapshot is available.",
        }

    current_dims = metrics.get("health_dimensions", {}) or {}
    previous_dims = previous.get("health_dimensions", {}) or {}
    drivers: list[dict[str, Any]] = []
    for key, weight in HEALTH_WEIGHTS.items():
        if key not in current_dims and key not in previous_dims:
            continue
        current = _num(current_dims.get(key))
        old = _num(previous_dims.get(key))
        if abs(current - old) > 0.05:
            drivers.append(_dimension_driver(LABELS[key], current, old, weight))

    drivers.sort(key=lambda item: abs(item["weighted_impact"]), reverse=True)

    telemetry = []
    telemetry_specs = [
        ("Recent commits", "commits", False,
         "Development activity increased alongside the health movement.",
         "Development activity decreased alongside the health movement."),
        ("Contributors", "contributors", False,
         "The observed contributor base expanded.",
         "The observed contributor base contracted."),
        ("Open issues", "issues", True,
         "Open-issue pressure decreased.",
         "Open-issue pressure increased."),
        ("Open PRs", "pull_requests", True,
         "Open-PR pressure decreased.",
         "Open-PR pressure increased."),
    ]
    current_telemetry = {
        "commits": _num(metrics.get("recent_commit_count")),
        "contributors": _num(metrics.get("total_contributors")),
        "issues": _num(metrics.get("open_issue_count")),
        "pull_requests": _num(metrics.get("open_pull_request_count")),
    }
    for name, key, inverse, up, down in telemetry_specs:
        if key not in previous:
            continue
        old = _num(previous.get(key, 0))
        cur = current_telemetry[key]
        if abs(cur - old) > 0.05:
            telemetry.append(_telemetry_driver(name, cur, old, inverse, up, down))

    positive = [d for d in drivers if d["weighted_impact"] > 0.05]
    negative = [d for d in drivers if d["weighted_impact"] < -0.05]

    if health_delta > 0.5:
        headline = f"Health improved by {health_delta:.1f} points."
    elif health_delta < -0.5:
        headline = f"Health declined by {abs(health_delta):.1f} points."
    else:
        headline = "Health was broadly stable between the two snapshots."

    if negative:
        top = negative[:2]
        names = " and ".join(item["name"] for item in top)
        implication = f"The strongest measured downward contributors were {names}."
        action = top[0]["action"]
    elif positive:
        top = positive[:2]
        names = " and ".join(item["name"] for item in top)
        implication = f"The strongest measured improvements came from {names}."
        action = top[0]["action"]
    elif telemetry:
        implication = "The composite health score moved, but the stored dimension breakdown does not show a strong single driver."
        action = "Inspect the detailed health dimensions and re-scan to establish a clearer movement pattern."
    else:
        implication = "The stored health dimensions were effectively unchanged."
        action = "Continue monitoring historical movement rather than reacting to a negligible change."

    if health_delta < -0.5 and negative:
        direction_note = "These signals are the strongest measurable contributors within the current RepoPulse scoring model; they are not proof of causation."
    elif health_delta > 0.5 and positive:
        direction_note = "These signals are the strongest measurable contributors within the current RepoPulse scoring model; they are not proof of causation."
    else:
        direction_note = "RepoPulse attributes movement to changes in its measured score components; external causes are not observable from repository telemetry alone."

    return {
        "available": True,
        "health_delta": round(health_delta, 1),
        "headline": headline,
        "drivers": drivers[:4],
        "telemetry": telemetry[:4],
        "implication": implication,
        "action": action,
        "basis": direction_note,
        "positive_drivers": positive[:3],
        "negative_drivers": negative[:3],
    }
