from __future__ import annotations

import streamlit as st


def metric_card(title: str, value: str, delta: str | None = None, help_text: str | None = None, variant: str = "neutral"):
    delta_class = {
        "good": "good",
        "bad": "bad",
        "neutral": "neutral",
    }.get(variant, "neutral")

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta {delta_class}">{delta}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
