"""TheHive Task Management for MCP Server."""

import json
from typing import TYPE_CHECKING, Any

from thehive_mcp.tool_wrapper import Tool
from mcp import types
from thehive4py.errors import TheHiveError

from thehive_mcp.logger import get_logger

if TYPE_CHECKING:
    from thehive4py.endpoints import TaskEndpoint, TaskLogEndpoint

logger = get_logger(__name__)

_task_api = None
_task_log_api = None

def _get_task_api() -> "TaskEndpoint":
    """Get or create the task API endpoint."""
    from thehive4py.endpoints import TaskEndpoint

    from thehive_mcp.clients.thehive import hive_session
    global _task_api
    if _task_api is None:
        _task_api = TaskEndpoint(hive_session)
    return _task_api

def _get_task_log_api() -> "TaskLogEndpoint":
    """Get or create the task log API endpoint."""
    from thehive4py.endpoints import TaskLogEndpoint
    from thehive_mcp.clients.thehive import hive_session

    global _task_log_api
    if _task_log_api is None:
        _task_log_api = TaskLogEndpoint(hive_session)
    return _task_log_api


# For direct access and monkey-patching in tests
def __getattr__(name: str) -> Any:
    if name == "task_api":
        return _get_task_api()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_all_functions() -> list[Tool]:
    """Return functions exposed by this module for MCP server registration."""
    return [
        # Task CRUD operations
        Tool(
            fn=create_task,
            name="create_task",
            title="Create Task",
            description="Create a new task.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "case_id": {
                        "type": "string",
                        "description": "Case ID to create task in",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Task fields",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (required)",
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description",
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Assigned user",
                            },
                            "flag": {
                                "type": "boolean",
                                "description": "Flag status",
                            },
                            "order": {
                                "type": "integer",
                                "description": "Task order",
                            },
                            "status": {
                                "type": "string",
                                "description": "Task status",
                            },
                        },
                        "required": ["title"],
                    },
                },
                "required": ["case_id", "fields"],
            },
        ),
        Tool(
            fn=get_tasks,
            name="get_tasks",
            title="Get Tasks",
            description="Get all tasks with optional filters.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": 'Filter criteria for tasks. Example: {"_or": [{"_eq": {"_field": "title", "_value": "Test 1"}}, {"_eq": {"_field": "title", "_value": "Test 2"}}]}',
                    },
                    "sortby": {
                        "type": "object",
                        "description": 'Sort specification for results. Example: {"_fields": [{"_createdAt": "asc"}]}',
                    },
                    "paginate": {
                        "type": "object",
                        "description": 'Pagination settings. Example: {"from": 0, "to": 10, "extraData": []}',
                    },
                },
            },
        ),
        Tool(
            fn=get_task,
            name="get_task",
            title="Get Task",
            description="Get a single task by ID.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique identifier of the task",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            fn=update_task,
            name="update_task",
            title="Update Task",
            description="Update a task.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to update",
                    },
                    "fields": {
                        "type": "object",
                        "description": "Fields to update",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title",
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description",
                            },
                            "status": {
                                "type": "string",
                                "description": "Task status",
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Assigned user",
                            },
                            "flag": {
                                "type": "boolean",
                                "description": "Flag status",
                            },
                            "order": {
                                "type": "integer",
                                "description": "Task order",
                            },
                        },
                    },
                },
                "required": ["task_id", "fields"],
            },
        ),
        Tool(
            fn=delete_task,
            name="delete_task",
            title="Delete Task",
            description="Delete a task.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique identifier of the task to delete",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            fn=bulk_update_tasks,
            name="bulk_update_tasks",
            title="Bulk Update Tasks",
            description="Update multiple tasks.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of task IDs",
                    },
                    "title": {
                        "type": "string",
                        "description": "Title to update",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description to update",
                    },
                    "status": {
                        "type": "string",
                        "description": "Status to update",
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Assignee to update",
                    },
                },
                "required": ["task_ids"],
            },
        ),
        Tool(
            fn=count_tasks,
            name="count_tasks",
            title="Count Tasks",
            description="Count tasks matching filters.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Filter by assignee",
                    },
                    "case_id": {
                        "type": "string",
                        "description": "Filter by case ID",
                    },
                },
            },
        ),
        # Task status operations
        Tool(
            fn=complete_task,
            name="complete_task",
            title="Complete Task",
            description="Mark task as completed.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to complete",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            fn=start_task,
            name="start_task",
            title="Start Task",
            description="Start a task.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to start",
                    },
                },
                "required": ["task_id"],
            },
        ),
        Tool(
            fn=assign_task,
            name="assign_task",
            title="Assign Task",
            description="Assign task to user.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID",
                    },
                    "assignee": {
                        "type": "string",
                        "description": "User to assign to",
                    },
                },
                "required": ["task_id", "assignee"],
            },
        ),
        # Task logs
        Tool(
            fn=create_task_log,
            name="create_task_log",
            title="Create Task Log",
            description="Create log entry for task.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID",
                    },
                    "message": {
                        "type": "string",
                        "description": "Log message",
                    },
                    "include_in_timeline": {
                        "type": "boolean",
                        "description": "Include in report",
                    },
                },
                "required": ["task_id", "message"],
            },
        ),
        Tool(
            fn=find_task_logs,
            name="find_task_logs",
            title="Find Task Logs",
            description="Find logs for task.",
            is_async=True,
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task ID",
                    },
                },
                "required": ["task_id"],
            },
        ),
    ]


async def get_tasks(
    filters: dict | None = None,
    sortby: dict | None = None,
    paginate: dict | None = None,
) -> list[types.TextContent]:
    """Retrieve tasks from TheHive with optional filters and pagination."""
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


        result = _get_task_api().find(filters=_filters, sortby=_sortby, paginate=_paginate)  # type: ignore
        return [types.TextContent(type="text", text=json.dumps(item, indent=2, default=str)) for item in result]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error retrieving tasks: {e!s}"),
        ]

async def create_task(
    case_id: str,
    fields: dict,
) -> list[types.TextContent]:
    """Create a new task in TheHive."""
    try:
        if not case_id:
            return [
                types.TextContent(
                    type="text",
                    text="Error creating task: Missing case ID.",
                ),
            ]

        required_fields = ["title"]
        data = {}

        if not fields:
            return [
                types.TextContent(
                    type="text",
                    text="Error creating task: Missing task data.",
                ),
            ]

        data.update(fields)

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error creating task: Missing required fields: {', '.join(missing_fields)}. Required fields are: {', '.join(required_fields)}",
                ),
            ]

        result = _get_task_api().create(case_id=case_id, task=data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created task: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error creating task: {e!s}")]


async def get_task(
    task_id: str,
) -> list[types.TextContent]:
    """Get a single task by ID."""
    try:

        result = _get_task_api().get(task_id=task_id)
        return [types.TextContent(type="text", text=str(result))]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error getting task: {e!s}")]


async def update_task(
    task_id: str,
    fields: dict,
) -> list[types.TextContent]:
    """Update a task."""
    try:
        if not task_id:
           return [
               types.TextContent(
                   type="text",
                   text="Error updating task: Missing task ID.",
               ),
           ]
        if not fields:
            return [
                types.TextContent(
                    type="text",
                    text="Error updating task: Missing task fields.",
                ),
            ]

        _get_task_api().update(task_id=task_id, fields=fields)  # type: ignore
        return [
            types.TextContent(type="text", text=f"Task {task_id} updated successfully"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error updating task: {e!s}")]


async def delete_task(
    task_id: str,
) -> list[types.TextContent]:
    """Delete a task."""
    try:

        _get_task_api().delete(task_id=task_id)
        return [
            types.TextContent(type="text", text=f"Task {task_id} deleted successfully"),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error deleting task: {e!s}")]


async def bulk_update_tasks(
    task_ids: list[str],
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
) -> list[types.TextContent]:
    """Update multiple tasks at once."""
    try:

        fields: dict[str, Any] = {"ids": task_ids}

        if title is not None:
            fields["title"] = [title]
        if description is not None:
            fields["description"] = [description]
        if status is not None:
            fields["status"] = [status]
        if assignee is not None:
            fields["assignee"] = [assignee]

        _get_task_api().bulk_update(fields=fields)  # type: ignore
        return [
            types.TextContent(
                type="text",
                text=f"Updated {len(task_ids)} tasks successfully",
            ),
        ]
    except TheHiveError as e:
        return [
            types.TextContent(type="text", text=f"Error bulk updating tasks: {e!s}"),
        ]

async def count_tasks(
    status: str | None = None,
    assignee: str | None = None,
    case_id: str | None = None,
) -> list[types.TextContent]:
    """Count tasks matching the given filters."""
    try:

        filters = {}

        if status is not None:
            filters["status"] = status
        if assignee is not None:
            filters["assignee"] = assignee
        if case_id is not None:
            filters["case"] = case_id

        result = _get_task_api().count(filters=filters if filters else None)
        return [types.TextContent(type="text", text=f"Found {result} tasks")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error counting tasks: {e!s}")]


async def complete_task(
    task_id: str,
) -> list[types.TextContent]:
    """Mark a task as completed."""
    try:

        _get_task_api().update(task_id=task_id, fields={"status": "Completed"})
        return [types.TextContent(type="text", text=f"Task {task_id} completed")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error completing task: {e!s}")]


async def start_task(
    task_id: str,
) -> list[types.TextContent]:
    """Start a task."""
    try:

        _get_task_api().update(task_id=task_id, fields={"status": "InProgress"})
        return [types.TextContent(type="text", text=f"Task {task_id} started")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error starting task: {e!s}")]


async def assign_task(
    task_id: str,
    assignee: str,
) -> list[types.TextContent]:
    """Assign a task to a user."""
    try:

        _get_task_api().update(task_id=task_id, fields={"assignee": assignee})
        return [
            types.TextContent(
                type="text",
                text=f"Task {task_id} assigned to {assignee}",
            ),
        ]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error assigning task: {e!s}")]

async def create_task_log(
    task_id: str,
    message: str,
    include_in_timeline: bool | None = None,
) -> list[types.TextContent]:
    """Create a log entry for a task."""
    try:

        if not message:
            return [types.TextContent(type="text", text="Message is required")]

        log_data: dict[str, Any] = {"message": message}

        if include_in_timeline is not None:
            log_data["includeInTimeline"] = str(int(include_in_timeline))

        result = _get_task_log_api().create(task_id=task_id, task_log=log_data)  # type: ignore
        return [types.TextContent(type="text", text=f"Created log: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error creating log: {e!s}")]


async def find_task_logs(
    task_id: str,
) -> list[types.TextContent]:
    """Find logs for a task."""
    try:

        result = _get_task_api().find_logs(task_id=task_id)
        return [types.TextContent(type="text", text=f"Task logs: {result}")]
    except TheHiveError as e:
        return [types.TextContent(type="text", text=f"Error finding logs: {e!s}")]
