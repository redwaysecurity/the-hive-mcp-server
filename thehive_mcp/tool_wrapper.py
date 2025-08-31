"""
Tool wrapper to provide backward compatibility with the expected Tool interface.
"""

from typing import Any, Callable, Union
from mcp import Tool as MCPTool
from collections.abc import Awaitable


class Tool:
    """Wrapper around MCP Tool that maintains backward compatibility."""
    
    def __init__(
        self,
        fn: Callable[..., Union[Any, Awaitable[Any]]],
        name: str,
        title: str = "",
        description: str = "",
        is_async: bool = False,
        inputSchema: dict[str, Any] | None = None,
        outputSchema: dict[str, Any] | None = None,
    ):
        self.fn = fn
        self.name = name
        self.title = title
        self.description = description
        self.is_async = is_async
        self.__name__ = name
        
        # Create the underlying MCP Tool
        self._mcp_tool = MCPTool(
            name=name,
            title=title if title else None,
            description=description if description else None,
            inputSchema=inputSchema or {},
            outputSchema=outputSchema,
        )
    
    def to_mcp_tool(self) -> MCPTool:
        """Convert to MCP Tool format."""
        return self._mcp_tool
