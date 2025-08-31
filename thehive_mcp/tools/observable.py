"""TheHive Observable Management for MCP Server."""

import json
from typing import Any, TYPE_CHECKING

from thehive_mcp.tool_wrapper import Tool
from mcp import types

from thehive_mcp.logger import get_logger
from thehive4py.errors import TheHiveError

if TYPE_CHECKING:
    from thehive4py.endpoints import ObservableEndpoint


logger = get_logger(__name__)

_observable_api = None


def _get_observable_api() -> "ObservableEndpoint":
    """Get or create the observable API endpoint.
    
    Import performed lazily to honor any active patches.
    """
    from thehive4py.endpoints import ObservableEndpoint

    from thehive_mcp.clients.thehive import hive_session
    global _observable_api
    if _observable_api is None:
        _observable_api = ObservableEndpoint(hive_session)
    return _observable_api

# For direct access and monkey-patching in tests
def __getattr__(name: str) -> Any:
    if name == "observable_api":
        return _get_observable_api()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_all_functions() -> list[Tool]:
    """Return functions exposed by this module for MCP server registration."""
    return [
        Tool(
            fn=create_observable_in_case,
            name="create_observable_in_case",
            title="Create Observable in Case",
            description="Create a new observable in a specific case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID to create observable in",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Observable fields",
                        "properties": {
                            "dataType": {
                                "type": "string",
                                "description": "Observable data type",
                            },
                            "data": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}},
                                ],
                                "description": "Observable value(s)",
                            },
                            "message": {
                                "type": "string",
                                "description": "Description or context",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Observable tags",
                            },
                            "ioc": {
                                "type": "boolean",
                                "description": "Whether it's an IOC",
                            },
                            "sighted": {
                                "type": "boolean",
                                "description": "Whether it has been sighted",
                            },
                        },
                        "required": ["dataType", "data"],
                    },
                },
                "required": ["case_id", "fields"],
            },
        ),
        Tool(
            fn=create_observable_in_alert,
            name="create_observable_in_alert",
            title="Create Observable in Alert",
            description="Create a new observable in a specific alert.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "object",
                        "description": "Observable fields",
                        "properties": {
                            "dataType": {
                                "type": "string",
                                "description": "Observable data type",
                            },
                            "data": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}},
                                ],
                                "description": "Observable value(s)",
                            },
                            "message": {
                                "type": "string",
                                "description": "Description or context",
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Observable tags",
                            },
                            "ioc": {
                                "type": "boolean",
                                "description": "Whether it's an IOC",
                            },
                            "sighted": {
                                "type": "boolean",
                                "description": "Whether it has been sighted",
                            },
                        },
                        "required": ["dataType", "data"],
                    },
                },
                "required": ["fields"],
            },
        ),
        Tool(
            fn=get_observables,
            name="get_observables",
            title="Get Observables",
            description="Get all observables with optional filters.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filter criteria for observables",
                    },
                    "sortby": {
                        "type": "object",
                        "description": "Sort specification for results",
                    },
                    "paginate": {
                        "type": "object",
                        "description": "Pagination settings",
                    },
                },
            },
        ),
        Tool(
            fn=get_observable,
            name="get_observable",
            title="Get Observable",
            description="Get a single observable by ID.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_id": {
                        "type": "string",
                        "description": "The unique identifier of the observable",
                    },
                },
                "required": ["observable_id"],
            },
        ),
        Tool(
            fn=update_observable,
            name="update_observable",
            title="Update Observable",
            description="Update an observable.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_id": {
                        "type": "string",
                        "description": "Observable ID to update",
                    },
                    "message": {
                        "type": "string",
                        "description": "Updated message",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Updated tags",
                    },
                    "ioc": {
                        "type": "boolean",
                        "description": "Whether it's an IOC",
                    },
                    "sighted": {
                        "type": "boolean",
                        "description": "Whether it has been sighted",
                    },
                },
                "required": ["observable_id"],
            },
        ),
        Tool(
            fn=delete_observable,
            name="delete_observable",
            title="Delete Observable",
            description="Delete an observable.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_id": {
                        "type": "string",
                        "description": "The unique identifier of the observable to delete",
                    },
                },
                "required": ["observable_id"],
            },
        ),
        Tool(
            fn=bulk_update_observables,
            name="bulk_update_observables",
            title="Bulk Update Observables",
            description="Update multiple observables.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of observable IDs",
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to update",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags to update",
                    },
                    "ioc": {
                        "type": "boolean",
                        "description": "IOC status to update",
                    },
                    "sighted": {
                        "type": "boolean",
                        "description": "Sighted status to update",
                    },
                },
                "required": ["observable_ids"],
            },
        ),
        Tool(
            fn=bulk_delete_observables,
            name="bulk_delete_observables",
            title="Bulk Delete Observables",
            description="Delete multiple observables.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of observable IDs to delete",
                    },
                },
                "required": ["observable_ids"],
            },
        ),
        Tool(
            fn=count_observables,
            name="count_observables",
            title="Count Observables",
            description="Count observables matching filters.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "description": "Filter by data type",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags",
                    },
                },
            },
        ),
        # Observable sharing
        Tool(
            fn=share_observable,
            name="share_observable",
            title="Share Observable",
            description="Share an observable.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_id": {
                        "type": "string",
                        "description": "Observable ID",
                    },
                    "organizations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Organizations to share with",
                    },
                },
                "required": ["observable_id", "organizations"],
            },
        ),
        Tool(
            fn=unshare_observable,
            name="unshare_observable",
            title="Unshare Observable",
            description="Unshare an observable.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "observable_id": {
                        "type": "string",
                        "description": "Observable ID",
                    },
                    "organizations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Organizations to unshare from",
                    },
                },
                "required": ["observable_id", "organizations"],
            },
        ),
    ]

async def get_observables(
    filters: dict | None = None,
    sortby: dict | None = None,
    paginate: dict | None = None,
) -> list[types.TextContent]:
    """
    Retrieve observables from TheHive with optional filters and pagination.

    """
    try:
        _filters = None
        _sortby = None
        _paginate = None

        if filters:
            _filters = {"_name": "filter", **filters}
        if sortby:
            _sortby = {"_name": "sort", **sortby}
        if paginate:
            _paginate = {"_name": "page", **paginate}

        result = _get_observable_api().find(filters=_filters, sortby=_sortby, paginate=_paginate)  # type: ignore
        return [types.TextContent(type="text", text=json.dumps(item, indent=2, default=str)) for item in result]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error retrieving observables: {e!s}",
            ),
        ]

async def create_observable_in_case(
    case_id: str,
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """Create a new observable in a case in TheHive."""
    try:
        required_fields = ["dataType", "data"]
        data = {}

        if not fields:
            return [
                types.TextContent(
                    type="text",
                    text="Error creating observable: Missing observable data.",
                ),
            ]

        data.update(fields)

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating observable: Missing required fields: {', '.join(missing_fields)}. Required fields are: {', '.join(required_fields)}",
                ),
            ]

        result = _get_observable_api().create_in_case(case_id=case_id, observable=data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created observable: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error creating observable: {e!s}"),
        ]


async def create_observable_in_alert(
    alert_id: str,
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """Create a new observable in an alert in TheHive."""
    try:
        required_fields = ["dataType", "data"]
        data = {}

        if not fields:
            return [
                types.TextContent(
                    type="text",
                    text="Error creating observable: Missing observable data.",
                ),
            ]

        data.update(fields)

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating observable: Missing required fields: {', '.join(missing_fields)}. Required fields are: {', '.join(required_fields)}",
                ),
            ]

        result = _get_observable_api().create_in_alert(alert_id=alert_id, observable=data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created observable: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error creating observable: {e!s}"),
        ]


async def get_observable(
    observable_id: str,
) -> list[types.TextContent]:
    """Get a single observable by ID."""
    try:
        api = _get_observable_api()
        result = api.get(observable_id=observable_id)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error getting observable: {e!s}"),
        ]


async def update_observable(
    observable_id: str,
    message: str | None = None,
    tags: list[str] | None = None,
    ioc: bool | None = None,
    sighted: bool | None = None,
) -> list[types.TextContent]:
    """Update an observable."""
    try:
        api = _get_observable_api()
        fields: dict[str, Any] = {}

        if message is not None:
            fields["message"] = message
        if tags is not None:
            fields["tags"] = tags
        if ioc is not None:
            fields["ioc"] = ioc
        if sighted is not None:
            fields["sighted"] = sighted

        api.update(observable_id=observable_id, fields=fields)  # type: ignore
        return [
            types.TextContent(
                type="text",
                text=f"Observable {observable_id} updated successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error updating observable: {e!s}"),
        ]


async def delete_observable(
    observable_id: str,
) -> list[types.TextContent]:
    """Delete an observable."""
    try:
        api = _get_observable_api()
        api.delete(observable_id=observable_id)
        return [
            types.TextContent(
                type="text",
                text=f"Observable {observable_id} deleted successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error deleting observable: {e!s}"),
        ]

async def bulk_update_observables(
    observable_ids: list[str],
    message: str | None = None,
    tags: list[str] | None = None,
    ioc: bool | None = None,
    sighted: bool | None = None,
) -> list[types.TextContent]:
    """Update multiple observables at once."""
    try:
        api = _get_observable_api()
        fields: dict[str, Any] = {"ids": observable_ids}

        if message is not None:
            fields["message"] = [message]
        if tags is not None:
            fields["tags"] = tags  # already a list
        if ioc is not None:
            fields["ioc"] = [ioc]
        if sighted is not None:
            fields["sighted"] = [sighted]

        api.bulk_update(fields=fields)  # type: ignore
        return [
            types.TextContent(
                type="text",
                text=f"Updated {len(observable_ids)} observables successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error bulk updating observables: {e!s}",
            ),
        ]


async def bulk_delete_observables(
    observable_ids: list[str],
) -> list[types.TextContent]:
    """Delete multiple observables at once."""
    try:
        deleted_count = 0
        errors = []

        for obs_id in observable_ids:
            try:
                _get_observable_api().delete(observable_id=obs_id)
                deleted_count += 1
            except TheHiveError as e:
                errors.append(f"Failed to delete {obs_id}: {e!s}")

        if errors:
            return [
                types.TextContent(
                    type="text",
                    text=f"Deleted {deleted_count} observables successfully. Errors: {'; '.join(errors)}",
                ),
            ]
        return [
            types.TextContent(
                type="text",
                text=f"Deleted {deleted_count} observables successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error bulk deleting observables: {e!s}",
            ),
        ]


async def count_observables(
    data_type: str | None = None,
    tags: list[str] | None = None,
) -> list[types.TextContent]:
    """Count observables matching the given filters."""
    try:
        api = _get_observable_api()
        filters = {}

        if data_type is not None:
            filters["dataType"] = data_type
        if tags is not None:
            filters["tags"] = tags  # type: ignore

        result = api.count(filters=filters if filters else None)
        return [types.TextContent(type="text", text=f"Found {result} observables")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error counting observables: {e!s}"),
        ]

async def share_observable(
    observable_id: str,
    organizations: list[str],
) -> list[types.TextContent]:
    """Share an observable with organizations."""
    try:
        api = _get_observable_api()
        api.share(observable_id=observable_id, organisations=organizations)
        return [
            types.TextContent(
                type="text",
                text=f"Observable {observable_id} shared with {len(organizations)} organizations",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error sharing observable: {e!s}"),
        ]


async def unshare_observable(
    observable_id: str,
    organizations: list[str],
) -> list[types.TextContent]:
    """Unshare an observable from organizations."""
    try:
        api = _get_observable_api()
        api.unshare(observable_id=observable_id, organisations=organizations)
        return [
            types.TextContent(
                type="text",
                text=f"Observable {observable_id} unshared from {len(organizations)} organizations",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error unsharing observable: {e!s}"),
        ]
