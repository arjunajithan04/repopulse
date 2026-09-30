from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts import render_grouped_comparison
from components.ui import empty_state, page_header, section_header
from analysis.intelligence import compare_snapshots


def compare_page():
    snapshots = st.session_state.get("repo_snapshots", {})
    repos = list(snapshots.keys())
    page_header("Intelligence", "Repository comparison", "Compare measured health, engineering, activity, and backlog signals side by side.")
    if len(repos) < 2:
        empty_state("Comparison needs two repositories", "Analyze at least two repositories in this session to unlock the comparison workspace.", "⇄")
        return

    c1, c2 = st.columns(2)
    with c1:
        a_name = st.selectbox("Repository A", repos, key="phase2_compare_a")
    with c2:
        b_name = st.selectbox("Repository B", repos, index=min(1, len(repos) - 1), key="phase2_compare_b")
    if a_name == b_name:
        st.warning("Choose two different repositories.")
        return

    result = compare_snapshots(a_name, snapshots[a_name], b_name, snapshots[b_name])
    rows = pd.DataFrame(result["rows"])

    section_header("Comparison radar", "Explore the same metrics as a visual profile before drilling into the table.", "Side-by-side intelligence")
    metric_mode = st.selectbox("Metric group", ["Core health", "Community", "Engineering & backlog"], label_visibility="collapsed")
    groups = {
        "Core health": ["Health", "Engineering", "Documentation", "Testing"],
        "Community": ["Stars", "Forks", "Contributors", "Recent commits"],
        "Engineering & backlog": ["Engineering", "Documentation", "Testing", "Open issues", "Open PRs"],
    }
    selected_metrics = groups[metric_mode]
    filtered = rows[rows["Metric"].isin(selected_metrics)].copy()
    # Normalize each selected metric to a 0-100 visual index so very different scales remain readable.
    normalized = filtered.copy()
    for col in [a_name, b_name]:
        normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)
    for idx in normalized.index:
        values = [normalized.at[idx, a_name], normalized.at[idx, b_name]]
        lo, hi = min(values), max(values)
        for col in [a_name, b_name]:
            normalized.at[idx, col] = 50 if hi == lo else (normalized.at[idx, col] - lo) / (hi - lo) * 100
    render_grouped_comparison(normalized, [a_name, b_name])
    st.caption("The comparison chart uses a per-metric 0–100 index for visual readability. Raw measured values are shown below.")

    a, b = st.columns(2)
    a.metric(a_name, f"{result['scores'][a_name]} metric leads")
    b.metric(b_name, f"{result['scores'][b_name]} metric leads")

    section_header("Raw comparison", "Measured values without visual normalization.")
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("Open issues and open PRs are interpreted as lower-is-better in the existing comparison heuristic; other selected signals reward higher values. The metric-lead count is a comparison aid, not an overall repository quality score.")
