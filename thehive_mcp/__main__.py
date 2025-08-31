"""
TheHive MCP Server Entry Point

This module serves as the main entry point for the TheHive Model Context Protocol server
when executed as a package. It provides a clean interface for starting the server
with proper exit handling.

Usage:
    python -m src
    uv run python -m src

The module imports and executes the main function from main, ensuring proper
command-line argument parsing and server initialization.
"""

import sys

import click


def run() -> int:
    """Run the MCP server with proper error handling."""
    try:
        from .main import main

        exit_code = main.main(standalone_mode=False)

        return exit_code  # type: ignore
    except click.exceptions.BadParameter as e:
        click.echo(f"Failed to start server: {e}", err=True)
        return 1
    except SystemExit as e:
        # Handle Click's SystemExit gracefully
        return e.code if e.code is not None else 0  # type: ignore
    except Exception as e:
        click.echo(f"Failed to start server: {e}", err=True)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Execute the main function and exit with its return code
    # This ensures proper exit status propagation for process management
    exit_code = run()
    click.echo(f"Server exited with code: {exit_code}")
    sys.exit(exit_code)
