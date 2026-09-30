from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


def _tone(value: str) -> str:
    return value if value in {"good", "warning", "danger", "neutral"} else "neutral"


def render_health_orb(score: float, status: str, delta: float | None = None):
    safe_score = max(0.0, min(100.0, float(score)))
    tone = "good" if safe_score >= 80 else "warning" if safe_score >= 60 else "danger"
    circumference = 339.3
    dash = circumference * safe_score / 100
    delta_html = "Baseline scan" if delta is None else f"{delta:+.1f} pts since last scan"
    st.html(
        f"""
        <div class="health-orb-card">
            <div class="health-orb-glow {tone}"></div>
            <svg class="health-orb" viewBox="0 0 128 128" role="img" aria-label="Health score {safe_score:.0f} out of 100">
                <circle class="orb-track" cx="64" cy="64" r="54" fill="none"></circle>
                <circle class="orb-value {tone}" cx="64" cy="64" r="54" fill="none" stroke-dasharray="{dash:.1f} {circumference:.1f}"></circle>
            </svg>
            <div class="health-orb-content">
                <div class="health-orb-score">{safe_score:.0f}</div>
                <div class="health-orb-label">HEALTH / 100</div>
                <div class="health-orb-status {tone}"><span class="status-dot"></span>{html.escape(status)}</div>
            </div>
            <div class="health-orb-delta">{html.escape(delta_html)}</div>
        </div>
        """,
    )


def render_spotlight(title: str, body: str, detail: str = "", tone: str = "neutral", eyebrow: str = "Repo spotlight"):
    safe_tone = _tone(tone)
    detail_html = f'<div class="cinematic-detail">{html.escape(str(detail))}</div>' if detail else ""
    st.html(
        f"""
        <div class="cinematic-spotlight {safe_tone}">
            <div class="spotlight-orbit"></div>
            <div class="cinematic-kicker">✦ {html.escape(eyebrow)}</div>
            <div class="cinematic-title">{html.escape(title)}</div>
            <div class="cinematic-body">{html.escape(body)}</div>
            {detail_html}
        </div>
        """,
    )


def render_telemetry_strip(items: Iterable[tuple[str, str, str]]):
    blocks = []
    for label, value, tone in items:
        safe_tone = _tone(tone)
        blocks.append(
            f'<div class="telemetry-item"><span class="telemetry-label">{html.escape(label)}</span><span class="telemetry-value {safe_tone}">{html.escape(value)}</span></div>'
        )
    st.html(f'<div class="telemetry-strip">{"".join(blocks)}</div>')
