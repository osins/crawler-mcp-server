from operator import ge
from enum import Enum
from crawl4ai import LLMConfig, LLMExtractionStrategy, CrawlerRunConfig, CacheMode
from pydantic import BaseModel

import os
import litellm

from spider_mcp_server.config import OLLAMA_API_BASE, OLLAMA_MODEL, OLLAMA_TOKEN, OLLAMA_MAX_INPUT_LEN


DEFAULT_INSTRUCTION = """
将接收到的内容原样保存到 "block" 字段中。
"""

def llm_config(instruction: str = DEFAULT_INSTRUCTION):
    litellm.client_session_timeout = 3000
    # litellm._turn_on_debug() 
    
    print(f"LLM instruction: \n{instruction}")

    # LLM extraction strategy
    llm_strat = LLMExtractionStrategy(
        llm_config = LLMConfig(
                provider=OLLAMA_MODEL,
                api_token=OLLAMA_TOKEN,
                base_url=OLLAMA_API_BASE,
                max_tokens=OLLAMA_MAX_INPUT_LEN
            ),
        input_format="html",
        extraction_type="schema",
        instruction=instruction,
        apply_chunking=True,
        force_json_response=True,
        chunk_token_threshold=1000,
        overlap_rate=0.0,
        verbose=True,
        extra_args={"temperature": 0.0, "max_tokens": 800}
    )
    
    llm_strat.show_usage()
    llm_strat.verbose = True

    # type: ignore
    return CrawlerRunConfig(
        extraction_strategy=llm_strat,
        screenshot=True,
        pdf=True,
        cache_mode=CacheMode.DISABLED,
        word_count_threshold=1,
        remove_overlay_elements=True,
        only_text=False 
    )