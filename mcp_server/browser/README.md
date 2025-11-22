# 浏览器功能模块说明

## 概述

此模块为 MCP (Model Context Protocol) 服务器添加了浏览器自动化功能，使用 Playwright 实现。提供了三个主要功能：

1. 获取指定 URL 地址的页面内容
2. 获取指定页面的控制台信息
3. 获取指定页面加载的所有网络请求列表

这些功能旨在协助 AI 分析页面和接口的功能执行情况。

## 功能详情

### 1. get_page_content

获取指定 URL 地址的页面内容。

#### 参数
- `url` (string, required): 目标页面的 URL
- `wait_for_selector` (string, optional): 可选，等待页面中特定元素出现的 CSS 选择器
- `wait_timeout` (integer, optional): 等待超时时间（毫秒），默认 30000

#### 返回值
包含以下字段的 JSON 对象：
- `url`: 请求的 URL
- `status`: HTTP 状态码
- `title`: 页面标题
- `html`: 页面 HTML 内容
- `text`: 页面文本内容
- `meta`: 页面元数据
- `links`: 页面链接列表
- `images`: 页面图片列表
- `timestamp`: 操作时间戳

### 2. get_console_messages

获取指定页面的控制台信息。

#### 参数
- `url` (string, required): 目标页面的 URL
- `wait_for_selector` (string, optional): 可选，等待页面中特定元素出现的 CSS 选择器
- `wait_timeout` (integer, optional): 等待超时时间（毫秒），默认 30000

#### 返回值
包含以下字段的 JSON 对象：
- `url`: 请求的 URL
- `status`: HTTP 状态码
- `console_messages`: 控制台消息列表，每条消息包含类型、文本、位置和堆栈信息
- `timestamp`: 操作时间戳

### 3. get_network_requests

获取指定页面加载的所有网络请求列表。

#### 参数
- `url` (string, required): 目标页面的 URL
- `wait_for_selector` (string, optional): 可选，等待页面中特定元素出现的 CSS 选择器
- `wait_timeout` (integer, optional): 等待超时时间（毫秒），默认 30000

#### 返回值
包含以下字段的 JSON 对象：
- `url`: 请求的 URL
- `status`: HTTP 状态码
- `requests`: 请求列表，每条请求包含 URL、方法、资源类型等信息
- `responses`: 响应列表，每条响应包含 URL、状态码、头信息等
- `total_requests`: 总请求数
- `total_responses`: 总响应数
- `timestamp`: 操作时间戳

## 安全措施

- URL 长度限制（最大 2048 字符）
- 阻止访问本地网络地址（localhost, 127.0.0.1, 内网地址等）
- 验证 URL 格式，仅支持 http 和 https 协议
- 检查 URL 中的潜在危险字符