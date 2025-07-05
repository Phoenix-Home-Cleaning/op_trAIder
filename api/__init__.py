"""Legacy alias package: `api`

Maintains compatibility with older test suites that imported from the top-level
`api` package (e.g., ``from api.auth import get_current_user``).

The canonical location for these modules is ``backend.api``. This shim simply
re-exports that package under the old name so existing imports keep working.

NOTE: This file should contain **no** functional logic. All implementation
lives in ``backend.api``.
"""

from __future__ import annotations

import importlib
import sys

# Import the canonical backend package
_backend_api = importlib.import_module("backend.api")

# Register this module alias so Python sees `api` as the same object as
# `backend.api`. This also ensures sub-packages like `api.auth` resolve
# correctly once they are imported under the canonical name.
sys.modules[__name__] = _backend_api 