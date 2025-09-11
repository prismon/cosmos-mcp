#!/usr/bin/env python
"""
Start the Cosmos MCP Server with DCR OAuth authentication.
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
os.environ["KEYCLOAK_REALM"] = os.environ.get("KEYCLOAK_REALM", "openc3")

# DCR Initial Access Token for Dynamic Client Registration
os.environ["DCR_INITIAL_TOKEN"] = os.environ.get("DCR_INITIAL_TOKEN", 
    "eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIyNjQ0YmQ2ZS1kNmU3LTQ5Y2UtYWRiYy00Y2NhM2NhYmI4ZmIifQ.eyJleHAiOjE3NTc2MzQyOTMsImlhdCI6MTc1NzU0Nzg5MywianRpIjoiN2I1YzhkMzItNGY4Ni00ZDUwLWFhZjctMmQ1NDk4N2M4YzMxIiwiaXNzIjoiaHR0cHM6Ly90cmFpbmluZzIwLm9wZW5jMy5jb20vYXV0aC9yZWFsbXMvb3BlbmMzIiwiYXVkIjoiaHR0cHM6Ly90cmFpbmluZzIwLm9wZW5jMy5jb20vYXV0aC9yZWFsbXMvb3BlbmMzIiwidHlwIjoiSW5pdGlhbEFjY2Vzc1Rva2VuIn0.nIrERCnq9KxaII3Oo6Q3OBvgM0JUcu5IfbJLhVLerCX6n5XrnKuIX4EZpn9FvnOFGuqcR9uOq3PSVMCqoSENWw"
)

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
print("OAuth DCR Configuration:")
print(f"  Keycloak URL: {os.environ['OPENC3_KEYCLOAK_URL']}")
print(f"  Realm: {os.environ['KEYCLOAK_REALM']}")
print(f"  DCR Token: {'*' * 20} (configured)")
print(f"  MCP Base URL: {os.environ['MCP_BASE_URL']}")
print("")
print("Clients can dynamically register using the DCR token")
print("=" * 60)

# NOW import and run the server after environment is configured
from server_dcr import mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=3443)