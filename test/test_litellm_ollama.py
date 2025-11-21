#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import traceback
import os
import litellm
from crawl4ai import AsyncWebCrawler, LLMConfig, CrawlerRunConfig, LLMExtractionStrategy

from spider_mcp_server.llm_client import LLMClient

PROVIDER = "ollama/qwen2.5:7b"
API_BASE = "http://localhost:11434"

def test_litellm():
    # 调用本地 Ollama 模型
        print("正在调用 Ollama...")
        response = litellm.completion(
            model=PROVIDER,
            messages=[
                {"role": "user", "content": "你好，请回答一个简单问题：1+1=多少？"}
            ],
            api_base=API_BASE,
            timeout=30
        )

        print("=== 响应开始 ===")
        if hasattr(response, 'choices') and response.choices:
            print(response.choices[0].message.content)
        else:
            print(response)
        print("=== 响应结束 ===")

async def test_llm_client():
    print("正在调用 LLMClient...")
    client = LLMClient()
    response = client.ask([
        {"role": "user", "content": "你好，请回答一个简单问题：1+1=多少？"}
    ])
    print(response)
    print("=== LLMClient 响应结束 ===")

async def test_crawl_llama():
    # 配置 LLM 用于提取
    llm_config = LLMConfig(
        provider=PROVIDER, 
        api_token=None,  # 使用 ollama 作为 token
        base_url=API_BASE,
    )

    # LLM 提取策略
    llm_strat = LLMExtractionStrategy(
        llm_config=llm_config,
        extraction_type="schema",
        instruction="Extract the main title, content summary, and purpose of this webpage. Return valid JSON with fields: title, content, purpose.",
        chunk_token_threshold=1400,
        apply_chunking=True,
        input_format="html",
        extra_args={"temperature": 0.1, "max_tokens": 1500}
    )
    
    crawler_config = CrawlerRunConfig(
        extraction_strategy=llm_strat,
        screenshot=True,
        pdf=True,
        cache_mode="bypass"
    )
    
    print("Testing Crawl4AI with Ollama...")
        
    # Use crawl4ai to crawl the web page
    async with AsyncWebCrawler(verbose=True) as crawler:
        print("Making request to Crawl4AI with Ollama config...")
        result = await crawler.arun(
            url="https://zh.wikipedia.org/zh-cn/玉蒲團之偷情寶鑑",
            config=crawler_config
        )        

        if result.success:
            print("Crawl4AI with LLM extraction succeeded!")
            print(f"Crawled content length: {len(result.html)} characters")
            print(f"LLM extracted content: {result.extracted_content}")
        else:
            print(f"Crawl4AI with LLM extraction failed: {result.error}")

async def main():
    try:
        # 先测试 Ollama 连接
        test_litellm()

        # 再测试 LLMClient
        await test_llm_client()

        # 最后测试 Crawl4AI 调用
        # await test_crawl_llama()
    except Exception as e:
        print("调用过程中出现异常：", str(e))
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
