# client_agent.py
import asyncio
from contextlib import AsyncExitStack
from typing import Optional

from dotenv import load_dotenv
from anthropic import Anthropic

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class DocsNavigatorClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self._tools_cache = None

    async def connect(self, server_script_path: str = "server_docs.py"):
        """
        Start the docs MCP server (via stdio) and initialize a session.
        """
        params = StdioServerParameters(
            command="python",  # or "uv" with args if you prefer
            args=[server_script_path],
            env=None,
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()

        tools_response = await self.session.list_tools()
        self._tools_cache = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in tools_response.tools
        ]

    async def close(self):
        await self.exit_stack.aclose()

    async def answer(self, user_query: str) -> str:
        """
        Ask the LLM to answer a question, using docs tools when needed.
        """
        if not self.session:
            raise RuntimeError("MCP session not initialized. Call connect() first.")

        if self._tools_cache is None:
            tools_response = await self.session.list_tools()
            self._tools_cache = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in tools_response.tools
            ]

        messages = [
            {
                "role": "user",
                "content": (
                    "You are a documentation assistant. "
                    "Use the available MCP tools to search and read docs in order "
                    "to answer the question. Always reference the files you used.\n\n"
                    f"User question: {user_query}"
                ),
            }
        ]

        tools = self._tools_cache

        # Initial call: let the LLM decide whether to call tools
        response = self.anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1200,
            messages=messages,
            tools=tools,
        )

        final_chunks: list[str] = []

        # ––– Basic single-round tool handling like in the official example –––
        for content in response.content:
            if content.type == "text":
                final_chunks.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Call the MCP tool
                result = await self.session.call_tool(tool_name, tool_args)

                # Feed tool result back to Claude
                messages.append(
                    {
                        "role": "assistant",
                        "content": [content],
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": result.content,
                            }
                        ],
                    }
                )

                followup = self.anthropic.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1200,
                    messages=messages,
                    tools=tools,
                )
                # Take the first chunk of the follow-up as final text
                for c2 in followup.content:
                    if c2.type == "text":
                        final_chunks.append(c2.text)

        if not final_chunks:
            # Fallback: if Claude didn’t emit plain text, you could show raw content
            return "[no text response from model]"
        return "\n".join(final_chunks)


# Thread-local storage for client instances
import threading
_thread_local = threading.local()


def answer_sync(user_query: str) -> str:
    """
    Synchronous wrapper so Gradio can call into our async flow easily.
    Creates a new client for each request to avoid event loop conflicts.
    """
    import concurrent.futures
    
    def run_in_new_loop():
        # Create a new event loop in this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_answer_async(user_query))
        finally:
            loop.close()
    
    # Run in a separate thread to avoid conflicts with Gradio's event loop
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_new_loop)
        return future.result()


async def _answer_async(user_query: str) -> str:
    """
    Create a fresh client for each request to avoid event loop issues.
    """
    client = DocsNavigatorClient()
    try:
        await client.connect("server_docs.py")
        return await client.answer(user_query)
    finally:
        await client.close()
