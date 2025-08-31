# src.envs

Environment Configuration Module

This module manages environment variables and configuration settings for TheHive MCP server.
It provides centralized access to configuration parameters that can be set via environment
variables, allowing for flexible deployment across different environments.

Environment Variables:
    HIVE_URL: The base URL of TheHive instance (default: http://localhost:9000)
    HIVE_API_KEY: API key for authenticating with TheHive (default: "123")

The module uses sensible defaults for development while allowing production deployments
to override settings through environment variables.

## Module Variables

### `HIVE_API_KEY`

Type: `str`

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

---

### `HIVE_URL`

Type: `str`

str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.

---

