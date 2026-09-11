from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from analysis.code_analysis import analyze_files
from analysis.engineering import analyze_engineering
from analysis.repository_analysis import analyze_repository, parse_repository_input
from core.github_client import GitHubAPIError, GitHubClient
from data.history import get_snapshots, init_db, save_snapshot

MAX_ANALYSES = 10
MAX_CODE_FILES = 60
CACHE_TTL = 300


def _normalize_repository_input(repository: str) -> str:
    value = (repository or "").strip()
    if not value:
        raise ValueError("Enter a GitHub repository URL or owner/repository name.")
    return value.rstrip("/")


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_repository(owner: str, repo: str, nonce: int):
    return GitHubClient().get_repository(owner, repo)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_contributors(owner: str, repo: str, nonce: int):
    return GitHubClient().get_contributors(owner, repo)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_prs(owner: str, repo: str, nonce: int):
    return GitHubClient().get_pull_requests(owner, repo)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_issues(owner: str, repo: str, nonce: int):
    return GitHubClient().get_issues(owner, repo)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_languages(owner: str, repo: str, nonce: int):
    return GitHubClient().get_languages(owner, repo)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_commits(owner: str, repo: str, branch: str, nonce: int):
    return GitHubClient().get_commits(owner, repo, branch)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_tree(owner: str, repo: str, branch: str, nonce: int):
    return GitHubClient().get_tree(owner, repo, branch)


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _cached_file_content(owner: str, repo: str, path: str, branch: str, nonce: int):
    return GitHubClient().get_file_content(owner, repo, path, branch)


def _snapshot(analysis: object) -> dict:
    repo = analysis.repository
    metrics = analysis.metrics or {}
    engineering = metrics.get("engineering_intelligence", {}) or {}
    activity = metrics.get("activity_intelligence", {}) or {}
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
        "activity_score": min(100.0, (activity.get("recent_30d_commits", 0) * 8) + (metrics.get("active_contributors", 0) * 4)),
        "engineering_score": engineering.get("engineering_score", 0),
        "documentation_score": engineering.get("documentation_score", 0),
        "testing_score": engineering.get("testing_score", 0),
        "dependencies_observed": engineering.get("dependencies_observed", 0),
        "engineering": engineering.get("engineering_score", 0),
        "documentation": engineering.get("documentation_score", 0),
        "testing": engineering.get("testing_score", 0),
    }


def _friendly_error(exc: Exception) -> str:
    if isinstance(exc, GitHubAPIError):
        if exc.status_code == 404:
            return "Repository not found. Check the owner/repository name and make sure the repository is public or your token has access."
        if exc.status_code in (401, 403):
            return "GitHub denied the request or the API rate limit was reached. Configure a GitHub token in your deployment secrets or try again later."
        return f"GitHub request failed: {exc}"
    return str(exc)


def _prepare_scan(tree: list[dict], owner: str, repo: str, branch: str, nonce: int, deep_scan: bool) -> tuple[dict, list[dict]]:
    source_items = []
    for item in tree:
        path = item.get("path", "")
        if item.get("type") != "blob" or item.get("size", 0) > 200_000:
            continue
        if any(part in {".git", ".venv", "node_modules", "dist", "build", "coverage"} for part in path.split("/")):
            continue
        source_items.append(item)

    engineering_files = []
    for item in source_items:
        filename = item.get("path", "")
        base = filename.rsplit("/", 1)[-1]
        # Dependency manifests and documentation are cheap, high-value files to inspect.
        if base in {"requirements.txt", "pyproject.toml", "Pipfile", "package.json", "pom.xml", "build.gradle", "build.gradle.kts", "pubspec.yaml", "go.mod", "Cargo.toml", "Gemfile", "composer.json", "README.md", "README.rst", "CONTRIBUTING.md"}:
            content = _cached_file_content(owner, repo, filename, branch, nonce)
            if content:
                engineering_files.append({"path": filename, "content": content})

    code_files = []
    if deep_scan:
        for item in source_items[:MAX_CODE_FILES]:
            path = item.get("path", "")
            content = _cached_file_content(owner, repo, path, branch, nonce)
            if content:
                code_files.append({"path": path, "content": content})

    engineering = analyze_engineering(tree, engineering_files)
    if deep_scan:
        code = analyze_files(code_files)
        code["scan_limit"] = MAX_CODE_FILES
        code["tree_files_found"] = len(source_items)
    else:
        code = {}
    return engineering, code


def _render_history(repo_name: str):
    snapshots = get_snapshots(repo_name, limit=20)
    if not snapshots:
        st.info("No persistent history exists yet. Re-analyze this repository later to build a trend history.")
        return
    st.markdown("### Persistent history")
    st.caption("Snapshots are stored locally in RepoPulse's SQLite history database.")
    rows = [
        {"Captured": item["captured_at"], "Stars": item["stars"], "Forks": item["forks"], "Issues": item["open_issues"], "PRs": item["open_pull_requests"], "Contributors": item["contributors"], "Commits": item["recent_commits"], "Health": item["health_score"], "Engineering": item.get("engineering_score", 0)}
        for item in reversed(snapshots)
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def repository_page():
    init_db()
    st.subheader("Repository overview", divider="blue")
    st.caption("Analyze a GitHub repository and build a cached, evidence-based intelligence profile.")

    st.session_state.setdefault("repo_session_count", 0)
    st.session_state.setdefault("repo_session_history", [])
    st.session_state.setdefault("repo_snapshots", {})
    st.session_state.setdefault("repository_input", "microsoft/vscode")
    st.session_state.setdefault("repo_cache_nonce", 0)

    col1, col2 = st.columns([4, 1])
    with col1:
        repository = st.text_input("GitHub repository", key="repository_input", placeholder="https://github.com/owner/repository or owner/repository")
    with col2:
        st.write("")
        st.write("")
        same_repo = bool(st.session_state.get("current_repo") and st.session_state.current_repo.lower() == repository.strip().lower())
        analyze_clicked = st.button("Refresh live data" if same_repo else "Analyze", use_container_width=True, type="primary")

    deep_scan = st.checkbox("Run deep code scan", value=False, help="Downloads a bounded set of source files. Cached requests make repeated scans faster.")

    if analyze_clicked:
        if st.session_state.repo_session_count >= MAX_ANALYSES:
            st.warning(f"This browser session has reached the {MAX_ANALYSES}-repository analysis limit.")
            return
        try:
            if same_repo:
                st.session_state.repo_cache_nonce += 1
            nonce = st.session_state.repo_cache_nonce
            repo_owner, repo_name = parse_repository_input(_normalize_repository_input(repository))
            client = GitHubClient()
            progress = st.progress(0, text="Connecting to GitHub…")
            repo_data = _cached_repository(repo_owner, repo_name, nonce)
            progress.progress(16, text="Loading repository metadata…")
            contributors_data = _cached_contributors(repo_owner, repo_name, nonce)
            progress.progress(29, text="Loading contributors…")
            pull_requests_data = _cached_prs(repo_owner, repo_name, nonce)
            progress.progress(42, text="Loading pull requests…")
            issues_data = _cached_issues(repo_owner, repo_name, nonce)
            progress.progress(55, text="Loading issues…")
            languages_data = _cached_languages(repo_owner, repo_name, nonce)
            progress.progress(66, text="Loading languages and activity…")
            commits_data = _cached_commits(repo_owner, repo_name, repo_data.get("default_branch", "main"), nonce)
            progress.progress(76, text="Building repository inventory…")
            tree_data = _cached_tree(repo_owner, repo_name, repo_data.get("default_branch", "main"), nonce)
            progress.progress(84, text="Calculating engineering intelligence…")
            analysis = analyze_repository(repo_data, contributors_data, languages_data, issues_data, pull_requests_data, commits_data, tree_data=tree_data)

            engineering, code_metrics = _prepare_scan(tree_data, repo_owner, repo_name, analysis.repository.default_branch or "main", nonce, deep_scan)
            analysis.metrics["engineering_intelligence"] = engineering
            if deep_scan:
                analysis.metrics["code_analysis"] = code_metrics
            progress.progress(94, text="Checking API capacity…")
            try:
                st.session_state.api_rate_limit = client.get_rate_limit()
            except Exception:
                st.session_state.api_rate_limit = None

            snapshot = _snapshot(analysis)
            full_name = f"{repo_owner}/{repo_name}"
            st.session_state.previous_snapshot = st.session_state.repo_snapshots.get(full_name)
            save_snapshot(snapshot)
            st.session_state.last_refresh = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
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
    if analysis is None:
        return

    rate = st.session_state.get("api_rate_limit") or {}
    resources = rate.get("resources", {}) if isinstance(rate, dict) else {}
    core = resources.get("core", {}) if isinstance(resources, dict) else {}
    if core and core.get("remaining") is not None and core.get("limit"):
        remaining, limit = core["remaining"], core["limit"]
        tone = "good" if remaining / limit > .25 else "warning" if remaining / limit > .1 else "danger"
        st.markdown(f'<span class="status-badge {tone}">API {remaining:,} / {limit:,} requests remaining</span>', unsafe_allow_html=True)

    repo = analysis.repository
    metrics = analysis.metrics or {}
    engineering = metrics.get("engineering_intelligence", {}) or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stars", f"{repo.stars:,}")
    c2.metric("Forks", f"{repo.forks:,}")
    c3.metric("Recent commits", f"{metrics.get('recent_commit_count', 0):,}")
    c4.metric("Health", f"{metrics.get('repository_health_score', 0):.1f}/100")

    st.markdown("### Engineering pulse")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Engineering", f"{engineering.get('engineering_score', 0):.1f}/100")
    e2.metric("Documentation", f"{engineering.get('documentation_score', 0):.1f}/100")
    e3.metric("Testing", f"{engineering.get('testing_score', 0):.1f}/100")
    e4.metric("Dependencies", f"{engineering.get('dependencies_observed', 0):,}")

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Repository profile")
        st.markdown(repo.description or "No repository description provided.")
        profile = [
            {"Field": "Repository", "Value": repo.full_name or repo.name},
            {"Field": "Default branch", "Value": repo.default_branch or "N/A"},
            {"Field": "Primary language", "Value": repo.language or "N/A"},
            {"Field": "Open PRs", "Value": metrics.get("open_pull_request_count", 0)},
            {"Field": "Contributors", "Value": metrics.get("total_contributors", 0)},
            {"Field": "Bus factor", "Value": metrics.get("bus_factor", 0)},
        ]
        st.dataframe(profile, use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Activity intelligence")
        activity = metrics.get("activity_intelligence", {}) or {}
        st.metric("Activity status", activity.get("status", "Unknown"))
        trend = activity.get("commit_trend_pct", 0)
        st.metric("30-day commit trend", f"{trend:+.1f}%")
        st.caption(f"Last commit: {activity.get('last_commit_days_ago', 0)} days ago · {activity.get('active_days', 0)} active days observed")
        if activity.get("peak_commit_weekday"):
            st.caption(f"Peak commit weekday: {activity['peak_commit_weekday']}")

    if engineering:
        st.markdown("### Engineering signals")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("**Documentation**")
            st.write("README ✓" if engineering.get("has_readme") else "README ✗")
            st.write("License ✓" if engineering.get("has_license") else "License ✗")
            st.write("Contributing ✓" if engineering.get("has_contributing") else "Contributing ✗")
        with s2:
            st.markdown("**Testing**")
            st.write(engineering.get("testing_status", "Unknown"))
            st.caption(f"{engineering.get('test_files', 0)} test files / {engineering.get('source_files', 0)} source files")
        with s3:
            st.markdown("**Dependencies**")
            st.write(engineering.get("dependency_status", "Unknown"))
            st.caption(f"{len(engineering.get('dependency_manifests', []))} manifest(s) detected")

    if metrics.get("code_analysis"):
        code = metrics["code_analysis"]
        st.markdown("### Code scan result")
        a, b, c, d = st.columns(4)
        a.metric("Files analyzed", code.get("files_analyzed", 0))
        b.metric("Lines", f"{code.get('total_lines', 0):,}")
        c.metric("Avg complexity", code.get("avg_complexity", 0))
        d.metric("Status", code.get("status", "Unknown"))
    else:
        st.info("Deep code metrics are optional. Enable **Run deep code scan** and refresh to inspect source-level complexity.")

    _render_history(repo.full_name or repo.name)
