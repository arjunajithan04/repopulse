from __future__ import annotations

import streamlit as st

from components.cards import metric_card
from components.charts import render_bar_chart


def dashboard_page():
    st.subheader("Executive overview", divider="violet")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate the executive overview.")
        return

    repo = analysis.repository
    metrics = analysis.metrics

    stars = repo.stars or 0
    forks = repo.forks or 0
    open_issues = metrics.get("open_issue_count", 0)
    health_score = metrics.get("repository_health_score", 0)
    total_contributors = metrics.get("total_contributors", 0)

    stars_str = f"{stars // 1000}K" if stars >= 1000 else str(stars)
    forks_str = f"{forks // 1000}K" if forks >= 1000 else str(forks)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Stars", stars_str, f"+{total_contributors}%", f"Repository popularity", variant="good")
    with col2:
        metric_card("Forks", forks_str, "+9.4%", "Development activity", variant="neutral")
    with col3:
        metric_card("Issues", str(open_issues), "-4.8%", "Open issue count", variant="bad" if open_issues > 20 else "good")
    with col4:
        metric_card("Health", f"{health_score}/100", "+3.1", "Repository health score", variant="good" if health_score >= 80 else "neutral")

    st.write("")
    chart_data = {
        "Stars": stars,
        "Forks": forks,
        "Issues": open_issues,
        "Contributors": total_contributors,
    }
    render_bar_chart(chart_data, title="Summary metrics")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("### Highlights")
        highlights = []
        if stars >= 1000:
            highlights.append("- Strong community traction and adoption")
        if open_issues < 50:
            highlights.append("- Stable issue resolution trend")
        if total_contributors >= 10:
            highlights.append("- Consistent contributor velocity")
        if health_score >= 80:
            highlights.append("- Excellent repository health score")
        highlights_text = "\n".join(highlights) if highlights else "- Repository is being actively maintained"
        st.markdown(highlights_text)
    with col_right:
        st.markdown("### Trend note")
        repo_name = repo.full_name or repo.name
        trend_text = f"**{repo_name}** shows "
        if health_score >= 80:
            trend_text += "healthy growth with strong community engagement and well-managed issues."
        elif open_issues > 50:
            trend_text += "active development with manageable issue pressure."
        else:
            trend_text += "steady momentum with consistent contributor participation."
        st.markdown(trend_text)
