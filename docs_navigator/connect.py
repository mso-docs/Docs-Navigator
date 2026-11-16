"""Real MCP client configuration for Docs Navigator, generated from the server address."""

from __future__ import annotations

import json
import os

DEFAULT_SPACE_HOST = "mackenzietechdocs-docsnavigatormcp.hf.space"
SERVER_NAME = "docs-navigator"


def mcp_url(base: str | None = None) -> str:
    """Streamable HTTP endpoint that Gradio serves when launched with mcp_server=True."""
    if base is None:
        host = os.getenv("SPACE_HOST") or DEFAULT_SPACE_HOST
        base = f"https://{host}"
    return base.rstrip("/") + "/gradio_api/mcp/"


def _dump(data: dict) -> str:
    return json.dumps(data, indent=2)


def client_configs(url: str, script_path: str = "/path/to/Docs-Navigator/mcp_server.py") -> dict[str, dict]:
    """Return {client: {"hint": str, "language": str, "code": str}} for the hosted endpoint."""
    return {
        "Cursor": {
            "hint": "Add to `~/.cursor/mcp.json`, or `.cursor/mcp.json` inside a project.",
            "language": "json",
            "code": _dump({"mcpServers": {SERVER_NAME: {"url": url}}}),
        },
        "Claude Desktop": {
            "hint": "Add to `claude_desktop_config.json`. Needs Node.js for `npx mcp-remote`, which bridges a remote server to Claude Desktop.",
            "language": "json",
            "code": _dump({"mcpServers": {SERVER_NAME: {"command": "npx", "args": ["mcp-remote", url]}}}),
        },
        "Claude Code": {
            "hint": "Run once in a terminal.",
            "language": "shell",
            "code": f"claude mcp add --transport http {SERVER_NAME} {url}",
        },
        "VS Code": {
            "hint": "Add to `.vscode/mcp.json` in your workspace, or run “MCP: Add Server” from the Command Palette.",
            "language": "json",
            "code": _dump({"servers": {SERVER_NAME: {"type": "http", "url": url}}}),
        },
        "Your own docs (local)": {
            "hint": "Runs on your machine over stdio and reads your folder. Works in any client that launches a command; this shape is for Cursor and Claude Desktop.",
            "language": "json",
            "code": _dump(
                {
                    "mcpServers": {
                        SERVER_NAME: {
                            "command": "python",
                            "args": [script_path],
                            "env": {"DOCS_DIR": "/path/to/your/docs"},
                        }
                    }
                }
            ),
        },
    }
