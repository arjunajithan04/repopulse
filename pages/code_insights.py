from __future__ import annotations

import pandas as pd
import streamlit as st

from components.cards import metric_card
from components.charts import render_language_donut, render_health_radar
from components.interaction import get_focus, set_focus

try:
    import plotly.express as px
except ImportError:  # pragma: no cover
    px = None


def _quality_label(score: float) -> str:
    if score >= 80:
        return "Healthy"
    if score >= 60:
        return "Moderate"
    return "Needs attention"


def _render_codebase_map(df: pd.DataFrame):
    if df.empty:
        return
    map_df = df.copy()
    map_df["lines"] = pd.to_numeric(map_df.get("lines", 0), errors="coerce").fillna(0)
    map_df["complexity"] = pd.to_numeric(map_df.get("complexity", 0), errors="coerce").fillna(0)
    map_df["language"] = map_df.get("language", "Unknown").fillna("Unknown")
    map_df = map_df[map_df["lines"] > 0].head(80)
    if px is not None and not map_df.empty:
        fig = px.treemap(map_df, path=["language", "file"], values="lines", color="complexity", color_continuous_scale="Purples", hover_data={"lines": True, "complexity": True})
        fig.update_layout(height=500, margin=dict(l=4, r=4, t=10, b=4), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#d9deea"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.dataframe(map_df[["file", "language", "lines", "complexity"]], use_container_width=True, hide_index=True)


def code_insights_page():
    st.subheader("Code insights", divider="blue")
    st.caption("Explore language composition, structural complexity, and repository-level quality signals.")
    analysis = st.session_state.get("repo_analysis")
    if analysis is None:
        st.info("Analyze a repository from the Repository page to populate code quality insights.")
        return

    metrics = analysis.metrics or {}
    code = metrics.get("code_analysis")
    languages = metrics.get("language_breakdown", {}) or {}

    if languages:
        total_bytes = sum(languages.values()) or 1
        lang_rows = [{"Language": lang, "Share": round(size / total_bytes * 100, 1), "Bytes": size} for lang, size in sorted(languages.items(), key=lambda x: x[1], reverse=True)]
        st.markdown("### Language profile")
        st.caption("Share is calculated from the byte counts reported by GitHub, not from file count or lines of code.")
        render_language_donut(pd.DataFrame(lang_rows).head(10), height=320)
    else:
        st.info("GitHub did not return language composition data for this repository.")

    if code:
        score = float(code.get("quality_score", 0) or 0)
        status = _quality_label(score)
        st.markdown("### Codebase health")
        a, b, c, d = st.columns(4)
        with a:
            metric_card("Code quality", f"{score:.0f}/100", help_text=status, icon="◉",
                        variant="good" if score >= 80 else "bad" if score < 60 else "neutral",
                        progress=score)
        with b:
            metric_card("Files analyzed", f"{int(code.get('files_analyzed', 0) or 0):,}",
                        help_text="Bounded source scan", icon="▤")
        with c:
            metric_card("Lines of code", f"{int(code.get('total_lines', 0) or 0):,}",
                        help_text="Lines observed in analyzed files", icon="≡")
        with d:
            complexity = float(code.get("avg_complexity", 0) or 0)
            metric_card("Average complexity", f"{complexity:.1f}",
                        help_text="Average measured per-file complexity", icon="⌘",
                        variant="bad" if complexity >= 10 else "neutral")
        st.caption(f"{code.get('files_analyzed_with_ast', 0)} AST-analyzed files · {code.get('files_analyzed_with_heuristics', 0)} heuristic-analyzed files")

        q1, q2, q3 = st.columns(3)
        with q1:
            metric_card("Functions", f"{int(code.get('functions', 0) or 0):,}",
                        help_text="Functions detected in the bounded scan", icon="ƒ")
        with q2:
            metric_card("Classes", f"{int(code.get('classes', 0) or 0):,}",
                        help_text="Classes detected in the bounded scan", icon="▦")
        with q3:
            comment_ratio = float(code.get("comment_ratio", 0) or 0)
            metric_card("Comment ratio", f"{comment_ratio:.1f}%",
                        help_text="Comment lines relative to scanned source", icon="¶",
                        variant="bad" if comment_ratio < 10 else "neutral")

        flags = code.get("flags", [])
        if flags:
            st.markdown("### Quality flags")
            for flag in flags:
                st.warning(flag)
        else:
            st.success("No major code-quality flags were detected in the scanned files.")

        files = code.get("files", [])
        if files:
            st.markdown("### Codebase complexity map")
            st.caption("Tile size represents lines of code; intensity represents measured complexity. Click a file below to inspect its evidence.")
            _render_codebase_map(pd.DataFrame(files))

            st.markdown("### File explorer")
            df = pd.DataFrame(files)
            languages_filter = ["All"] + sorted(df["language"].dropna().unique().tolist()) if "language" in df else ["All"]
            f1, f2 = st.columns([2, 1])
            with f1:
                query = st.text_input("Search files", placeholder="e.g. services, utils, main.py")
            with f2:
                selected_language = st.selectbox("Language", languages_filter)
            filtered = df.copy()
            focus_file = get_focus("file")
            if query:
                filtered = filtered[filtered["file"].str.contains(query, case=False, na=False)]
            if selected_language != "All" and "language" in filtered:
                filtered = filtered[filtered["language"] == selected_language]
            sort_by = st.selectbox("Sort file metrics by", ["lines", "complexity", "file"], index=0)
            if sort_by in filtered.columns:
                filtered = filtered.sort_values(sort_by, ascending=False)
            st.dataframe(filtered, use_container_width=True, hide_index=True)

            options = filtered["file"].tolist() if "file" in filtered else []
            if focus_file in options:
                selected_file = st.selectbox("Inspect file", options, index=options.index(focus_file), key="phase5_file_select")
            else:
                selected_file = st.selectbox("Inspect file", options, key="phase5_file_select") if options else None
            if selected_file:
                row = df[df["file"] == selected_file].iloc[0]
                i1, i2, i3, i4 = st.columns(4)
                i1.metric("Lines", int(row.get("lines", 0)))
                i2.metric("Complexity", row.get("complexity", 0))
                i3.metric("Language", row.get("language", "Unknown"))
                i4.metric("Functions", int(row.get("functions", 0)))
                if st.button("Focus this file", key="focus_code_file"):
                    set_focus("file", selected_file, "Code Insights")
                    st.rerun()
                st.caption("File-level source content remains bounded by the existing scan limits.")

        left, right = st.columns(2)
        with left:
            st.markdown("### Largest files")
            largest = code.get("largest_files", [])
            if largest:
                st.dataframe(pd.DataFrame(largest)[["file", "language", "lines", "complexity"]], use_container_width=True, hide_index=True)
            else:
                st.info("No file-level results available.")
        with right:
            st.markdown("### Highest complexity")
            complex_files = code.get("complex_files", [])
            if complex_files:
                st.dataframe(pd.DataFrame(complex_files)[["file", "language", "complexity", "lines"]], use_container_width=True, hide_index=True)
            else:
                st.info("No complexity results available.")
    else:
        st.markdown("### Deep code analysis")
        st.info("Run **Deep code scan** from the Repository page to calculate file count, LOC, complexity, functions, classes, documentation signals, and problem files.")

    st.markdown("### Repository-level quality signals")
    dimensions = metrics.get("health_dimensions", {})
    if dimensions:
        render_health_radar({key.replace("_", " ").title(): float(value or 0) for key, value in dimensions.items()}, height=340)
    else:
        st.info("Repository health dimensions are not available for this scan.")

    st.markdown("### Recommendations")
    recommendations = []
    health = float(metrics.get("repository_health_score", 0) or 0)
    if health < 70:
        recommendations.append("Review the weakest repository-health dimension before expanding scope.")
    if code and float(code.get("avg_complexity", 0) or 0) >= 10:
        recommendations.append("Inspect the highest-complexity files and split large functions into smaller units.")
    if code and float(code.get("comment_ratio", 0) or 0) < 10:
        recommendations.append("Consider adding documentation around complex or public-facing logic.")
    if not recommendations:
        recommendations.append("No immediate code-quality action is suggested by the current bounded scan.")
    for item in recommendations:
        st.info(item)
