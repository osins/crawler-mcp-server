#!/usr/bin/env python3
"""
An MCP (Model Context Protocol) server that provides web crawling capabilities using crawl4ai.
Supports multiple content formats output (HTML, JSON, PDF, screenshots, Markdown) and browser interaction features.
"""

import asyncio
from typing import cast
import os
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from mcp_server.crawl.crawl import crawl_web_page, DEFAULT_INSTRUCTION
from mcp_server.browser.browser_service import get_browser_service


# Define the server
server = Server("dev-tool-mcp-server")    

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Return the list of available tools.
    """
    tools = [
        Tool(
            name="say_hello",
            description="A simple greeting tool that returns personalized messages to users",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name to greet, defaults to World",
                        "default": "World"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="echo_message",
            description="Echo tool that returns user-provided information as-is",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo back"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="crawl_web_page",
            description="Crawl web page content and save in multiple formats (HTML, JSON, PDF, screenshots) while downloading file resources from the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to crawl"
                    },
                    "save_path": {
                        "type": "string", 
                        "description": "The base file path to save the crawled content and downloaded files"
                    },
                    "instruction": {
                        "type": "string",
                        "description": "The instruction to use for the LLM"
                    },
                    "save_screenshot": {
                        "type": "boolean",
                        "description": "Save a screenshot of the page",
                        "default": False
                    },
                    "save_pdf": {
                        "type": "boolean",
                        "description": "Save a PDF of the page",
                        "default": False
                    },
                    "generate_markdown": {
                        "type": "boolean",
                        "description": "Generate a Markdown representation of the page",
                        "default": False
                    }
                },
                "required": ["url", "save_path"]
            }
        ),
        Tool(
            name="get_page_content",
            description="Get complete content of a specified URL webpage, including HTML structure and page data",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to get content from"
                    },
                    "wait_for_selector": {
                        "type": "string",
                        "description": "Optional CSS selector to wait for before getting content"
                    },
                    "wait_timeout": {
                        "type": "integer",
                        "description": "Wait timeout in milliseconds, default 30000",
                        "default": 30000
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="get_console_messages",
            description="Capture console output information from specified URL webpage (including logs, warnings, errors, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to get console messages from"
                    },
                    "wait_for_selector": {
                        "type": "string",
                        "description": "Optional CSS selector to wait for before getting console messages"
                    },
                    "wait_timeout": {
                        "type": "integer",
                        "description": "Wait timeout in milliseconds, default 30000",
                        "default": 30000
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="get_network_requests",
            description="Monitor and retrieve all network requests initiated by specified URL webpage (API calls, resource loading, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to get network requests from"
                    },
                    "wait_for_selector": {
                        "type": "string",
                        "description": "Optional CSS selector to wait for before getting network requests"
                    },
                    "wait_timeout": {
                        "type": "integer",
                        "description": "Wait timeout in milliseconds, default 30000",
                        "default": 30000
                    }
                },
                "required": ["url"]
            }
        )
    ]
    return tools


class StreamingContext:
    """A context object that allows sending streaming content during tool execution."""

    def __init__(self):
        self.outputs = []

    async def send_output(self, content: list[TextContent | ImageContent | EmbeddedResource]):
        """Send output to the client during tool execution."""
        # In a real MCP implementation with streaming support, this would
        # send the content immediately to the client using ProgressNotification
        self.outputs.extend(content)


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, object]) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool calls from the client with streaming output support.
    """
    # Create streaming context
    ctx = StreamingContext()

    # Define a progress callback function that sends output via the context
    async def progress_callback(msg: str):
        await ctx.send_output([TextContent(type="text", text=f"PROGRESS: {msg}")])

    if name == "say_hello":
        name_param = cast(str, arguments.get("name", "World"))
        result = f"Hello, {name_param}!"
        return [TextContent(type="text", text=result)]
    elif name == "echo_message":
        message = cast(str, arguments.get("message", ""))
        result = message
        return [TextContent(type="text", text=result)]
    elif name == "crawl_web_page":
        url = cast(str, arguments.get("url", ""))
        save_path = cast(str, arguments.get("save_path", ""))
        instruction = cast(str, arguments.get("instruction", DEFAULT_INSTRUCTION))
        save_screenshot = cast(bool, arguments.get("save_screenshot", False))
        save_pdf = cast(bool, arguments.get("save_pdf", False))
        generate_markdown = cast(bool, arguments.get("generate_markdown", False))

        # Call crawl_web_page with progress callback
        result = await crawl_web_page(
            url, save_path, instruction, save_screenshot,
            save_pdf, generate_markdown, progress_callback=progress_callback
        )
        # Add final result to outputs
        await ctx.send_output([TextContent(type="text", text=result)])
        # Return all outputs collected during execution
        return ctx.outputs
    elif name == "get_page_content":
        url = cast(str, arguments.get("url", ""))
        wait_for_selector = cast(str, arguments.get("wait_for_selector", None))
        wait_timeout = cast(int, arguments.get("wait_timeout", 30000))

        browser_service = await get_browser_service()

        # Call with progress callback
        result = await browser_service.get_page_content(
            url, wait_for_selector, wait_timeout,
            progress_callback=progress_callback
        )
        # Add final result to outputs
        await ctx.send_output([TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
        # Return all outputs collected during execution
        return ctx.outputs
    elif name == "get_console_messages":
        url = cast(str, arguments.get("url", ""))
        wait_for_selector = cast(str, arguments.get("wait_for_selector", None))
        wait_timeout = cast(int, arguments.get("wait_timeout", 30000))

        browser_service = await get_browser_service()

        # Call with progress callback
        result = await browser_service.get_console_messages(
            url, wait_for_selector, wait_timeout,
            progress_callback=progress_callback
        )
        # Add final result to outputs
        await ctx.send_output([TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
        # Return all outputs collected during execution
        return ctx.outputs
    elif name == "get_network_requests":
        url = cast(str, arguments.get("url", ""))
        wait_for_selector = cast(str, arguments.get("wait_for_selector", None))
        wait_timeout = cast(int, arguments.get("wait_timeout", 30000))

        browser_service = await get_browser_service()

        # Call with progress callback
        result = await browser_service.get_network_requests(
            url, wait_for_selector, wait_timeout,
            progress_callback=progress_callback
        )
        # Add final result to outputs
        await ctx.send_output([TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))])
        # Return all outputs collected during execution
        return ctx.outputs
    else:
        error_msg = f"Unknown tool: {name}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """
    Main entry point for the dev-tool MCP server - provides web crawling, content extraction, and browser interaction features.
    """
    async with stdio_server() as (stdin, stdout):
        await server.run(
            stdin,
            stdout,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())