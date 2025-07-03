#!/usr/bin/env python3
"""
@fileoverview Health check endpoints for TRAIDER V1
@module backend.api.health

@description
Comprehensive health check endpoints for monitoring system status,
database connectivity, external service health, and performance metrics.
Essential for institutional-grade monitoring and alerting.

@performance
- Health checks complete in <100ms
- Minimal resource usage
- Cached results for frequent checks

@risk
- Failure impact: LOW - Monitoring only
- Recovery strategy: N/A - Read-only operations
- No trading impact

@compliance
- Audit requirements: Health status logged
- Data retention: 30 days for health logs

@see {@link docs/monitoring/health-checks.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import asyncio
import os
import platform
import psutil
import time
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from database import check_database_health
from utils.logging import get_logger

# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter()
logger = get_logger(__name__)

# =============================================================================
# SYSTEM INFORMATION
# =============================================================================

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information for health monitoring.
    
    @description
    Collects system metrics including CPU, memory, disk usage,
    and platform information for monitoring dashboards.
    
    @returns Dict with system metrics and platform information
    
    @performance <10ms execution time
    @sideEffects Reads system metrics
    
    @tradingImpact None - Monitoring only
    @riskLevel LOW - Read-only system calls
    """
    
    try:
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Network information (basic)
        network_io = psutil.net_io_counters()
        
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            },
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None,
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 1),
            },
            "network": {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
            } if network_io else None,
        }
        
    except Exception as exc:
        logger.warning(f"Failed to get system info: {exc}")
        return {"error": "System information unavailable"}

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
            "uptime_seconds": time.time() - psutil.Process().create_time(),
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
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "Service not responding",
                "timestamp": time.time(),
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
        "service": {
            "name": "TRAIDER V1 API",
            "version": "1.0.0-alpha",
            "environment": os.getenv("PYTHON_ENV", "development"),
            "uptime_seconds": round(time.time() - psutil.Process().create_time(), 2),
        },
        "system": system_info,
        "dependencies": {
            "database": db_health,
        },
        "warnings": warnings,
    }

    status_code = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(status_code=status_code, content=response_data)

@router.get("/metrics", summary="Prometheus Metrics")
async def prometheus_metrics() -> str:
    """
    Prometheus-compatible metrics endpoint.
    
    @description
    Exposes system and application metrics in Prometheus format
    for monitoring and alerting infrastructure.
    
    @returns Plain text Prometheus metrics
    
    @performance <50ms response time
    @sideEffects System metrics collection
    
    @tradingImpact LOW - Monitoring infrastructure
    @riskLevel LOW - Metrics collection only
    """
    
    metrics = []

    # ============================= HELP / TYPE LINES =============================
    def _add_metric(name: str, value: float | int, help_text: str, metric_type: str = "gauge"):
        metrics.append(f"# HELP {name} {help_text}")
        metrics.append(f"# TYPE {name} {metric_type}")
        metrics.append(f"{name} {value}")

    # Safe collection blocks ------------------------------------------------------
    system_ok = True
    db_ok = True
    db_health: Dict[str, Any] = {}

    try:
        system_info = get_system_info()
    except Exception as exc:  # pragma: no cover – safeguarded
        system_ok = False
        system_info = {}
        logger.error(f"System metrics collection failed: {exc}")

    try:
        db_health = await check_database_health()
    except Exception as exc:  # pragma: no cover – safeguarded
        db_ok = False
        db_health = {"status": "unhealthy", "error": str(exc), "response_time_ms": 0}
        logger.error(f"Database metrics collection failed: {exc}")

    service_healthy = system_ok and db_ok and db_health.get("status") == "healthy"

    # Overall health gauges -------------------------------------------------------
    _add_metric("traider_health_status", 1 if service_healthy else 0, "Overall health status (1=healthy,0=unhealthy)")
    _add_metric("traider_system_error", 0 if system_ok else 1, "System metrics collection error (1=error)")

    # System metrics --------------------------------------------------------------
    if system_ok and system_info:
        cpu = system_info.get("cpu", {})
        _add_metric("traider_cpu_usage_percent", cpu.get("usage_percent", 0), "CPU utilisation percentage")
        _add_metric("traider_cpu_count", cpu.get("count", 0), "Logical CPU cores", "gauge")

        mem = system_info.get("memory", {})
        _add_metric("traider_memory_usage_percent", mem.get("usage_percent", 0), "Memory utilisation percentage")

        disk = system_info.get("disk", {})
        _add_metric("traider_disk_usage_percent", disk.get("usage_percent", 0), "Disk utilisation percentage")

    # Database metrics ------------------------------------------------------------
    _add_metric("traider_database_up", 1 if db_health.get("status") == "healthy" else 0, "Database up status (1=up,0=down)")
    _add_metric("traider_database_response_time_ms", db_health.get("response_time_ms", 0), "Database health check latency (ms)")

    # Service uptime --------------------------------------------------------------
    uptime_seconds = time.time() - psutil.Process().create_time()
    _add_metric("traider_uptime_seconds", round(uptime_seconds, 2), "Service uptime in seconds")

    return "\n".join(metrics) + "\n" 