#!/bin/bash
# pr:list command — lists open pull requests
# Usage: soulclone pr:list [--state open|closed|merged]
set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
STATE="${1:-open}"
REMOTE="${REMOTE:-$($GH_BIN repo view --json nameWithOwner 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('nameWithOwner',''))" 2>/dev/null || true)}"

if [ -z "$REMOTE" ]; then
    echo "❌ No GitHub remote found"
    exit 1
fi

$GH_BIN pr list --repo "$REMOTE" --state "$STATE" --limit 20 \
    --json number,title,state,headRefName,baseRefName,createdAt,url \
    | python3 -m json.tool 2>/dev/null
