"""
@fileoverview Pytest Configuration for TRAIDER V1 Test Suite
@module tests.conftest

@description
Global pytest configuration that sets up environment variables, Python paths,
and test fixtures for both frontend and backend testing. Ensures proper
isolation and institutional-grade test reliability.

@performance
- Environment setup: <100ms
- Fixture initialization: <50ms per fixture
- Memory usage: <5MB overhead

@risk
- Failure impact: CRITICAL (blocks all testing)
- Recovery strategy: Fallback to default configuration

@compliance
- Audit requirements: Yes
- Test environment isolation: Required

@see {@link docs/testing/testing-strategy.md}
@since 1.0.0
@author TRAIDER Team
"""

import os
import sys
from pathlib import Path
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE any imports
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add backend directory to Python path for imports
backend_path = project_root / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Set test environment variables if not already set
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "test_secret_key_for_unit_testing_only_not_production_use"

if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/traider_test"

if not os.getenv("TEST_SECRET_KEY"):
    os.environ["TEST_SECRET_KEY"] = "test_secret_key_for_unit_testing_only"

# Ensure test mode
os.environ["TESTING"] = "true"
os.environ["PYTHON_ENV"] = "testing"


@pytest.fixture(scope="session")
def test_environment():
    """
    Session-scoped fixture to validate test environment setup
    
    @description Ensures all required environment variables and paths are configured
    @performance O(1) validation, <10ms execution
    @riskLevel LOW - Environment validation only
    """
    required_vars = ["SECRET_KEY", "DATABASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.fail(f"Missing required environment variables: {missing_vars}")
    
    return {
        "project_root": project_root,
        "backend_path": backend_path,
        "environment": "testing"
    }


@pytest.fixture(scope="function")
def mock_environment():
    """
    Function-scoped fixture for environment variable mocking
    
    @description Provides isolated environment for tests that need custom env vars
    @performance O(1) setup/teardown, <5ms per test
    @riskLevel LOW - Test isolation only
    """
    original_env = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="session")
def trading_test_config():
    """
    Trading-specific test configuration
    
    @description Provides safe test configuration for trading logic tests
    @performance O(1) configuration, <5ms setup
    @riskLevel MEDIUM - Must ensure test isolation from production
    """
    return {
        "max_position_size": 100.0,  # Small test position
        "daily_loss_limit": 10.0,    # Small test limit
        "emergency_stop_enabled": True,
        "sandbox_mode": True,
        "test_mode": True
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers for TRAIDER test suite"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "trading: marks tests as trading logic tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )


# Set asyncio mode for async tests
def pytest_configure(config):
    """Configure asyncio mode for async test execution"""
    config.option.asyncio_mode = "auto" 