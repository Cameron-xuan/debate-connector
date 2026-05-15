#!/bin/bash
# 从 stdin 读取 prompt，传给 codex exec
PROMPT=$(cat)
codex exec --skip-git-repo-check "$PROMPT"
