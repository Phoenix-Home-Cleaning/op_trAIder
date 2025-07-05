"""
@fileoverview API Integration Tests for Authentication
@module tests.integration.test_api_auth

@description
This file contains integration tests for the authentication API endpoints defined
in `backend/api/auth.py`. It uses FastAPI's TestClient to simulate real HTTP
requests and validate the behavior of the /login, /me, /validate, and /logout
endpoints under various conditions, including success, failure, and edge cases.

These tests ensure that the entire authentication flow, from request validation
to token generation and verification, works as expected in an integrated
environment.

@see {@link backend/api/auth.py}
@see {@link docs/testing/authentication-testing-guide.md}
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
import time

from backend.main import app
from backend.config import settings

client = TestClient(app)

class TestAuthAPI:
    """
    Integration tests for the authentication API endpoints.
    """

    def test_login_success_dashboard_user(self, client: TestClient):
        """
        Verify successful login for the main dashboard user.
        
        @tradingImpact CRITICAL - Ensures the primary user can access the system.
        @riskLevel HIGH - A failure here locks out all primary operators.
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "dashboard", "password": settings.dashboard_password}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "dashboard"
        assert data["user"]["role"] == "admin"

    def test_login_success_guest_user(self, client: TestClient):
        """
        Verify successful login for a guest user with view-only permissions.
        
        @tradingImpact LOW - Ensures read-only users can access dashboards.
        @riskLevel LOW - A failure here has no impact on trading operations.
        """
        if not settings.guest_password:
            pytest.skip("GUEST_PASSWORD is not set, skipping guest login test.")

        response = client.post(
            "/api/v1/auth/login",
            json={"username": "guest", "password": settings.guest_password}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "guest"
        assert data["user"]["role"] == "viewer"

    def test_login_failure_wrong_password(self, client: TestClient):
        """
        Verify that login fails with an incorrect password.
        
        @tradingImpact CRITICAL - Prevents unauthorized access.
        @riskLevel CRITICAL - Must robustly reject invalid credentials.
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "dashboard", "password": "wrong-password"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_failure_nonexistent_user(self, client: TestClient):
        """
        Verify that login fails for a user that does not exist.
        
        @tradingImpact CRITICAL - Prevents username enumeration if not handled correctly.
        @riskLevel HIGH - Must not leak information about valid usernames.
        """
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent-user", "password": "any-password"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_get_me_success(self, client: TestClient):
        """
        Verify the /me endpoint returns user data for a valid token.
        """
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "dashboard", "password": settings.dashboard_password}
        )
        token = login_res.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        me_res = client.get("/api/v1/auth/me", headers=headers)
        
        assert me_res.status_code == 200
        data = me_res.json()
        assert data["username"] == "dashboard"
        assert data["role"] == "admin"

    def test_get_me_failure_no_token(self, client: TestClient):
        """
        Verify the /me endpoint fails without an authentication token.
        """
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403 # Changed from 401 based on HTTPBearer behavior
        assert response.json()["detail"] == "Not authenticated"

    def test_get_me_failure_invalid_token(self, client: TestClient):
        """
        Verify the /me endpoint fails with a malformed or invalid token.
        """
        headers = {"Authorization": "Bearer an-invalid-token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_get_me_failure_expired_token(self, client: TestClient):
        """
        Verify the /me endpoint fails when using an expired token.
        """
        # Create an expired token by overriding the expiration
        expired_payload = {
            "sub": "dashboard",
            "role": "admin",
            "exp": int(time.time()) - 1 # Expired 1 second ago
        }
        expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm=settings.algorithm)

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        assert "Token has expired" in response.json()["detail"]

    def test_validate_endpoint_success(self, client: TestClient):
        """
        Verify the /validate endpoint succeeds with a valid token.
        """
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "dashboard", "password": settings.dashboard_password}
        )
        token = login_res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        validate_res = client.post("/api/v1/auth/validate", headers=headers)
        
        assert validate_res.status_code == 200
        data = validate_res.json()
        assert data["valid"] is True
        assert data["user"]["username"] == "dashboard"
        assert "expires_at" in data

    def test_logout_endpoint(self, client: TestClient):
        """
        Verify the /logout endpoint returns a success message for an authenticated user.
        """
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "dashboard", "password": settings.dashboard_password}
        )
        token = login_res.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        logout_res = client.post("/api/v1/auth/logout", headers=headers)

        assert logout_res.status_code == 200
        assert logout_res.json() == {"message": "Successfully logged out"} 