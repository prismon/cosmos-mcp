#!/usr/bin/env python
import asyncio
from server import mcp

async def main():
    # List all registered tools
    tools = await mcp.get_tools()
    print(f"Number of tools registered: {len(tools)}")
    print("\nRegistered tools:")
    for tool_name, tool_info in tools.items():
        print(f"  - {tool_name}")
        if 'description' in tool_info:
            print(f"    Description: {tool_info['description']}")

if __name__ == "__main__":
    asyncio.run(main())