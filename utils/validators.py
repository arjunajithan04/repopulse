from __future__ import annotations


def is_valid_github_owner(value: str) -> bool:
    return bool(value and value.strip() and value.strip() not in {"/", " "})


def is_valid_repository_name(value: str) -> bool:
    return bool(value and value.strip() and "/" not in value.strip())
