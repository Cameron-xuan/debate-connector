#!/usr/bin/env python3
"""OpenAI-compatible streaming bridge for debate-connector.
Reads prompt from stdin, streams response tokens to stdout.
Supports any API that follows the OpenAI chat.completions protocol
(OpenAI, DeepSeek, Qwen, vLLM, Ollama OpenAI compatibility mode, etc.)

Environment variables:
  OPENAI_API_KEY   Required. API key for the service.
  OPENAI_BASE_URL  Optional. Custom API endpoint (e.g. https://api.deepseek.com).
  OPENAI_MODEL     Optional. Model name. Default: gpt-4o
"""
from debate_connector.openai_stream import main


if __name__ == "__main__":
    raise SystemExit(main())
