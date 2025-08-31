# observable

File: `src/thehive/observable.py`

## Description

TheHive Observable Management Functions

This module provides MCP-compatible functions for managing observables (IoCs)
in TheHive platform. Observables are critical pieces of evidence that can be
analyzed, enriched, and used for detection and response activities.

MCP Integration Features:
- Standardized observable operations for AI assistants
- Type validation for different observable types
- Structured response formatting for MCP clients
- Integration with Cortex analyzers

Observable Types Supported:
- IP addresses and CIDR blocks
- Domain names and FQDNs
- File hashes (MD5, SHA1, SHA256, etc.)
- Email addresses and message IDs
- URLs and URIs
- Filenames and file paths
- Registry keys and values

Planned Functions:
get_observables: Retrieve observables with filtering
create_observable: Add new observables to cases/alerts
update_observable: Modify observable properties
delete_observable: Remove observables
bulk_create_observables: Efficiently add multiple observables
analyze_observable: Trigger Cortex analysis

Note:
This module is currently under development. MCP-compatible observable functions
will be implemented following the same patterns as the alert module.

## Statistics

- Functions: 0
- Classes: 0
- Lines of code: 42

