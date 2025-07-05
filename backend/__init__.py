"""
Compatibility shim for legacy imports such as ``import backend.database``.

This thin wrapper re-exports the canonical ``apps.backend`` package so that
external tools, tests and scripts that still rely on a top-level ``backend``
package continue to work after the monorepo re-organisation (see
ADR-017).

Do **NOT** add business logic here – all functionality lives in
``apps.backend``.  This module only handles import aliasing.
"""

from __future__ import annotations

import importlib
import sys as _sys
from types import ModuleType as _ModuleType

# ---------------------------------------------------------------------------
# Import the real backend package (located at ``apps.backend``).
# ---------------------------------------------------------------------------
_real_backend: _ModuleType = importlib.import_module("apps.backend")

# Expose every public attribute of the real package through this shim so that
# ``from backend import X`` continues to work unchanged.
globals().update(_real_backend.__dict__)

# Ensure sub-module imports such as ``backend.database`` resolve correctly.
# We explicitly insert the loaded module objects into ``sys.modules`` under
# the *backend.* namespace hierarchy.
_sys.modules.setdefault(__name__, _real_backend)
for _name, _mod in list(_sys.modules.items()):
    if _name.startswith("apps.backend"):
        shim_name = _name.replace("apps.backend", __name__, 1)
        _sys.modules.setdefault(shim_name, _mod) 