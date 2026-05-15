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
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("[error] openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
BASE_URL = os.environ.get("OPENAI_BASE_URL") or None
API_KEY = os.environ.get("OPENAI_API_KEY", "")

if not API_KEY:
    print("[error] OPENAI_API_KEY not set", file=sys.stderr)
    sys.exit(1)

prompt = sys.stdin.read().strip()
if not prompt:
    sys.exit(0)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        max_tokens=2048,
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
except Exception as e:
    print(f"[error] {e}", file=sys.stderr)
    sys.exit(1)
