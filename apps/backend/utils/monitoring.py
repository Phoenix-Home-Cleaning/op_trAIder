#!/usr/bin/env python3
"""
@fileoverview Monitoring and metrics collection for TRAIDER V1
@module backend.utils.monitoring

@description
Comprehensive monitoring and metrics collection system for institutional-grade
observability. Provides performance tracking, alerting, and operational metrics
for trading system monitoring and optimization.

@performance
- Low-overhead metrics collection (<1ms per metric)
- Async background processing
- Efficient memory usage with metric aggregation

@risk
- Failure impact: LOW - Monitoring only, no trading impact
- Recovery strategy: Graceful degradation without metrics
- Fallback to basic logging if metrics unavailable

@compliance
- Audit requirements: Performance metrics logged
- Data retention: 90 days for metrics, 30 days for alerts

@see {@link docs/monitoring/metrics-collection.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from threading import Lock
import statistics

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from prometheus_client.core import REGISTRY

from utils.logging import get_logger

# =============================================================================
# CONFIGURATION
# =============================================================================

logger = get_logger(__name__)

# Metrics configuration
METRICS_ENABLED = True
METRICS_COLLECTION_INTERVAL = 10  # seconds
HISTOGRAM_BUCKETS = [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class MetricPoint:
    """
    Individual metric data point.
    
    @description
    Represents a single metric measurement with timestamp and metadata
    for time-series analysis and alerting.
    """
    
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"

@dataclass
class PerformanceWindow:
    """
    Rolling window for performance metrics.
    
    @description
    Maintains a rolling window of performance measurements
    for calculating statistics and detecting anomalies.
    """
    
    values: deque = field(default_factory=lambda: deque(maxlen=1000))
    window_size: int = 1000
    
    def add(self, value: float) -> None:
        """Add value to the rolling window."""
        self.values.append(value)
    
    def get_stats(self) -> Dict[str, float]:
        """Get statistical summary of the window."""
        if not self.values:
            return {}
        
        values_list = list(self.values)
        return {
            "count": len(values_list),
            "min": min(values_list),
            "max": max(values_list),
            "mean": statistics.mean(values_list),
            "median": statistics.median(values_list),
            "p95": statistics.quantiles(values_list, n=20)[18] if len(values_list) >= 20 else max(values_list),
            "p99": statistics.quantiles(values_list, n=100)[98] if len(values_list) >= 100 else max(values_list),
        }

# =============================================================================
# METRICS COLLECTOR
# =============================================================================

class MetricsCollector:
    """
    Central metrics collection and management system.
    
    @description
    Collects, aggregates, and exposes metrics for monitoring systems.
    Provides Prometheus-compatible metrics and custom alerting.
    
    @performance
    - <1ms per metric recording
    - Background aggregation every 10 seconds
    - Memory-efficient rolling windows
    
    @tradingImpact MEDIUM - Performance monitoring affects optimization
    @riskLevel LOW - Monitoring only, graceful degradation
    """
    
    def __init__(self, service_name: str):
        """
        Initialize metrics collector.
        
        @param service_name Name of the service being monitored
        """
        
        self.service_name = service_name
        self.enabled = METRICS_ENABLED
        self._lock = Lock()
        self._background_task: Optional[asyncio.Task] = None
        
        # Metric storage
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._performance_windows: Dict[str, PerformanceWindow] = defaultdict(PerformanceWindow)
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        logger.info(f"Metrics collector initialized for {service_name}")
    
    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics collectors."""
        
        # Request metrics
        self.request_duration = Histogram(
            'traider_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint', 'status_code'],
            buckets=HISTOGRAM_BUCKETS
        )
        
        self.request_count = Counter(
            'traider_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status_code']
        )
        
        # Trading metrics
        self.trading_operations = Counter(
            'traider_trading_operations_total',
            'Total trading operations',
            ['operation_type', 'symbol', 'status']
        )
        
        self.trading_latency = Histogram(
            'traider_trading_latency_seconds',
            'Trading operation latency',
            ['operation_type', 'symbol'],
            buckets=HISTOGRAM_BUCKETS
        )
        
        # System metrics
        self.active_connections = Gauge(
            'traider_active_connections',
            'Number of active connections',
            ['connection_type']
        )
        
        self.error_count = Counter(
            'traider_errors_total',
            'Total number of errors',
            ['error_type', 'component']
        )
        
        # Performance metrics
        self.response_time_p95 = Gauge(
            'traider_response_time_p95_seconds',
            '95th percentile response time',
            ['endpoint']
        )
        
        self.memory_usage = Gauge(
            'traider_memory_usage_bytes',
            'Memory usage in bytes'
        )
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None,
                     metric_type: str = "gauge") -> None:
        """
        Record a custom metric.
        
        @description
        Records a metric point with timestamp and optional labels
        for custom monitoring and alerting.
        
        @param name Metric name
        @param value Metric value
        @param labels Optional metric labels
        @param metric_type Type of metric (gauge, counter, histogram)
        
        @performance <0.5ms per metric
        @sideEffects Stores metric in memory
        
        @tradingImpact LOW - Monitoring only
        @riskLevel LOW - Metric recording only
        """
        
        if not self.enabled:
            return
        
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            metric_type=metric_type
        )
        
        with self._lock:
            self._metrics[name].append(metric_point)
            
            # Limit metric history to prevent memory growth
            if len(self._metrics[name]) > 10000:
                self._metrics[name] = self._metrics[name][-5000:]
    
    def record_request_duration(self, method: str, endpoint: str, 
                               status_code: int, duration: float) -> None:
        """
        Record HTTP request duration and count.
        
        @description
        Records request metrics for API performance monitoring
        and SLA tracking.
        
        @param method HTTP method
        @param endpoint Request endpoint
        @param status_code HTTP status code
        @param duration Request duration in seconds
        
        @performance <0.5ms per request
        @sideEffects Updates Prometheus metrics
        
        @tradingImpact LOW - API monitoring
        @riskLevel LOW - Metrics only
        """
        
        if not self.enabled:
            return
        
        # Update Prometheus metrics
        self.request_duration.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).observe(duration)
        
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        # Update performance windows
        window_key = f"request_duration_{endpoint}"
        self._performance_windows[window_key].add(duration)
        
        # Log slow requests
        if duration > 1.0:  # Log requests slower than 1 second
            logger.warning(
                "Slow request detected",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "duration_seconds": duration,
                    "status_code": status_code,
                }
            )
    
    def record_trading_operation(self, operation_type: str, symbol: str, 
                                status: str, duration: Optional[float] = None) -> None:
        """
        Record trading operation metrics.
        
        @description
        Records trading-specific metrics for performance monitoring
        and trading system optimization.
        
        @param operation_type Type of trading operation
        @param symbol Trading symbol
        @param status Operation status (success/failure)
        @param duration Operation duration in seconds (optional)
        
        @performance <0.5ms per operation
        @sideEffects Updates trading metrics
        
        @tradingImpact MEDIUM - Trading performance monitoring
        @riskLevel LOW - Metrics only
        """
        
        if not self.enabled:
            return
        
        # Update operation count
        self.trading_operations.labels(
            operation_type=operation_type,
            symbol=symbol,
            status=status
        ).inc()
        
        # Update latency if provided
        if duration is not None:
            self.trading_latency.labels(
                operation_type=operation_type,
                symbol=symbol
            ).observe(duration)
            
            # Update performance window
            window_key = f"trading_latency_{operation_type}_{symbol}"
            self._performance_windows[window_key].add(duration)
        
        # Log trading operations
        logger.info(
            "Trading operation recorded",
            extra={
                "operation_type": operation_type,
                "symbol": symbol,
                "status": status,
                "duration_seconds": duration,
            }
        )
    
    def record_error(self, endpoint: str, error_type: str, component: str = "api") -> None:
        """
        Record error occurrence.
        
        @description
        Records error metrics for monitoring and alerting systems.
        
        @param endpoint Endpoint where error occurred
        @param error_type Type of error
        @param component Component where error occurred
        
        @performance <0.5ms per error
        @sideEffects Updates error metrics
        
        @tradingImpact MEDIUM - Error monitoring affects reliability
        @riskLevel LOW - Metrics only
        """
        
        if not self.enabled:
            return
        
        self.error_count.labels(
            error_type=error_type,
            component=component
        ).inc()
        
        logger.error(
            "Error recorded in metrics",
            extra={
                "endpoint": endpoint,
                "error_type": error_type,
                "component": component,
            }
        )
    
    def get_performance_stats(self, metric_name: str) -> Optional[Dict[str, float]]:
        """
        Get performance statistics for a metric.
        
        @description
        Returns statistical summary of performance metrics
        for monitoring dashboards and alerting.
        
        @param metric_name Name of the metric
        @returns Dictionary with performance statistics
        
        @performance <1ms per metric
        @sideEffects None
        
        @tradingImpact LOW - Monitoring query
        @riskLevel LOW - Read-only operation
        """
        
        window = self._performance_windows.get(metric_name)
        return window.get_stats() if window else None
    
    def get_prometheus_metrics(self) -> str:
        """
        Get Prometheus-formatted metrics.
        
        @description
        Returns all metrics in Prometheus exposition format
        for scraping by monitoring systems.
        
        @returns Prometheus-formatted metrics string
        
        @performance <10ms for all metrics
        @sideEffects None
        
        @tradingImpact LOW - Monitoring export
        @riskLevel LOW - Read-only operation
        """
        
        if not self.enabled:
            return ""
        
        return generate_latest(REGISTRY).decode('utf-8')
    
    def start_background_tasks(self) -> None:
        """
        Start background metric processing tasks.
        
        @description
        Starts background tasks for metric aggregation,
        cleanup, and performance monitoring.
        
        @performance Background processing
        @sideEffects Starts async tasks
        
        @tradingImpact LOW - Background monitoring
        @riskLevel LOW - Background tasks only
        """
        
        if not self.enabled:
            return
        
        if self._background_task is None or self._background_task.done():
            self._background_task = asyncio.create_task(self._background_processor())
            logger.info("Metrics background tasks started")
    
    def stop_background_tasks(self) -> None:
        """
        Stop background metric processing tasks.
        
        @description
        Gracefully stops background tasks during shutdown.
        
        @performance <1s shutdown time
        @sideEffects Cancels async tasks
        
        @tradingImpact LOW - Shutdown process
        @riskLevel LOW - Cleanup only
        """
        
        if self._background_task and not self._background_task.done():
            self._background_task.cancel()
            logger.info("Metrics background tasks stopped")
    
    async def _background_processor(self) -> None:
        """
        Background task for metric processing and cleanup.
        
        @description
        Processes metrics, calculates aggregations, and performs
        cleanup to prevent memory growth.
        """
        
        while True:
            try:
                await asyncio.sleep(METRICS_COLLECTION_INTERVAL)
                
                # Update performance gauges
                self._update_performance_gauges()
                
                # Cleanup old metrics
                self._cleanup_old_metrics()
                
                logger.debug("Metrics background processing completed")
                
            except asyncio.CancelledError:
                logger.info("Metrics background processor cancelled")
                break
            except Exception as exc:
                logger.error(f"Metrics background processor error: {exc}", exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying
    
    def _update_performance_gauges(self) -> None:
        """Update Prometheus gauges with performance statistics."""
        
        for metric_name, window in self._performance_windows.items():
            stats = window.get_stats()
            if stats and 'p95' in stats:
                # Extract endpoint from metric name
                if metric_name.startswith('request_duration_'):
                    endpoint = metric_name.replace('request_duration_', '')
                    self.response_time_p95.labels(endpoint=endpoint).set(stats['p95'])
    
    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics to prevent memory growth."""
        
        current_time = time.time()
        retention_period = 3600  # 1 hour
        
        with self._lock:
            for metric_name, points in self._metrics.items():
                # Keep only recent metrics
                self._metrics[metric_name] = [
                    point for point in points
                    if current_time - point.timestamp < retention_period
                ]

# =============================================================================
# ALERTING SYSTEM
# =============================================================================

class AlertManager:
    """
    Simple alerting system for metric thresholds.
    
    @description
    Monitors metrics and triggers alerts when thresholds are exceeded.
    Provides basic alerting functionality for operational monitoring.
    
    @tradingImpact MEDIUM - Alerts affect operational response
    @riskLevel LOW - Alerting only, no trading logic
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize alert manager."""
        
        self.metrics_collector = metrics_collector
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_history: deque = deque(maxlen=1000)
        
        logger.info("Alert manager initialized")
    
    def add_alert_rule(self, metric_name: str, threshold: float, 
                      comparison: str = "greater", severity: str = "warning") -> None:
        """
        Add an alert rule for metric monitoring.
        
        @param metric_name Name of metric to monitor
        @param threshold Alert threshold value
        @param comparison Comparison operator (greater, less, equal)
        @param severity Alert severity (info, warning, critical)
        """
        
        rule = {
            "metric_name": metric_name,
            "threshold": threshold,
            "comparison": comparison,
            "severity": severity,
            "last_triggered": None,
        }
        
        self.alert_rules.append(rule)
        logger.info(f"Alert rule added: {metric_name} {comparison} {threshold}")
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Check all alert rules and return triggered alerts.
        
        @returns List of triggered alerts
        """
        
        triggered_alerts = []
        
        for rule in self.alert_rules:
            stats = self.metrics_collector.get_performance_stats(rule["metric_name"])
            if not stats:
                continue
            
            # Use mean value for comparison
            current_value = stats.get("mean", 0)
            threshold = rule["threshold"]
            comparison = rule["comparison"]
            
            # Check threshold
            triggered = False
            if comparison == "greater" and current_value > threshold:
                triggered = True
            elif comparison == "less" and current_value < threshold:
                triggered = True
            elif comparison == "equal" and abs(current_value - threshold) < 0.001:
                triggered = True
            
            if triggered:
                alert = {
                    "metric_name": rule["metric_name"],
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": rule["severity"],
                    "timestamp": time.time(),
                }
                
                triggered_alerts.append(alert)
                self.alert_history.append(alert)
                rule["last_triggered"] = time.time()
                
                logger.warning(
                    f"Alert triggered: {rule['metric_name']}",
                    extra=alert
                )
        
        return triggered_alerts

# =============================================================================
# GLOBAL METRICS INSTANCE
# =============================================================================

# Global metrics collector instance
_global_metrics: Optional[MetricsCollector] = None

def get_metrics_collector() -> Optional[MetricsCollector]:
    """Get the global metrics collector instance."""
    return _global_metrics

def initialize_metrics(service_name: str) -> MetricsCollector:
    """Initialize the global metrics collector."""
    global _global_metrics
    _global_metrics = MetricsCollector(service_name)
    return _global_metrics 