from __future__ import annotations

import html
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import streamlit as st

from analysis.repository_analysis import analyze_repository, parse_repository_input
from core.github_client import GitHubClient


# -----------------------------------------------------------------------------
# Comparison helpers
# -----------------------------------------------------------------------------

def _obj_value(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _analysis_parts(analysis: Any) -> Tuple[Any, Mapping[str, Any]]:
    """Read both the current AnalysisResult dataclass and dictionary-style data."""
    if analysis is None:
        return None, {}
    repo = _obj_value(analysis, "repository")
    metrics = _obj_value(analysis, "metrics", {}) or {}
    return repo, metrics


def _repo_name(analysis: Any) -> str:
    repo, _ = _analysis_parts(analysis)
    return str(
        _obj_value(repo, "full_name")
        or _obj_value(repo, "name")
        or "Repository"
    )


def _metric(analysis: Any, name: str, default: float = 0.0) -> float:
    repo, metrics = _analysis_parts(analysis)
    if name in metrics:
        value = metrics.get(name)
    else:
        value = _obj_value(repo, name, default)
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def _display_number(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:.1f}"


def _analysis_to_dict(analysis: Any) -> Dict[str, Any]:
    """Convert an analysis object to a JSON-ish structure for session storage."""
    if is_dataclass(analysis):
        return asdict(analysis)
    if isinstance(analysis, Mapping):
        return dict(analysis)
    return {"analysis": analysis}


def _analysis_from_session(repo_name: str) -> Any:
    """Resolve an analysis from the current analysis or stored repository snapshots."""
    current_name = st.session_state.get("current_repo")
    current_analysis = st.session_state.get("repo_analysis")
    if current_analysis is not None and repo_name == current_name:
        return current_analysis

    snapshots = st.session_state.get("repo_snapshots", {}) or {}
    candidate = snapshots.get(repo_name)
    if candidate is not None:
        # Some versions store the complete AnalysisResult, others store a snapshot
        # dictionary. Both are supported; dictionaries can still render raw metrics.
        return candidate

    # Session history can contain names even when the complete analysis wasn't
    # retained. We deliberately don't fabricate metrics for those repositories.
    return None


def _build_metrics(analysis: Any) -> Dict[str, float]:
    return {
        "Health": _metric(analysis, "repository_health_score"),
        "Recent activity": _metric(analysis, "recent_commit_count"),
        "Contributors": _metric(analysis, "total_contributors"),
        "Stars": _metric(analysis, "stars"),
        "Forks": _metric(analysis, "forks"),
        "Open issues": _metric(analysis, "open_issue_count"),
        "Open PRs": _metric(analysis, "open_pull_request_count"),
        "Engineering": _metric(analysis, "engineering_score"),
        "Documentation": _metric(analysis, "documentation_score"),
        "Testing": _metric(analysis, "testing_score"),
    }


def _dimension_metrics(analysis: Any) -> Dict[str, float]:
    """Return only 0-100 style intelligence dimensions.

    The scoring engine has evolved over time, so support both the current
    health_dimensions mapping and explicit top-level scores.
    """
    _, metrics = _analysis_parts(analysis)
    dimensions = metrics.get("health_dimensions") or {}

    def pick(label: str, *keys: str) -> float:
        for key in keys:
            if key in metrics:
                try:
                    return float(metrics[key] or 0)
                except (TypeError, ValueError):
                    pass
            if key in dimensions:
                try:
                    return float(dimensions[key] or 0)
                except (TypeError, ValueError):
                    pass
        return 0.0

    return {
        "Health": pick("Health", "repository_health_score"),
        "Activity": pick("Activity", "activity"),
        "Community": pick("Community", "community"),
        "Maintenance": pick("Maintenance", "maintenance"),
        "Issue health": pick("Issue health", "issue_health"),
        "PR health": pick("PR health", "pr_health"),
        "Contributor health": pick("Contributor health", "contributor_health"),
    }


def _fetch_repository(repo_input: str) -> Any:
    owner, repo_name = parse_repository_input(repo_input)
    client = GitHubClient()
    repo_data = client.get_repository(owner, repo_name)
    contributors_data = client.get_contributors(owner, repo_name)
    pull_requests_data = client.get_pull_requests(owner, repo_name)
    issues_data = client.get_issues(owner, repo_name)
    languages_data = client.get_languages(owner, repo_name)
    commits_data = client.get_commits(owner, repo_name, repo_data.get("default_branch"))
    return analyze_repository(
        repo_data=repo_data,
        contributors_data=contributors_data,
        languages_data=languages_data,
        issues_data=issues_data,
        pull_requests_data=pull_requests_data,
        commits_data=commits_data,
    )


def _winner(a: float, b: float, higher_is_better: bool = True) -> Tuple[str, float]:
    delta = a - b
    if not higher_is_better:
        delta = -delta
    if abs(delta) < 1e-9:
        return "Tie", 0.0
    return ("A" if delta > 0 else "B"), abs(delta)


def _glass_css() -> None:
    st.markdown(
        """
        <style>
        .compare-kicker{font:800 .62rem/1.2 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.18em;text-transform:uppercase;color:#a995ff}
        .compare-title{margin-top:.35rem;font-size:clamp(1.9rem,3vw,3rem);font-weight:850;letter-spacing:-.065em;color:#f7f8ff}
        .compare-copy{max-width:820px;margin-top:.5rem;color:rgba(211,218,234,.68);font-size:.78rem;line-height:1.6}
        .compare-glass{border:1px solid rgba(255,255,255,.105);border-radius:20px;background:linear-gradient(145deg,rgba(16,21,34,.58),rgba(9,13,23,.40));box-shadow:0 18px 55px rgba(0,0,0,.20),inset 0 1px 0 rgba(255,255,255,.06);backdrop-filter:blur(18px) saturate(125%);-webkit-backdrop-filter:blur(18px) saturate(125%)}
        .compare-hero{padding:1.3rem 1.35rem;margin-bottom:1rem;position:relative;overflow:hidden}
        .compare-hero:after{content:"";position:absolute;right:-80px;top:-100px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(139,92,246,.18),transparent 68%);pointer-events:none}
        .compare-score-grid{display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:center;padding:1.15rem;margin-top:1rem}
        .compare-score{padding:1rem;border:1px solid rgba(255,255,255,.075);border-radius:16px;background:rgba(255,255,255,.025)}
        .compare-score.is-leader{border-color:rgba(139,92,246,.38);box-shadow:0 0 34px rgba(99,102,241,.11)}
        .compare-score-name{font-size:.68rem;color:#8f9aae;text-transform:uppercase;letter-spacing:.12em}
        .compare-score-value{margin-top:.25rem;font-size:2.35rem;font-weight:850;letter-spacing:-.06em;color:#f7f8ff}
        .compare-score-label{font-size:.62rem;color:#6f7a8d;margin-top:.15rem}
        .compare-vs{font:800 .62rem ui-monospace,SFMono-Regular,Menlo,monospace;color:#68758b;letter-spacing:.16em}
        .compare-delta{text-align:center;padding:.5rem .75rem;border-radius:999px;background:rgba(139,92,246,.11);border:1px solid rgba(139,92,246,.22);color:#c9bcff;font-size:.68rem;font-weight:800}
        .compare-section{margin:1.25rem 0 .6rem;font-size:1.05rem;font-weight:800;letter-spacing:-.025em;color:#edf1f8}
        .compare-sub{font-size:.7rem;color:#7f899a;margin-top:-.25rem;margin-bottom:.75rem}
        .compare-matrix{overflow:hidden}
        .compare-row{display:grid;grid-template-columns:minmax(150px,1.1fr) minmax(160px,1fr) minmax(160px,1fr) minmax(130px,.8fr);gap:0;border-top:1px solid rgba(255,255,255,.065);align-items:center}
        .compare-row:first-child{border-top:0}
        .compare-cell{padding:.78rem .8rem;min-width:0}
        .compare-head{font-size:.58rem;text-transform:uppercase;letter-spacing:.12em;color:#727e91;font-weight:800}
        .compare-metric{font-size:.72rem;font-weight:720;color:#e6eaf2}
        .compare-number{font-size:.82rem;font-weight:800;color:#f2f5fa}
        .compare-track{height:5px;margin-top:.42rem;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden}
        .compare-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#8b5cf6,#5ea7ff)}
        .compare-fill.alt{background:linear-gradient(90deg,#5ea7ff,#8b5cf6)}
        .compare-winner{display:inline-flex;align-items:center;gap:.28rem;padding:.3rem .5rem;border-radius:999px;border:1px solid rgba(139,92,246,.22);background:rgba(139,92,246,.09);font-size:.59rem;font-weight:800;color:#cfc5ff}
        .compare-winner.tie{border-color:rgba(255,255,255,.10);background:rgba(255,255,255,.025);color:#8d98aa}
        .compare-findings{display:grid;grid-template-columns:1fr 1fr;gap:.8rem}
        .compare-find{padding:1rem;border:1px solid rgba(255,255,255,.09);border-radius:16px;background:linear-gradient(145deg,rgba(17,22,35,.48),rgba(8,12,21,.30));backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px)}
        .compare-find-label{font:800 .58rem ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.14em;text-transform:uppercase;color:#9e91ff}
        .compare-find-title{margin-top:.38rem;font-size:.88rem;font-weight:800;color:#edf1f8}
        .compare-find-copy{margin-top:.28rem;font-size:.66rem;line-height:1.5;color:#8792a5}
        .compare-verdict{padding:1.2rem 1.3rem}
        .compare-verdict-title{font-size:1.15rem;font-weight:820;letter-spacing:-.035em;color:#f5f7fb}
        .compare-verdict-copy{margin-top:.42rem;font-size:.72rem;line-height:1.65;color:#9aa4b5}
        .compare-action{margin-top:.85rem;padding:.75rem .8rem;border-left:2px solid #8b5cf6;background:rgba(139,92,246,.06);color:#bfc7d5;font-size:.67rem;line-height:1.5}
        @media(max-width:760px){.compare-score-grid{grid-template-columns:1fr}.compare-vs{display:none}.compare-findings{grid-template-columns:1fr}.compare-row{grid-template-columns:1fr 1fr}.compare-row .leader-cell{grid-column:1/-1;padding-top:0}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_metric_matrix(a_name: str, a: Any, b_name: str, b: Any) -> None:
    raw = _build_metrics(a)
    raw_b = _build_metrics(b)

    # Keep raw repository telemetry together, while clearly separating it from
    # the normalized intelligence dimensions below.
    raw_keys = ["Recent activity", "Contributors", "Stars", "Forks", "Open issues", "Open PRs"]
    dimension_keys = ["Health", "Activity", "Community", "Maintenance", "Issue health", "PR health", "Contributor health"]

    def render_group(title: str, subtitle: str, keys: Iterable[str], dimension: bool = False):
        st.markdown(f'<div class="compare-section">{title}</div><div class="compare-sub">{subtitle}</div>', unsafe_allow_html=True)
        rows = []
        for key in keys:
            va = raw.get(key, 0.0) if not dimension else _dimension_metrics(a).get(key, 0.0)
            vb = raw_b.get(key, 0.0) if not dimension else _dimension_metrics(b).get(key, 0.0)
            rows.append((key, va, vb))

        body = ['<div class="compare-glass compare-matrix">']
        body.append('<div class="compare-row"><div class="compare-cell compare-head">Metric</div><div class="compare-cell compare-head">Repository A</div><div class="compare-cell compare-head">Repository B</div><div class="compare-cell compare-head">Leader</div></div>')
        for key, va, vb in rows:
            winner, delta = _winner(va, vb)
            winner_name = a_name if winner == "A" else b_name if winner == "B" else "Tie"
            max_scale = max(va, vb, 1.0)
            pa = min(100.0, (va / max_scale) * 100.0)
            pb = min(100.0, (vb / max_scale) * 100.0)
            winner_cls = "compare-winner tie" if winner == "Tie" else "compare-winner"
            label = f"{winner_name} · +{_display_number(delta)}" if winner != "Tie" else "Tie"
            body.append(
                f'<div class="compare-row">'
                f'<div class="compare-cell compare-metric">{html.escape(key)}</div>'
                f'<div class="compare-cell"><div class="compare-number">{_display_number(va)}</div><div class="compare-track"><div class="compare-fill" style="width:{pa:.1f}%"></div></div></div>'
                f'<div class="compare-cell"><div class="compare-number">{_display_number(vb)}</div><div class="compare-track"><div class="compare-fill alt" style="width:{pb:.1f}%"></div></div></div>'
                f'<div class="compare-cell leader-cell"><span class="{winner_cls}">{html.escape(label)}</span></div>'
                f'</div>'
            )
        body.append('</div>')
        st.markdown("".join(body), unsafe_allow_html=True)

    render_group("Repository telemetry", "Raw operational values. Useful for context, but not directly comparable across different scales.", raw_keys)
    render_group("Normalized intelligence", "Comparable 0–100 dimensions used to interpret repository health and engineering maturity.", dimension_keys, dimension=True)


def compare_page() -> None:
    _glass_css()

    current = st.session_state.get("repo_analysis")
    current_name = st.session_state.get("current_repo")
    if current is None or not current_name:
        st.markdown('<div class="compare-kicker">Repository intelligence</div><div class="compare-title">Compare repositories</div><div class="compare-copy">Analyze a repository first. Comparison becomes available after RepoPulse has a repository intelligence profile to use as the baseline.</div>', unsafe_allow_html=True)
        st.info("Analyze a repository from the Repository page to unlock comparison.")
        return

    st.markdown('<div class="compare-kicker">Repository intelligence / comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="compare-title">Compare repositories</div>', unsafe_allow_html=True)
    st.markdown('<div class="compare-copy">Compare repository health, activity and engineering maturity without mixing incomparable raw scales.</div>', unsafe_allow_html=True)

    snapshots = st.session_state.get("repo_snapshots", {}) or {}
    history = [name for name in st.session_state.get("repo_session_history", []) if name]
    candidates = []
    for name in [*snapshots.keys(), *history]:
        if name != current_name and name not in candidates:
            candidates.append(name)

    with st.container():
        st.markdown('<div class="compare-glass compare-hero">', unsafe_allow_html=True)
        st.markdown("**Comparison setup**")
        st.caption(f"Baseline repository: **{current_name}**")
        default_target = st.session_state.get("compare_target", candidates[0] if candidates else "")
        target = st.text_input(
            "Repository B",
            value=default_target,
            placeholder="owner/repository or https://github.com/owner/repository",
            key="compare_target_input",
            label_visibility="visible",
        )
        analyze_target = st.button("Analyze repository for comparison", type="secondary", use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)

    if analyze_target:
        target = (target or "").strip()
        if not target:
            st.error("Enter a second GitHub repository to compare.")
        elif target == current_name:
            st.warning("Choose a different repository for comparison.")
        else:
            with st.spinner("Building comparison profile…"):
                try:
                    second = _fetch_repository(target)
                    second_name = _repo_name(second)
                    st.session_state.compare_target = second_name
                    st.session_state.compare_analysis = second
                    st.session_state.comparison_result = {
                        "left": _analysis_to_dict(current),
                        "right": _analysis_to_dict(second),
                    }
                    st.success(f"Comparison profile ready for {second_name}.")
                except Exception as exc:
                    st.error(f"Unable to analyze the comparison repository: {exc}")

    second = st.session_state.get("compare_analysis")
    second_name = st.session_state.get("compare_target")

    if second is None and second_name:
        second = _analysis_from_session(second_name)

    if second is None:
        st.markdown(
            '<div class="compare-glass compare-verdict"><div class="compare-verdict-title">Choose a second repository</div><div class="compare-verdict-copy">Your current repository is ready as the baseline. Analyze another public GitHub repository above to generate the intelligence comparison.</div></div>',
            unsafe_allow_html=True,
        )
        return

    a_name = _repo_name(current)
    b_name = _repo_name(second)
    a_dims = _dimension_metrics(current)
    b_dims = _dimension_metrics(second)
    a_health = a_dims.get("Health", _metric(current, "repository_health_score"))
    b_health = b_dims.get("Health", _metric(second, "repository_health_score"))
    overall_winner, health_delta = _winner(a_health, b_health)
    leader_name = a_name if overall_winner == "A" else b_name if overall_winner == "B" else "Tie"

    leader_a = overall_winner == "A"
    leader_b = overall_winner == "B"
    st.markdown(
        f'''<div class="compare-glass compare-score-grid">
          <div class="compare-score {"is-leader" if leader_a else ""}">
            <div class="compare-score-name">{html.escape(a_name)}</div>
            <div class="compare-score-value">{a_health:.1f}</div>
            <div class="compare-score-label">overall health / 100</div>
          </div>
          <div class="compare-delta">{("+" + _display_number(health_delta) + " health") if overall_winner != "Tie" else "HEALTH TIE"}</div>
          <div class="compare-score {"is-leader" if leader_b else ""}">
            <div class="compare-score-name">{html.escape(b_name)}</div>
            <div class="compare-score-value">{b_health:.1f}</div>
            <div class="compare-score-label">overall health / 100</div>
          </div>
        </div>''',
        unsafe_allow_html=True,
    )

    _render_metric_matrix(a_name, current, b_name, second)

    # Wins/losses across normalized dimensions.
    wins_a, wins_b = [], []
    for key in ["Activity", "Community", "Maintenance", "Issue health", "PR health", "Contributor health"]:
        va, vb = a_dims.get(key, 0), b_dims.get(key, 0)
        if va > vb:
            wins_a.append((key, va - vb))
        elif vb > va:
            wins_b.append((key, vb - va))

    st.markdown('<div class="compare-section">Where each repository wins</div><div class="compare-sub">The comparison highlights meaningful differences rather than forcing a single opaque score.</div>', unsafe_allow_html=True)
    left_items = "".join(f'<div class="compare-find"><div class="compare-find-label">RepoPulse lead</div><div class="compare-find-title">{html.escape(k)} · +{d:.1f}</div><div class="compare-find-copy">This dimension is stronger for {html.escape(a_name)} in the current analysis.</div></div>' for k, d in wins_a) or '<div class="compare-find"><div class="compare-find-label">No clear lead</div><div class="compare-find-title">No normalized dimensions won</div><div class="compare-find-copy">The repositories are currently tied or the available dimensions are incomplete.</div></div>'
    right_items = "".join(f'<div class="compare-find"><div class="compare-find-label">Repository B lead</div><div class="compare-find-title">{html.escape(k)} · +{d:.1f}</div><div class="compare-find-copy">This dimension is stronger for {html.escape(b_name)} in the current analysis.</div></div>' for k, d in wins_b) or '<div class="compare-find"><div class="compare-find-label">No clear lead</div><div class="compare-find-title">No normalized dimensions won</div><div class="compare-find-copy">The repositories are currently tied or the available dimensions are incomplete.</div></div>'
    st.markdown(f'<div class="compare-findings">{left_items}{right_items}</div>', unsafe_allow_html=True)

    raw_a = _build_metrics(current)
    raw_b = _build_metrics(second)
    activity_a, activity_b = raw_a["Recent activity"], raw_b["Recent activity"]
    testing_a, testing_b = raw_a.get("Testing", 0), raw_b.get("Testing", 0)

    if overall_winner == "A":
        verdict = f"{a_name} currently has the stronger overall repository profile, leading the health comparison by {health_delta:.1f} points."
    elif overall_winner == "B":
        verdict = f"{b_name} currently has the stronger overall repository profile, leading the health comparison by {health_delta:.1f} points."
    else:
        verdict = "The repositories are currently tied on overall health; the dimension-level differences are more informative than a single winner."

    action_bits = []
    if activity_a > activity_b:
        action_bits.append(f"{a_name} has stronger recent activity")
    elif activity_b > activity_a:
        action_bits.append(f"{b_name} has stronger recent activity")
    if testing_a > testing_b:
        action_bits.append(f"{a_name} has stronger testing signals")
    elif testing_b > testing_a:
        action_bits.append(f"{b_name} has stronger testing signals")

    action = "; ".join(action_bits) + "." if action_bits else "Review the dimension-level matrix to identify the clearest engineering differences."
    st.markdown(
        f'''<div class="compare-glass compare-verdict">
          <div class="compare-kicker">Comparison verdict</div>
          <div class="compare-verdict-title">{html.escape(leader_name)} is the current overall leader.</div>
          <div class="compare-verdict-copy">{html.escape(verdict)}</div>
          <div class="compare-action"><strong>Interpretation</strong><br>{html.escape(action)}</div>
        </div>''',
        unsafe_allow_html=True,
    )
