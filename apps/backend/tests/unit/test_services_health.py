#!/usr/bin/env python3
"""
@fileoverview Comprehensive test suite for TRAIDER health check service
@module tests.unit.backend.test_services_health

@description
Institutional-grade test coverage for the health check API service.
Tests include system monitoring, database connectivity, performance metrics,
error scenarios, and operational visibility features.

@performance
- Health check response: <100ms
- Test execution: <50ms per test
- System metrics collection: <10ms

@risk
- Failure impact: MEDIUM - Health monitoring affects operational visibility
- Recovery strategy: Fallback monitoring systems

@compliance
- Audit requirements: Yes - Health monitoring must be tested
- Operational monitoring: All health endpoints covered

@see {@link backend/api/health.py}
@since 1.0.0-alpha.1
@author TRAIDER Team
"""

import os
import time
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any

from fastapi import status
from fastapi.responses import JSONResponse

# Import the health module and its components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from api.health import (
    router,
    get_system_info,
    health_check,
    liveness_probe,
    readiness_probe,
    detailed_health_check,
    prometheus_metrics
)

class TestHealthCheckService:
    """
    Health check service test suite
    
    @description
    Comprehensive testing of the health check service including:
    - Basic health check endpoints
    - System information collection
    - Database connectivity testing
    - Performance metrics monitoring
    - Kubernetes probe compatibility
    - Error handling and edge cases
    - Prometheus metrics integration
    
    @tradingImpact Tests operational visibility for trading system health
    @riskLevel MEDIUM - Health monitoring affects operational decisions
    """

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """
        Setup test environment with mocked dependencies.
        
        @description
        Sets up isolated test environment with mocked system
        dependencies for consistent health check testing.
        
        @performance Target: <10ms setup time
        @tradingImpact Ensures isolated test environment
        @riskLevel LOW - Test environment isolation
        """
        # Mock logging to avoid test output pollution
        with patch('api.health.logger'):
            yield

    @pytest.fixture
    def mock_system_metrics(self):
        """
        Create mock system metrics for testing.
        
        @description
        Provides mock system metrics data for health check tests
        with realistic system information.
        
        @returns Dict with mock system metrics
        @tradingImpact Mock system data for testing health monitoring
        @riskLevel LOW - Test data creation
        """
        return {
            "platform": {
                "system": "Linux",
                "release": "5.4.0",
                "version": "#1 SMP Ubuntu 20.04",
                "machine": "x86_64",
                "processor": "x86_64",
                "python_version": "3.9.0",
            },
            "cpu": {
                "usage_percent": 25.5,
                "count": 4,
                "load_avg": [0.5, 0.3, 0.2],
            },
            "memory": {
                "total_gb": 16.0,
                "available_gb": 12.5,
                "used_gb": 3.5,
                "usage_percent": 21.9,
            },
            "disk": {
                "total_gb": 500.0,
                "free_gb": 350.0,
                "used_gb": 150.0,
                "usage_percent": 30.0,
            },
            "network": {
                "bytes_sent": 1048576,
                "bytes_recv": 2097152,
                "packets_sent": 1000,
                "packets_recv": 1500,
            },
        }

    @pytest.fixture
    def mock_database_health(self):
        """
        Create mock database health data for testing.
        
        @description
        Provides mock database health data for health check tests
        with realistic database connectivity information.
        
        @returns Dict with mock database health data
        @tradingImpact Mock database data for testing health monitoring
        @riskLevel LOW - Test data creation
        """
        return {
            "status": "healthy",
            "response_time_ms": 5.2,
            "connection_pool": {
                "active": 2,
                "idle": 8,
                "total": 10,
            },
            "last_check": time.time(),
        }

    # =============================================================================
    # SYSTEM INFORMATION TESTS
    # =============================================================================

    @patch('api.health.psutil')
    @patch('api.health.platform')
    @patch('api.health.os')
    def test_get_system_info_success(self, mock_os, mock_platform, mock_psutil, mock_system_metrics):
        """
        Test successful system information collection.
        
        @description
        Tests system information collection with mocked system
        dependencies and validates proper metrics gathering.
        
        @performance Target: <10ms system info collection
        @tradingImpact System info essential for operational monitoring
        @riskLevel MEDIUM - System monitoring validation
        """
        # Mock platform information
        mock_platform.system.return_value = "Linux"
        mock_platform.release.return_value = "5.4.0"
        mock_platform.version.return_value = "#1 SMP Ubuntu 20.04"
        mock_platform.machine.return_value = "x86_64"
        mock_platform.processor.return_value = "x86_64"
        mock_platform.python_version.return_value = "3.9.0"
        
        # Mock psutil metrics
        mock_psutil.cpu_percent.return_value = 25.5
        mock_psutil.cpu_count.return_value = 4
        
        # Mock memory information
        mock_memory = MagicMock()
        mock_memory.total = 16 * 1024**3  # 16GB
        mock_memory.available = 12.5 * 1024**3  # 12.5GB
        mock_memory.used = 3.5 * 1024**3  # 3.5GB
        mock_memory.percent = 21.9
        mock_psutil.virtual_memory.return_value = mock_memory
        
        # Mock disk information
        mock_disk = MagicMock()
        mock_disk.total = 500 * 1024**3  # 500GB
        mock_disk.free = 350 * 1024**3  # 350GB
        mock_disk.used = 150 * 1024**3  # 150GB
        mock_psutil.disk_usage.return_value = mock_disk
        
        # Mock network information
        mock_network = MagicMock()
        mock_network.bytes_sent = 1048576
        mock_network.bytes_recv = 2097152
        mock_network.packets_sent = 1000
        mock_network.packets_recv = 1500
        mock_psutil.net_io_counters.return_value = mock_network
        
        # Mock load average
        mock_os.getloadavg.return_value = [0.5, 0.3, 0.2]
        mock_os.hasattr = lambda obj, name: name == 'getloadavg'
        
        start_time = time.time()
        
        # Test system info collection
        system_info = get_system_info()
        
        # Verify system info structure
        assert isinstance(system_info, dict)
        assert "platform" in system_info
        assert "cpu" in system_info
        assert "memory" in system_info
        assert "disk" in system_info
        assert "network" in system_info
        
        # Verify platform information
        assert system_info["platform"]["system"] == "Linux"
        assert system_info["platform"]["python_version"] == "3.9.0"
        
        # Verify CPU information
        assert system_info["cpu"]["usage_percent"] == 25.5
        assert system_info["cpu"]["count"] == 4
        assert system_info["cpu"]["load_avg"] == [0.5, 0.3, 0.2]
        
        # Verify memory information
        assert system_info["memory"]["total_gb"] == 16.0
        assert system_info["memory"]["usage_percent"] == 21.9
        
        # Verify disk information
        assert system_info["disk"]["total_gb"] == 500.0
        assert system_info["disk"]["usage_percent"] == 30.0
        
        # Verify network information
        assert system_info["network"]["bytes_sent"] == 1048576
        assert system_info["network"]["packets_recv"] == 1500
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 10, f"System info collection took {execution_time:.2f}ms, expected <10ms"

    @patch('api.health.psutil')
    def test_get_system_info_error_handling(self, mock_psutil):
        """
        Test system information collection error handling.
        
        @description
        Tests system information collection with simulated errors
        and validates proper error handling and fallback.
        
        @performance Target: <10ms error handling
        @tradingImpact Error handling ensures monitoring resilience
        @riskLevel MEDIUM - Error handling validation
        """
        # Mock psutil to raise exception
        mock_psutil.cpu_percent.side_effect = Exception("CPU metrics unavailable")
        
        # Test error handling
        system_info = get_system_info()
        
        # Verify error response
        assert isinstance(system_info, dict)
        assert "error" in system_info
        assert system_info["error"] == "System information unavailable"

    # =============================================================================
    # BASIC HEALTH CHECK TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """
        Test basic health check endpoint.
        
        @description
        Tests basic health check endpoint response format,
        status code, and performance characteristics.
        
        @performance Target: <1ms response time
        @tradingImpact Basic health check essential for load balancers
        @riskLevel LOW - Basic health monitoring
        """
        start_time = time.time()
        
        # Test health check
        response = await health_check()
        
        # Verify response structure
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == "healthy"
        assert data["service"] == "TRAIDER V1 API"
        assert data["version"] == "1.0.0-alpha"
        assert "timestamp" in data
        assert "uptime_seconds" in data
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 1, f"Health check took {execution_time:.2f}ms, expected <1ms"

    @pytest.mark.asyncio
    async def test_liveness_probe_success(self):
        """
        Test successful liveness probe.
        
        @description
        Tests Kubernetes liveness probe with successful response
        and proper status indication.
        
        @performance Target: <1ms response time
        @tradingImpact Liveness probe essential for container management
        @riskLevel MEDIUM - Container lifecycle management
        """
        start_time = time.time()
        
        # Test liveness probe
        response = await liveness_probe()
        
        # Verify response structure
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == "alive"
        assert data["service"] == "TRAIDER V1 API"
        assert "timestamp" in data
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 1, f"Liveness probe took {execution_time:.2f}ms, expected <1ms"

    @patch('api.health.time.time')
    def test_liveness_probe_error_handling(self, mock_time):
        """
        Test liveness probe error handling.
        
        @description
        Tests liveness probe with simulated errors and validates
        proper error response and status codes.
        
        @performance Target: <10ms error handling
        @tradingImpact Error handling ensures probe reliability
        @riskLevel MEDIUM - Probe error handling
        """
        # Mock time to raise exception
        mock_time.side_effect = Exception("Time service unavailable")
        
        # Test error handling
        async def test_error():
            response = await liveness_probe()
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            
            content = response.body.decode()
            import json
            data = json.loads(content)
            assert data["status"] == "unhealthy"
        
        # Run the async test
        asyncio.run(test_error())

    # =============================================================================
    # READINESS PROBE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    @patch('api.health.check_database_health')
    async def test_readiness_probe_success(self, mock_db_health, mock_database_health):
        """
        Test successful readiness probe.
        
        @description
        Tests Kubernetes readiness probe with successful database
        connectivity and proper readiness indication.
        
        @performance Target: <100ms response time including DB check
        @tradingImpact Readiness probe essential for service routing
        @riskLevel HIGH - Service readiness validation
        """
        # Mock successful database health
        mock_db_health.return_value = mock_database_health
        
        start_time = time.time()
        
        # Test readiness probe
        response = await readiness_probe()
        
        # Verify response structure
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == "ready"
        assert data["service"] == "TRAIDER V1 API"
        assert "timestamp" in data
        assert "checks" in data
        assert data["checks"]["database"]["status"] == "healthy"
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 100, f"Readiness probe took {execution_time:.2f}ms, expected <100ms"

    @pytest.mark.asyncio
    @patch('api.health.check_database_health')
    async def test_readiness_probe_database_failure(self, mock_db_health):
        """
        Test readiness probe with database failure.
        
        @description
        Tests readiness probe with database connectivity failure
        and validates proper not-ready response.
        
        @performance Target: <100ms error response time
        @tradingImpact Database failure affects service readiness
        @riskLevel HIGH - Database connectivity validation
        """
        # Mock database health failure
        mock_db_health.side_effect = Exception("Database connection failed")
        
        # Test readiness probe with DB failure
        response = await readiness_probe()
        
        # Verify error response
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Verify response content
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == "not_ready"
        assert "error" in data

    # =============================================================================
    # DETAILED HEALTH CHECK TESTS
    # =============================================================================

    @pytest.mark.asyncio
    @patch('api.health.check_database_health')
    @patch('api.health.get_system_info')
    async def test_detailed_health_check_success(self, mock_system_info, mock_db_health, 
                                               mock_system_metrics, mock_database_health):
        """
        Test successful detailed health check.
        
        @description
        Tests detailed health check with comprehensive system
        and database information collection.
        
        @performance Target: <100ms comprehensive health check
        @tradingImpact Detailed health check provides operational visibility
        @riskLevel MEDIUM - Comprehensive health monitoring
        """
        # Mock successful responses
        mock_system_info.return_value = mock_system_metrics
        mock_db_health.return_value = mock_database_health
        
        start_time = time.time()
        
        # Test detailed health check
        response = await detailed_health_check()
        
        # Verify response structure
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == "healthy"
        assert data["service"] == "TRAIDER V1 API"
        assert "timestamp" in data
        assert "system" in data
        assert "database" in data
        
        # Verify system information
        assert data["system"]["cpu"]["usage_percent"] == 25.5
        assert data["system"]["memory"]["total_gb"] == 16.0
        
        # Verify database information
        assert data["database"]["status"] == "healthy"
        assert data["database"]["response_time_ms"] == 5.2
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 100, f"Detailed health check took {execution_time:.2f}ms, expected <100ms"

    @pytest.mark.asyncio
    @patch('api.health.check_database_health')
    @patch('api.health.get_system_info')
    async def test_detailed_health_check_partial_failure(self, mock_system_info, mock_db_health):
        """
        Test detailed health check with partial failures.
        
        @description
        Tests detailed health check with some components failing
        and validates proper degraded status reporting.
        
        @performance Target: <100ms error handling
        @tradingImpact Partial failures should be properly reported
        @riskLevel MEDIUM - Partial failure handling
        """
        # Mock system info success, database failure
        mock_system_info.return_value = {"cpu": {"usage_percent": 50.0}}
        mock_db_health.side_effect = Exception("Database unavailable")
        
        # Test detailed health check with partial failure
        response = await detailed_health_check()
        
        # Verify response structure
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Verify response content
        content = response.body.decode()
        import json
        data = json.loads(content)
        
        assert data["status"] == "degraded"
        assert "system" in data
        assert "database" in data
        assert "error" in data["database"]

    # =============================================================================
    # PROMETHEUS METRICS TESTS
    # =============================================================================

    @pytest.mark.asyncio
    @patch('api.health.check_database_health')
    @patch('api.health.get_system_info')
    async def test_prometheus_metrics_endpoint(self, mock_system_info, mock_db_health,
                                             mock_system_metrics, mock_database_health):
        """
        Test Prometheus metrics endpoint.
        
        @description
        Tests Prometheus metrics endpoint with proper metrics
        format and content for monitoring integration.
        
        @performance Target: <50ms metrics generation
        @tradingImpact Prometheus metrics essential for monitoring
        @riskLevel MEDIUM - Metrics monitoring integration
        """
        # Mock successful responses
        mock_system_info.return_value = mock_system_metrics
        mock_db_health.return_value = mock_database_health
        
        start_time = time.time()
        
        # Test Prometheus metrics
        response = await prometheus_metrics()
        
        # Verify response format
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Verify Prometheus format
        lines = response.strip().split('\n')
        assert any('# HELP' in line for line in lines)  # Help comments
        assert any('# TYPE' in line for line in lines)  # Type definitions
        
        # Verify specific metrics
        assert 'traider_health_status' in response
        assert 'traider_cpu_usage_percent' in response
        assert 'traider_memory_usage_percent' in response
        assert 'traider_disk_usage_percent' in response
        assert 'traider_database_response_time_ms' in response
        
        # Performance check
        execution_time = (time.time() - start_time) * 1000
        assert execution_time < 50, f"Metrics generation took {execution_time:.2f}ms, expected <50ms"

    @pytest.mark.asyncio
    @patch('api.health.check_database_health')
    @patch('api.health.get_system_info')
    async def test_prometheus_metrics_error_handling(self, mock_system_info, mock_db_health):
        """
        Test Prometheus metrics with error handling.
        
        @description
        Tests Prometheus metrics endpoint with component failures
        and validates proper error metric reporting.
        
        @performance Target: <50ms error metrics generation
        @tradingImpact Error metrics essential for alerting
        @riskLevel MEDIUM - Error metrics handling
        """
        # Mock system info failure
        mock_system_info.side_effect = Exception("System metrics unavailable")
        mock_db_health.side_effect = Exception("Database metrics unavailable")
        
        # Test Prometheus metrics with errors
        response = await prometheus_metrics()
        
        # Verify response format
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Verify error metrics
        assert 'traider_health_status 0' in response  # 0 = unhealthy
        assert 'traider_system_error 1' in response   # 1 = error present

    # =============================================================================
    # PERFORMANCE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self):
        """
        Test concurrent health check performance.
        
        @description
        Tests multiple concurrent health check requests to validate
        performance under load and resource efficiency.
        
        @performance Target: <200ms for 10 concurrent checks
        @tradingImpact Concurrent performance affects monitoring scalability
        @riskLevel MEDIUM - Performance under load
        """
        import asyncio
        
        async def single_health_check():
            return await health_check()
        
        start_time = time.time()
        
        # Test concurrent health checks
        tasks = [single_health_check() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Verify all responses
        assert len(responses) == 10
        for response in responses:
            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_200_OK
        
        # Performance check
        total_time_ms = total_time * 1000
        assert total_time_ms < 200, f"Concurrent health checks took {total_time_ms:.2f}ms, expected <200ms"

    @pytest.mark.asyncio
    async def test_health_check_memory_usage(self):
        """
        Test health check memory usage.
        
        @description
        Tests health check memory consumption to ensure
        efficient resource usage and no memory leaks.
        
        @performance Target: Stable memory usage
        @tradingImpact Memory efficiency affects system stability
        @riskLevel MEDIUM - Memory usage validation
        """
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform multiple health checks
        for _ in range(100):
            response = await health_check()
            assert response.status_code == status.HTTP_200_OK
        
        # Force garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (< 1MB)
        assert memory_increase < 1024 * 1024, f"Memory increased by {memory_increase} bytes, expected <1MB"

    # =============================================================================
    # EDGE CASES AND ERROR SCENARIOS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_health_check_stability(self):
        """
        Test health check endpoint stability.
        
        @description
        Tests health check endpoint stability under various
        conditions and validates consistent behavior.
        
        @performance Target: <100ms for stability test
        @tradingImpact Stability ensures reliable monitoring
        @riskLevel HIGH - Health check reliability
        """
        # Test multiple rapid requests
        start_time = time.time()
        
        for i in range(50):
            response = await health_check()
            assert response.status_code == status.HTTP_200_OK
            
            # Verify response consistency
            content = response.body.decode()
            import json
            data = json.loads(content)
            assert data["status"] == "healthy"
            assert data["service"] == "TRAIDER V1 API"
        
        total_time = time.time() - start_time
        
        # Performance check
        total_time_ms = total_time * 1000
        assert total_time_ms < 100, f"Stability test took {total_time_ms:.2f}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_health_check_response_format_consistency(self):
        """
        Test health check response format consistency.
        
        @description
        Tests health check response format consistency across
        multiple requests and validates schema compliance.
        
        @performance Target: <50ms format validation
        @tradingImpact Consistent format ensures monitoring compatibility
        @riskLevel MEDIUM - Response format validation
        """
        # Required fields for health check response
        required_fields = ["status", "service", "version", "timestamp", "uptime_seconds"]
        
        # Test multiple responses
        for _ in range(5):
            response = await health_check()
            assert response.status_code == status.HTTP_200_OK
            
            content = response.body.decode()
            import json
            data = json.loads(content)
            
            # Verify all required fields present
            for field in required_fields:
                assert field in data, f"Required field '{field}' missing from response"
            
            # Verify field types
            assert isinstance(data["status"], str)
            assert isinstance(data["service"], str)
            assert isinstance(data["version"], str)
            assert isinstance(data["timestamp"], (int, float))
            assert isinstance(data["uptime_seconds"], (int, float))

    @pytest.mark.asyncio
    async def test_health_check_under_system_stress(self):
        """
        Test health check behavior under system stress.
        
        @description
        Tests health check behavior when system resources
        are under stress and validates graceful degradation.
        
        @performance Target: <500ms under stress conditions
        @tradingImpact Stress behavior affects monitoring reliability
        @riskLevel HIGH - Stress condition handling
        """
        import threading
        import time
        
        # Create CPU stress in background
        def cpu_stress():
            end_time = time.time() + 2  # Run for 2 seconds
            while time.time() < end_time:
                pass  # Busy loop
        
        # Start stress threads
        stress_threads = [threading.Thread(target=cpu_stress) for _ in range(2)]
        for thread in stress_threads:
            thread.start()
        
        try:
            start_time = time.time()
            
            # Test health check under stress
            response = await health_check()
            
            execution_time = (time.time() - start_time) * 1000
            
            # Verify response even under stress
            assert response.status_code == status.HTTP_200_OK
            
            content = response.body.decode()
            import json
            data = json.loads(content)
            assert data["status"] == "healthy"
            
            # Performance should degrade gracefully
            assert execution_time < 500, f"Health check under stress took {execution_time:.2f}ms, expected <500ms"
            
        finally:
            # Wait for stress threads to complete
            for thread in stress_threads:
                thread.join()

    # =============================================================================
    # INTEGRATION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_health_endpoints_integration(self):
        """
        Test integration between different health endpoints.
        
        @description
        Tests integration and consistency between basic health,
        liveness, readiness, and detailed health endpoints.
        
        @performance Target: <200ms for all endpoints
        @tradingImpact Endpoint integration ensures monitoring completeness
        @riskLevel MEDIUM - Endpoint integration validation
        """
        start_time = time.time()
        
        # Test all health endpoints
        basic_response = await health_check()
        liveness_response = await liveness_probe()
        
        # Verify all endpoints respond successfully
        assert basic_response.status_code == status.HTTP_200_OK
        assert liveness_response.status_code == status.HTTP_200_OK
        
        # Verify response consistency
        basic_content = basic_response.body.decode()
        liveness_content = liveness_response.body.decode()
        
        import json
        basic_data = json.loads(basic_content)
        liveness_data = json.loads(liveness_content)
        
        # Service name should be consistent
        assert basic_data["service"] == liveness_data["service"]
        
        # Both should indicate healthy/alive status
        assert basic_data["status"] == "healthy"
        assert liveness_data["status"] == "alive"
        
        total_time = (time.time() - start_time) * 1000
        assert total_time < 200, f"Health endpoints integration took {total_time:.2f}ms, expected <200ms"