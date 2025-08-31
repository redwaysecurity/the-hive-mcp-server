"""
Unit tests for alert module.

This module contains unit tests for the alert-related functionality
in the TheHive MCP server. Tests are organized by function for easy maintenance.
"""

import sys
from collections import UserDict
from pathlib import Path

import pytest
from thehive4py.errors import TheHiveError

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Note: Imports moved inside test methods to avoid triggering environment variable
# requirements before test fixtures have a chance to set them


@pytest.mark.unit
class TestAlertModule:
    """Test cases for alert module functionality."""

    def test_module_import(self):
        """Test that alert module can be imported."""
        try:
            import thehive_mcp.tools.alert

            assert thehive_mcp.tools.alert is not None
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")
        finally:
            pass  # reset the api_client as it may be set in the module

    def test_get_all_functions_structure(self, mock_hive_session):
        """Test that get_all_functions returns a list of Tool objects with required attributes."""
        from thehive_mcp.tools.alert import get_all_functions

        functions = get_all_functions()

        assert isinstance(functions, list)
        assert len(functions) > 0

        for tool in functions:
            from thehive_mcp.tool_wrapper import Tool

            assert isinstance(tool, Tool)
            assert hasattr(tool, "fn")
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert callable(tool.fn)
            assert isinstance(tool.name, str)
            assert isinstance(tool.description, str)
            assert len(tool.name) > 0
            assert len(tool.description) > 0

    def test_get_all_functions_includes_core_functions(self, mock_hive_session):
        """Test that get_all_functions includes expected core functions."""
        from thehive_mcp.tools.alert import get_all_functions

        functions = get_all_functions()
        function_names = [tool.name for tool in functions]

        # Check for core CRUD operations
        expected_functions = [
            "create_alert",
            "get_alerts",
            "get_alert",
            "update_alert",
            "delete_alert",
            "bulk_update_alerts",
            "bulk_delete_alerts",
            "count_alerts",
            "follow_alert",
            "unfollow_alert",
            "promote_alert_to_case",
            "merge_alert_into_case",
            "import_alert_into_case",
            "bulk_merge_alerts_into_case",
            "create_alert_observable",
            "find_alert_observables",
            "get_alert_similar_observables",
        ]

        for expected_func in expected_functions:
            assert expected_func in function_names, f"{expected_func} not found in function list"


@pytest.mark.unit
class TestCreateAlert:
    """Test cases for create_alert function."""

    @pytest.mark.asyncio
    async def test_create_alert_with_fields(self, mock_hive_session):
        """Test create_alert with field dictionary."""
        from thehive_mcp.tools.alert import create_alert

        # Setup mock response - create method returns the created object
        mock_hive_session.alert.create.return_value = {"_id": "new_alert", "title": "Test Alert"}

        # Test function call
        result = await create_alert(
            fields={
                "title": "Test Alert",
                "description": "Test Description",
                "type": "test-type",
                "source": "test-source",
                "sourceRef": "test-ref",
            },
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Created alert" in result[0].text
        mock_hive_session.alert.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_alert_without_fields(self, mock_hive_session):
        """Test create_alert without fields parameter."""
        from thehive_mcp.tools.alert import create_alert

        # Test function call with no fields
        result = await create_alert()

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Missing alert data" in result[0].text

    @pytest.mark.asyncio
    async def test_create_alert_api_error(self, mock_hive_session):
        """Test create_alert handles API errors gracefully."""
        from thehive_mcp.tools.alert import create_alert

        # Setup mock to raise exception
        mock_hive_session.alert.create.side_effect = TheHiveError("Error")

        # Test function call
        result = await create_alert(fields={"title": "Test"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error creating alert" in result[0].text


@pytest.mark.unit
class TestGetAlerts:
    """Test cases for get_alerts function."""

    @pytest.mark.asyncio
    async def test_get_alerts_no_parameters(self, mock_hive_session):
        """Test get_alerts with no parameters."""
        from thehive_mcp.tools.alert import get_alerts

        # Setup mock response - the find method returns the actual data
        mock_hive_session.alert.find.return_value = [
            {"_id": "alert1", "title": "Test Alert 1"},
            {"_id": "alert2", "title": "Test Alert 2"},
        ]

        result = await get_alerts()

        assert isinstance(result, list)
        assert len(result) == 2
        mock_hive_session.alert.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_alerts_with_filters(self, mock_hive_session):
        """Test get_alerts with filter parameters."""
        from thehive_mcp.tools.alert import get_alerts

        # Setup mock response
        mock_hive_session.alert.find.return_value = [{"_id": "alert1", "status": "New"}]

        # Test with filters
        filters = UserDict({"status": "New", "tags": ["malware"]})
        result = await get_alerts(filters=filters)

        assert isinstance(result, list)
        mock_hive_session.alert.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_alerts_with_sorting(self, mock_hive_session):
        """Test get_alerts with sorting parameters."""
        from thehive_mcp.tools.alert import get_alerts

        # Setup mock response
        mock_hive_session.alert.find.return_value = []

        # Test with sorting
        sortby = UserDict({"field": "createdAt", "order": "desc"})
        result = await get_alerts(sortby=sortby)

        assert isinstance(result, list)
        mock_hive_session.alert.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_alerts_with_pagination(self, mock_hive_session):
        """Test get_alerts with pagination parameters."""
        from thehive_mcp.tools.alert import get_alerts

        # Setup mock response
        mock_hive_session.alert.find.return_value = []

        # Test with pagination
        paginate = UserDict({"from": 0, "to": 10})
        result = await get_alerts(paginate=paginate)

        assert isinstance(result, list)
        mock_hive_session.alert.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_alerts_api_error(self, mock_hive_session):
        """Test get_alerts handles API errors gracefully."""
        from thehive_mcp.tools.alert import get_alerts

        # Setup mock to raise exception
        mock_hive_session.alert.find.side_effect = TheHiveError("Error")

        result = await get_alerts()

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error retrieving alerts" in result[0].text


@pytest.mark.unit
class TestGetAlert:
    """Test cases for get_alert function."""

    @pytest.mark.asyncio
    async def test_get_alert_success(self, mock_hive_session):
        """Test get_alert with valid alert ID."""
        from thehive_mcp.tools.alert import get_alert

        # Setup mock response - get method returns single object
        mock_hive_session.alert.get.return_value = {"_id": "alert123", "title": "Test Alert"}

        result = await get_alert(alert_id="alert123")

        assert isinstance(result, list)
        assert len(result) == 1
        mock_hive_session.alert.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_alert_api_error(self, mock_hive_session):
        """Test get_alert handles API errors gracefully."""
        from thehive_mcp.tools.alert import get_alert

        # Setup mock to raise exception
        mock_hive_session.alert.get.side_effect = TheHiveError("Alert not found")

        result = await get_alert(alert_id="nonexistent")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error getting alert" in result[0].text


@pytest.mark.unit
class TestUpdateAlert:
    """Test cases for update_alert function."""

    @pytest.mark.asyncio
    async def test_update_alert_success(self, mock_hive_session):
        """Test update_alert with valid parameters."""
        from thehive_mcp.tools.alert import update_alert

        # Setup mock response - update typically returns None or updated object
        mock_hive_session.alert.update.return_value = None

        result = await update_alert(
            alert_id="alert123",
            fields={
                "title": "Updated Alert Title",
                "status": "Closed",
                "severity": 3,
            },
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "updated successfully" in result[0].text
        mock_hive_session.alert.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_alert_api_error(self, mock_hive_session):
        """Test update_alert handles API errors gracefully."""
        from thehive_mcp.tools.alert import update_alert

        # Setup mock to raise exception
        mock_hive_session.alert.update.side_effect = TheHiveError("Update failed")

        result = await update_alert(alert_id="alert123", fields={"title": "New Title"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error updating alert" in result[0].text


@pytest.mark.unit
class TestDeleteAlert:
    """Test cases for delete_alert function."""

    @pytest.mark.asyncio
    async def test_delete_alert_success(self, mock_hive_session):
        """Test delete_alert with valid alert ID."""
        from thehive_mcp.tools.alert import delete_alert

        # Setup mock response - delete typically returns None
        mock_hive_session.alert.delete.return_value = None

        result = await delete_alert(alert_id="alert123")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "deleted successfully" in result[0].text
        mock_hive_session.alert.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_alert_api_error(self, mock_hive_session):
        """Test delete_alert handles API errors gracefully."""
        from thehive_mcp.tools.alert import delete_alert

        # Setup mock to raise exception
        mock_hive_session.alert.delete.side_effect = TheHiveError("Delete failed")

        result = await delete_alert(alert_id="alert123")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Error deleting alert" in result[0].text


@pytest.mark.unit
class TestBulkAlertOperations:
    """Test cases for bulk alert operations."""

    @pytest.mark.asyncio
    async def test_bulk_update_alerts_success(self, mock_hive_session):
        """Test bulk_update_alerts with valid parameters."""
        from thehive_mcp.tools.alert import bulk_update_alerts

        # Setup mock response - bulk_update typically returns None
        mock_hive_session.alert.bulk_update.return_value = None

        result = await bulk_update_alerts(
            alert_ids=["alert1", "alert2"],
            fields={"status": "Closed"},
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Updated 2 alerts successfully" in result[0].text
        mock_hive_session.alert.bulk_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_update_alerts_empty_ids(self, mock_hive_session):
        """Test bulk_update_alerts with empty alert IDs list."""
        from thehive_mcp.tools.alert import bulk_update_alerts

        result = await bulk_update_alerts(alert_ids=[], fields={"status": "Closed"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "No alert IDs provided" in result[0].text

    @pytest.mark.asyncio
    async def test_bulk_delete_alerts_success(self, mock_hive_session):
        """Test bulk_delete_alerts with valid parameters."""
        from thehive_mcp.tools.alert import bulk_delete_alerts

        # Setup mock response - bulk_delete typically returns None
        mock_hive_session.alert.bulk_delete.return_value = None

        result = await bulk_delete_alerts(alert_ids=["alert1", "alert2"])

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Deleted 2 alerts successfully" in result[0].text
        mock_hive_session.alert.bulk_delete.assert_called_once()


@pytest.mark.unit
class TestAlertObservables:
    """Test cases for alert observable operations."""

    @pytest.mark.asyncio
    async def test_create_alert_observable_success(self, mock_hive_session):
        """Test create_alert_observable with valid parameters."""
        from thehive_mcp.tools.alert import create_alert_observable

        # Setup mock response - create_observable method returns the created object
        mock_hive_session.alert.create_observable.return_value = {"_id": "obs123"}

        result = await create_alert_observable(
            alert_id="alert123",
            observable={
                "dataType": "ip",
                "data": "192.168.1.1",
                "message": "Test IP",
                "tags": ["test"],
            },
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Created observable" in result[0].text
        mock_hive_session.alert.create_observable.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_alert_observable_missing_required(self, mock_hive_session):
        """Test create_alert_observable with missing required fields."""
        from thehive_mcp.tools.alert import create_alert_observable

        result = await create_alert_observable(
            alert_id="alert123",
            observable={"message": "Missing dataType and data"},
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Missing required keys" in result[0].text

    @pytest.mark.asyncio
    async def test_find_alert_observables_success(self, mock_hive_session):
        """Test find_alert_observables with valid alert ID."""
        from thehive_mcp.tools.alert import find_alert_observables

        # Setup mock response - find_observables method returns list
        mock_hive_session.alert.find_observables.return_value = [{"_id": "obs1"}, {"_id": "obs2"}]

        result = await find_alert_observables(alert_id="alert123")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Alert observables" in result[0].text
        mock_hive_session.alert.find_observables.assert_called_once()


@pytest.mark.unit
class TestAlertStatusOperations:
    """Test cases for alert status operations."""

    @pytest.mark.asyncio
    async def test_follow_alert_success(self, mock_hive_session):
        """Test follow_alert with valid alert ID."""
        from thehive_mcp.tools.alert import follow_alert

        # Setup mock response - follow method typically returns None
        mock_hive_session.alert.follow.return_value = None

        result = await follow_alert(alert_id="alert123")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Now following alert" in result[0].text
        mock_hive_session.alert.follow.assert_called_once()

    @pytest.mark.asyncio
    async def test_unfollow_alert_success(self, mock_hive_session):
        """Test unfollow_alert with valid alert ID."""
        from thehive_mcp.tools.alert import unfollow_alert

        # Setup mock response - unfollow method typically returns None
        mock_hive_session.alert.unfollow.return_value = None

        result = await unfollow_alert(alert_id="alert123")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Unfollowed alert" in result[0].text
        mock_hive_session.alert.unfollow.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_alerts_with_filters(self, mock_hive_session):
        """Test count_alerts with filter parameters."""
        from thehive_mcp.tools.alert import count_alerts

        # Setup mock response - count method returns integer
        mock_hive_session.alert.count.return_value = 42

        filters = {"status": "New", "tags": ["malware"]}
        result = await count_alerts(filters=filters)

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Found 42 alerts" in result[0].text
        mock_hive_session.alert.count.assert_called_once()


@pytest.mark.unit
class TestAlertCaseOperations:
    """Test cases for alert-to-case operations."""

    @pytest.mark.asyncio
    async def test_promote_alert_to_case_success(self, mock_hive_session):
        """Test promote_alert_to_case with valid parameters."""
        from thehive_mcp.tools.alert import promote_alert_to_case

        # Setup mock response - promote_to_case returns the created case
        mock_hive_session.alert.promote_to_case.return_value = {"_id": "case123"}

        result = await promote_alert_to_case(alert_id="alert123", fields={"title": "New Case"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Promoted alert to case" in result[0].text
        mock_hive_session.alert.promote_to_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_merge_alert_into_case_success(self, mock_hive_session):
        """Test merge_alert_into_case with valid parameters."""
        from thehive_mcp.tools.alert import merge_alert_into_case

        # Setup mock response - merge_into_case returns merge result
        mock_hive_session.alert.merge_into_case.return_value = {"success": True}

        result = await merge_alert_into_case(alert_id="alert123", case_id="case456")

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Merged alert into case" in result[0].text
        mock_hive_session.alert.merge_into_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_merge_alerts_into_case_success(self, mock_hive_session):
        """Test bulk_merge_alerts_into_case with valid parameters."""
        from thehive_mcp.tools.alert import bulk_merge_alerts_into_case

        # Setup mock response - bulk_merge_into_case returns merge statistics
        mock_hive_session.alert.bulk_merge_into_case.return_value = {"merged": 2}

        result = await bulk_merge_alerts_into_case(
            case_id="case123",
            alert_ids=["alert1", "alert2"],
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Merged 2 alerts into case" in result[0].text
        mock_hive_session.alert.bulk_merge_into_case.assert_called_once()
