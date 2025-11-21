# node_integration.py
from __future__ import annotations
from typing import List
from spider_mcp_server.config import OLLAMA_MAX_INPUT_LEN
from spider_mcp_server.llm_client import LLMClient, Message
from spider_mcp_server.crawl_json_node import SimpleNode
from spider_mcp_server.ollama_tokenizer import OllamaTokenizer
import traceback
import sys
import json

class NodeIntegrator:
    SYSTEM_MSG = """
你是一个纯内容抽取模块。你只负责从输入中抽取“正文内容”，并严格输出正文本身。
禁止输出任何说明、分析、解释、评论、总结、提示、标签、标题、章节编号、推测、格式化描述。
禁止输出你自己的观点。
禁止生成额外内容。
禁止补充任何不存在的句子。
如果输入中包含多个部分，你只能抽取其中的“正文文本”。
除了正文，禁止输出任何多余字符。
如果正文包含 Markdown 原始文本，则按原样返回，不允许改写。
如果输入中不存在正文，返回空字符串。

"""

    NODE_PREFIX = "节点 {}:\n"
    NODE_SEPARATOR = "\n\n---节点分隔线---\n\n"

    def __init__(self, llm_client: LLMClient = None, max_tokens_limit: int = OLLAMA_MAX_INPUT_LEN):
        self.llm_client = llm_client or LLMClient()
        self.tokenizer = OllamaTokenizer()
        self.max_tokens_limit = max_tokens_limit

        # 系统消息 token 数
        self.system_tokens = self.tokenizer.count_tokens(self.SYSTEM_MSG)
        # 用户消息可用 token = 总限制 - 系统消息 token
        self.user_max_tokens = self.max_tokens_limit - self.system_tokens

    def _count_tokens(self, text: str) -> int:
        return self.tokenizer.count_tokens(text)

    def _split_text_by_tokens(self, text: str, max_tokens: int) -> List[str]:
        """按 token 数严格拆分文本"""
        tokens = self.tokenizer.encode(text)
        splits = []
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            splits.append(self.tokenizer.decode(tokens[start:end]))
            start = end
        return splits

    def _split_long_node(self, node: SimpleNode, max_tokens_per_node: int) -> List[SimpleNode]:
        """拆分节点，每段严格小于 max_tokens_per_node"""
        split_texts = self._split_text_by_tokens(node.markdown, max_tokens_per_node)
        return [SimpleNode(markdown=t) for t in split_texts]

    def _prepare_integration_prompt(self, nodes: List[SimpleNode]) -> List[Message]:
        """拼接节点，生成 LLM 消息"""
        nodes_content = self.NODE_SEPARATOR.join(
            [self.NODE_PREFIX.format(i+1) + node.markdown for i, node in enumerate(nodes)]
        )
        message = nodes_content
        print(message)
        return [
            Message(role="system", content=self.SYSTEM_MSG),
            Message(role="user", content=message)
        ]

    def integrate_nodes(self, nodes: List[SimpleNode]) -> List[SimpleNode]:
        if not nodes:
            return []

        # 拆分批次，确保每批次 token 不超限
        batches = []
        current_batch = []
        current_tokens = 0

        for node in nodes:
            # 计算每个节点的额外 token（编号 + 分隔符）
            extra_tokens = self._count_tokens(self.NODE_PREFIX.format(1)) + self._count_tokens(self.NODE_SEPARATOR)
            node_tokens = self._count_tokens(node.markdown)
            
            if node_tokens + extra_tokens > self.user_max_tokens:
                # 超长节点拆分
                max_tokens_per_chunk = self.user_max_tokens - extra_tokens
                split_nodes = self._split_long_node(node, max_tokens_per_chunk)
            else:
                split_nodes = [node]

            for sn in split_nodes:
                sn_tokens = self._count_tokens(sn.markdown) + extra_tokens
                if current_tokens + sn_tokens > self.user_max_tokens:
                    if current_batch:
                        batches.append(current_batch)
                    current_batch = [sn]
                    current_tokens = sn_tokens
                else:
                    current_batch.append(sn)
                    current_tokens += sn_tokens

        if current_batch:
            batches.append(current_batch)

        integrated_nodes = []
        for batch in batches:
            if len(batch) == 1:
                integrated_nodes.extend(batch)
            else:
                try:
                    messages = self._prepare_integration_prompt(batch)
                    response = self.llm_client.ask(messages)
                    response_nodes = self._parse_llm_response(response)
                    integrated_nodes.extend(response_nodes)
                except Exception as e:
                    cls_name = self.__class__.__name__
                    tb = sys.exc_info()[2]
                    last_frame = traceback.extract_tb(tb)[-1]
                    print(
                        f"节点整合失败: {e}\n类名: {cls_name}\n"
                        f"文件: {last_frame.filename}\n行号: {last_frame.lineno}\n"
                        f"完整堆栈:\n{''.join(traceback.format_exception(e))}"
                    )
                    # 失败时返回原始节点
                    integrated_nodes.extend(batch)

        return integrated_nodes

    def _parse_llm_response(self, response: str) -> List[SimpleNode]:
        try:
            print(f"response: {response}")
            return [SimpleNode(markdown=response)]
        except Exception:
            return [SimpleNode(markdown=response)]


def fit_integrator(nodes: list[SimpleNode]):
    llm_client = LLMClient()
    integrator = NodeIntegrator(llm_client)
    return integrator.integrate_nodes(nodes)
