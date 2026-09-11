from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from analysis.code_analysis import analyze_files
from analysis.repository_analysis import analyze_repository, parse_repository_input
from core.github_client import GitHubAPIError, GitHubClient
from data.history import get_snapshots, init_db, save_snapshot

MAX_ANALYSES = 10
MAX_CODE_FILES = 60


def _normalize_repository_input(repository: str) -> str:
    value = (repository or "").strip()
    if not value:
        raise ValueError("Enter a GitHub repository URL or owner/repository name.")
    return value.rstrip("/")


def _snapshot(analysis: object) -> dict:
    repo = analysis.repository
    metrics = analysis.metrics or {}
    return {
        "full_name": repo.full_name or repo.name,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stars": repo.stars or 0,
        "forks": repo.forks or 0,
        "issues": metrics.get("open_issue_count", 0),
        "pull_requests": metrics.get("open_pull_request_count", 0),
        "contributors": metrics.get("total_contributors", 0),
        "health": metrics.get("repository_health_score", 0),
        "commits": metrics.get("recent_commit_count", 0),
        "health_dimensions": metrics.get("health_dimensions", {}),
    }


def _friendly_error(exc: Exception) -> str:
    if isinstance(exc, GitHubAPIError):
        if exc.status_code == 404:
            return "Repository not found. Check the owner/repository name and make sure the repository is public or your token has access."
        if exc.status_code in (401, 403):
            return "GitHub denied the request or the API rate limit was reached. Configure a GitHub token in your deployment secrets or try again later."
        return f"GitHub request failed: {exc}"
    return str(exc)


def _deep_code_scan(client: GitHubClient, owner: str, repo: str, branch: str) -> dict:
    tree = client.get_tree(owner, repo, branch)
    candidates = []
    for item in tree:
        path = item.get("path", "")
        if item.get("type") != "blob" or item.get("size", 0) > 200_000:
            continue
        if any(part in {".git", ".venv", "node_modules", "dist", "build"} for part in path.split("/")):
            continue
        candidates.append(item)
    candidates = candidates[:MAX_CODE_FILES]
    files = []
    for item in candidates:
        content = client.get_file_content(owner, repo, item["path"], branch)
        if content:
            files.append({"path": item["path"], "content": content})
    result = analyze_files(files)
    result["scan_limit"] = MAX_CODE_FILES
    result["tree_files_found"] = len(candidates)
    return result


def _render_history(repo_name: str):
    snapshots = get_snapshots(repo_name, limit=20)
    if not snapshots:
        st.info("No persistent history exists yet. Re-analyze this repository later to build a trend history.")
        return
    st.markdown("### Persistent history")
    st.caption("Snapshots are stored locally in RepoPulse's SQLite history database.")
    rows = [
        {
            "Captured": item["captured_at"],
            "Stars": item["stars"],
            "Forks": item["forks"],
            "Issues": item["open_issues"],
            "PRs": item["open_pull_requests"],
            "Contributors": item["contributors"],
            "Commits": item["recent_commits"],
            "Health": item["health_score"],
        }
        for item in reversed(snapshots)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_comparison():
    st.markdown("### Compare repositories")
    snapshots = st.session_state.get("repo_snapshots", {})
    repos = list(snapshots.keys())
    if len(repos) < 2:
        st.info("Analyze at least two repositories in this session to enable comparison.")
        return
    a_name, b_name = st.columns(2)
    with a_name:
        repo_a = st.selectbox("Repository A", repos, key="compare_a")
    with b_name:
        repo_b = st.selectbox("Repository B", repos, index=min(1, len(repos) - 1), key="compare_b")
    if repo_a == repo_b:
        st.warning("Choose two different repositories.")
        return
    a, b = snapshots[repo_a], snapshots[repo_b]
    metrics = [("Stars", a["stars"], b["stars"]), ("Forks", a["forks"], b["forks"]), ("Open issues", a["issues"], b["issues"]), ("Open PRs", a["pull_requests"], b["pull_requests"]), ("Contributors", a["contributors"], b["contributors"]), ("Health", a["health"], b["health"]), ("Recent commits", a["commits"], b["commits"])]
    rows = [{"Metric": label, repo_a: va, repo_b: vb} for label, va, vb in metrics]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    winners = sum(1 for _, va, vb in metrics if va > vb) - sum(1 for _, va, vb in metrics if va < vb)
    if winners > 0:
        st.success(f"{repo_a} leads on more of the selected raw metrics.")
    elif winners < 0:
        st.success(f"{repo_b} leads on more of the selected raw metrics.")
    else:
        st.info("The selected repositories are balanced across the displayed metrics.")


def repository_page():
    init_db()
    st.subheader("Repository overview", divider="blue")
    st.caption("Analyze a GitHub repository, persist health snapshots, and optionally scan source files for code-level signals.")

    st.session_state.setdefault("repo_session_count", 0)
    st.session_state.setdefault("repo_session_history", [])
    st.session_state.setdefault("repo_snapshots", {})
    st.session_state.setdefault("repository_input", "microsoft/vscode")

    col1, col2 = st.columns([4, 1])
    with col1:
        repository = st.text_input("GitHub repository", key="repository_input", placeholder="https://github.com/owner/repository or owner/repository")
    with col2:
        st.write("")
        st.write("")
        analyze_clicked = st.button("Analyze", use_container_width=True, type="primary")

    deep_scan = st.checkbox("Run deep code scan", value=False, help="Downloads a bounded set of source files and performs local code metrics. This can increase API requests.")

    if analyze_clicked:
        if st.session_state.repo_session_count >= MAX_ANALYSES:
            st.warning(f"This browser session has reached the {MAX_ANALYSES}-repository analysis limit.")
            return
        try:
            repo_owner, repo_name = parse_repository_input(_normalize_repository_input(repository))
            client = GitHubClient()
            progress = st.progress(0, text="Connecting to GitHub…")
            repo_data = client.get_repository(repo_owner, repo_name)
            progress.progress(18, text="Loading repository metadata…")
            contributors_data = client.get_contributors(repo_owner, repo_name)
            progress.progress(32, text="Loading contributors…")
            pull_requests_data = client.get_pull_requests(repo_owner, repo_name)
            progress.progress(47, text="Loading pull requests…")
            issues_data = client.get_issues(repo_owner, repo_name)
            progress.progress(62, text="Loading issues…")
            languages_data = client.get_languages(repo_owner, repo_name)
            progress.progress(76, text="Loading languages and commits…")
            commits_data = client.get_commits(repo_owner, repo_name, repo_data.get("default_branch"))
            progress.progress(88, text="Calculating repository intelligence…")
            analysis = analyze_repository(repo_data, contributors_data, languages_data, issues_data, pull_requests_data, commits_data)

            if deep_scan:
                progress.progress(92, text="Scanning source files…")
                code_metrics = _deep_code_scan(client, repo_owner, repo_name, repo.default_branch if (repo := analysis.repository) else "main")
                analysis.metrics["code_analysis"] = code_metrics

            snapshot = _snapshot(analysis)
            save_snapshot(snapshot)
            full_name = f"{repo_owner}/{repo_name}"
            st.session_state.repo_session_count += 1
            st.session_state.repo_session_history.append(full_name)
            st.session_state.current_repo = full_name
            st.session_state.repo_analysis = analysis
            st.session_state.repo_snapshots[full_name] = snapshot
            progress.progress(100, text="Analysis complete")
            st.success(f"Analyzed {full_name} · {st.session_state.repo_session_count}/{MAX_ANALYSES} this session")
        except Exception as exc:
            st.error(_friendly_error(exc))
            return

    analysis = st.session_state.get("repo_analysis")
    if analysis is not None:
        repo = analysis.repository
        metrics = analysis.metrics or {}
        repo_name = repo.full_name or repo.name
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Stars", f"{repo.stars:,}")
        c2.metric("Forks", f"{repo.forks:,}")
        c3.metric("Open issues", f"{metrics.get('open_issue_count', 0):,}")
        c4.metric("Health", f"{metrics.get('repository_health_score', 0)}/100")

        left, right = st.columns([1.15, 1])
        with left:
            st.markdown("### Repository profile")
            st.markdown(repo.description or "No repository description provided.")
            profile = [
                {"Field": "Repository", "Value": repo_name},
                {"Field": "Default branch", "Value": repo.default_branch or "N/A"},
                {"Field": "Primary language", "Value": repo.language or "N/A"},
                {"Field": "Open PRs", "Value": metrics.get("open_pull_request_count", 0)},
                {"Field": "Contributors", "Value": metrics.get("total_contributors", 0)},
                {"Field": "Bus factor", "Value": metrics.get("bus_factor", 0)},
            ]
            st.dataframe(profile, use_container_width=True, hide_index=True)
        with right:
            st.markdown("### Repository assessment")
            st.info(analysis.summary)
            health = float(metrics.get("repository_health_score", 0) or 0)
            if health >= 80:
                st.success("Healthy repository profile")
            elif health >= 60:
                st.warning("Moderate repository health")
            else:
                st.error("Elevated repository risk")

        if metrics.get("code_analysis"):
            code = metrics["code_analysis"]
            st.markdown("### Code scan result")
            a, b, c, d = st.columns(4)
            a.metric("Files analyzed", code.get("files_analyzed", 0))
            b.metric("Lines", f"{code.get('total_lines', 0):,}")
            c.metric("Avg complexity", code.get("avg_complexity", 0))
            d.metric("Status", code.get("status", "Unknown"))

        _render_history(repo_name)
    _render_comparison()
