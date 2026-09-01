from __future__ import annotations

from typing import Any, Dict, List


def summarize_code_health(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_lines = sum(item.get("lines", 0) for item in files)
    total_complexity = sum(item.get("complexity", 0) for item in files)
    return {
        "files_analyzed": len(files),
        "total_lines": total_lines,
        "total_complexity": total_complexity,
        "avg_complexity": round((total_complexity / len(files)), 2) if files else 0,
        "status": "Healthy" if total_complexity < 250 else "Needs attention",
    }
