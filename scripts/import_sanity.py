#!/usr/bin/env python3
"""
@fileoverview Import Sanity Check for CI
@module scripts.import_sanity

@description
Simple script executed in CI to verify that key internal packages can be
imported successfully after editable installation. Fails with non-zero exit
status if imports are broken, allowing a fast-fail guard early in the
pipeline.

@performance O(1) – negligible runtime (<100 ms)
@risk LOW – Read-only import verification
@since 1.0.0-alpha
"""

from __future__ import annotations

import sys

try:
    import backend  # noqa: F401 – we only check importability
    from backend.main import app  # noqa: F401
except Exception as exc:  # pragma: no cover – explicit guard
    print(f"❌ Import sanity check failed: {exc}", file=sys.stderr)
    sys.exit(1)

print("✅ Import sanity check passed") 