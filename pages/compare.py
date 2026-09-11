from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis.intelligence import compare_snapshots


def compare_page():
    snapshots = st.session_state.get("repo_snapshots", {})
    repos = list(snapshots.keys())
    st.subheader("Repository Comparison", divider="blue")
    st.caption("Compare repositories using the same health, activity, engineering, and backlog signals.")
    if len(repos) < 2:
        st.info("Analyze at least two repositories in this session to unlock comparison.")
        return

    c1, c2 = st.columns(2)
    with c1:
        a_name = st.selectbox("Repository A", repos, key="phase4_compare_a")
    with c2:
        b_name = st.selectbox("Repository B", repos, index=min(1, len(repos) - 1), key="phase4_compare_b")
    if a_name == b_name:
        st.warning("Choose two different repositories.")
        return

    result = compare_snapshots(a_name, snapshots[a_name], b_name, snapshots[b_name])
    winner = result["winner"]
    if winner == "Tie":
        st.info("The repositories are balanced across the selected signals.")
    else:
        st.success(f"🏆 {winner} leads across more of the selected signals.")

    x, y = st.columns(2)
    x.metric(a_name, f"{result['scores'][a_name]} leads")
    y.metric(b_name, f"{result['scores'][b_name]} leads")
    st.dataframe(pd.DataFrame(result["rows"]), use_container_width=True, hide_index=True)
    st.caption("Stars, forks, contributors, health, engineering, documentation, testing, and recent commits reward higher values. Open issues and PRs reward lower backlogs.")
