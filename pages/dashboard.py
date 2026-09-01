from __future__ import annotations

import streamlit as st

from components.cards import metric_card
from components.charts import render_bar_chart


def dashboard_page():
    st.subheader("Repository dashboard", divider="violet")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Stars", "1.2K", "+18.2%", "Repository stars over time", variant="good")
    with col2:
        metric_card("Forks", "432", "+9.4%", "Development activity", variant="neutral")
    with col3:
        metric_card("Issues", "27", "-4.8%", "Open issue count", variant="bad")
    with col4:
        metric_card("Health", "92/100", "+3.1", "Repository health score", variant="good")

    st.write("")
    render_bar_chart({"Stars": 1200, "Forks": 432, "Issues": 27, "Watchers": 980}, title="Summary metrics")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### Highlights")
        st.markdown(
            "- Strong adoption and community engagement\n"
            "- Stable issue trend with declining backlog\n"
            "- High code health score and contributor momentum"
        )
    with col_right:
        st.markdown("### Trend note")
        st.markdown(
            "The repo continues to show healthy growth in stars and forks while maintaining a balanced issue profile."
        )
