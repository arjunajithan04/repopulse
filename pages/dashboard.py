from __future__ import annotations

import streamlit as st

from components.cards import metric_card
from components.charts import render_bar_chart


def dashboard_page():
    st.subheader("Repository Dashboard")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Stars", "1.2K", "+18%", "Repository stars over time")
    with col2:
        metric_card("Forks", "432", "+9%", "Fork activity")
    with col3:
        metric_card("Issues", "27", "-4%", "Open issue count")
    with col4:
        metric_card("Health", "92/100", "+3", "Repository health score")

    st.write("---")
    render_bar_chart({"Stars": 1200, "Forks": 432, "Issues": 27, "Watchers": 980}, title="Summary Metrics")
