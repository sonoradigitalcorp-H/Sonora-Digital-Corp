#!/usr/bin/env bash
set -euo pipefail

# implementador.sh — Autonomous implementation agent.
#
# Triggered by GitHub Actions when an Issue gets label "approved".
# Reads the Issue content, finds the corresponding spec,
# implements with OpenCode, and opens a PR.
#
# Usage:
#   export GITHUB_TOKEN=...
#   export ISSUE_NUMBER=42
#   bash scripts/implementador.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

GITHUB_TOKEN="${GITHUB_TOKEN:?GITHUB_TOKEN required}"
ISSUE_NUMBER="${ISSUE_NUMBER:?ISSUE_NUMBER required}"
REPO="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY required}"

echo "🔧 implementador.sh — processing Issue #$ISSUE_NUMBER"

# Step 1: Get issue details
ISSUE_JSON=$(gh api "repos/$REPO/issues/$ISSUE_NUMBER")
ISSUE_TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
ISSUE_BODY=$(echo "$ISSUE_JSON" | jq -r '.body')
ISSUE_AUTHOR=$(echo "$ISSUE_JSON" | jq -r '.user.login')

echo "  Issue: $ISSUE_TITLE (by @$ISSUE_AUTHOR)"

# Step 2: Extract spec path from issue body or labels
SPEC_PATH=$(echo "$ISSUE_BODY" | grep -oP 'specs/\S+' | head -1 || echo "")
if [ -z "$SPEC_PATH" ]; then
  # Try to find spec from issue number reference
  SPEC_PATH=$(find specs/ -name "spec.md" -path "*/$ISSUE_NUMBER*" 2>/dev/null | head -1 || echo "")
fi

if [ -z "$SPEC_PATH" ]; then
  # Fall back: find the newest unlinked spec
  SPEC_PATH=$(find specs/ -name "spec.md" | sort | head -1)
fi

if [ -z "$SPEC_PATH" ] || [ ! -f "$SPEC_PATH" ]; then
  echo "❌ No spec found. Issue body must reference a spec path."
  echo "   Format: specs/<n>-<name>/spec.md"
  exit 1
fi

echo "  Spec: $SPEC_PATH"

# Step 3: Create branch
BRANCH_NAME="impl/$(basename "$(dirname "$SPEC_PATH")")-$(date +%s)"
git checkout -b "$BRANCH_NAME"
echo "  Branch: $BRANCH_NAME"

# Step 4: Run OpenCode implementation
# OpenCode reads the spec and implements it
echo "  Running OpenCode..."
opencode --yes 2>&1 <<EOF
Read the spec at $SPEC_PATH.
Implement according to the spec and its acceptance criteria.
Create necessary test files in tests/.
Make sure all tests pass.
Do not modify files outside the scope of the spec.
EOF

# Step 5: Commit and push
git add -A
git commit -m "[impl] $ISSUE_TITLE

Implements spec: $SPEC_PATH
Closes #$ISSUE_NUMBER

By: implementador.sh (triggered by Issue #$ISSUE_NUMBER)"
git push origin "$BRANCH_NAME"

# Step 6: Open PR
PR_URL=$(gh pr create \
  --base main \
  --head "$BRANCH_NAME" \
  --title "[feat] $ISSUE_TITLE" \
  --body "## Implementation

Closes #$ISSUE_NUMBER

**Spec**: $SPEC_PATH

**Author**: @$ISSUE_AUTHOR

### Quality Gates
- [ ] All tests pass
- [ ] Coverage ≥ 80%
- [ ] Lint passes
- [ ] 4R review (Risk, Readability, Reliability, Resilience)
- [ ] PR approved

---

_🤖 Automated PR by implementador.sh_")

echo "✅ PR created: $PR_URL"
