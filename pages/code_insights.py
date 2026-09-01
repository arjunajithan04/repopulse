from __future__ import annotations

import streamlit as st


def code_insights_page():
    st.subheader("Code insights", divider="orange")

    files = [
        {"File": "app.py", "Lines": 120, "Complexity": 22},
        {"File": "core/github_client.py", "Lines": 200, "Complexity": 34},
        {"File": "analysis/metrics.py", "Lines": 150, "Complexity": 18},
    ]

    st.dataframe(files, use_container_width=True)

    st.markdown("### Quality signals")
    st.markdown(
        "- Maintainability remains high across the core modules\n"
        "- Complexity remains within a safe operating range\n"
        "- The architecture is modular and easy to extend"
    )
