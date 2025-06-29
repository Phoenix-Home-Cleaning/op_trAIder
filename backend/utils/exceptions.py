#!/usr/bin/env python3
"""
@fileoverview Custom exception classes for TRAIDER V1
@module backend.utils.exceptions

@description
Institutional-grade exception handling with typed errors, severity levels,
and recovery strategies. Provides comprehensive error classification for
trading operations, system failures, and business logic errors.

@performance
- Minimal overhead exception creation
- Structured error information
- Recovery guidance included

@risk
- Failure impact: LOW - Error handling infrastructure
- Recovery strategy: Graceful degradation with fallback errors
- Critical for proper error reporting and debugging

@compliance
- Audit requirements: All errors logged with context
- Data retention: Error logs kept for 90 days

@see {@link docs/architecture/error-handling.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

from typing import Optional, Dict, Any
from enum import Enum

# =============================================================================
# ERROR SEVERITY LEVELS
# =============================================================================

class ErrorSeverity(Enum):
    """
    Error severity classification for institutional-grade error handling.
    
    @description
    Defines severity levels for errors to enable appropriate response,
    alerting, and recovery procedures.
    """
    
    LOW = "LOW"           # Minor issues, system continues normally
    MEDIUM = "MEDIUM"     # Moderate issues, some functionality affected
    HIGH = "HIGH"         # Major issues, significant functionality impacted
    CRITICAL = "CRITICAL" # Critical issues, system or trading at risk

# =============================================================================
# BASE EXCEPTION CLASSES
# =============================================================================

class TradingError(Exception):
    """
    Base exception class for all trading-related errors.
    
    @description
    Provides structured error information including severity, recovery
    strategies, and contextual information for institutional-grade
    error handling and debugging.
    
    @attributes
    - code: Error code for programmatic handling
    - message: Human-readable error message
    - severity: Error severity level
    - recovery: Recovery strategy description
    - context: Additional error context
    
    @tradingImpact CRITICAL - Proper error handling prevents financial loss
    @riskLevel HIGH - Error handling affects system reliability
    """
    
    def __init__(
        self,
        message: str,
        code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery: str = "Contact system administrator",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize trading error.
        
        @param message Human-readable error message
        @param code Unique error code for programmatic handling
        @param severity Error severity level
        @param recovery Recovery strategy description
        @param context Additional error context
        """
        
        super().__init__(message)
        self.message = message
        self.code = code
        self.severity = severity.value if isinstance(severity, ErrorSeverity) else severity
        self.recovery = recovery
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary for JSON serialization.
        
        @returns Dictionary representation of the error
        """
        
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "severity": self.severity,
            "recovery": self.recovery,
            "context": self.context,
        }
    
    def __str__(self) -> str:
        """String representation of the error."""
        return f"[{self.code}] {self.message} (Severity: {self.severity})"

# =============================================================================
# SYSTEM ERRORS
# =============================================================================

class DatabaseError(TradingError):
    """
    Database-related errors.
    
    @description
    Handles database connectivity, query, and transaction errors
    with appropriate recovery strategies.
    """
    
    def __init__(self, message: str, operation: str = "unknown", 
                 recovery: str = "Retry operation or check database connectivity"):
        super().__init__(
            message=message,
            code="DB_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery=recovery,
            context={"operation": operation}
        )

class ConnectionError(TradingError):
    """
    Network and connection-related errors.
    
    @description
    Handles external service connectivity issues including
    exchange APIs, market data feeds, and internal services.
    """
    
    def __init__(self, message: str, service: str, 
                 recovery: str = "Check network connectivity and retry"):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery=recovery,
            context={"service": service}
        )

class ConfigurationError(TradingError):
    """
    Configuration and setup errors.
    
    @description
    Handles invalid configuration, missing environment variables,
    and system setup issues.
    """
    
    def __init__(self, message: str, parameter: str = "unknown",
                 recovery: str = "Check configuration and environment variables"):
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            severity=ErrorSeverity.CRITICAL,
            recovery=recovery,
            context={"parameter": parameter}
        )

# =============================================================================
# AUTHENTICATION & AUTHORIZATION ERRORS
# =============================================================================

class AuthenticationError(TradingError):
    """
    Authentication-related errors.
    
    @description
    Handles login failures, token validation, and credential issues.
    """
    
    def __init__(self, message: str, user_id: Optional[str] = None,
                 recovery: str = "Verify credentials and try again"):
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"user_id": user_id}
        )

class AuthorizationError(TradingError):
    """
    Authorization and permission errors.
    
    @description
    Handles insufficient permissions and access control violations.
    """
    
    def __init__(self, message: str, resource: str, action: str,
                 recovery: str = "Contact administrator for access permissions"):
        super().__init__(
            message=message,
            code="AUTHZ_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"resource": resource, "action": action}
        )

# =============================================================================
# MARKET DATA ERRORS
# =============================================================================

class MarketDataError(TradingError):
    """
    Market data-related errors.
    
    @description
    Handles market data feed issues, data quality problems,
    and real-time data connectivity.
    """
    
    def __init__(self, message: str, symbol: Optional[str] = None, 
                 source: Optional[str] = None,
                 recovery: str = "Check market data feed connectivity"):
        super().__init__(
            message=message,
            code="MARKET_DATA_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery=recovery,
            context={"symbol": symbol, "source": source}
        )

class DataQualityError(TradingError):
    """
    Data quality and validation errors.
    
    @description
    Handles invalid data, missing data points, and data integrity issues.
    """
    
    def __init__(self, message: str, data_type: str, validation_rule: str,
                 recovery: str = "Review data quality checks and data source"):
        super().__init__(
            message=message,
            code="DATA_QUALITY_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"data_type": data_type, "validation_rule": validation_rule}
        )

# =============================================================================
# TRADING OPERATION ERRORS
# =============================================================================

class OrderError(TradingError):
    """
    Order-related errors.
    
    @description
    Handles order placement, modification, and cancellation errors.
    """
    
    def __init__(self, message: str, order_id: Optional[str] = None, 
                 symbol: Optional[str] = None,
                 recovery: str = "Review order parameters and account status"):
        super().__init__(
            message=message,
            code="ORDER_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery=recovery,
            context={"order_id": order_id, "symbol": symbol}
        )

class RiskManagementError(TradingError):
    """
    Risk management and compliance errors.
    
    @description
    Handles risk limit violations, position size errors,
    and compliance rule violations.
    """
    
    def __init__(self, message: str, rule: str, current_value: Optional[float] = None,
                 limit_value: Optional[float] = None,
                 recovery: str = "Review risk parameters and position sizes"):
        super().__init__(
            message=message,
            code="RISK_ERROR",
            severity=ErrorSeverity.CRITICAL,
            recovery=recovery,
            context={
                "rule": rule,
                "current_value": current_value,
                "limit_value": limit_value
            }
        )

class PositionError(TradingError):
    """
    Position management errors.
    
    @description
    Handles position tracking, P&L calculation, and portfolio errors.
    """
    
    def __init__(self, message: str, symbol: Optional[str] = None,
                 position_id: Optional[str] = None,
                 recovery: str = "Review position data and calculations"):
        super().__init__(
            message=message,
            code="POSITION_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery=recovery,
            context={"symbol": symbol, "position_id": position_id}
        )

# =============================================================================
# STRATEGY & MODEL ERRORS
# =============================================================================

class StrategyError(TradingError):
    """
    Trading strategy errors.
    
    @description
    Handles strategy execution, signal generation, and model errors.
    """
    
    def __init__(self, message: str, strategy_name: str, 
                 recovery: str = "Review strategy parameters and market conditions"):
        super().__init__(
            message=message,
            code="STRATEGY_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"strategy_name": strategy_name}
        )

class ModelError(TradingError):
    """
    Machine learning model errors.
    
    @description
    Handles model prediction, training, and deployment errors.
    """
    
    def __init__(self, message: str, model_name: str, model_version: Optional[str] = None,
                 recovery: str = "Check model status and retrain if necessary"):
        super().__init__(
            message=message,
            code="MODEL_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"model_name": model_name, "model_version": model_version}
        )

# =============================================================================
# EXTERNAL SERVICE ERRORS
# =============================================================================

class ExchangeError(TradingError):
    """
    Exchange API errors.
    
    @description
    Handles exchange-specific errors, API rate limits, and service issues.
    """
    
    def __init__(self, message: str, exchange: str, api_error_code: Optional[str] = None,
                 recovery: str = "Check exchange status and API credentials"):
        super().__init__(
            message=message,
            code="EXCHANGE_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery=recovery,
            context={"exchange": exchange, "api_error_code": api_error_code}
        )

class RateLimitError(TradingError):
    """
    API rate limit errors.
    
    @description
    Handles API rate limiting and throttling from external services.
    """
    
    def __init__(self, message: str, service: str, retry_after: Optional[int] = None,
                 recovery: str = "Wait for rate limit reset and retry"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"service": service, "retry_after": retry_after}
        )

# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class ValidationError(TradingError):
    """
    Input validation errors.
    
    @description
    Handles invalid input parameters, data format errors,
    and business rule violations.
    """
    
    def __init__(self, message: str, field: str, value: Any = None,
                 recovery: str = "Correct the invalid input and try again"):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            recovery=recovery,
            context={"field": field, "value": str(value) if value is not None else None}
        )

class BusinessRuleError(TradingError):
    """
    Business rule violation errors.
    
    @description
    Handles violations of business logic rules and constraints.
    """
    
    def __init__(self, message: str, rule: str,
                 recovery: str = "Review business rules and input parameters"):
        super().__init__(
            message=message,
            code="BUSINESS_RULE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery=recovery,
            context={"rule": rule}
        )

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_error_response(error: TradingError) -> Dict[str, Any]:
    """
    Create standardized error response for API endpoints.
    
    @param error TradingError instance
    @returns Standardized error response dictionary
    
    @performance <1ms response creation
    @sideEffects None
    
    @tradingImpact LOW - Error response formatting
    @riskLevel LOW - Response formatting only
    """
    
    return {
        "success": False,
        "error": error.to_dict(),
        "timestamp": __import__('time').time(),
    }

def handle_exception(exc: Exception, context: Optional[Dict[str, Any]] = None) -> TradingError:
    """
    Convert generic exceptions to TradingError instances.
    
    @param exc Generic exception to convert
    @param context Additional context information
    @returns TradingError instance with appropriate classification
    
    @performance <1ms conversion
    @sideEffects None
    
    @tradingImpact MEDIUM - Error classification affects handling
    @riskLevel LOW - Error conversion only
    """
    
    if isinstance(exc, TradingError):
        return exc
    
    # Map common exceptions to appropriate TradingError types
    if isinstance(exc, ConnectionError):
        return ConnectionError(str(exc), "unknown")
    elif isinstance(exc, ValueError):
        return ValidationError(str(exc), "unknown")
    elif isinstance(exc, PermissionError):
        return AuthorizationError(str(exc), "unknown", "unknown")
    else:
        # Generic error for unknown exceptions
        return TradingError(
            message=str(exc),
            code="UNKNOWN_ERROR",
            severity=ErrorSeverity.MEDIUM,
            recovery="Contact system administrator",
            context=context or {"exception_type": type(exc).__name__}
        ) 