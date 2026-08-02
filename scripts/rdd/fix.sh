#!/bin/bash
# RDD Step 3: Bounded fix (max 120 lines changed, single attempt)
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

FREEZE_DIR="sonora-digital-corp/.rdd/freezes"
TODAY=$(date +%Y%m%d)
REVIEW_DIR="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}-reviews"

# Count total findings from all reviewers
TOTAL_FINDINGS=$(cd "$REVIEW_DIR" && cat *.json 2>/dev/null | python3 -c "
import json, sys
findings = []
for line in sys.stdin:
    try:
        data = json.loads(line)
        if 'findings' in data:
            findings.extend(data['findings'])
    except:
        pass
print(len(findings))
" 2>/dev/null || echo "0")

# Count critical/high
CRITICAL=$(cat "$REVIEW_DIR"/*.json 2>/dev/null | python3 -c "
import json, sys
critical = 0
for line in sys.stdin:
    try:
        data = json.loads(line)
        if 'severity' in data:
            critical += data['severity'].get('critical', 0) + data['severity'].get('high', 0)
    except:
        pass
print(critical)
" 2>/dev/null || echo "0")

echo "=== RDD: Bounded Fix ==="
echo "Feature: $FEATURE_NAME"
echo "Total findings: $TOTAL_FINDINGS"
echo "Critical/High findings: $CRITICAL"
echo ""

if [ "$CRITICAL" -eq 0 ] && [ "$TOTAL_FINDINGS" -eq 0 ]; then
  echo "No issues found. Proceed to receipt generation."
  echo "Run: opencode run rdd:receipt '$FEATURE_NAME'"
  exit 0
fi

# Generate the fix prompt (bounded to 120 lines)
echo "4. Generating bounded fix plan (max 120 lines)..."
FIX_PLAN_FILE="$REVIEW_DIR/fix-plan.md"

cat > "$FIX_PLAN_FILE" << EOF
# RDD Fix Plan: $FEATURE_NAME

## Issues to Fix ($TOTAL_FINDINGS total, $CRITICAL critical/high)

EOF

# Append findings from all reviews
python3 -c "
import json, glob, os
review_dir = os.path.dirname('$FIX_PLAN_FILE')
for f in glob.glob(os.path.join(review_dir, '*.json')):
    with open(f) as fh:
        try:
            data = json.load(fh)
            if 'findings' in data and data['findings']:
                print(f'## {data[\"reviewer\"]}')
                for finding in data['findings'][:5]:  # Max 5 per reviewer
                    print(f'- [{finding.get(\"severity\", \"medium\")}] {finding.get(\"message\", finding)}')
                print()
        except:
            pass
" >> "$FIX_PLAN_FILE"

cat >> "$FIX_PLAN_FILE" << EOF

## Fix Constraints
- **Single attempt only** - no iterative fixes
- **120 line maximum** - total diff across all files
- **Read-only validation** - must not break existing functionality

## Fix Plan (auto-generated)

The fix must address all critical/high findings while staying within the 120-line limit.

**Approach:**
1. Critical findings first (max 60 lines)
2. High findings (max 40 lines)
3. Medium/Low only if space allows (max 20 lines)

**Execution:**
Use an LLM agent with this prompt:
"You are a focused code fixer. Fix the issues in \$FIX_PLAN_FILE.
Make ONE edit pass. Maximum 120 lines changed across all files.
No new features, no refactoring beyond fixes.
After fixing, run: opencode run rdd:validate $FEATURE_NAME"
EOF

echo "Fix plan saved: $FIX_PLAN_FILE"
echo ""
echo "5. Execute bounded fix (single agent, 120-line limit)"
echo "   Run: opencode agent sdd-engineer \"Fix $FEATURE_NAME per \$REVIEW_DIR/fix-plan.md. ONE pass only. 120 line limit. No new features.\""
echo ""
echo "6. After fix: opencode run rdd:validate '$FEATURE_NAME'"