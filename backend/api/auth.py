#!/usr/bin/env python3
"""
@fileoverview Authentication API endpoints for TRAIDER V1
@module backend.api.auth

@description
Authentication system with JWT tokens, password-based login, and session management.
Provides secure access control for the institutional trading platform with
comprehensive audit logging and security monitoring.

@performance
- JWT token generation: <5ms
- Password verification: <100ms (bcrypt)
- Session validation: <1ms

@risk
- Failure impact: HIGH - System access control
- Recovery strategy: Fallback to emergency access
- Security monitoring for failed attempts

@compliance
- Audit requirements: All authentication attempts logged
- Data retention: Authentication logs kept for 1 year

@see {@link docs/security/authentication.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt

from utils.logging import get_logger, get_audit_logger
from utils.exceptions import AuthenticationError, AuthorizationError, ValidationError

# =============================================================================
# CONFIGURATION
# =============================================================================

router = APIRouter()
security = HTTPBearer()
logger = get_logger(__name__)
audit_logger = get_audit_logger()

# -----------------------------------------------------------------------------
# Centralised configuration
# -----------------------------------------------------------------------------
# Use validated settings provided by backend.config to avoid import-time failures
# when optional variables are missing in non-production environments.

try:
    # Attempt package-relative import first (works when `backend` is a package)
    from ..config import settings  # type: ignore  # pylint: disable=import-error
except ImportError:
    # Fallback to absolute import when backend is on PYTHONPATH as top-level package
    try:
        from backend.config import settings  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover – ultimate fallback
        class _FallbackSettings:  # pylint: disable=too-few-public-methods
            """Minimal fallback settings used only in test environments."""

            secret_key = os.getenv("SECRET_KEY", "test_secret_key_fallback")
            dashboard_password = os.getenv("DASHBOARD_PASSWORD", "test_dashboard_password")
            guest_password = os.getenv("GUEST_PASSWORD", "")
            algorithm = "HS256"
            access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        settings = _FallbackSettings()  # type: ignore

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Password settings
DASHBOARD_PASSWORD = settings.dashboard_password
GUEST_PASSWORD = settings.guest_password

# Password hashing with CI optimization
_bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", "12"))
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=_bcrypt_rounds)

# =============================================================================
# AUTHENTICATION MODELS
# =============================================================================

class AuthUser(dict):
    """
    Authentication user hybrid dict/object.
    
    @description
    Supports both dictionary access (user['email']) and attribute access
    (user.email) patterns for compatibility with different test scenarios.
    
    @performance <1ms attribute access
    @riskLevel LOW - Data structure wrapper
    """
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
    
    def __setattr__(self, key, value):
        self[key] = value

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class LoginRequest(BaseModel):
    """
    Login request model.
    
    @description
    Validates login credentials with proper input validation
    and security constraints.
    """
    
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    password: str = Field(..., min_length=1, max_length=100, description="Password")
    remember_me: bool = Field(False, description="Extended session duration")

class LoginResponse(BaseModel):
    """
    Login response model.
    
    @description
    Standardized login response with token and user information.
    """
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: Dict[str, Any] = Field(..., description="User information")

class TokenValidationResponse(BaseModel):
    """
    Token validation response model.
    
    @description
    Response for token validation requests with user context.
    """
    
    valid: bool = Field(..., description="Token validity status")
    user: Optional[Dict[str, Any]] = Field(None, description="User information if valid")
    expires_at: Optional[float] = Field(None, description="Token expiration timestamp")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    @param plain_password Plain text password
    @param hashed_password Hashed password
    @returns True if password matches
    
    @performance ~100ms (bcrypt security)
    @sideEffects None
    
    @tradingImpact HIGH - Access control security
    @riskLevel CRITICAL - Authentication security
    """
    
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt.
    
    @param password Plain text password
    @returns Hashed password
    
    @performance ~100ms (bcrypt security)
    @sideEffects None
    
    @tradingImpact HIGH - Password security
    @riskLevel CRITICAL - Password storage security
    """
    
    return pwd_context.hash(password)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    *,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> str:
    """
    Create JWT access token.
    
    @param data Token payload data
    @param expires_delta Token expiration delta
    @returns Encoded JWT token
    
    @performance <5ms token creation
    @sideEffects None
    
    @tradingImpact HIGH - Session management
    @riskLevel HIGH - Token security
    """
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "iss": "traider-v1",
    })
    
    # Allow dependency injection of cryptographic parameters (useful for tests and multi-tenant deployments)
    skey: str = secret_key or SECRET_KEY
    algo: str = algorithm or ALGORITHM

    encoded_jwt = jwt.encode(to_encode, skey, algorithm=algo)
    return encoded_jwt

def verify_token(
    token: str,
    *,
    secret_key: Optional[str] = None,
    algorithms: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    
    @param token JWT token to verify
    @returns Decoded token payload
    @throws AuthenticationError if token is invalid
    
    @performance <1ms token verification
    @sideEffects None
    
    @tradingImpact HIGH - Session validation
    @riskLevel HIGH - Token security
    """
    
    try:
        skey: str = secret_key or SECRET_KEY
        algos = algorithms or [ALGORITHM]

        payload = jwt.decode(token, skey, algorithms=algos)
        
        # Validate required claims
        if "sub" not in payload or "exp" not in payload:
            raise AuthenticationError("Invalid token format", "INVALID_TOKEN")
        
        # Check expiration
        exp_timestamp = payload["exp"]
        if datetime.now(timezone.utc).timestamp() > exp_timestamp:
            raise AuthenticationError("Token has expired", "TOKEN_EXPIRED")
        
        return payload
        
    except JWTError as exc:
        raise AuthenticationError(f"Token validation failed: {str(exc)}", "TOKEN_INVALID")

def get_user_by_email(email: str) -> Optional[AuthUser]:
    """
    Get user by email address from database.
    
    @param email User email address
    @returns AuthUser object if found, None otherwise
    
    @performance <50ms database query
    @sideEffects Database read operation
    
    @tradingImpact HIGH - User lookup for authentication
    @riskLevel MEDIUM - Database dependency
    """
    
    try:
        # Import database connection here to avoid circular imports
        from database import get_raw_connection
        
        # For Phase 0, we return None as tests will mock this function
        # In Phase 1+, this will perform actual database lookup
        return None
        
    except Exception as exc:
        logger.error(f"Database error in get_user_by_email: {exc}")
        return None

async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user credentials against database.
    
    @param username Username to authenticate
    @param password Password to verify
    @returns User information if authenticated, None otherwise
    
    @performance <100ms authentication
    @sideEffects Logs authentication attempts, updates last_login
    
    @tradingImpact CRITICAL - System access control
    @riskLevel CRITICAL - Authentication security
    """
    
    user_info = None
    
    try:
        # Import database connection here to avoid circular imports
        from database import get_raw_connection
        
        # Get database connection
        async with get_raw_connection() as conn:
            # Query user from database
            user_query = """
                SELECT id, username, email, password_hash, role, permissions, 
                       is_active, login_attempts, locked_until
                FROM users 
                WHERE username = $1 AND is_active = true
            """
            
            user_record = await conn.fetchrow(user_query, username)
            
            if not user_record:
                logger.warning(f"Authentication failed: User '{username}' not found")
                return None
            
            # Check if account is locked
            if user_record['locked_until'] and user_record['locked_until'] > datetime.now(timezone.utc):
                logger.warning(f"Authentication failed: Account '{username}' is locked")
                return None
            
            # Verify password
            if not verify_password(password, user_record['password_hash']):
                # Increment login attempts
                await conn.execute(
                    "UPDATE users SET login_attempts = login_attempts + 1 WHERE id = $1",
                    user_record['id']
                )
                
                logger.warning(f"Authentication failed: Invalid password for user '{username}'")
                return None
            
            # Reset login attempts and update last login on successful authentication
            await conn.execute("""
                UPDATE users SET 
                    login_attempts = 0, 
                    last_login = CURRENT_TIMESTAMP 
                WHERE id = $1
            """, user_record['id'])
            
            # Build user info
            user_info = {
                "user_id": str(user_record['id']),
                "username": user_record['username'],
                "email": user_record['email'],
                "role": user_record['role'],
                "permissions": user_record['permissions'] or [],
                "created_at": time.time(),
            }
            
            logger.info(f"User '{username}' authenticated successfully")
            
    except Exception as error:
        logger.error(f"Database error during authentication: {error}")
        return None
    
    # Log authentication attempt
    audit_logger.info(
        "Authentication attempt",
        extra={
            "username": username,
            "success": user_info is not None,
            "ip_address": "unknown",  # Will be added by middleware
            "user_agent": "unknown",  # Will be added by middleware
        }
    )
    
    return user_info

# =============================================================================
# DEPENDENCY FUNCTIONS
# =============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    
    @param credentials HTTP authorization credentials
    @returns Current user information
    @throws AuthenticationError if not authenticated
    
    @performance <1ms user extraction
    @sideEffects None
    
    @tradingImpact HIGH - Authorization for all protected endpoints
    @riskLevel HIGH - Authentication dependency
    """
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        # Extract user information from token
        user_info = {
            "user_id": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", []),
            "token_expires": payload.get("exp"),
        }
        
        return user_info
        
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_permission(permission: str):
    """
    Dependency factory for permission-based access control.
    
    @param permission Required permission
    @returns Dependency function that checks permission
    
    @performance <1ms permission check
    @sideEffects None
    
    @tradingImpact HIGH - Granular access control
    @riskLevel HIGH - Authorization security
    """
    
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        
        if permission not in user_permissions and "admin" not in user_permissions:
            audit_logger.warning(
                "Permission denied",
                extra={
                    "user_id": current_user.get("user_id"),
                    "required_permission": permission,
                    "user_permissions": user_permissions,
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}",
            )
        
        return current_user
    
    return permission_checker

# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.post("/login", response_model=LoginResponse, summary="User Login")
async def login(login_request: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return JWT token.
    
    @description
    Validates user credentials and returns JWT access token for
    authenticated sessions. Supports admin and optional guest access.
    
    @param login_request Login credentials
    @returns JWT token and user information
    @throws HTTPException for invalid credentials
    
    @example
    ```bash
    curl -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "your-password"}'
    ```
    
    @performance <100ms login process
    @sideEffects Creates user session, logs authentication
    
    @tradingImpact CRITICAL - System access control
    @riskLevel CRITICAL - Authentication security
    """
    
    try:
        # Authenticate user
        user = await authenticate_user(login_request.username, login_request.password)
        
        if not user:
            # Log failed authentication
            audit_logger.warning(
                "Authentication failed",
                extra={
                    "username": login_request.username,
                    "reason": "invalid_credentials",
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        
        # Convert AuthUser to plain dict for token creation
        user_dict = dict(user) if isinstance(user, AuthUser) else user
        
        # Create access token
        token_expires = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES * (7 if login_request.remember_me else 1)
        )
        
        token_data = {
            "sub": user_dict["user_id"],
            "username": user_dict["username"],
            "role": user_dict["role"],
            "permissions": user_dict["permissions"],
        }
        
        access_token = create_access_token(data=token_data, expires_delta=token_expires)
        
        # Log successful authentication
        audit_logger.info(
            "Authentication successful",
            extra={
                "user_id": user_dict["user_id"],
                "username": user_dict["username"],
                "role": user_dict["role"],
                "remember_me": login_request.remember_me,
            }
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(token_expires.total_seconds()),
            user={
                "user_id": user_dict["user_id"],
                "username": user_dict["username"],
                "role": user_dict["role"],
                "permissions": user_dict["permissions"],
            }
        )
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Login error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable",
        )

@router.post("/validate", response_model=TokenValidationResponse, summary="Validate Token")
async def validate_token(current_user: Dict[str, Any] = Depends(get_current_user)) -> TokenValidationResponse:
    """
    Validate JWT token and return user information.
    
    @description
    Validates the provided JWT token and returns user information
    if the token is valid and not expired.
    
    @param current_user Current user from token (dependency)
    @returns Token validation status and user information
    
    @performance <1ms token validation
    @sideEffects None
    
    @tradingImpact MEDIUM - Session validation
    @riskLevel MEDIUM - Token verification
    """
    
    return TokenValidationResponse(
        valid=True,
        user={
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "role": current_user["role"],
            "permissions": current_user["permissions"],
        },
        expires_at=current_user.get("token_expires")
    )

@router.post("/logout", summary="User Logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> JSONResponse:
    """
    Logout user and invalidate token.
    
    @description
    Logs out the current user. In Phase 0, this is primarily for
    audit logging. In Phase 1+, this will invalidate the token.
    
    @param current_user Current user from token (dependency)
    @returns Logout confirmation
    
    @performance <1ms logout process
    @sideEffects Logs logout event
    
    @tradingImpact LOW - Session cleanup
    @riskLevel LOW - Logout operation
    """
    
    # Log logout event
    audit_logger.info(
        "User logout",
        extra={
            "user_id": current_user["user_id"],
            "username": current_user["username"],
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Successfully logged out",
            "timestamp": time.time(),
        }
    )

@router.get("/me", summary="Get Current User")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user information.
    
    @description
    Returns information about the currently authenticated user
    including permissions and session details.
    
    @param current_user Current user from token (dependency)
    @returns Current user information
    
    @performance <1ms user info retrieval
    @sideEffects None
    
    @tradingImpact LOW - User information query
    @riskLevel LOW - Read-only user data
    """
    
    return {
        "user": {
            "user_id": current_user["user_id"],
            "username": current_user["username"],
            "role": current_user["role"],
            "permissions": current_user["permissions"],
        },
        "session": {
            "expires_at": current_user.get("token_expires"),
            "authenticated": True,
        },
        "timestamp": time.time(),
    } 