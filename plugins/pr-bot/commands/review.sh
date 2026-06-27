#!/bin/bash
# pr:review command — reviews a pull request
# Usage: soulclone pr:review <number>
exec "$(dirname "$0")/../agents/pr-reviewer.sh" "$@"
