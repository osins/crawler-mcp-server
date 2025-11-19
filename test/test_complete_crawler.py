#!/usr/bin/env python3

import asyncio
import tempfile
import os
import shutil
from spider_mcp_server.server import handle_call_tool, TextContent

def clean_temp_dir(temp_dir):
    # 清理临时文件
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"\n🧹 已清理临时目录: {temp_dir}")
        
async def test_complete_crawler():
    print("🔍 测试完整的爬虫功能（包含文件保存）")
    print("=" * 50)
    
    # 创建临时目录
    temp_dir = "./test_output/complete_crawler_test"
    
    clean_temp_dir(temp_dir)

    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        print(f"📁 测试目录: {temp_dir}")
        
        # 测试爬虫调用
        result = await handle_call_tool("crawl_web_page", {
            "url": "https://zh.wikipedia.org/zh-cn/%E7%8E%89%E8%92%B2%E5%9C%98%E4%B9%8B%E5%81%B7%E6%83%85%E5%AF%B6%E9%91%91",
            "save_path": temp_dir
        })
        
        print("📤 爬虫执行结果:")
        for content in result:
            if hasattr(content, 'text'):
                print(f"   {content.text}")
        
        # 检查生成的文件
        print(f"\n📄 生成的文件:")
        if os.path.exists(temp_dir):
            files = os.listdir(temp_dir)
            for file in sorted(files):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   ✅ {file} ({size} bytes)")
                elif os.path.isdir(file_path):
                    sub_files = os.listdir(file_path)
                    print(f"   📁 {file}/ 目录 ({len(sub_files)} 个文件)")
                    for sub_file in sorted(sub_files):
                        sub_path = os.path.join(file_path, sub_file)
                        sub_size = os.path.getsize(sub_path)
                        print(f"      📄 {sub_file} ({sub_size} bytes)")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_crawler())