from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from config.settings import settings


class GitHubClient:
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or settings.github_token
        self.base_url = (base_url or settings.github_api_base_url).rstrip("/")
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        self.session.headers.update({"Accept": "application/vnd.github+json"})

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._request(f"/repos/{owner}/{repo}")

    def get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        try:
            return self._request(f"/repos/{owner}/{repo}/contributors")
        except requests.HTTPError:
            return []

    def get_commits(self, owner: str, repo: str, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"sha": branch} if branch else None
        try:
            return self._request(f"/repos/{owner}/{repo}/commits", params=params)
        except requests.HTTPError:
            return []

    def get_pull_requests(self, owner: str, repo: str, state: str = "all") -> List[Dict[str, Any]]:
        try:
            return self._request(f"/repos/{owner}/{repo}/pulls", params={"state": state})
        except requests.HTTPError:
            return []

    def get_issues(self, owner: str, repo: str, state: str = "all") -> List[Dict[str, Any]]:
        try:
            return self._request(f"/repos/{owner}/{repo}/issues", params={"state": state, "per_page": 100})
        except requests.HTTPError:
            return []

    def get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        try:
            return self._request(f"/repos/{owner}/{repo}/languages")
        except requests.HTTPError:
            return {}
