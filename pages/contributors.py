from __future__ import annotations

import streamlit as st


def contributors_page():
    st.subheader("Contributor intelligence", divider="green")

    contributors = [
        {
            "name": "Alice Nguyen",
            "role": "Frontend lead",
            "commits": 142,
            "prs": 22,
            "reviews": 18,
            "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80",
        },
        {
            "name": "Bob Patel",
            "role": "Platform engineer",
            "commits": 98,
            "prs": 19,
            "reviews": 12,
            "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
        },
        {
            "name": "Charlie Ross",
            "role": "DevOps",
            "commits": 76,
            "prs": 11,
            "reviews": 20,
            "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=200&q=80",
        },
    ]

    cols = st.columns(len(contributors))
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
        "- Top contributor momentum remains strong\n"
        "- Review coverage is balanced across the team\n"
        "- Commit flow indicates healthy engineering discipline"
    )
