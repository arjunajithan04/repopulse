from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any, Dict, Iterable, List

DEPENDENCY_FILES = {
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "Pipfile": "Python",
    "package.json": "Node.js",
    "package-lock.json": "Node.js",
    "yarn.lock": "Node.js",
    "pnpm-lock.yaml": "Node.js",
    "pom.xml": "Java",
    "build.gradle": "Java/Kotlin",
    "build.gradle.kts": "Kotlin",
    "pubspec.yaml": "Dart/Flutter",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
}

DOC_FILES = {"README", "README.md", "README.rst", "README.txt", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "LICENSE", "LICENSE.md", "SECURITY.md"}
TEST_DIRS = {"test", "tests", "spec", "__tests__"}
SOURCE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".go", ".rs", ".dart", ".php", ".rb", ".swift", ".c", ".h", ".cpp", ".cc", ".cs"}


def _is_test_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    name = PurePosixPath(path).name.lower()
    return any(part.lower() in TEST_DIRS for part in parts) or name.startswith("test_") or ".test." in name or ".spec." in name or name.endswith("_test.go")


def _dependency_count(name: str, content: str) -> int:
    lower = name.lower()
    if lower == "package.json":
        import json
        try:
            data = json.loads(content or "{}")
            return len((data.get("dependencies") or {})) + len((data.get("devDependencies") or {}))
        except (ValueError, TypeError):
            return 0
    if lower == "pyproject.toml":
        # Conservative count: dependency-looking entries under common arrays/tables.
        return len(re.findall(r"^[\s]*[\"']?[A-Za-z0-9_.-]+(?:\s*[<>=!~].*)?[\"']?\s*,?\s*$", content, re.MULTILINE))
    if lower in {"requirements.txt", "pipfile"}:
        return sum(1 for line in content.splitlines() if line.strip() and not line.lstrip().startswith(("#", "[")))
    if lower == "go.mod":
        return sum(1 for line in content.splitlines() if line.strip().startswith(("require ", "// indirect")))
    if lower == "cargo.toml":
        return 0 if "[dependencies]" not in content else sum(1 for line in content.split("[dependencies]", 1)[1].split("[", 1)[0].splitlines() if "=" in line and not line.strip().startswith("#"))
    if lower in {"pom.xml", "build.gradle", "build.gradle.kts", "pubspec.yaml", "composer.json", "gemfile"}:
        return sum(1 for line in content.splitlines() if re.search(r"(implementation|api|compile|dependency|dependencies|sdk:|http:|path:|gem |require)", line, re.I))
    return 0


def analyze_engineering(tree: Iterable[Dict[str, Any]], files: Iterable[Dict[str, str]] = ()) -> Dict[str, Any]:
    tree = [item for item in tree if item.get("type") == "blob"]
    files = list(files)
    paths = [str(item.get("path", "")) for item in tree]
    path_set = {PurePosixPath(p).name for p in paths}
    doc_hits = [name for name in paths if PurePosixPath(name).name in DOC_FILES]
    source_files = [p for p in paths if PurePosixPath(p).suffix.lower() in SOURCE_EXTENSIONS]
    test_files = [p for p in paths if _is_test_path(p)]
    dependency_paths = [p for p in paths if PurePosixPath(p).name in DEPENDENCY_FILES]

    dep_counts = []
    for item in files:
        name = PurePosixPath(item.get("path", "")).name
        if name in DEPENDENCY_FILES:
            count = _dependency_count(name, item.get("content", ""))
            if count:
                dep_counts.append({"file": item.get("path", ""), "ecosystem": DEPENDENCY_FILES[name], "dependencies": count})

    documentation = 35.0
    if any(PurePosixPath(p).name.startswith("README") for p in paths):
        documentation += 30
    if any(PurePosixPath(p).name == "LICENSE" or PurePosixPath(p).name.startswith("LICENSE.") for p in paths):
        documentation += 15
    if any(PurePosixPath(p).name == "CONTRIBUTING.md" for p in paths):
        documentation += 10
    if any("docs" in PurePosixPath(p).parts for p in paths):
        documentation += 10
    documentation = min(100.0, documentation)

    test_ratio = (len(test_files) / len(source_files) * 100) if source_files else 0.0
    if not source_files:
        testing_score = 50.0
        testing_status = "Unknown"
    elif test_files and test_ratio >= 20:
        testing_score, testing_status = 95.0, "Strong test presence"
    elif test_files:
        testing_score, testing_status = 75.0, "Test infrastructure detected"
    else:
        testing_score, testing_status = 35.0, "No obvious test files detected"

    if dependency_paths:
        dependency_score = 85.0 if dep_counts else 65.0
        dependency_status = "Dependency manifests detected"
    else:
        dependency_score, dependency_status = 55.0, "No common dependency manifest detected"

    engineering_score = round(documentation * 0.35 + testing_score * 0.35 + dependency_score * 0.30, 1)
    return {
        "engineering_score": engineering_score,
        "documentation_score": round(documentation, 1),
        "documentation_files": sorted(set(doc_hits)),
        "has_readme": any(PurePosixPath(p).name.startswith("README") for p in paths),
        "has_license": any(PurePosixPath(p).name == "LICENSE" or PurePosixPath(p).name.startswith("LICENSE.") for p in paths),
        "has_contributing": "CONTRIBUTING.md" in path_set,
        "has_docs_directory": any("docs" in PurePosixPath(p).parts for p in paths),
        "testing_score": round(testing_score, 1),
        "testing_status": testing_status,
        "test_files": len(test_files),
        "source_files": len(source_files),
        "test_to_source_ratio": round(test_ratio, 1),
        "dependency_score": round(dependency_score, 1),
        "dependency_status": dependency_status,
        "dependency_manifests": dependency_paths,
        "dependencies_observed": sum(item["dependencies"] for item in dep_counts),
        "dependency_breakdown": dep_counts,
        "tree_files": len(paths),
    }
