from fastmcp import FastMCP
from datetime import datetime
import asyncio
import os
import inspect
import json
from typing import Any, Dict, Optional, List, Union
from openc3 import script

# NOTE: Environment variables must be set BEFORE importing openc3
# Use start_server.py to run this server with proper configuration

mcp = FastMCP("Cosmos MCP Server")

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

# ===== Check Tools =====

@mcp.tool
async def cosmos_check(
    target_name: str,
    packet_name: str,
    item_name: str,
    comparison: str,
    expected_value: str,
    timeout: float = 5.0,
    scope: str = "DEFAULT"
) -> str:
    """
    Check telemetry value against expected value
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        comparison: Comparison operator (==, !=, >, <, >=, <=)
        expected_value: Expected value (will be converted to appropriate type)
        timeout: Check timeout in seconds (default: 5.0)
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Check result
    """
    try:
        # Try to convert expected_value to appropriate type
        try:
            if '.' in expected_value:
                expected_value = float(expected_value)
            else:
                expected_value = int(expected_value)
        except ValueError:
            # Keep as string if not numeric
            pass
        
        script.check(target_name, packet_name, item_name, comparison, expected_value, timeout=timeout, scope=scope)
        return f"Check passed: {target_name} {packet_name} {item_name} {comparison} {expected_value}"
    except Exception as e:
        return f"Check failed: {str(e)}"

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
async def cosmos_get_target(target_name: str, scope: str = "DEFAULT") -> str:
    """
    Get detailed information about a specific target
    
    Args:
        target_name: Target name to get info for
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON with target information
    """
    try:
        target_info = script.get_target(target_name, scope=scope)
        return json.dumps(target_info, indent=2, default=str)
    except Exception as e:
        return f"Error getting target info: {str(e)}"

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
async def cosmos_get_cmd(
    target_name: str,
    command_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get detailed information about a specific command
    
    Args:
        target_name: Target name
        command_name: Command name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON with command information including parameters
    """
    try:
        # get_cmd returns command definition
        cmd_info = script.get_cmd(target_name, command_name, scope=scope)
        return json.dumps(cmd_info, indent=2, default=str)
    except Exception as e:
        return f"Error getting command info: {str(e)}"

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

@mcp.tool
async def cosmos_get_item(
    target_name: str,
    packet_name: str,
    item_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get detailed information about a specific telemetry item
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON with telemetry item information
    """
    try:
        # get_item takes target, packet, item as separate args
        item_info = script.get_item(target_name, packet_name, item_name, scope=scope)
        return json.dumps(item_info, indent=2, default=str)
    except Exception as e:
        return f"Error getting item info: {str(e)}"

# ===== Interface and Router Tools =====

@mcp.tool
async def cosmos_get_interface_names(scope: str = "DEFAULT") -> str:
    """
    Get list of all interface names
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of interface names
    """
    try:
        interfaces = script.get_interface_names(scope=scope)
        return json.dumps(interfaces, indent=2)
    except Exception as e:
        return f"Error getting interfaces: {str(e)}"

@mcp.tool
async def cosmos_get_interface(interface_name: str, scope: str = "DEFAULT") -> str:
    """
    Get detailed information about a specific interface
    
    Args:
        interface_name: Interface name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON with interface information
    """
    try:
        interface_info = script.get_interface(interface_name, scope=scope)
        return json.dumps(interface_info, indent=2, default=str)
    except Exception as e:
        return f"Error getting interface info: {str(e)}"

@mcp.tool
async def cosmos_get_router_names(scope: str = "DEFAULT") -> str:
    """
    Get list of all router names
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of router names
    """
    try:
        routers = script.get_router_names(scope=scope)
        return json.dumps(routers, indent=2)
    except Exception as e:
        return f"Error getting routers: {str(e)}"

@mcp.tool
async def cosmos_connect_interface(
    interface_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Connect a specific interface
    
    Args:
        interface_name: Interface name to connect
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Connection status
    """
    try:
        script.connect_interface(interface_name, scope=scope)
        return f"Successfully connected interface: {interface_name}"
    except Exception as e:
        return f"Error connecting interface: {str(e)}"

@mcp.tool
async def cosmos_disconnect_interface(
    interface_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Disconnect a specific interface
    
    Args:
        interface_name: Interface name to disconnect
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Disconnection status
    """
    try:
        script.disconnect_interface(interface_name, scope=scope)
        return f"Successfully disconnected interface: {interface_name}"
    except Exception as e:
        return f"Error disconnecting interface: {str(e)}"

# ===== Limits Tools =====

@mcp.tool
async def cosmos_get_limits(
    target_name: str,
    packet_name: str,
    item_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get limits information for a telemetry item
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON with limits information
    """
    try:
        limits_info = script.get_limits(target_name, packet_name, item_name, scope=scope)
        return json.dumps(limits_info, indent=2, default=str)
    except Exception as e:
        return f"Error getting limits: {str(e)}"

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
async def cosmos_get_limits_set(scope: str = "DEFAULT") -> str:
    """
    Get the currently active limits set
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Current limits set name
    """
    try:
        current_set = script.get_limits_set(scope=scope)
        return f"Current limits set: {current_set}"
    except Exception as e:
        return f"Error getting current limits set: {str(e)}"

@mcp.tool
async def cosmos_set_limits_set(
    limits_set_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Set the active limits set
    
    Args:
        limits_set_name: Name of limits set to activate
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Status message
    """
    try:
        script.set_limits_set(limits_set_name, scope=scope)
        return f"Successfully set limits set to: {limits_set_name}"
    except Exception as e:
        return f"Error setting limits set: {str(e)}"

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

@mcp.tool
async def cosmos_get_overall_limits_state(
    ignored_items: Optional[str] = None,
    scope: str = "DEFAULT"
) -> str:
    """
    Get the overall system limits state
    
    Args:
        ignored_items: JSON list of items to ignore (e.g., '[["TGT", "PKT", "ITEM"], ...]')
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Overall limits state (GREEN, YELLOW, RED)
    """
    try:
        ignored = []
        if ignored_items:
            try:
                ignored = json.loads(ignored_items)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON for ignored_items: {ignored_items}"
        
        state = script.get_overall_limits_state(ignored, scope=scope)
        return f"Overall limits state: {state}"
    except Exception as e:
        return f"Error getting overall limits state: {str(e)}"

# ===== Packet and Command Count Tools =====

@mcp.tool
async def cosmos_get_tlm_cnt(
    target_name: str,
    packet_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get telemetry packet receive count
    
    Args:
        target_name: Target name
        packet_name: Packet name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Packet receive count
    """
    try:
        count = script.get_tlm_cnt(target_name, packet_name, scope=scope)
        return f"{target_name} {packet_name} receive count: {count}"
    except Exception as e:
        return f"Error getting telemetry count: {str(e)}"

@mcp.tool
async def cosmos_get_cmd_cnt(
    target_name: str,
    command_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get command send count
    
    Args:
        target_name: Target name
        command_name: Command name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Command send count
    """
    try:
        count = script.get_cmd_cnt(target_name, command_name, scope=scope)
        return f"{target_name} {command_name} send count: {count}"
    except Exception as e:
        return f"Error getting command count: {str(e)}"

# ===== Settings Tools =====

@mcp.tool
async def cosmos_get_setting(
    setting_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get a COSMOS setting value
    
    Args:
        setting_name: Name of the setting
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Setting value
    """
    try:
        value = script.get_setting(setting_name, scope=scope)
        return f"{setting_name}: {value}"
    except Exception as e:
        return f"Error getting setting: {str(e)}"

@mcp.tool
async def cosmos_get_all_settings(scope: str = "DEFAULT") -> str:
    """
    Get all COSMOS settings
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON dict of all settings
    """
    try:
        settings = script.get_all_settings(scope=scope)
        return json.dumps(settings, indent=2, default=str)
    except Exception as e:
        return f"Error getting settings: {str(e)}"

@mcp.tool
async def cosmos_list_settings(scope: str = "DEFAULT") -> str:
    """
    List all available setting names
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of setting names
    """
    try:
        settings_list = script.list_settings(scope=scope)
        return json.dumps(settings_list, indent=2)
    except Exception as e:
        return f"Error listing settings: {str(e)}"

# ===== Stash (Key-Value Store) Tools =====

@mcp.tool
async def cosmos_stash_set(
    key: str,
    value: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Store a value in the COSMOS stash (key-value store)
    
    Args:
        key: Key to store the value under
        value: Value to store (will be JSON parsed if possible)
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Status message
    """
    try:
        # Try to parse as JSON for complex types
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        script.stash_set(key, parsed_value, scope=scope)
        return f"Successfully stored value for key: {key}"
    except Exception as e:
        return f"Error storing stash value: {str(e)}"

@mcp.tool
async def cosmos_stash_get(
    key: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get a value from the COSMOS stash (key-value store)
    
    Args:
        key: Key to retrieve
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Stored value
    """
    try:
        value = script.stash_get(key, scope=scope)
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2)
        return str(value)
    except Exception as e:
        return f"Error getting stash value: {str(e)}"

@mcp.tool
async def cosmos_stash_keys(scope: str = "DEFAULT") -> str:
    """
    Get all keys in the COSMOS stash
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON list of stash keys
    """
    try:
        keys = script.stash_keys(scope=scope)
        return json.dumps(keys, indent=2)
    except Exception as e:
        return f"Error getting stash keys: {str(e)}"

@mcp.tool
async def cosmos_stash_delete(
    key: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Delete a key from the COSMOS stash
    
    Args:
        key: Key to delete
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Status message
    """
    try:
        script.stash_delete(key, scope=scope)
        return f"Successfully deleted key: {key}"
    except Exception as e:
        return f"Error deleting stash key: {str(e)}"

@mcp.tool
async def cosmos_stash_all(scope: str = "DEFAULT") -> str:
    """
    Get all key-value pairs from the COSMOS stash
    
    Args:
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON dict of all stash entries
    """
    try:
        all_stash = script.stash_all(scope=scope)
        return json.dumps(all_stash, indent=2, default=str)
    except Exception as e:
        return f"Error getting all stash entries: {str(e)}"

# ===== Metadata Tools =====

@mcp.tool
async def cosmos_metadata_set(
    target_name: str,
    packet_name: str,
    item_name: str,
    key: str,
    value: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Set metadata for a telemetry item
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        key: Metadata key
        value: Metadata value
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Status message
    """
    try:
        script.metadata_set(target_name, packet_name, item_name, key, value, scope=scope)
        return f"Successfully set metadata for {target_name} {packet_name} {item_name}: {key}={value}"
    except Exception as e:
        return f"Error setting metadata: {str(e)}"

@mcp.tool
async def cosmos_metadata_get(
    target_name: str,
    packet_name: str,
    item_name: str,
    key: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get metadata value for a telemetry item
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        key: Metadata key
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        Metadata value
    """
    try:
        value = script.metadata_get(target_name, packet_name, item_name, key, scope=scope)
        return f"{key}: {value}"
    except Exception as e:
        return f"Error getting metadata: {str(e)}"

@mcp.tool
async def cosmos_metadata_all(
    target_name: str,
    packet_name: str,
    item_name: str,
    scope: str = "DEFAULT"
) -> str:
    """
    Get all metadata for a telemetry item
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        scope: COSMOS scope (default: DEFAULT)
    
    Returns:
        JSON dict of all metadata
    """
    try:
        metadata = script.metadata_all(target_name, packet_name, item_name, scope=scope)
        return json.dumps(metadata, indent=2, default=str)
    except Exception as e:
        return f"Error getting all metadata: {str(e)}"

print(f"\nCosmos MCP Server with {len([name for name in dir(mcp) if name.startswith('openc3_') or name.startswith('cosmos_')])} OpenC3 tools registered")

if __name__ == "__main__":
    import asyncio
    mcp.run(transport="http", host="0.0.0.0", port=3443)