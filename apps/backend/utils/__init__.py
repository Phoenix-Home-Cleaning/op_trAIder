# TRAIDER V1 Utils Package 

# Ensure package can be imported via both 'utils' and 'backend.utils'
import sys

# When package is imported as 'backend.utils', ensure modules are shared
module_name = __name__  # 'utils'
backend_name = f"backend.{module_name}"

if backend_name not in sys.modules:
    sys.modules[backend_name] = sys.modules[module_name] 

from .monitoring import MetricsCollector, initialize_metrics, get_metrics_collector  # noqa: F401
from .exceptions import TradingError, ErrorSeverity  # noqa: F401 