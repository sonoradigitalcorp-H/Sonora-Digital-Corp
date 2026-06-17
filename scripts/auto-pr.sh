#!/bin/bash
# JARVIS — Auto PR
# Creates a branch, commits changes, pushes, and opens a PR
# Usage: bash scripts/auto-pr.sh [--title "title"] [--body "body"] [--base main] [--head branch]
set -euo pipefail

PROJECT_DIR="/home/mystic/jarvis"
cd "$PROJECT_DIR"

TITLE=""
BODY=""
BASE="main"
HEAD=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --title) TITLE="$2"; shift 2 ;;
        --body) BODY="$2"; shift 2 ;;
        --base) BASE="$2"; shift 2 ;;
        --head) HEAD="$2"; shift 2 ;;
        --help) echo "Usage: $0 [--title 'title'] [--body 'body'] [--base main] [--head branch]"; exit 0 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

# Detect gh binary
GH_BIN=""
for p in /usr/bin/gh /home/mystic/.local/bin/gh /snap/bin/gh; do
    [ -x "$p" ] && { GH_BIN="$p"; break; }
done
if [ -z "$GH_BIN" ]; then
    GH_BIN="gh"
fi

# Validate gh auth
if ! $GH_BIN auth status 2>&1 | grep -q "Logged in"; then
    echo "❌ GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Determine remote
REMOTE=$($GH_BIN repo view --json nameWithOwner 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('nameWithOwner',''))" 2>/dev/null || true)
if [ -z "$REMOTE" ]; then
    echo "❌ No GitHub remote found"
    exit 1
fi

# Auto-generate branch name from current branch or SDD feature
if [ -z "$HEAD" ]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
        # Create feature branch from SDD spec or timestamp
        if [ -f .specify/feature.json ]; then
            FEATURE_DIR=$(python3 -c "import json; print(json.load(open('.specify/feature.json')).get('feature_directory',''))" 2>/dev/null || true)
            if [ -n "$FEATURE_DIR" ]; then
                BRANCH_NAME=$(basename "$FEATURE_DIR")
            fi
        fi
        if [ -z "${BRANCH_NAME:-}" ]; then
            BRANCH_NAME="pr-$(date +%Y%m%d-%H%M%S)"
        fi
        git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME" 2>/dev/null || true
        HEAD="$BRANCH_NAME"
    else
        HEAD="$CURRENT_BRANCH"
    fi
fi

# Auto-generate title from recent commits if not provided
if [ -z "$TITLE" ]; then
    LATEST_COMMIT=$(git log -1 --pretty=%s 2>/dev/null || echo "")
    if [ -n "$LATEST_COMMIT" ]; then
        TITLE="$LATEST_COMMIT"
    else
        TITLE="feat: auto PR $(date '+%Y-%m-%d %H:%M')"
    fi
fi

# Auto-generate body from spec if available
if [ -z "$BODY" ]; then
    SPEC_FILE=""
    if [ -f .specify/feature.json ]; then
        FEATURE_DIR=$(python3 -c "import json; print(json.load(open('.specify/feature.json')).get('feature_directory',''))" 2>/dev/null || true)
        if [ -n "$FEATURE_DIR" ] && [ -f "$FEATURE_DIR/spec.md" ]; then
            SPEC_FILE="$FEATURE_DIR/spec.md"
        fi
    fi
    if [ -n "$SPEC_FILE" ]; then
        BODY=$(python3 -c "
import re
with open('$SPEC_FILE') as f:
    content = f.read()
# Extract first meaningful section
match = re.search(r'(?:##?\s*(?:Descripción|Descripcion|Description|Objetivo|Purpose).*?)(?=\n##?\s)', content, re.DOTALL)
if match:
    print(match.group(0).strip()[:2000])
else:
    print(content[:2000].strip())
" 2>/dev/null || echo "Auto PR from JARVIS SDD workflow")
    else
        # Collect changed file summary
        CHANGED_FILES=$(git diff --name-only HEAD~1..HEAD 2>/dev/null | head -20 || git diff --name-only --cached 2>/dev/null | head -20 || echo "")
        if [ -n "$CHANGED_FILES" ]; then
            BODY="## Cambios\n\n$(echo "$CHANGED_FILES" | sed 's/^/- /')\n\n> PR creado por JARVIS — SDD Auto PR"
        else
            BODY="> PR creado por JARVIS — SDD Auto PR"
        fi
    fi
fi

# Commit if there are pending changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📦 Committing pending changes..."
    git add -A
    git commit -m "$TITLE" --allow-empty 2>/dev/null || true
fi

# Push
echo "📤 Pushing branch: $HEAD"
git push origin "$HEAD" -u 2>&1

# Create PR
echo "🔀 Creating PR..."
PR_OUTPUT=$($GH_BIN pr create \
    --repo "$REMOTE" \
    --title "$TITLE" \
    --body "$BODY" \
    --base "$BASE" \
    --head "$HEAD" 2>&1)

echo "$PR_OUTPUT"

# Extract PR URL
PR_URL=$(echo "$PR_OUTPUT" | grep -oP 'https://github.com/\S+' || true)
if [ -n "$PR_URL" ]; then
    echo ""
    echo "✅ PR creado: $PR_URL"
fi
