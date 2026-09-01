from __future__ import annotations

import streamlit as st


def repository_page():
    st.subheader("Repository overview", divider="blue")

    col1, col2 = st.columns(2)
    with col1:
        owner = st.text_input("GitHub owner", value="microsoft")
    with col2:
        repo = st.text_input("Repository name", value="vscode")

    if st.button("Analyze repository"):
        st.success(f"Analyzing {owner}/{repo}...")
        st.info("This is a starter template for live GitHub API integration.")

    st.markdown("### Repository snapshot")
    st.markdown(
        """
        | Field | Value |
        |---|---|
        | Owner | microsoft |
        | Repository | vscode |
        | Default branch | main |
        | Visibility | Public |
        | Primary language | TypeScript |
        """
    )
