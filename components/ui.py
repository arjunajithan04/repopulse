from __future__ import annotations
import html
import streamlit as st


def page_header(eyebrow: str, title: str, description: str = "", action=None):
    c1, c2 = st.columns([5.5, 1], vertical_alignment="bottom")
    with c1:
        st.markdown(f'<div class="eyebrow">{html.escape(eyebrow)}</div><h1 class="page-title">{html.escape(title)}</h1>', unsafe_allow_html=True)
        if description:
            st.markdown(f'<div class="page-description">{html.escape(description)}</div>', unsafe_allow_html=True)
    if action:
        with c2:
            action()


def section_header(title: str, subtitle: str = "", eyebrow: str = ""):
    eyebrow_html = f'<div class="section-eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ''
    text = f'<div class="section-head">{eyebrow_html}<div class="section-title">{html.escape(title)}</div>'
    if subtitle:
        text += f'<div class="section-subtitle">{html.escape(subtitle)}</div>'
    text += '</div>'
    st.markdown(text, unsafe_allow_html=True)


def insight_card(title: str, body: str, tone: str = "neutral", label: str | None = None, icon: str = "✦"):
    label_html = f'<span class="insight-label {tone}">{html.escape(label)}</span>' if label else ''
    st.markdown(
        f'<div class="insight-card {tone} rp-insight"><div class="insight-top"><span class="insight-icon">{html.escape(icon)}</span>{label_html}</div><div class="insight-title">{html.escape(title)}</div><div class="insight-text">{html.escape(body)}</div></div>',
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str, icon: str = "◌", action=None):
    st.markdown(f'<div class="empty-state rp-empty"><div class="empty-icon">{html.escape(icon)}</div><div class="empty-title">{html.escape(title)}</div><div class="empty-text">{html.escape(body)}</div></div>', unsafe_allow_html=True)
    if action:
        action()


def divider():
    st.markdown('<div class="rp-divider"></div>', unsafe_allow_html=True)


def callout(title: str, body: str, tone: str = "neutral", icon: str = "i"):
    safe = tone if tone in {"good", "warning", "danger", "neutral"} else "neutral"
    st.markdown(
        f'<div class="rp-callout {safe}"><div class="rp-callout-icon">{html.escape(icon)}</div><div><div class="rp-callout-title">{html.escape(title)}</div><div class="rp-callout-body">{html.escape(body)}</div></div></div>',
        unsafe_allow_html=True,
    )
