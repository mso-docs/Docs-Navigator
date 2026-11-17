# Docs Navigator MCP

Search a folder of documentation and hand it to your AI tools over the Model Context Protocol (MCP). It runs as a web app you can try in a browser, as a hosted MCP endpoint, or as a local server that reads your own files.

- **Project page:** [mso-docs.github.io/Docs-Navigator](https://mso-docs.github.io/Docs-Navigator/)
- **Try it (live Space):** [mackenzietechdocs/DocsNavigatorMCP](https://huggingface.co/spaces/mackenzietechdocs/DocsNavigatorMCP) ([AI Lounge listing](https://ai.lounge.ai/@mackenzietechdocs/hf-docsnavigatormcp))
- **Original release (frozen Space):** [mackenzietechdocs/DocsNavigatorMCP-original](https://huggingface.co/spaces/mackenzietechdocs/DocsNavigatorMCP-original)
- **Collection:** [Docs Navigator](https://huggingface.co/collections/mackenzietechdocs/docs-navigator)
- **Portfolio:** [mso-docs.github.io/mac-portfolio](https://mso-docs.github.io/mac-portfolio/)
- **Original GitHub branch:** the first public tree, from December 2025, is on [`original-release`](https://github.com/mso-docs/Docs-Navigator/tree/original-release).

## What it does

| MCP tool | What it returns |
| --- | --- |
| `list_docs` | Every searchable file, with type, size, and passage count |
| `search_docs` | The best matching passages, ranked, with file and section |
| `read_doc` | The full text of one file |

Search is BM25 over passages split at headings and paragraphs. It reads Markdown, text, reStructuredText, PDF, and Excel files. It needs no API key and makes no network calls.

The web app adds an **Ask with AI** button. It sends the top passages to an open model through [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) and cites them as `[1]`, `[2]`. On the hosted Space, visitors sign in with Hugging Face, so calls use their own free monthly credits and nothing is billed to the author.

## Quickstart

Python 3.10 or newer.

```bash
git clone https://github.com/mso-docs/Docs-Navigator.git
cd Docs-Navigator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:7860. The MCP endpoint is http://127.0.0.1:7860/gradio_api/mcp/ and its tool schema is at `/gradio_api/mcp/schema`.

To search your own files, point `DOCS_DIR` at a folder:

```bash
DOCS_DIR=/path/to/your/docs python app.py
```

To use Ask with AI when you run it yourself, put a Hugging Face token with the “Make calls to Inference Providers” permission in `DOCSNAV_SERVER_TOKEN` (see `.env.example`).

## Connect an MCP client

Hosted endpoint: `https://mackenzietechdocs-docsnavigatormcp.hf.space/gradio_api/mcp/` (searches the sample Aurora AI docs).

**Cursor**: add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "docs-navigator": { "url": "https://mackenzietechdocs-docsnavigatormcp.hf.space/gradio_api/mcp/" }
  }
}
```

**Claude Code**:

```bash
claude mcp add --transport http docs-navigator https://mackenzietechdocs-docsnavigatormcp.hf.space/gradio_api/mcp/
```

**VS Code**: add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "docs-navigator": { "type": "http", "url": "https://mackenzietechdocs-docsnavigatormcp.hf.space/gradio_api/mcp/" }
  }
}
```

**Claude Desktop** (uses `mcp-remote`, which needs Node.js), in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docs-navigator": {
      "command": "npx",
      "args": ["mcp-remote", "https://mackenzietechdocs-docsnavigatormcp.hf.space/gradio_api/mcp/"]
    }
  }
}
```

**Your own docs, over stdio** (works in any client that launches a command):

```json
{
  "mcpServers": {
    "docs-navigator": {
      "command": "python",
      "args": ["/path/to/Docs-Navigator/mcp_server.py"],
      "env": { "DOCS_DIR": "/path/to/your/docs" }
    }
  }
}
```

Use the Python from the virtual environment where you installed the requirements.

## Project layout

```
app.py              Gradio web app; launches with mcp_server=True
mcp_server.py       Local stdio MCP server
docs_navigator/     corpus.py (index + search), llm.py (Ask), tools.py (MCP tools), connect.py (config snippets)
docs/               Sample documentation (Aurora AI, a fictional product)
tests/              Unit tests plus real MCP client round trips over HTTP and stdio
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests start the app and call it as an MCP client over HTTP and over stdio.

## Optional OCR

Scanned PDF pages are skipped unless OCR is available. Install the Tesseract and Poppler system packages, then `pip install -r requirements-ocr.txt`.

## License

MIT. See [LICENSE](LICENSE).
