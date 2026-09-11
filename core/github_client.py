from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from config.settings import settings


class GitHubAPIError(RuntimeError):
    """User-friendly GitHub API error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GitHubRateLimitError(GitHubAPIError):
    pass


class GitHubNotFoundError(GitHubAPIError):
    pass


class GitHubClient:
    """Small GitHub REST client with pagination and rate-limit awareness."""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or settings.github_token
        self.base_url = (base_url or settings.github_api_base_url).rstrip("/")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.session.headers.update({"Accept": "application/vnd.github+json"})

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=20)
        except requests.RequestException as exc:
            raise GitHubAPIError("GitHub could not be reached. Check your internet connection and try again.") from exc

        if response.status_code == 404:
            raise GitHubNotFoundError("The requested GitHub resource was not found.", 404)
        if response.status_code in (403, 429) and response.headers.get("X-RateLimit-Remaining") == "0":
            reset = response.headers.get("X-RateLimit-Reset")
            suffix = f" Rate limit resets at Unix time {reset}." if reset else ""
            raise GitHubRateLimitError(f"GitHub API rate limit reached.{suffix}", response.status_code)
        if not response.ok:
            try:
                detail = response.json().get("message", response.reason)
            except ValueError:
                detail = response.reason
            raise GitHubAPIError(f"GitHub API request failed: {detail}", response.status_code)
        return response.json()

    def get_rate_limit(self) -> Dict[str, Any]:
        return self._request("/rate_limit")

    def _request_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: int = 10,
        per_page: int = 100,
    ) -> List[Dict[str, Any]]:
        base_params = dict(params or {})
        results: List[Dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            page_params = {**base_params, "per_page": per_page, "page": page}
            payload = self._request(endpoint, page_params)
            if not isinstance(payload, list):
                return payload
            results.extend(payload)
            if len(payload) < per_page:
                break
        return results

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._request(f"/repos/{owner}/{repo}")

    def get_contributors(self, owner: str, repo: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        return self._request_paginated(f"/repos/{owner}/{repo}/contributors", max_pages=max_pages)

    def get_commits(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        max_pages: int = 3,
    ) -> List[Dict[str, Any]]:
        params = {"sha": branch} if branch else {}
        return self._request_paginated(f"/repos/{owner}/{repo}/commits", params=params, max_pages=max_pages)

    def get_pull_requests(self, owner: str, repo: str, state: str = "all", max_pages: int = 10) -> List[Dict[str, Any]]:
        return self._request_paginated(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "sort": "updated", "direction": "desc"},
            max_pages=max_pages,
        )

    def get_issues(self, owner: str, repo: str, state: str = "all", max_pages: int = 10) -> List[Dict[str, Any]]:
        return self._request_paginated(
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "sort": "updated", "direction": "desc"},
            max_pages=max_pages,
        )

    def get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._request(f"/repos/{owner}/{repo}/languages")
