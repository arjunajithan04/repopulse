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
    selected = st.selectbox("Select a contributor", [p["name"] for p in people])
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
