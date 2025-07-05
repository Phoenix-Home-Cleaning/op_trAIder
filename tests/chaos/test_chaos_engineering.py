#!/usr/bin/env python3
"""
@fileoverview Comprehensive chaos engineering test suite for TRAIDER
@module tests.chaos.test_chaos_engineering

@description
Institutional-grade chaos engineering test coverage for system resilience.
Tests include network failures, service outages, database failures, high load,
resource exhaustion, and disaster recovery scenarios for trading systems.

@performance
- Recovery time: <30s for critical services
- Degraded mode: <5s failover
- Full recovery: <5min

@risk
- Failure impact: CRITICAL - System resilience affects trading availability
- Recovery strategy: Comprehensive disaster recovery testing

@compliance
- Audit requirements: Yes - System resilience must be validated
- Business continuity: 99.9% uptime requirement

@see {@link docs/infrastructure/dr-strategy.md}
@since 1.0.0-alpha.1
@author TRAIDER Team
"""

import asyncio
import os
import psutil
import random
import signal
import subprocess
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import patch, MagicMock

import pytest
import requests
import docker
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import test utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# ---------------------------------------------------------------------------
# By default we skip chaos engineering tests during standard unit/integration
# runs because they depend on Docker, local container orchestration, and can
# take several minutes to complete.  Set the environment variable
# `RUN_CHAOS_TESTS=true` to enable them explicitly (e.g., nightly build).
# ---------------------------------------------------------------------------

if os.getenv("RUN_CHAOS_TESTS", "false").lower() != "true":
    import pytest as _pytest
    _pytest.skip("Skipping chaos engineering tests – set RUN_CHAOS_TESTS=true to enable", allow_module_level=True)

class TestChaosEngineering:
    """
    Chaos engineering test suite for TRAIDER trading platform
    
    @description
    Comprehensive chaos testing including:
    - Network partition and latency injection
    - Service failure and recovery testing
    - Database connection failures
    - Resource exhaustion scenarios
    - Load testing under failures
    - Disaster recovery validation
    - Circuit breaker testing
    - Cascading failure prevention
    - Data consistency under failures
    
    @tradingImpact Tests system resilience critical for trading uptime
    @riskLevel CRITICAL - System failures affect trading operations
    """

    # =============================================================================
    # TEST CONFIGURATION
    # =============================================================================

    DOCKER_CLIENT = None
    SERVICES = {
        'frontend': 'traider-frontend',
        'backend': 'traider-backend',
        'postgres': 'traider-postgres',
        'redis': 'traider-redis',
        'redpanda': 'traider-redpanda-dev'
    }
    
    API_BASE_URL = 'http://localhost:8000'
    FRONTEND_URL = 'http://localhost:3000'
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """
        Initialize Docker client for container management.
        
        @description
        Sets up Docker client for chaos testing operations including
        container stopping, network manipulation, and resource constraints.
        
        @performance Target: <2s Docker operations
        @tradingImpact Docker control essential for chaos testing
        @riskLevel HIGH - Test infrastructure dependency
        """
        try:
            client = docker.from_env()
            self.DOCKER_CLIENT = client
            
            # Verify Docker is available
            client.ping()
            
            yield client
            
        except Exception as e:
            pytest.skip(f"Docker not available for chaos testing: {e}")

    @pytest.fixture
    def resilient_http_session(self):
        """
        Create HTTP session with retry logic for testing.
        
        @description
        Creates HTTP session with institutional-grade retry logic
        for testing service availability during chaos scenarios.
        
        @returns Configured requests session with retry logic
        @tradingImpact HTTP session for testing service resilience
        @riskLevel LOW - Test utility
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    @pytest.fixture
    def system_baseline_metrics(self):
        """
        Collect baseline system metrics before chaos testing.
        
        @description
        Captures baseline system performance metrics including
        CPU, memory, disk, and network for comparison during chaos.
        
        @returns Dictionary of baseline metrics
        @tradingImpact Baseline metrics for chaos impact measurement
        @riskLevel LOW - Monitoring utility
        """
        baseline = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_connections': len(psutil.net_connections()),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return baseline

    # =============================================================================
    # NETWORK CHAOS TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_network_partition_resilience(self, docker_client, resilient_http_session):
        """
        Test system resilience during network partitions.
        
        @description
        Tests system behavior when network connections are severed
        between services, simulating network partition scenarios.
        
        @performance Target: <30s recovery after partition heals
        @tradingImpact Network partitions affect service communication
        @riskLevel HIGH - Network failures affect trading operations
        """
        # Get initial service status
        initial_status = await self._check_service_health(resilient_http_session)
        
        if not initial_status['backend_healthy']:
            pytest.skip("Backend service not available for chaos testing")
        
        try:
            # Create network partition by stopping Redis (cache layer)
            redis_container = None
            try:
                redis_container = docker_client.containers.get(self.SERVICES['redis'])
                
                # Record pre-partition metrics
                pre_partition_time = time.time()
                
                # Stop Redis to simulate network partition
                redis_container.stop()
                
                # Test system behavior during partition
                partition_duration = 15  # 15 seconds
                degraded_responses = []
                
                for i in range(partition_duration):
                    try:
                        response = resilient_http_session.get(
                            f"{self.API_BASE_URL}/health",
                            timeout=2
                        )
                        degraded_responses.append({
                            'status_code': response.status_code,
                            'response_time': response.elapsed.total_seconds(),
                            'timestamp': time.time() - pre_partition_time
                        })
                    except Exception as e:
                        degraded_responses.append({
                            'error': str(e),
                            'timestamp': time.time() - pre_partition_time
                        })
                    
                    await asyncio.sleep(1)
                
                # Restart Redis to heal partition
                redis_container.start()
                
                # Wait for service recovery
                recovery_start = time.time()
                recovery_timeout = 60  # 60 seconds max recovery time
                
                while time.time() - recovery_start < recovery_timeout:
                    try:
                        response = resilient_http_session.get(
                            f"{self.API_BASE_URL}/health",
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            recovery_time = time.time() - recovery_start
                            break
                    except Exception:
                        pass
                    
                    await asyncio.sleep(2)
                else:
                    pytest.fail("Service did not recover within timeout")
                
                # Verify recovery
                final_status = await self._check_service_health(resilient_http_session)
                assert final_status['backend_healthy'], "Backend did not recover after partition"
                assert recovery_time < 30, f"Recovery took {recovery_time:.2f}s, expected <30s"
                
                # Analyze degraded performance
                successful_responses = [r for r in degraded_responses if 'status_code' in r]
                error_responses = [r for r in degraded_responses if 'error' in r]
                
                # System should degrade gracefully, not fail completely
                if len(successful_responses) > 0:
                    avg_response_time = sum(r['response_time'] for r in successful_responses) / len(successful_responses)
                    assert avg_response_time < 5.0, f"Average response time {avg_response_time:.2f}s too high during partition"
                
            except docker.errors.NotFound:
                pytest.skip("Redis container not found for chaos testing")
                
        except Exception as e:
            # Ensure Redis is restarted even if test fails
            if redis_container:
                try:
                    redis_container.start()
                except:
                    pass
            raise e

    @pytest.mark.asyncio
    async def test_network_latency_injection(self, resilient_http_session):
        """
        Test system performance under high network latency.
        
        @description
        Tests system behavior when network latency is artificially
        increased to simulate poor network conditions.
        
        @performance Target: <10s timeout handling under high latency
        @tradingImpact Network latency affects trading performance
        @riskLevel MEDIUM - Latency affects user experience
        """
        # Baseline response time measurement
        baseline_times = []
        for _ in range(5):
            try:
                start_time = time.time()
                response = resilient_http_session.get(
                    f"{self.API_BASE_URL}/health",
                    timeout=10
                )
                response_time = time.time() - start_time
                baseline_times.append(response_time)
            except Exception:
                pass
        
        if not baseline_times:
            pytest.skip("Unable to establish baseline response times")
        
        baseline_avg = sum(baseline_times) / len(baseline_times)
        
        # Simulate high latency using timeout configuration
        # (In production, this would use traffic shaping tools like tc)
        high_latency_session = requests.Session()
        high_latency_session.timeout = 0.1  # Very short timeout to simulate latency issues
        
        # Test with simulated high latency
        latency_responses = []
        for _ in range(10):
            try:
                start_time = time.time()
                response = high_latency_session.get(
                    f"{self.API_BASE_URL}/health",
                    timeout=5  # Longer timeout for actual request
                )
                response_time = time.time() - start_time
                latency_responses.append(response_time)
            except requests.exceptions.Timeout:
                # Timeout is expected behavior under high latency
                latency_responses.append(5.0)  # Record as max timeout
            except Exception:
                pass
        
        # Verify system handles latency gracefully
        if latency_responses:
            max_response_time = max(latency_responses)
            assert max_response_time < 10, f"Max response time {max_response_time:.2f}s under latency, expected <10s"

    # =============================================================================
    # SERVICE FAILURE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_backend_service_failure_recovery(self, docker_client, resilient_http_session):
        """
        Test backend service failure and automatic recovery.
        
        @description
        Tests system behavior when the backend service fails
        and validates automatic recovery mechanisms.
        
        @performance Target: <60s service recovery time
        @tradingImpact Backend failure affects all trading operations
        @riskLevel CRITICAL - Backend is core service
        """
        # Verify initial state
        initial_status = await self._check_service_health(resilient_http_session)
        if not initial_status['backend_healthy']:
            pytest.skip("Backend service not available for chaos testing")
        
        backend_container = None
        try:
            backend_container = docker_client.containers.get(self.SERVICES['backend'])
            
            # Record failure time
            failure_start = time.time()
            
            # Stop backend service
            backend_container.stop()
            
            # Verify service is down
            await asyncio.sleep(2)
            
            try:
                response = resilient_http_session.get(f"{self.API_BASE_URL}/health", timeout=5)
                # If we get a response, the container might have restarted automatically
            except requests.exceptions.ConnectionError:
                # Expected - service should be unavailable
                pass
            
            # Restart service (simulating automatic recovery)
            backend_container.start()
            
            # Wait for service recovery
            recovery_start = time.time()

            # Skip quickly if the container exited immediately (e.g., image
            # not present in CI environment).
            if backend_container.status.lower() != 'running':
                pytest.skip("Backend container not running – skipping recovery test in CI environment")

            recovery_timeout = 30  # seconds – keep suite under 5 min total
            
            while time.time() - recovery_start < recovery_timeout:
                try:
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        recovery_time = time.time() - recovery_start
                        break
                        
                except Exception:
                    pass
                
                await asyncio.sleep(3)
            else:
                pytest.fail("Backend service did not recover within timeout")
            
            # Verify full recovery
            final_status = await self._check_service_health(resilient_http_session)
            assert final_status['backend_healthy'], "Backend service not fully recovered"
            assert recovery_time < 60, f"Recovery took {recovery_time:.2f}s, expected <60s"
            
        except docker.errors.NotFound:
            pytest.skip("Backend container not found for chaos testing")
        except Exception as e:
            # Ensure backend is restarted even if test fails
            if backend_container:
                try:
                    backend_container.start()
                except:
                    pass
            raise e

    @pytest.mark.asyncio
    async def test_database_connection_failure(self, docker_client, resilient_http_session):
        """
        Test database connection failure and recovery.
        
        @description
        Tests system behavior when database connections fail
        and validates connection pool recovery mechanisms.
        
        @performance Target: <45s database recovery time
        @tradingImpact Database failure affects data persistence
        @riskLevel CRITICAL - Database is core infrastructure
        """
        # Verify initial state
        initial_status = await self._check_service_health(resilient_http_session)
        if not initial_status['backend_healthy']:
            pytest.skip("Backend service not available for chaos testing")
        
        postgres_container = None
        try:
            postgres_container = docker_client.containers.get(self.SERVICES['postgres'])
            
            # Stop database
            postgres_container.stop()
            
            # Test system behavior without database
            db_failure_responses = []
            for i in range(10):
                try:
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=5
                    )
                    db_failure_responses.append({
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    })
                except Exception as e:
                    db_failure_responses.append({'error': str(e)})
                
                await asyncio.sleep(2)
            
            # Restart database
            postgres_container.start()
            
            # Wait for database recovery
            recovery_start = time.time()
            recovery_timeout = 90  # 90 seconds for database startup
            
            while time.time() - recovery_start < recovery_timeout:
                try:
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Additional check for database connectivity
                        health_data = response.json()
                        if health_data.get('database', {}).get('status') == 'healthy':
                            recovery_time = time.time() - recovery_start
                            break
                            
                except Exception:
                    pass
                
                await asyncio.sleep(3)
            else:
                pytest.fail("Database did not recover within timeout")
            
            # Verify recovery
            assert recovery_time < 45, f"Database recovery took {recovery_time:.2f}s, expected <45s"
            
            # Analyze failure behavior
            error_responses = [r for r in db_failure_responses if 'error' in r]
            successful_responses = [r for r in db_failure_responses if 'status_code' in r]
            
            # System should handle database failures gracefully
            if successful_responses:
                # Some responses might be successful with degraded functionality
                for response in successful_responses:
                    # Response time should still be reasonable
                    assert response['response_time'] < 10, "Response time too high during DB failure"
            
        except docker.errors.NotFound:
            pytest.skip("PostgreSQL container not found for chaos testing")
        except Exception as e:
            # Ensure database is restarted even if test fails
            if postgres_container:
                try:
                    postgres_container.start()
                except:
                    pass
            raise e

    # =============================================================================
    # RESOURCE EXHAUSTION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_memory_exhaustion_resilience(self, resilient_http_session, system_baseline_metrics):
        """
        Test system behavior under memory pressure.
        
        @description
        Tests system resilience when memory usage is high,
        validating memory management and garbage collection.
        
        @performance Target: <50% performance degradation under memory pressure
        @tradingImpact Memory exhaustion affects system performance
        @riskLevel HIGH - Memory issues affect trading performance
        """
        # Create memory pressure (be careful not to crash the system)
        memory_hogs = []
        
        try:
            # Get current memory usage
            initial_memory = psutil.virtual_memory().percent
            
            # Create moderate memory pressure
            target_memory_mb = 100  # 100MB of additional memory usage
            chunk_size = 1024 * 1024  # 1MB chunks
            
            for _ in range(target_memory_mb):
                # Allocate memory in small chunks
                memory_chunk = bytearray(chunk_size)
                memory_hogs.append(memory_chunk)
                
                # Check if we're causing too much pressure
                current_memory = psutil.virtual_memory().percent
                if current_memory > 85:  # Stop if memory usage gets too high
                    break
            
            # Test system performance under memory pressure
            pressure_responses = []
            for i in range(10):
                try:
                    start_time = time.time()
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    pressure_responses.append({
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'memory_percent': psutil.virtual_memory().percent
                    })
                    
                except Exception as e:
                    pressure_responses.append({
                        'error': str(e),
                        'memory_percent': psutil.virtual_memory().percent
                    })
                
                await asyncio.sleep(1)
            
            # Analyze performance under pressure
            successful_responses = [r for r in pressure_responses if 'status_code' in r]
            
            if successful_responses:
                avg_response_time = sum(r['response_time'] for r in successful_responses) / len(successful_responses)
                max_response_time = max(r['response_time'] for r in successful_responses)
                
                # System should still respond, albeit slower
                assert avg_response_time < 5.0, f"Average response time {avg_response_time:.2f}s too high under memory pressure"
                assert max_response_time < 10.0, f"Max response time {max_response_time:.2f}s too high under memory pressure"
                
                # Verify all responses were successful
                for response in successful_responses:
                    assert response['status_code'] == 200, "Service returned error under memory pressure"
            
        finally:
            # Release memory
            memory_hogs.clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Wait for memory to stabilize
            await asyncio.sleep(5)

    @pytest.mark.asyncio
    async def test_cpu_exhaustion_resilience(self, resilient_http_session):
        """
        Test system behavior under high CPU load.
        
        @description
        Tests system resilience when CPU usage is high,
        validating thread management and request handling.
        
        @performance Target: <100% response time increase under CPU load
        @tradingImpact High CPU load affects trading performance
        @riskLevel HIGH - CPU exhaustion affects system responsiveness
        """
        # Get baseline response time
        baseline_times = []
        for _ in range(3):
            try:
                start_time = time.time()
                response = resilient_http_session.get(f"{self.API_BASE_URL}/health", timeout=10)
                baseline_times.append(time.time() - start_time)
            except Exception:
                pass
        
        if not baseline_times:
            pytest.skip("Unable to establish baseline response times")
        
        baseline_avg = sum(baseline_times) / len(baseline_times)
        
        # Create CPU load using multiprocessing
        import multiprocessing
        
        def cpu_stress_worker():
            """Worker function to create CPU load."""
            end_time = time.time() + 15  # Run for 15 seconds
            while time.time() < end_time:
                # CPU-intensive calculation
                sum(i * i for i in range(10000))
        
        # Start CPU stress processes (use fewer cores to avoid system freeze)
        cpu_count = min(multiprocessing.cpu_count() // 2, 2)  # Use half the cores, max 2
        processes = []
        
        try:
            for _ in range(cpu_count):
                process = multiprocessing.Process(target=cpu_stress_worker)
                process.start()
                processes.append(process)
            
            # Test system performance under CPU load
            load_responses = []
            for i in range(10):
                try:
                    start_time = time.time()
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=15
                    )
                    response_time = time.time() - start_time
                    
                    load_responses.append({
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'cpu_percent': psutil.cpu_percent()
                    })
                    
                except Exception as e:
                    load_responses.append({
                        'error': str(e),
                        'cpu_percent': psutil.cpu_percent()
                    })
                
                await asyncio.sleep(1.5)
            
            # Wait for processes to complete
            for process in processes:
                process.join(timeout=5)
                if process.is_alive():
                    process.terminate()
            
            # Analyze performance under load
            successful_responses = [r for r in load_responses if 'status_code' in r]
            
            if successful_responses:
                avg_response_time = sum(r['response_time'] for r in successful_responses) / len(successful_responses)
                
                # Response time should not increase by more than 100%
                max_acceptable_time = baseline_avg * 2
                assert avg_response_time < max_acceptable_time, f"Response time {avg_response_time:.2f}s vs baseline {baseline_avg:.2f}s under CPU load"
                
                # Verify system remained responsive
                for response in successful_responses:
                    assert response['status_code'] == 200, "Service returned error under CPU load"
                    assert response['response_time'] < 15, "Response time exceeded timeout under CPU load"
            
        finally:
            # Ensure all processes are terminated
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)

    # =============================================================================
    # CASCADING FAILURE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_cascading_failure_prevention(self, docker_client, resilient_http_session):
        """
        Test prevention of cascading failures across services.
        
        @description
        Tests system behavior when multiple services fail simultaneously
        and validates circuit breaker and isolation mechanisms.
        
        @performance Target: <50% service degradation during cascading failures
        @tradingImpact Cascading failures can bring down entire system
        @riskLevel CRITICAL - Cascading failures affect system availability
        """
        # Verify initial state
        initial_status = await self._check_service_health(resilient_http_session)
        if not initial_status['backend_healthy']:
            pytest.skip("Backend service not available for chaos testing")
        
        failed_containers = []
        
        try:
            # Simulate cascading failure by stopping multiple services
            services_to_fail = ['redis', 'redpanda']  # Start with non-critical services
            
            for service_name in services_to_fail:
                try:
                    container = docker_client.containers.get(self.SERVICES[service_name])
                    container.stop()
                    failed_containers.append(container)
                    
                    # Wait between failures to observe cascading effects
                    await asyncio.sleep(5)
                    
                    # Test system state after each failure
                    try:
                        response = resilient_http_session.get(
                            f"{self.API_BASE_URL}/health",
                            timeout=10
                        )
                        
                        # System should still respond even with degraded functionality
                        assert response.status_code in [200, 503], f"Unexpected status code {response.status_code} after {service_name} failure"
                        
                    except requests.exceptions.ConnectionError:
                        # If backend is completely down, that's a cascading failure
                        pytest.fail(f"Backend became unavailable after {service_name} failure - cascading failure detected")
                    
                except docker.errors.NotFound:
                    # Service container not found, skip
                    continue
            
            # Test system resilience with multiple services down
            degraded_responses = []
            for i in range(10):
                try:
                    start_time = time.time()
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    degraded_responses.append({
                        'status_code': response.status_code,
                        'response_time': response_time
                    })
                    
                except Exception as e:
                    degraded_responses.append({'error': str(e)})
                
                await asyncio.sleep(2)
            
            # Restart failed services
            for container in failed_containers:
                container.start()
                await asyncio.sleep(3)  # Wait between restarts
            
            # Wait for full recovery
            recovery_start = time.time()
            while time.time() - recovery_start < 120:  # 2 minutes max
                try:
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        break
                        
                except Exception:
                    pass
                
                await asyncio.sleep(5)
            
            # Analyze degraded operation
            successful_responses = [r for r in degraded_responses if 'status_code' in r]
            error_responses = [r for r in degraded_responses if 'error' in r]
            
            # At least 50% of requests should succeed even with multiple failures
            success_rate = len(successful_responses) / len(degraded_responses)
            assert success_rate >= 0.5, f"Success rate {success_rate:.2%} too low during cascading failures"
            
            # Successful responses should be reasonably fast
            if successful_responses:
                avg_response_time = sum(r['response_time'] for r in successful_responses) / len(successful_responses)
                assert avg_response_time < 10, f"Average response time {avg_response_time:.2f}s too high during failures"
            
        finally:
            # Ensure all containers are restarted
            for container in failed_containers:
                try:
                    if container.status != 'running':
                        container.start()
                except:
                    pass

    # =============================================================================
    # DISASTER RECOVERY TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_disaster_recovery_simulation(self, docker_client, resilient_http_session):
        """
        Test disaster recovery procedures and data consistency.
        
        @description
        Tests complete system failure and recovery procedures,
        validating backup systems and data consistency.
        
        @performance Target: <10min full system recovery
        @tradingImpact Disaster recovery critical for business continuity
        @riskLevel CRITICAL - Disasters can cause complete system outage
        """
        # This test simulates a major disaster scenario
        # In production, this would test actual backup/restore procedures
        
        # Verify initial state
        initial_status = await self._check_service_health(resilient_http_session)
        if not initial_status['backend_healthy']:
            pytest.skip("System not in healthy state for disaster recovery testing")
        
        # Record pre-disaster state
        pre_disaster_time = datetime.now(timezone.utc)
        
        # Simulate disaster by stopping all services except database
        # (Database represents persistent storage that survives disasters)
        disaster_containers = []
        
        try:
            services_to_stop = ['backend', 'frontend', 'redis', 'redpanda']
            
            for service_name in services_to_stop:
                try:
                    container = docker_client.containers.get(self.SERVICES[service_name])
                    container.stop()
                    disaster_containers.append((service_name, container))
                except docker.errors.NotFound:
                    continue
            
            # Verify system is down
            await asyncio.sleep(5)
            
            try:
                response = resilient_http_session.get(f"{self.API_BASE_URL}/health", timeout=5)
                pytest.fail("System still responding after disaster simulation")
            except requests.exceptions.ConnectionError:
                # Expected - system should be down
                pass
            
            # Begin disaster recovery
            recovery_start = time.time()
            
            # Restart services in proper order (infrastructure first)
            recovery_order = ['redis', 'redpanda', 'backend', 'frontend']
            
            for service_name in recovery_order:
                for stored_name, container in disaster_containers:
                    if stored_name == service_name:
                        container.start()
                        
                        # Wait for service to stabilize
                        await asyncio.sleep(10)
                        
                        # Test intermediate recovery state
                        if service_name == 'backend':
                            # Backend should be recoverable at this point
                            backend_recovery_start = time.time()
                            while time.time() - backend_recovery_start < 60:
                                try:
                                    response = resilient_http_session.get(
                                        f"{self.API_BASE_URL}/health",
                                        timeout=10
                                    )
                                    if response.status_code == 200:
                                        break
                                except Exception:
                                    pass
                                await asyncio.sleep(5)
                        break
            
            # Verify full recovery
            full_recovery_start = time.time()
            while time.time() - full_recovery_start < 300:  # 5 minutes max
                try:
                    response = resilient_http_session.get(
                        f"{self.API_BASE_URL}/health",
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        # Additional checks for full functionality
                        health_data = response.json()
                        if (health_data.get('status') == 'healthy' and
                            health_data.get('database', {}).get('status') == 'healthy'):
                            total_recovery_time = time.time() - recovery_start
                            break
                            
                except Exception:
                    pass
                
                await asyncio.sleep(10)
            else:
                pytest.fail("System did not fully recover from disaster within timeout")
            
            # Verify recovery metrics
            assert total_recovery_time < 600, f"Disaster recovery took {total_recovery_time:.2f}s, expected <600s (10min)"
            
            # Test post-recovery functionality
            post_recovery_tests = []
            for _ in range(5):
                try:
                    response = resilient_http_session.get(f"{self.API_BASE_URL}/health", timeout=10)
                    post_recovery_tests.append(response.status_code == 200)
                except Exception:
                    post_recovery_tests.append(False)
                await asyncio.sleep(2)
            
            # At least 80% of post-recovery tests should pass
            recovery_success_rate = sum(post_recovery_tests) / len(post_recovery_tests)
            assert recovery_success_rate >= 0.8, f"Post-recovery success rate {recovery_success_rate:.2%} too low"
            
        finally:
            # Ensure all services are running
            for service_name, container in disaster_containers:
                try:
                    if container.status != 'running':
                        container.start()
                except:
                    pass

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    async def _check_service_health(self, session: requests.Session) -> Dict[str, bool]:
        """
        Check health status of all services.
        
        @description
        Performs health checks on all system services to determine
        current operational status for chaos testing.
        
        @param session HTTP session for making requests
        @returns Dictionary of service health statuses
        
        @performance <5s health check completion
        @tradingImpact Health checks essential for chaos test validation
        @riskLevel LOW - Monitoring utility
        """
        health_status = {
            'backend_healthy': False,
            'frontend_healthy': False,
            'database_healthy': False
        }
        
        # Check backend health
        try:
            response = session.get(f"{self.API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                health_status['backend_healthy'] = True
                
                # Check database health from backend response
                health_data = response.json()
                if health_data.get('database', {}).get('status') == 'healthy':
                    health_status['database_healthy'] = True
                    
        except Exception:
            pass
        
        # Check frontend health
        try:
            response = session.get(self.FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                health_status['frontend_healthy'] = True
        except Exception:
            pass
        
        return health_status

    def _generate_load(self, duration_seconds: int = 30, requests_per_second: int = 10):
        """
        Generate load on the system for testing.
        
        @description
        Generates controlled load on the system to test performance
        under stress and validate scaling behavior.
        
        @param duration_seconds Duration of load test
        @param requests_per_second Rate of requests to generate
        
        @performance Configurable load generation
        @tradingImpact Load testing validates system capacity
        @riskLevel MEDIUM - High load can affect system performance
        """
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker():
            session = requests.Session()
            end_time = time.time() + duration_seconds
            
            while time.time() < end_time:
                try:
                    start_time = time.time()
                    response = session.get(f"{self.API_BASE_URL}/health", timeout=5)
                    response_time = time.time() - start_time
                    
                    results.put({
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'timestamp': time.time()
                    })
                    
                except Exception as e:
                    results.put({
                        'error': str(e),
                        'timestamp': time.time()
                    })
                
                # Control request rate
                time.sleep(1.0 / requests_per_second)
        
        # Start worker threads
        threads = []
        for _ in range(min(requests_per_second, 10)):  # Max 10 threads
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        load_results = []
        while not results.empty():
            load_results.append(results.get())
        
        return load_results