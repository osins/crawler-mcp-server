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

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlResult, CrawlerRunConfig, JsonCssExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

import aiohttp
from numpy import append

from spider_mcp_server.crawl import saveJson
from spider_mcp_server.utils import save


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
        
        if not url:
            error_msg = "URL is required for crawling"
            return [TextContent(type="text", text=error_msg)]
        
        if not save_path:
            error_msg = "Save path is required for saving content"
            return [TextContent(type="text", text=error_msg)]
        
        try:
            schema = {
                "baseSelector": "body",
                "fields": [
                    {"name": "title", "selector": "h2", "type": "text"},
                    {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
                    {"name": "p", "selector": "p", "type": "text"}
                ]
            }

            filter = PruningContentFilter(
                threshold=0.35,
                min_word_threshold=3,
                threshold_type="dynamic"
            )

            md_generator = DefaultMarkdownGenerator(content_filter=filter)

            # Configure browser and crawler
            browser_config = BrowserConfig(headless=True, java_script_enabled=True)

            # type: ignore
            crawler_config = CrawlerRunConfig(
                markdown_generator=md_generator,
                screenshot=True,
                pdf=True,
                cache_mode="bypass",
                extraction_strategy=JsonCssExtractionStrategy(schema)
            )
            
            # Use crawl4ai to crawl the web page
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=crawler_config)
                
                if result.success:
                    # 创建目录
                    os.makedirs(save_path, exist_ok=True)
                    files_dir = os.path.join(save_path, 'files')
                    os.makedirs(files_dir, exist_ok=True)
                    
                    saved_files = []
                    
                    # 1. 保存HTML文件
                    if hasattr(result, 'html') and result.html:
                        html_path = os.path.join(save_path, 'output.html')
                        with open(html_path, 'w', encoding='utf-8') as f:
                            if isinstance(result.html, str):
                                f.write(result.html)
                            else:
                                _ = f.write(str(result.html))
                        saved_files.append(html_path)
                    
                    # 1. 保存HTML文件
                    if hasattr(result, 'markdown') and result.markdown:
                        save(
                            save_path, 
                            'raw_markdown.md',
                            result.markdown.raw_markdown, 
                            lambda s: saved_files.append(s)
                        )

                        save(
                            save_path, 
                            'fit_markdown.md',
                            result.markdown.fit_markdown, 
                            lambda s: saved_files.append(s)
                        )
                    
                    # 2. 保存JSON文件（extracted_content）
                    save(save_path, 'output.json', result.extracted_content, lambda s: saved_files.append(s))
                    
                    # 3. 保存截图文件
                    save(save_path, 'output.png', result.screenshot, lambda s: saved_files.append(s))
                    
                    # 4. 保存PDF文件
                    save(save_path, 'output.pdf', result.pdf, lambda s: saved_files.append(s))
                    
                    # 5. 保存downloaded_files为JSON
                    await saveJson(save_path, result, lambda s: saved_files.append(s))
                    
                    success_msg = f"Successfully crawled {url} and saved {len(saved_files)} files to {save_path}"
                    return [TextContent(type="text", text=success_msg)]
                else:
                    print("Error:", result.error_message)
                    error_msg = f"Failed to crawl URL: {result.error_message}"
                    return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Error crawling URL or saving files: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
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