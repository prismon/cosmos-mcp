from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProvider
from datetime import datetime
import asyncio
import os
import json
from typing import Any, Dict, Optional, List, Union
from openc3 import script

# NOTE: Environment variables must be set BEFORE importing openc3
# Use start_server_oauth.py to run this server with proper configuration

# OAuth Configuration using OpenC3's Keycloak
# The OAuthProvider will handle OAuth with Dynamic Client Registration
# Keycloak issuer URL typically includes /realms/{realm-name}
keycloak_base = os.environ.get("OPENC3_KEYCLOAK_URL", "https://training20.openc3.com/auth")
keycloak_realm = os.environ.get("KEYCLOAK_REALM", "openc3")
issuer_url = f"{keycloak_base}/realms/{keycloak_realm}"

# Get base URL for this server (where it's hosted)
base_url = os.environ.get("MCP_BASE_URL", "http://localhost:3443")

auth_provider = OAuthProvider(
    base_url=base_url,
    issuer_url=issuer_url,
    required_scopes=["openid", "profile", "email"],
    service_documentation_url="https://github.com/openc3/cosmos",
)

mcp = FastMCP(
    name="Cosmos MCP Server (OAuth Protected)",
    auth=auth_provider
)

# Keep the original simple tools
@mcp.tool
async def ping(host: str = "pong") -> str:
    """
    Simple ping tool that returns a pong response with timestamp
    
    Args:
        host: Optional host identifier to include in response
    
    Returns:
        A pong response with current timestamp
    """
    timestamp = datetime.now().isoformat()
    return f"Pong from {host} at {timestamp}"

@mcp.tool
async def stream_ping(count: int = 5, delay: float = 1.0) -> str:
    """
    Streaming ping tool that sends multiple pings over time
    
    Args:
        count: Number of pings to send (default: 5)
        delay: Delay in seconds between pings (default: 1.0)
    
    Returns:
        Stream of ping responses
    """
    for i in range(count):
        timestamp = datetime.now().isoformat()
        yield f"Ping {i+1}/{count} at {timestamp}\n"
        if i < count - 1:
            await asyncio.sleep(delay)

# ===== Core Command and Telemetry Tools =====

@mcp.tool
async def cosmos_cmd(
    target_name: str,
    command_name: str,
    parameters: Optional[str] = None,
    timeout: Optional[float] = None,
    log_message: Optional[str] = None,
    validate: bool = True,
    scope: str = "DEFAULT"
) -> str:
    """
    Send a command to OpenC3 COSMOS
    
    Args:
        target_name: Target name (e.g., 'INST', 'INST2')
        command_name: Command name (e.g., 'COLLECT', 'ABORT')
        parameters: JSON string of command parameters (e.g., '{"TYPE": "NORMAL", "DURATION": 5.0}')
        timeout: Command timeout in seconds
        log_message: Optional log message
        validate: Whether to validate the command
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Command execution result
    
    Example:
        cosmos_cmd("INST", "COLLECT", '{"TYPE": "NORMAL", "DURATION": 5.0}')
    """
    try:
        # Parse parameters if provided
        params = {}
        if parameters:
            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON parameters: {parameters}"
        
        # Build kwargs for the command
        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout
        if log_message:
            kwargs['log_message'] = log_message
        kwargs['validate'] = validate
        kwargs['scope'] = scope
        
        # Send the command
        result = script.cmd(target_name, command_name, params, **kwargs)
        
        timestamp = datetime.now().isoformat()
        return f"Command sent successfully at {timestamp}\nTarget: {target_name}\nCommand: {command_name}\nParameters: {params}\nResult: {result}"
    except Exception as e:
        return f"Error sending command: {str(e)}"

@mcp.tool
async def cosmos_cmd_string(
    command_string: str,
    timeout: Optional[float] = None,
    log_message: Optional[str] = None,
    validate: bool = True,
    scope: str = "DEFAULT"
) -> str:
    """
    Send a command using COSMOS string syntax
    
    Args:
        command_string: Command in format "TARGET COMMAND with PARAM1 value, PARAM2 value"
        timeout: Command timeout in seconds
        log_message: Optional log message
        validate: Whether to validate the command
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Command execution result
    
    Example:
        cosmos_cmd_string("INST COLLECT with TYPE NORMAL, DURATION 5.0")
    """
    try:
        kwargs = {}
        if timeout is not None:
            kwargs['timeout'] = timeout
        if log_message:
            kwargs['log_message'] = log_message
        kwargs['validate'] = validate
        kwargs['scope'] = scope
        
        result = script.cmd(command_string, **kwargs)
        
        timestamp = datetime.now().isoformat()
        return f"Command sent successfully at {timestamp}\nCommand: {command_string}\nResult: {result}"
    except Exception as e:
        return f"Error sending command: {str(e)}"

@mcp.tool
async def cosmos_tlm(
    target_name: str,
    packet_name: str,
    item_name: str,
    value_type: str = "CONVERTED",
    scope: str = "DEFAULT"
) -> str:
    """
    Get telemetry value from OpenC3 COSMOS
    
    Args:
        target_name: Target name (e.g., 'INST')
        packet_name: Packet name (e.g., 'HEALTH_STATUS')
        item_name: Item name (e.g., 'TEMP1')
        value_type: Value type - CONVERTED, RAW, FORMATTED, WITH_UNITS (default: CONVERTED)
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Telemetry value
    """
    try:
        kwargs = {'type': value_type, 'scope': scope}
        value = script.tlm(target_name, packet_name, item_name, **kwargs)
        return f"{target_name} {packet_name} {item_name}: {value}"
    except Exception as e:
        return f"Error getting telemetry: {str(e)}"

@mcp.tool
async def cosmos_tlm_raw(
    target_name: str,
    packet_name: str,
    item_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get raw telemetry value from OpenC3 COSMOS
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Raw telemetry value
    """
    try:
        value = script.tlm_raw(target_name, packet_name, item_name, scope=scope)
        return f"{target_name} {packet_name} {item_name} (RAW): {value}"
    except Exception as e:
        return f"Error getting raw telemetry: {str(e)}"

@mcp.tool
async def cosmos_tlm_formatted(
    target_name: str,
    packet_name: str,
    item_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get formatted telemetry value from OpenC3 COSMOS
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Formatted telemetry value
    """
    try:
        value = script.tlm_formatted(target_name, packet_name, item_name, scope=scope)
        return f"{target_name} {packet_name} {item_name} (FORMATTED): {value}"
    except Exception as e:
        return f"Error getting formatted telemetry: {str(e)}"

@mcp.tool
async def cosmos_tlm_with_units(
    target_name: str,
    packet_name: str,
    item_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get telemetry value with units from OpenC3 COSMOS
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Telemetry value with units
    """
    try:
        value = script.tlm_with_units(target_name, packet_name, item_name, scope=scope)
        return f"{target_name} {packet_name} {item_name}: {value}"
    except Exception as e:
        return f"Error getting telemetry with units: {str(e)}"

# ===== Target and System Information Tools =====

@mcp.tool
async def cosmos_get_target_names(scope: str = "DEFAULT") -> str:
    """
    Get list of all available targets in OpenC3 COSMOS
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of target names
    """
    try:
        targets = script.get_target_names(scope=scope)
        return json.dumps(targets, indent=2)
    except Exception as e:
        return f"Error getting targets: {str(e)}"

@mcp.tool
async def cosmos_get_all_cmd_names(target_name: str, scope: str = "DEFAULT") -> str:
    """
    Get all command names for a specific target
    
    Args:
        target_name: Target name to get commands for
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of command names
    """
    try:
        # Use get_all_cmd_names which is the actual function name
        commands = script.get_all_cmd_names(target_name, scope=scope)
        return json.dumps(commands, indent=2)
    except Exception as e:
        return f"Error getting commands: {str(e)}"

@mcp.tool
async def cosmos_get_all_tlm(target_name: str, scope: str = "DEFAULT") -> str:
    """
    Get all telemetry packets and items for a specific target
    
    Args:
        target_name: Target name to get telemetry for
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON dict of telemetry packets and their items
    """
    try:
        # Use get_all_tlm instead of get_all_telemetry
        telemetry = script.get_all_tlm(target_name, scope=scope)
        # Convert to JSON-serializable format
        result = {}
        for packet_name, packet_data in telemetry.items():
            if isinstance(packet_data, dict):
                result[packet_name] = list(packet_data.keys())
            else:
                result[packet_name] = str(packet_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting telemetry: {str(e)}"

# ===== Limits Tools =====

@mcp.tool
async def cosmos_get_limits_sets(scope: str = "DEFAULT") -> str:
    """
    Get all available limits sets
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of limits set names
    """
    try:
        limits_sets = script.get_limits_sets(scope=scope)
        return json.dumps(limits_sets, indent=2)
    except Exception as e:
        return f"Error getting limits sets: {str(e)}"

@mcp.tool
async def cosmos_get_out_of_limits(scope: str = "DEFAULT") -> str:
    """
    Get all telemetry items currently out of limits
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of out-of-limits items
    """
    try:
        out_of_limits = script.get_out_of_limits(scope=scope)
        return json.dumps(out_of_limits, indent=2, default=str)
    except Exception as e:
        return f"Error getting out of limits: {str(e)}"

print(f"\nCosmos MCP Server (OAuth Protected) with OpenC3 tools registered")
print(f"OAuth Issuer URL: {issuer_url}")
print(f"OAuth Base URL: {base_url}")
print(f"OAuth Scopes: openid, profile, email")

if __name__ == "__main__":
    import asyncio
    mcp.run(transport="http", host="0.0.0.0", port=3443)