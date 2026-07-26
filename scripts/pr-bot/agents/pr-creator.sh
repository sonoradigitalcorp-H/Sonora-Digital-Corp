#!/bin/bash
# PR Creator Agent — creates structured pull requests
# Usage: ./pr-creator.sh [--title TITLE] [--base BASE] [--body BODY]
set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
REMOTE="${REMOTE:-$($GH_BIN repo view --json nameWithOwner 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('nameWithOwner',''))" 2>/dev/null || true)}"
CURRENT_BRANCH="${CURRENT_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'main')}"
TITLE="${1:-}"
BASE="${2:-main}"
BODY="${3:-}"

if [ -z "$TITLE" ]; then
    TITLE=$(git log -1 --pretty=%s 2>/dev/null || echo "feat: auto PR $(date '+%Y-%m-%d')")
fi

if [ -z "$BODY" ]; then
    CHANGED=$(git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --name-only --cached 2>/dev/null || echo "")
    if [ -n "$CHANGED" ]; then
        BODY="## Cambios\n\n$(echo "$CHANGED" | sed 's/^/- /')\n\n---\n> PR creado por SoulClone PR Bot"
    fi
fi

if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "$TITLE" --allow-empty 2>/dev/null || true
fi

git push origin "$CURRENT_BRANCH" -u 2>&1

$GH_BIN pr create \
    --repo "$REMOTE" \
    --title "$TITLE" \
    --body "$(echo -e "$BODY")" \
    --base "$BASE" \
    --head "$CURRENT_BRANCH"
