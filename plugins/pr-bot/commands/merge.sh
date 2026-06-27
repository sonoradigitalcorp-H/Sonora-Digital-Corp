#!/bin/bash
# pr:merge command — merges a pull request
# Usage: soulclone pr:merge <number> [--strategy merge|squash|rebase]
exec "$(dirname "$0")/../agents/pr-merger.sh" "$@"
