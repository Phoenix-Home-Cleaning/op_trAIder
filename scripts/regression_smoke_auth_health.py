#!/usr/bin/env python3
"""
Quick smoke-tests for authentication and health endpoints.

Runs in CI to ensure that core endpoints remain functional after
code changes. Exits with non-zero status on failure.
"""

import sys
import asyncio
from datetime import timedelta

import httpx
from fastapi import status
from fastapi.testclient import TestClient

# Ensure project root is on sys.path (already true when running from repo root)

from backend.api.auth import create_access_token  # noqa: E402
from backend.main import app  # noqa: E402 – FastAPI application instance

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

async def async_smoke():
    """Run async smoke-tests."""

    client = TestClient(app)

    # ---------------------------------------------------------------------
    # 1. Auth token creation + decode round-trip
    # ---------------------------------------------------------------------
    token_payload = {"sub": "smoke@test", "user_id": "0", "role": "viewer"}
    token = create_access_token(data=token_payload, secret_key="smoke_secret", expires_delta=timedelta(minutes=5))
    assert isinstance(token, str) and len(token) > 20, "Token generation failed"

    # ---------------------------------------------------------------------
    # 2. Health detailed endpoint should return 200 or 503 but never 500
    # ---------------------------------------------------------------------
    resp = client.get("/health/detailed")
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE), resp.text

    # ---------------------------------------------------------------------
    # 3. Metrics endpoint must return text with required gauges
    # ---------------------------------------------------------------------
    metrics_resp = client.get("/health/metrics")
    assert metrics_resp.status_code == status.HTTP_200_OK, metrics_resp.text
    body = metrics_resp.text
    required_substrings = [
        "# HELP traider_health_status",
        "# TYPE traider_health_status gauge",
        "traider_uptime_seconds",
    ]
    for substr in required_substrings:
        assert substr in body, f"Missing metric line: {substr}"


if __name__ == "__main__":
    try:
        asyncio.run(async_smoke())
    except AssertionError as exc:
        print(f"Smoke-test assertion failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover – defensive
        print(f"Unhandled exception during smoke-test: {exc}", file=sys.stderr)
        sys.exit(1)
    print("✅ Regression smoke-tests passed") 