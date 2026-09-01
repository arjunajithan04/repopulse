from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RepositoryStats:
    name: str
    full_name: str
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    watchers: int = 0
    default_branch: str = "main"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ContributorStats:
    login: str
    contributions: int = 0
    commits: int = 0
    pull_requests: int = 0
    issues: int = 0
    avatar_url: Optional[str] = None


@dataclass
class AnalysisResult:
    repository: RepositoryStats
    contributors: List[ContributorStats] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
