#!/usr/bin/env python3
"""
@fileoverview Validation utility to enforce bootstrap import in script files.
@module scripts.validate_script_imports

@description
Scans all ``*.py`` files inside the ``scripts/`` directory. If any script
contains an ``import backend`` (or ``from backend``) statement **without** a
preceding ``import scripts.bootstrap`` line, the script exits with status 1 and
prints the offending filenames. This tool is intended to be run in CI as part
of linting to guarantee that new utility scripts follow the established
bootstrap convention.

@risk MEDIUM – Blocks CI if guideline is violated
@since 1.0.0-alpha
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

SCRIPTS_DIR = Path(__file__).resolve().parent
PATTERN_BACKEND = re.compile(r"^\s*(?:from|import)\s+backend\b", re.MULTILINE)
PATTERN_BOOTSTRAP = re.compile(r"^\s*import\s+scripts\.bootstrap\b", re.MULTILINE)

def find_offenders() -> List[str]:
    offenders: List[str] = []
    for py_file in SCRIPTS_DIR.glob("*.py"):
        if py_file.name in {"bootstrap.py", Path(__file__).name}:  # Skip utility scripts
            continue
        content = py_file.read_text(encoding="utf-8")
        if PATTERN_BACKEND.search(content) and not PATTERN_BOOTSTRAP.search(content):
            offenders.append(py_file.name)
    return offenders


def main() -> None:
    offenders = find_offenders()
    if offenders:
        print("❌ The following script files import 'backend' without importing 'scripts.bootstrap':", file=sys.stderr)
        for name in offenders:
            print(f"  - {name}", file=sys.stderr)
        sys.exit(1)
    print("✅ All scripts correctly import scripts.bootstrap")


if __name__ == "__main__":  # pragma: no cover
    main() 