#!/bin/bash
# Auto-commit script
set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD)
MESSAGE="${1:-chore: auto-commit}"

if [[ -n $(git status --porcelain) ]]; then
  git add -A
  git commit -m "${MESSAGE}"
  echo "Committed: ${MESSAGE}"
else
  echo "Nothing to commit."
fi
