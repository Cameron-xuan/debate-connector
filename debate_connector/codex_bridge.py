"""Codex CLI bridge for debate-connector."""

import subprocess
import sys


def main() -> int:
    prompt = sys.stdin.read()
    return subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", prompt],
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
