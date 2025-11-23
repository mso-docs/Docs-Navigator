#!/usr/bin/env python3
"""
Lightweight MCP server without heavy OCR models for faster startup
"""

import os
import sys
import subprocess
from contextlib import redirect_stdout, redirect_stderr

# Set environment variable to disable heavy OCR models
os.environ['DISABLE_TROCR'] = '1'

# Suppress all output to prevent JSON-RPC interference
class DevNull:
    def write(self, *args, **kwargs):
        pass
    def flush(self, *args, **kwargs):
        pass

if __name__ == "__main__":
    # Redirect all stdout/stderr during import to prevent progress bar interference
    with redirect_stdout(DevNull()), redirect_stderr(DevNull()):
        # Import and run server
        sys.path.insert(0, os.path.dirname(__file__))
        from src.server.server import mcp
        
    # Now run with clean stdio for JSON-RPC
    mcp.run(transport="stdio")