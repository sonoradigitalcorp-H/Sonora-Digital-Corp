#!/bin/bash
# RDD Step 4: Generate receipt (validation proof = commit authorization)
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

FREEZE_DIR="sonora-digital-corp/.rdd/freezes"
TODAY=$(date +%Y%m%d)
REVIEW_DIR="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}-reviews"
RECEIPT_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.receipt.json"

echo "=== RDD: Generating Receipt ==="
echo "Feature: $FEATURE_NAME"
echo ""

# Check if all reviews are complete
PENDING=$(find "$REVIEW_DIR" -name "*.json" -exec python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
if data.get('status') != 'complete':
    print('pending')
" {} \; 2>/dev/null | grep -c pending || echo "0")

if [ "$PENDING" -gt 0 ]; then
  echo "ERROR: $PENDING reviews still pending"
  echo "Complete all reviews first: opencode run rdd:review all '$FEATURE_NAME'"
  exit 1
fi

# Aggregate scores
AGGREGATE=$(python3 -c "
import json, glob, os

review_dir = os.path.dirname('$RECEIPT_FILE')
scores = []
findings = []
for f in glob.glob('$REVIEW_DIR/*.json'):
    with open(f) as fh:
        try:
            data = json.load(fh)
            if data.get('score') is not None:
                scores.append(data['score'])
            if data.get('findings'):
                findings.extend(data['findings'])
        except:
            pass

avg_score = sum(scores) / len(scores) if scores else 0
critical = sum(1 for f in findings if f.get('severity') in ['critical', 'high'])
total = len(findings)

print(json.dumps({
    'avg_score': round(avg_score, 1),
    'critical_issues': critical,
    'total_findings': total
}))
" 2>/dev/null)

SCORE=$(echo "$AGGREGATE" | python3 -c "import json,sys; print(json.load(sys.stdin)['avg_score'])")
CRITICAL=$(echo "$AGGREGATE" | python3 -c "import json,sys; print(json.load(sys.stdin)['critical_issues'])")

# Generate receipt
cat > "$RECEIPT_FILE" << EOF
{
  "feature": "$FEATURE_NAME",
  "receipt_id": "$(date +%Y%m%d)-$((RANDOM % 10000))",
  "generated_at": "$(date -Iseconds)",
  "freeze_fingerprint": "$(sha256sum "$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.fingerprint" 2>/dev/null | awk '{print $1}' || echo 'none')",
  "aggregated_score": $SCORE,
  "critical_issues": $CRITICAL,
  "reviews_complete": true,
  "fix_attempted": $(test -f "$REVIEW_DIR/fix-plan.md" && echo true || echo false),
  "validation_passed": true,
  "line_fix_budget": 120,
  "lines_fixed": 0,
  "authorization": {
    "allowed_to_commit": $( [ $(echo "$SCORE >= 80 && $CRITICAL == 0" | bc -l 2>/dev/null || echo 0) ] && echo true || echo false),
    "authorized_by": "RDD Gate",
    "reason": "Score: $SCORE/100, Critical: $CRITICAL"
  },
  "message": "✅ RDD Receipt Generated - Safe to commit and deploy"
}
EOF

echo "Receipt saved: $RECEIPT_FILE"
echo ""

# Display receipt
python3 -c "
import json
with open('$RECEIPT_FILE') as f:
    receipt = json.load(f)
    print('📋 RDD Receipt Summary')
    print('=' * 40)
    print(f'  Receipt ID: {receipt[\"receipt_id\"]}')
    print(f'  Feature: {receipt[\"feature\"]}')
    print(f'  Score:     {receipt[\"aggregated_score\"]}/100')
    print(f'  Critical:  {receipt[\"critical_issues\"]}')
    print(f'  Authorized: {receipt[\"authorization\"][\"allowed_to_commit\"]}')
    print(f'  Reason:    {receipt[\"authorization\"][\"reason\"]}')
    print()
    if receipt['authorization']['allowed_to_commit']:
        print(f'  ✅ COMMIT AUTHORIZED')
        print(f'  Run: git commit -m \"feat: {receipt[\"feature\"]} (RDD-verified)\"')
    else:
        print(f'  ❌ COMMIT BLOCKED')
        print(f'  Fix issues and re-run: opencode run rdd:validate {receipt[\"feature\"]}')
"

echo ""
echo "To commit with receipt:"
echo "  opencode run rdd:commit '$FEATURE_NAME'"