"""Legacy alias package: `utils`

Re-exports the canonical ``backend.utils`` package to preserve backwards
compatibility for code/tests importing top-level ``utils``.
"""

from __future__ import annotations

import importlib
import sys

_backend_utils = importlib.import_module("backend.utils")

sys.modules[__name__] = _backend_utils 