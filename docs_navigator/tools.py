"""The tool functions shared by the Gradio MCP endpoint and the stdio MCP server."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from .corpus import Corpus

ROOT = Path(__file__).resolve().parent.parent
MAX_READ_CHARS = 60_000


@lru_cache(maxsize=1)
def get_corpus() -> Corpus:
    return Corpus(os.getenv("DOCS_DIR") or ROOT / "docs")


def list_docs() -> list[dict]:
    """List every document that can be searched, with its type and size.

    Returns:
        One entry per file: path relative to the docs folder, file type, character count, and number of searchable passages.
    """
    corpus = get_corpus()
    corpus.refresh()
    return corpus.list_docs()


def search_docs(query: str, max_results: int = 5, file: str = "") -> list[dict]:
    """Search the documentation and return the best matching passages, ranked.

    Args:
        query: Plain-language question or keywords, for example "how do I rotate an API key".
        max_results: How many passages to return, between 1 and 20.
        file: Optional path from list_docs. When given, only that file is searched.

    Returns:
        Passages with the file, section heading, relevance score, and full passage text.
    """
    limit = max(1, min(int(max_results), 20))
    hits = get_corpus().search(query, limit=limit, doc=file or None)
    return [h.as_dict() for h in hits]


def read_doc(file: str) -> str:
    """Read the full text of one document.

    Args:
        file: Path of the document as shown by list_docs, for example "text/setup.md".

    Returns:
        The document text, shortened with a note if it is very long.
    """
    text = get_corpus().read(file)
    if len(text) > MAX_READ_CHARS:
        return text[:MAX_READ_CHARS] + f"\n\n[Truncated after {MAX_READ_CHARS:,} of {len(text):,} characters. Use search_docs to find the part you need.]"
    return text
