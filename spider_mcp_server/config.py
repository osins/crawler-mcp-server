# config.py
import os

# 模型名称，必须确保 Ollama 已 pull
OLLAMA_MODEL = os.getenv("LLAMA_PROVIDER", "ollama/gemma3:4b")

OLLAMA_TOKEN = os.getenv("LLAMA_API_TOKEN", None)

OLLAMA_ENCODING = os.getenv("LLAMA_ENCODING", "cl100k_base")

# Ollama 服务地址
OLLAMA_API_BASE = os.getenv("LLAMA_BASE_URL", "http://192.168.50.2:11434")

# 请求超时（秒）
OLLAMA_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 360))

# 最大输入长度（生产环境要严格限制避免OOM）
OLLAMA_MAX_INPUT_LEN = os.getenv("LLAMA_MAX_TOKENS", 100000)
