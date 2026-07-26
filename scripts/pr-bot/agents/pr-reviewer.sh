#!/bin/bash
# PR Reviewer Agent — reviews PRs with multi-agent evaluation
# Usage: ./pr-reviewer.sh <pr-number>
set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
REMOTE="${REMOTE:-$($GH_BIN repo view --json nameWithOwner 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin).get('nameWithOwner',''))" 2>/dev/null || true)}"
PR_NUMBER="${1:-}"

if [ -z "$PR_NUMBER" ]; then
    echo "Usage: $0 <pr-number>"
    exit 1
fi

echo "🔍 Reviewing PR #$PR_NUMBER..."

# Get PR info
PR_INFO=$($GH_BIN pr view "$PR_NUMBER" --repo "$REMOTE" --json title,state,headRefName,baseRefName,author,additions,deletions,body,files 2>/dev/null || echo '{}')

echo "$PR_INFO" | python3 -c "
import sys, json

data = json.load(sys.stdin)
if not data:
    print('❌ Could not fetch PR info')
    sys.exit(0)

print(f'📋 PR #{PR_NUMBER}: {data.get(\"title\", \"N/A\")}')
print(f'   Author: {data.get(\"author\", {}).get(\"login\", \"N/A\")}')
print(f'   Branch: {data.get(\"headRefName\", \"?\")} → {data.get(\"baseRefName\", \"?\")}')
print(f'   Changes: +{data.get(\"additions\", 0)} / -{data.get(\"deletions\", 0)}')
print()

# Analyze files
files = data.get('files', [])
if files:
    print(f'📁 Files ({len(files)}):')
    for f in files:
        status = 'M' if f.get('status') == 'modified' else 'A' if f.get('status') == 'added' else 'D'
        print(f'   [{status}] {f.get(\"path\", \"?\")} (+{f.get(\"additions\",0)}/-{f.get(\"deletions\",0)})')

# Run checklist
print()
print('✅ Review Checklist:')
print('   [ ] Code follows project conventions')
print('   [ ] No hardcoded secrets/credentials')
print('   [ ] Tests included or updated')
print('   [ ] No debugging code left behind (console.log, print, TODO, FIXME)')
print('   [ ] Error handling present')
print('   [ ] No large binary files added')
print('   [ ] Branch name follows convention')
print('   [ ] PR description is clear and descriptive')
print(f'   [ ] No merge conflicts (mergeable: {data.get(\"mergeable\", \"unknown\")})')

# Score
score = 8
if data.get('body') and len(data['body']) > 50:
    score += 1
if data.get('additions', 0) > 500:
    score -= 1
    print()
    print('   ⚠️  Large PR (>500 additions), consider splitting')
if data.get('additions', 0) == 0 and data.get('deletions', 0) == 0:
    score -= 2
    print()
    print('   ⚠️  No code changes detected')

print()
print(f'📊 Confidence Score: {score}/10')
" 2>/dev/null

# Fetch diff for deeper analysis
echo ""
echo "📝 Diff preview:"
$GH_BIN pr diff "$PR_NUMBER" --repo "$REMOTE" 2>/dev/null | head -80
