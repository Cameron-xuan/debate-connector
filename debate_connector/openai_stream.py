"""OpenAI-compatible streaming bridge for debate-connector."""

import os
import sys
from typing import Optional

from openai import OpenAI

TEST_PROMPT = "Reply exactly with: OK"


def _sanitize(text: str) -> str:
    """Strip lone surrogates (\\udcXX) that arise on Windows when
    sys.stdin/env decodes pipe bytes with a non-UTF-8 codepage +
    surrogateescape handler, which then break strict UTF-8 encoding
    inside httpx/openai when building the request."""
    return text.encode('utf-8', errors='replace').decode('utf-8')


def _write_stdout(text: str) -> None:
    sys.stdout.buffer.write(text.encode('utf-8', errors='replace'))
    sys.stdout.buffer.flush()


def _write_stderr(text: str) -> None:
    sys.stderr.buffer.write((text + '\n').encode('utf-8', errors='replace'))
    sys.stderr.buffer.flush()


def _is_test_mode() -> bool:
    return any(arg in ('--test', '--demo') for arg in sys.argv[1:])


def _read_stdin() -> str:
    data = sys.stdin.buffer.read()
    return data.decode('utf-8', errors='replace').strip()


def _write_missing_key_hint() -> None:
    _write_stderr("[error] OPENAI_API_KEY not set")
    _write_stderr('[hint] macOS/Linux: export OPENAI_API_KEY="sk-..."')
    _write_stderr('[hint] Windows PowerShell: $env:OPENAI_API_KEY="sk-..."')


def _write_api_error_hint(exc: Exception, model: str, base_url: Optional[str]) -> None:
    _write_stderr(f"[error] {exc}")
    _write_stderr(f"[hint] OPENAI_MODEL={model}")
    _write_stderr(f"[hint] OPENAI_BASE_URL={base_url or '(default OpenAI endpoint)'}")
    _write_stderr("[hint] Check your API key, model name, base URL, network, and account quota.")


def run_openai_stream(prompt: str) -> int:
    model = _sanitize(os.environ.get("OPENAI_MODEL", "gpt-4o"))
    base_url = _sanitize(os.environ.get("OPENAI_BASE_URL") or "") or None
    api_key = _sanitize(os.environ.get("OPENAI_API_KEY", ""))

    if not api_key:
        _write_missing_key_hint()
        return 1

    if not prompt:
        return 0
    prompt = _sanitize(prompt)

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
        _write_api_error_hint(exc, model, base_url)
        return 1

    return 0


def run_test() -> int:
    return run_openai_stream(TEST_PROMPT)


def main() -> int:
    prompt = TEST_PROMPT if _is_test_mode() else _read_stdin()
    return run_openai_stream(prompt)


if __name__ == "__main__":
    raise SystemExit(main())
