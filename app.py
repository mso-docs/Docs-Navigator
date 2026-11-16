#!/usr/bin/env python3
"""Docs Navigator MCP: a searchable documentation set that is also an MCP server.

Run locally:   python app.py
MCP endpoint:  http://127.0.0.1:7860/gradio_api/mcp/   (schema at /gradio_api/mcp/schema)
"""

from __future__ import annotations

import html
import os

import gradio as gr
from dotenv import load_dotenv

from docs_navigator import __version__, tools
from docs_navigator.connect import client_configs, mcp_url
from docs_navigator.llm import LLMUnavailable, answer_question, configured_models

load_dotenv()

TITLE = "Docs Navigator MCP"
TAGLINE = "Search a documentation set, then plug it into Cursor, Claude, or VS Code over MCP."
EXAMPLES = ["How do I deploy Aurora AI?", "context window size", "troubleshooting API timeouts", "safety guardrails"]
SERVER_TOKEN = os.getenv("DOCSNAV_SERVER_TOKEN", "")  # self-hosting only; never set on the public Space
# "Sign in with Hugging Face" only works on a Space. Locally Gradio would need a logged-in machine,
# so the button stays off unless DOCSNAV_ENABLE_LOGIN=1.
LOGIN = bool(os.getenv("SPACE_ID")) or os.getenv("DOCSNAV_ENABLE_LOGIN") == "1"

CSS = """
:root { --dn-indigo-950:#1e1b4b; --dn-indigo-700:#4338ca; --dn-indigo-600:#4f46e5; --dn-indigo-500:#6366f1; --dn-indigo-100:#e0e7ff; --dn-indigo-50:#eef2ff; }
.gradio-container { width: 100% !important; min-width: 0 !important; max-width: 1040px !important; margin: 0 auto !important; box-sizing: border-box; font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
footer { display: none !important; }
@media (max-width: 640px) {
  #dn-hero { padding: 20px 18px 18px; border-radius: 14px; }
  #dn-hero h1 { font-size: 1.45rem; }
  .dn-file { word-break: break-all; }
}
#dn-hero { background: linear-gradient(135deg, var(--dn-indigo-950) 0%, var(--dn-indigo-700) 60%, var(--dn-indigo-500) 100%); color: #fff; border-radius: 18px; padding: 28px 30px 24px; margin-bottom: 14px; }
#dn-hero h1 { margin: 0 0 6px; font-size: 1.9rem; letter-spacing: -0.02em; color: #fff; }
#dn-hero p { margin: 0; color: var(--dn-indigo-100); font-size: 1.02rem; max-width: 46rem; }
#dn-hero .brand { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
#dn-hero .chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:16px; }
#dn-hero .chip { background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25); color:#fff; border-radius:999px; padding:3px 12px; font-size:.82rem; }
#dn-search textarea, #dn-search input { font-size: 1.08rem !important; }
.dn-hit { border:1px solid var(--border-color-primary); border-left:4px solid var(--dn-indigo-500); border-radius:12px; padding:12px 16px; margin:10px 0; background: var(--background-fill-secondary); }
.dn-hit .meta { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:6px; font-size:.82rem; }
.dn-file { background: var(--dn-indigo-50); color: var(--dn-indigo-700); border-radius:6px; padding:1px 8px; font-weight:600; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.dark .dn-file { background: rgba(99,102,241,.2); color:#c7d2fe; }
.dn-score { color: var(--body-text-color-subdued); }
.dn-hit mark { background: rgba(99,102,241,.25); color: inherit; border-radius:3px; padding:0 2px; }
.dn-answer { border:1px solid var(--dn-indigo-500); background: var(--dn-indigo-50); color:#1e1b4b; border-radius:12px; padding:14px 18px; margin:10px 0; }
.dark .dn-answer { background: rgba(99,102,241,.14); color:#e0e7ff; }
.dn-note { color: var(--body-text-color-subdued); font-size:.9rem; margin: 6px 2px; }
.dn-empty { text-align:center; padding:26px; color: var(--body-text-color-subdued); }
"""

HERO_ICON = (
    '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
    '<path d="M15.5 8.5l-2 5-5 2 2-5z"/></svg>'
)


HIDE = gr.update(value="", visible=False)


def hero_html() -> str:
    s = tools.get_corpus().stats()
    return (
        f'<div id="dn-hero"><div class="brand">{HERO_ICON}<h1>{TITLE}</h1></div>'
        f"<p>{TAGLINE}</p>"
        f'<div class="chips"><span class="chip">{s["documents"]} documents</span>'
        f'<span class="chip">{s["passages"]} searchable passages</span>'
        f'<span class="chip">MCP tools: list_docs · search_docs · read_doc</span>'
        f'<span class="chip">v{__version__}</span></div></div>'
    )


def render_hits(hits) -> str:
    if not hits:
        return '<div class="dn-empty">No passages matched. Try fewer or different words.</div>'
    cards = []
    for h in hits:
        section = f" › {html.escape(h.heading)}" if h.heading else ""
        cards.append(
            f'<div class="dn-hit"><div class="meta"><span class="dn-file">{html.escape(h.doc)}</span>'
            f'<span>{section.lstrip(" ›")}</span><span class="dn-score">score {h.score:.2f}</span></div>'
            f"<div>{h.snippet}</div></div>"
        )
    return "".join(cards)


def search_ui(query: str):
    query = (query or "").strip()
    if not query:
        return HIDE, '<div class="dn-empty">Type a question or a few keywords above.</div>'
    return HIDE, render_hits(tools.get_corpus().search(query, limit=6))


def ask_ui(query: str, oauth_token: gr.OAuthToken | None = None):
    query = (query or "").strip()
    if not query:
        return HIDE, '<div class="dn-empty">Type a question above, then press Ask.</div>'
    hits = tools.get_corpus().search(query, limit=6)
    token = oauth_token.token if oauth_token else SERVER_TOKEN
    try:
        result = answer_question(query, hits, token)
    except LLMUnavailable as exc:
        note = f'<div class="dn-answer">{html.escape(str(exc))}</div>'
        return gr.update(value=note, visible=True), render_hits(hits)
    body = html.escape(result.text).replace("\n", "<br>")
    answer = (
        f'<div class="dn-answer">{body}<div class="dn-note">Answered by {html.escape(result.model)} '
        "from the passages below, using your Hugging Face inference credits.</div></div>"
    )
    return gr.update(value=answer, visible=True), render_hits(hits)


def ask_ui_signed_in(query: str, oauth_token: gr.OAuthToken | None):
    return ask_ui(query, oauth_token)


def ask_ui_plain(query: str):
    return ask_ui(query, None)


def browse_ui(name: str):
    if not name:
        return ""
    try:
        return tools.read_doc(name)
    except (FileNotFoundError, ValueError) as exc:
        return str(exc)


def build_demo() -> gr.Blocks:
    corpus = tools.get_corpus()
    file_choices = [d["file"] for d in corpus.list_docs()]
    url = mcp_url()
    configs = client_configs(url)

    with gr.Blocks(title=TITLE, fill_width=False) as demo:
        gr.HTML(hero_html())

        with gr.Group(elem_id="dn-search"):
            with gr.Row(equal_height=True):
                query = gr.Textbox(
                    placeholder="Search the docs, or ask a question…",
                    show_label=False,
                    lines=1,
                    scale=6,
                    container=False,
                    autofocus=True,
                )
                search_btn = gr.Button("Search", variant="primary", scale=1, min_width=110)
                ask_btn = gr.Button("Ask with AI", scale=1, min_width=130)
        with gr.Row():
            gr.Examples(EXAMPLES, inputs=query, label="Try", examples_per_page=4)
            if LOGIN:
                gr.LoginButton("Sign in with Hugging Face to use Ask", size="sm")
        if LOGIN:
            gr.HTML(
                '<div class="dn-note">Search is free and needs no sign-in. “Ask with AI” uses an open model through '
                "Hugging Face Inference Providers and is paid from your own free monthly credits.</div>"
            )
        else:
            gr.HTML(
                '<div class="dn-note">Search needs no key. “Ask with AI” runs when <code>DOCSNAV_SERVER_TOKEN</code> '
                "is set to a Hugging Face token. The hosted Space uses Sign in with Hugging Face instead.</div>"
            )
        answer_box = gr.HTML(visible=False)
        results_box = gr.HTML('<div class="dn-empty">Results appear here.</div>')

        with gr.Tabs():
            with gr.Tab("Browse documents"):
                gr.Dataframe(
                    value=[[d["file"], d.get("type", ""), d.get("passages", 0), d.get("chars", 0)] for d in corpus.list_docs()],
                    headers=["File", "Type", "Passages", "Characters"],
                    interactive=False,
                    wrap=True,
                )
                picker = gr.Dropdown(file_choices, label="Open a document", value=None)
                viewer = gr.Textbox(label="Contents", lines=16, max_lines=28, interactive=False)
            with gr.Tab("Connect via MCP"):
                gr.Markdown(
                    f"This app is an MCP server. Point your client at `{url}` and it can call "
                    "`list_docs`, `search_docs`, and `read_doc`. The tool schema is at "
                    f"`{url}schema`."
                )
                with gr.Tabs():
                    for name, cfg in configs.items():
                        with gr.Tab(name):
                            gr.Markdown(cfg["hint"])
                            gr.Code(cfg["code"], language=cfg["language"], show_label=False, interactive=False)
                gr.Markdown(
                    "Hosted tools search the sample Aurora AI docs. To search your own files, run the app or "
                    "`mcp_server.py` yourself with `DOCS_DIR` pointing at a folder."
                )

        search_btn.click(search_ui, query, [answer_box, results_box], api_visibility="private")
        query.submit(search_ui, query, [answer_box, results_box], api_visibility="private")
        ask_btn.click(ask_ui_signed_in if LOGIN else ask_ui_plain, query, [answer_box, results_box], api_visibility="private")
        picker.change(browse_ui, picker, viewer, api_visibility="private")

        # MCP tools. gr.api registers each function as an API endpoint and an MCP tool, with no UI.
        gr.api(tools.list_docs, api_name="list_docs")
        gr.api(tools.search_docs, api_name="search_docs")
        gr.api(tools.read_doc, api_name="read_doc")

    # The login button registers an internal endpoint; keep it out of the MCP tool list.
    for fn in demo.fns.values():
        if fn.api_name == "_check_login_status":
            fn.api_visibility = "private"
    return demo


demo = build_demo()

if __name__ == "__main__":
    demo.launch(
        mcp_server=True,
        theme=gr.themes.Base(primary_hue="indigo", secondary_hue="indigo", neutral_hue="slate", radius_size="lg"),
        css=CSS,
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0" if os.getenv("SPACE_ID") else "127.0.0.1"),
        server_port=int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860"))),
        show_error=True,
    )
