import json
from typing import Callable
from crawl4ai import CrawlResult
from bs4 import BeautifulSoup
from spider_mcp_server.node_integration import fit_integrator
from spider_mcp_server.crawl_json_node import Node, build_node_tree, format_node_tree
from spider_mcp_server.utils import save

def save_json(path: str, name: str, html: str | None, call: Callable[[str], None]) -> None:
    if html is None:
        return
    
    soup = BeautifulSoup(html, "lxml")
    root_node = build_node_tree(soup.body if soup.body else soup)

    save(path, name, json.dumps(root_node.to_dict(), ensure_ascii=False, indent=2), call)
                
    try:
        simple_nodes = format_node_tree(root_node)
        save(path, f"midle_{name}", json.dumps([node.model_dump() for node in simple_nodes], ensure_ascii=False, indent=2), call)

        fit_nodes = fit_integrator(simple_nodes)
        save(path, f"fit_{name}", json.dumps([node.model_dump() for node in fit_nodes], ensure_ascii=False, indent=2), call)
    except Exception as e:
        print(f"Failed to format node tree: {e}")
    