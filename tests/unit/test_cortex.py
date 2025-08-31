"""
Unit tests for cortex module.

This module contains unit tests for the Cortex-related functionality
in the TheHive MCP server.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from thehive4py.errors import TheHiveError

# Add src to path (kept for consistency with other tests)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.mark.unit
class TestCortexModule:
    """Basic tests for cortex module import and function list."""

    def test_module_import(self):
        try:
            import thehive_mcp.tools.cortex

            assert thehive_mcp.tools.cortex is not None
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    def test_get_all_functions_exists(self):
        from thehive_mcp.tools.cortex import get_all_functions

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

        # Ensure some expected tool names are present
        names = [tool.name for tool in functions]
        assert "list_cortex_analyzers" in names
        assert "create_cortex_analyzer_job" in names
        assert "list_cortex_responders" in names


@pytest.mark.unit
class TestCortexAnalyzers:
    """Tests for analyzer listing and job creation."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_list_cortex_analyzers(self, mock_get_api):
        from thehive_mcp.tools.cortex import list_cortex_analyzers

        mock_api = Mock()
        mock_api.list_analyzers = Mock(return_value=[{"id": "an1"}])
        mock_get_api.return_value = mock_api

        result = await list_cortex_analyzers(range="0-49")

        mock_api.list_analyzers.assert_called_once_with(range="0-49")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_list_cortex_analyzers_by_type(self, mock_get_api):
        from thehive_mcp.tools.cortex import list_cortex_analyzers_by_type

        mock_api = Mock()
        mock_api.list_analyzers_by_type = Mock(return_value=[{"id": "an2"}])
        mock_get_api.return_value = mock_api

        result = await list_cortex_analyzers_by_type(data_type="ip")

        mock_api.list_analyzers_by_type.assert_called_once_with(data_type="ip")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_get_cortex_analyzer(self, mock_get_api):
        from thehive_mcp.tools.cortex import get_cortex_analyzer

        mock_api = Mock()
        mock_api.get_analyzer = Mock(return_value={"id": "anX"})
        mock_get_api.return_value = mock_api

        result = await get_cortex_analyzer(analyzer_id="anX")

        mock_api.get_analyzer.assert_called_once_with(analyzer_id="anX")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_create_cortex_analyzer_job(self, mock_get_api):
        from thehive_mcp.tools.cortex import create_cortex_analyzer_job

        mock_api = Mock()
        mock_api.create_analyzer_job = Mock(return_value={"id": "job1"})
        mock_get_api.return_value = mock_api

        result = await create_cortex_analyzer_job(
            analyzer_id="anX",
            cortex_id="cx1",
            artifact_id="obs123",
            parameters={"foo": "bar"},
        )

        mock_api.create_analyzer_job.assert_called_once()
        # Verify payload mapping
        args, kwargs = mock_api.create_analyzer_job.call_args
        assert "job" in kwargs
        job = kwargs["job"]
        assert job["analyzerId"] == "anX"
        assert job["cortexId"] == "cx1"
        assert job["artifactId"] == "obs123"
        assert job["parameters"] == {"foo": "bar"}
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_get_cortex_analyzer_job(self, mock_get_api):
        from thehive_mcp.tools.cortex import get_cortex_analyzer_job

        mock_api = Mock()
        mock_api.get_analyzer_job = Mock(return_value={"id": "job1"})
        mock_get_api.return_value = mock_api

        result = await get_cortex_analyzer_job(job_id="job1")

        mock_api.get_analyzer_job.assert_called_once_with(job_id="job1")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch(
        "thehive_mcp.tools.cortex.create_cortex_analyzer_job",
        new_callable=AsyncMock,
    )
    async def test_run_observable_analyzer(self, mock_create_job):
        from thehive_mcp.tools.cortex import run_observable_analyzer

        mock_create_job.return_value = [
            # mimic TextContent list
            type("T", (), {"type": "text", "text": "ok"}),
        ]

        result = await run_observable_analyzer(
            analyzer_id="anX",
            cortex_id="cx1",
            observable_id="obs123",
            parameters={"p": 1},
        )

        mock_create_job.assert_awaited_once_with(
            analyzer_id="anX",
            cortex_id="cx1",
            artifact_id="obs123",
            parameters={"p": 1},
        )
        assert isinstance(result, list)


@pytest.mark.unit
class TestCortexResponders:
    """Tests for responder listing and responder actions."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_list_cortex_responders(self, mock_get_api):
        from thehive_mcp.tools.cortex import list_cortex_responders

        mock_api = Mock()
        mock_api.list_responders = Mock(return_value=[{"id": "resp1"}])
        mock_get_api.return_value = mock_api

        result = await list_cortex_responders(entity_type="case", entity_id="case123")

        mock_api.list_responders.assert_called_once_with(
            entity_type="case",
            entity_id="case123",
        )
        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_create_cortex_responder_action(self, mock_get_api):
        from thehive_mcp.tools.cortex import create_cortex_responder_action

        mock_api = Mock()
        mock_api.create_responder_action = Mock(return_value={"id": "act1"})
        mock_get_api.return_value = mock_api

        result = await create_cortex_responder_action(
            object_type="case",
            object_id="case123",
            responder_id="respX",
            parameters={"confirm": True},
            tlp=2,
        )

        mock_api.create_responder_action.assert_called_once()
        args, kwargs = mock_api.create_responder_action.call_args
        assert "action" in kwargs
        action = kwargs["action"]
        assert action["objectType"] == "case"
        assert action["objectId"] == "case123"
        assert action["responderId"] == "respX"
        assert action["parameters"] == {"confirm": True}
        assert action["tlp"] == 2
        assert isinstance(result, list)


@pytest.mark.unit
class TestCortexErrorHandling:
    """Tests for error handling in cortex tools."""

    @pytest.mark.asyncio
    @patch("thehive_mcp.tools.cortex._get_cortex_api")
    async def test_list_analyzers_error(self, mock_get_api):
        from thehive_mcp.tools.cortex import list_cortex_analyzers, types

        mock_api = Mock()
        mock_api.list_analyzers.side_effect = TheHiveError("boom")
        mock_get_api.return_value = mock_api

        result = await list_cortex_analyzers()
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error listing analyzers: boom" in result[0].text
