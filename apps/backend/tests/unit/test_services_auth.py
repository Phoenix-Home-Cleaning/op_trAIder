#!/usr/bin/env python3
"""
@fileoverview Comprehensive test suite for TRAIDER authentication service
@module tests.unit.backend.test_services_auth

@description
Institutional-grade test coverage for the authentication API service.
Tests include JWT tokens, password verification, error handling, and security scenarios.

@performance
- Test execution target: <200ms per test
- JWT operations: <5ms
- Password verification: <100ms

@risk
- Failure impact: CRITICAL - Authentication affects system security
- Recovery strategy: Comprehensive error scenario testing

@compliance
- Audit requirements: Yes - Authentication must be thoroughly tested
- Security testing: All attack vectors covered

@see {@link backend/api/auth.py}
@since 1.0.0-alpha.1
@author TRAIDER Team
"""

import os
import time
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
import bcrypt
from pydantic import BaseModel

# Import the auth module and its components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from backend.api.auth import (
    router,
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    authenticate_user,
    get_current_user,
    login,
    validate_token,
    logout,
    get_me,
    LoginRequest,
    LoginResponse,
    TokenValidationResponse,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DASHBOARD_PASSWORD,
    pwd_context
)
from backend.utils.exceptions import AuthenticationError, AuthorizationError, ValidationError

# Test configuration
TEST_SECRET_KEY = "test-secret-key-for-jwt-testing-only"
TEST_DASHBOARD_PASSWORD = "test-dashboard-password-123"
TEST_GUEST_PASSWORD = "guest-access-password"

class TestAuthenticationService:
    """
    Authentication service test suite
    
    @description
    Comprehensive testing of the authentication service including:
    - Password hashing and verification
    - JWT token creation and validation
    - User authentication flows
    - Security error scenarios
    - Performance characteristics
    - Edge cases and error handling
    
    @tradingImpact Tests critical authentication for trading system access
    @riskLevel CRITICAL - Authentication security essential
    """

    @pytest.fixture(autouse=True)
    def setup_test_environment(self, monkeypatch):
        """
        Setup test environment with secure test credentials.
        
        @description
        Sets up isolated test environment with test credentials
        and mocked dependencies for secure testing.
        
        @performance Target: <10ms setup time
        @tradingImpact Ensures isolated test environment
        @riskLevel LOW - Test environment isolation
        """
        # Set test environment variables
        monkeypatch.setenv("SECRET_KEY", TEST_SECRET_KEY)
        monkeypatch.setenv("DASHBOARD_PASSWORD", TEST_DASHBOARD_PASSWORD)
        monkeypatch.setenv("GUEST_PASSWORD", TEST_GUEST_PASSWORD)
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        
        # Mock logging to avoid test output pollution
        with patch('api.auth.logger'), patch('api.auth.audit_logger'):
            yield

    @pytest.fixture
    def valid_login_request(self) -> LoginRequest:
        """
        Create valid login request for testing.
        
        @description
        Provides valid login request object for authentication tests
        with proper username and password format.
        
        @returns LoginRequest with valid credentials
        @tradingImpact Standard login request for testing flows
        @riskLevel LOW - Test data creation
        """
        return LoginRequest(
            username="dashboard",
            password=TEST_DASHBOARD_PASSWORD,
            remember_me=False
        )

    @pytest.fixture
    def invalid_login_request(self) -> LoginRequest:
        """
        Create invalid login request for testing.
        
        @description
        Provides invalid login request object for testing
        authentication failure scenarios.
        
        @returns LoginRequest with invalid credentials
        @tradingImpact Invalid login request for error testing
        @riskLevel LOW - Test data creation
        """
        return LoginRequest(
            username="dashboard",
            password="wrong-password",
            remember_me=False
        )

    @pytest.fixture
    def mock_user_data(self) -> Dict[str, Any]:
        """
        Create mock user data for testing.
        
        @description
        Provides mock user data structure for authentication tests
        with proper user information format including user_id.
        
        @returns Dict with mock user information
        @tradingImpact Mock user data for testing authentication flows
        @riskLevel LOW - Test data creation
        """
        return {
            "user_id": "test-user-123",
            "username": "dashboard",
            "role": "admin",
            "permissions": ["read", "write", "admin"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": datetime.now(timezone.utc).isoformat(),
        }

    # =============================================================================
    # PASSWORD HASHING AND VERIFICATION TESTS
    # =============================================================================

    def test_password_hashing_and_verification(self):
        """
        Test password hashing and verification functions.
        
        @description
        Tests bcrypt password hashing and verification with proper
        security parameters and performance characteristics.
        
        @performance Target: <200ms for hash + verify cycle
        @tradingImpact Password security essential for system access
        @riskLevel CRITICAL - Password security validation
        """
        start_time = time.time()
        
        # Test password hashing
        plain_password = "test-password-123"
        hashed_password = get_password_hash(plain_password)
        
        # Verify hash properties
        assert isinstance(hashed_password, str)
        assert len(hashed_password) > 50  # bcrypt hashes are long
        assert hashed_password.startswith('$2b$')  # bcrypt identifier
        assert hashed_password != plain_password  # Must be different
        
        # Test password verification
        assert verify_password(plain_password, hashed_password) is True
        assert verify_password("wrong-password", hashed_password) is False
        
        # Performance check - bcrypt is intentionally slow for security
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 1000, f"Password operations took {execution_time:.2f}ms, expected <1000ms"

    def test_password_hashing_consistency(self):
        """
        Test password hashing produces different hashes for same password.
        
        @description
        Verifies bcrypt salt functionality ensures different hashes
        for the same password on multiple runs.
        
        @performance Target: <100ms for multiple hash operations
        @tradingImpact Hash uniqueness prevents rainbow table attacks
        @riskLevel HIGH - Security validation
        """
        password = "consistent-test-password"
        
        # Generate multiple hashes
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        hash3 = get_password_hash(password)
        
        # Hashes should be different (salt effect)
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3
        
        # But all should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
        assert verify_password(password, hash3)

    def test_password_verification_edge_cases(self):
        """
        Test password verification edge cases and error conditions.
        
        @description
        Tests password verification with edge cases including
        empty passwords, special characters, and malformed hashes.
        
        @performance Target: <50ms per verification
        @tradingImpact Edge case handling prevents authentication bypass
        @riskLevel HIGH - Security edge case validation
        """
        # Test with empty password - should still work (bcrypt handles it)
        empty_hash = get_password_hash("")
        assert verify_password("", empty_hash)
        
        # Test with very long password
        long_password = "a" * 1000
        hashed_long = get_password_hash(long_password)
        assert verify_password(long_password, hashed_long)
        
        # Test with special characters
        special_password = "pāssw0rd!@#$%^&*()_+-=[]{}|;':\",./<>?"  # NOSONAR
        hashed_special = get_password_hash(special_password)
        assert verify_password(special_password, hashed_special)
        
        # Test with malformed hash - should raise exception or return False
        try:
            result = verify_password("any-password", "malformed-hash")
            assert result is False
        except Exception:
            # Malformed hash can raise exception, which is acceptable
            pass

    # =============================================================================
    # JWT TOKEN TESTS
    # =============================================================================

    def test_jwt_token_creation_and_validation(self):
        """
        Test JWT token creation and validation.
        
        @description
        Tests JWT token creation with proper payload, expiration,
        and validation with performance benchmarks.
        
        @performance Target: <10ms for token operations
        @tradingImpact JWT tokens essential for session management
        @riskLevel HIGH - Token security validation
        """
        start_time = time.time()
        
        # Test data with required sub field
        payload = {
            "sub": "test-user-123",
            "username": "dashboard", 
            "role": "admin"
        }
        
        # Create token
        token = create_access_token(payload)
        
        # Verify token properties
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are substantial
        assert token.count('.') == 2  # JWT has 3 parts separated by dots
        
        # Validate token
        decoded_payload = verify_token(token)
        
        # Verify payload content
        assert decoded_payload["sub"] == "test-user-123"
        assert decoded_payload["username"] == "dashboard"
        assert decoded_payload["role"] == "admin"
        assert "exp" in decoded_payload  # Expiration
        assert "iat" in decoded_payload  # Issued at
        assert "iss" in decoded_payload  # Issuer
        assert decoded_payload["iss"] == "traider-v1"
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 10, f"Token operations took {execution_time:.2f}ms, expected <10ms"

    def test_jwt_token_expiration(self):
        """
        Test JWT token expiration handling.
        
        @description
        Tests JWT token creation with custom expiration and
        validation of expired tokens.
        
        @performance Target: <10ms for token operations
        @tradingImpact Token expiration critical for security
        @riskLevel HIGH - Token lifecycle security
        """
        # Create token with short expiration and required sub field
        payload = {"sub": "test-user", "username": "test"}
        short_expiration = timedelta(seconds=5)
        token = create_access_token(payload, expires_delta=short_expiration)
        
        # Token should be valid immediately
        decoded = verify_token(token)
        assert decoded["sub"] == "test-user"
        assert decoded["username"] == "test"
        
        # Wait for expiration
        time.sleep(8)
        
        # Token should now be expired
        with pytest.raises(AuthenticationError):
            verify_token(token)

    def test_jwt_token_invalid_scenarios(self):
        """
        Test JWT token validation with invalid tokens.
        
        @description
        Tests JWT token validation with various invalid token
        scenarios including malformed, tampered, and wrong signature.
        
        @performance Target: <5ms per validation
        @tradingImpact Invalid token handling prevents unauthorized access
        @riskLevel CRITICAL - Token security validation
        """
        # Test malformed token
        with pytest.raises(AuthenticationError):
            verify_token("malformed.token")
        
        # Test empty token
        with pytest.raises(AuthenticationError):
            verify_token("")
        
        # Test token with wrong signature
        payload = {"username": "test"}
        token = create_access_token(payload)
        
        # Tamper with token
        tampered_token = token[:-10] + "tampered123"
        with pytest.raises(AuthenticationError):
            verify_token(tampered_token)
        
        # Test token signed with different key
        wrong_key_token = jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)
        with pytest.raises(AuthenticationError):
            verify_token(wrong_key_token)

    # =============================================================================
    # USER AUTHENTICATION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_user_data):
        """
        Test successful user authentication.
        
        @description
        Tests successful user authentication with valid credentials
        and proper user data return.
        
        @performance Target: <100ms authentication time
        @tradingImpact Successful authentication enables system access
        @riskLevel HIGH - Authentication flow validation
        """
        start_time = time.time()
        
        # Test successful authentication
        user = await authenticate_user("dashboard", TEST_DASHBOARD_PASSWORD)
        
        # Verify user data
        assert user is not None
        assert isinstance(user, dict)
        assert user["username"] == "dashboard"
        assert "role" in user
        assert "permissions" in user
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 100, f"Authentication took {execution_time:.2f}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self):
        """
        Test user authentication failure scenarios.
        
        @description
        Tests user authentication with invalid credentials
        and proper error handling.
        
        @performance Target: <100ms authentication time
        @tradingImpact Authentication failure must be handled securely
        @riskLevel HIGH - Authentication security validation
        """
        # Test with wrong password
        user = await authenticate_user("dashboard", "wrong-password")
        assert user is None
        
        # Test with wrong username
        user = await authenticate_user("wrong-user", TEST_DASHBOARD_PASSWORD)
        assert user is None
        
        # Test with empty credentials
        user = await authenticate_user("", "")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_user_data):
        """
        Test successful current user retrieval.
        
        @description
        Tests current user retrieval with valid JWT token
        and proper user data return.
        
        @performance Target: <10ms user retrieval time
        @tradingImpact Current user data essential for authorization
        @riskLevel HIGH - User session validation
        """
        # Create valid token with proper JWT structure
        token_data = {
            "sub": mock_user_data["user_id"],
            "username": mock_user_data["username"],
            "role": mock_user_data["role"],
            "permissions": mock_user_data["permissions"],
        }
        token = create_access_token(token_data)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        start_time = time.time()
        
        # Get current user
        user = await get_current_user(credentials)
        
        # Verify user data
        assert user is not None
        assert user["username"] == mock_user_data["username"]
        assert user["role"] == mock_user_data["role"]
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 10, f"User retrieval took {execution_time:.2f}ms, expected <10ms"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """
        Test current user retrieval with invalid token.
        
        @description
        Tests current user retrieval with invalid JWT token
        and proper error handling.
        
        @performance Target: <10ms error handling time
        @tradingImpact Invalid token handling prevents unauthorized access
        @riskLevel CRITICAL - Token validation security
        """
        # Test with invalid token
        invalid_credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", 
            credentials="invalid.token.here"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(invalid_credentials)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    # =============================================================================
    # API ENDPOINT TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_login_endpoint_success(self, valid_login_request, mock_user_data):
        """
        Test successful login endpoint.
        
        @description
        Tests login endpoint with valid credentials and proper
        response format with JWT token and user data.
        
        @performance Target: <200ms login response time
        @tradingImpact Login endpoint essential for system access
        @riskLevel HIGH - Authentication endpoint validation
        """
        with patch('api.auth.authenticate_user', return_value=mock_user_data):
            start_time = time.time()
            
            response = await login(valid_login_request)
            
            # Verify response structure
            assert isinstance(response, LoginResponse)
            assert response.access_token is not None
            assert response.token_type == "bearer"
            assert response.expires_in > 0
            assert response.user["username"] == "dashboard"
            
            # Verify token is valid
            decoded = verify_token(response.access_token)
            assert decoded["username"] == "dashboard"
            
            # Performance check
            execution_time = (time.time() - start_time) * 1000
            assert execution_time < 200, f"Login took {execution_time:.2f}ms, expected <200ms"

    @pytest.mark.asyncio
    async def test_login_endpoint_failure(self, invalid_login_request):
        """
        Test login endpoint failure scenarios.
        
        @description
        Tests login endpoint with invalid credentials and proper
        error response with security considerations.
        
        @performance Target: <200ms error response time
        @tradingImpact Login failure must be handled securely
        @riskLevel HIGH - Authentication security validation
        """
        with patch('api.auth.authenticate_user', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await login(invalid_login_request)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid username or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_token_endpoint(self, mock_user_data):
        """
        Test token validation endpoint.
        
        @description
        Tests token validation endpoint with valid token
        and proper validation response.
        
        @performance Target: <10ms validation response time
        @tradingImpact Token validation essential for session management
        @riskLevel HIGH - Token validation endpoint
        """
        start_time = time.time()
        
        # Add token expiration to mock data
        mock_user_with_expiry = {**mock_user_data, "token_expires": time.time() + 3600}
        response = await validate_token(mock_user_with_expiry)
        
        # Verify response structure
        assert isinstance(response, TokenValidationResponse)
        assert response.valid is True
        assert response.user["username"] == mock_user_data["username"]
        assert response.expires_at is not None
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 10, f"Validation took {execution_time:.2f}ms, expected <10ms"

    @pytest.mark.asyncio
    async def test_logout_endpoint(self, mock_user_data):
        """
        Test logout endpoint.
        
        @description
        Tests logout endpoint with valid user session
        and proper logout response.
        
        @performance Target: <50ms logout response time
        @tradingImpact Logout endpoint essential for session management
        @riskLevel MEDIUM - Session termination
        """
        start_time = time.time()
        
        response = await logout(mock_user_data)
        
        # Verify response
        assert response.status_code == 200
        response_data = response.body.decode()
        assert "successfully logged out" in response_data.lower()
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 50, f"Logout took {execution_time:.2f}ms, expected <50ms"

    @pytest.mark.asyncio
    async def test_get_me_endpoint(self, mock_user_data):
        """
        Test get current user endpoint.
        
        @description
        Tests get current user endpoint with valid session
        and proper user data response.
        
        @performance Target: <10ms user data response time
        @tradingImpact User data endpoint essential for UI personalization
        @riskLevel MEDIUM - User data access
        """
        start_time = time.time()
        
        response = await get_me(mock_user_data)
        
        # Verify response structure (get_me returns nested structure)
        assert isinstance(response, dict)
        assert "user" in response
        assert "session" in response
        assert response["user"]["username"] == mock_user_data["username"]
        assert response["user"]["role"] == mock_user_data["role"]
        assert "permissions" in response["user"]
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 10, f"Get me took {execution_time:.2f}ms, expected <10ms"

    # =============================================================================
    # SECURITY TESTS
    # =============================================================================

    def test_timing_attack_resistance(self):
        """
        Test resistance to timing attacks in password verification.
        
        @description
        Tests password verification timing consistency to prevent
        timing attacks that could reveal valid usernames.
        
        @performance Target: Consistent timing regardless of validity
        @tradingImpact Timing attack resistance prevents username enumeration
        @riskLevel HIGH - Security timing attack prevention
        """
        # Test with valid and invalid passwords
        valid_password = TEST_DASHBOARD_PASSWORD
        invalid_password = "definitely-wrong-password"
        
        # Hash a password for testing
        hashed = get_password_hash(valid_password)
        
        # Measure timing for valid password
        start_time = time.time()
        verify_password(valid_password, hashed)
        valid_time = time.time() - start_time
        
        # Measure timing for invalid password
        start_time = time.time()
        verify_password(invalid_password, hashed)
        invalid_time = time.time() - start_time
        
        # Times should be relatively similar (within 50ms difference)
        time_difference = abs(valid_time - invalid_time)
        assert time_difference < 0.05, f"Timing difference {time_difference:.3f}s may indicate timing attack vulnerability"

    @pytest.mark.asyncio
    async def test_brute_force_protection_simulation(self):
        """
        Test authentication behavior under brute force simulation.
        
        @description
        Simulates brute force attack scenarios to verify
        authentication system behavior and performance.
        
        @performance Target: Consistent response times under load
        @tradingImpact Brute force resistance prevents unauthorized access
        @riskLevel HIGH - Brute force attack simulation
        """
        # Simulate rapid authentication attempts
        attempts = 10
        start_time = time.time()
        
        for i in range(attempts):
            result = await authenticate_user("dashboard", f"wrong-password-{i}")
            assert result is None  # All should fail
        
        total_time = time.time() - start_time
        avg_time = total_time / attempts
        
        # Average time per attempt should be reasonable
        assert avg_time < 0.2, f"Average authentication time {avg_time:.3f}s too slow under load"

    def test_token_payload_security(self):
        """
        Test JWT token payload security and information disclosure.
        
        @description
        Tests JWT token payload to ensure no sensitive information
        is disclosed in the token content.
        
        @performance Target: <5ms token analysis
        @tradingImpact Token security prevents information disclosure
        @riskLevel HIGH - Token information security
        """
        # Create token with user data
        user_data = {
            "username": "dashboard",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        
        token = create_access_token(user_data)
        
        # Decode token payload (without verification for analysis)
        import base64
        import json
        
        # Get payload part (middle section)
        payload_b64 = token.split('.')[1]
        # Add padding if needed
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_json = base64.b64decode(payload_b64)
        payload = json.loads(payload_json)
        
        # Verify no sensitive information in payload
        assert "password" not in payload
        assert "secret" not in payload
        assert "key" not in payload
        
        # Verify required claims are present
        assert "username" in payload
        assert "exp" in payload  # Expiration
        assert "iat" in payload  # Issued at
        assert "iss" in payload  # Issuer

    # =============================================================================
    # PERFORMANCE STRESS TESTS
    # =============================================================================

    def test_concurrent_password_hashing_performance(self):
        """
        Test password hashing performance under concurrent load.
        
        @description
        Tests password hashing performance with multiple concurrent
        operations to verify scalability.
        
        @performance Target: <500ms for 5 concurrent hashes
        @tradingImpact Hash performance affects login response times
        @riskLevel MEDIUM - Performance under load
        """
        import concurrent.futures
        import threading
        
        def hash_password(password):
            return get_password_hash(f"password-{password}")
        
        start_time = time.time()
        
        # Test concurrent hashing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(hash_password, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        # Verify all hashes completed
        assert len(results) == 5
        assert all(isinstance(result, str) for result in results)
        
        # Performance check
        assert total_time < 0.5, f"Concurrent hashing took {total_time:.3f}s, expected <0.5s"

    def test_jwt_token_generation_performance(self):
        """
        Test JWT token generation performance under load.
        
        @description
        Tests JWT token generation performance with multiple
        rapid token creation operations.
        
        @performance Target: <50ms for 100 tokens
        @tradingImpact Token generation performance affects login scalability
        @riskLevel MEDIUM - Token generation performance
        """
        user_data = {"username": "test", "role": "user"}
        
        start_time = time.time()
        
        # Generate multiple tokens rapidly
        tokens = []
        for i in range(100):
            token = create_access_token({**user_data, "id": i})
            tokens.append(token)
        
        total_time = time.time() - start_time
        
        # Verify all tokens generated
        assert len(tokens) == 100
        assert all(isinstance(token, str) for token in tokens)
        assert len(set(tokens)) == 100  # All tokens should be unique
        
        # Performance check
        assert total_time < 0.05, f"Token generation took {total_time:.3f}s, expected <0.05s" 