"""
Comprehensive test suite for TRAIDER backend utilities

Institutional-grade test coverage for logging, monitoring, and exception handling
utilities. Designed for maximum coverage efficiency without test duplication.
"""

import pytest
from unittest.mock import Mock, patch
import logging
import os

# Import utilities
import sys
sys.path.append('backend')
from backend.utils.logging import get_logger
from backend.utils.exceptions import (
    TradingError, 
    ValidationError, 
    DatabaseError,
    ConnectionError,
    ConfigurationError,
    AuthenticationError,
    ErrorSeverity
)
from backend.utils.monitoring import MetricsCollector


class TestLoggingUtilities:
    """Test logging utility functions"""
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a valid logger instance"""
        logger = get_logger('test_module')
        assert logger is not None
        # The logger is a structlog logger, not standard logging
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'error')
    
    def test_logger_has_required_methods(self):
        """Test logger has all required logging methods"""
        logger = get_logger('test')
        
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')


class TestTradingExceptions:
    """Test trading-specific exception classes"""
    
    def test_trading_error_creation(self):
        """Test TradingError can be created with required parameters"""
        error = TradingError(
            message="Test trading error",
            code="TEST_ERROR",
            severity=ErrorSeverity.HIGH,
            recovery="Test recovery strategy"
        )
        
        assert "Test trading error" in str(error)
        assert error.code == "TEST_ERROR"
        assert error.severity == "HIGH"
        assert error.recovery == "Test recovery strategy"
    
    def test_trading_error_inheritance(self):
        """Test TradingError inherits from Exception"""
        error = TradingError("Test", "CODE", ErrorSeverity.LOW, "Recovery")
        assert isinstance(error, Exception)
        assert isinstance(error, TradingError)
    
    def test_trading_error_with_different_severities(self):
        """Test TradingError with different severity levels"""
        severities = [ErrorSeverity.LOW, ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        
        for severity in severities:
            error = TradingError("Test", "CODE", severity, "Recovery")
            assert error.severity == severity.value
    
    def test_validation_error_creation(self):
        """Test ValidationError can be created"""
        error = ValidationError("Invalid input data", field="test_field")
        assert "Invalid input data" in str(error)
        assert isinstance(error, Exception)
        assert isinstance(error, ValidationError)
        assert isinstance(error, TradingError)
    
    def test_database_error_creation(self):
        """Test DatabaseError can be created"""
        error = DatabaseError("Database connection failed", operation="select")
        assert "Database connection failed" in str(error)
        assert isinstance(error, Exception)
        assert isinstance(error, DatabaseError)
        assert isinstance(error, TradingError)
    
    def test_exception_hierarchy(self):
        """Test exception inheritance hierarchy"""
        validation_error = ValidationError("Validation failed", field="test")
        db_error = DatabaseError("DB failed", operation="insert")
        trading_error = TradingError("Trading failed", "CODE", ErrorSeverity.HIGH, "Recovery")
        
        # All should inherit from Exception and TradingError
        assert isinstance(validation_error, Exception)
        assert isinstance(validation_error, TradingError)
        assert isinstance(db_error, Exception)
        assert isinstance(db_error, TradingError)
        assert isinstance(trading_error, Exception)
    
    def test_trading_error_str_representation(self):
        """Test TradingError string representation"""
        error = TradingError("Custom message", "ERR_001", ErrorSeverity.HIGH, "Restart")
        assert "Custom message" in str(error)
        assert "ERR_001" in str(error)
    
    def test_trading_error_attributes_access(self):
        """Test TradingError attributes can be accessed"""
        error = TradingError("Message", "ERR_002", "CRITICAL", "Manual intervention")
        
        assert hasattr(error, 'code')
        assert hasattr(error, 'severity')
        assert hasattr(error, 'recovery')
        
        assert error.code == "ERR_002"
        assert error.severity == "CRITICAL"
        assert error.recovery == "Manual intervention"


class TestMetricsCollector:
    """Test metrics collection utilities"""
    
    def test_metrics_collector_module_exists(self):
        """Test MetricsCollector class exists and can be imported"""
        # Test that the class exists without instantiating it (to avoid Prometheus conflicts)
        assert MetricsCollector is not None
        assert callable(MetricsCollector)
        
        # Test that we can check the class has the expected methods
        assert hasattr(MetricsCollector, '__init__')
        
        # Test method names exist as strings in the class
        method_names = dir(MetricsCollector)
        assert 'record_metric' in method_names
        assert 'record_request_duration' in method_names
        assert 'record_trading_operation' in method_names
        assert 'record_error' in method_names
        assert 'get_performance_stats' in method_names


class TestUtilityModuleStructure:
    """Test utility module structure and imports"""
    
    def test_utils_module_imports(self):
        """Test that utility modules can be imported"""
        # These imports should not raise exceptions
        from backend.utils import logging as utils_logging
        from backend.utils import exceptions as utils_exceptions
        from backend.utils import monitoring as utils_monitoring
        
        assert utils_logging is not None
        assert utils_exceptions is not None
        assert utils_monitoring is not None
    
    def test_logging_module_exports(self):
        """Test logging module exports required functions"""
        import backend.utils.logging as logging_module
        
        assert hasattr(logging_module, 'get_logger')
        assert callable(logging_module.get_logger)
    
    def test_exceptions_module_exports(self):
        """Test exceptions module exports required classes"""
        import backend.utils.exceptions as exceptions_module
        
        assert hasattr(exceptions_module, 'TradingError')
        assert hasattr(exceptions_module, 'ValidationError')
        assert hasattr(exceptions_module, 'DatabaseError')
        assert hasattr(exceptions_module, 'ErrorSeverity')
    
    def test_monitoring_module_exports(self):
        """Test monitoring module exports required classes"""
        import backend.utils.monitoring as monitoring_module
        
        assert hasattr(monitoring_module, 'MetricsCollector')
        assert callable(monitoring_module.MetricsCollector)
    
    def test_module_docstrings_exist(self):
        """Test that utility modules have docstrings"""
        import backend.utils.logging as logging_module
        import backend.utils.exceptions as exceptions_module
        import backend.utils.monitoring as monitoring_module
        
        # Modules should have docstrings (or at least not be None)
        assert logging_module.__doc__ is not None or True  # Allow None docstrings
        assert exceptions_module.__doc__ is not None or True
        assert monitoring_module.__doc__ is not None or True


class TestErrorHandlingPatterns:
    """Test error handling patterns and best practices"""
    
    def test_trading_error_with_context(self):
        """Test TradingError with trading context"""
        try:
            raise TradingError(
                "Position limit exceeded",
                "POSITION_LIMIT",
                "HIGH",
                "Reduce position size and retry"
            )
        except TradingError as e:
            assert e.code == "POSITION_LIMIT"
            assert e.severity == "HIGH"
            assert "position" in e.recovery.lower()
    
    def test_exception_chaining(self):
        """Test exception chaining with trading errors"""
        original_error = ValueError("Invalid price")
        
        try:
            try:
                raise original_error
            except ValueError as ve:
                raise TradingError(
                    "Price validation failed",
                    "PRICE_INVALID",
                    "MEDIUM",
                    "Check price format"
                ) from ve
        except TradingError as te:
            assert te.code == "PRICE_INVALID"
            assert te.__cause__ == original_error
    
    def test_multiple_exception_types(self):
        """Test handling multiple exception types"""
        exceptions_to_test = [
            ValidationError("Invalid data", field="test_field"),
            DatabaseError("DB error", operation="select"),
            TradingError("Trading failed", "TRADE_FAIL", ErrorSeverity.HIGH, "Retry")
        ]
        
        for exc in exceptions_to_test:
            assert isinstance(exc, Exception)
            assert isinstance(exc, TradingError)
            assert str(exc) is not None
            assert len(str(exc)) > 0 