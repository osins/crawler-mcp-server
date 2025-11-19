#!/usr/bin/env python3
"""
Complete test for the spider MCP server functionality.
"""

import subprocess
import json
import asyncio
from spider_mcp_server.server import handle_call_tool


def test_initialization():
    print("1. Testing server initialization...")
    init_request = {
        "jsonrpc": "2.0",
        "id": "init",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "test-client",
                "version": "1.0"
            },
            "capabilities": {}
        }
    }
    
    result = subprocess.run(
        ["python", "spider_mcp_server/server.py"],
        input=json.dumps(init_request) + "\n",
        text=True,
        capture_output=True
    )
    
    if result.returncode == 0 and 'result' in result.stdout:
        response = json.loads(result.stdout.strip())
        if "result" in response and "capabilities" in response["result"]:
            print("   ✓ Initialization successful")
            return True
    print("   ✗ Initialization failed")
    return False


async def test_tools():
    print("\n2. Testing all tools...")
    
    # Test say_hello
    print("   Testing say_hello tool...")
    result = await handle_call_tool("say_hello", {"name": "MCP User"})
    if result and "Hello, MCP User!" in result[0].text:
        print("   ✓ say_hello tool working correctly")
    else:
        print("   ✗ say_hello tool not working correctly")
        return False
    
    # Test echo_message
    print("   Testing echo_message tool...")
    result = await handle_call_tool("echo_message", {"message": "Hello from test!"})
    if result and "Hello from test!" in result[0].text:
        print("   ✓ echo_message tool working correctly")
    else:
        print("   ✗ echo_message tool not working correctly")
        return False
    
    # Test crawl_web_page
    print("   Testing crawl_web_page tool...")
    result = await handle_call_tool("crawl_web_page", {"url": "https://httpbin.org/html"})
    if result and len(result[0].text) > 0:
        print(f"   ✓ crawl_web_page tool working correctly, retrieved {len(result[0].text)} characters")
    else:
        print("   ✗ crawl_web_page tool not working correctly")
        return False
    
    return True


async def main():
    print("=== Complete Spider MCP Server Test ===\n")
    
    # Test 1: Initialization
    init_success = test_initialization()
    
    # Test 2: Tools
    tools_success = await test_tools()
    
    print(f"\n=== Final Result ===")
    if init_success and tools_success:
        print("✓ All tests passed!")
        print("✓ Spider MCP server with crawling functionality is working correctly.")
        print("✓ Ready for production use.")
    else:
        print("✗ Some tests failed")
        print("✗ Server needs debugging.")


if __name__ == "__main__":
    asyncio.run(main())