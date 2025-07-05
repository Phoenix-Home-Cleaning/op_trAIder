#!/usr/bin/env python3
"""
@fileoverview Health check endpoints for TRAIDER V1
@module backend.api.health

@description
Comprehensive health monitoring system with Kubernetes probes, system metrics,
and dependency health checks. Provides operational visibility for the
institutional trading platform.

@performance
- Basic health check: <1ms
- Liveness probe: <5ms
- Readiness probe: <100ms (includes DB check)
- Detailed health check: <200ms

@risk
- Failure impact: LOW - Monitoring only
- Recovery strategy: Graceful degradation

@compliance
- Audit requirements: Health check logs retained
- Data retention: 30 days for troubleshooting

@see {@link docs/infrastructure/monitoring.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import os
import time
import psutil
import platform as platform  # Expose module for unit-test patching
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse, PlainTextResponse

from utils.logging import get_logger

# =============================================================================
# CONFIGURATION
# =============================================================================

router = APIRouter()
logger = get_logger(__name__)

# Cache process start time for performance optimization
_START_TIME = psutil.Process().create_time()

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information and metrics.
    
    @returns System metrics dictionary
    
    @performance <50ms system info collection
    @sideEffects System metrics collection
    
    @tradingImpact LOW - Monitoring data collection
    @riskLevel LOW - Read-only system access
    """
    
    try:
        # CPU information
        cpu_info = {
            "count": psutil.cpu_count(),
            "usage_percent": psutil.cpu_percent(interval=0.1),
            "load_avg": list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0.0, 0.0, 0.0]
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "usage_percent": memory.percent
        }
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "usage_percent": round((disk.used / disk.total) * 100, 2)
        }
        
        # Network information (basic)
        network = psutil.net_io_counters()
        network_info = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        return {
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "python_version": platform.python_version(),
            },
            "timestamp": time.time(),
        }
        
    except Exception as exc:
        logger.warning(f"Failed to get system info: {exc}")
        return {"error": "System information unavailable"}

async def check_database_health() -> Dict[str, Any]:
    """
    Check database connectivity and health.
    
    @returns Database health status
    
    @performance <50ms database health check
    @sideEffects Database connectivity test
    
    @tradingImpact LOW - Health monitoring only
    @riskLevel LOW - Read-only database check
    """
    
    try:
        # Import here to avoid circular dependencies
        from database import get_raw_connection
        
        start_time = time.time()
        
        # Test database connection
        async with get_raw_connection() as conn:
            # Simple health check query
            result = await conn.fetchval("SELECT 1")
            
            if result != 1:
                return {
                    "status": "unhealthy",
                    "error": "Database query returned unexpected result",
                    "last_check": time.time()
                }
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "last_check": time.time(),
            "connection_pool": {
                "active": 2,  # Mock values for Phase 0
                "idle": 8,
                "total": 10
            }
        }
        
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}", exc_info=True)
        return {
            "status": "unhealthy", 
            "error": str(exc),
            "last_check": time.time()
        }

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@router.get("/", summary="Basic Health Check")
async def health_check() -> JSONResponse:
    """
    Basic health check endpoint for load balancers and uptime monitoring.
    
    @description
    Lightweight health check that returns 200 OK if the service is running.
    Used by load balancers, Kubernetes probes, and uptime monitoring.
    
    @returns JSONResponse with basic status and timestamp
    
    @example
    ```bash
    curl http://localhost:8000/health
    # Returns: {"status": "healthy", "timestamp": 1640995200.123}
    ```
    
    @performance <1ms response time
    @sideEffects None
    
    @tradingImpact None - Basic monitoring only
    @riskLevel LOW - No external dependencies
    """
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": "TRAIDER V1 API",
            "version": "1.0.0-alpha",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - _START_TIME,
        }
    )

@router.get("/live", summary="Liveness Probe")
async def liveness_probe() -> JSONResponse:
    """
    Kubernetes liveness probe endpoint.
    
    @description
    Indicates whether the application is running and should be restarted
    if unhealthy. Used by Kubernetes for container lifecycle management.
    
    @returns JSONResponse with liveness status
    
    @performance <1ms response time
    @sideEffects None
    
    @tradingImpact None - Container management only
    @riskLevel LOW - Basic service check
    """
    
    try:
        # Basic application health check
        current_time = time.time()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "alive",
                "timestamp": current_time,
                "service": "TRAIDER V1 API",
            }
        )
        
    except Exception as exc:
        logger.error(f"Liveness probe failed: {exc}", exc_info=True)
        
        # Use datetime.now() to avoid patched time.time() in tests
        fallback_time = datetime.now().timestamp()
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "Service not responding",
                "timestamp": fallback_time,
            }
        )

@router.get("/ready", summary="Readiness Probe")
async def readiness_probe() -> JSONResponse:
    """
    Kubernetes readiness probe endpoint.
    
    @description
    Indicates whether the application is ready to receive traffic.
    Checks database connectivity and essential services.
    
    @returns JSONResponse with readiness status and dependency checks
    
    @performance <100ms response time (includes DB check)
    @sideEffects Database connectivity test
    
    @tradingImpact LOW - Affects traffic routing
    @riskLevel LOW - Read-only dependency checks
    """
    
    try:
        start_time = time.time()
        
        # Check database connectivity
        db_health = await check_database_health()
        
        # Determine overall readiness
        is_ready = db_health.get("status") in ["healthy", "degraded"]
        
        response_data = {
            "status": "ready" if is_ready else "not_ready",
            "timestamp": time.time(),
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "dependencies": {
                "database": db_health,
            },
            "service": "TRAIDER V1 API",
        }
        
        # Add compatibility aliases for test contracts
        response_data["checks"] = response_data["dependencies"]
        
        status_code = (
            status.HTTP_200_OK if is_ready 
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
        
    except Exception as exc:
        logger.error(f"Readiness probe failed: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "error": str(exc),
                "timestamp": time.time(),
            }
        )

@router.get("/detailed", summary="Detailed Health Check")
async def detailed_health_check() -> JSONResponse:
    """
    Comprehensive health check with system metrics and dependency status.
    
    @description
    Detailed health information including system resources, database status,
    performance metrics, and service dependencies. Used for monitoring
    dashboards and operational visibility.
    
    @returns JSONResponse with comprehensive health and performance data
    
    @performance <200ms response time
    @sideEffects System metrics collection, database queries
    
    @tradingImpact LOW - Monitoring and alerting only
    @riskLevel LOW - Read-only operations
    """
    
    start_time = time.time()
    
    # Collect system information (non-fatal if it fails)
    try:
        system_info = get_system_info()
        system_ok = True
    except Exception as exc:  # pragma: no cover – safeguarded
        logger.error(f"System info collection failed: {exc}", exc_info=True)
        system_info = {"error": str(exc)}
        system_ok = False

    # Check database health (non-fatal if it fails)
    try:
        db_health = await check_database_health()
        db_ok = db_health.get("status") == "healthy"
    except Exception as exc:  # pragma: no cover – safeguarded
        logger.error(f"Database health check failed: {exc}", exc_info=True)
        db_health = {"status": "unhealthy", "error": str(exc)}
        db_ok = False

    # Determine overall status
    overall_status = "healthy" if system_ok and db_ok else "degraded"

    # Resource threshold warnings (only when system metrics available)
    warnings = []
    if system_ok and isinstance(system_info, dict):
        if system_info.get("cpu", {}).get("usage_percent", 0) > 80:
            warnings.append("High CPU usage")
        if system_info.get("memory", {}).get("usage_percent", 0) > 85:
            warnings.append("High memory usage")
        if system_info.get("disk", {}).get("usage_percent", 0) > 90:
            warnings.append("High disk usage")

    response_data = {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": round((time.time() - start_time) * 1000, 2),
        "service_info": {
            "name": "TRAIDER V1 API",
            "version": "1.0.0-alpha",
            "environment": os.getenv("PYTHON_ENV", "development"),
            "uptime_seconds": round(time.time() - _START_TIME, 2),
        },
        "system": system_info,
        "dependencies": {
            "database": db_health,
        },
        "warnings": warnings,
    }

    # Add compatibility aliases for test contracts
    response_data["service"] = "TRAIDER V1 API"  # Flat string for compatibility
    response_data["database"] = db_health  # Top-level database key

    # Ensure both old and new schema keys exist for monitoring dashboards
    if "service_info" not in response_data:
        response_data["service_info"] = {
            "name": "TRAIDER V1 API",
            "version": "1.0.0-alpha",
        }

    status_code = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(status_code=status_code, content=response_data)

@router.get("/metrics", summary="Prometheus Metrics")
async def prometheus_metrics() -> PlainTextResponse:
    """
    Prometheus-compatible metrics endpoint.
    
    @description
    Returns metrics in Prometheus format for monitoring and alerting.
    Includes system metrics, application metrics, and custom trading metrics.
    
    @returns Plain text metrics in Prometheus format
    
    @performance <100ms metrics collection
    @sideEffects System metrics collection
    
    @tradingImpact LOW - Monitoring data export
    @riskLevel LOW - Read-only metrics collection
    """
    
    try:
        metrics_lines = []
        
        def _add_metric(name: str, value: float | int, help_text: str, metric_type: str = "gauge"):
            """Helper to add a metric in Prometheus format."""
            metrics_lines.append(f"# HELP {name} {help_text}")
            metrics_lines.append(f"# TYPE {name} {metric_type}")
            metrics_lines.append(f"{name} {value}")
            metrics_lines.append("")
        
        system_error = 0
        overall_healthy = 1

        # System metrics
        try:
            system_info = get_system_info()
            if "error" not in system_info:
                # Primary TRAIDER-prefixed metrics
                _add_metric("traider_cpu_usage_percent", 
                          system_info["cpu"]["usage_percent"], 
                          "CPU usage percentage")
                _add_metric("traider_memory_usage_percent", 
                          system_info["memory"]["usage_percent"], 
                          "Memory usage percentage")
                _add_metric("traider_disk_usage_percent", 
                          system_info["disk"]["usage_percent"], 
                          "Disk usage percentage")

                # -----------------------------------------------------------------
                # Backwards-compatibility aliases – the integration test-suite
                # (and some existing Grafana dashboards) still expect generic
                # `system_*` and `process_*` metric names.  We publish both
                # names for one release cycle to avoid breaking consumers.
                # -----------------------------------------------------------------
                _add_metric("system_cpu_usage_percent", 
                          system_info["cpu"]["usage_percent"], 
                          "CPU usage percentage (alias)")
                _add_metric("system_memory_usage_percent", 
                          system_info["memory"]["usage_percent"], 
                          "Memory usage percentage (alias)")
                _add_metric("system_disk_usage_percent", 
                          system_info["disk"]["usage_percent"], 
                          "Disk usage percentage (alias)")
        except Exception as exc:
            logger.warning(f"Failed to collect system metrics: {exc}")
            system_error = 1
            overall_healthy = 0

        # Database metrics
        try:
            db_health = await check_database_health()
            db_status = 1 if db_health.get("status") == "healthy" else 0
            _add_metric("traider_database_healthy", db_status, "Database health status (1=healthy, 0=unhealthy)")
            
            if "response_time_ms" in db_health:
                _add_metric("traider_database_response_time_ms", 
                          db_health["response_time_ms"], 
                          "Database response time in milliseconds")
        except Exception as exc:
            logger.warning(f"Failed to collect database metrics: {exc}")
            system_error = 1
            overall_healthy = 0

        # Application metrics
        uptime_seconds = time.time() - _START_TIME
        _add_metric("traider_uptime_seconds", uptime_seconds, "Application uptime in seconds")

        # Compatibility alias for legacy dashboards/tests
        _add_metric("process_uptime_seconds", uptime_seconds, "Process uptime in seconds (alias)")

        _add_metric("traider_health_status", overall_healthy, "Overall health status (1=healthy, 0=unhealthy)")
        _add_metric("traider_system_error", system_error, "System error indicator (1=error present, 0=ok)")

        return PlainTextResponse("\n".join(metrics_lines), media_type="text/plain")
        
    except Exception as exc:
        logger.error(f"Metrics endpoint failed: {exc}", exc_info=True)
        return PlainTextResponse(f"# Error collecting metrics: {exc}\n", media_type="text/plain") 