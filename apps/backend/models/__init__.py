"""
@fileoverview Models package initialization with role definitions
@module backend.models

@description
Centralized model exports and role definitions for the TRAIDER platform.
Provides consistent access to all database models and user role management.

@see {@link docs/architecture/models.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from enum import Enum
from typing import List

# Import all models
from .user import User
from .market_data import MarketData, OrderBookLevel2
from .signal import Signal
from .trade import Trade
from .position import Position

class UserRole(Enum):
    """
    User role enumeration for role-based access control.
    
    @description
    Defines the available user roles in the TRAIDER platform with
    hierarchical permissions for institutional-grade access control.
    
    @tradingImpact CRITICAL - Controls system access levels
    @riskLevel HIGH - Security-sensitive role definitions
    """
    
    ADMIN = "admin"
    TRADER = "trader" 
    VIEWER = "viewer"
    
    @classmethod
    def get_permissions(cls, role: str) -> List[str]:
        """
        Get permissions for a given role.
        
        @param role Role string
        @returns List of permissions
        
        @tradingImpact HIGH - Authorization decisions
        @riskLevel HIGH - Access control enforcement
        """
        
        permissions_map = {
            cls.ADMIN.value: [
                "trading", "portfolio_management", "risk_management",
                "user_management", "system_administration", "audit_access"
            ],
            cls.TRADER.value: [
                "trading", "portfolio_management", "risk_management"
            ],
            cls.VIEWER.value: [
                "portfolio_view", "performance_view"
            ]
        }
        
        return permissions_map.get(role, [])

# Export all models and enums
__all__ = [
    "User",
    "MarketData",
    "OrderBookLevel2",
    "Signal",
    "Trade",
    "Position",
    "UserRole",
]

# ---------------------------------------------------------------------------
# Compatibility shim for legacy import paths used by tests
# ---------------------------------------------------------------------------
# Many unit-test files manipulate *sys.path* and then perform imports such as
# `from models.market_data import MarketData`.  Inside the application code the
# canonical import path is `apps.backend.models`.  Without an alias Python
# treats these two import strings as distinct packages causing the module to
# be executed twice and SQLAlchemy to attempt to register the same tables
# twice – leading to `InvalidRequestError: Table 'X' is already defined'.
#
# We therefore register a *single* canonical module in `sys.modules['models']`
# and map sub-modules accordingly.  This guarantees that all subsequent import
# statements – regardless of the package prefix – resolve to the already
# initialised module objects.

import sys as _sys

# Alias the package itself
_sys.modules.setdefault("models", _sys.modules[__name__])

# Alias known sub-modules that have already been imported above.
for _sub in ("market_data", "signal", "trade", "position", "user"):
    full_name = f"{__name__}.{_sub}"
    if full_name in _sys.modules:
        _sys.modules[f"models.{_sub}"] = _sys.modules[full_name] 