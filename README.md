# MCP Spider Server

An MCP (Model Context Protocol) spider server based on [crawl4ai](https://github.com/unclecode/crawl4ai) that provides powerful web crawling and content extraction capabilities.

## 🚀 Features

- **智能网络爬虫**: 基于 crawl4ai 的高效网页内容提取
- **LLM 增强提取**: 集成大语言模型，支持智能内容理解和结构化提取
- **多格式输出**: 支持 HTML、Markdown、JSON、PDF 和 PNG 格式
- **智能内容提取**: 使用 LLMExtractionStrategy 进行基于语义的内容提取
- **灵活配置**: 支持传统 CSS 选择器提取和 LLM 智能提取两种模式
- **截图功能**: 自动生成网页截图
- **PDF 导出**: 将网页内容导出为 PDF 文件
- **内容过滤**: 使用 PruningContentFilter 优化内容提取
- **结构化数据提取**: 支持 JsonCssExtractionStrategy 精确数据提取
- **文件下载**: 自动下载并保存引用文件
- **多模型支持**: 支持 Ollama、OpenAI、Claude 等多种 LLM 提供商
- **环境变量配置**: 灵活的模型配置和切换机制
- **MCP 协议支持**: 完全兼容 MCP 标准，可集成到支持 MCP 的客户端

## 📦 Installation

### Requirements

- Python 3.8+
- Virtual environment recommended
- **LLM 依赖**: 
  - `litellm` - 统一的多模型 LLM 接口
  - Ollama 或其他 LLM 提供商 (可选，用于智能内容提取)
- **浏览器依赖**: 
  - Chrome/Chromium (crawl4ai 需要)

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

### 🤖 LLM 配置选项

为了启用 LLM 增强功能，可以设置以下环境变量：

```bash
# 启用 LLM 模式
export CRAWL_MODE=llm

# LLM 提供商配置
export LLAMA_PROVIDER="ollama/qwen2.5-coder:latest"  # 默认值
export LLAMA_API_TOKEN="your_api_token"             # 可选，某些提供商需要
export LLAMA_BASE_URL="http://localhost:11434"       # 可选，自定义 API 端点
export LLAMA_MAX_TOKENS=4096                         # 可选，最大 token 数
```

**支持的 LLM 提供商:**
- **Ollama**: `ollama/model-name` (本地部署)
- **OpenAI**: `openai/gpt-4` / `openai/gpt-3.5-turbo`
- **Claude**: `anthropic/claude-3-sonnet`
- **其他**: 通过 litellm 支持的所有提供商

## 🛠️ MCP Protocol Usage Guide

### Client Development Based on MCP Protocol

This project is based on the [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) protocol and provides standardized tool call interfaces. Here are the key points for writing MCP clients:

#### 1. MCP Connection Establishment

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure server parameters
server_params = StdioServerParameters(
    command="/path/to/venv/bin/python",  # Python interpreter path
    args=["/path/to/server.py"]         # Server script path
)

# Establish stdio connection
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()  # Initialize session
```

#### 2. Tool Calls and Result Handling

**⚠️ Important: MCP Return Value Structure**

The MCP server returns a `CallToolResult` object, with the actual content in `result.content`:

```python
# ❌ Incorrect approach (common error)
for content in result:  # result is not iterable
    print(content.text)

# ✅ Correct approach
result = await session.call_tool("tool_name", {"param": "value"})
for content in result.content:  # Access content attribute
    if content.type == "text":  # Check content type
        print(content.text)
```

#### 3. Tool Interfaces for This Project

**Available Tools:**
- `say_hello` - Test connection
- `echo_message` - Echo message  
- `crawl_web_page` - Web page crawling

**crawl_web_page Tool Parameters:**
```python
{
    "url": "https://example.com",           # URL to crawl
    "save_path": "./output_directory"       # Save path
}
```

**Return Value Handling:**
```python
result = await session.call_tool("crawl_web_page", {
    "url": "https://github.com/unclecode/crawl4ai",
    "save_path": "./results"
})

# Parse return results correctly
for content in result.content:
    if content.type == "text":
        message = content.text
        print(f"Crawling result: {message}")
        
        # Message format example:
        # "Successfully crawled https://github.com/unclecode/crawl4ai and saved 8 files to ./results/20231119-143022"
```

#### 4. Error Handling Best Practices

```python
async def safe_crawl(session: ClientSession, url: str, save_path: str):
    try:
        result = await session.call_tool("crawl_web_page", {
            "url": url,
            "save_path": save_path
        })
        
        # Check return results
        if result.content:
            for content in result.content:
                if content.type == "text":
                    if "Failed to crawl" in content.text:
                        print(f"❌ Crawling failed: {content.text}")
                    else:
                        print(f"✅ Crawling successful: {content.text}")
        else:
            print("❌ No return result received")
            
    except Exception as e:
        print(f"❌ Tool call failed: {e}")
```

## 🛠️ Available Tools

### 1. `crawl_web_page`

Crawl webpage content from the specified URL and save in multiple formats. Supports both traditional CSS extraction and LLM-enhanced extraction modes.

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
- **LLM 智能提取** (当设置 CRAWL_MODE=llm 时启用):
  - 基于语义的内容理解
  - 自动去除导航、广告等非主要内容
  - 结构化的 Markdown 输出
  - 支持多种 LLM 提供商

**Example usage:**
```python
# 传统爬取模式
result = await session.call_tool("crawl_web_page", {
    "url": "https://example.com",
    "save_path": "./output_directory"
})

# LLM 增强模式 (设置环境变量)
os.environ["CRAWL_MODE"] = "llm"
os.environ["LLAMA_PROVIDER"] = "ollama/qwen2.5-coder:latest"
os.environ["LLAMA_BASE_URL"] = "http://localhost:11434"
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

# Run example
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

### LLM 增强爬取示例

```python
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def llm_enhanced_crawl():
    # 配置 LLM 环境变量
    os.environ["CRAWL_MODE"] = "llm"
    os.environ["LLAMA_PROVIDER"] = "ollama/qwen2.5-coder:latest"
    os.environ["LLAMA_BASE_URL"] = "http://localhost:11434"
    
    # 配置服务器连接
    server_params = StdioServerParameters(
        command="/path/to/venv/bin/python",
        args=["/path/to/spider_mcp_server/server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # LLM 增强爬取
            result = await session.call_tool("crawl_web_page", {
                "url": "https://example.com/article",
                "save_path": "./llm_results"
            })
            
            for content in result.content:
                if content.type == "text":
                    print(f"LLM 增强爬取结果: {content.text}")

asyncio.run(llm_enhanced_crawl())
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
│   ├── llm.py                # LLM configuration and extraction strategies
│   └── utils.py              # Utility functions for file I/O
├── test/                     # Test suite
│   ├── test_litellm_ollama.py # LLM integration tests
│   └── ...                   # Other test files
├── test_output/              # Test output directory
├── typings/                  # Type stubs for crawl4ai
├── pyproject.toml            # Project configuration
└── README.md                # This file
```

## 📚 API Reference

### Core Classes and Functions

#### `llm_config()` function (`llm.py`)
配置 LLM 增强爬取策略。

**参数:**
- `instruction` (str): 提取指令，默认为专门优化的网页内容提取指令

**返回:**
- `CrawlerRunConfig`: 配置了 LLM 提取策略的爬取配置

**特性:**
- 支持 litellm 的所有提供商
- 自动分块处理大型内容
- 智能内容过滤和结构化输出
- 可配置的温度和 token 参数

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

#### `crawl_config()` function (`crawl.py`)
动态选择爬取配置，根据环境变量决定是否启用 LLM 模式。

**环境变量:**
- `CRAWL_MODE=llm`: 启用 LLM 增强提取
- 其他值: 使用传统 CSS 选择器提取

## 🎯 Configuration Details

### LLM 提取策略

当启用 LLM 模式时，使用以下智能提取配置：

**默认提取指令:**
```
You are a **Web Content Extraction Assistant**. Your task is to extract the **complete, clean, and precise main text content** from a given web page...
```

**LLM 配置参数:**
- `provider`: 通过 `LLAMA_PROVIDER` 环境变量配置
- `api_token`: 通过 `LLAMA_API_TOKEN` 环境变量配置
- `base_url`: 通过 `LLAMA_BASE_URL` 环境变量配置  
- `max_tokens`: 默认 4096，可通过 `LLAMA_MAX_TOKENS` 调整
- `temperature`: 0.1 (确保输出稳定性)
- `chunk_token_threshold`: 1400 (分块处理阈值)
- `apply_chunking`: true (启用内容分块)

### CSS Extraction Strategy

传统模式使用预配置的 CSS 提取模式：

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

使用 `PruningContentFilter` 配置：
- `threshold`: 0.35 (动态阈值)
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
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Ollama Documentation](https://github.com/ollama/ollama)
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

## 🛠️ Available Tools

---

**Made with ❤️ using crawl4ai and MCP**

*Current Version: 0.1.0*