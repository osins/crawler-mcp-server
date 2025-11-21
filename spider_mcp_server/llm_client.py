# llm_client.py
from __future__ import annotations
from typing import TypedDict, Literal
from spider_mcp_server.config import OLLAMA_MODEL, OLLAMA_API_BASE, OLLAMA_TIMEOUT, OLLAMA_MAX_INPUT_LEN
from spider_mcp_server.ollama_tokenizer import OllamaTokenizer

import litellm

class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMClientError(Exception):
    pass


class LLMClient:
    def __init__(
        self,
        model: str = OLLAMA_MODEL,
        api_base: str = OLLAMA_API_BASE,
        timeout: int = OLLAMA_TIMEOUT,
        tokenizer: OllamaTokenizer = None
    ) -> None:
        self.model: str = model
        self.api_base: str = api_base
        self.timeout: int = timeout
        self.tokenizer = OllamaTokenizer()

    def _validate_inputs(self, messages: list[Message]) -> None:
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role not in ("system", "user", "assistant"):
                raise LLMClientError(f"非法 role: {role}")

            if not isinstance(content, str):
                raise LLMClientError("content 必须是字符串")

            if self.tokenizer.count_tokens(content) > OLLAMA_MAX_INPUT_LEN:
                raise LLMClientError(
                    f"LLM 输入超长（最大 {OLLAMA_MAX_INPUT_LEN} 字符, 实际 {self.tokenizer.count_tokens(content)}）"
                )

    def ask(self, messages: list[Message]) -> str:
        self._validate_inputs(messages)

        try:
            response = litellm.completion(
                model=self.model,
                api_base=self.api_base,
                messages=messages,
                timeout=self.timeout
            )

            print("")
            print("==========================")
            print(f"model: {self.model}, base: {self.api_base}, timeout: {self.timeout}")
            print("==========================")
            print(f"message: {messages}\n\nresponse: {response}")
            print("==========================")

            if not hasattr(response, "choices") or not response.choices:
                raise LLMClientError(f"LLM 返回结构异常: {response}")

            choice = response.choices[0]
            if not choice:
                raise LLMClientError(f"LLM 返回内容为空（choice）: {choice}")

            content = choice.message.get("content")
            if not content:
                raise LLMClientError(f"LLM 返回内容为空（content）: {content}")

            return content

        except Exception as e:
            raise LLMClientError(f"LLM 调用失败：{e}") from e
