#!/usr/bin/env python3
"""Run Docs Navigator as a local stdio MCP server over your own folder of docs.

    DOCS_DIR=/path/to/your/docs python mcp_server.py
"""

from mcp.server.fastmcp import FastMCP

from docs_navigator import tools

mcp = FastMCP("Docs Navigator")
mcp.tool()(tools.list_docs)
mcp.tool()(tools.search_docs)
mcp.tool()(tools.read_doc)

if __name__ == "__main__":
    mcp.run()
