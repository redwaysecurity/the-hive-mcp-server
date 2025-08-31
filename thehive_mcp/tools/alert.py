"""
TheHive Alert Management Module

This module provides functions for managing alerts in TheHive platform through
the Model Context Protocol (MCP) server interface. It includes functionality
for retrieving, filtering, and processing alerts with various query options.

The module uses thehive4py library for API interactions and formats responses
according to MCP specifications for integration with AI assistants.
"""


import json
from typing import Any, TYPE_CHECKING

from mcp import types
from thehive_mcp.tool_wrapper import Tool

from thehive_mcp.logger import get_logger
from thehive4py.errors import TheHiveError

if TYPE_CHECKING:
    from thehive4py.endpoints import AlertEndpoint


logger = get_logger(__name__)

_alert_api = None

def _get_alert_api() -> "AlertEndpoint":
    """Get or create the alert API endpoint.

    Import of AlertEndpoint is performed lazily so that test fixtures which
    patch 'thehive4py.endpoints.AlertEndpoint'
    """
    global _alert_api
    if _alert_api is None:
        from thehive4py.endpoints import AlertEndpoint

        from thehive_mcp.clients.thehive import hive_session
        _alert_api = AlertEndpoint(hive_session)
    return _alert_api

def __getattr__(name: str) -> Any:
    if name == "alert_api":
        return _get_alert_api()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_all_functions() -> list[Tool]:
    """Return functions exposed by this module for MCP server registration."""
    return [
        Tool(
            fn=create_alert,
            name="create_alert",
            title="Create Alert",
            description="Create a new alert in TheHive.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "object",
                        "description": "Alert fields dictionary",
                        "properties": {
                            "type": {"type": "string", "description": "Alert type (required)"},
                            "source": {"type": "string", "description": "Alert source (required)"},
                            "sourceRef": {"type": "string", "description": "Source reference (required)"},
                            "title": {"type": "string", "description": "Alert title (required)"},
                            "description": {"type": "string", "description": "Alert description (required)"},
                            "severity": {"type": "integer", "description": "Alert severity (1-4)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Alert tags"},
                            "tlp": {"type": "integer", "description": "TLP level (0-4)"},
                            "pap": {"type": "integer", "description": "PAP level (0-4)"},
                        },
                    },
                },
            },
        ),
        Tool(
            fn=get_alerts,
            name="get_alerts",
            title="Get Alerts",
            description="Get all alerts with optional filtering and pagination.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filter criteria for alerts",
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
            fn=get_alert,
            name="get_alert",
            title="Get Alert",
            description="Get a single alert by ID.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "The unique identifier of the alert",
                    },
                },
                "required": ["alert_id"],
            },
        ),
        Tool(
            fn=update_alert,
            name="update_alert",
            title="Update Alert",
            description="Update an alert using fields dictionary.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert ID to update",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Fields to update",
                        "properties": {
                            "title": {"type": "string", "description": "Alert title"},
                            "description": {"type": "string", "description": "Alert description"},
                            "severity": {"type": "integer", "description": "Alert severity (1-4)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Alert tags"},
                            "status": {"type": "string", "description": "Alert status"},
                        },
                    },
                },
                "required": ["alert_id", "fields"],
            },
        ),
        Tool(
            fn=delete_alert,
            name="delete_alert",
            title="Delete Alert",
            description="Delete an alert permanently.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "The unique identifier of the alert to delete",
                    },
                },
                "required": ["alert_id"],
            },
        ),
        Tool(
            fn=bulk_update_alerts,
            name="bulk_update_alerts",
            title="Bulk Update Alerts",
            description="Update multiple alerts with same values.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of alert IDs to update",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Fields to update for all alerts",
                    },
                },
                "required": ["alert_ids", "fields"],
            },
        ),
        Tool(
            fn=bulk_delete_alerts,
            name="bulk_delete_alerts",
            title="Bulk Delete Alerts",
            description="Delete multiple alerts at once.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of alert IDs to delete",
                    },
                },
                "required": ["alert_ids"],
            },
        ),
        Tool(
            fn=count_alerts,
            name="count_alerts",
            title="Count Alerts",
            description="Count alerts matching given filters.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filter criteria dictionary with TheHive query format",
                    },
                },
            },
        ),
        Tool(
            fn=follow_alert,
            name="follow_alert",
            title="Follow Alert",
            description="Follow an alert to receive notifications.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "The alert ID to follow",
                    },
                },
                "required": ["alert_id"],
            },
        ),
        Tool(
            fn=unfollow_alert,
            name="unfollow_alert",
            title="Unfollow Alert",
            description="Unfollow an alert to stop notifications.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "The alert ID to unfollow",
                    },
                },
                "required": ["alert_id"],
            },
        ),
        Tool(
            fn=promote_alert_to_case,
            name="promote_alert_to_case",
            title="Promote Alert to Case",
            description="Promote an alert to a case for investigation.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert to promote",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Case creation fields",
                    },
                },
                "required": ["alert_id"],
            },
        ),
        Tool(
            fn=merge_alert_into_case,
            name="merge_alert_into_case",
            title="Merge Alert into Case",
            description="Merge an alert into existing case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert to merge",
                    },
                    "case_id": {
                        "type": "string",
                        "description": "Target case ID",
                    },
                },
                "required": ["alert_id", "case_id"],
            },
        ),
        Tool(
            fn=import_alert_into_case,
            name="import_alert_into_case",
            title="Import Alert into Case",
            description="Import alert data into a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Source alert",
                    },
                    "case_id": {
                        "type": "string",
                        "description": "Target case",
                    },
                },
                "required": ["alert_id", "case_id"],
            },
        ),
        Tool(
            fn=bulk_merge_alerts_into_case,
            name="bulk_merge_alerts_into_case",
            title="Bulk Merge Alerts into Case",
            description="Merge multiple alerts into one case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Target case",
                    },
                    "alert_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Alerts to merge",
                    },
                },
                "required": ["case_id", "alert_ids"],
            },
        ),
        Tool(
            fn=create_alert_observable,
            name="create_alert_observable",
            title="Create Alert Observable",
            description="Create observable in alert.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert ID",
                    },
                    "observable": {
                        "type": "object",
                        "description": "Observable fields",
                        "properties": {
                            "dataType": {"type": "string", "description": "Observable data type (required)"},
                            "data": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "array", "items": {"type": "string"}},
                                ],
                                "description": "Observable value(s) (required)",
                            },
                            "message": {"type": "string", "description": "Description or context"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Observable tags"},
                            "ioc": {"type": "boolean", "description": "Whether it's an IOC"},
                            "sighted": {"type": "boolean", "description": "Whether it has been sighted"},
                        },
                        "required": ["dataType", "data"],
                    },
                },
                "required": ["alert_id", "observable"],
            },
        ),
        Tool(
            fn=find_alert_observables,
            name="find_alert_observables",
            title="Find Alert Observables",
            description="Find observables in alert.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Alert to search",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                    },
                },
                "required": ["alert_id"],
            },
        ),
        Tool(
            fn=get_alert_similar_observables,
            name="get_alert_similar_observables",
            title="Get Alert Similar Observables",
            description="Get similar observables between alerts/cases.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "description": "Source alert",
                    },
                    "other_id": {
                        "type": "string",
                        "description": "Target alert/case ID",
                    },
                },
                "required": ["alert_id", "other_id"],
            },
        ),
    ]

async def get_alerts(
    filters: dict | None = None,
    sortby: dict | None = None,
    paginate: dict | None = None,
) -> list[types.TextContent]:
    """
    Retrieve alerts from TheHive with optional filters and pagination.

    Parameters:
    filters (dict, optional): Filter criteria for alerts
    sortby (dict, optional): Sort specification for results
    paginate (dict, optional): Pagination settings

    Example filters:
        "_or": [
            {"_eq": {"_field": "tags", "_value": "antivirus"}},
            {"_eq": {"_field": "tags", "_value": "phishing"}},
        ]
    Example sortby:
        {"_field": "createdAt", "_order": "desc"}
    Example paginate:
        {"_page": 1, "_perPage": 50}
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

        result = _get_alert_api().find(filters=_filters, sortby=_sortby, paginate=_paginate)  # type: ignore
        return [types.TextContent(type="text", text=json.dumps(item, indent=2, default=str)) for item in result]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error retrieving alerts: {e!s}")]

async def create_alert(
   fields: dict[str, Any] | None = None,
) -> list[types.TextContent]:
    """
    Create a new alert in TheHive.

    This function allows you to create a new alert by providing the necessary fields.
    The required fields are: type, source, sourceRef, title, description

    """
    try:
        required_fields = ["type", "source", "sourceRef", "title", "description"]

        data = {}

        if not fields:
            return [
                types.TextContent(
                    type="text",
                    text="Error creating alert: Missing alert data.",
                ),
            ]

        data.update(fields)

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating alert: Missing required fields: {', '.join(missing_fields)}. Required fields are: {', '.join(required_fields)}",
                ),
            ]

        result = _get_alert_api().create(alert=data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created alert: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error creating alert: {e!s}")]

async def get_alert(
    alert_id: str,
) -> list[types.TextContent]:
    """Get a single alert by ID."""
    try:

        result = _get_alert_api().get(alert_id=alert_id)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error getting alert: {e!s}")]

async def update_alert(
    alert_id: str,
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """Update an alert using fields dictionary.
    
    Args:
        alert_id: The ID of the alert to update
        fields: A dictionary containing alert update fields. Supported fields:
            - title: str - Alert title
            - description: str - Alert description
            - severity: int - Alert severity (1-4)
            - tags: List[str] - Alert tags
            - status: str - Alert status (New, InProgress, Closed, etc.)
    """
    try:


        _get_alert_api().update(alert_id=alert_id, fields=fields)  # type: ignore
        return [
            types.TextContent(
                type="text",
                text=f"Alert {alert_id} updated successfully",
            ),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error updating alert: {e!s}")]

async def delete_alert(
    alert_id: str,
) -> list[types.TextContent]:
    """Delete an alert."""
    try:

        _get_alert_api().delete(alert_id=alert_id)
        return [
            types.TextContent(
                type="text",
                text=f"Alert {alert_id} deleted successfully",
            ),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error deleting alert: {e!s}")]

async def bulk_update_alerts(
    alert_ids: list[str],
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """
        Update multiple alerts with the same values.

       Args:
           alert_ids: The IDs of the alerts to update.
           fields: The fields to update for each alert.
    """
    try:


        if not alert_ids:
            return [
                types.TextContent(
                    type="text",
                    text="No alert IDs provided for bulk update",
                ),
            ]
        if not isinstance(fields, dict) or not fields:
            return [
                types.TextContent(
                    type="text",
                    text="fields must be a non-empty dictionary",
                ),
            ]
        if not isinstance(alert_ids, list) or not all(isinstance(id, str) for id in alert_ids):
            return [
                types.TextContent(
                    type="text",
                    text="alert_ids must be a list of strings",
                ),
            ]

        _fields = {"ids": alert_ids, **fields}

        _get_alert_api().bulk_update(fields=_fields)  # type: ignore
        return [
            types.TextContent(
                type="text",
                text=f"Updated {len(alert_ids)} alerts successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error bulk updating alerts: {e!s}"),
        ]

async def bulk_delete_alerts(
    alert_ids: list[str],
) -> list[types.TextContent]:
    """Delete multiple alerts at once."""
    try:

        _get_alert_api().bulk_delete(ids=alert_ids)
        return [
            types.TextContent(
                type="text",
                text=f"Deleted {len(alert_ids)} alerts successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error bulk deleting alerts: {e!s}"),
        ]

async def count_alerts(
    filters: dict[str, Any] | None = None,
) -> list[types.TextContent]:
    """Count alerts matching the given filters."""
    try:


        # Prepare filters in TheHive query format
        query_filters = None
        if filters:
            query_filters = {"_name": "filter", **filters}

        result = _get_alert_api().count(filters=query_filters)
        return [types.TextContent(type="text", text=f"Found {result} alerts")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error counting alerts: {e!s}")]

async def follow_alert(
    alert_id: str,
) -> list[types.TextContent]:
    """Follow an alert."""
    try:

        _get_alert_api().follow(alert_id=alert_id)
        return [types.TextContent(type="text", text=f"Now following alert {alert_id}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error following alert: {e!s}")]

async def unfollow_alert(
    alert_id: str,
) -> list[types.TextContent]:
    """Unfollow an alert."""
    try:

        _get_alert_api().unfollow(alert_id=alert_id)
        return [types.TextContent(type="text", text=f"Unfollowed alert {alert_id}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error unfollowing alert: {e!s}"),
        ]

async def promote_alert_to_case(
    alert_id: str,
    fields: dict[str, Any] = {},
) -> list[types.TextContent]:
    """Promote an alert to a case."""
    try:


        result = _get_alert_api().promote_to_case(alert_id=alert_id, fields=fields)  # type: ignore
        return [
            types.TextContent(type="text", text=f"Promoted alert to case: {result}"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error promoting alert: {e!s}")]

async def merge_alert_into_case(
    alert_id: str,
    case_id: str,
) -> list[types.TextContent]:
    """Merge an alert into an existing case."""
    try:

        result = _get_alert_api().merge_into_case(alert_id=alert_id, case_id=case_id)
        return [
            types.TextContent(type="text", text=f"Merged alert into case: {result}"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error merging alert: {e!s}")]

async def import_alert_into_case(
    alert_id: str,
    case_id: str,
) -> list[types.TextContent]:
    """Import an alert into a case."""
    try:

        result = _get_alert_api().import_into_case(alert_id=alert_id, case_id=case_id)
        return [
            types.TextContent(type="text", text=f"Imported alert into case: {result}"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error importing alert: {e!s}")]

async def bulk_merge_alerts_into_case(
    case_id: str,
    alert_ids: list[str],
) -> list[types.TextContent]:
    """Merge multiple alerts into a case."""
    try:

        result = _get_alert_api().bulk_merge_into_case(case_id=case_id, alert_ids=alert_ids)
        return [
            types.TextContent(
                type="text",
                text=f"Merged {len(alert_ids)} alerts into case: {result}",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error bulk merging alerts: {e!s}"),
        ]

async def create_alert_observable(
    alert_id: str,
    observable: dict[str, Any],
) -> list[types.TextContent]:
    """
    Create an observable in an alert.

    Args:
        alert_id: The ID of the alert.
        observable: A dictionary with observable fields. Valid keys:
            - dataType (str, required): The type of the observable (e.g., 'ip', 'domain', etc.)
            - data (str | list[str], required): The observable value(s)
            - message (str, optional): Description or context for the observable
            - tags (list[str], optional): Tags for the observable
            - ioc (bool, optional): Whether the observable is an IOC
            - sighted (bool, optional): Whether the observable has been sighted
            - sightedAt (str, optional): Timestamp when the observable was sighted
            - ignoreSimilarity (bool, optional): Whether to ignore similarity checks
            - isZip (bool, optional): Whether the observable is a ZIP file
            - zipPassword (str, optional): Password for the ZIP file if applicable
    """
    try:

        valid_keys = {"dataType", "data",  "message", "startDate", "endDate", "tlp", "pap", "tags", "ioc", "sighted", "sightedAt", "ignoreSimilarity", "isZip", "zipPassword"}

        obs = {k: v for k, v in observable.items() if k in valid_keys}

        if "dataType" not in obs or "data" not in obs:
            return [
                types.TextContent(
                    type="text",
                    text="Missing required keys: 'dataType' and 'data' are required in observable.",
                ),
            ]

        result = _get_alert_api().create_observable(alert_id=alert_id, observable=obs)  # type: ignore
        return [types.TextContent(type="text", text=f"Created observable: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error creating observable: {e!s}"),
        ]

async def find_alert_observables(
    alert_id: str,
    limit: int | None = None,
) -> list[types.TextContent]:
    """Find observables in an alert."""
    try:

        result = _get_alert_api().find_observables(alert_id=alert_id)
        return [types.TextContent(type="text", text=f"Alert observables: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error finding observables: {e!s}"),
        ]

async def get_alert_similar_observables(
    alert_id: str,
    other_id: str,
) -> list[types.TextContent]:
    """Get similar observables between alerts/cases."""
    try:

        result = _get_alert_api().get_similar_observables(
            alert_id=alert_id,
            alert_or_case_id=other_id,
        )
        return [types.TextContent(type="text", text=f"Similar observables: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error getting similar observables: {e!s}",
            ),
        ]
