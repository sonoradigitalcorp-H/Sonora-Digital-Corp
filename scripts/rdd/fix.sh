#!/bin/bash
# RDD Step 3: Bounded fix (max 120 lines changed, single attempt)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

FREEZE_DIR="$RDD_FREEZE_DIR"
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
        severity = data.get('severity', {}) if isinstance(data.get('severity'), dict) else {}
        critical += severity.get('critical', 0) + severity.get('high', 0)
    except:
        pass
print(critical)
" 2>/dev/null || echo "0")

echo "=== RDD: Bounded Fix ==="
echo "Feature: $FEATURE_NAME"
echo "Total findings: $TOTAL_FINDINGS"
echo "Critical/High findings: $CRITICAL"
echo ""

if [ "${CRITICAL:-0}" -eq 0 ] && [ "${TOTAL_FINDINGS:-0}" -eq 0 ]; then
  echo "No issues found. Proceed to receipt generation."
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
            if isinstance(data.get('findings'), list) and data['findings']:
                print(f'## {data.get(\"reviewer\", \"unknown\")}')
                for finding in data['findings'][:5]:
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
EOF

echo "Fix plan saved: $FIX_PLAN_FILE"
echo "Execute the bounded fix (single agent, 120-line limit), then: bash scripts/rdd/validate.sh '$FEATURE_NAME'"
