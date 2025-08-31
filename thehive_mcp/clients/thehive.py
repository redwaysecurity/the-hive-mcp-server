"""
TheHive API client (lazy, cached)

This module exposes a lazily created and cached TheHiveSession instance using
project environment settings. It mirrors the previous modules.hive_session
API to ease migration.
"""

from __future__ import annotations

import time

import urllib3
from thehive4py.session import TheHiveSession 
from thehive4py.errors import TheHiveError

from thehive_mcp.envs import get_hive_api_key, get_hive_url
from thehive_mcp.logger import get_logger

logger = get_logger(__name__)

# Disable SSL warnings for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ["get_hive_session"]

_hive_session: TheHiveSession | None = None
_client_creation_time: float | None = None
_CLIENT_CACHE_DURATION = 300  # seconds


def _reset_hive_session() -> None:
    """Reset the cached API client. Used for testing."""
    global _hive_session, _client_creation_time
    _hive_session = None
    _client_creation_time = None


def _create_hive_session() -> TheHiveSession:
    """Create a new API client with optimized settings."""
    hive_url = get_hive_url()
    hive_api_key = get_hive_api_key()
    logger.debug(f"Creating TheHiveSession with URL: {hive_url}")
    try:
        session = TheHiveSession(url=hive_url, apikey=hive_api_key, verify=False)
        logger.debug(f"Successfully created TheHiveSession: {type(session)}")
        return session
    except TheHiveError as e:
        logger.error(f"Failed to create TheHiveSession: {e}")
        raise e


def get_hive_session() -> TheHiveSession:
    """Get a cached TheHive session instance."""
    global _hive_session, _client_creation_time

    now = time.time()
    if (
        _hive_session is None
        or _client_creation_time is None
        or now - _client_creation_time > _CLIENT_CACHE_DURATION
    ):
        logger.debug("Creating new hive session")
        _hive_session = _create_hive_session()
        _client_creation_time = now
    else:
        logger.debug("Using cached hive session")

    logger.debug(f"Returning hive_session: {type(_hive_session)}")
    return _hive_session


def __getattr__(name: str) -> TheHiveSession:
    """Lazy initialization of hive (and hive_session alias) with caching."""
    if name in ("hive_session"):
        return get_hive_session()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
