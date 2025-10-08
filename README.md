# Cosmos MCP Server

> **⚠️ AI-Generated Project - Use at Your Own Risk**
>
> This project was created with AI assistance and is provided as-is. See [License](#license) for details.
>
> **DO NOT PROVIDE AI SYSTEMS WITH ACCESS TO NUCLEAR WEAPONS OR WEAPONS SYSTEMS.**

A Model Context Protocol (MCP) server that provides AI assistants with access to OpenC3 COSMOS command and control systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12.4-green.svg)](https://gofastmcp.com/)

## Features

- 🚀 **MCP Protocol Support** - Full implementation of Model Context Protocol 2024-11-05
- 🔧 **OpenC3 Integration** - Direct access to COSMOS command and telemetry systems
- 🔐 **OAuth/OIDC Security** - Optional authentication via Keycloak
- 📡 **Real-time Telemetry** - Get spacecraft telemetry values and monitoring
- 🎯 **Command Execution** - Send commands to spacecraft targets
- 🔄 **Streaming Support** - Server-Sent Events (SSE) for real-time updates
- 🐳 **Docker Ready** - Containerized deployment support

## Quick Start

### Prerequisites

- Python 3.13 or higher
- `uv` package manager (or `pip`)
- Access to an OpenC3 COSMOS instance

### Installation

```bash
# Clone the repository
git clone https://github.com/prismon/cosmos-mcp.git
cd cosmos-mcp/fastmcp-server

# Install dependencies (using uv)
uv sync

# Or with pip
pip install -r requirements.txt
```

### Configuration

Set required environment variables:

```bash
export OPENC3_API_HOSTNAME="training20.openc3.com"
export OPENC3_API_PORT="443"
export OPENC3_API_SCHEMA="https"
export OPENC3_API_USER="admin"
export OPENC3_API_PASSWORD="admin"
export OPENC3_KEYCLOAK_URL="https://training20.openc3.com/auth"
```

### Running the Server

**Without authentication (development/testing):**
```bash
cd fastmcp-server
uv run python start_server.py
```

**With OAuth/OIDC (production):**
```bash
export KEYCLOAK_CLIENT_ID="mcp"
export KEYCLOAK_CLIENT_SECRET="your-secret"
uv run python start_server_oauth.py
```

Server will start on `http://0.0.0.0:3443/mcp`

## Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cosmos": {
      "url": "http://localhost:3443/mcp"
    }
  }
}
```

### With MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:3443/mcp
```

### Example Commands

Once connected, AI assistants can use tools like:

- `cosmos_cmd` - Send commands to targets
- `cosmos_tlm` - Get telemetry values
- `cosmos_get_target_names` - List available targets
- `cosmos_get_out_of_limits` - Check for limit violations
- And many more...

## Authentication

> **⚠️ Note:** OAuth and DCR authentication features are currently in development and incomplete.
> Production use should only use the no-auth mode in trusted environments until OAuth implementation is finalized.

### Disable OAuth (Local Development)

Use `start_server.py` which runs without authentication:

```bash
uv run python start_server.py
```

### Enable OAuth (Production - Work in Progress)

**Status:** OAuth/OIDC and DCR implementations are incomplete and under active development.

1. Register OAuth client in Keycloak:
   - Client ID: `mcp`
   - Client authentication: ON
   - Valid redirect URIs: `http://localhost:3443/*`

2. Configure environment:
   ```bash
   export KEYCLOAK_CLIENT_ID="mcp"
   export KEYCLOAK_CLIENT_SECRET="your-secret"
   export OPENC3_KEYCLOAK_URL="https://your-keycloak.com/auth"
   ```

3. Start server:
   ```bash
   uv run python start_server_oauth.py
   ```

See [SPEC.md](SPEC.md) for detailed configuration options.

## Available Tools

| Tool | Description |
|------|-------------|
| `cosmos_cmd` | Send commands with structured parameters |
| `cosmos_cmd_string` | Send commands using string syntax |
| `cosmos_tlm` | Get telemetry values (converted/raw/formatted) |
| `cosmos_get_target_names` | List all available targets |
| `cosmos_get_all_cmd_names` | List commands for a target |
| `cosmos_get_all_tlm` | List telemetry for a target |
| `cosmos_get_limits_sets` | Get configured limits sets |
| `cosmos_get_out_of_limits` | Get out-of-limits telemetry items |
| `ping` | Simple connectivity test |
| `stream_ping` | Streaming test with SSE |

Full tool documentation in [SPEC.md](SPEC.md).

## Docker Deployment

```bash
cd fastmcp-server
docker build -t cosmos-mcp .
docker run -p 3443:3443 \
  -e OPENC3_API_HOSTNAME=training20.openc3.com \
  -e OPENC3_API_USER=admin \
  -e OPENC3_API_PASSWORD=admin \
  cosmos-mcp
```

## Project Structure

```
cosmos-mcp/
├── fastmcp-server/
│   ├── server_dynamic_v2.py    # Main server (no auth)
│   ├── server_oauth.py         # OAuth server
│   ├── server_dcr.py           # DCR OAuth server
│   ├── start_server.py         # Startup script (no auth)
│   ├── start_server_oauth.py   # OAuth startup
│   ├── pyproject.toml          # Dependencies
│   └── Dockerfile              # Container config
├── SPEC.md                     # Technical specification
├── CHANGELOG.md                # Version history
├── CLAUDE.md                   # AI assistant instructions
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## Development

### Adding New Tools

Edit `server_dynamic_v2.py` and add a new tool:

```python
@mcp.tool
async def your_tool_name(param: str) -> str:
    """Tool description for AI clients"""
    try:
        result = script.some_openc3_function(param)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

Restart the server to register the new tool.

### Testing

```bash
# Test with curl
curl -X POST http://localhost:3443/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## Documentation

- **[SPEC.md](SPEC.md)** - Complete technical specification
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[CLAUDE.md](CLAUDE.md)** - Instructions for AI assistants

## Technology Stack

- **[FastMCP](https://gofastmcp.com/)** v2.12.4 - MCP server framework
- **[OpenC3](https://openc3.com/)** v6.7.0+ - COSMOS Python client
- **Python** 3.13+ - Runtime environment
- **Keycloak** - OAuth/OIDC authentication (optional)

## Known Limitations

1. OpenC3 functions with `**kwargs` require explicit wrappers
2. All operations execute synchronously (OpenC3 API constraint)
3. Default port 3443 may conflict with other services
4. DCR tokens may require manual renewal

See [SPEC.md](SPEC.md) for complete details.

## Contributing

This is an AI-generated project. Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

**Disclaimer:** This software is provided "as is" without warranty. Users are solely responsible for testing, validation, and deployment decisions.

## References

- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **FastMCP Documentation:** https://gofastmcp.com/
- **OpenC3 COSMOS:** https://openc3.com/
- **Model Context Protocol:** https://modelcontextprotocol.io/

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/prismon/cosmos-mcp/issues)
- See [SPEC.md](SPEC.md) for technical details
- Check [CHANGELOG.md](CHANGELOG.md) for version history

---

**Version:** 0.1.0
**Created with:** Claude Code (AI-assisted development)
**Status:** Active Development
