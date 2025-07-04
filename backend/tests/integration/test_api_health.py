"""
@fileoverview API Integration Tests for Health Checks
@module tests.integration.test_api_health

@description
This file contains integration tests for the health check API endpoints defined
in `backend/api/health.py`. It uses FastAPI's TestClient to ensure that all
health endpoints (/health, /health/live, /health/ready, /health/detailed, /health/metrics)
are functioning correctly, return the expected status codes, and have the correct
response structure.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

class TestHealthAPI:
    """
    Integration tests for the health check API endpoints.
    """

    def test_basic_health_check(self, client: TestClient):
        """
        Verify the basic /health endpoint returns 200 OK and correct service info.
        """
        response = client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TRAIDER V1 API"
        assert "version" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data

    def test_liveness_probe(self, client: TestClient):
        """
        Verify the /health/live endpoint returns 200 OK for liveness check.
        """
        response = client.get("/api/v1/health/live")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "TRAIDER V1 API"

    @patch('backend.api.health.check_database_health', new_callable=AsyncMock)
    def test_readiness_probe_healthy(self, mock_db_check, client: TestClient):
        """
        Verify /health/ready returns 200 OK when all dependencies are healthy.
        """
        mock_db_check.return_value = {"status": "healthy"}
        response = client.get("/api/v1/health/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"
        assert data["dependencies"]["database"]["status"] == "healthy"

    @patch('backend.api.health.check_database_health', new_callable=AsyncMock)
    def test_readiness_probe_unhealthy(self, mock_db_check, client: TestClient):
        """
        Verify /health/ready returns 503 Service Unavailable if a dependency is unhealthy.
        """
        mock_db_check.return_value = {"status": "unhealthy", "error": "DB connection failed"}
        response = client.get("/api/v1/health/ready")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["dependencies"]["database"]["status"] == "unhealthy"

    def test_detailed_health_check(self, client: TestClient):
        """
        Verify the /health/detailed endpoint returns a comprehensive health report.
        """
        with patch('backend.api.health.check_database_health', new_callable=AsyncMock) as mock_db_check:
            mock_db_check.return_value = {"status": "healthy", "response_time_ms": 10.5}
            response = client.get("/api/v1/health/detailed")
            
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "service_info" in data
        assert "system" in data
        assert "cpu" in data["system"]
        assert "memory" in data["system"]
        assert "disk" in data["system"]
        assert "dependencies" in data
        assert data["dependencies"]["database"]["status"] == "healthy"

    def test_prometheus_metrics(self, client: TestClient):
        """
        Verify the /health/metrics endpoint returns Prometheus-formatted metrics.
        """
        response = client.get("/api/v1/health/metrics")
        assert response.status_code == status.HTTP_200_OK
        assert "text/plain" in response.headers["content-type"]
        
        content = response.text
        assert "# HELP" in content
        assert "# TYPE" in content
        assert "system_cpu_usage_percent" in content
        assert "system_memory_usage_percent" in content
        assert "process_uptime_seconds" in content 