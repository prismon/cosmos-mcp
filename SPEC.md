# Cosmos MCP Server - Technical Specification

> **⚠️ AI-GENERATED PROJECT - USE AT YOUR OWN RISK**
>
> This project was created with AI assistance (Claude Code) and is provided as-is without warranty.
> Users are solely responsible for testing, validation, and any consequences of use in their environments.
>
> **DO NOT PROVIDE AI SYSTEMS WITH ACCESS TO NUCLEAR WEAPONS OR WEAPONS SYSTEMS.**

## Overview

The Cosmos MCP Server is a Model Context Protocol (MCP) server implementation that provides AI assistants (Claude, ChatGPT, etc.) with direct access to OpenC3 COSMOS command and control systems. Built with FastMCP, it exposes OpenC3's Python API as MCP tools that can be invoked by AI clients.

**Version:** 0.1.0
**Protocol:** MCP 2024-11-05
**Transport:** HTTP/Streamable (Server-Sent Events)
**Default Port:** 3443
**Endpoint:** `/mcp`
**License:** MIT

## Architecture

### Core Components

```
cosmos-mcp/
├── fastmcp-server/
│   ├── server_dynamic_v2.py    # Main server with OpenC3 tools (no auth)
│   ├── server_oauth.py         # OAuth-protected server
│   ├── server_dcr.py           # DCR OAuth server
│   ├── start_server.py         # Main startup script (no auth)
│   ├── start_server_oauth.py   # OAuth startup script
│   ├── start_server_dcr.py     # DCR startup script
│   ├── pyproject.toml          # Python dependencies
│   └── Dockerfile              # Container build
├── CHANGELOG.md                # Version history
├── CLAUDE.md                   # AI assistant instructions
├── LICENSE                     # MIT License
├── README.md                   # GitHub documentation
└── SPEC.md                     # This file
```

### Technology Stack

- **FastMCP:** v2.12.4 - MCP server framework
- **Python:** 3.13+ required
- **OpenC3:** v6.7.0+ - COSMOS Python API client
- **MCP SDK:** v1.16.0 - Model Context Protocol implementation
- **Transport:** Streamable HTTP (Server-Sent Events)
- **Authentication:** OAuth 2.0/OIDC with Keycloak (optional)

## Server Configurations

The server supports three authentication modes. Choose the appropriate configuration based on your security requirements.

### 1. No Authentication Mode (Development/Testing)

**File:** `server_dynamic_v2.py`
**Startup:** `start_server.py`
**Port:** 3443 (configurable)
**Authentication:** Disabled

Use for local development, testing, or trusted network environments only.

**Starting the server:**
```bash
cd fastmcp-server
uv run python start_server.py
```

### 2. OAuth Server with Pre-Registered Client (Recommended for Production)

**File:** `server_oauth.py`
**Startup:** `start_server_oauth.py`
**Authentication:** OAuth 2.0/OIDC via OAuthProxy with Keycloak

This mode requires a pre-registered OAuth client in your Keycloak instance.

**Required Configuration:**
```bash
export KEYCLOAK_REALM="openc3"
export KEYCLOAK_CLIENT_ID="mcp"
export KEYCLOAK_CLIENT_SECRET="your-client-secret"
export OPENC3_KEYCLOAK_URL="https://training20.openc3.com/auth"
export MCP_BASE_URL="http://localhost:3443"
```

**Starting the server:**
```bash
cd fastmcp-server
uv run python start_server_oauth.py
```

**To enable OAuth in server code:**
```python
from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier

# Configure JWT verification
token_verifier = JWTVerifier(
    jwks_uri="https://keycloak-server/realms/realm/protocol/openid-connect/certs",
    issuer="https://keycloak-server/realms/realm",
    audience="client-id"
)

# Create OAuth proxy
auth = OAuthProxy(
    upstream_authorization_endpoint="https://keycloak-server/realms/realm/protocol/openid-connect/auth",
    upstream_token_endpoint="https://keycloak-server/realms/realm/protocol/openid-connect/token",
    upstream_client_id="mcp",
    upstream_client_secret="secret",
    token_verifier=token_verifier,
    base_url="http://localhost:3443"
)

# Create server with authentication
mcp = FastMCP(name="Cosmos MCP Server", auth=auth)
```

**To disable OAuth:**
Simply remove the `auth` parameter when creating the FastMCP instance:
```python
# No authentication
mcp = FastMCP(name="Cosmos MCP Server")
```

### 3. OAuth with Dynamic Client Registration (DCR)

**File:** `server_dcr.py`
**Startup:** `start_server_dcr.py`
**Authentication:** OAuth 2.0 with Dynamic Client Registration

This mode automatically registers clients on first connection. Requires a DCR initial access token from Keycloak admin.

**Required Configuration:**
```bash
export DCR_INITIAL_TOKEN="eyJ..."
export OPENC3_KEYCLOAK_URL="https://training20.openc3.com/auth"
export KEYCLOAK_REALM="openc3"
export MCP_BASE_URL="http://localhost:3443"
```

**Starting the server:**
```bash
cd fastmcp-server
uv run python start_server_dcr.py
```

## Enabling/Disabling OAuth Security

### Quick Start: Disable OAuth

To run without authentication (e.g., for local testing):
```bash
cd fastmcp-server
uv run python start_server.py
```

### Quick Start: Enable OAuth

To run with OAuth/OIDC security:

1. **Register OAuth client in Keycloak:**
   - Client ID: `mcp`
   - Client authentication: ON
   - Valid redirect URIs: `http://localhost:3443/*`
   - Note the generated client secret

2. **Set environment variables:**
   ```bash
   export KEYCLOAK_CLIENT_ID="mcp"
   export KEYCLOAK_CLIENT_SECRET="your-secret-here"
   export OPENC3_KEYCLOAK_URL="https://your-keycloak.com/auth"
   ```

3. **Start OAuth-enabled server:**
   ```bash
   cd fastmcp-server
   uv run python start_server_oauth.py
   ```

### Switching Between Modes

The server configuration is determined by which startup script you use:

- **No Auth:** `python start_server.py` → Uses `server_dynamic_v2.py`
- **OAuth:** `python start_server_oauth.py` → Uses `server_oauth.py`
- **DCR:** `python start_server_dcr.py` → Uses `server_dcr.py`

No code changes required - just use the appropriate startup script.

## OpenC3 Integration

### Environment Configuration

The server requires OpenC3 environment variables to be set **before** importing the `openc3` module:

```bash
OPENC3_API_HOSTNAME       # COSMOS API hostname
OPENC3_API_PORT          # API port (default: 443)
OPENC3_API_SCHEMA        # http or https
OPENC3_API_USER          # Username for authentication
OPENC3_API_PASSWORD      # Password for authentication
OPENC3_KEYCLOAK_URL      # Keycloak server URL
```

**Critical:** All startup scripts (`start_server*.py`) set these environment variables before importing any OpenC3 modules. This ensures proper API endpoint configuration.

## MCP Tools

The server dynamically exposes OpenC3 functionality as MCP tools. All tools follow async patterns and return string responses (often JSON-formatted).

### Command Tools

#### `cosmos_cmd`
Send commands to targets with structured parameters.

**Parameters:**
- `target_name` (str): Target identifier (e.g., "INST")
- `command_name` (str): Command identifier (e.g., "COLLECT")
- `parameters` (str, optional): JSON string of command parameters
- `timeout` (float, optional): Command timeout in seconds
- `log_message` (str, optional): Optional log entry
- `validate` (bool): Validate command before sending (default: true)
- `scope` (str): COSMOS scope (default: "DEFAULT")

**Example:**
```json
{
  "target_name": "INST",
  "command_name": "COLLECT",
  "parameters": "{\"TYPE\": \"NORMAL\", \"DURATION\": 5.0}"
}
```

#### `cosmos_cmd_string`
Send commands using COSMOS string syntax.

**Parameters:**
- `command_string` (str): Full command string (e.g., "INST COLLECT with TYPE NORMAL, DURATION 5.0")
- `timeout` (float, optional)
- `log_message` (str, optional)
- `validate` (bool)
- `scope` (str)

### Telemetry Tools

#### `cosmos_tlm`
Get telemetry value with specified type conversion.

**Parameters:**
- `target_name` (str): Target identifier
- `packet_name` (str): Telemetry packet name
- `item_name` (str): Telemetry item name
- `value_type` (str): "CONVERTED", "RAW", "FORMATTED", "WITH_UNITS" (default: "CONVERTED")
- `scope` (str): COSMOS scope

**Variants:**
- `cosmos_tlm_raw` - Get raw value
- `cosmos_tlm_formatted` - Get formatted value
- `cosmos_tlm_with_units` - Get value with units

### System Information Tools

#### `cosmos_get_target_names`
List all available targets.

**Returns:** JSON array of target names

#### `cosmos_get_all_cmd_names`
List all commands for a specific target.

**Parameters:**
- `target_name` (str)
- `scope` (str)

**Returns:** JSON array of command names

#### `cosmos_get_all_tlm`
List all telemetry packets and items for a target.

**Parameters:**
- `target_name` (str)
- `scope` (str)

**Returns:** JSON object mapping packet names to item lists

### Limits and Monitoring Tools

#### `cosmos_get_limits_sets`
Get all available telemetry limits sets.

**Returns:** JSON array of limits set names

#### `cosmos_get_out_of_limits`
Get all telemetry items currently violating limits.

**Returns:** JSON array of out-of-limits items with details

### Utility Tools

#### `ping`
Simple connectivity test with timestamp.

**Parameters:**
- `host` (str): Optional identifier (default: "pong")

**Returns:** Timestamp string

#### `stream_ping`
Streaming ping for testing SSE transport.

**Parameters:**
- `count` (int): Number of pings (default: 5)
- `delay` (float): Delay between pings in seconds (default: 1.0)

**Returns:** Stream of timestamped ping messages

## Deployment

### Local Development

```bash
cd fastmcp-server
uv run python start_server.py
```

Server starts on `http://0.0.0.0:3443/mcp`

### Docker Deployment

```bash
cd fastmcp-server
docker build -t cosmos-mcp .
docker run -p 3443:3443 \
  -e OPENC3_API_HOSTNAME=training20.openc3.com \
  -e OPENC3_API_USER=admin \
  -e OPENC3_API_PASSWORD=admin \
  cosmos-mcp
```

### Environment Variables

All configuration via environment variables:

```bash
# OpenC3 Configuration
export OPENC3_API_HOSTNAME="training20.openc3.com"
export OPENC3_API_PORT="443"
export OPENC3_API_SCHEMA="https"
export OPENC3_API_USER="admin"
export OPENC3_API_PASSWORD="admin"
export OPENC3_KEYCLOAK_URL="https://training20.openc3.com/auth"

# MCP Server Configuration
export MCP_BASE_URL="http://localhost:3443"

# OAuth Configuration (if using OAuth)
export KEYCLOAK_REALM="openc3"
export KEYCLOAK_CLIENT_ID="mcp"
export KEYCLOAK_CLIENT_SECRET="secret"

# DCR Configuration (if using DCR)
export DCR_INITIAL_TOKEN="eyJ..."
```

## Client Integration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cosmos": {
      "url": "http://localhost:3443/mcp"
    }
  }
}
```

### ChatGPT Custom GPT

Configure as remote MCP server:
- URL: `http://localhost:3443/mcp`
- Protocol: MCP 2024-11-05
- Transport: HTTP/SSE

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:3443/mcp
```

## API Versioning

### MCP Protocol
- **Current:** 2024-11-05
- **Supported:** 2024-11-05

### Server Version
- **Current:** 0.1.0
- **FastMCP:** 2.12.4
- **MCP SDK:** 1.16.0

## Limitations

### Known Constraints

1. **Function Wrapping:** OpenC3 functions with `**kwargs` cannot be directly exposed as MCP tools due to FastMCP limitations. Explicit wrapper functions with defined parameters are required.

2. **Synchronous Operations:** All OpenC3 operations are wrapped in async functions but execute synchronously. This is due to OpenC3's synchronous API design.

3. **Token Management:** OAuth tokens are managed by FastMCP. Token refresh is automatic but DCR initial access tokens may expire and require manual renewal.

4. **Port Conflicts:** Default port 3443 may conflict with other services. Configure via environment or modify startup scripts.

5. **Environment Variables:** Must be set before importing `openc3` module. Always use provided startup scripts rather than running server files directly.

## Security Considerations

### Authentication Modes

- **No Auth Mode:** Suitable for local development and testing only. Not recommended for production.
- **OAuth Mode (Recommended):** Uses OIDC with Keycloak for production deployments. Provides proper authentication and authorization.
- **DCR Mode:** Provides dynamic client registration. Useful for environments with many clients.

### Network Security

- Server binds to `0.0.0.0` by default (all interfaces)
- Consider firewall rules or reverse proxy for production
- HTTPS termination recommended via reverse proxy (nginx, Caddy)

### Credentials

- OpenC3 credentials stored in environment variables
- OAuth secrets should be managed via secrets management system
- Never commit credentials to version control

## Performance

### Concurrent Connections

- FastMCP handles multiple concurrent MCP sessions
- Each session maintains separate state
- OpenC3 connection pooling not implemented

### Request Timeouts

- Default command timeout: OpenC3 defaults (typically 5-10 seconds)
- Configurable per-command via `timeout` parameter
- HTTP connection timeout: 120 seconds (uvicorn default)

### Resource Usage

- Memory: ~100-200MB baseline (Python + dependencies)
- CPU: Minimal when idle, scales with request volume
- Network: Dependent on OpenC3 telemetry polling frequency

## Error Handling

### Tool Errors

All tools return error messages as strings when exceptions occur:

```python
try:
    result = script.cmd(target_name, command_name, params)
    return f"Success: {result}"
except Exception as e:
    return f"Error sending command: {str(e)}"
```

### MCP Protocol Errors

FastMCP handles MCP protocol errors automatically:
- Invalid JSON → `-32700` Parse error
- Method not found → `-32601` Method not found
- Invalid params → `-32602` Invalid params

### OpenC3 Connection Errors

If OpenC3 API is unreachable, tools return descriptive error messages including connection details.

## Development

### Adding New Tools

1. Add tool function to `server_dynamic_v2.py`:

```python
@mcp.tool
async def cosmos_new_tool(param1: str, param2: int = 10) -> str:
    """
    Tool description for AI clients

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value
    """
    try:
        result = script.some_openc3_function(param1, param2)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

2. Restart server to register new tool

### Testing

```bash
# Start server
cd fastmcp-server
uv run python start_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:3443/mcp

# Test with curl
curl -X POST http://localhost:3443/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## References

- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **FastMCP Documentation:** https://gofastmcp.com/
- **OpenC3 COSMOS:** https://openc3.com/
- **GitHub Repository:** https://github.com/prismon/cosmos-mcp

## License

MIT License - See LICENSE file for details

## Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.**

This is an AI-generated project created with Claude Code assistance. Users assume all responsibility and risk for testing, validation, and deployment decisions.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-08
**Status:** Active Development
**AI-Generated:** Yes (Claude Code)
