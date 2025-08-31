# main

File: `src/main.py`

## Description

TheHive MCP Server Main Entry Point

This module provides the main command-line interface for the TheHive Model Context
Protocol server. It uses Click to handle command-line arguments and supports
multiple transport protocols for MCP communication.

The server can operate in different transport modes:
- stdio: Standard input/output communication (default)
- sse: Server-Sent Events for HTTP-based communication

This flexibility allows the server to integrate with various MCP clients
and deployment scenarios.

## Statistics

- Functions: 1
- Classes: 0
- Lines of code: 66

