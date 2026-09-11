from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "repopulse.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repository_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                open_pull_requests INTEGER DEFAULT 0,
                contributors INTEGER DEFAULT 0,
                recent_commits INTEGER DEFAULT 0,
                health_score REAL DEFAULT 0,
                health_dimensions TEXT DEFAULT '{}',
                activity_score REAL DEFAULT 0,
                engineering_score REAL DEFAULT 0,
                documentation_score REAL DEFAULT 0,
                testing_score REAL DEFAULT 0,
                dependencies_observed INTEGER DEFAULT 0
            )
        """)
        existing = {row[1] for row in conn.execute("PRAGMA table_info(repository_snapshots)").fetchall()}
        migrations = {
            "activity_score": "REAL DEFAULT 0",
            "engineering_score": "REAL DEFAULT 0",
            "documentation_score": "REAL DEFAULT 0",
            "testing_score": "REAL DEFAULT 0",
            "dependencies_observed": "INTEGER DEFAULT 0",
        }
        for column, definition in migrations.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE repository_snapshots ADD COLUMN {column} {definition}")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_repo_time ON repository_snapshots(full_name, captured_at)")


def save_snapshot(snapshot: dict[str, Any]) -> None:
    init_db()
    with _connect() as conn:
        conn.execute("""
            INSERT INTO repository_snapshots
            (full_name, captured_at, stars, forks, open_issues, open_pull_requests,
             contributors, recent_commits, health_score, health_dimensions,
             activity_score, engineering_score, documentation_score, testing_score, dependencies_observed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.get("full_name", ""), snapshot.get("timestamp", ""), snapshot.get("stars", 0), snapshot.get("forks", 0),
            snapshot.get("issues", 0), snapshot.get("pull_requests", 0), snapshot.get("contributors", 0), snapshot.get("commits", 0),
            snapshot.get("health", 0), json.dumps(snapshot.get("health_dimensions", {})), snapshot.get("activity_score", 0),
            snapshot.get("engineering_score", 0), snapshot.get("documentation_score", 0), snapshot.get("testing_score", 0),
            snapshot.get("dependencies_observed", 0),
        ))


def get_snapshots(full_name: str, limit: int = 30) -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM repository_snapshots WHERE lower(full_name) = lower(?) ORDER BY captured_at DESC, id DESC LIMIT ?",
            (full_name, limit),
        ).fetchall()
    results = []
    for row in rows:
        item = dict(row)
        try:
            item["health_dimensions"] = json.loads(item.get("health_dimensions") or "{}")
        except json.JSONDecodeError:
            item["health_dimensions"] = {}
        results.append(item)
    return results


def get_latest_snapshot(full_name: str) -> dict[str, Any] | None:
    snapshots = get_snapshots(full_name, limit=1)
    return snapshots[0] if snapshots else None
