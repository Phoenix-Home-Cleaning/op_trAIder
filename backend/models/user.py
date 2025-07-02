"""
@fileoverview User model for TRAIDER V1 authentication
@module backend.models.user

@description
SQLAlchemy model for user authentication and authorization.
Supports role-based access control and audit logging for
institutional-grade security requirements.

@performance
- Indexed username and email fields
- Efficient password hashing with bcrypt
- Session management optimization

@risk
- Failure impact: HIGH - Authentication system unavailable
- Recovery strategy: Database backup restoration

@compliance
- Audit requirements: All user actions logged
- Data retention: User data retained per privacy policy

@see {@link docs/architecture/user-management.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    @description
    Stores user credentials, profile information, and access control
    data for the TRAIDER platform with institutional security standards.
    
    @attributes
    - id: Primary key
    - username: Unique username for login
    - email: User email address
    - password_hash: Bcrypt hashed password
    - role: User role (admin, trader, viewer)
    - permissions: JSON array of specific permissions
    - is_active: Account status flag
    - created_at: Account creation timestamp
    - last_login: Last successful login timestamp
    - login_attempts: Failed login attempt counter
    - profile: Additional profile information
    
    @tradingImpact CRITICAL - Controls system access
    @riskLevel HIGH - Security-sensitive user data
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Authorization fields
    role = Column(String(20), nullable=False, default="viewer")
    permissions = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, nullable=False, default=0)
    
    # Profile information
    profile = Column(JSON, nullable=False, default=dict)
    notes = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert user to dictionary representation.
        
        @param include_sensitive Whether to include sensitive fields
        @returns Dictionary representation of user
        
        @performance <1ms serialization
        @sideEffects None
        
        @tradingImpact LOW - Data serialization
        @riskLevel MEDIUM - Potential sensitive data exposure
        """
        
        user_dict = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile": self.profile,
        }
        
        if include_sensitive:
            user_dict.update({
                "login_attempts": self.login_attempts,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "notes": self.notes,
            })
        
        return user_dict
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        @param permission Permission to check
        @returns True if user has permission
        
        @performance <0.1ms permission check
        @sideEffects None
        
        @tradingImpact HIGH - Authorization decisions
        @riskLevel HIGH - Access control enforcement
        """
        
        # Admin role has all permissions
        if self.role == "admin":
            return True
        
        # Check specific permissions
        return permission in (self.permissions or [])
    
    def can_trade(self) -> bool:
        """
        Check if user can execute trades.
        
        @returns True if user can trade
        
        @performance <0.1ms permission check
        @sideEffects None
        
        @tradingImpact CRITICAL - Trading authorization
        @riskLevel CRITICAL - Financial operation control
        """
        
        return self.is_active and (
            self.role in ["admin", "trader"] or 
            self.has_permission("trading")
        ) 