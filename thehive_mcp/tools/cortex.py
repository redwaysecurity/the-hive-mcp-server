"""Cortex integration tools for TheHive MCP Server.

This module exposes a subset of Cortex connector features via TheHive4py's
CortexEndpoint. It allows listing analyzers, running analyzers on
observables, tracking analyzer jobs, listing responders, and executing
responder actions.
"""

from typing import Any, TYPE_CHECKING

from thehive_mcp.tool_wrapper import Tool
from mcp import types

from thehive_mcp.logger import get_logger
from thehive4py.errors import TheHiveError

if TYPE_CHECKING:
    from thehive4py.endpoints import CortexEndpoint


logger = get_logger(__name__)

_cortex_api = None


def _get_cortex_api() -> "CortexEndpoint":
    """Get or create the cortex API endpoint.
    
    Import performed lazily to honor any active patches.
    """
    from thehive4py.endpoints import CortexEndpoint

    from thehive_mcp.clients.thehive import hive_session
    global _cortex_api
    if _cortex_api is None:
        _cortex_api = CortexEndpoint(hive_session)
    return _cortex_api


# For direct access and monkey-patching in tests
def __getattr__(name: str) -> Any:
    if name == "cortex_api":
        return _get_cortex_api()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_all_functions() -> list[Tool]:
    """Return functions exposed by this module for MCP server registration."""
    return [
        # Analyzers
        Tool(
            fn=list_cortex_analyzers,
            name="list_cortex_analyzers",
            title="List Cortex Analyzers",
            description="List available Cortex analyzers.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "range": {
                        "type": "string",
                        "description": "Optional pagination range header value, e.g. '0-49'",
                    },
                },
            },
        ),
        Tool(
            fn=list_cortex_analyzers_by_type,
            name="list_cortex_analyzers_by_type",
            title="List Cortex Analyzers by Type",
            description="List Cortex analyzers for a data type.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "description": "Observable data type",
                    },
                },
                "required": ["data_type"],
            },
        ),
        Tool(
            fn=get_cortex_analyzer,
            name="get_cortex_analyzer",
            title="Get Cortex Analyzer",
            description="Get a Cortex analyzer by id.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "analyzer_id": {
                        "type": "string",
                        "description": "Analyzer ID",
                    },
                },
                "required": ["analyzer_id"],
            },
        ),
        Tool(
            fn=create_cortex_analyzer_job,
            name="create_cortex_analyzer_job",
            title="Create Cortex Analyzer Job",
            description="Create a Cortex analyzer job.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "analyzer_id": {
                        "type": "string",
                        "description": "Analyzer ID",
                    },
                    "cortex_id": {
                        "type": "string",
                        "description": "Cortex ID",
                    },
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional parameters",
                    },
                },
                "required": ["analyzer_id", "cortex_id", "artifact_id"],
            },
        ),
        Tool(
            fn=get_cortex_analyzer_job,
            name="get_cortex_analyzer_job",
            title="Get Cortex Analyzer Job",
            description="Get a Cortex analyzer job by id.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID",
                    },
                },
                "required": ["job_id"],
            },
        ),
        Tool(
            fn=run_observable_analyzer,
            name="run_observable_analyzer",
            title="Run Observable Analyzer",
            description="Run a Cortex analyzer on an observable.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "analyzer_id": {
                        "type": "string",
                        "description": "Analyzer ID",
                    },
                    "cortex_id": {
                        "type": "string",
                        "description": "Cortex ID",
                    },
                    "observable_id": {
                        "type": "string",
                        "description": "Observable ID",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional parameters",
                    },
                },
                "required": ["analyzer_id", "cortex_id", "observable_id"],
            },
        ),
        # Responders
        Tool(
            fn=list_cortex_responders,
            name="list_cortex_responders",
            title="List Cortex Responders",
            description="List Cortex responders for an entity.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "Entity type",
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID",
                    },
                },
                "required": ["entity_type", "entity_id"],
            },
        ),
        Tool(
            fn=create_cortex_responder_action,
            name="create_cortex_responder_action",
            title="Create Cortex Responder Action",
            description="Execute a Cortex responder action.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "object_type": {
                        "type": "string",
                        "description": "Object type",
                    },
                    "object_id": {
                        "type": "string",
                        "description": "Object ID",
                    },
                    "responder_id": {
                        "type": "string",
                        "description": "Responder ID",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Optional parameters",
                    },
                    "tlp": {
                        "type": "integer",
                        "description": "TLP level",
                    },
                },
                "required": ["object_type", "object_id", "responder_id"],
            },
        ),
    ]


async def list_cortex_analyzers(
    range: str | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """List available Cortex analyzers.

    Args:
        range: Optional pagination range header value, e.g. "0-49".
    """
    try:
        api = _get_cortex_api()
        result = api.list_analyzers(range=range)  # returns a list of analyzers
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error listing analyzers: {e!s}"),
        ]


async def list_cortex_analyzers_by_type(
    data_type: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """List Cortex analyzers supporting a specific observable data type."""
    try:
        api = _get_cortex_api()
        result = api.list_analyzers_by_type(data_type=data_type)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error listing analyzers by type: {e!s}",
            ),
        ]


async def get_cortex_analyzer(
    analyzer_id: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Get a Cortex analyzer by id."""
    try:
        api = _get_cortex_api()
        result = api.get_analyzer(analyzer_id=analyzer_id)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error getting analyzer: {e!s}"),
        ]


async def create_cortex_analyzer_job(
    analyzer_id: str,
    cortex_id: str,
    artifact_id: str,
    parameters: dict[str, Any] | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Create a Cortex analyzer job for an observable (artifact).

    Equivalent to TheHive4py: CortexEndpoint.create_analyzer_job(job).
    """
    try:
        api = _get_cortex_api()
        job: dict[str, Any] = {
            "analyzerId": analyzer_id,
            "cortexId": cortex_id,
            "artifactId": artifact_id,
        }
        if parameters is not None:
            job["parameters"] = parameters
        result = api.create_analyzer_job(job=job)  # type: ignore
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error creating analyzer job: {e!s}",
            ),
        ]


async def get_cortex_analyzer_job(
    job_id: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Get a Cortex analyzer job by id."""
    try:
        api = _get_cortex_api()
        result = api.get_analyzer_job(job_id=job_id)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error getting analyzer job: {e!s}"),
        ]


async def run_observable_analyzer(
    analyzer_id: str,
    cortex_id: str,
    observable_id: str,
    parameters: dict[str, Any] | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Convenience wrapper to run an analyzer for an observable.

    Builds and submits an analyzer job.
    """
    return await create_cortex_analyzer_job(
        analyzer_id=analyzer_id,
        cortex_id=cortex_id,
        artifact_id=observable_id,
        parameters=parameters,
    )


async def list_cortex_responders(
    entity_type: str,
    entity_id: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """List Cortex responders available for the given entity.

    entity_type typically one of: alert, case, case_artifact, task, task_log, procedure, page.
    """
    try:
        api = _get_cortex_api()
        result = api.list_responders(entity_type=entity_type, entity_id=entity_id)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error listing responders: {e!s}"),
        ]


async def create_cortex_responder_action(
    object_type: str,
    object_id: str,
    responder_id: str,
    parameters: dict[str, Any] | None = None,
    tlp: int | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute a Cortex responder action on an entity.

    Equivalent to TheHive4py: CortexEndpoint.create_responder_action(action).
    """
    try:
        api = _get_cortex_api()
        action: dict[str, Any] = {
            "objectId": object_id,
            "objectType": object_type,
            "responderId": responder_id,
        }
        if parameters is not None:
            action["parameters"] = parameters
        if tlp is not None:
            action["tlp"] = tlp
        result = api.create_responder_action(action=action)  # type: ignore
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error creating responder action: {e!s}",
            ),
        ]
