#!/usr/bin/env python3
"""
An MCP (Model Context Protocol) server that provides web crawling capabilities using crawl4ai.
"""

import asyncio
from typing import cast
import os
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from spider_mcp_server.crawl import crawl_web_page


# Define the server
server = Server("spider-mcp-server")    

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Return the list of available tools.
    """
    tools = [
        Tool(
            name="say_hello",
            description="A simple tool that greets the user",
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
            description="Echo back the message provided by the user",
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
            description="Crawl a web page and save content in multiple formats (HTML, JSON, PDF, screenshot) with downloaded files",
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
                    }
                },
                "required": ["url", "save_path"]
            }
        )
    ]
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, object]) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool calls from the client.
    """
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
        
        result = await crawl_web_page(url, save_path)
        return [TextContent(type="text", text=result)]
    else:
        error_msg = f"Unknown tool: {name}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """
    Main entry point for the spider MCP server.
    """
    async with stdio_server() as (stdin, stdout):
        await server.run(
            stdin,
            stdout,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())