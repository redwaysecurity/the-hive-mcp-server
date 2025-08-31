# handlers

TheHive Handler Functions Package

This package contains handler functions for various TheHive platform operations.
These handlers implement the business logic for processing requests related to
alerts, cases, observables, tasks, and other TheHive entities.

The handlers are designed to work with message-based communication patterns,
making them suitable for integration with MCP (Model Context Protocol) servers,
event-driven architectures, and other messaging systems.

Available Handlers:
    alert: Alert creation and search functionality
    case: Case management and search operations
    observable: Observable (IoC) handling and analysis
    task: Task creation and management
    comment: Comment and note management
    timeline: Timeline event handling
    user: User management operations
    cortex: Cortex analyzer integration
    procedure: Procedure and playbook execution

Each handler module provides functions that accept an API client and a message
object, returning appropriate responses for the requested operations.

Example:
    from handlers.alert import create_alert, search_alerts
    from handlers.case import create_case, search_cases

