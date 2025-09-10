# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Cosmos MCP (Model Context Protocol) server built with FastMCP. The server provides simple tools for ping operations and is designed to run as an HTTP service on port 3443.

## Development Commands

### Running the Server
```bash
cd fastmcp-server
uv run python start_server.py
```
The server will start on `http://127.0.0.1:3443/mcp`

**Important:** Always use `start_server.py` to run the server. This script sets OpenC3 environment variables BEFORE importing the openc3 module, which is required for proper API configuration.

### Managing Dependencies
```bash
cd fastmcp-server
uv add <package>        # Add a new dependency
uv sync                 # Sync dependencies from pyproject.toml
uv pip list            # List installed packages
```

### Docker Operations
```bash
cd fastmcp-server
docker build -t cosmos-mcp .
docker run -p 3443:3443 cosmos-mcp
```

## Architecture

### Core Components

- **server.py**: Main FastMCP server implementation with tool definitions
  - `ping` tool: Simple ping with timestamp response
  - `stream_ping` tool: Streaming ping tool with configurable count and delay
  - HTTP transport on port 3443

- **FastMCP Framework**: The server uses FastMCP v2.12.2 which provides:
  - Automatic MCP protocol handling
  - Tool registration via decorators
  - Built-in HTTP transport support
  - Streaming response capabilities

### Dependencies

- **fastmcp>=2.12.2**: MCP server framework
- **openc3>=6.7.0**: OpenC3 COSMOS integration library
- Python 3.13+ required

## Adding New Tools

To add new tools to the MCP server, use the `@mcp.tool` decorator in server.py:

```python
@mcp.tool
async def your_tool_name(param: str) -> str:
    """Tool description for MCP clients"""
    # Implementation
    return result
```

For streaming tools, yield responses:

```python
@mcp.tool
async def streaming_tool() -> str:
    """Streaming tool description"""
    for item in items:
        yield f"Response: {item}\n"
```