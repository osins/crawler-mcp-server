from numpy import ma
from bs4 import BeautifulSoup, Tag, NavigableString
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from pydantic import BaseModel
import requests
import json
import tiktoken

# --------------------------
# Node 定义
# --------------------------
class Node:
    tag: str
    text: str
    attributes: dict[str, str | list[str] | dict[str, str]]
    children: list['Node'] | None
    markdown: str
    
    def __init__(
        self, 
        tag: str, 
        text: str = "", 
        attributes: dict[str, str | list[str] | dict[str, str]] | None = None, 
        children: list['Node'] | None = None,
        markdown: str = ""
    ):
        self.tag = tag
        self.text = text.strip() if text else ""
        self.attributes = attributes if attributes else {}
        self.children = children if children else []
        self.markdown = markdown

    def split_text(self, max_len: int = 1024) -> list['Node']:
        """
        将过长文本拆分为多个节点，保持层级
        """
        if len(self.text) <= max_len:
            return [self]
        parts = []
        text = self.text
        while text:
            part_text = text[:max_len]
            text = text[max_len:]
            part_node = Node(tag=self.tag, text=part_text, attributes=self.attributes.copy())
            parts.append(part_node)
        # 子节点也递归拆分
        result = []
        for p in parts:
            result.append(p)
        for child in self.children:
            result.extend(child.split_text(max_len))
        return result

    def to_dict(self) -> dict[str, str | list[str] | dict[str, str]]:
        return {
            "tag": self.tag,
            "text": self.text,
            "attributes": self.attributes,
            'markdown': self.markdown,
            "children": [child.to_dict() for child in self.children] if self.children else []
        }

def html_to_markdown(html: str)->str:
    generator = DefaultMarkdownGenerator()
    markdown_result = generator.generate_markdown(input_html=html)

    print(f"html to markdown, html: {html}")
    print(f"html to markdown, result: {markdown_result.markdown_with_citations}")

    return markdown_result.markdown_with_citations

# --------------------------
# Step 2: 解析 HTML 生成 Node Tree
# --------------------------
def build_node_tree(bs_element: BeautifulSoup | Tag | NavigableString) -> Node:
    children_nodes = [build_node_tree(child) for child in bs_element.find_all(recursive=False)]
    # 如果是文本节点且没有标签
    if bs_element.name is None:
        return Node(tag="text", text=str(bs_element))
    return Node(
        tag=bs_element.name,
        text=bs_element.string if bs_element.string else "",
        attributes=bs_element.attrs if hasattr(bs_element, 'attrs') else {},
        children=children_nodes,
        markdown=html_to_markdown(str(bs_element))
    )

class SimpleNode(BaseModel):
    markdown: str

def format_node_tree(node: Node, min_len: int = 1024):
    children: list[SimpleNode] = []
    if not node.children:
        children.append(SimpleNode(markdown=node.markdown))
        return children

    for child in node.children:
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = encoder.encode(child.markdown)
        if len(tokens) < min_len:
            child.children = []
            children.append(SimpleNode(markdown=child.markdown))
            continue
        # 如果子节点长度超过了最小长度，则递归调用
        cs = format_node_tree(child, min_len)
        for c in cs:
            children.append(SimpleNode(markdown=c.markdown))

    return children