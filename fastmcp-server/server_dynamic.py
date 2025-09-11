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

# List of functions to skip (internal, deprecated, or problematic)
SKIP_FUNCTIONS = {
    # Internal/private functions
    '_file_dialog',
    'current_functions',
    'extract_fields_from_check_text',
    'extract_fields_from_cmd_text', 
    'extract_fields_from_set_tlm_text',
    'extract_fields_from_tlm_text',
    'extract_string_kwargs_to_args',
    'initialize_offline_access',
    'offline_access_needed',
    'set_offline_access',
    'remove_quotes',
    'is_array',
    'is_float', 
    'is_hex',
    'is_int',
    'hex_to_byte_string',
    'convert_to_value',
    'normalize_tlm',
    
    # UI functions that don't work in headless mode
    'ask',
    'ask_string',
    'combo_box',
    'message_box',
    'vertical_message_box',
    'prompt',
    'open_file_dialog',
    'open_files_dialog',
    'cosmos_calendar',
    
    # Screen/display functions
    'clear_all_screens',
    'clear_screen',
    'create_screen',
    'delete_screen',
    'display_screen',
    'get_screen_definition',
    'get_screen_list',
    'local_screen',
    'screen',
    
    # Script runner specific
    'disconnect_script',
    'goto',
    'load_utility',
    'shutdown_script',
    'start',
    'step_mode',
    'run_mode',
    
    # Module references
    'contextmanager',
    'datetime',
    'exceptions',
    'func',
    'function',
    'io',
    'json',
    'method',
    'openc3',
    'os',
    're',
    'requests',
    'sys',
    'tempfile',
    'threading',
    'time',
    'typing',
    'storage',
    'code',
    
    # Classes and constants
    'ApiServerProxy',
    'ScriptServerProxy',
    'LocalMode',
    'Packet',
    'CheckError',
    'CriticalCmdError',
    'HazardousError',
    'SkipScript',
    'StopScript',
    'OpenC3KeycloakAuthentication',
    'Optional',
    
    # Constants
    'API_SERVER',
    'ARRAY_CHECK_REGEX',
    'DEFAULT_TLM_POLLING_RATE',
    'DISCONNECT',
    'FLOAT_CHECK_REGEX',
    'HEX_CHECK_REGEX',
    'INT_CHECK_REGEX',
    'LIMITS_METHODS',
    'OPENC3_CLOUD',
    'OPENC3_IN_CLUSTER',
    'OPENC3_KEYCLOAK_URL',
    'OPENC3_SCOPE',
    'RUNNING_SCRIPT',
    'SCANNING_REGULAR_EXPRESSION',
    'SCIENTIFIC_CHECK_REGEX',
    'SCRIPT_RUNNER_API_SERVER',
    'SPLIT_WITH_REGEX',
    'WHITELIST',
    
    # Wait/sleep functions that might block
    'openc3_script_sleep',
    'wait',
    'wait_check',
    'wait_check_expression',
    'wait_check_packet',
    'wait_check_tolerance',
    'wait_expression',
    'wait_packet',
    'wait_tolerance',
}

# Functions that need special handling or have complex signatures
CUSTOM_IMPLEMENTATIONS = {
    'cmd', 'cmd_raw', 'tlm', 'tlm_raw', 'tlm_formatted', 'tlm_with_units',
    'check', 'check_expression', 'check_formatted', 'check_raw', 'check_tolerance', 'check_with_units'
}

def create_openc3_tool(func_name: str, func_obj: Any):
    """Create an MCP tool wrapper for an OpenC3 script function"""
    
    # Get function signature and docstring
    sig = None
    doc = func_obj.__doc__ or f"OpenC3 function: {func_name}"
    
    try:
        sig = inspect.signature(func_obj)
    except (ValueError, TypeError):
        # Some functions don't have inspectable signatures
        pass
    
    # Create async wrapper
    async def tool_wrapper(**kwargs):
        """Dynamic wrapper for OpenC3 function"""
        try:
            # Convert any JSON strings back to proper types
            for key, value in kwargs.items():
                if isinstance(value, str) and value.startswith('{') or value.startswith('['):
                    try:
                        kwargs[key] = json.loads(value)
                    except:
                        pass  # Keep as string if not valid JSON
            
            # Call the OpenC3 function
            result = func_obj(**kwargs)
            
            # Convert result to JSON-serializable format
            if result is None:
                return f"Successfully executed {func_name}"
            elif isinstance(result, (str, int, float, bool)):
                return str(result)
            elif isinstance(result, (list, dict)):
                return json.dumps(result, indent=2)
            else:
                return str(result)
                
        except Exception as e:
            return f"Error executing {func_name}: {str(e)}"
    
    # Set function metadata
    tool_wrapper.__name__ = f"openc3_{func_name}"
    tool_wrapper.__doc__ = doc
    
    return tool_wrapper

# Register OpenC3 functions as tools
print("Registering OpenC3 functions as MCP tools...")
registered_count = 0
skipped_count = 0

for name in dir(script):
    # Skip private/internal functions
    if name.startswith('_'):
        skipped_count += 1
        continue
        
    # Skip items in skip list
    if name in SKIP_FUNCTIONS:
        skipped_count += 1
        continue
    
    # Skip items that need custom implementation (we'll handle these separately)
    if name in CUSTOM_IMPLEMENTATIONS:
        continue
        
    obj = getattr(script, name)
    
    # Only register callable functions
    if callable(obj) and not inspect.isclass(obj):
        try:
            tool_func = create_openc3_tool(name, obj)
            mcp.tool(tool_func)
            registered_count += 1
            print(f"  ✓ Registered: openc3_{name}")
        except Exception as e:
            print(f"  ✗ Failed to register {name}: {e}")
            skipped_count += 1

# Add custom implementations for complex functions
@mcp.tool
async def openc3_cmd(
    target_name: str = None,
    command_name: str = None,
    command_params: Optional[Dict[str, Any]] = None,
    command_string: str = None,
    **kwargs
) -> str:
    """
    Send a command to OpenC3 COSMOS
    
    Can be called in two ways:
    1. With target_name, command_name, and optional command_params dict
    2. With command_string in format "TARGET COMMAND with PARAM1 value, PARAM2 value"
    
    Args:
        target_name: Target name (e.g., 'INST', 'INST2')
        command_name: Command name
        command_params: Optional dict of command parameters
        command_string: Alternative string format for the command
        **kwargs: Additional options like timeout, log_message, etc.
    
    Returns:
        Command execution result
    """
    try:
        if command_string:
            result = script.cmd(command_string, **kwargs)
        elif target_name and command_name:
            if command_params:
                result = script.cmd(target_name, command_name, command_params, **kwargs)
            else:
                result = script.cmd(target_name, command_name, **kwargs)
        else:
            return "Error: Must provide either command_string or target_name + command_name"
        
        return f"Command sent successfully: {result}"
    except Exception as e:
        return f"Error sending command: {str(e)}"

@mcp.tool
async def openc3_tlm(
    target_name: str,
    packet_name: str,
    item_name: str,
    **kwargs
) -> str:
    """
    Get telemetry value from OpenC3 COSMOS
    
    Args:
        target_name: Target name (e.g., 'INST', 'INST2')
        packet_name: Packet name (e.g., 'HEALTH_STATUS')
        item_name: Item name (e.g., 'TEMP1')
        **kwargs: Additional options
    
    Returns:
        Telemetry value
    """
    try:
        value = script.tlm(target_name, packet_name, item_name, **kwargs)
        return f"{item_name}: {value}"
    except Exception as e:
        return f"Error getting telemetry: {str(e)}"

@mcp.tool
async def openc3_check(
    target_name: str,
    packet_name: str,
    item_name: str,
    comparison: str,
    value: Any,
    **kwargs
) -> str:
    """
    Check telemetry value against expected value
    
    Args:
        target_name: Target name
        packet_name: Packet name
        item_name: Item name
        comparison: Comparison operator (==, !=, >, <, >=, <=)
        value: Expected value
        **kwargs: Additional options like timeout
    
    Returns:
        Check result
    """
    try:
        script.check(target_name, packet_name, item_name, comparison, value, **kwargs)
        return f"Check passed: {item_name} {comparison} {value}"
    except Exception as e:
        return f"Check failed: {str(e)}"

@mcp.tool
async def openc3_get_target_list() -> str:
    """
    Get list of all available targets in OpenC3 COSMOS
    
    Returns:
        JSON list of target names
    """
    try:
        targets = script.get_target_names()
        return json.dumps(targets, indent=2)
    except Exception as e:
        return f"Error getting targets: {str(e)}"

@mcp.tool
async def openc3_get_all_commands(target_name: str) -> str:
    """
    Get all commands for a specific target
    
    Args:
        target_name: Target name to get commands for
    
    Returns:
        JSON list of command names
    """
    try:
        commands = script.get_all_command_names(target_name)
        return json.dumps(commands, indent=2)
    except Exception as e:
        return f"Error getting commands: {str(e)}"

@mcp.tool
async def openc3_get_all_telemetry(target_name: str) -> str:
    """
    Get all telemetry items for a specific target
    
    Args:
        target_name: Target name to get telemetry for
    
    Returns:
        JSON dict of telemetry packets and items
    """
    try:
        telemetry = script.get_all_telemetry(target_name)
        # Convert to JSON-serializable format
        result = {}
        for packet_name, packet_data in telemetry.items():
            result[packet_name] = list(packet_data.keys()) if isinstance(packet_data, dict) else str(packet_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting telemetry: {str(e)}"

print(f"\nTotal OpenC3 functions registered: {registered_count + 6}")  # +6 for custom implementations
print(f"Total functions skipped: {skipped_count}")

if __name__ == "__main__":
    import asyncio
    mcp.run(transport="http", host="0.0.0.0", port=3443)