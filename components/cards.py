from __future__ import annotations

import streamlit as st


def metric_card(title: str, value: str, delta: str | None = None, help_text: str | None = None):
    st.metric(label=title, value=value, delta=delta, help=help_text)
