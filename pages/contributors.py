from __future__ import annotations

import pandas as pd
import streamlit as st


def _contribution_score(person: dict) -> float:
    # Weighted score keeps the ranking understandable rather than pretending
    # GitHub's raw counts are directly comparable.
    return round(person["commits"] * 1.0 + person["prs"] * 3.0 + person["reviews"] * 2.0, 1)


def _bus_factor(contributors: list[dict]) -> tuple[str, str]:
    if not contributors:
        return "Unknown", "No contributor data is available."
    total = sum(max(0, p["score"]) for p in contributors)
    if total <= 0:
        return "Unknown", "Contribution volume is too low to estimate concentration."
    ranked = sorted(contributors, key=lambda x: x["score"], reverse=True)
    cumulative = 0
    count = 0
    for person in ranked:
        cumulative += person["score"]
        count += 1
        if cumulative / total >= 0.5:
            break
    if count == 1:
        return "High concentration", "One contributor accounts for at least half of the weighted contribution score."
    if count <= 3:
        return "Moderate concentration", "A small group of contributors accounts for at least half of the weighted contribution score."
    return "Distributed", "Contribution is spread across several contributors."


def contributors_page():
    st.subheader("Contributor intelligence", divider="green")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate contributor insights.")
        return

    contributors = []
    for contributor in analysis.contributors:
        person = {
            "name": contributor.login,
            "commits": int(getattr(contributor, "commits", 0) or 0),
            "prs": int(getattr(contributor, "pull_requests", 0) or 0),
            # Preserve the existing data model, but label it accurately below.
            "issues": int(getattr(contributor, "issues", 0) or 0),
            "avatar": contributor.avatar_url or "https://ui-avatars.com/api/?name=" + contributor.login,
        }
        person["reviews"] = person["issues"]
        person["score"] = _contribution_score({**person, "reviews": person["reviews"]})
        contributors.append(person)

    if not contributors:
        st.info("No contributor data was returned for this repository.")
        return

    contributors.sort(key=lambda x: x["score"], reverse=True)
    total_score = sum(p["score"] for p in contributors) or 1

    st.markdown("### Contributor leaderboard")
    leaderboard = []
    for rank, person in enumerate(contributors, 1):
        leaderboard.append({
            "Rank": rank,
            "Contributor": person["name"],
            "Score": person["score"],
            "Commits": person["commits"],
            "PRs": person["prs"],
            "Issues / reviews": person["issues"],
            "Share": f"{person['score'] / total_score * 100:.1f}%",
        })
    st.dataframe(pd.DataFrame(leaderboard), use_container_width=True, hide_index=True)

    top = contributors[:4]
    cols = st.columns(min(4, len(top)))
    for col, person in zip(cols, top):
        with col:
            share = person["score"] / total_score * 100
            st.markdown(
                f"""
                <div class="insight-card" style="text-align:center;">
                    <img src="{person['avatar']}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid rgba(139,92,246,.8);" />
                    <div class="insight-title" style="margin-top:.55rem;">#{contributors.index(person)+1} {person['name']}</div>
                    <div class="score-pill">Score {person['score']}</div>
                    <div class="insight-text" style="margin-top:.5rem;">{person['commits']} commits · {person['prs']} PRs · {person['issues']} issues/reviews<br>{share:.1f}% contribution share</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Contribution distribution")
    chart_df = pd.DataFrame({"Contributor": [p["name"] for p in contributors], "Score": [p["score"] for p in contributors]})
    st.bar_chart(chart_df, x="Contributor", y="Score")

    left, right = st.columns(2)
    with left:
        st.markdown("### Team health")
        bus_level, bus_text = _bus_factor(contributors)
        if bus_level == "High concentration":
            st.warning(f"**{bus_level}**")
        elif bus_level == "Moderate concentration":
            st.info(f"**{bus_level}**")
        else:
            st.success(f"**{bus_level}**")
        st.caption(bus_text)
        st.markdown(f"- Total contributors: **{analysis.metrics.get('total_contributors', len(contributors))}**")
        st.markdown(f"- Top contributor: **{analysis.metrics.get('top_contributor', contributors[0]['name'])}**")
        st.markdown(f"- Combined contribution score: **{total_score:.1f}**")

    with right:
        st.markdown("### Contributor actions")
        if bus_level == "High concentration":
            st.markdown("- Document ownership of critical areas.")
            st.markdown("- Pair the primary contributor with another maintainer.")
        if len(contributors) <= 3:
            st.markdown("- Create contributor onboarding documentation.")
        if any(p["prs"] == 0 for p in contributors):
            st.markdown("- Encourage contributors to participate in PR workflows, not only issue activity.")
        if bus_level == "Distributed":
            st.markdown("- Keep the current ownership distribution healthy through reviews and documentation.")

    st.markdown("### Contributor explorer")
    selected = st.selectbox("Select a contributor", [p["name"] for p in contributors])
    person = next(p for p in contributors if p["name"] == selected)
    detail = pd.DataFrame([
        {"Metric": "Commits", "Value": person["commits"]},
        {"Metric": "Pull requests", "Value": person["prs"]},
        {"Metric": "Issues / reviews", "Value": person["issues"]},
        {"Metric": "Contribution score", "Value": person["score"]},
        {"Metric": "Share of weighted contribution", "Value": f"{person['score'] / total_score * 100:.1f}%"},
    ])
    st.dataframe(detail, use_container_width=True, hide_index=True)
