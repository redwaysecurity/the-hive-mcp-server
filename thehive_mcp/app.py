"""
TheHive MCP Server Configuration
"""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

app = FastMCP(
    "The Hive MCP Server",
    host="localhost",
    port=8000,
    dependencies=["thehive4py"],
)
