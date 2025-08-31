import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Pytest configuration
pytest_plugins = []


# Custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers",
        "requires_api: mark test as requiring API connection",
    )


# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark async tests
        if "async" in item.name:
            item.add_marker(pytest.mark.asyncio)


# Fixtures for test environment
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""

    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["HIVE_URL"] = "http://test-thehive.local:9000"
    os.environ["HIVE_API_KEY"] = "test-integration-key"


@pytest.fixture
def mock_hive_session():
    """Simple mock fixture for TheHive session and endpoints.

    Returns a mock session with pre-configured endpoints that return empty lists
    for find/search operations and mock objects for other operations.

    Usage:
        - mock_hive_session.alert.find.return_value = [...]  # Configure alert results
        - mock_hive_session.case.create.return_value = {...}  # Configure case creation
        - mock_hive_session.task.get.return_value = {...}     # Configure task retrieval
    """
    # Create mock session with all endpoints
    mock_session = MagicMock(name="MockHiveSession")

    # Configure alert endpoint with sensible defaults
    mock_session.alert = MagicMock()
    mock_session.alert.find.return_value = []
    mock_session.alert.count.return_value = 0
    mock_session.alert.create.return_value = {"_id": "mock_alert_id"}

    # Configure case endpoint with sensible defaults
    mock_session.case = MagicMock()
    mock_session.case.find.return_value = []
    mock_session.case.count.return_value = 0
    mock_session.case.create.return_value = {"_id": "mock_case_id"}

    # Configure task endpoint with sensible defaults
    mock_session.task = MagicMock()
    mock_session.task.find.return_value = []
    mock_session.task.count.return_value = 0
    mock_session.task.create.return_value = {"_id": "mock_task_id"}

    # Configure observable endpoint with sensible defaults
    mock_session.observable = MagicMock()
    mock_session.observable.find.return_value = []
    mock_session.observable.count.return_value = 0
    mock_session.observable.create.return_value = {"_id": "mock_observable_id"}

    # Start patchers
    patchers = []

    # Patch the session factory
    session_patcher = patch("thehive_mcp.clients.thehive._create_hive_session", return_value=mock_session)
    patchers.append(session_patcher)
    session_patcher.start()

    # Patch individual API getters to return the mock endpoints
    alert_patcher = patch("thehive_mcp.tools.alert._get_alert_api", return_value=mock_session.alert)
    patchers.append(alert_patcher)
    alert_patcher.start()

    case_patcher = patch("thehive_mcp.tools.case._get_case_api", return_value=mock_session.case)
    patchers.append(case_patcher)
    case_patcher.start()

    task_patcher = patch("thehive_mcp.tools.task._get_task_api", return_value=mock_session.task)
    patchers.append(task_patcher)
    task_patcher.start()

    # Reset module caches to ensure patches take effect
    _reset_module_caches()

    yield mock_session

    # Cleanup: stop all patchers and reset caches
    for patcher in patchers:
        patcher.stop()
    _reset_module_caches()


def _reset_module_caches():
    """Reset cached API objects in all tool modules."""
    try:
        from thehive_mcp.clients import thehive as client_mod

        client_mod._reset_hive_session()

        import thehive_mcp.tools.alert as alert_mod

        alert_mod._alert_api = None

        import thehive_mcp.tools.case as case_mod

        case_mod._case_api = None

        import thehive_mcp.tools.task as task_mod

        task_mod._task_api = None
        task_mod._task_log_api = None
    except ImportError:
        # Some modules might not be available during cleanup
        pass
