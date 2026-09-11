from __future__ import annotations

import html
import streamlit as st


def metric_card(title: str, value: str, delta: str | None = None, help_text: str | None = None, variant: str = "neutral", icon: str = "•"):
    delta_class = {"good": "good", "bad": "bad", "neutral": "neutral"}.get(variant, "neutral")
    delta_text = delta or "No change"
    st.markdown(
        f"""
        <div class="metric-card rp-metric">
            <div class="metric-top"><div class="metric-label">{html.escape(str(title))}</div><div class="metric-icon">{html.escape(icon)}</div></div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-delta {delta_class}">{html.escape(str(delta_text))}</div>
            <div class="metric-help">{html.escape(str(help_text or ''))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(label: str, tone: str = "neutral"):
    safe_tone = tone if tone in {"good", "warning", "danger", "neutral"} else "neutral"
    st.markdown(f'<span class="status-badge {safe_tone}"><span class="status-dot"></span>{html.escape(label)}</span>', unsafe_allow_html=True)
