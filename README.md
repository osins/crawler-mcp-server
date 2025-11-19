# MCP Spider Server

一个基于 [crawl4ai](https://github.com/unclecode/crawl4ai) 的 MCP (Model Context Protocol) 爬虫服务器，提供强大的网页抓取和内容提取功能。

## 🚀 功能特性

- **智能网页抓取**：使用 crawl4ai 进行高效的网页内容提取
- **多格式输出**：支持 Markdown、HTML、JSON 等多种格式
- **截图功能**：自动生成网页截图
- **PDF 导出**：将网页内容导出为 PDF 文件
- **内容过滤**：使用 PruningContentFilter 优化内容提取
- **结构化数据提取**：支持 JsonCssExtractionStrategy 进行精确数据提取
- **MCP 协议支持**：完全兼容 MCP 标准，可与支持 MCP 的客户端集成

## 📦 安装

### 环境要求

- Python 3.8+
- 推荐使用虚拟环境

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/osins/crawler-mcp-server.git
cd crawler-mcp-server
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -e .
```

## 🔧 MCP 服务配置

### Claude Desktop 配置示例

将以下配置添加到 Claude Desktop 的配置文件中：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "spider": {
      "command": "/path/to/crawler-mcp-server/venv/bin/python",
      "args": [
        "/path/to/crawler-mcp-server/spider_mcp_server/server.py"
      ],
      "description": "MCP spider server using crawl4ai for web crawling and content extraction"
    }
  }
}
```

### MCP 客户端配置示例

如果您使用其他 MCP 客户端，可以使用以下通用配置：

```json
{
  "servers": {
    "spider-crawler": {
      "name": "Spider Crawler Server",
      "description": "Web crawling and content extraction server",
      "command": "/path/to/crawler-mcp-server/venv/bin/python",
      "args": [
        "/path/to/crawler-mcp-server/spider_mcp_server/server.py"
      ],
      "timeout": 30000
    }
  }
}
```

### 📋 配置说明

**直接运行脚本即可：**
- 无需设置环境变量
- 无需使用 `-m` 参数
- Python 会自动处理相对导入
- 配置最简洁，最可靠

### 环境变量配置

通常不需要额外环境变量，因为使用模块运行方式 Python 会自动处理路径。

如果需要自定义，可以设置：

```bash
# 设置输出目录（默认为 test_output）
export SPIDER_OUTPUT_DIR=/path/to/output

# 设置用户代理
export CRAWL4AI_USER_AGENT="MCP Spider Bot 1.0"
```

## 🛠️ 可用工具

### 1. `crawl_web_page`

抓取指定 URL 的网页内容。

**参数：**
- `url` (string, 必需): 要抓取的网页 URL
- `output_dir` (string, 可选): 输出目录路径，默认为 "test_output"

**功能：**
- 自动生成网页截图 (PNG)
- 导出 PDF 版本
- 生成 Markdown 格式内容
- 提取结构化数据 (JSON)

**示例使用：**
```python
# 抓取网页并保存到默认目录
result = await session.call_tool("crawl_web_page", {
    "url": "https://example.com"
})

# 指定输出目录
result = await session.call_tool("crawl_web_page", {
    "url": "https://example.com",
    "output_dir": "/path/to/custom/output"
})
```

### 2. `say_hello`

简单的问候工具，用于测试连接。

**参数：** 无

**示例使用：**
```python
result = await session.call_tool("say_hello", {})
```

### 3. `echo_message`

回显消息，用于测试通信。

**参数：**
- `message` (string, 必需): 要回显的消息

**示例使用：**
```python
result = await session.call_tool("echo_message", {
    "message": "Hello MCP!"
})
```

## 📁 输出文件结构

抓取完成后，会在指定的输出目录中生成以下文件：

```
output_directory/
├── example_com.png          # 网页截图
├── example_com.pdf          # PDF 版本
├── example_com.md          # Markdown 内容
├── example_com_cleaned.md  # 清理后的 Markdown
├── example_com.json        # 结构化数据
├── example_com_iframes.md  # iframe 内容
├── example_com_links.md    # 链接列表
└── example_com_images.md   # 图片列表
```

## 🔍 使用示例

### 基本网页抓取

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def crawl_example():
    # 连接到 MCP 服务器（直接运行，无需额外参数）
    server_params = StdioServerParameters(
        command="/path/to/crawler-mcp-server/venv/bin/python",
        args=["/path/to/crawler-mcp-server/spider_mcp_server/server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化会话
            await session.initialize()
            
            # 抓取网页
            result = await session.call_tool("crawl_web_page", {
                "url": "https://github.com/unclecode/crawl4ai",
                "output_dir": "./crawl_results"
            })
            
            print("抓取完成！")
            print(f"结果: {result.content[0].text}")

# 运行示例
asyncio.run(crawl_example())
```

### 批量抓取多个网页

```python
urls = [
    "https://example.com",
    "https://github.com",
    "https://stackoverflow.com"
]

for url in urls:
    result = await session.call_tool("crawl_web_page", {
        "url": url,
        "output_dir": f"./results/{url.replace('https://', '').replace('/', '_')}"
    })
    print(f"已抓取: {url}")
```

## 🧪 开发和测试

### 运行测试

```bash
# 运行完整测试
python test_complete_crawler.py

# 或者使用 pytest（如果已安装）
pytest test/
```

### 开发模式

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行代码检查
flake8 spider_mcp_server/
black spider_mcp_server/
```

## 📚 API 参考

### 核心类和函数

#### `Crawl4aiExtractor`
主要的爬虫提取器类，封装了 crawl4ai 的功能。

**主要方法：**
- `extract_content(url: str) -> dict`: 提取网页内容
- `save_results(result: dict, output_dir: str, url: str)`: 保存结果到文件

#### `save_markdown_file(content: str, file_path: str) -> str`
保存 Markdown 内容到文件

#### `save_binary_file(data: bytes, file_path: str) -> str`
保存二进制数据（如截图、PDF）到文件

## ⚠️ 注意事项

1. **频率限制**：请合理控制抓取频率，避免对目标网站造成过大压力
2. **robots.txt**：请遵守目标网站的 robots.txt 规则
3. **法律合规**：确保抓取行为符合相关法律法规和网站使用条款
4. **依赖环境**：确保已安装所有必要的系统依赖（如 Chrome/Chromium）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [crawl4ai 官方文档](https://github.com/unclecode/crawl4ai)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Claude Desktop 文档](https://docs.anthropic.com/claude/docs/overview)

## 📞 支持

如果您遇到问题或有建议，请：
1. 查看 [Issues](https://github.com/osins/crawler-mcp-server/issues) 页面
2. 创建新的 Issue 描述您的问题
3. 联系维护者

---

**Made with ❤️ using crawl4ai and MCP**