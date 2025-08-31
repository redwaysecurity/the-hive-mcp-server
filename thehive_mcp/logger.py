"""
Logging configuration utilities for TheHive MCP Server.

This module provides centralized logging configuration that can be used
across the entire project to ensure consistent logging format and behavior.
"""

import logging


def configure_logging(level: str = "INFO", logger_name: str | None = None) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: Optional specific logger name, defaults to root logger

    Returns:
        Configured logger instance
    """
    # Get the appropriate logger
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set logging level
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (only used if root logger is not configured)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Check if root logger is already configured with handlers
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # If root logger is configured, inherit its level
        logger.setLevel(root_logger.level)
    elif not logger.handlers:
        # Only configure if not already configured and root logger isn't configured
        configure_logging(level, name)

    return logger
