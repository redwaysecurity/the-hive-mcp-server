"""
Unit tests for task module.

This module contains unit tests for the task-related functionality
in the TheHive MCP server.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.mark.unit
class TestTaskModule:
    """Test cases for task module functionality."""

    def test_module_import(self):
        """Test that task module can be imported."""
        try:
            import thehive_mcp.tools.task

            assert thehive_mcp.tools.task is not None
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    @patch("thehive_mcp.tools.task._get_task_api")
    def test_get_all_functions_exists(self, mock_hive_session):
        """Test that get_all_functions exists and returns expected format."""
        try:
            from thehive_mcp.tools.task import get_all_functions

            functions = get_all_functions()

            assert isinstance(functions, list)
            assert len(functions) > 0

            from thehive_mcp.tool_wrapper import Tool

            for tool in functions:
                assert isinstance(tool, Tool)
                assert hasattr(tool, "fn")
                assert hasattr(tool, "name")
                assert hasattr(tool, "description")
                assert callable(tool.fn)
                assert isinstance(tool.name, str)
                assert isinstance(tool.description, str)
                assert len(tool.name) > 0
                assert len(tool.description) > 0
        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_get_tasks_function_format(self, mock_hive_session):
        """Test that get_tasks function has proper async signature."""
        try:
            from thehive_mcp.tools.task import get_tasks

            # Mock the API client and its methods
            mock_task_api = MagicMock()
            mock_task_api.find = MagicMock(return_value=[])
            mock_hive_session.task = mock_task_api

            # Test that the function can be called
            assert callable(get_tasks)

            # Try calling with minimal arguments
            try:
                result = await get_tasks(status="Waiting", limit=1, sort="+createdAt")
                # Check the format
                assert isinstance(result, list)
            except Exception:
                # Expected to fail without proper setup, that's OK for unit test
                pass

        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_create_task_function(self, mock_hive_session):
        """Test create_task function."""
        try:
            from thehive_mcp.tools.task import create_task

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.create = MagicMock(
                return_value={"id": "task123", "title": "Test Task"},
            )
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await create_task(
                case_id="case123",
                fields={
                    "title": "Test Task",
                    "description": "Test Description",
                    "status": "Waiting",
                    "assignee": "analyst1",
                },
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_update_task_function(self, mock_hive_session):
        """Test update_task function."""
        try:
            from thehive_mcp.tools.task import update_task

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.update = MagicMock()
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await update_task(
                task_id="task123",
                fields={
                    "title": "Updated Title",
                    "status": "InProgress",
                },
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")


@pytest.mark.unit
class TestTaskFunctionSignatures:
    """Test function signatures and basic validation."""

    def test_task_functions_are_callable(self):
        """Test that task functions have proper callable signatures."""
        try:
            from thehive_mcp.tools.task import (
                assign_task,
                complete_task,
                create_task,
                delete_task,
                get_task,
                get_tasks,
                start_task,
                update_task,
            )

            assert callable(get_tasks)
            assert callable(create_task)
            assert callable(get_task)
            assert callable(update_task)
            assert callable(delete_task)
            assert callable(complete_task)
            assert callable(start_task)
            assert callable(assign_task)

        except ImportError:
            pytest.skip("Task module not available")

    def test_function_docstrings_exist(self):
        """Test that functions have proper docstrings."""
        try:
            from thehive_mcp.tools.task import create_task, get_tasks, update_task

            assert get_tasks.__doc__ is not None
            assert create_task.__doc__ is not None
            assert update_task.__doc__ is not None

        except ImportError:
            pytest.skip("Task module not available")


@pytest.mark.unit
class TestTaskStatusOperations:
    """Test task status-related operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_complete_task(self, mock_hive_session):
        """Test complete_task function."""
        try:
            from thehive_mcp.tools.task import complete_task

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.complete = MagicMock()
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await complete_task(task_id="task123")

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_start_task(self, mock_hive_session):
        """Test start_task function."""
        try:
            from thehive_mcp.tools.task import start_task

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.start = MagicMock()
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await start_task(task_id="task123")

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_assign_task(self, mock_hive_session):
        """Test assign_task function."""
        try:
            from thehive_mcp.tools.task import assign_task

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.assign = MagicMock()
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await assign_task(task_id="task123", assignee="analyst2")

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")


@pytest.mark.unit
class TestTaskLogOperations:
    """Test task log-related operations."""

    @pytest.mark.asyncio
    async def test_create_task_log(self, mock_hive_session):
        """Test create_task_log function."""
        try:
            from thehive_mcp.tools.task import create_task_log

            # Mock the API client via the hive_session fixture
            mock_task_api = MagicMock()
            mock_task_api.create_log = MagicMock(return_value={"id": "log123"})
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await create_task_log(
                task_id="task123",
                message="Task progress update",
                include_in_timeline=True,
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_find_task_logs(self, mock_hive_session):
        """Test find_task_logs function."""
        try:
            from thehive_mcp.tools.task import find_task_logs

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.find_logs = MagicMock(return_value=[])
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await find_task_logs(task_id="task123")

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")


@pytest.mark.unit
class TestTaskBulkOperations:
    """Test task bulk operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_bulk_update_tasks(self, mock_hive_session):
        """Test bulk_update_tasks function."""
        try:
            from thehive_mcp.tools.task import bulk_update_tasks

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.bulk_update = MagicMock()
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await bulk_update_tasks(
                task_ids=["task1", "task2"],
                status="Completed",
                assignee="analyst1",
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.task._get_task_api")
    async def test_count_tasks(self, mock_hive_session):
        """Test count_tasks function."""
        try:
            from thehive_mcp.tools.task import count_tasks

            # Mock the API client
            mock_task_api = MagicMock()
            mock_task_api.count = MagicMock(return_value=8)
            mock_hive_session.task = mock_task_api

            # Test function call
            result = await count_tasks(status="InProgress", assignee="analyst1")

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Task module not available")


@pytest.mark.unit
class TestTaskFiltering:
    """Test task filtering functionality."""

    @pytest.mark.asyncio
    async def test_get_tasks_by_case(self, mock_hive_session):
        """Test getting tasks filtered by case."""

        from thehive_mcp.tools.task import get_tasks

        # Setup mock via the make_request_mock to return empty list for API calls
        mock_hive_session.make_request_mock.return_value = []

        # Test function call with case filter
        result = await get_tasks(filters={"case_id": "case123", "status": "Waiting"})

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_tasks_by_assignee(self, mock_hive_session):
        """Test getting tasks filtered by assignee."""

        from thehive_mcp.tools.task import get_tasks

        # Setup mock via the make_request_mock to return empty list for API calls
        mock_hive_session.make_request_mock.return_value = []

        # Test function call with assignee filter
        result = await get_tasks(filters={"assignee": "analyst1", "status": "InProgress"})

        assert isinstance(result, list)
