#!/usr/bin/env python3
"""
Test script for the crawl_web_page functionality.
"""

import asyncio
from spider_mcp_server.server import handle_call_tool


async def test_crawl_functionality():
    print("Testing crawl_web_page functionality...")
    
    # Test crawling a simple page
    try:
        result = await handle_call_tool('crawl_web_page', {
            'url': 'https://httpbin.org/html',
            'save_path': 'test_output/httpbin_html'
        })
        
        if result and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            print(f"Success! Retrieved content: {content}")
        else:
            print("No content returned from crawler")
    except Exception as e:
        print(f"Error during crawling: {e}")
        
    # Test crawling another page
    print("\nTesting with another URL...")
    try:
        result = await handle_call_tool('crawl_web_page', {
            'url': 'https://httpbin.org/json',
            'save_path': 'test_output/httpbin_json'
        })
        
        if result and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            print(f"Success! Retrieved content: {content}")
        else:
            print("No content returned from crawler")
    except Exception as e:
        print(f"Error during crawling: {e}")

    # Test error handling - invalid URL
    print("\nTesting error handling with invalid URL...")
    try:
        result = await handle_call_tool('crawl_web_page', {
            'url': 'invalid-url',
            'save_path': 'test_output/invalid_url'
        })
        
        if result and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            print(f"Error handling response: {content}")
        else:
            print("No response for invalid URL")
    except Exception as e:
        print(f"Error during crawling invalid URL: {e}")


if __name__ == "__main__":
    asyncio.run(test_crawl_functionality())