from __future__ import annotations

import html
from typing import Any

import streamlit as st


FOCUS_LABELS = {
    "health": "Health",
    "activity": "Activity",
    "engineering": "Engineering",
    "testing": "Testing",
    "documentation": "Documentation",
    "risk": "Risk",
    "contributor": "Contributor",
    "language": "Language",
    "file": "File",
}


def init_interaction_state() -> None:
    defaults = {
        "rp_focus": None,
        "rp_focus_value": None,
        "rp_focus_source": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_focus(kind: str, value: Any, source: str = "workspace") -> None:
    init_interaction_state()
    st.session_state.rp_focus = kind
    st.session_state.rp_focus_value = value
    st.session_state.rp_focus_source = source


def clear_focus() -> None:
    init_interaction_state()
    st.session_state.rp_focus = None
    st.session_state.rp_focus_value = None
    st.session_state.rp_focus_source = None


def get_focus(kind: str | None = None) -> Any:
    init_interaction_state()
    if kind is not None and st.session_state.rp_focus != kind:
        return None
    return st.session_state.rp_focus_value


def render_focus_bar() -> None:
    init_interaction_state()
    kind = st.session_state.rp_focus
    value = st.session_state.rp_focus_value
    if not kind or value in (None, ""):
        return
    label = FOCUS_LABELS.get(kind, kind.replace("_", " ").title())
    source = st.session_state.rp_focus_source or "workspace"
    st.html(
        f'''<div class="rp-focus-bar"><div><span class="rp-focus-kicker">FOCUS</span><span class="rp-focus-label">{html.escape(label)}</span><span class="rp-focus-value">{html.escape(str(value))}</span><span class="rp-focus-source">from {html.escape(source)}</span></div></div>'''
    )
    if st.button("Clear focus", key="rp_clear_focus", help="Return all views to their default context"):
        clear_focus()
        st.rerun()
