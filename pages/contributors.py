from __future__ import annotations

import streamlit as st


def contributors_page():
    st.subheader("Contributor intelligence", divider="green")

    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate contributor insights.")
        return

    contributors = []
    for contributor in analysis.contributors:
        contributors.append(
            {
                "name": contributor.login,
                "role": "Contributor",
                "commits": contributor.commits,
                "prs": contributor.pull_requests,
                "reviews": contributor.issues,
                "avatar": contributor.avatar_url or "https://ui-avatars.com/api/?name=" + contributor.login,
            }
        )

    if not contributors:
        st.info("No contributor data was returned for this repository.")
        return

    cols = st.columns(min(len(contributors), 4))
    for col, person in zip(cols, contributors):
        with col:
            st.markdown(
                f"""
                <div style="background: rgba(17,24,39,0.9); border:1px solid rgba(148,163,184,0.16); border-radius:18px; padding:1rem; text-align:center; min-height:230px;">
                    <img src="{person['avatar']}" style="width:72px; height:72px; border-radius:50%; object-fit:cover; border:2px solid rgba(139,92,246,0.9);" />
                    <h4 style="margin:0.7rem 0 0.2rem; color:white;">{person['name']}</h4>
                    <p style="margin:0 0 0.5rem; color:#a5b4cf;">{person['role']}</p>
                    <p style="margin:0; color:#dfe7f5;">{person['commits']} commits</p>
                    <p style="margin:0; color:#dfe7f5;">{person['prs']} PRs</p>
                    <p style="margin:0; color:#dfe7f5;">{person['reviews']} reviews</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Contributor summary")
    st.markdown(
        f"- Total contributors: {analysis.metrics.get('total_contributors', len(contributors))}\n"
        f"- Top contributor: {analysis.metrics.get('top_contributor', 'N/A')}\n"
        f"- Combined contributions: {analysis.metrics.get('total_contributions', 0)}\n"
        f"- Current repo: {analysis.repository.full_name or analysis.repository.name}"
    )
