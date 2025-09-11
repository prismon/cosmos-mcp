# Changelog

All notable changes to the Cosmos MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-11

### Added
- Initial release of Cosmos MCP Server
- FastMCP-based Model Context Protocol server for OpenC3 COSMOS integration
- Dynamic tool generation from OpenC3 script module functions
- Core command and telemetry tools:
  - `cosmos_cmd` - Send commands with parameters
  - `cosmos_cmd_string` - Send commands using string syntax
  - `cosmos_tlm`, `cosmos_tlm_raw`, `cosmos_tlm_formatted`, `cosmos_tlm_with_units` - Get telemetry values
  - `cosmos_check` - Verify telemetry values
- System information tools for targets, commands, and telemetry
- Interface and router management tools
- Limits monitoring and management tools
- Settings and metadata tools
- Stash key-value storage tools
- OAuth authentication support with multiple providers:
  - RemoteAuthProvider with Dynamic Client Registration (DCR)
  - OAuthProxy for existing OAuth providers
  - Support for OpenC3's Keycloak integration
- Multiple server configurations:
  - Non-OAuth server for simple integration
  - OAuth-protected server with DCR support
  - OAuth proxy server for pre-registered clients
- Comprehensive startup scripts for different authentication modes
- Docker support with Dockerfile
- Environment variable configuration for OpenC3 connection
- HTTP traffic logging for debugging
- Compatible with:
  - Claude Desktop
  - ChatGPT (via custom GPT)
  - MCP Inspector
  - Any MCP-compatible client

### Technical Details
- Built with FastMCP v2.12.2
- Python 3.13+ required
- OpenC3 (openc3>=6.7.0) integration
- Supports both authenticated and non-authenticated modes
- HTTP/Streamable transport on port 3443

### Configuration
- Configurable OpenC3 API endpoints
- Support for custom Keycloak realms
- Dynamic Client Registration with initial access tokens
- Environment-based configuration for all settings

### Documentation
- CLAUDE.md for AI assistant guidance
- README.md with setup instructions
- Inline documentation for all tools
- OAuth configuration examples

### Known Issues
- OAuth .well-known endpoints require proper configuration for full client discovery
- Some OpenC3 functions with **kwargs cannot be exposed as MCP tools
- DCR token expiration needs manual renewal

### Future Improvements
- Add more OpenC3 automation tools
- Implement webhook support for telemetry monitoring
- Add batch command execution
- Improve OAuth metadata endpoint generation
- Add prometheus metrics endpoint