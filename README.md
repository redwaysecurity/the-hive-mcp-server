# TheHive MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server implementation for TheHive, enabling seamless integration with MCP clients. This project provides a standardized way to interact with TheHive's security incident response platform through the Model Context Protocol.

### Implemented MCP Tools

The following MCP tools are implemented and available:

- add_case_attachment
- assign_task
- bulk_delete_alerts
- bulk_delete_observables
- bulk_merge_alerts_into_case
- bulk_update_alerts
- bulk_update_cases
- bulk_update_observables
- bulk_update_tasks
- close_case
- complete_task
- count_alerts
- count_cases
- count_observables
- count_tasks
- create_alert
- create_alert_observable
- create_case
- create_case_observable
- create_case_page
- create_case_procedure
- create_case_task
- create_cortex_analyzer_job
- create_cortex_responder_action
- create_observable_in_alert
- create_observable_in_case
- create_task
- create_task_log
- delete_alert
- delete_case
- delete_case_attachment
- delete_observable
- delete_task
- download_case_attachment
- find_alert_observables
- find_case_attachments
- find_case_comments
- find_case_observables
- find_case_pages
- find_case_procedures
- find_case_tasks
- find_task_logs
- follow_alert
- get_alert
- get_alert_similar_observables
- get_alerts
- get_case
- get_case_similar_observables
- get_cases
- get_cortex_analyzer
- get_cortex_analyzer_job
- get_observable
- get_observable_analyzer_jobs
- get_observables
- get_task
- get_tasks
- import_alert_into_case
- list_cortex_analyzers
- list_cortex_analyzers_by_type
- list_cortex_responders
- merge_alert_into_case
- merge_cases
- promote_alert_to_case
- run_observable_analyzer
- run_observable_analyzers
- share_observable
- start_task
- unfollow_alert
- unshare_observable
- update_alert
- update_case
- update_observable
- update_task

## Setup

### Dependencies

This project depends on the official TheHive client library (`thehive4py`). It will be automatically installed when you install this package.

### Environment Variables

Set the following environment variables:

```bash
HIVE_URL=<your-thehive-url>              # Required: TheHive instance URL (e.g., https://thehive.company.com:9000)
HIVE_API_KEY=<your-thehive-api-key>      # Required: API key for authenticating with TheHive instance
```

### Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "thehive-mcp-server": {
      "command": "uvx",
      "args": ["thehive-mcp-server"],
      "env": {
        "HIVE_URL": "https://your-thehive-host:9000",
        "HIVE_API_KEY": "your-api-key"
      }
    }
  }
}
```

Alternative configuration using `uv`:

```json
{
  "mcpServers": {
    "thehive-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp",
        "run",
        "python",
        "-m",
        "thehive_mcp.main"
      ],
      "env": {
        "HIVE_URL": "https://your-thehive-host:9000",
        "HIVE_API_KEY": "your-api-key"
      }
    }
  }
}
```

Replace `/path/to/mcp` with the actual path to the root directory where you've cloned the repository.

### Manual Execution

You can also run the server manually:

```bash
# Install dependencies
pip install .

# Set environment variables
export HIVE_URL="http://localhost:9000"
export HIVE_API_KEY="your-api-key"

# Run the server
python -m thehive_mcp
```

## License

This project is licensed under the MIT License. See LICENSE file for details.
