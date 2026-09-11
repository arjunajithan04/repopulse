from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import streamlit as st

from analysis.repository_analysis import analyze_repository, parse_repository_input
from core.github_client import GitHubAPIError, GitHubClient, GitHubNotFoundError, GitHubRateLimitError


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_repository_bundle(owner: str, repo: str) -> Dict[str, Any]:
    client = GitHubClient()
    repo_data = client.get_repository(owner, repo)
    contributors_data = client.get_contributors(owner, repo)
    pull_requests_data = client.get_pull_requests(owner, repo)
    issues_data = client.get_issues(owner, repo)
    languages_data = client.get_languages(owner, repo)
    commits_data = client.get_commits(owner, repo, repo_data.get("default_branch"))
    return {
        "repo_data": repo_data,
        "contributors_data": contributors_data,
        "pull_requests_data": pull_requests_data,
        "issues_data": issues_data,
        "languages_data": languages_data,
        "commits_data": commits_data,
    }


def _snapshot(analysis: object) -> Dict[str, Any]:
    repo = analysis.repository
    metrics = analysis.metrics
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stars": repo.stars,
        "forks": repo.forks,
        "issues": metrics.get("open_issue_count", 0),
        "prs": metrics.get("open_pull_request_count", 0),
        "contributors": metrics.get("total_contributors", 0),
        "commits": metrics.get("recent_commit_count", 0),
        "health": metrics.get("repository_health_score", 0),
    }


def _store_snapshot(repo_name: str, analysis: object) -> None:
    snapshots = st.session_state.setdefault("repo_snapshots", {})
    history = snapshots.setdefault(repo_name, [])
    history.append(_snapshot(analysis))
    # Keep a useful local history without allowing session state to grow forever.
    snapshots[repo_name] = history[-20:]


def _normalize_repository_input(value: str) -> str:
    candidate = (value or "").strip()
    if not candidate:
        raise ValueError("Please enter a GitHub repository URL or owner/repository.")
    return candidate


def repository_page():
    st.subheader("Repository intelligence", divider="blue")

    st.markdown(
        """
        <div class="repo-input-card">
            <div class="repo-input-title">Analyze a GitHub repository</div>
            <div class="repo-input-subtitle">Paste a GitHub URL or use the owner/repository format.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "repo_session_count" not in st.session_state:
        st.session_state.repo_session_count = 0
    if "repo_session_history" not in st.session_state:
        st.session_state.repo_session_history = []

    repo_value = st.text_input(
        "GitHub repository",
        value="microsoft/vscode",
        placeholder="https://github.com/owner/repository",
        label_visibility="collapsed",
    )

    analyze_clicked = st.button("Analyze repository", type="primary", use_container_width=True)

    if analyze_clicked:
        if st.session_state.repo_session_count >= 10:
            st.warning("This browser session has reached the 10-repository analysis limit.")
            return

        try:
            owner, repo_name = parse_repository_input(_normalize_repository_input(repo_value))
            with st.status("Analyzing repository...", expanded=True) as status:
                st.write("Fetching repository metadata")
                bundle = _fetch_repository_bundle(owner, repo_name)
                st.write("Analyzing contributors, issues, pull requests and commits")
                analysis = analyze_repository(**bundle)
                st.write("Calculating repository health signals")
                status.update(label="Analysis complete", state="complete", expanded=False)

            st.session_state.repo_session_count += 1
            full_name = f"{owner}/{repo_name}"
            if full_name not in st.session_state.repo_session_history:
                st.session_state.repo_session_history.append(full_name)
            st.session_state.current_repo = full_name
            st.session_state.repo_analysis = analysis
            _store_snapshot(full_name, analysis)

            st.success(f"Analyzed {full_name} · {st.session_state.repo_session_count}/10 analyses this session")
            st.markdown(f"### {full_name}")
            if analysis.repository.description:
                st.caption(analysis.repository.description)
            st.info(analysis.summary)

            metrics = analysis.metrics
            cols = st.columns(4)
            cards = [
                ("Stars", analysis.repository.stars),
                ("Forks", analysis.repository.forks),
                ("Contributors", metrics.get("total_contributors", 0)),
                ("Health", f"{metrics.get('repository_health_score', 0)}/100"),
            ]
            for col, (label, value) in zip(cols, cards):
                with col:
                    st.metric(label, value)

            st.markdown("### Repository profile")
            profile = {
                "Owner": owner,
                "Repository": repo_name,
                "Default branch": analysis.repository.default_branch,
                "Visibility": "Private" if bundle["repo_data"].get("private") else "Public",
                "Primary language": analysis.repository.language or "N/A",
                "Open issues": metrics.get("open_issue_count", 0),
                "Open PRs": metrics.get("open_pull_request_count", 0),
                "Recent commits analyzed": metrics.get("recent_commit_count", 0),
                "Languages detected": metrics.get("languages_total", 0),
            }
            st.dataframe(list(profile.items()), hide_index=True, use_container_width=True, column_config={"0": "Field", "1": "Value"})

        except GitHubNotFoundError:
            st.error(f"Repository not found: {repo_value}. Check the owner and repository name.")
        except GitHubRateLimitError as exc:
            st.error(str(exc))
        except GitHubAPIError as exc:
            st.error(str(exc))
        except ValueError as exc:
            st.warning(str(exc))
        except Exception:
            st.error("RepoPulse could not complete the analysis. Please try again.")

    current = st.session_state.get("repo_analysis")
    if current is not None:
        st.caption(f"Current analysis: {st.session_state.get('current_repo', current.repository.full_name)}")

    history = st.session_state.get("repo_session_history", [])
    if history:
        st.markdown("### Recent analyses")
        st.dataframe(
            [{"Repository": repo, "Analyses": len(st.session_state.get("repo_snapshots", {}).get(repo, []))} for repo in reversed(history)],
            hide_index=True,
            use_container_width=True,
        )
