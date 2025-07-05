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

# Ensure the legacy top-level alias `models` is registered *before* any model
# sub-modules are imported. This guarantees that a single module object is
# shared between the canonical package name (``backend.models``) and the
# legacy alias (``models``), preventing duplicate SQLAlchemy table metadata
# registration.

import sys as _sys

# Register the legacy alias *immediately* so it's available during submodule
# resolution that may occur as part of an import statement like
# ``from models.market_data import MarketData``. We also eagerly import each
# sub-module under its canonical name and then create the alias in
# ``sys.modules`` *before* control returns to the caller. This guarantees the
# import system finds the already-initialised module and avoids a second
# evaluation that would result in duplicated SQLAlchemy table metadata.

import importlib as _importlib

# Canonical package alias
_sys.modules.setdefault("models", _sys.modules[__name__])

# Eagerly load all sub-modules once and create alias entries
for _sub in ("market_data", "signal", "trade", "position", "user"):
    _canonical_name = f"{__name__}.{_sub}"  # backend.models.market_data etc.
    _alias_name = f"models.{_sub}"

    if _canonical_name not in _sys.modules:
        _importlib.import_module(_canonical_name)

    _sys.modules[_alias_name] = _sys.modules[_canonical_name]

from enum import Enum
from typing import List

# Import Base declarative class early so sub-models can inherit it without
# circular import issues.
from backend.database import Base as Base  # noqa: N812 – keep original name

# Import all models **after** alias registration to avoid double imports.
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
# Legacy import compatibility helpers
# ---------------------------------------------------------------------------

# Export Base declarative class for callers doing ``from models import Base``
__all__.append("Base")

# Expose already-imported sub-modules under the legacy alias so that imports
# like ``import models.market_data`` resolve to the canonical modules without
# causing a second evaluation.
for _sub in ("market_data", "signal", "trade", "position", "user"):
    _canonical = f"{__name__}.{_sub}"
    if _canonical in _sys.modules:
        _sys.modules[f"models.{_sub}"] = _sys.modules[_canonical] 