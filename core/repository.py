from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Repository:
    name: str
    full_name: str
    private: bool = False
    description: Optional[str] = None
    default_branch: str = "main"
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    subscribers_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "Repository":
        return cls(
            name=payload.get("name", ""),
            full_name=payload.get("full_name", ""),
            private=payload.get("private", False),
            description=payload.get("description"),
            default_branch=payload.get("default_branch", "main"),
            language=payload.get("language"),
            stargazers_count=payload.get("stargazers_count", 0),
            forks_count=payload.get("forks_count", 0),
            open_issues_count=payload.get("open_issues_count", 0),
            subscribers_count=payload.get("subscribers_count", 0),
            created_at=payload.get("created_at"),
            updated_at=payload.get("updated_at"),
        )
