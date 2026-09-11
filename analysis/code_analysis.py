from __future__ import annotations

import ast
import re
from pathlib import PurePosixPath
from typing import Any, Dict, List

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".kts", ".dart", ".css", ".scss",
    ".html", ".vue", ".sql",
}
IGNORED_PARTS = {".git", ".venv", "node_modules", "dist", "build", "coverage", "vendor"}


def _python_complexity(source: str) -> tuple[int, int, int]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0, 0, 0
    complexity = 1
    functions = 0
    classes = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions += 1
        elif isinstance(node, ast.ClassDef):
            classes += 1
        elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try,
                              ast.With, ast.AsyncWith, ast.ExceptHandler, ast.IfExp,
                              ast.BoolOp, ast.Match, ast.comprehension)):
            complexity += 1
    return complexity, functions, classes


def _generic_complexity(source: str, suffix: str) -> tuple[int, int, int]:
    """Lightweight heuristic for non-Python files; deliberately labelled as heuristic."""
    lines = source.splitlines()
    branch_patterns = re.compile(r"\b(if|else\s+if|for|while|case|catch|switch)\b|&&|\|\|")
    function_patterns = {
        ".js": re.compile(r"\b(function|def)\b|=>"),
        ".jsx": re.compile(r"\b(function|def)\b|=>"),
        ".ts": re.compile(r"\b(function|def)\b|=>"),
        ".tsx": re.compile(r"\b(function|def)\b|=>"),
        ".go": re.compile(r"\bfunc\b"),
        ".rs": re.compile(r"\bfn\b"),
        ".php": re.compile(r"\bfunction\b"),
        ".rb": re.compile(r"\bdef\b"),
        ".swift": re.compile(r"\bfunc\b"),
        ".kt": re.compile(r"\bfun\b"),
        ".kts": re.compile(r"\bfun\b"),
        ".dart": re.compile(r"\b(?:void|Future|String|int|bool|double)\s+\w+\s*\("),
        ".java": re.compile(r"\b(public|private|protected)\s+[\w<>\[\], ?]+\s+\w+\s*\("),
        ".c": re.compile(r"\b(?:int|void|char|float|double|long)\s+\w+\s*\("),
        ".cpp": re.compile(r"\b(?:int|void|char|float|double|auto|bool)\s+\w+\s*\("),
    }
    function_re = function_patterns.get(suffix)
    functions = sum(1 for line in lines if function_re and function_re.search(line))
    branches = sum(1 for line in lines if branch_patterns.search(line))
    complexity = max(1, functions + branches)
    return complexity, functions, 0


def _comment_lines(source: str, suffix: str) -> int:
    markers = {
        ".py": "#", ".js": "//", ".jsx": "//", ".ts": "//", ".tsx": "//",
        ".java": "//", ".c": "//", ".cpp": "//", ".h": "//", ".hpp": "//",
        ".go": "//", ".rs": "//", ".php": "//", ".rb": "#", ".swift": "//",
        ".kt": "//", ".kts": "//", ".dart": "//", ".css": "/*", ".scss": "//",
        ".html": "<!--", ".vue": "<!--", ".sql": "--",
    }
    marker = markers.get(suffix)
    if not marker:
        return 0
    return sum(1 for line in source.splitlines() if line.strip().startswith(marker))


def analyze_files(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    total_lines = 0
    total_complexity = 0
    total_functions = 0
    total_classes = 0
    total_comment_lines = 0

    for item in files:
        path = str(item.get("path", ""))
        content = str(item.get("content", ""))
        suffix = PurePosixPath(path).suffix.lower()
        if not content or suffix not in SUPPORTED_EXTENSIONS:
            continue
        if any(part in IGNORED_PARTS for part in PurePosixPath(path).parts):
            continue

        lines = len(content.splitlines())
        if suffix == ".py":
            complexity, functions, classes = _python_complexity(content)
            analysis_type = "AST"
        else:
            complexity, functions, classes = _generic_complexity(content, suffix)
            analysis_type = "heuristic"
        comments = _comment_lines(content, suffix)
        total_lines += lines
        total_complexity += complexity
        total_functions += functions
        total_classes += classes
        total_comment_lines += comments
        rows.append({
            "file": path,
            "language": suffix.lstrip("."),
            "lines": lines,
            "complexity": complexity,
            "functions": functions,
            "classes": classes,
            "comment_lines": comments,
            "comment_ratio": round((comments / lines) * 100, 1) if lines else 0,
            "analysis_type": analysis_type,
        })

    avg_complexity = total_complexity / len(rows) if rows else 0
    avg_file_lines = total_lines / len(rows) if rows else 0
    comment_ratio = (total_comment_lines / total_lines * 100) if total_lines else 0

    if not rows:
        status = "No analyzable source files"
        quality_score = 0
    else:
        status = "Healthy" if avg_complexity <= 3 else "Moderate" if avg_complexity <= 8 else "Needs attention"
        complexity_score = max(0, min(100, 100 - max(0, avg_complexity - 1) * 9))
        size_score = max(0, min(100, 100 - max(0, avg_file_lines - 250) * 0.12))
        documentation_score = min(100, comment_ratio * 4)
        quality_score = round(complexity_score * 0.55 + size_score * 0.25 + documentation_score * 0.20, 1)

    largest = sorted(rows, key=lambda row: row["lines"], reverse=True)[:10]
    complex_files = sorted(rows, key=lambda row: row["complexity"], reverse=True)[:10]
    flags = []
    if avg_complexity > 8:
        flags.append("High average complexity")
    if avg_file_lines > 400:
        flags.append("Large average file size")
    if comment_ratio < 5 and rows:
        flags.append("Low comment/documentation ratio")
    if any(row["lines"] > 800 for row in rows):
        flags.append("Very large source files detected")

    return {
        "files_analyzed": len(rows),
        "total_lines": total_lines,
        "total_complexity": total_complexity,
        "avg_complexity": round(avg_complexity, 2),
        "avg_file_lines": round(avg_file_lines, 1),
        "functions": total_functions,
        "classes": total_classes,
        "comment_lines": total_comment_lines,
        "comment_ratio": round(comment_ratio, 1),
        "quality_score": quality_score,
        "status": status,
        "flags": flags,
        "largest_files": largest,
        "complex_files": complex_files,
        "files": rows,
        "files_analyzed_with_ast": sum(1 for row in rows if row["analysis_type"] == "AST"),
        "files_analyzed_with_heuristics": sum(1 for row in rows if row["analysis_type"] == "heuristic"),
    }


def summarize_code_health(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    return analyze_files(files)
