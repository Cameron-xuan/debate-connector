"""OpenAI-compatible streaming bridge for debate-connector."""

import os
import sys

from openai import OpenAI

TEST_PROMPT = "Reply exactly with: OK"


def _write_stdout(text: str) -> None:
    sys.stdout.buffer.write(text.encode('utf-8', errors='replace'))
    sys.stdout.buffer.flush()


def _write_stderr(text: str) -> None:
    sys.stderr.buffer.write((text + '\n').encode('utf-8', errors='replace'))
    sys.stderr.buffer.flush()


def _is_test_mode() -> bool:
    return any(arg in ('--test', '--demo') for arg in sys.argv[1:])


def main() -> int:
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    base_url = os.environ.get("OPENAI_BASE_URL") or None
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        _write_stderr("[error] OPENAI_API_KEY not set")
        return 1

    prompt = TEST_PROMPT if _is_test_mode() else sys.stdin.read().strip()
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
                _write_stdout(delta)
    except Exception as exc:
        _write_stderr(f"[error] {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
