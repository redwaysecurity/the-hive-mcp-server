"""TheHive Case Management for MCP Server."""

import json
from typing import Any, TYPE_CHECKING

from thehive_mcp.tool_wrapper import Tool
from mcp import types
from thehive4py.errors import TheHiveError
from thehive4py.types.case import InputUpdateCase

from thehive_mcp.logger import get_logger

if TYPE_CHECKING:
    from thehive4py.endpoints import CaseEndpoint

logger = get_logger(__name__)

_case_api = None


def _get_case_api() -> "CaseEndpoint":
    """Get or create the case API endpoint."""
    from thehive4py.endpoints import CaseEndpoint

    from thehive_mcp.clients.thehive import hive_session
    global _case_api
    if _case_api is None:
        # Local import to honor any active patches
        _case_api = CaseEndpoint(hive_session)
    return _case_api

def __getattr__(name: str) -> Any:
    if name == "case_api":
        return _get_case_api()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def get_all_functions() -> list[Tool]:
    """Return functions exposed by this module for MCP server registration."""
    return [
        # Case CRUD operations
        Tool(
            fn=create_case,
            name="create_case",
            title="Create Case",
            description="Create a new case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "object",
                        "description": "Case fields dictionary",
                        "properties": {
                            "title": {"type": "string", "description": "Case title (required)"},
                            "description": {"type": "string", "description": "Case description (required)"},
                            "severity": {"type": "integer", "description": "Case severity (1-4)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Case tags"},
                            "customFields": {"type": "object", "description": "Custom fields"},
                            "flag": {"type": "boolean", "description": "Flag status"},
                            "pap": {"type": "integer", "description": "PAP level (0-3)"},
                            "tlp": {"type": "integer", "description": "TLP level (0-3)"},
                        },
                        "required": ["title", "description"],
                    },
                },
                "required": ["fields"],
            },
        ),
        Tool(
            fn=get_cases,
            name="get_cases",
            title="Get Cases",
            description="Get all cases with optional filtering and pagination.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filter criteria for cases",
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
            fn=get_case,
            name="get_case",
            title="Get Case",
            description="Get a single case by ID.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The unique identifier of the case",
                    },
                },
                "required": ["case_id"],
            },
        ),
        Tool(
            fn=update_case,
            name="update_case",
            title="Update Case",
            description="Update a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID to update",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Fields to update",
                        "properties": {
                            "title": {"type": "string", "description": "Case title"},
                            "description": {"type": "string", "description": "Case description"},
                            "severity": {"type": "integer", "description": "Case severity (1-4)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Case tags"},
                            "status": {"type": "string", "description": "Case status"},
                        },
                    },
                },
                "required": ["case_id", "fields"],
            },
        ),
        Tool(
            fn=delete_case,
            name="delete_case",
            title="Delete Case",
            description="Delete a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The unique identifier of the case to delete",
                    },
                },
                "required": ["case_id"],
            },
        ),
        Tool(
            fn=bulk_update_cases,
            name="bulk_update_cases",
            title="Bulk Update Cases",
            description="Update multiple cases.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of case IDs",
                    },
                    "title": {"type": "string", "description": "Title to update"},
                    "description": {"type": "string", "description": "Description to update"},
                    "severity": {"type": "integer", "description": "Severity to update"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags to update"},
                    "status": {"type": "string", "description": "Status to update"},
                },
                "required": ["case_ids"],
            },
        ),
        Tool(
            fn=count_cases,
            name="count_cases",
            title="Count Cases",
            description="Count cases matching given filters.",
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
            fn=close_case,
            name="close_case",
            title="Close Case",
            description="Close a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The ID of the case to close",
                    },
                    "status": {
                        "type": "string",
                        "description": "The status to set when closing. Typically 'FalsePositive, TruePositive, or Duplicated",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Closure summary",
                    },
                    "impact_status": {
                        "type": "string",
                        "description": "Impact status for closure",
                        "default": "NotApplicable",
                    },
                },
                "required": ["case_id", "status"],
            },
        ),
        # Case merging
        Tool(
            fn=merge_cases,
            name="merge_cases",
            title="Merge Cases",
            description="Merge two or more cases together.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of case IDs to merge",
                    },
                },
                "required": ["case_ids"],
            },
        ),
        # Case observables
        Tool(
            fn=create_case_observable,
            name="create_case_observable",
            title="Create Case Observable",
            description="Create observable in case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                    "data_type": {
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
                },
                "required": ["case_id", "data_type", "data"],
            },
        ),
        Tool(
            fn=find_case_observables,
            name="find_case_observables",
            title="Find Case Observables",
            description="Find observables in case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                    },
                },
                "required": ["case_id"],
            },
        ),
        Tool(
            fn=get_case_similar_observables,
            name="get_case_similar_observables",
            title="Get Case Similar Observables",
            description="Get similar observables.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Source case",
                    },
                    "other_id": {
                        "type": "string",
                        "description": "Target case/alert ID",
                    },
                },
                "required": ["case_id", "other_id"],
            },
        ),
        # Case comments
        Tool(
            fn=find_case_comments,
            name="find_case_comments",
            title="Find Case Comments",
            description="Find comments in case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                },
                "required": ["case_id"],
            },
        ),
        # Case tasks
        Tool(
            fn=create_case_task,
            name="create_case_task",
            title="Create Case Task",
            description="Create a task in a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The ID of the case",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Task fields",
                        "properties": {
                            "title": {"type": "string", "description": "Task title (required)"},
                            "description": {"type": "string", "description": "Task description (required)"},
                        },
                        "required": ["title", "description"],
                    },
                },
                "required": ["case_id", "fields"],
            },
        ),
        Tool(
            fn=find_case_tasks,
            name="find_case_tasks",
            title="Find Case Tasks",
            description="Find tasks in a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The ID of the case",
                    },
                },
                "required": ["case_id"],
            },
        ),
        # Case procedures
        Tool(
            fn=create_case_procedure,
            name="create_case_procedure",
            title="Create Case Procedure",
            description="Create a procedure in a case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "The ID of the case",
                    },
                    "procedure": {
                        "type": "object",
                        "description": "Procedure details",
                        "properties": {
                            "occurDate": {"type": "integer", "description": "Occurrence date (required)"},
                            "patternId": {"type": "string", "description": "Pattern ID (required)"},
                            "tactic": {"type": "string", "description": "Tactic"},
                            "description": {"type": "string", "description": "Description"},
                        },
                        "required": ["occurDate", "patternId"],
                    },
                },
                "required": ["case_id", "procedure"],
            },
        ),
        Tool(
            fn=find_case_procedures,
            name="find_case_procedures",
            title="Find Case Procedures",
            description="Find procedures in case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                },
                "required": ["case_id"],
            },
        ),
        # Case attachments
        Tool(
            fn=add_case_attachment,
            name="add_case_attachment",
            title="Add Case Attachment",
            description="Add attachment to case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                    "attachment_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to attachments",
                    },
                    "can_rename": {
                        "type": "boolean",
                        "description": "Whether files can be renamed",
                        "default": True,
                    },
                },
                "required": ["case_id", "attachment_paths"],
            },
        ),
        Tool(
            fn=delete_case_attachment,
            name="delete_case_attachment",
            title="Delete Case Attachment",
            description="Delete case attachment.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "Attachment ID",
                    },
                },
                "required": ["case_id", "attachment_id"],
            },
        ),
        Tool(
            fn=download_case_attachment,
            name="download_case_attachment",
            title="Download Case Attachment",
            description="Download case attachment.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                    "attachment_id": {
                        "type": "string",
                        "description": "Attachment ID",
                    },
                    "attachment_path": {
                        "type": "string",
                        "description": "Path to save attachment",
                    },
                },
                "required": ["case_id", "attachment_id", "attachment_path"],
            },
        ),
        Tool(
            fn=find_case_attachments,
            name="find_case_attachments",
            title="Find Case Attachments",
            description="Find case attachments.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                },
                "required": ["case_id"],
            },
        ),
        # Case pages
        Tool(
            fn=create_case_page,
            name="create_case_page",
            title="Create Case Page",
            description="Create page in case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                    "title": {
                        "type": "string",
                        "description": "Page title",
                    },
                    "content": {
                        "type": "string",
                        "description": "Page content",
                    },
                    "category": {
                        "type": "string",
                        "description": "Page category",
                    },
                    "order": {
                        "type": "integer",
                        "description": "Page order",
                    },
                },
                "required": ["case_id", "title", "content"],
            },
        ),
        Tool(
            fn=find_case_pages,
            name="find_case_pages",
            title="Find Case Pages",
            description="Find pages in case.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID",
                    },
                },
                "required": ["case_id"],
            },
        ),
    ]

async def get_cases(
    filters: dict | None = None,
    sortby: dict | None = None,
    paginate: dict | None = None,
) -> list[types.TextContent]:
    """
    Retrieve cases from TheHive with optional filters, sorting, and pagination.

    This asynchronous function queries TheHive for case records, allowing the caller to specify
    optional filtering, sorting, and pagination parameters. The results are returned as a list
    of content objects suitable for further processing or display.

    Args:
        filters (dict | None): Optional dictionary specifying filter criteria for the cases.
        sortby (dict | None): Optional dictionary specifying sorting options for the results.
        paginate (dict | None): Optional dictionary specifying pagination options (e.g., page number, page size).
    Returns:
        list[types.TextContent]:
            A list of content objects representing the retrieved cases. If an error occurs,
            a single TextContent object describing the error is returned.
    Raises:
        This function handles all exceptions internally and logs errors. No exceptions are propagated.

    """
    logger.debug(f"get_cases called with filters={filters}")
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

        logger.debug(f"Calling {__name__} with filters: {_filters}")
        result = _get_case_api().find(filters=_filters, sortby=_sortby, paginate=_paginate)  # type: ignore
        # logger.debug(f"API find result: {result}")
        return [types.TextContent(type="text", text=json.dumps(item, indent=2, default=str)) for item in result]
    except TheHiveError as e:
        logger.error(f"Error in get_cases: {e}", exc_info=True)
        return [
            types.TextContent(type="text", text=f"Error retrieving cases: {e!s}"),
        ]


async def create_case(
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """Create a new case in TheHive.
    
    Args:
        fields: A dictionary containing case creation fields. Required fields:
            - title: str - Case title
            - description: str - Case description
        Optional fields:
            - severity: int - Case severity (1-4)
            - tags: List[str] - Case tags
            - customFields: dict - Custom fields
            - flag: bool - Flag status
            - pap: int - Permissible Actions Protocol (0-3)
            - tlp: int - Traffic Light Protocol (0-3)
    """
    try:


        # Validate required fields
        if "title" not in fields:
            return [types.TextContent(type="text", text="Error: title is required")]
        if "description" not in fields:
            return [types.TextContent(type="text", text="Error: description is required")]

        case_data = fields.copy()

        result = _get_case_api().create(case=case_data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created case: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error creating case: {e!s}")]


async def get_case(
    case_id: str,
) -> list[types.TextContent]:
    """Get a single case by ID."""
    logger.debug(f"get_case called with case_id={case_id}")
    try:
        logger.debug(f"Calling _get_case_api().get with case_id: {case_id}")
        result = _get_case_api().get(case_id=case_id)
        logger.debug(f"API get result: {result}")
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except TheHiveError as e:
        logger.error(f"Error in get_case: {e}", exc_info=True)
        return [types.TextContent(type="text", text=f"Error getting case: {e!s}")]


async def update_case(
    case_id: str,
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """Update a case using InputUpdateCase fields.

    Args:
        case_id: The ID of the case to update
        fields: A dictionary containing case update fields. Supported fields:
            - title: str - Case title
            - description: str - Case description
            - severity: int - Case severity (1-4)
            - tags: List[str] - Case tags
            - status: str - Case status (New, InProgress, Resolved, etc.)
            - flag: bool - Flag status
            - tlp: int - Traffic Light Protocol (0-3)
            - pap: int - Permissible Actions Protocol (0-3)
            - summary: str - Case summary
            - assignee: str - Assigned user
            - impactStatus: str - Impact status
            - startDate: int - Start date (timestamp)
            - endDate: int - End date (timestamp)
            - addTags: List[str] - Tags to add
            - removeTags: List[str] - Tags to remove
    """
    try:


        # Cast to InputUpdateCase type for type safety
        update_fields: InputUpdateCase = fields  # type: ignore

        _get_case_api().update(case_id=case_id, fields=update_fields)
        return [
            types.TextContent(type="text", text=f"Case {case_id} updated successfully"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error updating case: {e!s}")]


async def delete_case(
    case_id: str,
) -> list[types.TextContent]:
    """Delete a case."""
    try:

        _get_case_api().delete(case_id=case_id)
        return [
            types.TextContent(type="text", text=f"Case {case_id} deleted successfully"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error deleting case: {e!s}")]


async def bulk_update_cases(
    case_ids: list[str],
    title: str | None = None,
    description: str | None = None,
    severity: int | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
) -> list[types.TextContent]:
    """Update multiple cases at once."""
    try:

        fields: dict[str, Any] = {"ids": case_ids}

        if title is not None:
            fields["title"] = [title]
        if description is not None:
            fields["description"] = [description]
        if severity is not None:
            fields["severity"] = [severity]
        if tags is not None:
            fields["tags"] = tags  # already a list
        if status is not None:
            fields["status"] = [status]

        _get_case_api().bulk_update(fields=fields)  # type: ignore
        return [
            types.TextContent(
                type="text",
                text=f"Updated {len(case_ids)} cases successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error bulk updating cases: {e!s}"),
        ]


async def count_cases(
    filters: dict[str, Any] | None = None,
) -> list[types.TextContent]:
    """Count cases matching the given filters."""
    try:


        # Prepare filters in TheHive query format
        query_filters = None
        if filters:
            query_filters = {"_name": "filter", **filters}

        result = _get_case_api().count(filters=query_filters)
        return [types.TextContent(type="text", text=f"Found {result} cases")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error counting cases: {e!s}")]


async def close_case(
    case_id: str,
    status: str,
    summary: str | None = None,
    impact_status: str | None = "NotApplicable",
) -> list[types.TextContent]:
    """
    Close a case.
    Args:
        case_id: The id of the case.
        status: The status to close the case with.
        summary: The closure summary of the case.
        impact_status: The impact status of the case.
    """
    try:


        _get_case_api().close(
            case_id=case_id,
            status=status,  # type: ignore
            summary=summary,  # type: ignore
            impact_status=impact_status,  # type: ignore
        )
        return [types.TextContent(type="text", text=f"Case {case_id} closed")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error closing case: {e!s}")]

async def merge_cases(
    case_ids: list[str],
) -> list[types.TextContent]:
    """Merge two cases together."""
    try:
        result = _get_case_api().merge(case_ids=case_ids)
        return [types.TextContent(type="text", text=f"Merged cases: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error merging cases: {e!s}")]


async def create_case_observable(
    case_id: str,
    data_type: str,
    data: str | list[str],
    message: str | None = None,
    tags: list[str] | None = None,
    ioc: bool | None = None,
) -> list[types.TextContent]:
    """Create an observable in a case."""
    try:

        observable = {
            "dataType": data_type,
            "data": data,
        }

        if message is not None:
            observable["message"] = message
        if tags is not None:
            observable["tags"] = tags
        if ioc is not None:
            observable["ioc"] = ioc  # type: ignore

        result = _get_case_api().create_observable(case_id=case_id, observable=observable)  # type: ignore
        return [types.TextContent(type="text", text=f"Created observables: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error creating observable: {e!s}"),
        ]


async def find_case_observables(
    case_id: str,
    limit: int | None = None,
) -> list[types.TextContent]:
    """Find observables in a case."""
    try:

        result = _get_case_api().find_observables(case_id=case_id)
        return [types.TextContent(type="text", text=f"Case observables: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error finding observables: {e!s}"),
        ]


async def get_case_similar_observables(
    case_id: str,
    other_id: str,
) -> list[types.TextContent]:
    """Get similar observables between cases/alerts."""
    try:

        result = _get_case_api().get_similar_observables(case_id=case_id, alert_or_case_id=other_id)
        return [types.TextContent(type="text", text=f"Similar observables: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error getting similar observables: {e!s}",
            ),
        ]


async def find_case_comments(
    case_id: str,
) -> list[types.TextContent]:
    """Find comments in a case."""
    try:

        result = _get_case_api().find_comments(case_id=case_id)
        return [types.TextContent(type="text", text=f"Case comments: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error finding comments: {e!s}"),
        ]


async def create_case_task(
    case_id: str,
    fields: dict[str, Any],
) -> list[types.TextContent]:
    """
    Create a task in a case.

    Args:
        case_id (str): The ID of the case to create the task in.
        fields (dict[str, Any]): The fields for the task.

    """
    try:

        data = {}

        if fields:
            data.update(fields)

        required_fields = ["title","description"]

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating alert: Missing required fields: {', '.join(missing_fields)}. Required fields are: {', '.join(required_fields)}",
                ),
            ]



        result = _get_case_api().create_task(case_id=case_id, task=data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created task: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error creating task: {e!s}")]

async def find_case_tasks(
    case_id: str,
) -> list[types.TextContent]:
    """Find tasks in a case."""
    try:

        result = _get_case_api().find_tasks(case_id=case_id)
        return [types.TextContent(type="text", text=f"Case tasks: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error finding tasks: {e!s}")]


async def create_case_procedure(
    case_id: str,
    procedure: dict[str, Any],
) -> list[types.TextContent]:
    """
    Create a procedure in a case.
    Args:
        case_id (str): The ID of the case to create the procedure in.
        procedure (dict[str, Any]): The procedure details.
            occurDate: int
            patternId: str
            tactic: NotRequired[str]
            description: NotRequired[str]
    """
    try:
        required_fields = ["occurDate", "patternId"]

        data = {}

        if not procedure:
            return [
                types.TextContent(
                    type="text",
                    text="Error creating procedure: Missing procedure data.",
                ),
            ]

        data.update(procedure)

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating procedure: Missing required fields: {', '.join(missing_fields)}. Required fields are: {', '.join(required_fields)}",
                ),
            ]

        result = _get_case_api().create_procedure(case_id=case_id, procedure=data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created procedure: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error creating procedure: {e!s}"),
        ]


async def find_case_procedures(
    case_id: str,
) -> list[types.TextContent]:
    """Find procedures in a case."""
    try:
        result = _get_case_api().find_procedures(case_id=case_id)
        return [types.TextContent(type="text", text=f"Case procedures: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error finding procedures: {e!s}"),
        ]


async def add_case_attachment(
    case_id: str,
    attachment_paths: list[str],
    can_rename: bool = True,
) -> list[types.TextContent]:
    """Add attachments to a case."""
    try:

        result = _get_case_api().add_attachment(
            case_id=case_id,
            attachment_paths=attachment_paths,
        )
        return [types.TextContent(type="text", text=f"Added attachments: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error adding attachments: {e!s}"),
        ]


async def delete_case_attachment(
    case_id: str,
    attachment_id: str,
) -> list[types.TextContent]:
    """Delete a case attachment."""
    try:

        _get_case_api().delete_attachment(case_id=case_id, attachment_id=attachment_id)
        return [
            types.TextContent(type="text", text=f"Deleted attachment {attachment_id}"),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error deleting attachment: {e!s}"),
        ]


async def download_case_attachment(
    case_id: str,
    attachment_id: str,
    attachment_path: str,
) -> list[types.TextContent]:
    """Download a case attachment."""
    try:

        _get_case_api().download_attachment(
            case_id=case_id,
            attachment_id=attachment_id,
            attachment_path=attachment_path,
        )
        return [
            types.TextContent(
                type="text",
                text=f"Downloaded attachment to {attachment_path}",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error downloading attachment: {e!s}",
            ),
        ]


async def find_case_attachments(
    case_id: str,
) -> list[types.TextContent]:
    """Find attachments in a case."""
    try:

        result = _get_case_api().find_attachments(case_id=case_id)
        return [types.TextContent(type="text", text=f"Case attachments: {result}")]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error finding attachments: {e!s}"),
        ]


async def create_case_page(
    case_id: str,
    title: str,
    content: str,
    category: str | None = None,
    order: int | None = None,
) -> list[types.TextContent]:
    """Create a page in a case."""
    try:

        page = {
            "title": title,
            "content": content,
        }

        if category is not None:
            page["category"] = category
        if order is not None:
            page["order"] = str(order)  # Convert int to str

        result = _get_case_api().create_page(case_id=case_id, page=page)  # type: ignore
        return [types.TextContent(type="text", text=f"Created page: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error creating page: {e!s}")]


async def find_case_pages(
    case_id: str,
) -> list[types.TextContent]:
    """Find pages in a case."""
    try:

        result = _get_case_api().find_pages(case_id=case_id)
        return [types.TextContent(type="text", text=f"Case pages: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error finding pages: {e!s}")]


def search_cases(api: Any, message: Any) -> Any:
    """Compatibility function for tests; delegates to API client's case.find."""
    query = message.content.get("query") if hasattr(message, "content") else None
    return _get_case_api().find(filters=query if query is not None else None)  # Fixed attribute access
