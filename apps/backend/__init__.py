# TRAIDER V1 Backend Package 

"""
Backend package initialization with legacy import aliases.

Provides compatibility for test suites that import top-level modules like
`import database` or `from database import Base`.
The canonical import path inside the application is `backend.database`, but we
map the shorter alias to avoid breaking existing tests.
"""

import sys as _sys
import importlib

# Lazily import the database sub-module and register alias only if not present
if "database" not in _sys.modules:
    _db_mod = importlib.import_module("backend.database")
    _sys.modules["database"] = _db_mod 

# ---------------------------------------------------------------------------
# Legacy alias mappings for `utils` and `api` top-level packages referenced in
# older test suites. These simply forward to the canonical `backend.utils` and
# `backend.api` modules so imports like `from utils.logging import get_logger`
# continue to resolve.
# ---------------------------------------------------------------------------

for _legacy, _canonical in (("utils", "backend.utils"), ("api", "backend.api")):
    if _legacy not in _sys.modules:
        try:
            _mod = importlib.import_module(_canonical)
            _sys.modules[_legacy] = _mod
        except ModuleNotFoundError:
            # Module might not exist yet (e.g., API package not imported in
            # backend-only contexts). It will be resolved lazily when first
            # needed.
            pass 