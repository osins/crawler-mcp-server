# MCP Server for Web Crawling

An MCP (Model Context Protocol) server that provides web crawling capabilities using crawl4ai. Supports multiple content formats output (HTML, JSON, PDF, screenshots, Markdown) and browser interaction features.

## Table of Contents

- [MCP Configuration](#mcp-configuration)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## MCP Configuration

To configure this server with MCP, add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "dev-tool-mcp": {
      "command": "/path/to/dev-tool-mcp/venv/bin/python",
      "args": [
        "/path/to/dev-tool-mcp/mcp_server/server.py"
      ],
      "description": "MCP development tool server providing web crawling, browser automation, content extraction, and real-time page analysis capabilities"
    }
  }
}
```

Make sure to replace `/path/to/dev-tool-mcp/` with the actual path to your project directory.

## Features

- **Web Crawling**: Advanced web crawling capabilities using crawl4ai
- **Multiple Output Formats**: Support for HTML, JSON, PDF, screenshots, and Markdown output
- **Browser Interaction**: Get page content, console messages, and network requests
- **LLM Integration**: Supports LLM extraction strategies for content processing
- **File Download**: Automatic download and saving of files found on crawled pages
- **Progress Tracking**: Streaming progress updates during crawling operations
- **Security**: URL validation and sanitization to prevent security issues

## Architecture

The MCP server is structured into the following modules:

```
mcp_server/
├── server.py          # Main MCP server definition and tool handling
├── utils.py          # Utility functions for file operations
├── browser/          # Browser automation functionality
│   ├── browser_service.py  # Playwright-based browser service
│   └── README.md     # Browser module documentation
└── crawl/            # Web crawling functionality
    └── crawl.py      # Core crawling implementation with crawl4ai
```

### Core Components

- **Server**: Implements MCP protocol with tool registration and execution
- **BrowserService**: Manages Playwright browser instances for page content and network monitoring
- **Crawler**: Uses crawl4ai for advanced web crawling with multiple output formats
- **Utils**: Provides file handling utilities for saving content

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- System dependencies for Playwright (Chromium browser)

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcp-server
   ```

2. Install the package and dependencies:
   ```bash
   pip install -e .
   ```

3. Install Playwright browsers:
   ```bash
   python -m playwright install chromium
   ```

### Dependencies

The server requires the following dependencies (automatically installed via pip):

- `crawl4ai>=0.7.7`: Web crawling library
- `pydantic>=2.0.0`: Data validation
- `mcp==1.0.0`: Model Context Protocol implementation
- `httpx[socks]`: HTTP client
- `litellm`: LLM interface
- `beautifulsoup4>=4.12.2`: HTML parsing
- `lxml>=4.9.3`: XML/HTML processing
- `sentencepiece`: Text processing
- `playwright>=1.40.0`: Browser automation

## Configuration

### Environment Variables

The server uses the following environment variables (optional):

- `TEST_URL`: URL for testing (used in test files)

### Available Tools

The server exposes the following tools via MCP:

#### say_hello
- **Description**: A simple greeting tool that returns personalized messages to users
- **Parameters**:
  - `name` (string, optional): The name to greet, defaults to "World"
- **Returns**: Greeting message text

#### echo_message
- **Description**: Echo tool that returns user-provided information as-is
- **Parameters**:
  - `message` (string, required): The message to echo back
- **Returns**: Echoed message text

#### crawl_web_page
- **Description**: Crawl web page content and save in multiple formats (HTML, JSON, PDF, screenshots) while downloading file resources from the page
- **Parameters**:
  - `url` (string, required): The URL of the web page to crawl
  - `save_path` (string, required): The base file path to save the crawled content and downloaded files
  - `instruction` (string, optional): The instruction to use for the LLM (default: "")
  - `save_screenshot` (boolean, optional): Save a screenshot of the page (default: false)
  - `save_pdf` (boolean, optional): Save a PDF of the page (default: false)
  - `generate_markdown` (boolean, optional): Generate a Markdown representation of the page (default: false)
- **Returns**: Success message with file count and save location

#### get_page_content
- **Description**: Get complete content of a specified URL webpage, including HTML structure and page data
- **Parameters**:
  - `url` (string, required): The URL of the web page to get content from
  - `wait_for_selector` (string, optional): Optional CSS selector to wait for before getting content
  - `wait_timeout` (integer, optional): Wait timeout in milliseconds, default 30000
- **Returns**: JSON object containing page content, title, HTML, text, metadata, links, and images

#### get_console_messages
- **Description**: Capture console output information from specified URL webpage (including logs, warnings, errors, etc.)
- **Parameters**:
  - `url` (string, required): The URL of the web page to get console messages from
  - `wait_for_selector` (string, optional): Optional CSS selector to wait for before getting console messages
  - `wait_timeout` (integer, optional): Wait timeout in milliseconds, default 30000
- **Returns**: JSON object containing console messages with type, text, location, and stack information

#### get_network_requests
- **Description**: Monitor and retrieve all network requests initiated by specified URL webpage (API calls, resource loading, etc.)
- **Parameters**:
  - `url` (string, required): The URL of the web page to get network requests from
  - `wait_for_selector` (string, optional): Optional CSS selector to wait for before getting network requests
  - `wait_timeout` (integer, optional): Wait timeout in milliseconds, default 30000
- **Returns**: JSON object containing requests and responses with URLs, status, headers, and timing information

## Usage

### Running the Server

The server can be started using the console script defined in pyproject.toml:

```bash
dev-tool-mcp
```

Or directly via Python:

```bash
python -m mcp_server.server
```

The server uses stdio for MCP communication, making it compatible with MCP clients.

### Tool Examples

#### Crawling a Web Page

To crawl a web page and save content in multiple formats:

```json
{
  "name": "crawl_web_page",
  "arguments": {
    "url": "https://example.com",
    "save_path": "/path/to/save",
    "save_screenshot": true,
    "save_pdf": true,
    "generate_markdown": true
  }
}
```

This will create a timestamped subdirectory with:
- `output.html` - Page HTML content
- `output.json` - Page content in JSON format
- `output.png` - Screenshot of the page (if requested)
- `output.pdf` - PDF of the page (if requested)
- `raw_markdown.md` - Markdown representation of the page (if requested)
- `downloaded_files.json` - List of downloaded files
- `files/` - Directory containing downloaded files

#### Getting Page Content

To retrieve page content:

```json
{
  "name": "get_page_content",
  "arguments": {
    "url": "https://example.com",
    "wait_for_selector": "#main-content",
    "wait_timeout": 10000
  }
}
```

#### Getting Console Messages

To capture console messages from a page:

```json
{
  "name": "get_console_messages",
  "arguments": {
    "url": "https://example.com",
    "wait_for_selector": ".app",
    "wait_timeout": 15000
  }
}
```

#### Getting Network Requests

To monitor network requests made by a page:

```json
{
  "name": "get_network_requests",
  "arguments": {
    "url": "https://example.com",
    "wait_for_selector": "[data-loaded]",
    "wait_timeout": 20000
  }
}
```

## Testing

The project includes comprehensive tests for both browser and crawler functionality:

### Run Tests

```bash
# Run all tests
pytest

# Run specific test files
python -m pytest test/test_crawler.py
python -m pytest test/test_browser.py

# Run browser tests directly
python -m test.test_browser
```

### Test Coverage

- `test_crawler.py`: Tests the complete crawler functionality, including file saving and format generation
- `test_browser.py`: Tests browser service functions for page content, console messages, and network requests

The crawler test specifically verifies:
- HTML, JSON, PDF, screenshot, and Markdown file generation
- File download and saving functionality
- Proper error handling and directory creation

## Deployment

### Production Deployment

1. Install the package in your production environment:
   ```bash
   pip install dev-tool-mcp
   ```

2. Install Playwright browsers:
   ```bash
   python -m playwright install chromium --with-deps
   ```

3. Run the server:
   ```bash
   dev-tool-mcp
   ```

### Docker Deployment (Optional)

Create a Dockerfile for containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY mcp_server/ ./mcp_server/

RUN pip install -e .
RUN python -m playwright install chromium --with-deps

CMD ["dev-tool-mcp"]
```

## Security

### URL Validation

The server includes security measures to prevent malicious URLs:

- URL length limit (2048 characters)
- Protocol validation (only http/https allowed)
- Input sanitization to prevent injection attacks
- Validation to prevent access to local network addresses

### Browser Security

- Playwright runs in headless mode by default
- Security flags are set to disable dangerous features
- Browser runs with limited privileges

### File System Security

- Files are saved only to explicitly specified paths
- No arbitrary file system access is allowed
- Temporary files are properly cleaned up

## Troubleshooting

### Common Issues

#### Playwright Browser Not Found

If you encounter browser-related errors:

```bash
python -m playwright install chromium
```

#### Permission Errors

Ensure the server has write permissions to the specified save paths:

```bash
mkdir -p /path/to/save
chmod 755 /path/to/save
```

#### Network Issues

For network-related crawling issues, verify:
- The target URL is accessible
- No firewall restrictions exist
- Appropriate timeout values are set

#### Memory Usage

Large page crawls can consume significant memory. For large-scale crawling:
- Monitor memory usage
- Process pages sequentially rather than in parallel
- Clean up temporary files regularly

### Debugging

Enable verbose logging to troubleshoot issues:

```bash
# Check the server logs for error messages
# Monitor file system permissions
# Verify network connectivity to target URLs
```

## Version Information

- **Package**: dev-tool-mcp
- **Version**: 0.1.0
- **Python Support**: 3.8+
- **Dependencies**: See pyproject.toml for exact versions

## License

This project is licensed under the terms specified in the pyproject.toml file. See the project repository for full license details.