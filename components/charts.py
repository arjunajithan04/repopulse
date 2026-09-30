from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:  # pragma: no cover - requirements install Plotly in normal runs
    PLOTLY_AVAILABLE = False


BG = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,.07)"
TEXT = "#dce3ed"
MUTED = "#7f8a9b"
PURPLE = "#8b5cf6"
INDIGO = "#6366f1"
GREEN = "#34d399"
AMBER = "#fbbf24"
RED = "#fb7185"


def _base(fig):
    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family="Inter, system-ui, sans-serif", size=12),
        margin=dict(l=8, r=8, t=16, b=8),
        hoverlabel=dict(bgcolor="#151923", bordercolor="rgba(255,255,255,.12)", font=dict(color=TEXT)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=MUTED)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=MUTED)
    return fig


def _render(fig, height: int = 320):
    fig = _base(fig)
    fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})


def render_bar_chart(data: Dict[str, int], title: str = "Overview"):
    if not data:
        st.info("No chart data available.")
        return
    if not PLOTLY_AVAILABLE:
        st.bar_chart(pd.DataFrame({"Metric": list(data.keys()), "Value": list(data.values())}), x="Metric", y="Value", use_container_width=True)
        return
    df = pd.DataFrame({"Metric": list(data.keys()), "Value": list(data.values())})
    fig = px.bar(df, x="Metric", y="Value", title=title, color_discrete_sequence=[PURPLE])
    fig.update_layout(title=None)
    _render(fig)


def render_line_chart(series: List[float], title: str = "Trend"):
    if not series:
        st.info("No trend data available.")
        return
    if not PLOTLY_AVAILABLE:
        st.line_chart(series, use_container_width=True)
        return
    df = pd.DataFrame({"Index": range(len(series)), "Value": series})
    fig = px.line(df, x="Index", y="Value", markers=True, color_discrete_sequence=[PURPLE])
    fig.update_layout(title=None)
    _render(fig)


def render_health_radar(dimensions: Dict[str, float], height: int = 360):
    if not dimensions:
        st.info("No health dimensions available.")
        return
    if not PLOTLY_AVAILABLE:
        rows = [{"Dimension": str(k).replace("_", " ").title(), "Score": float(v or 0)} for k, v in dimensions.items()]
        st.bar_chart(pd.DataFrame(rows), x="Dimension", y="Score", use_container_width=True)
        return
    labels = [str(k).replace("_", " ").title() for k in dimensions]
    values = [max(0, min(100, float(v or 0))) for v in dimensions.values()]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(139,92,246,.16)",
        line=dict(color=PURPLE, width=2),
        marker=dict(color=INDIGO, size=5),
        hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
        name="Health",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor=GRID),
            angularaxis=dict(gridcolor=GRID, color=MUTED),
        ),
        showlegend=False,
        margin=dict(l=35, r=35, t=20, b=20),
    )
    _render(fig, height)


def render_history_chart(df: pd.DataFrame, metric: str, label: str, height: int = 330):
    if df.empty or metric not in df.columns:
        st.info("No historical data is available for this metric yet.")
        return
    if not PLOTLY_AVAILABLE:
        chart = df[[metric]].rename(columns={metric: label})
        st.line_chart(chart, use_container_width=True)
        return
    chart = df[["captured_at", metric]].copy()
    chart["captured_at"] = pd.to_datetime(chart["captured_at"], errors="coerce")
    chart = chart.dropna(subset=["captured_at"])
    chart[label] = pd.to_numeric(chart[metric], errors="coerce").fillna(0)
    fig = px.line(chart, x="captured_at", y=label, markers=True, color_discrete_sequence=[PURPLE])
    fig.update_layout(title=None, hovermode="x unified")
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    _render(fig, height)


def render_grouped_comparison(df: pd.DataFrame, metric_columns: Sequence[str], height: int = 430):
    if df.empty:
        st.info("No comparison data available.")
        return
    if not PLOTLY_AVAILABLE:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return
    melted = df.melt(id_vars=["Metric"], value_vars=list(metric_columns), var_name="Repository", value_name="Value")
    fig = px.bar(melted, x="Metric", y="Value", color="Repository", barmode="group", color_discrete_sequence=[PURPLE, INDIGO])
    fig.update_layout(title=None, xaxis_tickangle=-25)
    _render(fig, height)


def render_language_donut(rows: pd.DataFrame, height: int = 340):
    if rows.empty:
        st.info("No language data available.")
        return
    if not PLOTLY_AVAILABLE:
        st.bar_chart(rows, x="Language", y="Share", use_container_width=True)
        return
    fig = px.pie(rows, names="Language", values="Share", hole=.68, color_discrete_sequence=[PURPLE, INDIGO, GREEN, AMBER, RED, "#a78bfa", "#818cf8", "#6ee7b7"])
    fig.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}: %{value:.1f}%<extra></extra>")
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-.08), margin=dict(l=8, r=8, t=8, b=36))
    _render(fig, height)


def render_codebase_treemap(files: pd.DataFrame, height: int = 470):
    required = {"file", "lines", "complexity", "language"}
    if files.empty or not required.issubset(files.columns):
        st.info("No file-level scan data is available for the codebase map.")
        return
    if not PLOTLY_AVAILABLE:
        st.dataframe(files[["file", "lines", "complexity", "language"]], use_container_width=True, hide_index=True)
        return
    chart = files.copy()
    chart["lines"] = pd.to_numeric(chart["lines"], errors="coerce").fillna(0).clip(lower=1)
    chart["complexity"] = pd.to_numeric(chart["complexity"], errors="coerce").fillna(0)
    chart["display"] = chart["file"].astype(str).str.replace("/", " / ", regex=False)
    fig = px.treemap(
        chart,
        path=["language", "display"],
        values="lines",
        color="complexity",
        color_continuous_scale=[[0, "#20263a"], [.45, "#6366f1"], [1, "#fb7185"]],
        hover_data={"lines": True, "complexity": True, "language": True},
    )
    fig.update_traces(root_color="rgba(0,0,0,0)", marker=dict(line=dict(color="rgba(255,255,255,.07)", width=1)))
    fig.update_layout(coloraxis_colorbar=dict(title="Complexity", tickfont=dict(color=MUTED)), margin=dict(l=2, r=2, t=8, b=2))
    _render(fig, height)


def render_concentration(scores: Iterable[float], height: int = 300):
    values = sorted([float(v or 0) for v in scores], reverse=True)
    if not values:
        st.info("No contribution data available.")
        return
    total = sum(values) or 1
    cumulative = []
    running = 0.0
    for value in values:
        running += value
        cumulative.append(running / total * 100)
    if not PLOTLY_AVAILABLE:
        st.line_chart(pd.DataFrame({"Contributor rank": range(1, len(cumulative) + 1), "Cumulative share": cumulative}), x="Contributor rank", y="Cumulative share", use_container_width=True)
        return
    df = pd.DataFrame({"Contributor rank": range(1, len(cumulative) + 1), "Cumulative share": cumulative})
    fig = px.line(df, x="Contributor rank", y="Cumulative share", markers=True, color_discrete_sequence=[PURPLE])
    fig.update_layout(title=None, yaxis_range=[0, 100])
    fig.add_hline(y=50, line_dash="dot", line_color=AMBER, opacity=.6)
    _render(fig, height)


def render_health_trajectory(df: pd.DataFrame, height: int = 300):
    """Render a cinematic health trajectory from persisted snapshots."""
    required = {"captured_at", "health_score"}
    if df.empty or not required.issubset(df.columns):
        st.info("Not enough history to render a health trajectory yet.")
        return
    if not PLOTLY_AVAILABLE:
        chart = df[["captured_at", "health_score"]].copy().set_index("captured_at")
        st.line_chart(chart, use_container_width=True)
        return
    chart = df[["captured_at", "health_score"]].copy()
    chart["captured_at"] = pd.to_datetime(chart["captured_at"], errors="coerce")
    chart["health_score"] = pd.to_numeric(chart["health_score"], errors="coerce")
    chart = chart.dropna().sort_values("captured_at")
    if chart.empty:
        st.info("Not enough history to render a health trajectory yet.")
        return
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart["captured_at"],
            y=chart["health_score"],
            mode="lines+markers",
            line=dict(color=PURPLE, width=3, shape="spline"),
            marker=dict(size=7, color=INDIGO, line=dict(color="#0d1016", width=2)),
            fill="tozeroy",
            fillcolor="rgba(139,92,246,.08)",
            hovertemplate="%{x|%d %b %Y}<br>Health: %{y:.1f}<extra></extra>",
            name="Health",
        )
    )
    fig.add_hline(y=80, line_dash="dot", line_color=GREEN, opacity=.28)
    fig.add_hline(y=60, line_dash="dot", line_color=AMBER, opacity=.25)
    fig.update_yaxes(range=[0, 100], title=None)
    fig.update_xaxes(title=None)
    fig.update_layout(showlegend=False, hovermode="x unified")
    _render(fig, height)
