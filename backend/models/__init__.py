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
    "UserRole"
] 