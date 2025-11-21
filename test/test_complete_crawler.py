#!/usr/bin/env python3

import asyncio
import tempfile
import os
import shutil
from spider_mcp_server.server import handle_call_tool, TextContent

def clean_temp_dir(temp_dir):
    # Clean up temporary files
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned temporary directory: {temp_dir}")
        
async def test_complete_crawler():
    print("🔍 Testing complete crawler functionality (with file saving)")
    print("=" * 50)
    
    # Create temporary directory
    temp_dir = "./test_output"
    
    clean_temp_dir(temp_dir)

    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        print(f"📁 Test directory: {temp_dir}")
        
        # Test crawler call
        result = await handle_call_tool("crawl_web_page", {
            "url": os.getenv("TEST_URL", "https://zh.wikipedia.org/wiki/Wikipedia:%E9%A6%96%E9%A1%B5"),
            "save_path": temp_dir
        })
        
        print("📤 Crawler execution result:")
        for content in result:
            if hasattr(content, 'text'):
                print(f"   {content.text}")
        
        # Check generated files
        print(f"\n📄 Generated files:")
        if os.path.exists(temp_dir):
            files = os.listdir(temp_dir)
            for file in sorted(files):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   ✅ {file} ({size} bytes)")
                elif os.path.isdir(file_path):
                    sub_files = os.listdir(file_path)
                    print(f"   📁 {file}/ directory ({len(sub_files)} files)")
                    for sub_file in sorted(sub_files):
                        sub_path = os.path.join(file_path, sub_file)
                        sub_size = os.path.getsize(sub_path)
                        print(f"      📄 {sub_file} ({sub_size} bytes)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_crawler())