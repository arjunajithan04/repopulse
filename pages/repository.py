from __future__ import annotations

import streamlit as st

from analysis.repository_analysis import analyze_repository, parse_repository_input
from core.github_client import GitHubClient


def _normalize_repository_input(owner: str, repo: str) -> str:
    owner_value = (owner or "").strip()
    repo_value = (repo or "").strip()
    if not owner_value and not repo_value:
        raise ValueError("Please enter a repository owner and name.")
    if "github.com" in owner_value or "/" in owner_value:
        return owner_value
    if repo_value.startswith("http"):
        return repo_value
    return f"{owner_value}/{repo_value}"


def _set_last_analysis(analysis: object) -> None:
    st.session_state["repo_analysis"] = analysis
    st.session_state["repo_analysis_time"] = st.Timestamp.now() if hasattr(st, "Timestamp") else None


def repository_page():
    st.subheader("Repository overview", divider="blue")

    if "repo_session_count" not in st.session_state:
        st.session_state.repo_session_count = 0
    if "repo_session_history" not in st.session_state:
        st.session_state.repo_session_history = []

    col1, col2 = st.columns(2)
    with col1:
        owner = st.text_input("GitHub owner", value="microsoft")
    with col2:
        repo = st.text_input("Repository name", value="vscode")

    if st.button("Analyze repository"):
        if st.session_state.repo_session_count >= 10:
            st.warning("This browser session has already analyzed 10 repositories. Refresh the page to start a new session.")
            return

        try:
            repo_input = _normalize_repository_input(owner, repo)
            repo_owner, repo_name = parse_repository_input(repo_input)
            client = GitHubClient()

            repo_data = client.get_repository(repo_owner, repo_name)
            contributors_data = client.get_contributors(repo_owner, repo_name)
            pull_requests_data = client.get_pull_requests(repo_owner, repo_name)
            issues_data = client.get_issues(repo_owner, repo_name)
            languages_data = client.get_languages(repo_owner, repo_name)
            commits_data = client.get_commits(repo_owner, repo_name, repo_data.get("default_branch"))

            analysis = analyze_repository(
                repo_data=repo_data,
                contributors_data=contributors_data,
                languages_data=languages_data,
                issues_data=issues_data,
                pull_requests_data=pull_requests_data,
                commits_data=commits_data,
            )

            st.session_state.repo_session_count += 1
            st.session_state.repo_session_history.append(f"{repo_owner}/{repo_name}")
            st.session_state.current_repo = f"{repo_owner}/{repo_name}"
            st.session_state.repo_analysis = analysis

            st.success(f"Analyzed {repo_owner}/{repo_name} ({st.session_state.repo_session_count}/10 this session)")
            st.write(analysis.summary)

            st.markdown("### Repository snapshot")
            st.markdown(
                f"""
                | Field | Value |
                |---|---|
                | Owner | {repo_owner} |
                | Repository | {repo_name} |
                | Default branch | {analysis.repository.default_branch} |
                | Visibility | {'Private' if repo_data.get('private') else 'Public'} |
                | Primary language | {analysis.repository.language or 'N/A'} |
                | Stars | {analysis.repository.stars} |
                | Forks | {analysis.repository.forks} |
                | Open issues | {analysis.metrics.get('open_issue_count', 0)} |
                | Open PRs | {analysis.metrics.get('open_pull_request_count', 0)} |
                """
            )

            st.markdown("### Contributor and quality summary")
            st.write({
                "total_contributors": analysis.metrics.get("total_contributors", 0),
                "top_contributor": analysis.metrics.get("top_contributor"),
                "health_score": analysis.metrics.get("repository_health_score", 0),
                "language_breakdown": analysis.metrics.get("language_breakdown", {}),
                "recent_commit_count": analysis.metrics.get("recent_commit_count", 0),
            })

        except Exception as exc:
            st.error(f"Unable to analyze the repository: {exc}")

    if "repo_analysis" in st.session_state and st.session_state.repo_analysis is not None:
        current = st.session_state.repo_analysis
        st.caption(f"Current analysis: {st.session_state.get('current_repo', current.repository.full_name or 'Repository')}")

    if st.session_state.repo_session_history:
        st.caption(f"Analyzed this session: {', '.join(st.session_state.repo_session_history)}")
