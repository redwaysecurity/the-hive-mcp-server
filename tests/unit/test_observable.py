"""
Unit tests for observable module.

This module contains unit tests for the observable-related functionality
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
class TestObservableModule:
    """Test cases for observable module functionality."""

    def test_module_import(self):
        """Test that observable module can be imported."""
        try:
            import thehive_mcp.tools.observable

            assert thehive_mcp.tools.observable is not None
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    @patch("thehive_mcp.clients.thehive.hive_session")
    def test_get_all_functions_exists(self, mock_hive_session):
        """Test that get_all_functions exists and returns expected format (Tool objects)."""
        try:
            from thehive_mcp.tools.observable import get_all_functions

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
            pytest.skip("Observable module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_get_observables_function_format(self, mock_hive_session):
        """Test that get_observables function has proper async signature."""

        from thehive_mcp.tools.observable import get_all_functions

        # Mock the API client and its methods
        mock_observable_api = MagicMock()
        mock_observable_api.find = MagicMock(return_value=[])
        mock_hive_session.observable = mock_observable_api

        # Get the get_observables Tool
        tool = next(t for t in get_all_functions() if t.name == "get_observables")
        assert callable(tool.fn)

        # Try calling with minimal arguments
        result = await tool.fn(
            filters={
                "_and": {"_field": {"dataType": "ip"}},
                "paginate": {"from": 0, "to": 1},
                "sortby": {"createdAt": "asc"},
            }
        )
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_create_observable_function(self, mock_hive_session):
        """Test create_observable function via Tool object."""
        try:
            from thehive_mcp.tools.observable import get_all_functions

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.create = MagicMock(
                return_value={"id": "obs123", "data": "192.168.1.1"},
            )
            mock_hive_session.observable = mock_observable_api

            tool = next(t for t in get_all_functions() if t.name == "create_observable_in_case")
            result = await tool.fn(
                case_id="case123",
                fields={
                    "dataType": "ip",
                    "data": "192.168.1.1",
                    "message": "Test IP",
                    "tags": ["ioc"],
                    "ioc": True,
                },
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_update_observable_function(self, mock_hive_session):
        """Test update_observable function via Tool object."""
        try:
            from thehive_mcp.tools.observable import get_all_functions

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.update = MagicMock()
            mock_hive_session.observable = mock_observable_api

            tool = next(t for t in get_all_functions() if t.name == "update_observable")
            result = await tool.fn(observable_id="obs123", message="Updated message", ioc=True, sighted=True)

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")


@pytest.mark.unit
class TestObservableFunctionSignatures:
    """Test function signatures and basic validation."""

    def test_observable_functions_are_callable(self):
        """Test that observable functions have proper callable signatures."""
        # try:
        from thehive_mcp.tools.observable import (
            create_observable_in_alert,
            create_observable_in_case,
            delete_observable,
            get_observable,
            get_observables,
            share_observable,
            update_observable,
        )

        assert callable(get_observables)
        assert callable(create_observable_in_alert)
        assert callable(create_observable_in_case)
        assert callable(get_observable)
        assert callable(update_observable)
        assert callable(delete_observable)
        assert callable(share_observable)

        # except ImportError:
        #     pytest.skip("Observable module not available")

    def test_function_docstrings_exist(self):
        """Test that functions have proper docstrings."""

        from thehive_mcp.tools.observable import (
            create_observable_in_case,
            get_observables,
            update_observable,
        )

        assert get_observables.__doc__ is not None
        assert create_observable_in_case.__doc__ is not None
        assert update_observable.__doc__ is not None


@pytest.mark.unit
class TestObservableSharingOperations:
    """Test observable sharing-related operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_share_observable(self, mock_hive_session):
        """Test share_observable function."""
        try:
            from thehive_mcp.tools.observable import share_observable

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.share = MagicMock()
            mock_hive_session.observable = mock_observable_api

            # Test function call
            result = await share_observable(
                observable_id="obs123",
                organizations=["org1", "org2"],
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_unshare_observable(self, mock_hive_session):
        """Test unshare_observable function."""

        from thehive_mcp.tools.observable import unshare_observable

        # Mock the API client
        mock_observable_api = MagicMock()
        mock_observable_api.unshare = MagicMock()
        mock_hive_session.observable = mock_observable_api

        # Test function call
        result = await unshare_observable(
            observable_id="obs123",
            organizations=["org1"],
        )

        assert isinstance(result, list)


@pytest.mark.unit
class TestObservableBulkOperations:
    """Test observable bulk operations."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_bulk_update_observables(self, mock_hive_session):
        """Test bulk_update_observables function."""
        try:
            from thehive_mcp.tools.observable import bulk_update_observables

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.bulk_update = MagicMock()
            mock_hive_session.observable = mock_observable_api

            # Test function call
            result = await bulk_update_observables(
                observable_ids=["obs1", "obs2"],
                ioc=True,
                tags=["malicious"],
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_count_observables(self, mock_hive_session):
        """Test count_observables function."""
        try:
            from thehive_mcp.tools.observable import count_observables

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.count = MagicMock(return_value=15)
            mock_hive_session.observable = mock_observable_api

            # Test function call
            result = await count_observables(data_type="ip")

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")


@pytest.mark.unit
class TestObservableDataTypes:
    """Test observable data type handling."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_create_ip_observable(self, mock_hive_session):
        """Test creating IP observable."""
        try:
            from thehive_mcp.tools.observable import create_observable_in_case

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.create = MagicMock(return_value={"id": "obs123"})
            mock_hive_session.observable = mock_observable_api

            # Test function call with IP data
            result = await create_observable_in_case(
                case_id="case123",
                fields={
                    "dataType": "ip",
                    "data": "192.168.1.1",
                    "ioc": True,
                },
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")

    @pytest.mark.asyncio
    @patch("thehive_mcp.clients.thehive.hive_session")
    async def test_create_hash_observable(self, mock_hive_session):
        """Test creating hash observable."""
        try:
            from thehive_mcp.tools.observable import create_observable_in_case

            # Mock the API client
            mock_observable_api = MagicMock()
            mock_observable_api.create = MagicMock(return_value={"id": "obs124"})
            mock_hive_session.observable = mock_observable_api

            # Test function call with hash data
            result = await create_observable_in_case(
                case_id="case123",
                fields={
                    "dataType": "hash",
                    "data": "d41d8cd98f00b204e9800998ecf8427e",
                    "message": "MD5 hash",
                    "ioc": True,
                },
            )

            assert isinstance(result, list)

        except ImportError:
            pytest.skip("Observable module not available")
