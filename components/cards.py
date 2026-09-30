from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def metric_card(
    title: str,
    value: str,
    delta: str | None = None,
    help_text: str | None = None,
    variant: str = "neutral",
    icon: str = "•",
    progress: float | None = None,
    trend: Iterable[float] | None = None,
):
    delta_class = {"good": "good", "bad": "bad", "neutral": "neutral"}.get(variant, "neutral")
    delta_text = delta or "No change"
    safe_progress = max(0.0, min(100.0, float(progress))) if progress is not None else None

    progress_html = ""
    if safe_progress is not None:
        progress_html = (
            '<div class="metric-progress"><span style="width:'
            f'{safe_progress:.1f}%"></span></div>'
        )

    spark_html = ""
    values = list(trend or [])
    if len(values) >= 2:
        low, high = min(values), max(values)
        span = high - low or 1
        points = []
        for idx, value in enumerate(values):
            x = idx / (len(values) - 1) * 100
            y = 22 - ((value - low) / span * 18)
            points.append(f"{x:.1f},{y:.1f}")
        spark_html = f'<svg class="metric-spark" viewBox="0 0 100 24" preserveAspectRatio="none" aria-hidden="true"><polyline points="{" ".join(points)}" /></svg>'

    st.html(
        f"""
        <div class="metric-card rp-metric {html.escape(delta_class)}">
            <div class="metric-top">
                <div class="metric-label">{html.escape(str(title))}</div>
                <div class="metric-icon">{html.escape(icon)}</div>
            </div>
            <div class="metric-value-row">
                <div class="metric-value">{html.escape(str(value))}</div>
                {spark_html}
            </div>
            <div class="metric-delta {delta_class}">{html.escape(str(delta_text))}</div>
            {progress_html}
            <div class="metric-help">{html.escape(str(help_text or ""))}</div>
        </div>
        """
    )


def status_badge(label: str, tone: str = "neutral"):
    safe_tone = tone if tone in {"good", "warning", "danger", "neutral"} else "neutral"
    st.html(
        f'<span class="status-badge {safe_tone}"><span class="status-dot"></span>{html.escape(label)}</span>'
    )
