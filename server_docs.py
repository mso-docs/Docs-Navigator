# server_docs.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict

from mcp.server.fastmcp import FastMCP

# Name your server – this is what clients see
mcp = FastMCP("DocsNavigator")

DOCS_ROOT = Path(__file__).parent / "docs"


def _iter_docs() -> list[Path]:
    exts = {".md", ".txt", ".rst"}
    return [
        p for p in DOCS_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in exts
    ]


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


@mcp.resource("docs://list")
def list_docs_resource() -> list[str]:
    """
    Resource that returns a simple list of available doc paths.
    """
    return [str(p.relative_to(DOCS_ROOT)) for p in _iter_docs()]


@mcp.resource("docs://{relative_path}")
def read_doc(relative_path: str) -> str:
    """
    Read a specific doc by relative path (e.g. 'getting-started.md').
    """
    path = (DOCS_ROOT / relative_path).resolve()
    if not path.exists() or not path.is_file():
        return f"Document not found: {relative_path}"
    if DOCS_ROOT not in path.parents and DOCS_ROOT != path.parent:
        return "Access denied: path escapes docs root."
    return _read_file(path)


@mcp.tool()
def list_docs() -> List[str]:
    """
    List available documentation files relative to the docs/ folder.
    """
    return [str(p.relative_to(DOCS_ROOT)) for p in _iter_docs()]


@mcp.tool()
def search_docs(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Naive full-text search over docs.

    Args:
        query: Search query string.
        max_results: Max number of matches to return.
    Returns:
        List of {path, snippet} matches.
    """
    query_lower = query.lower()
    results: list[dict[str, str]] = []

    for path in _iter_docs():
        text = _read_file(path)
        idx = text.lower().find(query_lower)
        if idx == -1:
            continue

        start = max(0, idx - 80)
        end = min(len(text), idx + 80)
        snippet = text[start:end].replace("\n", " ")
        results.append(
            {
                "path": str(path.relative_to(DOCS_ROOT)),
                "snippet": snippet,
            }
        )

        if len(results) >= max_results:
            break

    return results


if __name__ == "__main__":
    # stdio transport keeps it compatible with the official client pattern
    mcp.run(transport="stdio")
