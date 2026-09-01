from __future__ import annotations

import streamlit as st


def repository_page():
    st.subheader("Repository Overview")
    owner = st.text_input("GitHub owner", value="microsoft")
    repo = st.text_input("Repository name", value="vscode")

    if st.button("Analyze repository"):
        st.success(f"Analyzing {owner}/{repo}...")
        st.info("This is a starter template for live GitHub API integration.")
