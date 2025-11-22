# app_gradio.py
import gradio as gr
from client_agent import answer_sync


def chat_fn(message: str, history: list[dict]):
    # You *could* join history and send it to the agent; for now we keep it simple
    reply = answer_sync(message)
    return reply


demo = gr.ChatInterface(
    fn=chat_fn,
    type="messages",  # Use the new messages format instead of deprecated tuples
    title="Docs Navigator MCP",
    description=(
        "Ask questions about the docs/ directory. "
        "Behind the scenes, an MCP server exposes docs as tools/resources, "
        "and an LLM agent uses them to answer."
    ),
)

if __name__ == "__main__":
    demo.launch()
