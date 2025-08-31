# src.main

TheHive MCP Server Main Entry Point

This module provides the main command-line interface for the TheHive Model Context
Protocol server. It uses Click to handle command-line arguments and supports
multiple transport protocols for MCP communication.

The server can operate in different transport modes:
- stdio: Standard input/output communication (default)
- sse: Server-Sent Events for HTTP-based communication

This flexibility allows the server to integrate with various MCP clients
and deployment scenarios.

## Module Variables

### `main`

Type: `Command`

Start the TheHive MCP server with the specified transport protocol.
    
    This function initializes and starts the TheHive Model Context Protocol server,
    which exposes TheHive functionality as tools that can be used by AI assistants
    and other MCP-compatible clients.
    
    Args:
        transport (str): The transport protocol to use for MCP communication.
            - "stdio": Uses standard input/output streams (suitable for subprocess communication)
            - "sse": Uses Server-Sent Events over HTTP (suitable for web-based clients)
    
    Returns:
        None: The function starts the server and runs indefinitely until terminated.
    
    Raises:
        ImportError: If required dependencies are not installed
        ConnectionError: If unable to connect to TheHive instance
        ConfigurationError: If environment variables are not properly configured
    
    Example:
        >>> # Start server with default stdio transport
        >>> main("stdio")
        
        >>> # Start server with SSE transport for web clients
        >>> main("sse")
    
    Note:
        The server will run indefinitely until interrupted (Ctrl+C) or the process
        is terminated. Ensure TheHive is accessible at the configured URL before
        starting the server.

---

