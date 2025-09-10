#!/usr/bin/env python
"""Test MCP client to verify tools are accessible"""
import asyncio
import aiohttp
import json

async def test_mcp_tools():
    """Test if tools are accessible via MCP protocol"""
    url = "http://localhost:3443/mcp"
    
    # Test tool invocation with ping
    async with aiohttp.ClientSession() as session:
        # First, we need to establish a session
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        print("Testing ping tool invocation...")
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "ping",
                "arguments": {"host": "test"}
            },
            "id": 1
        }
        
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"Response status: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())