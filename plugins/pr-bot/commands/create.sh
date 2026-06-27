#!/bin/bash
# pr:create command — creates a pull request
# Usage: soulclone pr:create [--title TITLE] [--base BASE]
exec "$(dirname "$0")/../agents/pr-creator.sh" "$@"
