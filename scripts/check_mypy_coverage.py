#!/usr/bin/env python3
"""
@fileoverview CI helper to enforce minimum mypy typed-coverage threshold
@module scripts.check_mypy_coverage

@description
Parses the `index.txt` file produced by `mypy --txt-report` and exits with
non-zero status if overall typed coverage is below the configured threshold.

Usage (CI):

    mypy --strict --ignore-missing-imports --txt-report build/mypy backend
    python scripts/check_mypy_coverage.py --report build/mypy/index.txt --min 30
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def parse_total_percentage(report_path: Path) -> float:
    if not report_path.is_file():
        raise FileNotFoundError(f"Mypy report file not found: {report_path}")

    content = report_path.read_text(encoding="utf-8")
    # Look for a line containing "Total" (allowing leading whitespace)
    match = re.search(
        r"^\s*\|?\s*Total.*?(\d+(?:\.\d+)?)%",
        content,
        flags=re.MULTILINE
    )
    if not match:
        raise ValueError(
            f"Could not find total-coverage line in {report_path}\n"
            f"Report contents:\n{content}"
        )
    return float(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser(description="Check mypy coverage threshold")
    parser.add_argument("--report", required=True, type=Path, help="Path to mypy index.txt")
    parser.add_argument("--min", dest="minimum", type=float, default=30.0, help="Minimum required percentage")
    args = parser.parse_args()

    percentage = parse_total_percentage(args.report)
    print(f"mypy typed coverage: {percentage:.1f}% (threshold {args.minimum}%)")

    if percentage < args.minimum - 0.01:  # small epsilon
        print("::error::Mypy typed-coverage below threshold")
        sys.exit(1)


if __name__ == "__main__":
    main() 