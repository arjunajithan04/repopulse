from __future__ import annotations

import streamlit as st


def contributors_page():
    st.subheader("Contributors")
    sample_data = [
        {"Contributor": "alice", "Commits": 142, "PRs": 22, "Reviews": 18},
        {"Contributor": "bob", "Commits": 98, "PRs": 19, "Reviews": 12},
        {"Contributor": "charlie", "Commits": 76, "PRs": 11, "Reviews": 20},
    ]
    st.dataframe(sample_data)
