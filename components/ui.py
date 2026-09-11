from __future__ import annotations
import html
import streamlit as st


def page_header(eyebrow: str, title: str, description: str = "", action=None):
    c1, c2 = st.columns([5, 1])
    with c1:
        st.markdown(f'<div class="eyebrow">{html.escape(eyebrow)}</div><h1 class="page-title">{html.escape(title)}</h1>', unsafe_allow_html=True)
        if description:
            st.markdown(f'<div class="page-description">{html.escape(description)}</div>', unsafe_allow_html=True)
    if action:
        with c2:
            action()


def section_header(title: str, subtitle: str = ""):
    text = f'<div class="section-title">{html.escape(title)}</div>'
    if subtitle:
        text += f'<div class="section-subtitle">{html.escape(subtitle)}</div>'
    st.markdown(text, unsafe_allow_html=True)


def insight_card(title: str, body: str, tone: str = "neutral", label: str | None = None):
    label_html = f'<span class="insight-label {tone}">{html.escape(label)}</span>' if label else ''
    st.markdown(f'<div class="insight-card {tone} rp-insight">{label_html}<div class="insight-title">{html.escape(title)}</div><div class="insight-text">{html.escape(body)}</div></div>', unsafe_allow_html=True)


def empty_state(title: str, body: str, icon: str = "◌"):
    st.markdown(f'<div class="empty-state rp-empty"><div class="empty-icon">{icon}</div><div class="empty-title">{html.escape(title)}</div><div class="empty-text">{html.escape(body)}</div></div>', unsafe_allow_html=True)
