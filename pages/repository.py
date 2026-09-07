from __future__ import annotations

from datetime import datetime

import streamlit as st

from analysis.repository_analysis import analyze_repository, parse_repository_input
from core.github_client import GitHubClient


MAX_ANALYSES = 10


def _normalize_repository_input(repository: str) -> str:
    value = (repository or "").strip()
    if not value:
        raise ValueError("Enter a GitHub repository URL or owner/repository name.")
    value = value.rstrip("/")
    if value.startswith("http://") or value.startswith("https://"):
        if "github.com/" not in value:
            raise ValueError("Please enter a valid GitHub repository URL.")
        return value
    return value


def _snapshot(analysis: object) -> dict:
    repo = analysis.repository
    metrics = analysis.metrics or {}
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stars": repo.stars or 0,
        "forks": repo.forks or 0,
        "issues": metrics.get("open_issue_count", 0),
        "pull_requests": metrics.get("open_pull_request_count", 0),
        "contributors": metrics.get("total_contributors", 0),
        "health": metrics.get("repository_health_score", 0),
        "commits": metrics.get("recent_commit_count", 0),
    }


def _friendly_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "404" in message or "not found" in message:
        return "Repository not found. Check the owner/repository name and make sure the repository is public or your GitHub token has access."
    if "401" in message or "403" in message or "rate limit" in message:
        return "GitHub denied the request or the API rate limit was reached. Try again later or configure a GitHub token in your deployment secrets."
    return f"Unable to analyze the repository. {exc}"


def _render_history():
    history = st.session_state.get("repo_session_history", [])
    if not history:
        return
    st.markdown("### Recent repositories")
    unique = list(dict.fromkeys(reversed(history)))[:8]
    for repo in unique:
        if st.button(f"↗  {repo}", key=f"history_{repo}", use_container_width=True):
            st.session_state["repository_input"] = repo
            st.rerun()


def _render_comparison():
    st.markdown("### Compare repositories")
    st.caption("Compare two repositories that have already been analyzed in this session.")
    snapshots = st.session_state.get("repo_snapshots", {})
    repos = list(snapshots.keys())
    if len(repos) < 2:
        st.info("Analyze at least two repositories to enable comparison.")
        return

    left, right = st.columns(2)
    with left:
        repo_a = st.selectbox("Repository A", repos, key="compare_a")
    with right:
        repo_b = st.selectbox("Repository B", repos, index=min(1, len(repos) - 1), key="compare_b")

    if repo_a == repo_b:
        st.warning("Choose two different repositories.")
        return

    a, b = snapshots[repo_a], snapshots[repo_b]
    metrics = [
        ("Stars", a["stars"], b["stars"]),
        ("Forks", a["forks"], b["forks"]),
        ("Open issues", a["issues"], b["issues"]),
        ("Open PRs", a["pull_requests"], b["pull_requests"]),
        ("Contributors", a["contributors"], b["contributors"]),
        ("Health score", a["health"], b["health"]),
        ("Recent commits", a["commits"], b["commits"]),
    ]
    rows = [{"Metric": label, repo_a: va, repo_b: vb} for label, va, vb in metrics]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def repository_page():
    st.subheader("Repository overview", divider="blue")
    st.caption("Analyze a public GitHub repository and keep a lightweight session history for trend and comparison views.")

    st.session_state.setdefault("repo_session_count", 0)
    st.session_state.setdefault("repo_session_history", [])
    st.session_state.setdefault("repo_snapshots", {})
    st.session_state.setdefault("repository_input", "microsoft/vscode")

    col1, col2 = st.columns([4, 1])
    with col1:
        repository = st.text_input(
            "GitHub repository",
            key="repository_input",
            placeholder="https://github.com/owner/repository or owner/repository",
        )
    with col2:
        st.write("")
        st.write("")
        analyze_clicked = st.button("Analyze", use_container_width=True, type="primary")

    if analyze_clicked:
        if st.session_state.repo_session_count >= MAX_ANALYSES:
            st.warning(f"This browser session has reached the {MAX_ANALYSES}-repository analysis limit.")
            return

        try:
            repo_input = _normalize_repository_input(repository)
            repo_owner, repo_name = parse_repository_input(repo_input)
            client = GitHubClient()

            progress = st.progress(0, text="Connecting to GitHub…")
            repo_data = client.get_repository(repo_owner, repo_name)
            progress.progress(20, text="Loading repository metadata…")
            contributors_data = client.get_contributors(repo_owner, repo_name)
            progress.progress(35, text="Loading contributors…")
            pull_requests_data = client.get_pull_requests(repo_owner, repo_name)
            progress.progress(50, text="Loading pull requests…")
            issues_data = client.get_issues(repo_owner, repo_name)
            progress.progress(65, text="Loading issues…")
            languages_data = client.get_languages(repo_owner, repo_name)
            progress.progress(80, text="Loading languages and commits…")
            commits_data = client.get_commits(repo_owner, repo_name, repo_data.get("default_branch"))
            progress.progress(92, text="Calculating repository intelligence…")

            analysis = analyze_repository(
                repo_data=repo_data,
                contributors_data=contributors_data,
                languages_data=languages_data,
                issues_data=issues_data,
                pull_requests_data=pull_requests_data,
                commits_data=commits_data,
            )
            progress.progress(100, text="Analysis complete")

            full_name = f"{repo_owner}/{repo_name}"
            st.session_state.repo_session_count += 1
            st.session_state.repo_session_history.append(full_name)
            st.session_state.current_repo = full_name
            st.session_state.repo_analysis = analysis
            st.session_state.repo_snapshots[full_name] = _snapshot(analysis)

            st.success(f"Analyzed {full_name} · {st.session_state.repo_session_count}/{MAX_ANALYSES} this session")

        except Exception as exc:
            st.error(_friendly_error(exc))
            return

    analysis = st.session_state.get("repo_analysis")
    if analysis is not None:
        repo = analysis.repository
        metrics = analysis.metrics or {}
        repo_name = repo.full_name or repo.name

        st.markdown("### Repository snapshot")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Stars", f"{repo.stars or 0:,}")
        c2.metric("Forks", f"{repo.forks or 0:,}")
        c3.metric("Open issues", f"{metrics.get('open_issue_count', 0):,}")
        c4.metric("Health", f"{metrics.get('repository_health_score', 0)}/100")

        left, right = st.columns([1.15, 1])
        with left:
            st.markdown("### Repository profile")
            profile = [
                {"Field": "Repository", "Value": repo_name},
                {"Field": "Owner", "Value": getattr(repo, "owner", None) or repo_name.split("/")[0]},
                {"Field": "Default branch", "Value": repo.default_branch or "N/A"},
                {"Field": "Visibility", "Value": "Private" if getattr(repo, "private", False) else "Public"},
                {"Field": "Primary language", "Value": repo.language or "N/A"},
                {"Field": "Open PRs", "Value": metrics.get("open_pull_request_count", 0)},
            ]
            st.dataframe(profile, use_container_width=True, hide_index=True)

        with right:
            st.markdown("### Repository summary")
            st.info(analysis.summary or "No summary was generated for this repository.")
            health = metrics.get("repository_health_score", 0)
            if health >= 80:
                st.success("Healthy repository profile — strong signals across maintenance and community activity.")
            elif health >= 60:
                st.warning("Moderate repository health — review the risk signals in the Dashboard and Code Insights pages.")
            else:
                st.error("Elevated repository risk — prioritize maintenance and contributor activity review.")

        st.markdown("### Session history")
        st.caption("These snapshots are intentionally session-based; they are not historical GitHub records.")
        snapshot_rows = []
        for name, snap in st.session_state.repo_snapshots.items():
            snapshot_rows.append({"Repository": name, **snap})
        if snapshot_rows:
            st.dataframe(snapshot_rows, use_container_width=True, hide_index=True)

    _render_history()
    _render_comparison()
