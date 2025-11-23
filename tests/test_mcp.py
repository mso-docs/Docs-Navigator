#!/usr/bin/env python3
"""
Test script to verify MCP functionality works correctly.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from agent.client import DocsNavigatorClient

async def test_mcp_connection():
    """Test that we can connect to the MCP server and use its tools."""
    client = DocsNavigatorClient()
    
    try:
        print("Connecting to MCP server...")
        await client.connect("src/server/server.py")
        
        print("Listing available docs...")
        tools_response = await client.session.list_tools()
        print(f"Available tools: {[t.name for t in tools_response.tools]}")
        
        # Test the list_docs tool
        result = await client.session.call_tool("list_docs", {})
        print(f"Available docs: {result.content}")
        
        # Test search functionality
        search_result = await client.session.call_tool("search_docs", {"query": "setup", "max_results": 3})
        print(f"Search results for 'setup': {search_result.content}")
        
        print("✅ MCP connection and tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())