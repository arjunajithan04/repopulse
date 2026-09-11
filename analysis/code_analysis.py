from __future__ import annotations

import ast
from pathlib import PurePosixPath
from typing import Any, Dict, List

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".kts", ".dart", ".css", ".scss",
    ".html", ".vue", ".sql",
}
IGNORED_PARTS = {".git", ".venv", "node_modules", "dist", "build", "coverage"}


def _python_complexity(source: str) -> tuple[int, int, int]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0, 0, 0
    complexity = 0
    functions = 0
    classes = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1
            complexity += 1
        elif isinstance(node, ast.ClassDef):
            classes += 1
        elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.ExceptHandler, ast.IfExp, ast.BoolOp)):
            complexity += 1
    return complexity, functions, classes


def analyze_files(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    total_lines = 0
    total_complexity = 0
    total_functions = 0
    total_classes = 0

    for item in files:
        path = str(item.get("path", ""))
        content = str(item.get("content", ""))
        suffix = PurePosixPath(path).suffix.lower()
        if not content or suffix not in SUPPORTED_EXTENSIONS:
            continue
        lines = len(content.splitlines())
        complexity = functions = classes = 0
        if suffix == ".py":
            complexity, functions, classes = _python_complexity(content)
        total_lines += lines
        total_complexity += complexity
        total_functions += functions
        total_classes += classes
        rows.append({
            "file": path,
            "language": suffix.lstrip("."),
            "lines": lines,
            "complexity": complexity,
            "functions": functions,
            "classes": classes,
        })

    avg_complexity = total_complexity / len(rows) if rows else 0
    if not rows:
        status = "No analyzable source files"
    elif avg_complexity <= 3:
        status = "Healthy"
    elif avg_complexity <= 8:
        status = "Moderate"
    else:
        status = "Needs attention"

    return {
        "files_analyzed": len(rows),
        "total_lines": total_lines,
        "total_complexity": total_complexity,
        "avg_complexity": round(avg_complexity, 2),
        "functions": total_functions,
        "classes": total_classes,
        "status": status,
        "files": sorted(rows, key=lambda row: row["lines"], reverse=True),
    }


def summarize_code_health(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    return analyze_files(files)
