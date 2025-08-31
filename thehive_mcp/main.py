"""
TheHive MCP Server Main Entry Point
"""

import importlib
import logging
from collections.abc import Callable
from functools import cache
from typing import Any

import click

from thehive_mcp.app import app
from thehive_mcp.logger import configure_logging


@cache
def get_tool_functions(module_name: str) -> list[Any]:
    """Lazily import module tools and cache them."""
    module_getters = {
        "alert": lambda: importlib.import_module("thehive_mcp.tools.alert").get_all_functions(),
        "case": lambda: importlib.import_module("thehive_mcp.tools.case").get_all_functions(),
        "observable": lambda: importlib.import_module("thehive_mcp.tools.observable").get_all_functions(),
        "task": lambda: importlib.import_module("thehive_mcp.tools.task").get_all_functions(),
        "cortex": lambda: importlib.import_module("thehive_mcp.tools.cortex").get_all_functions(),
    }
    if module_name in module_getters:
        return module_getters[module_name]()  # type: ignore
    return []


MODULE_TO_FUNCTIONS = {
    "alert": lambda: importlib.import_module("thehive_mcp.tools.alert").get_all_functions(),
    "case": lambda: importlib.import_module("thehive_mcp.tools.case").get_all_functions(), 
    "observable": lambda: importlib.import_module("thehive_mcp.tools.observable").get_all_functions(),
    "task": lambda: importlib.import_module("thehive_mcp.tools.task").get_all_functions(),
    "cortex": lambda: importlib.import_module("thehive_mcp.tools.cortex").get_all_functions(),
}


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="streamable-http",
    help="Transport protocol: stdio, sse, or streamable-http",
)
@click.option(
    "--modules",
    type=click.Choice(list(MODULE_TO_FUNCTIONS.keys())),
    default=list(MODULE_TO_FUNCTIONS.keys()),
    multiple=True,
    help="Modules to load. Default is all.",
)
@click.option("--log-level", default="INFO", help="Logging level")
def main(transport: str, modules: list[str], log_level: str) -> None:
    """Start the TheHive MCP server."""
    # Configure root logger so all modules inherit the same level
    configure_logging(level=log_level)
    logger = logging.getLogger("thehive_mcp.main")
    logger.info("Registering TheHive tools...")
    tool_count = 0
    registered = set()

    for module_name in modules:
        try:
            functions = MODULE_TO_FUNCTIONS[module_name]()
            # import pdb; pdb.set_trace()
            for tool in functions:
                logger.debug(f"Registering tool: {tool.name}")
                if not hasattr(tool, "__name__"):
                    tool.__name__ = tool.name
                if tool.name in registered:
                    logger.warning(f"Skipping duplicate tool: {tool.name}")
                    continue
                app.add_tool(tool.fn)
                registered.add(tool.name)
                tool_count += 1
        except Exception as e:
            logger.error(f"Failed loading module {module_name}: {e}")

    logger.info(f"Total tools registered: {tool_count}")
    if tool_count == 0:
        logger.warning("No tools registered!")

    logger.info(f"Starting server with transport: {transport}")

    app.run(transport=transport)  # type: ignore


if __name__ == "__main__":
    try:
        main()
    except click.exceptions.BadParameter as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)
