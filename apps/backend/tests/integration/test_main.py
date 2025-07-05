"""
@fileoverview Integration Tests for the Main FastAPI Application
@module tests.integration.test_main

@description
This file contains integration tests for the main FastAPI application instance
defined in `backend/main.py`. It verifies that core application components
like middleware (CORS, logging), route inclusion, and exception handlers are
all configured and functioning correctly.
"""

import pytest
from fastapi.testclient import TestClient

from backend.config import settings

# The client fixture is provided by conftest.py

class TestMainApp:
    """
    Test suite for the main application entrypoint.
    """

    def test_root_endpoint(self, client: TestClient):
        """
        Verify the root endpoint '/' returns a welcome message.
        """
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to TRAIDER V1 API"
        assert "version" in data

    def test_api_router_inclusion(self, client: TestClient):
        """
        Verify that API sub-routers are correctly included under the /api/v1 prefix.
        """
        # Test a known endpoint from the health router
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

        # Test a known endpoint from the auth router (requires no auth)
        # We can expect 422 if no body is sent, which proves the route exists.
        response = client.post("/api/v1/auth/login")
        assert response.status_code == 422 # Unprocessable Entity

    def test_cors_middleware_allowed_origin(self, client: TestClient):
        """
        Verify that the CORS middleware correctly handles allowed origins.
        """
        # The default allowed origin in the test environment is http://localhost:3000
        headers = {"Origin": "http://localhost:3000"}
        response = client.get("/", headers=headers)
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_cors_middleware_disallowed_origin(self, client: TestClient):
        """
        Verify that the CORS middleware blocks disallowed origins.
        """
        headers = {"Origin": "http://malicious-site.com"}
        response = client.get("/", headers=headers)
        assert response.status_code == 200
        # For a simple request, the header might be absent if the origin is not allowed.
        # A more complex pre-flight request would fail, but this is a good basic check.
        assert "access-control-allow-origin" not in response.headers

    def test_request_logging_middleware(self, client: TestClient):
        """
        Verify that the custom request logging middleware adds performance headers.
        """
        response = client.get("/")
        assert response.status_code == 200
        assert "x-process-time" in response.headers
        assert "x-request-id" in response.headers
        
        # Check that the process time is a float-like string
        try:
            float(response.headers["x-process-time"])
        except ValueError:
            pytest.fail("x-process-time header is not a valid float")

    def test_not_found_handler(self, client: TestClient):
        """
        Verify that requests to non-existent endpoints return a 404 error.
        """
        response = client.get("/non-existent-path")
        assert response.status_code == 404
        assert response.json() == {"detail": "Not Found"} 