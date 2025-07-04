"""
@fileoverview Unit Tests for Pytest Fixtures
@module tests.unit.test_conftest

@description
This file contains unit tests for the shared pytest fixtures defined in
`backend/conftest.py`. It verifies that each fixture provides the correct
data, mocks, or clients, ensuring a stable and predictable testing foundation
for all other test suites.

Testing fixtures is a best practice that prevents hard-to-debug errors in
other tests that consume these shared resources.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any
from jose import jwt

# All fixtures are automatically available from backend/conftest.py

def test_test_config_fixture(test_config: Dict[str, Any]):
    """
    Verify the 'test_config' fixture provides the correct configuration dictionary.
    
    @riskLevel LOW
    """
    assert isinstance(test_config, dict)
    assert "database_url" in test_config
    assert "secret_key" in test_config
    assert "jwt_algorithm" in test_config
    assert test_config["database_url"] == "sqlite:///:memory:"

def test_mock_user_fixture(mock_user: Mock):
    """
    Verify the 'mock_user' fixture provides a correctly configured user mock.
    
    @riskLevel LOW
    """
    assert isinstance(mock_user, Mock)
    assert mock_user.role == "trader"
    assert mock_user.is_active is True
    assert "trading" in mock_user.permissions
    assert mock_user.to_dict()["role"] == "trader"

def test_mock_admin_user_fixture(mock_admin_user: Mock):
    """
    Verify the 'mock_admin_user' fixture provides a correctly configured admin mock.
    
    @riskLevel LOW
    """
    assert isinstance(mock_admin_user, Mock)
    assert mock_admin_user.role == "admin"
    assert mock_admin_user.is_active is True
    assert "system_management" in mock_admin_user.permissions
    assert mock_admin_user.to_dict()["role"] == "admin"

def test_auth_headers_fixture(auth_headers: Dict[str, str], test_config: Dict[str, Any]):
    """
    Verify the 'auth_headers' fixture provides a valid JWT authentication header.
    
    @riskLevel MEDIUM - This fixture is critical for testing protected endpoints.
    """
    assert isinstance(auth_headers, dict)
    assert "Authorization" in auth_headers
    
    auth_string = auth_headers["Authorization"]
    assert auth_string.startswith("Bearer ")
    
    token = auth_string.split(" ")[1]
    
    # Verify the token can be decoded
    payload = jwt.decode(
        token, 
        test_config["secret_key"], 
        algorithms=[test_config["jwt_algorithm"]]
    )
    
    # Verify the payload contains expected claims from the mock_user fixture
    assert "sub" in payload
    assert payload["sub"] == "test@traider.com"
    assert payload["role"] == "trader" 