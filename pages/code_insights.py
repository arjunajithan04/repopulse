from __future__ import annotations

import streamlit as st


def code_insights_page():
    st.subheader("Code Insights")
    files = [
        {"File": "app.py", "Lines": 120, "Complexity": 22},
        {"File": "core/github_client.py", "Lines": 200, "Complexity": 34},
        {"File": "analysis/metrics.py", "Lines": 150, "Complexity": 18},
    ]
    st.dataframe(files)
