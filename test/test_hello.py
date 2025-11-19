#!/usr/bin/env python3
"""
Complete test for the MCP server hello functionality.
"""

import subprocess
import json


def test_hello_functionality():
    print("=== Testing MCP Server Hello Functionality ===\n")
    
    # Test 1: Initialize server
    print("1. Testing initialization...")
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
    
    print(f"   Response: {result.stdout}")
    
    # Check if initialization was successful
    response = json.loads(result.stdout.strip())
    if "result" in response and "capabilities" in response["result"]:
        print("   ✓ Initialization successful")
    else:
        print("   ✗ Initialization failed")
        return False
    
    print("\n=== Hello functionality test completed ===")
    print("Note: Due to the nature of the stdio transport protocol,")
    print("full interactive testing requires a persistent server connection.")
    print("The initialization response confirms the server is functioning correctly.")
    
    return True


def test_say_hello():
    print("\n2. Testing say_hello tool directly...")
    
    # Import and test the function directly
    try:
        from spider_mcp_server.server import handle_call_tool
        import asyncio
        
        async def test_call():
            result = await handle_call_tool("say_hello", {"name": "MCP"})
            print(f"   say_hello result: {result[0].text if result else 'No result'}")
            return result[0].text if result else None
        
        result = asyncio.run(test_call())
        if result and "Hello, MCP!" in result:
            print("   ✓ say_hello tool working correctly")
            return True
        else:
            print("   ✗ say_hello tool not working correctly")
            return False
    except Exception as e:
        print(f"   ✗ Error testing say_hello tool: {e}")
        return False


def test_echo_message():
    print("\n3. Testing echo_message tool directly...")
    
    try:
        from spider_mcp_server.server import handle_call_tool
        import asyncio
        
        async def test_call():
            result = await handle_call_tool("echo_message", {"message": "Hello from test!"})
            print(f"   echo_message result: {result[0].text if result else 'No result'}")
            return result[0].text if result else None
        
        result = asyncio.run(test_call())
        if result and "Hello from test!" in result:
            print("   ✓ echo_message tool working correctly")
            return True
        else:
            print("   ✗ echo_message tool not working correctly")
            return False
    except Exception as e:
        print(f"   ✗ Error testing echo_message tool: {e}")
        return False


if __name__ == "__main__":
    # Run the tests
    success1 = test_hello_functionality()
    success2 = test_say_hello()
    success3 = test_echo_message()
    
    print(f"\n=== Final Result ===")
    if success1 and success2 and success3:
        print("✓ All hello functionality tests passed!")
        print("✓ Hello functionality is working correctly.")
    else:
        print("✗ Some tests failed")
        print("✗ Hello functionality needs debugging.")