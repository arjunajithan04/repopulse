from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st


def render_bar_chart(data: Dict[str, int], title: str = "Overview"):
    st.subheader(title)
    chart_data = list(data.items())
    if not chart_data:
        st.info("No chart data available.")
        return
    labels, values = zip(*chart_data)
    st.bar_chart({"value": values}, x=labels)


def render_line_chart(series: List[float], title: str = "Trend"):
    st.subheader(title)
    if not series:
        st.info("No trend data available.")
        return
    st.line_chart(series)
