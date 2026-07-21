#!/bin/bash
# PR Merger Agent — merges approved PRs with correct strategy
# Usage: ./pr-merger.sh <pr-number> [--strategy merge|squash|rebase]
set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
REMOTE="${REMOTE:-$($GH_BIN repo view --json nameWithOwner 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('nameWithOwner',''))" 2>/dev/null || true)}"
PR_NUMBER="${1:-}"
STRATEGY="${2:-merge}"

if [ -z "$PR_NUMBER" ]; then
    echo "Usage: $0 <pr-number> [--strategy merge|squash|rebase]"
    exit 1
fi

echo "🔀 Merging PR #$PR_NUMBER with $STRATEGY strategy..."

# Check PR status
PR_STATE=$($GH_BIN pr view "$PR_NUMBER" --repo "$REMOTE" --json state --jq '.state' 2>/dev/null || echo "")
if [ "$PR_STATE" != "OPEN" ]; then
    echo "❌ PR #$PR_NUMBER is not open (state: $PR_STATE)"
    exit 1
fi

# Check mergeability
MERGEABLE=$($GH_BIN pr view "$PR_NUMBER" --repo "$REMOTE" --json mergeable --jq '.mergeable' 2>/dev/null || echo "")
if [ "$MERGEABLE" = "CONFLICTING" ]; then
    echo "❌ PR #$PR_NUMBER has merge conflicts"
    exit 1
fi

# Merge
$GH_BIN pr merge "$PR_NUMBER" --repo "$REMOTE" "--$STRATEGY" --delete-branch

echo "✅ PR #$PR_NUMBER merged successfully ($STRATEGY)"
