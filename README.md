# MCP Spider Server

An MCP (Model Context Protocol) spider server based on [crawl4ai](https://github.com/unclecode/crawl4ai) that provides powerful web crawling and content extraction capabilities.

## 🚀 Features

- **Intelligent Web Crawling**: Use crawl4ai for efficient web content extraction
- **Multi-format Output**: Support HTML, Markdown, JSON, PDF, and PNG formats
- **Screenshot Function**: Automatic webpage screenshot generation
- **PDF Export**: Export webpage content as PDF files
- **Content Filtering**: Use PruningContentFilter to optimize content extraction
- **Structured Data Extraction**: Support JsonCssExtractionStrategy for precise data extraction
- **File Downloads**: Automatically download and save referenced files
- **MCP Protocol Support**: Fully compatible with MCP standard, integrable with MCP-supporting clients

## 📦 Installation

### Requirements

- Python 3.8+
- Virtual environment recommended

### Installation Steps

1. **Clone repository**
```bash
git clone https://github.com/osins/crawler-mcp-server.git
cd crawler-mcp-server
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -e .
```

## 🔧 MCP Service Configuration

### Claude Desktop Configuration Example

Add the following configuration to Claude Desktop's configuration file:

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

### General MCP Client Configuration

If you use other MCP clients, you can use the following general configuration:

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

### 📋 Configuration Notes

**Direct script execution is all you need:**
- No environment variables needed
- No need to use `-m` parameter
- Python automatically handles relative imports
- Most simple and reliable configuration

## 🛠️ MCP 协议使用指南

### 基于 MCP 协议的客户端开发

本项目基于 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 协议，提供标准化的工具调用接口。以下是编写 MCP 客户端的核心要点：

#### 1. MCP 连接建立

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 配置服务器参数
server_params = StdioServerParameters(
    command="/path/to/venv/bin/python",  # Python 解释器路径
    args=["/path/to/server.py"]         # 服务器脚本路径
)

# 建立 stdio 连接
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()  # 初始化会话
```

#### 2. 工具调用与结果处理

**⚠️ 重要：MCP 返回值结构**

MCP 服务器返回的是 `CallToolResult` 对象，实际内容在 `result.content` 中：

```python
# ❌ 错误的写法（常见错误）
for content in result:  # result 不是可迭代对象
    print(content.text)

# ✅ 正确的写法
result = await session.call_tool("tool_name", {"param": "value"})
for content in result.content:  # 访问 content 属性
    if content.type == "text":  # 检查内容类型
        print(content.text)
```

#### 3. 本项目的工具接口

**可用工具列表：**
- `say_hello` - 测试连接
- `echo_message` - 回显消息  
- `crawl_web_page` - 网页爬取

**crawl_web_page 工具参数：**
```python
{
    "url": "https://example.com",           # 要爬取的URL
    "save_path": "./output_directory"       # 保存路径
}
```

**返回值处理：**
```python
result = await session.call_tool("crawl_web_page", {
    "url": "https://github.com/unclecode/crawl4ai",
    "save_path": "./results"
})

# 正确解析返回结果
for content in result.content:
    if content.type == "text":
        message = content.text
        print(f"爬取结果: {message}")
        
        # 消息格式示例：
        # "Successfully crawled https://github.com/unclecode/crawl4ai and saved 8 files to ./results/20231119-143022"
```

#### 4. 错误处理最佳实践

```python
async def safe_crawl(session: ClientSession, url: str, save_path: str):
    try:
        result = await session.call_tool("crawl_web_page", {
            "url": url,
            "save_path": save_path
        })
        
        # 检查返回结果
        if result.content:
            for content in result.content:
                if content.type == "text":
                    if "Failed to crawl" in content.text:
                        print(f"❌ 爬取失败: {content.text}")
                    else:
                        print(f"✅ 爬取成功: {content.text}")
        else:
            print("❌ 未收到返回结果")
            
    except Exception as e:
        print(f"❌ 调用工具失败: {e}")
```

## 🛠️ Available Tools

### 1. `crawl_web_page`

Crawl webpage content from the specified URL and save in multiple formats.

**Parameters:**
- `url` (string, required): The webpage URL to crawl
- `save_path` (string, required): The directory path to save crawled content

**Features:**
- Automatic webpage screenshot (PNG)
- PDF export generation
- Raw Markdown content extraction
- Cleaned/filtered Markdown content
- Structured data extraction (JSON)
- HTML content preservation
- Downloaded files processing

**Example usage:**
```python
# Crawl webpage and save to specified directory
result = await session.call_tool("crawl_web_page", {
    "url": "https://example.com",
    "save_path": "./output_directory"
})
```

### 2. `say_hello`

Simple greeting tool for testing server connectivity.

**Parameters:**
- `name` (string, optional): Name to greet, defaults to "World"

**Example usage:**
```python
result = await session.call_tool("say_hello", {
    "name": "Alice"
})
```

### 3. `echo_message`

Echo messages back to test communication.

**Parameters:**
- `message` (string, required): The message to echo

**Example usage:**
```python
result = await session.call_tool("echo_message", {
    "message": "Hello MCP!"
})
```

## 📁 Output File Structure

After crawling, the following files will be generated in the specified output directory:

```
output_directory/
├── output.html              # Complete HTML content
├── output.json              # Structured data (CSS-extracted JSON)
├── output.png               # Webpage screenshot
├── output.pdf               # PDF version of the page
├── raw_markdown.md          # Raw markdown extraction
├── fit_markdown.md          # Cleaned/filtered markdown
├── downloaded_files.json    # List of downloaded files (if any)
└── files/                   # Downloaded files directory (if any)
```

## 🔍 Usage Examples

### Basic Web Crawling

```python
import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def crawl_example():
    # Configure server connection parameters (adjust paths as needed)
    project_root = Path("/path/to/your/crawler-mcp-server")
    server_params = StdioServerParameters(
        command=str(project_root / "venv" / "bin" / "python"),
        args=[str(project_root / "spider_mcp_server" / "server.py")]
    )
    
    # Create output directory
    output_dir = "./crawl_results"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Connect to MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                
                # Call crawling tool
                result = await session.call_tool("crawl_web_page", {
                    "url": "https://github.com/unclecode/crawl4ai",
                    "save_path": output_dir
                })
                
                # ✅ Correct return value handling
                # MCP server returns CallToolResult object, content is in result.content
                for content in result.content:
                    if content.type == "text":
                        print(f"✅ Crawling result: {content.text}")
                        
    except Exception as e:
        print(f"❌ Crawling failed: {e}")

# 运行示例
asyncio.run(crawl_example())
```

### Batch Crawling Multiple Webpages

```python
urls = [
    "https://example.com",
    "https://github.com", 
    "https://stackoverflow.com"
]

for i, url in enumerate(urls):
    result = await session.call_tool("crawl_web_page", {
        "url": url,
        "save_path": f"./results/crawl_{i+1}"
    })
    
    # ✅ Correct return value handling
    for content in result.content:
        if content.type == "text":
            print(f"Crawled: {url} - {content.text}")
    
    # Add delay to avoid too frequent requests
    await asyncio.sleep(2)
```

## 🧪 Development and Testing

### Run Tests

The project includes a comprehensive test suite:

```bash
# Run complete crawler test with real file output
python test/test_complete_crawler.py

# Run individual component tests
python test/test_hello.py      # Test hello/echo functions
python test/test_server.py     # Test MCP server functionality
python test/test_crawl.py      # Test crawling functions
python test/test_complete.py    # Test complete workflow
```

### Test Directory Structure

```
test/
├── test_complete_crawler.py    # Full integration test
├── test_hello.py             # Hello/echo functionality
├── test_server.py            # MCP server protocol
├── test_crawl.py             # Core crawling logic
└── test_complete.py          # End-to-end workflow
```

### Development Mode

```bash
# Install development dependencies
pip install -e ".[dev]"

# The project uses pyright for type checking (configured in pyproject.toml)
# No additional linting tools are configured
```

## 📚 Project Structure

```
crawler-mcp-server/
├── spider_mcp_server/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── server.py              # MCP server implementation
│   ├── crawl.py              # Crawling logic and file handling
│   └── utils.py              # Utility functions for file I/O
├── test/                     # Test suite
├── test_output/              # Test output directory
├── typings/                  # Type stubs for crawl4ai
├── pyproject.toml            # Project configuration
└── README.md                # This file
```

## 📚 API Reference

### Core Classes and Functions

#### `save()` function (`utils.py`)
Save content to files with proper encoding handling.

**Parameters:**
- `path`: Directory path
- `name`: Filename
- `s`: Content (string, bytes, or bytearray)
- `call`: Callback function with saved file path

#### `saveJson()` function (`crawl.py`)
Async function to save downloaded files information and handle file downloads.

**Features:**
- Saves `downloaded_files.json` with file metadata
- Downloads and saves referenced files to `files/` subdirectory
- Error handling for failed downloads

## 🎯 Configuration Details

### CSS Extraction Strategy

The crawler uses a pre-configured CSS extraction schema:

```javascript
{
  "baseSelector": "body",
  "fields": [
    {"name": "title", "selector": "h2", "type": "text"},
    {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
    {"name": "p", "selector": "p", "type": "text"}
  ]
}
```

### Content Filtering

Uses `PruningContentFilter` with these settings:
- `threshold`: 0.35 (dynamic threshold)
- `min_word_threshold`: 3
- `threshold_type`: "dynamic"

### Browser Configuration

- Headless mode enabled
- JavaScript enabled
- Bypass cache for fresh content

## ⚠️ Important Notes

1. **Rate Limiting**: Please control crawling frequency reasonably to avoid excessive pressure on target websites
2. **robots.txt**: Please comply with robots.txt rules of target websites
3. **Legal Compliance**: Ensure crawling behavior complies with relevant laws, regulations and website terms of use
4. **Browser Requirements**: crawl4ai requires a browser engine (Chrome/Chromium) to be installed on the system
5. **Memory Usage**: Large screenshots and PDFs may consume significant memory and disk space

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project uses MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Links

- [crawl4ai Official Documentation](https://github.com/unclecode/crawl4ai)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Desktop Documentation](https://docs.anthropic.com/claude/docs/overview)
- [Project Package](https://pypi.org/project/spider-mcp/)

## 📞 Support

If you encounter problems or have suggestions:

1. **Check Issues**: [GitHub Issues](https://github.com/osins/crawler-mcp-server/issues)
2. **Create New Issue**: Report bugs or request features
3. **Test First**: Run `python test/test_complete_crawler.py` to verify setup

## 🎮 CLI Entry Point

The package includes a CLI entry point:

```bash
# After installation
spider-mcp
```

This is equivalent to running:
```bash
python -m spider_mcp_server.server
```

## 📚 完整示例代码

项目提供了完整的客户端示例代码：

```
examples/
├── mcp_client_tutorial.py    # 完整教程（推荐）
├── quick_start.py           # 快速开始示例
└── README.md               # 示例说明
```

### 运行示例

```bash
# 进入项目目录
cd crawler-mcp-server

# 安装依赖（如果还未安装）
pip install -e .

# 运行完整教程
python examples/mcp_client_tutorial.py

# 运行快速开始示例
python examples/quick_start.py
```

### 示例功能

**完整教程 (mcp_client_tutorial.py):**
- ✅ 环境自动检测
- ✅ 连接管理封装
- ✅ 错误处理演示
- ✅ 批量爬取示例
- ✅ 结果解析演示
- ✅ 最佳实践展示

**快速开始 (quick_start.py):**
- ✅ 最简使用方式
- ✅ 核心API演示
- ✅ 正确的返回值处理

这些示例展示了如何正确使用 MCP 协议与 spider-mcp-server 交互，包括：
- 正确的连接建立方式
- ✅ 准确的返回值解析（`result.content` 而不是直接迭代 `result`）
- 完整的错误处理机制
- 实际的使用场景演示

---

**Made with ❤️ using crawl4ai and MCP**

*Current Version: 0.1.0*