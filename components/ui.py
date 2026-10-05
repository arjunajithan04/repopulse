from __future__ import annotations

import html
import streamlit as st


def page_header(eyebrow: str, title: str, description: str = "", action=None):
    c1, c2 = st.columns([5.5, 1], vertical_alignment="bottom")
    with c1:
        st.html(
            f'<div class="rp-page-heading"><div class="eyebrow">{html.escape(eyebrow)}</div><h1 class="page-title">{html.escape(title)}</h1></div>'
        )
        if description:
            st.html(
                f'<div class="page-description">{html.escape(description)}</div>'
            )
    if action:
        with c2:
            action()


def section_header(title: str, subtitle: str = "", eyebrow: str = ""):
    eyebrow_html = f'<div class="section-eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ""
    text = f'<div class="section-head">{eyebrow_html}<div class="section-title">{html.escape(title)}</div>'
    if subtitle:
        text += f'<div class="section-subtitle">{html.escape(subtitle)}</div>'
    text += "</div>"
    st.html(text)


def insight_card(title: str, body: str, tone: str = "neutral", label: str | None = None, icon: str = "✦"):
    label_html = f'<span class="insight-label {tone}">{html.escape(label)}</span>' if label else ""
    st.html(
        f'<div class="insight-card {tone} rp-insight"><div class="insight-top"><span class="insight-icon">{html.escape(icon)}</span>{label_html}</div><div class="insight-title">{html.escape(title)}</div><div class="insight-text">{html.escape(body)}</div></div>'
    )


def empty_state(title: str, body: str, icon: str = "◌", action=None):
    st.html(
        f'<div class="empty-state rp-empty"><div class="empty-icon">{html.escape(icon)}</div><div class="empty-title">{html.escape(title)}</div><div class="empty-text">{html.escape(body)}</div></div>'
    )
    if action:
        action()


def divider():
    st.html('<div class="rp-divider"></div>')


def callout(title: str, body: str, tone: str = "neutral", icon: str = "i"):
    safe = tone if tone in {"good", "warning", "danger", "neutral"} else "neutral"
    st.html(
        f'<div class="rp-callout {safe}"><div class="rp-callout-icon">{html.escape(icon)}</div><div><div class="rp-callout-title">{html.escape(title)}</div><div class="rp-callout-body">{html.escape(body)}</div></div></div>'
    )


def health_dimension(name: str, score: float):
    safe_score = max(0.0, min(100.0, float(score)))
    tone = "good" if safe_score >= 80 else "warning" if safe_score >= 60 else "danger"
    st.html(
        f"""
        <div class="health-dimension">
            <div class="health-dimension-top">
                <span>{html.escape(name)}</span>
                <strong class="{tone}">{safe_score:.0f}</strong>
            </div>
            <div class="health-track"><span class="{tone}" style="width:{safe_score:.1f}%"></span></div>
        </div>
        """
    )
