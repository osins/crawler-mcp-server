#!/usr/bin/env python3
"""
Test script to verify the MCP server functionality.
"""

import asyncio
from anyio import create_memory_object_stream
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
from spider_mcp_server.server import server


async def test_mcp_functionality():
    print("Testing MCP server functionality...")
    
    # 创建内存流来模拟stdio
    request_send, request_receive = create_memory_object_stream(max_buffer_size=1)
    response_send, response_receive = create_memory_object_stream(max_buffer_size=1)
    
    # 启动服务器任务
    async def run_server():
        await server.run(
            request_receive,
            response_send,
            server.create_initialization_options()
        )
    
    server_task = asyncio.create_task(run_server())
    
    # 1. 发送初始化请求
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
    
    print("Sending initialize request...")
    await request_send.send(init_request)
    
    # 接收初始化响应
    init_response = await response_receive.receive()
    print("Initialize response:", init_response)
    
    # 2. 发送initialized通知
    initialized_request = {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {}
    }
    
    print("\nSending initialized notification...")
    await request_send.send(initialized_request)
    
    # 3. 发送list tools请求
    list_tools_request = {
        "jsonrpc": "2.0",
        "id": "list_tools",
        "method": "tools/list",
        "params": {}
    }
    
    print("Sending tools/list request...")
    await request_send.send(list_tools_request)
    
    # 接收工具列表响应
    tools_response = await response_receive.receive()
    print("Tools response:", tools_response)
    
    # 4. 调用say_hello工具
    call_hello_request = {
        "jsonrpc": "2.0",
        "id": "call_hello",
        "method": "tools/call",
        "params": {
            "name": "say_hello",
            "arguments": {"name": "MCP"}
        }
    }
    
    print("\nSending call to say_hello tool...")
    await request_send.send(call_hello_request)
    
    # 接收say_hello响应
    hello_response = await response_receive.receive()
    print("Say hello response:", hello_response)
    
    # 5. 调用echo_message工具
    call_echo_request = {
        "jsonrpc": "2.0",
        "id": "call_echo",
        "method": "tools/call",
        "params": {
            "name": "echo_message",
            "arguments": {"message": "Hello from test!"}
        }
    }
    
    print("\nSending call to echo_message tool...")
    await request_send.send(call_echo_request)
    
    # 接收echo_message响应
    echo_response = await response_receive.receive()
    print("Echo message response:", echo_response)
    
    # 停止服务器
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass
    
    print("\nMCP functionality test completed.")


if __name__ == "__main__":
    asyncio.run(test_mcp_functionality())