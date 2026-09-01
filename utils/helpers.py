from __future__ import annotations

from typing import Any, Dict, Iterable


def safe_get(mapping: Dict[str, Any], key: str, default: Any = None) -> Any:
    return mapping.get(key, default)


def format_number(value: int | float) -> str:
    if value >= 1000000:
        return f"{value / 1000000:.1f}M"
    if value >= 1000:
        return f"{value / 1000:.1f}K"
    return str(int(value))


def to_percent(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100
