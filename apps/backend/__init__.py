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

# ---------------------------------------------------------------------------
# Public alias so that `import backend` refers to this package. This is required
# for backwards-compatibility with tests that expect a top-level `backend` module
# rather than `apps.backend`.
# ---------------------------------------------------------------------------

if "backend" not in _sys.modules:
    _sys.modules["backend"] = _sys.modules[__name__]

# ---------------------------------------------------------------------------
# Ensure *all* submodules imported under ``apps.backend.*`` are available under
# the short ``backend.*`` alias as well.  This prevents duplicate module
# objects that would otherwise break ``isinstance`` checks when the same class
# is imported via different package prefixes.
# ---------------------------------------------------------------------------
for _mod_name, _mod in list(_sys.modules.items()):
    if _mod_name.startswith(__name__ + "."):
        _backend_alias = "backend" + _mod_name[len(__name__):]
        _sys.modules[_backend_alias] = _mod 