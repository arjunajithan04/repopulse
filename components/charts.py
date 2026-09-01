from __future__ import annotations

from typing import Dict, List

import pandas as pd
import streamlit as st


def render_bar_chart(data: Dict[str, int], title: str = "Overview"):
    st.subheader(title)

    # Check whether there is any data to display
    if not data:
        st.info("No chart data available.")
        return

    # Convert the dictionary into a DataFrame
    chart_data = pd.DataFrame(
        {
            "Metric": list(data.keys()),
            "Value": list(data.values()),
        }
    )

    # Create the bar chart
    st.bar_chart(
        chart_data,
        x="Metric",
        y="Value",
    )


def render_line_chart(series: List[float], title: str = "Trend"):
    st.subheader(title)

    # Check whether there is any data to display
    if not series:
        st.info("No trend data available.")
        return

    # Create the line chart
    st.line_chart(series)