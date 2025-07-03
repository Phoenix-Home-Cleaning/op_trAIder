#!/usr/bin/env python3
"""
@fileoverview Script bootstrapper for internal package resolution
@module scripts.bootstrap

@description
Ensures that the project root directory is present on ``sys.path`` when
executing standalone scripts located in the ``scripts/`` directory. This
enables clean imports such as ``import backend.main`` without requiring
external environment configuration or ``PYTHONPATH`` manipulation.

@performance
- Latency impact: <1 ms per script import
- Memory overhead: Negligible (single Path object)

@risk
- Failure impact: LOW – Import errors for internal packages
- Recovery strategy: Add root path manually or fix directory structure

@compliance
- Audit requirements: None – utility module only
- Data retention: None

@see {@link docs/infrastructure/ci-cd-pipeline.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Compute repository root path (one level above the "scripts" directory)
# ---------------------------------------------------------------------------
ROOT_PATH: Path = Path(__file__).resolve().parent.parent

# Prepend to ``sys.path`` so it has highest precedence
root_str = str(ROOT_PATH)
if root_str not in sys.path:
    sys.path.insert(0, root_str) 