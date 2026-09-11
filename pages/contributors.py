from __future__ import annotations

import pandas as pd
import streamlit as st


def _score(person: dict) -> float:
    return round(person["commits"] + person["prs"] * 3 + person["issues"] * 1.5, 1)


def contributors_page():
    st.subheader("Contributor intelligence", divider="green")
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate contributor insights.")
        return

    people = []
    for c in analysis.contributors:
        person = {
            "name": c.login,
            "commits": int(c.commits or 0),
            "prs": int(c.pull_requests or 0),
            "issues": int(c.issues or 0),
            "avatar": c.avatar_url,
        }
        person["score"] = _score(person)
        people.append(person)
    people.sort(key=lambda x: x["score"], reverse=True)
    if not people:
        st.info("No contributor data was returned for this repository.")
        return

    total_score = sum(p["score"] for p in people)
    top_share = (people[0]["score"] / total_score * 100) if total_score else 0
    bus_factor = int(analysis.metrics.get("bus_factor", 0) or 0)

    a, b, c, d = st.columns(4)
    a.metric("Contributors", len(people))
    b.metric("Top contributor", people[0]["name"])
    c.metric("Top contribution share", f"{top_share:.1f}%")
    d.metric("Bus factor", bus_factor or "—")

    if bus_factor <= 1:
        st.error("High concentration risk — one contributor represents at least half of the weighted contribution volume.")
    elif bus_factor <= 3:
        st.warning("Moderate concentration — a small group carries a large share of the repository's contribution volume.")
    else:
        st.success("Contribution is relatively distributed across the visible contributor set.")

    st.markdown("### Contributor leaderboard")
    rows = []
    for rank, p in enumerate(people, 1):
        rows.append({"Rank": rank, "Contributor": p["name"], "Commits": p["commits"], "PRs": p["prs"], "Issues": p["issues"], "Contribution score": p["score"], "Share": f"{(p['score'] / total_score * 100) if total_score else 0:.1f}%"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### Contribution distribution")
    chart_df = pd.DataFrame({"Contributor": [p["name"] for p in people[:10]], "Score": [p["score"] for p in people[:10]]})
    st.bar_chart(chart_df, x="Contributor", y="Score")

    st.markdown("### Contributor explorer")
    selected = st.selectbox("Select a contributor", [p["name"] for p in people])
    person = next(p for p in people if p["name"] == selected)
    x, y, z = st.columns(3)
    x.metric("Commits", person["commits"])
    y.metric("Pull requests", person["prs"])
    z.metric("Issues opened", person["issues"])
    st.caption("Contribution score is a RepoPulse analytical index: commits × 1 + pull requests × 3 + issues × 1.5. It is intended for relative comparison, not as an official GitHub score.")
