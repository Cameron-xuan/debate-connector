"""OpenAI-compatible streaming bridge for debate-connector."""

import os
import sys

from openai import OpenAI


def main() -> int:
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        print("[error] OPENAI_API_KEY not set", file=sys.stderr)
        return 1

    prompt = sys.stdin.read().strip()
    if not prompt:
        return 0

    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            max_tokens=2048,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
