from fastmcp import FastMCP
from datetime import datetime
import asyncio
import os
from openc3 import script

# NOTE: Environment variables must be set BEFORE importing openc3
# Use start_server.py to run this server with proper configuration

mcp = FastMCP("Cosmos MCP Server")

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

@mcp.tool
async def send_command(
    target_name: str,
    command_name: str,
    parameters: dict | None = None
) -> str:
    """
    Send a command to a COSMOS target
    
    Args:
        target_name: Name of the target (e.g., 'INST', 'INST2')
        command_name: Name of the command to send
        parameters: Optional dictionary of command parameters
    
    Returns:
        Success message with command details
    
    Example:
        send_command("INST", "COLLECT", {"TYPE": "NORMAL", "DURATION": 5.0})
    """
    try:
        if parameters is None:
            parameters = {}
        
        # Send the command using OpenC3 script API
        result = script.cmd(target_name, command_name, parameters)
        
        timestamp = datetime.now().isoformat()
        return f"Command sent successfully at {timestamp}\nTarget: {target_name}\nCommand: {command_name}\nParameters: {parameters}\nResult: {result}"
    except Exception as e:
        return f"Error sending command: {str(e)}\nTarget: {target_name}\nCommand: {command_name}\nParameters: {parameters}"

@mcp.tool
async def send_command_string(command_string: str) -> str:
    """
    Send a command using COSMOS string syntax
    
    Args:
        command_string: Command string in format "TARGET_NAME COMMAND_NAME with PARAM1 value1, PARAM2 value2"
    
    Returns:
        Success message with command details
    
    Example:
        send_command_string("INST COLLECT with TYPE NORMAL, DURATION 5.0")
    """
    try:
        # Send the command using OpenC3 script API string format
        result = script.cmd(command_string)
        
        timestamp = datetime.now().isoformat()
        return f"Command sent successfully at {timestamp}\nCommand string: {command_string}\nResult: {result}"
    except Exception as e:
        return f"Error sending command: {str(e)}\nCommand string: {command_string}"

if __name__ == "__main__":
    import asyncio
    mcp.run(transport="http", host="0.0.0.0", port=3443)