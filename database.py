"""Legacy alias module: `database`

Provides a thin re-export of the canonical ``backend.database`` module so that
``import database`` and related imports remain functional.
"""

from __future__ import annotations

import importlib as _importlib
import sys as _sys

_backend_database = _importlib.import_module("backend.database")

# Copy public names into this namespace for * import convenience
globals().update(_backend_database.__dict__)

# Tell the import machinery that this module *is* backend.database
_sys.modules[__name__] = _backend_database 