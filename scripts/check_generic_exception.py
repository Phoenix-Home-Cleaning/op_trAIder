#!/usr/bin/env python3
"""
@fileoverview CI guard to prevent use of bare `Exception` in backend source code.
@module scripts.check_generic_exception

@description
Traverses the `backend/` directory (excluding tests) and fails if it finds any
`raise Exception` or `except Exception` occurrences, enforcing typed error
usage (`TradingError` subclasses). This codifies the `codemod_tradingerror`
policy while gradual refactor proceeds.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

PATTERNS = [
    re.compile(r"\braise\s+Exception\b"),
    re.compile(r"\bexcept\s+Exception\b"),
]

EXCLUDE_PATHS = [
    "backend/tests",
    "backend/__init__.py",
]


def file_should_skip(path: Path) -> bool:
    return any(str(path).startswith(p) for p in EXCLUDE_PATHS)


def scan_file(path: Path) -> List[str]:
    violations: List[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in PATTERNS:
        for m in pattern.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            violations.append(f"{path}:{line_no}: {m.group(0).strip()}")
    return violations


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    backend_dir = repo_root / "backend"
    violations: List[str] = []
    for path in backend_dir.rglob("*.py"):
        if file_should_skip(path):
            continue
        violations.extend(scan_file(path))

    if violations:
        print("::error:: Found generic Exception usage – replace with TradingError subclasses")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print("✅ No generic Exception usage detected in backend source.")


if __name__ == "__main__":
    main() 