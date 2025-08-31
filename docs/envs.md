# envs

File: `src/envs.py`

## Description

Environment Configuration Module

This module manages environment variables and configuration settings for TheHive MCP server.
It provides centralized access to configuration parameters that can be set via environment
variables, allowing for flexible deployment across different environments.

Environment Variables:
HIVE_URL: The base URL of TheHive instance (default: http://localhost:9000)
HIVE_API_KEY: API key for authenticating with TheHive (default: "123")

The module uses sensible defaults for development while allowing production deployments
to override settings through environment variables.

## Statistics

- Functions: 0
- Classes: 0
- Lines of code: 33

