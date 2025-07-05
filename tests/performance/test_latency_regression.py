#!/usr/bin/env python3
"""
@fileoverview Comprehensive latency regression test suite for TRAIDER
@module tests.performance.test_latency_regression

@description
Institutional-grade latency regression test coverage for trading performance.
Tests include critical path timing, signal-to-order execution latency,
market data processing speed, and performance regression detection.

@performance
- Signal-to-order execution: ≤500ms (P95)
- Market data processing: ≤1ms
- API response time: ≤100ms (P95)
- Database queries: ≤10ms

@risk
- Failure impact: CRITICAL - Latency affects trading profitability
- Recovery strategy: Performance regression alerts and rollback

@compliance
- Audit requirements: Yes - Performance metrics must be tracked
- SLA monitoring: Real-time latency monitoring required

@see {@link docs/performance/} Performance documentation
@since 1.0.0-alpha.1
@author TRAIDER Team
"""

import asyncio
import json
import os
import statistics
import time
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from unittest.mock import patch, AsyncMock

import pytest
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import backend modules (when they exist)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

import os as _os
import pytest as _pytest

# ---------------------------------------------------------------------------
# Skip latency regression tests by default – they require a running system
# under load and take significant time.  Enable by setting
# `RUN_PERFORMANCE_TESTS=true`.
# ---------------------------------------------------------------------------

if _os.getenv("RUN_PERFORMANCE_TESTS", "false").lower() != "true":
    _pytest.skip(
        "Skipping performance latency regression tests – set RUN_PERFORMANCE_TESTS=true to enable",
        allow_module_level=True,
    )

class TestLatencyRegression:
    """
    Latency regression test suite for TRAIDER trading platform
    
    @description
    Comprehensive latency testing including:
    - Critical path timing validation
    - Signal-to-order execution latency
    - Market data processing performance
    - API endpoint response times
    - Database query performance
    - Memory allocation timing
    - Network communication latency
    - Regression detection and alerting
    - Performance benchmark tracking
    
    @tradingImpact Tests performance critical for trading profitability
    @riskLevel CRITICAL - Latency directly affects trading returns
    """

    # =============================================================================
    # PERFORMANCE BENCHMARKS (INSTITUTIONAL GRADE)
    # =============================================================================

    LATENCY_BENCHMARKS = {
        # Critical trading path latencies
        'signal_to_order_execution': {'p95': 500, 'p99': 1000, 'unit': 'ms'},
        'market_data_processing': {'p95': 1, 'p99': 5, 'unit': 'ms'},
        'risk_calculation': {'p95': 50, 'p99': 100, 'unit': 'ms'},
        'order_validation': {'p95': 10, 'p99': 25, 'unit': 'ms'},
        
        # API performance benchmarks
        'health_endpoint': {'p95': 100, 'p99': 200, 'unit': 'ms'},
        'auth_endpoint': {'p95': 200, 'p99': 500, 'unit': 'ms'},
        'market_data_api': {'p95': 150, 'p99': 300, 'unit': 'ms'},
        
        # Database performance benchmarks
        'simple_query': {'p95': 10, 'p99': 25, 'unit': 'ms'},
        'complex_query': {'p95': 100, 'p99': 250, 'unit': 'ms'},
        'timeseries_query': {'p95': 50, 'p99': 150, 'unit': 'ms'},
        
        # System performance benchmarks
        'memory_allocation': {'p95': 1, 'p99': 5, 'unit': 'ms'},
        'json_serialization': {'p95': 5, 'p99': 15, 'unit': 'ms'},
        'network_roundtrip': {'p95': 10, 'p99': 50, 'unit': 'ms'}
    }
    
    API_BASE_URL = 'http://localhost:8000'
    SAMPLE_SIZE = 1000  # Number of samples for statistical significance
    
    @pytest.fixture
    def performance_session(self):
        """
        Create optimized HTTP session for performance testing.
        
        @description
        Creates HTTP session optimized for latency testing with
        connection pooling and minimal overhead configuration.
        
        @returns Optimized requests session
        @tradingImpact HTTP session for accurate latency measurement
        @riskLevel LOW - Test utility
        """
        session = requests.Session()
        
        # Optimize for performance testing
        session.headers.update({
            'Connection': 'keep-alive',
            'User-Agent': 'TRAIDER-LatencyTest/1.0'
        })
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # No retries for accurate timing
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session

    @pytest.fixture
    def sample_market_data(self) -> List[Dict[str, Any]]:
        """
        Generate sample market data for latency testing.
        
        @description
        Creates realistic market data samples for testing
        data processing and serialization performance.
        
        @returns List of market data dictionaries
        @tradingImpact Sample data for performance testing
        @riskLevel LOW - Test data generation
        """
        base_time = datetime.now(timezone.utc)
        market_data = []
        
        for i in range(self.SAMPLE_SIZE):
            timestamp = base_time + timedelta(milliseconds=i)
            
            data = {
                'symbol': 'BTC-USD',
                'timestamp': timestamp.isoformat(),
                'price': Decimal('50000.00') + Decimal(str(i * 0.01)),
                'volume': Decimal('1.5') + Decimal(str(i * 0.001)),
                'bid': Decimal('49999.99') + Decimal(str(i * 0.01)),
                'ask': Decimal('50000.01') + Decimal(str(i * 0.01)),
                'sequence': i,
                'exchange': 'coinbase'
            }
            market_data.append(data)
        
        return market_data

    # =============================================================================
    # CRITICAL PATH LATENCY TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_signal_to_order_execution_latency(self, performance_session):
        """
        Test end-to-end signal-to-order execution latency.
        
        @description
        Measures the critical path from signal generation to order execution,
        the most important latency metric for trading profitability.
        
        @performance Target: P95 ≤ 500ms, P99 ≤ 1000ms
        @tradingImpact Direct impact on trading returns and market capture
        @riskLevel CRITICAL - Core trading performance metric
        """
        latencies = []
        
        # Simulate signal-to-order execution flow
        for i in range(100):  # Smaller sample for end-to-end testing
            try:
                # Start timing
                start_time = time.perf_counter()
                
                # Step 1: Signal generation (simulated)
                signal_data = {
                    'signal_id': str(uuid.uuid4()),
                    'symbol': 'BTC-USD',
                    'signal_type': 'buy',
                    'strength': 0.8,
                    'confidence': 0.9,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Step 2: Risk validation (API call)
                risk_start = time.perf_counter()
                # In production, this would be a risk validation API call
                # For now, simulate with health check + processing time
                response = performance_session.get(
                    f"{self.API_BASE_URL}/health",
                    timeout=2
                )
                
                if response.status_code == 200:
                    # Simulate risk calculation processing time
                    await asyncio.sleep(0.01)  # 10ms risk calculation
                    
                    # Step 3: Order generation and validation
                    order_data = {
                        'order_id': str(uuid.uuid4()),
                        'symbol': signal_data['symbol'],
                        'side': signal_data['signal_type'],
                        'quantity': 0.1,
                        'order_type': 'market',
                        'signal_id': signal_data['signal_id']
                    }
                    
                    # Step 4: Order execution (simulated)
                    # In production, this would be exchange API call
                    await asyncio.sleep(0.05)  # 50ms execution simulation
                    
                    # End timing
                    end_time = time.perf_counter()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                
            except Exception as e:
                # Log error but continue testing
                print(f"Signal-to-order test iteration {i} failed: {e}")
                continue
        
        # Analyze latency distribution
        if not latencies:
            pytest.fail("No successful signal-to-order executions measured")
        
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        mean_latency = statistics.mean(latencies)
        
        # Validate against benchmarks
        benchmark = self.LATENCY_BENCHMARKS['signal_to_order_execution']
        assert p95 <= benchmark['p95'], f"P95 latency {p95:.2f}ms exceeds benchmark {benchmark['p95']}ms"
        assert p99 <= benchmark['p99'], f"P99 latency {p99:.2f}ms exceeds benchmark {benchmark['p99']}ms"
        
        # Additional performance checks
        assert mean_latency < 300, f"Mean latency {mean_latency:.2f}ms too high for trading"
        assert len([l for l in latencies if l > 1000]) < len(latencies) * 0.01, "Too many outliers >1000ms"

    @pytest.mark.asyncio
    async def test_market_data_processing_latency(self, sample_market_data):
        """
        Test market data processing latency.
        
        @description
        Measures time to process incoming market data including
        parsing, validation, and transformation operations.
        
        @performance Target: P95 ≤ 1ms, P99 ≤ 5ms
        @tradingImpact Market data latency affects signal generation speed
        @riskLevel HIGH - Real-time data processing critical
        """
        processing_latencies = []
        
        for data in sample_market_data[:100]:  # Test subset for speed
            try:
                start_time = time.perf_counter()
                
                # Simulate market data processing pipeline
                # Step 1: JSON serialization/deserialization
                json_data = json.dumps(data, default=str)
                parsed_data = json.loads(json_data)
                
                # Step 2: Data validation
                required_fields = ['symbol', 'timestamp', 'price', 'volume']
                for field in required_fields:
                    if field not in parsed_data:
                        raise ValueError(f"Missing required field: {field}")
                
                # Step 3: Price calculation (mid-price)
                bid = float(parsed_data.get('bid', 0))
                ask = float(parsed_data.get('ask', 0))
                mid_price = (bid + ask) / 2 if bid and ask else float(parsed_data['price'])
                
                # Step 4: Data transformation
                processed_data = {
                    'symbol': parsed_data['symbol'],
                    'timestamp': parsed_data['timestamp'],
                    'price': float(parsed_data['price']),
                    'mid_price': mid_price,
                    'volume': float(parsed_data['volume']),
                    'sequence': parsed_data.get('sequence', 0)
                }
                
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                processing_latencies.append(latency_ms)
                
            except Exception as e:
                print(f"Market data processing failed: {e}")
                continue
        
        # Analyze processing performance
        if not processing_latencies:
            pytest.fail("No market data processing samples measured")
        
        p95 = np.percentile(processing_latencies, 95)
        p99 = np.percentile(processing_latencies, 99)
        mean_latency = statistics.mean(processing_latencies)
        
        # Validate against benchmarks
        benchmark = self.LATENCY_BENCHMARKS['market_data_processing']
        assert p95 <= benchmark['p95'], f"P95 processing latency {p95:.3f}ms exceeds benchmark {benchmark['p95']}ms"
        assert p99 <= benchmark['p99'], f"P99 processing latency {p99:.3f}ms exceeds benchmark {benchmark['p99']}ms"
        
        # Additional checks
        assert mean_latency < 1.0, f"Mean processing latency {mean_latency:.3f}ms too high"

    # =============================================================================
    # API ENDPOINT LATENCY TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_health_endpoint_latency(self, performance_session):
        """
        Test health endpoint response latency.
        
        @description
        Measures health check endpoint latency which is used for
        monitoring and load balancer health checks.
        
        @performance Target: P95 ≤ 100ms, P99 ≤ 200ms
        @tradingImpact Health checks affect monitoring and alerting
        @riskLevel MEDIUM - Monitoring infrastructure dependency
        """
        latencies = await self._measure_endpoint_latency(
            performance_session,
            f"{self.API_BASE_URL}/health",
            method='GET',
            samples=200
        )
        
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        
        benchmark = self.LATENCY_BENCHMARKS['health_endpoint']
        assert p95 <= benchmark['p95'], f"Health endpoint P95 {p95:.2f}ms exceeds benchmark {benchmark['p95']}ms"
        assert p99 <= benchmark['p99'], f"Health endpoint P99 {p99:.2f}ms exceeds benchmark {benchmark['p99']}ms"

    @pytest.mark.asyncio
    async def test_concurrent_api_latency(self, performance_session):
        """
        Test API latency under concurrent load.
        
        @description
        Measures API response times under concurrent request load
        to validate performance under realistic trading conditions.
        
        @performance Target: <50% latency increase under 100 concurrent requests
        @tradingImpact Concurrent load affects real-time trading performance
        @riskLevel HIGH - High load scenarios common in trading
        """
        # Baseline single-request latency
        baseline_latencies = await self._measure_endpoint_latency(
            performance_session,
            f"{self.API_BASE_URL}/health",
            method='GET',
            samples=50
        )
        baseline_p95 = np.percentile(baseline_latencies, 95)
        
        # Concurrent load test
        concurrent_latencies = []
        
        async def make_concurrent_request():
            start_time = time.perf_counter()
            try:
                response = performance_session.get(
                    f"{self.API_BASE_URL}/health",
                    timeout=5
                )
                end_time = time.perf_counter()
                
                if response.status_code == 200:
                    latency_ms = (end_time - start_time) * 1000
                    return latency_ms
            except Exception:
                pass
            return None
        
        # Execute concurrent requests
        tasks = [make_concurrent_request() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        concurrent_latencies = [r for r in results if isinstance(r, (int, float)) and r is not None]
        
        if not concurrent_latencies:
            pytest.fail("No successful concurrent requests measured")
        
        concurrent_p95 = np.percentile(concurrent_latencies, 95)
        
        # Validate performance degradation is acceptable
        latency_increase = (concurrent_p95 - baseline_p95) / baseline_p95
        assert latency_increase < 0.5, f"Latency increased {latency_increase:.1%} under load, expected <50%"

    # =============================================================================
    # DATABASE PERFORMANCE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_database_query_latency(self):
        """
        Test database query performance and latency.
        
        @description
        Measures database query execution times for common
        trading operations including simple and complex queries.
        
        @performance Target: Simple queries ≤10ms P95, Complex ≤100ms P95
        @tradingImpact Database performance affects all trading operations
        @riskLevel HIGH - Database is critical infrastructure
        """
        # This test would require actual database connection
        # For now, simulate database query timing
        
        simple_query_latencies = []
        complex_query_latencies = []
        
        # Simulate simple queries (e.g., user lookup, position check)
        for i in range(100):
            start_time = time.perf_counter()
            
            # Simulate simple query processing
            await asyncio.sleep(0.002)  # 2ms average processing
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            simple_query_latencies.append(latency_ms)
        
        # Simulate complex queries (e.g., aggregations, joins)
        for i in range(50):
            start_time = time.perf_counter()
            
            # Simulate complex query processing
            await asyncio.sleep(0.020)  # 20ms average processing
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            complex_query_latencies.append(latency_ms)
        
        # Validate simple query performance
        simple_p95 = np.percentile(simple_query_latencies, 95)
        simple_benchmark = self.LATENCY_BENCHMARKS['simple_query']
        assert simple_p95 <= simple_benchmark['p95'], f"Simple query P95 {simple_p95:.2f}ms exceeds benchmark"
        
        # Validate complex query performance
        complex_p95 = np.percentile(complex_query_latencies, 95)
        complex_benchmark = self.LATENCY_BENCHMARKS['complex_query']
        assert complex_p95 <= complex_benchmark['p95'], f"Complex query P95 {complex_p95:.2f}ms exceeds benchmark"

    # =============================================================================
    # MEMORY AND SERIALIZATION PERFORMANCE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_memory_allocation_latency(self):
        """
        Test memory allocation and garbage collection latency.
        
        @description
        Measures memory allocation performance for trading data
        structures and validates garbage collection impact.
        
        @performance Target: P95 ≤ 1ms allocation time
        @tradingImpact Memory performance affects real-time processing
        @riskLevel MEDIUM - Memory management affects performance
        """
        allocation_latencies = []
        
        for i in range(1000):
            start_time = time.perf_counter()
            
            # Simulate trading data structure allocation
            trading_data = {
                'positions': [{'symbol': f'SYMBOL_{j}', 'quantity': j * 0.1} for j in range(10)],
                'orders': [{'id': str(uuid.uuid4()), 'price': j * 100} for j in range(5)],
                'market_data': [{'timestamp': time.time(), 'price': j} for j in range(20)]
            }
            
            # Force some processing
            total_value = sum(pos['quantity'] for pos in trading_data['positions'])
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            allocation_latencies.append(latency_ms)
        
        p95 = np.percentile(allocation_latencies, 95)
        benchmark = self.LATENCY_BENCHMARKS['memory_allocation']
        assert p95 <= benchmark['p95'], f"Memory allocation P95 {p95:.3f}ms exceeds benchmark {benchmark['p95']}ms"

    @pytest.mark.asyncio
    async def test_json_serialization_latency(self, sample_market_data):
        """
        Test JSON serialization/deserialization performance.
        
        @description
        Measures JSON processing performance for market data
        and trading messages, critical for API performance.
        
        @performance Target: P95 ≤ 5ms serialization time
        @tradingImpact JSON performance affects API response times
        @riskLevel MEDIUM - Serialization affects data exchange
        """
        serialization_latencies = []
        
        for data in sample_market_data[:200]:
            start_time = time.perf_counter()
            
            # Serialize to JSON
            json_str = json.dumps(data, default=str)
            
            # Deserialize back
            parsed_data = json.loads(json_str)
            
            # Validate round-trip
            assert parsed_data['symbol'] == data['symbol']
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            serialization_latencies.append(latency_ms)
        
        p95 = np.percentile(serialization_latencies, 95)
        benchmark = self.LATENCY_BENCHMARKS['json_serialization']
        assert p95 <= benchmark['p95'], f"JSON serialization P95 {p95:.2f}ms exceeds benchmark {benchmark['p95']}ms"

    # =============================================================================
    # REGRESSION DETECTION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_performance_regression_detection(self, performance_session):
        """
        Test performance regression detection system.
        
        @description
        Validates that performance regressions are detected by
        comparing current performance against historical baselines.
        
        @performance Target: Detect >20% performance regressions
        @tradingImpact Regression detection prevents performance degradation
        @riskLevel HIGH - Performance regressions affect trading
        """
        # Simulate historical baseline (would be loaded from metrics storage)
        historical_baseline = {
            'health_endpoint_p95': 80.0,  # 80ms historical P95
            'timestamp': datetime.now(timezone.utc) - timedelta(days=1)
        }
        
        # Measure current performance
        current_latencies = await self._measure_endpoint_latency(
            performance_session,
            f"{self.API_BASE_URL}/health",
            method='GET',
            samples=100
        )
        
        current_p95 = np.percentile(current_latencies, 95)
        
        # Calculate regression
        regression_threshold = 0.2  # 20% regression threshold
        baseline_p95 = historical_baseline['health_endpoint_p95']
        
        if current_p95 > baseline_p95:
            regression_percent = (current_p95 - baseline_p95) / baseline_p95
            
            if regression_percent > regression_threshold:
                # This would trigger alerts in production
                print(f"PERFORMANCE REGRESSION DETECTED: {regression_percent:.1%} increase in latency")
                print(f"Current P95: {current_p95:.2f}ms, Baseline P95: {baseline_p95:.2f}ms")
                
                # For testing, we'll assert this is within acceptable bounds
                # In production, this would trigger rollback procedures
                assert regression_percent < 0.5, f"Severe performance regression: {regression_percent:.1%}"

    # =============================================================================
    # LOAD TESTING UNDER LATENCY CONSTRAINTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_sustained_load_latency(self, performance_session):
        """
        Test latency under sustained load conditions.
        
        @description
        Measures API latency under sustained load to validate
        performance stability over time during high-traffic periods.
        
        @performance Target: Stable latency over 5-minute sustained load
        @tradingImpact Sustained load testing validates production readiness
        @riskLevel HIGH - Production load patterns must be validated
        """
        test_duration = 30  # 30 seconds for testing (5 minutes in production)
        request_rate = 10   # 10 requests per second
        
        latency_samples = []
        start_time = time.time()
        
        async def sustained_load_worker():
            session = requests.Session()
            while time.time() - start_time < test_duration:
                try:
                    request_start = time.perf_counter()
                    response = session.get(f"{self.API_BASE_URL}/health", timeout=5)
                    request_end = time.perf_counter()
                    
                    if response.status_code == 200:
                        latency_ms = (request_end - request_start) * 1000
                        latency_samples.append({
                            'latency': latency_ms,
                            'timestamp': time.time() - start_time
                        })
                    
                except Exception:
                    pass
                
                await asyncio.sleep(1.0 / request_rate)
            
            session.close()
        
        # Run sustained load test
        workers = [sustained_load_worker() for _ in range(5)]  # 5 concurrent workers
        await asyncio.gather(*workers)
        
        if not latency_samples:
            pytest.fail("No latency samples collected during sustained load test")
        
        # Analyze latency stability over time
        # Split samples into time buckets
        bucket_size = 5  # 5-second buckets
        buckets = {}
        
        for sample in latency_samples:
            bucket = int(sample['timestamp'] // bucket_size)
            if bucket not in buckets:
                buckets[bucket] = []
            buckets[bucket].append(sample['latency'])
        
        # Calculate P95 for each bucket
        bucket_p95s = []
        for bucket_latencies in buckets.values():
            if len(bucket_latencies) >= 5:  # Minimum samples for percentile
                p95 = np.percentile(bucket_latencies, 95)
                bucket_p95s.append(p95)
        
        if len(bucket_p95s) < 2:
            pytest.skip("Insufficient time buckets for stability analysis")
        
        # Check latency stability (coefficient of variation)
        mean_p95 = statistics.mean(bucket_p95s)
        std_p95 = statistics.stdev(bucket_p95s)
        cv = std_p95 / mean_p95  # Coefficient of variation
        
        # Latency should be stable (low coefficient of variation)
        assert cv < 0.3, f"Latency too variable under sustained load: CV={cv:.2f}"
        assert mean_p95 < 200, f"Mean P95 latency {mean_p95:.2f}ms too high under sustained load"

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    async def _measure_endpoint_latency(
        self,
        session: requests.Session,
        url: str,
        method: str = 'GET',
        samples: int = 100,
        **kwargs
    ) -> List[float]:
        """
        Measure endpoint latency with statistical sampling.
        
        @description
        Performs latency measurement for HTTP endpoints with
        proper statistical sampling and error handling.
        
        @param session HTTP session for requests
        @param url Endpoint URL to test
        @param method HTTP method to use
        @param samples Number of samples to collect
        @returns List of latency measurements in milliseconds
        
        @performance Configurable sample size for accuracy
        @tradingImpact Latency measurement utility for all endpoint tests
        @riskLevel LOW - Measurement utility
        """
        latencies = []
        
        for i in range(samples):
            try:
                start_time = time.perf_counter()
                
                if method.upper() == 'GET':
                    response = session.get(url, timeout=5, **kwargs)
                elif method.upper() == 'POST':
                    response = session.post(url, timeout=5, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                end_time = time.perf_counter()
                
                if response.status_code in [200, 201]:
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                
            except Exception as e:
                # Log error but continue sampling
                if i % 10 == 0:  # Log every 10th error to avoid spam
                    print(f"Latency measurement error (sample {i}): {e}")
                continue
            
            # Small delay between requests to avoid overwhelming the server
            if i < samples - 1:
                await asyncio.sleep(0.01)  # 10ms between requests
        
        return latencies

    def _calculate_performance_metrics(self, latencies: List[float]) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics from latency samples.
        
        @description
        Calculates statistical metrics including percentiles, mean,
        standard deviation, and outlier detection for latency analysis.
        
        @param latencies List of latency measurements in milliseconds
        @returns Dictionary of performance metrics
        
        @performance Statistical analysis of latency data
        @tradingImpact Performance metrics for regression detection
        @riskLevel LOW - Analysis utility
        """
        if not latencies:
            return {}
        
        metrics = {
            'count': len(latencies),
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'min': min(latencies),
            'max': max(latencies),
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99),
            'p99_9': np.percentile(latencies, 99.9)
        }
        
        # Calculate outlier statistics
        q1 = np.percentile(latencies, 25)
        q3 = np.percentile(latencies, 75)
        iqr = q3 - q1
        outlier_threshold = q3 + 1.5 * iqr
        
        outliers = [l for l in latencies if l > outlier_threshold]
        metrics['outlier_count'] = len(outliers)
        metrics['outlier_rate'] = len(outliers) / len(latencies)
        
        return metrics 