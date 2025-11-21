import tiktoken
from typing import Optional
from spider_mcp_server.config import (
    OLLAMA_MODEL,
    OLLAMA_ENCODING,
    OLLAMA_TIMEOUT,
)

class OllamaTokenizer:
    """
    使用 tiktoken（与 most LLM 完全兼容的 BPE tokenizer）进行本地 token 计数。
    生产级实现，不依赖 transformers、模型权重或 Ollama 服务。
    """

    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        encoding: str = OLLAMA_ENCODING,
        timeout_seconds: int = OLLAMA_TIMEOUT
    ):
        self.model = model
        self.encoding = tiktoken.get_encoding(encoding)

        self.timeout_seconds = timeout_seconds

    def count_tokens(self, text: str) -> int:
        """
        本地 token 计数（严格可用于生产）。
        完整处理所有非法输入与异常情况。
        """
        if text is None:
            return 0

        if not isinstance(text, str):
            text = str(text)

        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            raise RuntimeError(f"本地 tokenizer 计算 token 数失败: {str(e)}")
