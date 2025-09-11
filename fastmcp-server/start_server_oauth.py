#!/usr/bin/env python
"""
Start the Cosmos MCP Server with OAuth authentication.
This script sets environment variables BEFORE importing any OpenC3 modules.
"""
import os
import sys

# IMPORTANT: Set OpenC3 environment variables BEFORE any imports
# These must be set before importing openc3 module
os.environ["OPENC3_API_HOSTNAME"] = os.environ.get("OPENC3_API_HOSTNAME", "training20.openc3.com")
os.environ["OPENC3_API_PORT"] = os.environ.get("OPENC3_API_PORT", "443")
os.environ["OPENC3_API_SCHEMA"] = os.environ.get("OPENC3_API_SCHEMA", "https")

# Script API Server configuration (usually same as API server)
os.environ["OPENC3_SCRIPT_API_HOSTNAME"] = os.environ.get("OPENC3_SCRIPT_API_HOSTNAME", os.environ["OPENC3_API_HOSTNAME"])
os.environ["OPENC3_SCRIPT_API_PORT"] = os.environ.get("OPENC3_SCRIPT_API_PORT", os.environ["OPENC3_API_PORT"])
os.environ["OPENC3_SCRIPT_API_SCHEMA"] = os.environ.get("OPENC3_SCRIPT_API_SCHEMA", os.environ["OPENC3_API_SCHEMA"])

# Authentication credentials
os.environ["OPENC3_API_USER"] = os.environ.get("OPENC3_API_USER", "admin")
os.environ["OPENC3_API_PASSWORD"] = os.environ.get("OPENC3_API_PASSWORD", "admin")

# Keycloak configuration
os.environ["OPENC3_KEYCLOAK_URL"] = os.environ.get("OPENC3_KEYCLOAK_URL", "https://training20.openc3.com/auth")

# OAuth Configuration for FastMCP
# Pre-registered OAuth client credentials with OpenC3 Keycloak
os.environ["OAUTH_CLIENT_ID"] = os.environ.get("OAUTH_CLIENT_ID", "mcp")
os.environ["OAUTH_CLIENT_SECRET"] = os.environ.get("OAUTH_CLIENT_SECRET", "KlUZZ3t6T8qDYdB4JxJzhKKe2FMfLJuY")

# MCP Server base URL
os.environ["MCP_BASE_URL"] = os.environ.get("MCP_BASE_URL", "http://localhost:3443")

# Print configuration
print("=" * 60)
print("OpenC3 Configuration (set before imports):")
print(f"  API Server: {os.environ['OPENC3_API_SCHEMA']}://{os.environ['OPENC3_API_HOSTNAME']}:{os.environ['OPENC3_API_PORT']}")
print(f"  Script API: {os.environ['OPENC3_SCRIPT_API_SCHEMA']}://{os.environ['OPENC3_SCRIPT_API_HOSTNAME']}:{os.environ['OPENC3_SCRIPT_API_PORT']}")
print(f"  Keycloak: {os.environ['OPENC3_KEYCLOAK_URL']}")
print(f"  Username: {os.environ['OPENC3_API_USER']}")
print("")
print("OAuth Configuration:")
print(f"  Keycloak URL: {os.environ['OPENC3_KEYCLOAK_URL']}")
print(f"  Realm: {os.environ.get('KEYCLOAK_REALM', 'openc3')}")
print(f"  Client ID: {os.environ['OAUTH_CLIENT_ID']}")
print(f"  Client Secret: {'*' * 20} (configured)")
print(f"  MCP Base URL: {os.environ['MCP_BASE_URL']}")
print("=" * 60)

# NOW import and run the server after environment is configured
from server_oauth_v2 import mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3443)