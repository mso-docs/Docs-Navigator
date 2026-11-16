"""Starts the real app and talks to it as an MCP client, over HTTP and over stdio."""

import asyncio
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

ROOT = Path(__file__).resolve().parent.parent
TOOLS = {"list_docs", "search_docs", "read_doc"}


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    port = _free_port()
    env = {**os.environ, "GRADIO_SERVER_PORT": str(port), "HF_TOKEN": "", "HF_HUB_DISABLE_TELEMETRY": "1", "GRADIO_ANALYTICS_ENABLED": "False"}
    proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            urllib.request.urlopen(base, timeout=1)
            break
        except Exception:
            time.sleep(1)
    else:
        proc.kill()
        pytest.fail("app did not start")
    yield base
    proc.terminate()


def test_schema_endpoint_lists_only_our_tools(server):
    import json

    schema = json.load(urllib.request.urlopen(server + "/gradio_api/mcp/schema"))
    assert {t["name"] for t in schema} == TOOLS


def test_http_mcp_roundtrip(server):
    async def run():
        async with streamable_http_client(server + "/gradio_api/mcp/") as (r, w, _):
            async with ClientSession(r, w) as session:
                await session.initialize()
                assert {t.name for t in (await session.list_tools()).tools} == TOOLS
                res = await session.call_tool("search_docs", {"query": "deployment", "max_results": 2})
                assert not res.isError and "file" in res.content[0].text

    asyncio.run(run())


def test_stdio_mcp_roundtrip():
    async def run():
        params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"], cwd=str(ROOT))
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                assert {t.name for t in (await session.list_tools()).tools} == TOOLS
                res = await session.call_tool("search_docs", {"query": "configuration"})
                assert not res.isError

    asyncio.run(run())
