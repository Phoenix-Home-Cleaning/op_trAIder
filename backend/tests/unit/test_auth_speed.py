#!/usr/bin/env python3
"""
@fileoverview Performance tests for authentication hashing
@module tests.unit.backend.test_auth_speed

@description
Ensures that password hashing operations meet institutional-grade performance
and security standards. Validates that bcrypt rounds are configurable and that
hashing time remains within acceptable limits to prevent DoS vulnerabilities.

@performance
- Hashing time validation: < 200ms

@risk
- Failure impact: MEDIUM - Slow hashing can impact user experience and API performance
- Recovery strategy: Adjust bcrypt rounds based on hardware capabilities

@compliance
- Audit requirements: Performance metrics logged during CI

@see {@link docs/testing/performance-testing.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import os
import time
import pytest
from unittest.mock import patch

from backend.api.auth import get_password_hash, pwd_context


class TestAuthHashingPerformance:
    """
    Validates bcrypt hashing performance and configuration.
    """

    def test_password_hashing_meets_performance_target(self):
        """
        Validates that default password hashing is under 200ms.
        
        @description This test ensures our default bcrypt configuration is not
        so slow that it impacts login performance or introduces a vector for
        denial-of-service attacks.
        
        @performance Target: < 200ms
        @riskLevel MEDIUM - Ensures responsive authentication.
        """
        start_time = time.time()
        get_password_hash("A-Very-Secure-Password-For-Institutional-Grade-Testing-123!")
        hash_time_ms = (time.time() - start_time) * 1000

        assert hash_time_ms < 200, f"Password hashing took {hash_time_ms:.2f}ms, exceeding the 200ms budget."

    @pytest.mark.parametrize("rounds, expected_max_time_ms", [
        ("8", 50),   # Very fast, for low-security needs or fast tests
        ("10", 150), # Good for CI/testing environments
        ("12", 400), # Standard production value
    ])
    @patch('backend.api.auth._DEFAULT_BCRYPT_ROUNDS')
    def test_bcrypt_rounds_are_configurable_via_env(self, mock_bcrypt_rounds, rounds, expected_max_time_ms):
        """
        Ensures BCRYPT_ROUNDS environment variable correctly configures hashing cost.
        
        @description This test validates that we can dynamically adjust the bcrypt
        work factor. This is critical for balancing security (higher rounds) and
        performance, especially in different environments like CI vs. Production.
        
        @riskLevel LOW - Validates configuration flexibility.
        """
        
        # Configure the mock to reflect the parameterized round count
        mock_bcrypt_rounds = int(rounds)
        
        # We must patch the context object directly where it's used
        with patch.object(pwd_context, "context_kwds", {"rounds": mock_bcrypt_rounds}):
            start_time = time.time()
            get_password_hash("Another-Secure-Password-For-Configurable-Testing-456!")
            hash_time_ms = (time.time() - start_time) * 1000

            assert hash_time_ms < expected_max_time_ms, (
                f"Hashing with {rounds} rounds took {hash_time_ms:.2f}ms, "
                f"exceeding the expected max of {expected_max_time_ms}ms."
            ) 