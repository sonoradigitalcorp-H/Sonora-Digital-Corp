#!/usr/bin/env bash
# Spec-Kit PR Creation Script
# Creates a PR from the current SDD feature branch
# Usage: ./create-pr.sh [--title "title"] [--body "body"] [--base main]
set -euo pipefail

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Parse args
TITLE=""
BODY=""
BASE="main"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --title) TITLE="$2"; shift 2 ;;
        --body) BODY="$2"; shift 2 ;;
        --base) BASE="$2"; shift 2 ;;
        --help) echo "Usage: $0 [--title 'title'] [--body 'body'] [--base main]"; exit 0 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

# Get feature paths
_paths_output=$(get_feature_paths) || { echo "ERROR: Failed to resolve feature paths" >&2; exit 1; }
eval "$_paths_output"

echo "═══════════════════════════════════════"
echo "  Spec-Kit PR Creation"
echo "═══════════════════════════════════════"
echo "  Branch:     $CURRENT_BRANCH"
echo "  Feature:    $FEATURE_DIR"
echo "  Spec:       $FEATURE_SPEC"
echo "  Base:       $BASE"
echo ""

# Detect gh binary
GH_BIN=""
for p in /usr/bin/gh /home/mystic/.local/bin/gh /snap/bin/gh; do
    [ -x "$p" ] && { GH_BIN="$p"; break; }
done
GH_BIN="${GH_BIN:-gh}"

# Check gh auth
if ! $GH_BIN auth status 2>&1 | grep -q "Logged in"; then
    echo "❌ GitHub CLI not authenticated."
    echo "   Run: gh auth login"
    exit 1
fi

# Get remote
REMOTE=$($GH_BIN repo view --json nameWithOwner 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('nameWithOwner',''))" 2>/dev/null || true)
if [ -z "$REMOTE" ]; then
    echo "❌ No GitHub remote found"
    exit 1
fi

# Build title from spec
if [ -z "$TITLE" ]; then
    if [ -f "$FEATURE_SPEC" ]; then
        TITLE=$(head -20 "$FEATURE_SPEC" | grep -E '^#\s+' | head -1 | sed 's/^# //' | head -c 120 || true)
    fi
    if [ -z "$TITLE" ]; then
        TITLE="feat: $(basename "$FEATURE_DIR")"
    fi
fi

# Build body from spec
if [ -z "$BODY" ] && [ -f "$FEATURE_SPEC" ]; then
    BODY=$(python3 -c "
import re
with open('$FEATURE_SPEC') as f:
    content = f.read()
match = re.search(r'(?:##?\s*(?:Descripción|Descripcion|Description|Objetivo|Purpose).*?)(?=\n##?\s)', content, re.DOTALL)
if match:
    print(match.group(0).strip()[:2000])
else:
    print(content[:2000].strip())
" 2>/dev/null || echo "")
fi

# Append SDD metadata
BODY="${BODY}\n\n---\n> **SDD Feature:** \`$(basename "$FEATURE_DIR")\`\n> **Branch:** \`$CURRENT_BRANCH\`\n> **PR creado por:** Spec-Kit Auto PR"

# Commit any pending changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📦 Committing pending changes..."
    git add -A
    git commit -m "$TITLE" --allow-empty 2>/dev/null || true
fi

# Push branch
echo "📤 Pushing branch: $CURRENT_BRANCH"
git push origin "$CURRENT_BRANCH" -u 2>&1

# Create PR
echo "🔀 Creating PR against $BASE..."
PR_OUTPUT=$($GH_BIN pr create \
    --repo "$REMOTE" \
    --title "$TITLE" \
    --body "$(echo -e "$BODY")" \
    --base "$BASE" \
    --head "$CURRENT_BRANCH" 2>&1)

echo "$PR_OUTPUT"

PR_URL=$(echo "$PR_OUTPUT" | grep -oP 'https://github.com/\S+' || true)
if [ -n "$PR_URL" ]; then
    echo ""
    echo "✅ PR creado exitosamente: $PR_URL"
else
    echo ""
    echo "⚠️  PR output above. If successful, check your GitHub repo."
fi
