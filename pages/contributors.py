from __future__ import annotations

import pandas as pd
import streamlit as st

from components.interaction import get_focus, set_focus

try:
    import plotly.express as px
except ImportError:  # pragma: no cover
    px = None


def _score(person: dict) -> float:
    return round(person["commits"] + person["prs"] * 3 + person["issues"] * 1.5, 1)


def _activity_matrix(people: list[dict]) -> pd.DataFrame:
    rows = []
    for p in people[:12]:
        rows.append({
            "Contributor": p["name"],
            "Contributions": p["commits"],
            "Pull requests": p["prs"],
            "Issues": p["issues"],
        })
    return pd.DataFrame(rows).set_index("Contributor")


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
    active = int(analysis.metrics.get("active_contributors", len(people)) or 0)

    a, b, c, d = st.columns(4)
    a.metric("Contributors", len(people))
    b.metric("Active", active)
    c.metric("Top share", f"{top_share:.1f}%")
    d.metric("Bus factor", bus_factor or "—")

    if bus_factor <= 1:
        st.error("High concentration risk — one contributor accounts for at least half of the visible contribution volume.")
    elif bus_factor <= 3:
        st.warning("Moderate concentration — a small group carries a large share of contribution volume.")
    else:
        st.success("Contribution is relatively distributed across the visible contributor set.")

    st.markdown("### Contributor leaderboard")
    search = st.text_input("Search contributors", placeholder="Filter by GitHub username…")
    filtered = [p for p in people if search.lower() in p["name"].lower()]
    rows = []
    for rank, p in enumerate(filtered, 1):
        share = (p["score"] / total_score * 100) if total_score else 0
        rows.append({"Rank": rank, "Contributor": p["name"], "Commits": p["commits"], "PRs": p["prs"], "Issues": p["issues"], "Score": p["score"], "Share": f"{share:.1f}%"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("### Contributor activity map")
    st.caption("A compact view of where the visible contributor activity is concentrated. Select a person to carry that context across the workspace.")
    matrix = _activity_matrix(people)
    if px is not None and not matrix.empty:
        fig = px.imshow(matrix, aspect="auto", color_continuous_scale="Purples", labels={"x": "Activity", "y": "Contributor", "color": "Count"})
        fig.update_layout(height=max(300, min(560, 110 + 28 * len(matrix))), margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#d9deea"))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.dataframe(matrix, use_container_width=True)

    selected_default = get_focus("contributor")
    names = [p["name"] for p in people]
    selected_index = names.index(selected_default) if selected_default in names else 0
    selected = st.selectbox("Focus contributor", names, index=selected_index, key="contributor_focus_select")
    if st.button("Focus this contributor", key="focus_contributor"):
        set_focus("contributor", selected, "Contributors")
        st.rerun()

    st.markdown("### Top contributors")
    top_people = people[:6]
    card_cols = st.columns(min(3, len(top_people)))
    for idx, person in enumerate(top_people):
        with card_cols[idx % len(card_cols)]:
            avatar = person.get("avatar")
            if avatar:
                st.image(avatar, width=52)
            st.markdown(f"**#{idx + 1} {person['name']}**")
            share = person["score"] / total_score * 100 if total_score else 0
            st.caption(f"Score {person['score']:.1f} · {share:.1f}% share")
            st.caption(f"{person['commits']:,} contributions · {person['prs']} PRs · {person['issues']} issues")

    left, right = st.columns(2)
    with left:
        st.markdown("### Contribution distribution")
        chart_df = pd.DataFrame({"Contributor": [p["name"] for p in people[:10]], "Score": [p["score"] for p in people[:10]]})
        st.bar_chart(chart_df, x="Contributor", y="Score", use_container_width=True)
    with right:
        st.markdown("### Activity mix")
        mix = pd.DataFrame({"Activity": ["Contributions", "Pull requests", "Issues"], "Count": [sum(p["commits"] for p in people), sum(p["prs"] for p in people), sum(p["issues"] for p in people)]})
        st.bar_chart(mix, x="Activity", y="Count", use_container_width=True)

    st.markdown("### Contributor explorer")
    person = next(p for p in people if p["name"] == selected)
    share = (person["score"] / total_score * 100) if total_score else 0
    if person.get("avatar"):
        st.image(person["avatar"], width=72)
    x, y, z, w = st.columns(4)
    x.metric("Contributions", person["commits"])
    y.metric("Pull requests", person["prs"])
    z.metric("Issues opened", person["issues"])
    w.metric("Contribution share", f"{share:.1f}%")

    st.markdown("### Team health interpretation")
    if top_share > 50:
        st.warning("The leading contributor group carries a disproportionate share of visible activity. Consider shared ownership and contributor onboarding.")
    elif top_share > 30:
        st.info("The repository has a noticeable primary contributor, but activity is not dominated by a single person.")
    else:
        st.success("Contribution volume is broadly distributed among the visible contributors.")

    st.caption("The GitHub contributors endpoint reports aggregate contribution counts; RepoPulse labels that source as Contributions rather than assuming every count is a commit. PR and issue counts reflect the fetched analysis window.")
