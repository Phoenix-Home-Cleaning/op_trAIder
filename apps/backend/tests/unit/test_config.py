"""
@fileoverview Unit Tests for Backend Configuration
@module tests.unit.test_config

@description
This file contains unit tests for the centralized configuration management
in `backend/config.py`. It verifies that settings are correctly loaded from
environment variables, default values are applied appropriately, and that the
application fails fast with a clear error message if required secrets are
missing.

These tests use mocking to simulate different environment conditions to ensure
the configuration system is robust and reliable.
"""

import pytest
import os
import importlib
from unittest.mock import patch

# The module to be tested
import backend.config

class TestConfig:
    """
    Test suite for backend configuration settings.
    """

    def test_load_defaults_successfully(self):
        """
        Verify that default values are loaded when environment variables are not set.
        """
        # These are required
        test_env = {
            "SECRET_KEY": "test-secret",
            "DASHBOARD_PASSWORD": "test-password"
        }
        with patch.dict(os.environ, test_env, clear=True):
            # Reload the module to re-trigger the settings load
            importlib.reload(backend.config)
            settings = backend.config.settings

            assert settings.guest_password == ""
            assert settings.algorithm == "HS256"
            assert settings.access_token_expire_minutes == 60

    def test_override_defaults_with_env_vars(self):
        """
        Verify that environment variables correctly override default settings.
        """
        test_env = {
            "SECRET_KEY": "a-different-secret",
            "DASHBOARD_PASSWORD": "a-different-password",
            "GUEST_PASSWORD": "a-guest-password",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "120"
        }
        with patch.dict(os.environ, test_env, clear=True):
            importlib.reload(backend.config)
            settings = backend.config.settings

            assert settings.secret_key == "a-different-secret"
            assert settings.dashboard_password == "a-different-password"
            assert settings.guest_password == "a-guest-password"
            assert settings.algorithm == "HS256" # Should not be overridden
            assert settings.access_token_expire_minutes == 120

    def test_missing_required_secret_key_raises_error(self):
        """
        Verify that a RuntimeError is raised if the SECRET_KEY is missing.
        """
        # Environment is missing SECRET_KEY
        test_env = {
            "DASHBOARD_PASSWORD": "test-password"
        }
        with patch.dict(os.environ, test_env, clear=True):
            with pytest.raises(RuntimeError) as excinfo:
                importlib.reload(backend.config)
            
            assert "missing required environment variables: secret_key" in str(excinfo.value)

    def test_missing_required_dashboard_password_raises_error(self):
        """
        Verify that a RuntimeError is raised if the DASHBOARD_PASSWORD is missing.
        """
        # Environment is missing DASHBOARD_PASSWORD
        test_env = {
            "SECRET_KEY": "test-secret"
        }
        with patch.dict(os.environ, test_env, clear=True):
            with pytest.raises(RuntimeError) as excinfo:
                importlib.reload(backend.config)

            assert "missing required environment variables: dashboard_password" in str(excinfo.value)
    
    def test_algorithm_is_not_overridden_by_env(self):
        """
        Verify that the 'algorithm' setting is hardcoded and not overridden by env.
        Pydantic BaseSettings only considers fields defined with `Field` or type annotations
        for environment variable mapping.
        """
        test_env = {
            "SECRET_KEY": "test-secret",
            "DASHBOARD_PASSWORD": "test-password",
            "ALGORITHM": "FAKE_ALGO_SHOULD_BE_IGNORED"
        }
        with patch.dict(os.environ, test_env, clear=True):
            importlib.reload(backend.config)
            settings = backend.config.settings
            assert settings.algorithm == "HS256"

# Restore original environment after tests run
@pytest.fixture(scope="module", autouse=True)
def restore_environment():
    """Fixture to ensure the config is reset after this test module runs."""
    yield
    importlib.reload(backend.config) 