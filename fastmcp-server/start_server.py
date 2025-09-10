#!/usr/bin/env python
"""
Start the Cosmos MCP Server with proper OpenC3 configuration.
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

# Print configuration
print("=" * 60)
print("OpenC3 Configuration (set before imports):")
print(f"  API Server: {os.environ['OPENC3_API_SCHEMA']}://{os.environ['OPENC3_API_HOSTNAME']}:{os.environ['OPENC3_API_PORT']}")
print(f"  Script API: {os.environ['OPENC3_SCRIPT_API_SCHEMA']}://{os.environ['OPENC3_SCRIPT_API_HOSTNAME']}:{os.environ['OPENC3_SCRIPT_API_PORT']}")
print(f"  Keycloak: {os.environ['OPENC3_KEYCLOAK_URL']}")
print(f"  Username: {os.environ['OPENC3_API_USER']}")
print("=" * 60)

# NOW import and run the server after environment is configured
from server import mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3443)