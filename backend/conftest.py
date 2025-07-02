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

# Import after path setup
from database import Base
from models import User, UserRole


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
        "secret_key": "test_secret_key_for_unit_testing_only",
        "jwt_algorithm": "HS256",
        "test_timeout": 30,
        "performance_threshold_ms": 100
    }


@pytest.fixture
def mock_user() -> User:
    """
    Mock user fixture for testing.
    
    @description
    Creates a mock user object with realistic data for testing
    authentication and authorization functionality.
    
    @returns Mock User object
    @performance <1ms user creation
    @riskLevel LOW - Test data generation
    """
    
    user = Mock(spec=User)
    user.id = 1
    user.username = "test_trader"
    user.email = "test@traider.com"
    user.role = UserRole.TRADER.value
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
def mock_admin_user() -> User:
    """
    Mock admin user fixture for testing.
    
    @description  
    Creates a mock admin user with full permissions for testing
    administrative functionality.
    
    @returns Mock admin User object
    @performance <1ms user creation
    @riskLevel LOW - Test data generation
    """
    
    user = Mock(spec=User)
    user.id = 2
    user.username = "admin"
    user.email = "admin@traider.com"
    user.role = UserRole.ADMIN.value
    user.is_active = True
    user.permissions = UserRole.get_permissions(UserRole.ADMIN.value)
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


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Automatic test environment setup.
    
    @description
    Sets up the test environment with proper environment variables
    and mocks for consistent test execution.
    
    @performance <5ms environment setup
    @riskLevel LOW - Test environment management
    """
    
    # Set test environment variables
    test_env = {
        "SECRET_KEY": "test_secret_key_for_unit_testing_only",
        "DASHBOARD_PASSWORD": "test_dashboard_password",
        "GUEST_PASSWORD": "test_guest_password",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        "TESTING": "true"
    }
    
    with patch.dict(os.environ, test_env):
        yield 