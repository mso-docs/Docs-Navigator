import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from docs_navigator import tools
from docs_navigator.connect import client_configs, mcp_url
from docs_navigator.corpus import Hit
from docs_navigator.llm import LLMUnavailable, answer_question, build_messages


def test_tool_functions():
    assert tools.list_docs()
    results = tools.search_docs("deployment", max_results=3)
    assert 1 <= len(results) <= 3 and {"file", "section", "score", "text"} <= set(results[0])
    first = tools.list_docs()[0]["file"]
    assert tools.read_doc(first)
    with pytest.raises(FileNotFoundError):
        tools.read_doc("missing.md")


def test_connect_configs_use_real_endpoint():
    url = mcp_url("http://127.0.0.1:7860")
    assert url == "http://127.0.0.1:7860/gradio_api/mcp/"
    configs = client_configs(url)
    assert json.loads(configs["Cursor"]["code"])["mcpServers"]["docs-navigator"]["url"] == url
    assert json.loads(configs["VS Code"]["code"])["servers"]["docs-navigator"]["type"] == "http"
    assert configs["Claude Code"]["code"].startswith("claude mcp add --transport http")


class _FakeChat(BaseHTTPRequestHandler):
    def do_POST(self):  # minimal OpenAI-compatible /chat/completions
        length = int(self.headers.get("content-length", 0))
        body = json.loads(self.rfile.read(length))
        assert self.headers.get("authorization") == "Bearer visitor-token"
        reply = {
            "id": "x", "object": "chat.completion", "created": 0, "model": body.get("model", "m"),
            "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "Use the deploy guide [1]."}}],
        }
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def test_answer_uses_visitor_token(monkeypatch):
    server = HTTPServer(("127.0.0.1", 0), _FakeChat)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("DOCSNAV_BASE_URL", f"http://127.0.0.1:{server.server_port}/v1")
    hits = [Hit("text/setup.md", "Install", 1.0, "Run the installer.", "Run the installer.")]
    result = answer_question("How do I install?", hits, token="visitor-token", models=["test/model"])
    assert "[1]" in result.text and result.model == "test/model"
    server.shutdown()


def test_answer_requires_token_and_passages():
    with pytest.raises(LLMUnavailable):
        answer_question("q", [Hit("a", "", 1, "t", "t")], token="")
    with pytest.raises(LLMUnavailable):
        answer_question("q", [], token="x")


def test_prompt_numbers_passages():
    msgs = build_messages("q?", [Hit("a.md", "H", 1, "alpha", "alpha"), Hit("b.md", "", 1, "beta", "beta")])
    assert "[1] a.md > H" in msgs[1]["content"] and "[2] b.md" in msgs[1]["content"]
