"""
Environment Configuration Module

This module manages environment variables and configuration settings for TheHive MCP server.
It provides centralized access to configuration parameters that can be set via environment
variables, allowing for flexible deployment across different environments.

Environment Variables:
    HIVE_URL: The base URL of TheHive instance (default: http://localhost:9000)
    HIVE_API_KEY: API key for authenticating with TheHive (default: "123")

The module uses sensible defaults for development while allowing production deployments
to override settings through environment variables.
"""

import os
from typing import Any

__all__ = ["get_hive_api_key", "get_hive_url"]

# No module-level assignments: values are provided dynamically by __getattr__


def get_hive_url() -> str:
    """Get TheHive URL from environment variable."""
    return str(os.getenv("HIVE_URL", "https://thehive.local:9000"))


def get_hive_api_key() -> str:
    """Get TheHive API key from environment variable."""
    return str(os.getenv("HIVE_API_KEY", ""))


def __getattr__(name: str) -> Any:
    """Dynamically resolve environment-backed settings at access time.

    This ensures tests that modify environment variables (or set them late)
    will always get current values without requiring module reloads.

    Args:
        name: The attribute name being accessed

    Returns:
        The environment variable value

    Raises:
        AttributeError: If the attribute is not a recognized environment variable
        ValueError: If a required environment variable is not set
    """
    # Define required environment variables
    required_env_vars = {
        "HIVE_URL": "TheHive instance base URL (e.g., https://thehive.com:9000)",
        "HIVE_API_KEY": "API key for authenticating with TheHive instance",
    }

    if name in required_env_vars:
        value = os.getenv(name)
        if value is None:
            raise ValueError(
                f"{name} environment variable is required but not set. Expected: {required_env_vars[name]}",
            )

        # Validate that the value is not empty or whitespace-only
        if not value.strip():
            raise ValueError(
                f"{name} environment variable is set but empty. Expected: {required_env_vars[name]}",
            )

        return value.strip()

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available attributes for better IDE support."""
    return sorted(list(globals().keys()) + __all__)
