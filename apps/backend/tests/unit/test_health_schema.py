#!/usr/bin/env python3
"""
@fileoverview Contract tests for health check API endpoints
@module tests.unit.backend.test_health_schema

@description
Ensures that the health check endpoints (/live, /ready, /detailed) adhere to
their defined response schemas. This prevents regressions and breaking changes
for monitoring systems, Kubernetes probes, and operational dashboards that rely
on this contract.

@performance
- Schema validation: < 5ms per endpoint

@risk
- Failure impact: MEDIUM - Broken monitoring and orchestration if schemas change
- Recovery strategy: Revert breaking changes to health endpoints

@compliance
- Audit requirements: N/A

@see {@link docs/infrastructure/monitoring.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import pytest
from unittest.mock import patch, AsyncMock

from fastapi import status
from fastapi.responses import JSONResponse

from backend.api.health import liveness_probe, readiness_probe, detailed_health_check


@pytest.mark.asyncio
class TestHealthEndpointSchemas:
    """
    Validates the JSON response structure of all health-related endpoints.
    """

    async def test_liveness_probe_schema(self):
        """
        Validates the schema for the /live endpoint.
        
        @description Ensures the liveness probe returns 'status', 'timestamp',
        and 'service' keys for Kubernetes and basic monitoring.
        @riskLevel LOW
        """
        response = await liveness_probe()
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK

        data = response.body
        import json
        content = json.loads(data)

        assert "status" in content
        assert "timestamp" in content
        assert "service" in content
        assert content["status"] == "alive"

    @patch('backend.api.health.check_database_health', new_callable=AsyncMock)
    async def test_readiness_probe_schema(self, mock_db_health):
        """
        Validates the schema for the /ready endpoint.
        
        @description The readiness probe must include a 'dependencies' object
        (aliased as 'checks') containing the database health status. This is
        critical for automated systems to diagnose startup and runtime issues.
        @riskLevel MEDIUM
        """
        mock_db_health.return_value = {"status": "healthy", "response_time_ms": 5.0}

        response = await readiness_probe()
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.body
        import json
        content = json.loads(data)

        assert "status" in content
        assert "dependencies" in content
        assert "checks" in content # Test the alias for backward compatibility
        assert "database" in content["dependencies"]
        assert content["dependencies"] == content["checks"]
        assert content["status"] == "ready"

    @patch('backend.api.health.get_system_info')
    @patch('backend.api.health.check_database_health', new_callable=AsyncMock)
    async def test_detailed_health_check_schema(self, mock_db_health, mock_sys_info):
        """
        Validates the schema for the /detailed endpoint.
        
        @description The detailed health check must provide a comprehensive, multi-level
        view of the system's health. This test validates the presence of critical
        top-level keys ('service', 'system', 'dependencies', 'database') and the
        nested 'service_info' object for detailed monitoring.
        @riskLevel MEDIUM
        """
        mock_sys_info.return_value = {"cpu": {"usage_percent": 10.0}}
        mock_db_health.return_value = {"status": "healthy", "response_time_ms": 5.0}

        response = await detailed_health_check()
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK

        data = response.body
        import json
        content = json.loads(data)
        
        # --- Top-level keys ---
        assert "status" in content
        assert "service" in content          # Flat string for simple displays
        assert "service_info" in content     # Nested object for detailed dashboards
        assert "system" in content
        assert "dependencies" in content
        assert "database" in content         # Alias for quick access
        
        # --- Content validation ---
        assert content["status"] == "healthy"
        assert content["service"] == "TRAIDER V1 API"
        assert content["dependencies"]["database"]["status"] == "healthy"
        assert content["database"]["status"] == "healthy"

    @patch('backend.api.health.check_database_health', new_callable=AsyncMock)
    async def test_readiness_probe_failure_schema(self, mock_db_health):
        """
        Validates the schema for a failing /ready endpoint.
        
        @description Ensures that even in a failure condition, the readiness
        probe returns a consistent schema with a 'not_ready' status, allowing
        orchestrators to correctly handle the state.
        @riskLevel MEDIUM
        """
        mock_db_health.return_value = {"status": "unhealthy", "error": "Connection failed"}
        
        response = await readiness_probe()
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

        data = response.body
        import json
        content = json.loads(data)

        assert content["status"] == "not_ready"
        assert "dependencies" in content
        assert "database" in content["dependencies"]
        assert content["dependencies"]["database"]["status"] == "unhealthy" 