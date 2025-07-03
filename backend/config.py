"""
@fileoverview Centralized configuration management for TRAIDER V1 backend
@module backend.config

@description
Provides a single source of truth for environment configuration using
Pydantic's BaseSettings. Ensures mandatory secrets are validated at import
and exposes a `settings` object for application modules.

@performance
- Load time: <10 ms
- Memory: <50 KB

@risk
- Failure impact: CRITICAL – Application will not start without required
  secrets in production.
- Recovery strategy: Fail-fast with clear error messages.

@compliance
- Audit requirements: Configuration access logged via calling modules
- Data retention: None (secrets kept in memory only)

@see {@link docs/security/environment-variables.md}
@since 1.0.0-alpha
"""

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, ValidationError
except ImportError:  # Fallback for pydantic v1.x
    from pydantic import BaseSettings, Field, ValidationError
from typing import Any
import os
import sys


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Security / authentication
    secret_key: str = Field(..., env="SECRET_KEY")
    dashboard_password: str = Field(..., env="DASHBOARD_PASSWORD")
    guest_password: str = Field("", env="GUEST_PASSWORD")

    # JWT configuration
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


try:
    settings = Settings()
except ValidationError as exc:
    # Provide a concise error for missing configuration. In production we want
    # to fail fast, while during tests we may fallback to defaults.
    missing = ", ".join(
        err["loc"][0] for err in exc.errors() if err["type"] == "value_error.missing"
    )
    message = (
        "Configuration validation error: missing required environment variables: "
        f"{missing}"
    )
    # Printing to stderr gives clearer output in container logs/CI.
    print(message, file=sys.stderr)
    # Re-raise as RuntimeError to avoid Pydantic's large traceback noise.
    raise RuntimeError(message) from exc 