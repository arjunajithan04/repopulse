from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from config.settings import settings


class GitHubAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class GitHubClient:
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
            raise GitHubAPIError(f"Could not connect to GitHub: {exc}") from exc

        if response.status_code >= 400:
            try:
                payload = response.json()
                message = payload.get("message", response.reason)
            except ValueError:
                message = response.reason
            raise GitHubAPIError(message or "GitHub request failed", response.status_code)
        return response.json()

    def _request_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: int = 5,
        per_page: int = 100,
    ) -> List[Dict[str, Any]]:
        base_params = dict(params or {})
        base_params["per_page"] = min(per_page, 100)
        results: List[Dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            page_params = {**base_params, "page": page}
            data = self._request(endpoint, page_params)
            if not isinstance(data, list):
                return results
            results.extend(data)
            if len(data) < base_params["per_page"]:
                break
        return results

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._request(f"/repos/{owner}/{repo}")

    def get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        try:
            return self._request_paginated(f"/repos/{owner}/{repo}/contributors", max_pages=5)
        except GitHubAPIError:
            return []

    def get_commits(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if branch:
            params["sha"] = branch
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        try:
            return self._request_paginated(f"/repos/{owner}/{repo}/commits", params=params, max_pages=5)
        except GitHubAPIError:
            return []

    def get_pull_requests(self, owner: str, repo: str, state: str = "all") -> List[Dict[str, Any]]:
        try:
            return self._request_paginated(
                f"/repos/{owner}/{repo}/pulls", params={"state": state, "sort": "updated", "direction": "desc"}, max_pages=5
            )
        except GitHubAPIError:
            return []

    def get_issues(self, owner: str, repo: str, state: str = "all") -> List[Dict[str, Any]]:
        try:
            return self._request_paginated(
                f"/repos/{owner}/{repo}/issues", params={"state": state, "sort": "updated", "direction": "desc"}, max_pages=5
            )
        except GitHubAPIError:
            return []

    def get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        try:
            return self._request(f"/repos/{owner}/{repo}/languages")
        except GitHubAPIError:
            return {}

    def get_rate_limit(self) -> Dict[str, Any]:
        try:
            return self._request("/rate_limit")
        except GitHubAPIError:
            return {}

    def get_tree(self, owner: str, repo: str, branch: str = "main") -> List[Dict[str, Any]]:
        try:
            data = self._request(f"/repos/{owner}/{repo}/git/trees/{branch}", params={"recursive": "1"})
            return data.get("tree", []) if isinstance(data, dict) else []
        except GitHubAPIError:
            return []

    def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> str:
        params = {"ref": ref} if ref else None
        try:
            data = self._request(f"/repos/{owner}/{repo}/contents/{path}", params=params)
            if data.get("encoding") == "base64" and data.get("content"):
                import base64
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return data.get("content", "")
        except (GitHubAPIError, UnicodeDecodeError):
            return ""
