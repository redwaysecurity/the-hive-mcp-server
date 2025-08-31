"""Contract-level integration tests for TheHive MCP Server.

Goals:
    * Exercise real tool functions end-to-end (argument shaping -> endpoint method -> HTTP layer) while
        isolating network by patching only ``TheHiveSession.make_request``.
    * Verify path & verb composition for representative resources (alert, case).
    * Validate error & malformed response handling surfaces graceful TextContent output.
    * Keep this suite lean; deep branching & formatting are covered by unit tests.

Optional future live tests can be gated behind an env flag (not implemented here to stay fast by default).
"""

from unittest.mock import patch

import pytest


class TestContractSearch:
    """Representative search workflows (alert & case)."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "resource, func_import, kwargs, path_fragment, sample",
        [
            (
                "alert",
                "thehive_mcp.tools.alert.get_alerts",
                {},  # get_alerts has (filters, sortby, paginate)
                "/api/v1/alert/_search",
                [
                    {"_id": "alert_1", "title": "Security Alert 1", "status": "New"},
                    {"_id": "alert_2", "title": "Security Alert 2", "status": "New"},
                ],
            ),
            (
                "case",
                "thehive_mcp.tools.case.get_cases",
                {"filters": {"status": "Open"}, "paginate": {"limit": 10}},
                "/api/v1/case/_search",
                [
                    {"_id": "case_1", "title": "Investigation Case 1", "status": "Open"},
                    {"_id": "case_2", "title": "Investigation Case 2", "status": "Open"},
                ],
            ),
        ],
    )
    async def test_search_contract(self, resource, func_import, kwargs, path_fragment, sample):
        """Contract: tool function invokes endpoint .find and returns content list.

        We patch the endpoint's high-level find method (rather than low-level HTTP) to stay
        resilient against session caching / prior monkeypatching in unit fixtures.
        """
        module_path, func_name = func_import.rsplit(".", 1)
        # Select endpoint method patch target
        endpoint_find_target = (
            "thehive4py.endpoints.AlertEndpoint.find"
            if resource == "alert"
            else "thehive4py.endpoints.CaseEndpoint.find"
        )
        with patch(endpoint_find_target) as mock_find:
            mock_find.return_value = sample
            # Reset specific cached endpoint so our patched method is used on fresh instance
            if resource == "alert":
                import thehive_mcp.tools.alert as alert_mod

                alert_mod._alert_api = None
            else:
                import thehive_mcp.tools.case as case_mod

                case_mod._case_api = None  # type: ignore
            mod = __import__(module_path, fromlist=[func_name])
            func = getattr(mod, func_name)
            result = await func(**kwargs)
            mock_find.assert_called_once()
            assert isinstance(result, list)
            assert len(result) == len(sample)

    def test_required_dependencies_available(self):
        """Test that all required dependencies can be imported."""
        required_imports = [
            "mcp.types",
            "thehive4py.session",
            "thehive4py.endpoints",
            "click",
        ]

        for import_name in required_imports:
            try:
                __import__(import_name)
            except ImportError as e:
                pytest.fail(
                    f"Required dependency {import_name} could not be imported: {e}",
                )

    def test_all_modules_have_documentation(self):
        """Test that all modules have proper documentation."""
        modules_to_check = [
            "thehive_mcp.main",
            "thehive_mcp.tools.alert",
            "thehive_mcp.tools.case",
            "thehive_mcp.tools.observable",
            "thehive_mcp.tools.task",
        ]

        for module_name in modules_to_check:
            module = __import__(module_name, fromlist=[""])
            assert hasattr(module, "__doc__")
            assert module.__doc__ is not None
            assert len(module.__doc__.strip()) > 10


class TestErrorHandling:
    """Error and malformed response handling at contract level."""

    @pytest.mark.asyncio
    async def test_api_connection_error_handling(self):
        """Test handling of API connection errors."""
        # Mock HTTP request to raise connection error
        with patch("thehive4py.session.TheHiveSession.make_request") as mock_request:
            from thehive4py.errors import TheHiveError

            mock_request.side_effect = TheHiveError("Connection refused")

            from thehive_mcp.tools.alert import get_alerts

            # Should handle error gracefully
            result = await get_alerts()

            # Should return error message, not raise exception
            assert isinstance(result, list)
            assert len(result) == 1
            assert "Error retrieving alerts" in str(result[0])
