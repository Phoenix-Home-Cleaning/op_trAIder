#!/usr/bin/env python3
"""
@fileoverview Pytest configuration for backend tests
@module backend.conftest

@description
Pytest configuration and fixtures for backend testing infrastructure.
Sets up proper Python path, database connections, and shared test utilities.

@performance
- Fast test database setup
- Efficient fixture sharing
- Minimal test isolation overhead

@risk
- Failure impact: MEDIUM - Test infrastructure unavailable
- Recovery strategy: Reset test environment

@compliance
- Audit requirements: Test execution logging
- Data retention: Test logs kept for 30 days

@see {@link docs/testing/backend-testing.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Add root directory to Python path  
root_dir = backend_dir.parent
sys.path.insert(0, str(root_dir))

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, Generator
from fastapi.testclient import TestClient

from backend.main import app

# Configure Hypothesis for CI environment
try:
    from hypothesis import settings, HealthCheck
    
    # Register CI profile with relaxed health checks
    settings.register_profile(
        "ci",
        database=None,
        deadline=None,
        print_blob=True,
        derandomize=True,
        suppress_health_check=(
            HealthCheck.too_slow,
            HealthCheck.filter_too_much,
            HealthCheck.data_too_large,
        ),
        max_examples=100,  # Reduced for CI speed
    )
    
    # Load CI profile by default
    settings.load_profile("ci")
    
except ImportError:
    # Hypothesis not available - tests will run without property-based testing
    pass

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Set comprehensive test environment variables before any imports
TEST_ENV = {
    # Core authentication
    "SECRET_KEY": "test_" + "secret_key_for_unit_testing_only",  # nosec: test configuration
    "DASHBOARD_PASSWORD": "test_dashboard_password",
    "GUEST_PASSWORD": "test_guest_password",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
    "BCRYPT_ROUNDS": "10",  # Fast bcrypt for CI (still secure)
    
    # Environment settings
    "PYTHON_ENV": "testing",
    "TESTING": "true",
    "NODE_ENV": "test",
    "DEBUG": "false",
    
    # Database settings
    "DATABASE_URL": "sqlite:///:memory:",
    "TEST_DATABASE_URL": "sqlite:///:memory:",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_DB": "test_db",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "TIMESCALEDB_ENABLED": "false",
    
    # API settings
    "API_HOST": "127.0.0.1",
    "API_PORT": "8000",
    "NEXTAUTH_URL": "http://localhost:3000",
    "NEXTAUTH_SECRET": "test_nextauth_secret",
    "NEXT_PUBLIC_API_URL": "http://localhost:8000",
    
    # Trading settings
    "COINBASE_API_KEY": "test_api_key",
    "COINBASE_PRIVATE_KEY": "test_private_key",
    "COINBASE_SANDBOX": "true",
    "MAX_POSITION_SIZE": "1000.00",
    "DAILY_LOSS_LIMIT": "100.00",
    "EMERGENCY_STOP_ENABLED": "true",
    
    # Infrastructure settings
    "REDIS_URL": "redis://localhost:6379",
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "json",
    "AUDIT_LOG_ENABLED": "true",
    "PROMETHEUS_PORT": "9090",
    "GRAFANA_PORT": "3001",
    
    # Security settings
    "CORS_ORIGINS": "http://localhost:3000",
    "CORS_CREDENTIALS": "true",
    "RATE_LIMIT_ENABLED": "false",  # Disabled for tests
    "SECURITY_SCAN_ENABLED": "false",  # Disabled for tests
    "VULNERABILITY_THRESHOLD": "medium",
    
    # Quality settings
    "COVERAGE_GLOBAL_THRESHOLD": "80",
    "COVERAGE_TRADING_THRESHOLD": "90",
    "COVERAGE_RISK_THRESHOLD": "100",
    "COVERAGE_ENFORCEMENT_ENABLED": "false",  # Disabled for tests
    "QUALITY_GATE_ENABLED": "false",  # Disabled for tests
    
    # Docker settings
    "COMPOSE_PROJECT_NAME": "traider_test",
    "DOCKER_REGISTRY": "localhost:5000",
    
    # Database connection settings
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "test_db",
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_password",
    "DB_POOL_SIZE": "5",
    "DB_MAX_OVERFLOW": "2",
    "DB_POOL_TIMEOUT": "10",
    
    # Logging settings
    "LOG_DIR": "logs",
    "AUDIT_LOG_RETENTION_DAYS": "30",
    
    # Compliance settings
    "COMPLIANCE_MODE": "testing",
    "DATA_ENCRYPTION_ENABLED": "false",  # Disabled for tests
    "ENCRYPTION_ALGORITHM": "AES-256-GCM",
    "KEY_ROTATION_INTERVAL_DAYS": "90",
    
    # External service tokens (test values)
    "SONAR_HOST_URL": "https://sonarcloud.io",
    "SONAR_TOKEN": "test_sonar_token",
    "SONARQUBE_DB_PASSWORD": "test_sonarqube_password",
    "SONARQUBE_PORT": "9000",
    "SONARQUBE_EXPORTER_PORT": "8080",
    "SEMGREP_APP_TOKEN": "test_semgrep_token",
    "SNYK_TOKEN": "test_snyk_token",
    "RENOVATE_TOKEN": "test_renovate_token",
    "RENOVATE_SCHEDULE": "disabled",
    "RENOVATE_AUTO_MERGE_ENABLED": "false",
}

# Apply test environment immediately
for key, value in TEST_ENV.items():
    os.environ[key] = value

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    TestClient fixture for making API requests.
    
    @description
    Provides a FastAPI TestClient instance for executing API integration tests.
    It is session-scoped for efficiency, so the client is created once per
    test session.
    
    @returns TestClient instance
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """
    Test configuration fixture.
    
    @description
    Provides test configuration settings for consistent test execution
    across all backend test modules.
    
    @returns Test configuration dictionary
    @performance <1ms configuration setup
    @riskLevel LOW - Test configuration
    """
    
    return {
        "database_url": "sqlite:///:memory:",
        "secret_key": "test_" + "secret_key_for_unit_testing_only",  # nosec: test configuration
        "jwt_algorithm": "HS256",
        "test_timeout": 30,
        "performance_threshold_ms": 100
    }


@pytest.fixture
def mock_user():
    """
    Mock user fixture for testing.
    
    @description
    Creates a mock user object with realistic data for testing
    authentication and authorization functionality.
    
    @returns Mock User object
    @performance <1ms user creation
    @riskLevel LOW - Test data generation
    """
    
    user = Mock()
    user.id = 1
    user.username = "test_trader"
    user.email = "test@traider.com"
    user.role = "trader"
    user.is_active = True
    user.permissions = ["trading", "portfolio_management"]
    user.to_dict.return_value = {
        "id": 1,
        "username": "test_trader",
        "email": "test@traider.com",
        "role": "trader",
        "is_active": True
    }
    
    return user


@pytest.fixture
def mock_admin_user():
    """
    Mock admin user fixture for testing.
    
    @description  
    Creates a mock admin user with full permissions for testing
    administrative functionality.
    
    @returns Mock admin User object
    @performance <1ms user creation
    @riskLevel LOW - Test data generation
    """
    
    user = Mock()
    user.id = 2
    user.username = "admin"
    user.email = "admin@traider.com"
    user.role = "admin"
    user.is_active = True
    user.permissions = ["admin", "trading", "portfolio_management", "user_management"]
    user.to_dict.return_value = {
        "id": 2,
        "username": "admin", 
        "email": "admin@traider.com",
        "role": "admin",
        "is_active": True
    }
    
    return user


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """
    Authentication headers fixture.
    
    @description
    Provides properly formatted authentication headers for API testing.
    
    @returns HTTP headers dictionary
    @performance <1ms header generation
    @riskLevel LOW - Test utilities
    """
    
    return {
        "Authorization": "Bearer test_jwt_token",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """
    Configure test settings for the entire test session.
    
    @description
    Sets up mock settings object to replace the real config.settings
    for all tests. This ensures consistent configuration across all
    test modules.
    
    @performance <1ms settings setup
    @riskLevel LOW - Test configuration
    """
    
    # Create mock settings object
    mock_settings = Mock()
    mock_settings.secret_key = "test_" + "secret_key_for_unit_testing_only"  # nosec: test configuration
    mock_settings.dashboard_password = "test_dashboard_password"
    mock_settings.guest_password = "test_guest_password"
    mock_settings.algorithm = "HS256"
    mock_settings.access_token_expire_minutes = 60
    
    # Patch the settings in both possible import locations
    with patch('backend.config.settings', mock_settings), \
         patch('config.settings', mock_settings):
        yield mock_settings 