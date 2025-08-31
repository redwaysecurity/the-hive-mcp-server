# __init__

File: `src/__init__.py`

## Description

TheHive MCP Server Package

This package provides the main implementation of the TheHive Model Context Protocol
(MCP) server. It enables AI assistants and other MCP clients to interact with
TheHive platform for security incident management and response.

The package includes:
- Main server configuration and startup logic
- Environment variable management
- TheHive API client initialization
- MCP transport protocol handling

Modules:
main: Command-line interface and server startup
server: FastMCP server configuration
envs: Environment variable management
thehive: TheHive-specific functionality and API clients

Usage:
The package can be run as a module:
python -m src --transport stdio

Or imported for programmatic use:
from src.main import main
main("stdio")

## Statistics

- Functions: 0
- Classes: 0
- Lines of code: 27

