#!/usr/bin/env python3
"""Claude streaming bridge for debate-connector.
Reads prompt from stdin, streams response tokens to stdout."""
import sys
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"  # or "claude-opus-4-7" for stronger reasoning
MAX_TOKENS = 2048

prompt = sys.stdin.read().strip()
if not prompt:
    sys.exit(0)

client = Anthropic()
with client.messages.stream(
    model=MODEL,
    max_tokens=MAX_TOKENS,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
