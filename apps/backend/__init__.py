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

# ---------------------------------------------------------------------------
# Legacy alias mappings for `utils` and `api` top-level packages. These must be
# established **before** we import other sub-modules like `database` because
# those sub-modules depend on `utils` during their import phase.
# ---------------------------------------------------------------------------

for _legacy, _canonical in (("utils", f"{__name__}.utils"), ("api", f"{__name__}.api")):
    if _legacy not in _sys.modules:
        try:
            _mod = importlib.import_module(_canonical)
            _sys.modules[_legacy] = _mod
        except ModuleNotFoundError:
            # Sub-module might not exist yet; it will be resolved lazily.
            pass

# ---------------------------------------------------------------------------
# Now we can safely import and alias the database sub-module.
# ---------------------------------------------------------------------------

if "database" not in _sys.modules:
    _db_mod = importlib.import_module(".database", package=__name__)
    _sys.modules["database"] = _db_mod 