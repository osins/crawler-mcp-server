from operator import ge
from crawl4ai import LLMConfig, LLMExtractionStrategy, CrawlerRunConfig

import os
import litellm

def llm_config():
    litellm.client_session_timeout = 3000
    # litellm._turn_on_debug() 
    
    # LLM extraction strategy
    llm_strat = LLMExtractionStrategy(
        llm_config = LLMConfig(
                provider=os.getenv("LLAMA_PROVIDER", "ollama/qwen2.5-coder:latest"),
                api_token=os.getenv("LLAMA_API_TOKEN", None),
                base_url=os.getenv("LLAMA_BASE_URL", None),
                max_tokens=os.getenv("LLAMA_MAX_TOKENS", 4096)
            ),
        extraction_type="schema",
        instruction="Extract entities and relationships from the content. Return valid JSON.",
        chunk_token_threshold=1400,
        apply_chunking=True,
        input_format="html",
        extra_args={"temperature": 0.1, "max_tokens": 1500}
    )
    
    # type: ignore
    return CrawlerRunConfig(
        extraction_strategy=llm_strat,
        screenshot=True,
        pdf=True,
        cache_mode="bypass"
    )