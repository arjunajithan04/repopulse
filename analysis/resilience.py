from __future__ import annotations

from typing import Any


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 1)


def _delta(current: float, previous: float) -> float:
    return current - previous


def _state(health: float, momentum: float, concentration: float, bus_factor: float, activity: float) -> tuple[str, str]:
    if activity < 20 and health < 60:
        return "DORMANT", "Low observed development activity and weakened repository health."
    if concentration >= 70 or (bus_factor <= 1 and bus_factor > 0):
        return "MAINTAINER DEPENDENT", "A small contributor group carries a disproportionate share of observed activity."
    if momentum >= 65 and health >= 70:
        return "ACCELERATING", "Health and recent momentum are both moving in a positive direction."
    if momentum >= 55 and health >= 75:
        return "GROWING", "The repository is healthy with positive recent movement."
    if health < 60 or momentum < 35:
        return "UNDER PRESSURE", "Current health or recent momentum indicates elevated operational pressure."
    if momentum >= 55 and health < 75:
        return "RECOVERING", "Recent movement is positive, although the repository has not fully returned to a strong health state."
    return "STABLE", "Repository health and recent movement are comparatively steady."


def _momentum(snapshots: list[dict[str, Any]]) -> float:
    if len(snapshots) < 2:
        return 50.0
    ordered = sorted(snapshots, key=lambda x: str(x.get("captured_at", "")))
    recent = ordered[-1]
    previous = ordered[-2]
    health_delta = _delta(_num(recent.get("health_score")), _num(previous.get("health_score")))
    activity_delta = _delta(_num(recent.get("recent_commits")), _num(previous.get("recent_commits")))
    # Health is intentionally dominant; activity only nudges the direction.
    activity_component = 0.0 if _num(previous.get("recent_commits")) == 0 else max(-10.0, min(10.0, activity_delta / abs(_num(previous.get("recent_commits"))) * 10.0))
    return _clamp(50.0 + health_delta * 4.0 + activity_component)


def _resilience_score(metrics: dict[str, Any], snapshots: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    dimensions = metrics.get("health_dimensions", {}) or {}
    health = _num(metrics.get("repository_health_score"))
    activity = _num(dimensions.get("activity", metrics.get("activity_score")))
    maintenance = _num(dimensions.get("maintenance"))
    issue_health = _num(dimensions.get("issue_health"))
    pr_health = _num(dimensions.get("pr_health"))
    contributor_health = _num(dimensions.get("contributor_health"))
    concentration = _num(metrics.get("contributor_concentration"))
    bus_factor = _num(metrics.get("bus_factor"))

    breadth = _clamp(contributor_health)
    if concentration:
        concentration_resilience = _clamp(100.0 - concentration)
    else:
        concentration_resilience = breadth
    if bus_factor <= 0:
        bus_resilience = 45.0
    elif bus_factor == 1:
        bus_resilience = 30.0
    elif bus_factor == 2:
        bus_resilience = 55.0
    elif bus_factor == 3:
        bus_resilience = 75.0
    else:
        bus_resilience = 90.0

    momentum = _momentum(snapshots)
    factors = [
        ("Current health", _clamp(health), "A stronger baseline gives the repository more room to absorb disruption."),
        ("Contributor resilience", _clamp((breadth * 0.45) + (concentration_resilience * 0.35) + (bus_resilience * 0.20)), "Broader ownership and a larger bus factor reduce dependence on a small maintainer group."),
        ("Operational stability", _clamp((maintenance * 0.45) + (issue_health * 0.30) + (pr_health * 0.25)), "Maintenance recency and manageable issue/PR pressure improve resilience."),
        ("Development continuity", _clamp((activity * 0.65) + (momentum * 0.35)), "Sustained activity and positive recent movement support continuity."),
    ]
    score = _clamp(sum(value * weight for (_, value, _), weight in zip(factors, [0.30, 0.30, 0.20, 0.20])))
    return score, [{"name": name, "score": value, "detail": detail} for name, value, detail in factors]


def _recommendation(state: str, factors: list[dict[str, Any]], metrics: dict[str, Any]) -> tuple[str, str]:
    concentration = _num(metrics.get("contributor_concentration"))
    bus_factor = _num(metrics.get("bus_factor"))
    if concentration >= 60 or (0 < bus_factor <= 1):
        return "Broaden ownership", "Distribute issue and review ownership across secondary contributors to reduce maintainer dependency."
    weakest = min(factors, key=lambda item: item["score"])
    mapping = {
        "Current health": ("Stabilize repository health", "Address the highest-severity active signals before taking on additional change."),
        "Contributor resilience": ("Broaden contributor participation", "Create more independent paths for contributors to own issues, reviews and releases."),
        "Operational stability": ("Reduce operational pressure", "Prioritize unresolved issues and review backlog to restore operating headroom."),
        "Development continuity": ("Protect development momentum", "Investigate the recent activity slowdown and keep a sustainable delivery cadence."),
    }
    return mapping.get(weakest["name"], ("Maintain current trajectory", "Continue monitoring the repository's health and historical movement."))


def build_resilience_intelligence(metrics: dict[str, Any], snapshots: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    history = snapshots or []
    health = _num(metrics.get("repository_health_score"))
    activity = _num((metrics.get("health_dimensions", {}) or {}).get("activity", metrics.get("activity_score")))
    concentration = _num(metrics.get("contributor_concentration"))
    bus_factor = _num(metrics.get("bus_factor"))
    momentum = _momentum(history)
    resilience, factors = _resilience_score(metrics, history)
    state, state_reason = _state(health, momentum, concentration, bus_factor, activity)
    action, action_detail = _recommendation(state, factors, metrics)

    return {
        "state": state,
        "state_reason": state_reason,
        "health": _clamp(health),
        "momentum": _clamp(momentum),
        "resilience": resilience,
        "factors": factors,
        "recommendation": {"title": action, "detail": action_detail},
        "limitations": [
            "Resilience is an explainable RepoPulse heuristic, not a probability of failure.",
            "Scenario outputs estimate directional impact from observed signals; they are not forecasts of exact future values.",
            "Historical confidence depends on the number and consistency of stored repository snapshots.",
        ],
    }


def simulate_scenario(metrics: dict[str, Any], scenario: str) -> dict[str, Any]:
    """Estimate directional resilience impact without claiming a causal prediction."""
    base = build_resilience_intelligence(metrics, [])
    health = base["health"]
    resilience = base["resilience"]
    concentration = _num(metrics.get("contributor_concentration"))
    bus_factor = _num(metrics.get("bus_factor"))
    issues = _num(metrics.get("open_issue_count"))

    if scenario == "maintainer_inactive":
        impact = 18 + (18 if concentration >= 60 else 8) + (10 if bus_factor <= 1 and bus_factor > 0 else 0)
        label = "Primary maintainer unavailable"
        detail = "Tests how much resilience is exposed to concentrated ownership."
    elif scenario == "issue_pressure":
        impact = 10 + (8 if issues >= 20 else 0)
        label = "Issue backlog increases 25%"
        detail = "Tests the repository's operating headroom under additional issue pressure."
    elif scenario == "broaden_ownership":
        impact = 12 + (8 if concentration >= 50 else 4)
        label = "Ownership broadens"
        detail = "Models a healthier distribution of contributor participation."
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    if scenario == "broaden_ownership":
        projected_resilience = _clamp(resilience + impact)
        projected_health = _clamp(health + impact * 0.35)
        direction = "positive"
    else:
        projected_resilience = _clamp(resilience - impact)
        projected_health = _clamp(health - impact * 0.45)
        direction = "negative"

    if projected_resilience >= 70:
        projected_state = "RESILIENT"
    elif projected_resilience >= 50:
        projected_state = "MODERATE"
    else:
        projected_state = "FRAGILE"

    return {
        "label": label,
        "detail": detail,
        "direction": direction,
        "base_resilience": resilience,
        "projected_resilience": projected_resilience,
        "base_health": health,
        "projected_health": projected_health,
        "projected_state": projected_state,
    }
