"""
Unit tests for case module.

This module contains unit tests for the case-related functionality
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
class TestCaseModule:
    """Test cases for case module functionality."""

    def test_module_import(self):
        """Test that case module can be imported."""

        import thehive_mcp.tools.case

        assert thehive_mcp.tools.case is not None

    @patch("thehive4py.endpoints.CaseEndpoint")
    def test_get_all_functions_exists(self, mock_case_endpoint_class, mock_hive_session):
        """Test that get_all_functions exists and returns expected format (Tool objects)."""
        from thehive_mcp.tools.case import get_all_functions

        # Setup basic mock
        mock_case_endpoint_class.return_value = MagicMock()

        functions = get_all_functions()

        assert isinstance(functions, list)
        assert len(functions) > 0

        # Check that each Tool object has the required fields
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

    @pytest.mark.asyncio
    async def test_get_cases_function(self, mock_hive_session):
        """Test get_cases function via Tool object."""

        from thehive_mcp.tools.case import get_all_functions

        # Setup mock response - the find method returns the actual data
        mock_hive_session.case.find.return_value = [
            {"_id": "case1", "title": "Test Case 1"},
            {"_id": "case2", "title": "Test Case 2"},
        ]

        # Get the get_cases Tool
        tool = next(t for t in get_all_functions() if t.name == "get_cases")
        result = await tool.fn()

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_create_case_function(self, mock_hive_session):
        """Test create_case function via Tool object."""

        from thehive_mcp.tools.case import get_all_functions

        # Setup mock response
        mock_hive_session.case.create.return_value = {"id": "new_case", "title": "Test Case"}

        tool = next(t for t in get_all_functions() if t.name == "create_case")
        result = await tool.fn(
            fields={
                "title": "Test Case",
                "description": "Test Description",
                "severity": 2,
                "tags": ["test"],
            }
        )

        assert isinstance(result, list)
        mock_hive_session.case.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_case_function(self, mock_hive_session):
        """Test update_case function via Tool object."""

        from thehive_mcp.tools.case import get_all_functions

        # Setup mock response
        mock_hive_session.case.update.return_value = None

        tool = next(t for t in get_all_functions() if t.name == "update_case")
        result = await tool.fn(
            case_id="case123",
            fields={
                "title": "Updated Title",
                "status": "Closed",
            },
        )

        assert isinstance(result, list)
        assert mock_hive_session.case.update.called
        assert mock_hive_session.case.update.call_count == 1


@pytest.mark.unit
class TestCaseFunctionSignatures:
    """Test function signatures and basic validation."""

    def test_case_functions_are_callable(self):
        """Test that case functions have proper callable signatures."""

        from thehive_mcp.tools.case import (
            close_case,
            create_case,
            delete_case,
            get_case,
            get_cases,
            merge_cases,
            update_case,
        )

        assert callable(get_cases)
        assert callable(create_case)
        assert callable(get_case)
        assert callable(update_case)
        assert callable(delete_case)
        assert callable(close_case)
        assert callable(merge_cases)

    def test_function_docstrings_exist(self):
        """Test that functions have proper docstrings."""
        from thehive_mcp.tools.case import create_case, get_cases, update_case

        assert get_cases.__doc__ is not None
        assert create_case.__doc__ is not None
        assert update_case.__doc__ is not None


@pytest.mark.unit
class TestCaseObservableOperations:
    """Test case observable-related operations."""

    @pytest.mark.asyncio
    async def test_create_case_observable(self, mock_hive_session):
        """Test create_case_observable function."""

        from thehive_mcp.tools.case import create_case_observable

        # Setup mock response
        mock_hive_session.case.create_observable = MagicMock(return_value=[{"id": "obs123"}])

        # Test function call
        result = await create_case_observable(
            case_id="case123",
            data_type="ip",
            data="192.168.1.1",
            message="Test observable",
            tags=["ioc"],
        )

        assert isinstance(result, list)
        # Verify the method was called
        assert mock_hive_session.case.create_observable.called

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.case._get_case_api")
    async def test_find_case_observables(self, mock_hive_session):
        """Test find_case_observables function."""
        from thehive_mcp.tools.case import find_case_observables

        # Mock the API client
        mock_case_api = MagicMock()
        mock_case_api.find_observables = MagicMock(return_value=[])
        mock_hive_session.case = mock_case_api

        # Test function call
        result = await find_case_observables(case_id="case123")

        assert isinstance(result, list)


@pytest.mark.unit
class TestCaseTaskOperations:
    """Test case task-related operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.case._get_case_api")
    async def test_create_case_task(self, mock_hive_session):
        """Test create_case_task function."""
        from thehive_mcp.tools.case import create_case_task

        # Mock the API client
        mock_case_api = MagicMock()
        mock_case_api.create_task = MagicMock(return_value={"id": "task123"})
        mock_hive_session.case = mock_case_api

        # Test function call
        result = await create_case_task(
            case_id="case123",
            fields={
                "title": "Test Task",
                "description": "Test Description",
                "status": "Waiting",
            },
        )

        assert isinstance(result, list)


@pytest.mark.unit
class TestCaseAttachmentOperations:
    """Test case attachment-related operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.case._get_case_api")
    async def test_add_case_attachment(self, mock_hive_session):
        """Test add_case_attachment function."""
        from thehive_mcp.tools.case import add_case_attachment

        # Mock the API client
        mock_case_api = MagicMock()
        mock_case_api.add_attachment = MagicMock(return_value=[{"id": "att123"}])
        mock_hive_session.case = mock_case_api

        # Test function call
        result = await add_case_attachment(
            case_id="case123",
            attachment_paths=["/tmp/test.txt"],
            can_rename=True,
        )

        assert isinstance(result, list)


@pytest.mark.unit
class TestCaseBulkOperations:
    """Test case bulk operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.case._get_case_api")
    async def test_bulk_update_cases(self, mock_hive_session):
        """Test bulk_update_cases function."""
        from thehive_mcp.tools.case import bulk_update_cases

        # Mock the API client
        mock_case_api = MagicMock()
        mock_case_api.bulk_update = MagicMock()
        mock_hive_session.case = mock_case_api

        # Test function call
        result = await bulk_update_cases(
            case_ids=["case1", "case2"],
            status="Closed",
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.case._get_case_api")
    async def test_count_cases(self, mock_hive_session):
        """Test count_cases function."""
        from thehive_mcp.tools.case import count_cases

        # Mock the API client
        mock_case_api = MagicMock()
        mock_case_api.count = MagicMock(return_value=42)
        mock_hive_session.case = mock_case_api

        # Test function call
        result = await count_cases(filters={"status": "Open"})

        assert isinstance(result, list)
