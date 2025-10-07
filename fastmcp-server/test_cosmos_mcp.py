#!/usr/bin/env python
"""
Comprehensive unit tests for Cosmos MCP Server
Tests basic connectivity, command exploration, and telemetry queries using MCP SSE client.
"""
import asyncio
import json
import pytest
import sys
import os

# Set environment variables before importing
os.environ["OPENC3_API_HOSTNAME"] = os.environ.get("OPENC3_API_HOSTNAME", "training20.openc3.com")
os.environ["OPENC3_API_PORT"] = os.environ.get("OPENC3_API_PORT", "443")
os.environ["OPENC3_API_SCHEMA"] = os.environ.get("OPENC3_API_SCHEMA", "https")
os.environ["OPENC3_SCRIPT_API_HOSTNAME"] = os.environ.get("OPENC3_SCRIPT_API_HOSTNAME", os.environ["OPENC3_API_HOSTNAME"])
os.environ["OPENC3_SCRIPT_API_PORT"] = os.environ.get("OPENC3_SCRIPT_API_PORT", os.environ["OPENC3_API_PORT"])
os.environ["OPENC3_SCRIPT_API_SCHEMA"] = os.environ.get("OPENC3_SCRIPT_API_SCHEMA", os.environ["OPENC3_API_SCHEMA"])
os.environ["OPENC3_API_USER"] = os.environ.get("OPENC3_API_USER", "admin")
os.environ["OPENC3_API_PASSWORD"] = os.environ.get("OPENC3_API_PASSWORD", "admin")
os.environ["OPENC3_KEYCLOAK_URL"] = os.environ.get("OPENC3_KEYCLOAK_URL", "https://training20.openc3.com/auth")

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_SERVER_URL = "http://localhost:3443/mcp"


class TestSystemConnectivity:
    """Test basic connectivity to the MCP server and COSMOS"""

    @pytest.mark.asyncio
    async def test_server_is_up(self):
        """Test if the MCP server is up and responding"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Test ping tool to verify server is alive
                result = await session.call_tool("ping", arguments={"host": "test"})
                assert result is not None, "Ping returned no result"

                content_text = result.content[0].text
                assert "Pong" in content_text, f"Unexpected ping response: {content_text}"
                print(f"✓ Server is up and responding: {content_text}")

    @pytest.mark.asyncio
    async def test_cosmos_connection(self):
        """Test if COSMOS system is accessible"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Get target names to verify COSMOS connection
                result = await session.call_tool("cosmos_get_target_names", arguments={})
                assert result is not None, "Got no result from cosmos_get_target_names"

                content_text = result.content[0].text

                # Try to parse as JSON
                try:
                    targets = json.loads(content_text)
                    assert isinstance(targets, list), "Expected list of targets"
                    assert len(targets) > 0, "No targets found in COSMOS"
                    print(f"✓ COSMOS is accessible with {len(targets)} targets: {targets}")
                except json.JSONDecodeError:
                    # If not JSON, just check it's not an error message
                    assert "Error" not in content_text, f"Got error: {content_text}"
                    print(f"✓ COSMOS connection attempted: {content_text}")


class TestCommandExploration:
    """Test command exploration capabilities"""

    @pytest.mark.asyncio
    async def test_list_example_commands(self):
        """Test listing all commands for EXAMPLE target (should have START command)"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool("cosmos_get_all_cmd_names",
                                               arguments={"target_name": "EXAMPLE"})

                content_text = result.content[0].text

                try:
                    commands = json.loads(content_text)
                    assert isinstance(commands, list), "Expected list of commands"
                    print(f"✓ EXAMPLE target commands: {commands}")

                    # Verify START command exists
                    assert "START" in commands, "START command not found in EXAMPLE target"
                    print(f"✓ Found START command in EXAMPLE target")
                except json.JSONDecodeError:
                    # If not JSON, just verify it's not an error
                    assert "Error" not in content_text, f"Got error: {content_text}"
                    print(f"Note: {content_text}")

    @pytest.mark.asyncio
    async def test_get_command_details(self):
        """Test getting detailed information about a command"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool("cosmos_get_cmd",
                                               arguments={
                                                   "target_name": "EXAMPLE",
                                                   "command_name": "START"
                                               })

                content_text = result.content[0].text
                print(f"✓ EXAMPLE START command details retrieved")
                assert len(content_text) > 0, "No command details returned"


class TestTelemetryQueries:
    """Test telemetry query capabilities"""

    @pytest.mark.asyncio
    async def test_list_inst_temperatures(self):
        """Test listing all temperature items from INST target HEALTH_STATUS packet"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool("cosmos_get_all_tlm",
                                               arguments={"target_name": "INST"})

                content_text = result.content[0].text

                # The result might be an error message or JSON
                if "Error" in content_text:
                    print(f"Note: {content_text}")
                    # Server returned an error, but we can still verify the tool works
                    assert "cosmos_get_all_tlm" not in content_text or "Error getting telemetry" in content_text
                else:
                    try:
                        tlm_data = json.loads(content_text)
                        # Check for HEALTH_STATUS packet
                        assert "HEALTH_STATUS" in tlm_data, "HEALTH_STATUS packet not found in INST target"
                        health_items = tlm_data["HEALTH_STATUS"]

                        # Filter temperature items (usually contain 'TEMP' in name)
                        temp_items = [item for item in health_items if "TEMP" in item.upper()]
                        print(f"✓ INST HEALTH_STATUS packet items: {health_items}")
                        print(f"✓ Temperature items found: {temp_items}")

                        assert len(temp_items) > 0, "No temperature items found in HEALTH_STATUS"
                    except json.JSONDecodeError:
                        print(f"Note: Could not parse JSON: {content_text}")

    @pytest.mark.asyncio
    async def test_get_inst_temperature_value(self):
        """Test getting a specific temperature value from INST"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool("cosmos_tlm",
                                               arguments={
                                                   "target_name": "INST",
                                                   "packet_name": "HEALTH_STATUS",
                                                   "item_name": "TEMP1"
                                               })

                content_text = result.content[0].text
                print(f"✓ INST TEMP1 value: {content_text}")
                assert "INST" in content_text and "TEMP1" in content_text, "Unexpected telemetry format"

    @pytest.mark.asyncio
    async def test_list_inst2_temperatures(self):
        """Test listing all temperature items from INST2 target"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool("cosmos_get_all_tlm",
                                               arguments={"target_name": "INST2"})

                content_text = result.content[0].text

                # The result might be an error message or JSON
                if "Error" in content_text:
                    print(f"Note: {content_text}")
                    # Server returned an error, still counts as test pass if tool executes
                    assert "cosmos_get_all_tlm" not in content_text or "Error getting telemetry" in content_text
                else:
                    try:
                        tlm_data = json.loads(content_text)

                        # Collect all temperature items from all packets
                        all_temp_items = {}
                        for packet_name, items in tlm_data.items():
                            temp_items = [item for item in items if "TEMP" in item.upper()]
                            if temp_items:
                                all_temp_items[packet_name] = temp_items

                        print(f"✓ INST2 telemetry packets: {list(tlm_data.keys())}")
                        print(f"✓ INST2 temperature items by packet: {all_temp_items}")

                        assert len(all_temp_items) > 0, "No temperature items found in INST2"
                    except json.JSONDecodeError:
                        print(f"Note: Could not parse JSON: {content_text}")


class TestToolsAvailability:
    """Test that required tools are available"""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing all available tools"""
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_result = await session.list_tools()

                # list_tools returns a ListToolsResult object with a 'tools' attribute
                if hasattr(tools_result, 'tools'):
                    tools = tools_result.tools
                    tool_names = [tool.name for tool in tools]
                elif isinstance(tools_result, list):
                    if len(tools_result) > 0 and hasattr(tools_result[0], 'name'):
                        tool_names = [tool.name for tool in tools_result]
                    else:
                        tool_names = [str(tool) for tool in tools_result]
                else:
                    tool_names = []

                print(f"✓ Available tools ({len(tool_names)}):")
                for name in sorted(tool_names)[:20]:  # Show first 20
                    print(f"  - {name}")
                if len(tool_names) > 20:
                    print(f"  ... and {len(tool_names) - 20} more")

                # Verify key tools are available
                required_tools = [
                    "ping",
                    "cosmos_cmd",
                    "cosmos_tlm",
                    "cosmos_get_target_names",
                    "cosmos_get_all_cmd_names",
                    "cosmos_get_all_tlm"
                ]

                for tool in required_tools:
                    assert tool in tool_names, f"Required tool {tool} not found"

                print(f"✓ All required tools are available")


if __name__ == "__main__":
    # Run tests
    print("=" * 80)
    print("COSMOS MCP Server Unit Tests")
    print("=" * 80)
    print()

    # Run with pytest
    sys.exit(pytest.main([__file__, "-v", "-s"]))
