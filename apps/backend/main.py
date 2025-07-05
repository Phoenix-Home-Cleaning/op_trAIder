#!/usr/bin/env python3
"""
@fileoverview FastAPI main application for TRAIDER V1
@module backend.main

@description
Main FastAPI application entry point for institutional-grade autonomous trading platform.
Includes health checks, CORS configuration, middleware setup, and API routing
with comprehensive error handling and structured logging.

@performance
- Async/await patterns throughout
- Connection pooling for database
- Request/response compression
- Rate limiting middleware

@risk
- Failure impact: CRITICAL - Core API unavailable
- Recovery strategy: Auto-restart with health checks
- Circuit breaker for external dependencies

@compliance
- Audit requirements: All requests logged
- Data retention: 90 days for logs, 7 years for trades

@see {@link docs/architecture/backend-api.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware

# Import custom modules
from backend.api.health import router as health_router
from backend.api.auth import router as auth_router
from database import get_database_connection, close_database_connection
from utils.logging import setup_logging, get_logger
from utils.monitoring import MetricsCollector
from utils.exceptions import TradingError
from backend.config import settings

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Environment configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("PYTHON_ENV", "development")
API_VERSION = "1.0.0-alpha"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Security configuration
security = HTTPBearer(auto_error=False)

# -----------------------------------------------------------------------------
# Fail-fast configuration validation (production only)
# -----------------------------------------------------------------------------

if ENVIRONMENT.lower() == "production":
    # Validate that critical secrets are present.
    missing_vars = []
    if not settings.secret_key:
        missing_vars.append("SECRET_KEY")
    if not settings.dashboard_password:
        missing_vars.append("DASHBOARD_PASSWORD")

    if missing_vars:
        logger.critical(
            "🔥 Critical configuration missing – application shutting down", extra={"missing": missing_vars}
        )
        # Exit immediately to prevent insecure startup
        raise SystemExit(1)

# =============================================================================
# LOGGING & MONITORING SETUP
# =============================================================================

# Initialize structured logging
setup_logging(level=logging.INFO if not DEBUG else logging.DEBUG)
logger = get_logger(__name__)

# Initialize metrics collection
metrics = MetricsCollector("traider_api")

# =============================================================================
# MIDDLEWARE CLASSES
# =============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging with performance metrics.
    
    @description
    Logs all API requests with timing, status codes, and error details.
    Essential for institutional-grade audit trails and performance monitoring.
    
    @performance O(1) overhead per request
    @sideEffects Writes to structured log files
    
    @tradingImpact Critical for debugging trading issues and compliance
    @riskLevel LOW - Logging only, no trading logic
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = id(request)
        
        # Log incoming request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Record metrics
            metrics.record_request_duration(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=process_time
            )
            
            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": round(process_time * 1000, 2),  # ms
                    "endpoint": request.url.path,
                }
            )
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            response.headers["X-Request-ID"] = str(request_id)
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "process_time": round(process_time * 1000, 2),
                },
                exc_info=True
            )
            
            # Record error metrics
            metrics.record_error(
                endpoint=request.url.path,
                error_type=type(exc).__name__
            )
            
            # Return structured error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": str(request_id),
                    "timestamp": time.time(),
                }
            )

# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown procedures.
    
    @description
    Handles database connections, external service initialization,
    and graceful shutdown procedures for institutional-grade reliability.
    
    @performance Startup: <5s, Shutdown: <10s
    @sideEffects Database connections, external API connections
    
    @tradingImpact Critical - System unavailable during startup/shutdown
    @riskLevel HIGH - Must handle gracefully to prevent data loss
    """
    
    # Startup procedures
    logger.info("🚀 TRAIDER API starting up...")
    
    try:
        # Initialize database connection
        await get_database_connection()
        logger.info("✅ Database connection established")
        
        # Initialize metrics collection
        metrics.start_background_tasks()
        logger.info("✅ Metrics collection started")
        
        # System ready
        logger.info(f"🎯 TRAIDER API v{API_VERSION} ready for trading operations")
        
        yield  # Application runs here
        
    except Exception as exc:
        logger.error(f"❌ Startup failed: {exc}", exc_info=True)
        raise
    
    finally:
        # Shutdown procedures
        logger.info("🛑 TRAIDER API shutting down...")
        
        try:
            # Close database connections
            await close_database_connection()
            logger.info("✅ Database connections closed")
            
            # Stop metrics collection
            metrics.stop_background_tasks()
            logger.info("✅ Metrics collection stopped")
            
            logger.info("✅ TRAIDER API shutdown complete")
            
        except Exception as exc:
            logger.error(f"❌ Shutdown error: {exc}", exc_info=True)

# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title="TRAIDER V1 API",
    description="Institutional-Grade Autonomous Cryptocurrency Trading Platform",
    version=API_VERSION,
    docs_url="/docs" if DEBUG else None,  # Disable in production
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
    lifespan=lifespan,
)

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Request logging middleware (first)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(TradingError)
async def trading_error_handler(request: Request, exc: TradingError):
    """
    Handle trading-specific errors with appropriate logging and response.
    
    @param exc TradingError with severity and recovery information
    @returns JSONResponse with error details and recovery guidance
    
    @tradingImpact HIGH - Trading errors must be handled gracefully
    @riskLevel CRITICAL - Improper handling could cause financial loss
    """
    
    logger.error(
        f"Trading error: {exc.message}",
        extra={
            "error_code": exc.code,
            "severity": exc.severity,
            "recovery": exc.recovery,
            "endpoint": request.url.path,
        }
    )
    
    # Determine HTTP status code based on severity
    status_code = 500 if exc.severity == "CRITICAL" else 400
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Trading operation failed",
            "code": exc.code,
            "message": exc.message,
            "severity": exc.severity,
            "recovery": exc.recovery,
            "timestamp": time.time(),
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions with structured logging."""
    
    logger.warning(
        f"HTTP error: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "endpoint": request.url.path,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": exc.detail,   # compatibility for test expectations
            "status_code": exc.status_code,
            "timestamp": time.time(),
        }
    )

# =============================================================================
# API ROUTES
# =============================================================================

# ---------------------------------------------------------------------------
# API ROUTING
# ---------------------------------------------------------------------------
# In Phase-0 we exposed health endpoints at the root ("/health") path to speed
# up early-stage smoke testing.  The integration test-suite – as well as our
# documented public API contract – now expects all first-class routes to be
# nested under the versioned base path "/api/v1".  To maintain backwards
# compatibility while satisfying the contract we:
#   1. Mount versioned routes at "/api/v1/*" (new canonical path).
#   2. Keep legacy mounts without the version prefix behind the same routers so
#      that existing monitoring dashboards and external tests continue to work
#      until they are migrated.  These legacy mounts are explicitly **NOT**
#      documented and will be removed in the next major version.
# ---------------------------------------------------------------------------

# Health check routes
app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health Check"]
)

# Authentication routes
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# ---------------------------------------------------------------------------
# Legacy mounts (to be deprecated)
# ---------------------------------------------------------------------------
# WARNING: These mounts exist solely for backwards compatibility with Phase-0
# scripts.  Do **not** rely on them for new integrations – use the `/api/v1/*`
# paths instead.

app.include_router(health_router, prefix="/health", tags=["Health Check (Legacy)"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication (Legacy)"])

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing basic API status.

    The integration test-suite expects two fields:
    1. `message` – human-readable welcome string.
    2. `version` – semantic version of the running API.

    Additional metadata is still returned for operational dashboards.
    """

    return {
        "message": "Welcome to TRAIDER V1 API",
        "version": API_VERSION,
        # extended metadata (kept for dashboards / backwards compat)
        "status": "operational",
        "environment": ENVIRONMENT,
        "documentation": "/docs" if DEBUG else "Contact administrator",
        "timestamp": time.time(),
    }

# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    """
    Development server entry point.
    
    @description
    Runs the FastAPI application using Uvicorn with development settings.
    Not for production use - use proper ASGI server in production.
    """
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info",
        access_log=True,
    ) 