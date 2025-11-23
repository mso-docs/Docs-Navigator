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

    async def connect(self, server_script_path: str = "src/server/server.py"):
        """
        Start the docs MCP server (via stdio) and initialize a session.
        """
        import os
        import sys
        
        # Try to use uv run first, then fall back to the virtual environment python
        if os.path.exists(".venv/Scripts/python.exe"):
            # Windows virtual environment
            python_path = ".venv/Scripts/python.exe"
            params = StdioServerParameters(
                command=python_path,
                args=[server_script_path],
                env=None,
            )
        elif os.path.exists(".venv/bin/python"):
            # Unix virtual environment
            python_path = ".venv/bin/python"
            params = StdioServerParameters(
                command=python_path,
                args=[server_script_path],
                env=None,
            )
        else:
            # Fallback to system python
            params = StdioServerParameters(
                command="python",
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
        Supports multi-turn conversations with multiple tool calls.
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
                    "to answer the question. You can use multiple tools and think through "
                    "your response step by step. Always reference the files you used.\n\n"
                    f"User question: {user_query}"
                ),
            }
        ]

        tools = self._tools_cache
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            
            # Call the LLM
            response = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2500,  # Increased token limit for longer responses
                messages=messages,
                tools=tools,
            )

            # Add assistant's response to conversation
            messages.append({
                "role": "assistant",
                "content": response.content,
            })

            # Check if there are any tool calls to execute
            tool_calls = [content for content in response.content if content.type == "tool_use"]
            
            if not tool_calls:
                # No more tool calls - we're done
                text_content = [content.text for content in response.content if content.type == "text"]
                return "\n".join(text_content) if text_content else "[no text response from model]"

            # Execute all tool calls in this round
            tool_results = []
            for tool_call in tool_calls:
                try:
                    tool_name = tool_call.name
                    tool_args = tool_call.input
                    
                    # Call the MCP tool
                    result = await self.session.call_tool(tool_name, tool_args)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result.content,
                    })
                except Exception as e:
                    # Handle tool errors gracefully
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": f"Error calling tool {tool_call.name}: {str(e)}",
                        "is_error": True,
                    })

            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results,
            })

        # If we hit max iterations, return what we have so far
        text_content = []
        for message in messages:
            if message["role"] == "assistant":
                for content in message["content"]:
                    if hasattr(content, 'type') and content.type == "text":
                        text_content.append(content.text)
                    elif isinstance(content, dict) and content.get("type") == "text":
                        text_content.append(content.get("text", ""))

        return "\n".join(text_content) if text_content else "[reached max iterations without final response]"


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
        await client.connect("src/server/server.py")
        return await client.answer(user_query)
    finally:
        await client.close()