# TRAIDER V1 Utils Package 

# Ensure package can be imported via both 'utils' and 'backend.utils'
import sys

# ---------------------------------------------------------------------------
# Alias handling to support multiple import paths:
#   - 'apps.backend.utils'   (canonical path)
#   - 'backend.utils'        (legacy alias via backend/__init__.py)
#   - 'utils'                (very old tests / scripts)
# We register *this* module under all these names **immediately** so that
# sub-modules imported later (e.g. ``utils.logging``) resolve correctly even
# during the execution of this package's own import cycle.
# ---------------------------------------------------------------------------

_self = sys.modules[__name__]

# Ensure 'backend.utils' alias
backend_alias = "backend.utils"
if backend_alias not in sys.modules:
    sys.modules[backend_alias] = _self

# Ensure top-level 'utils' alias
if "utils" not in sys.modules:
    sys.modules["utils"] = _self 

from .monitoring import MetricsCollector, initialize_metrics, get_metrics_collector  # noqa: F401
from .exceptions import TradingError, ErrorSeverity  # noqa: F401 