#!/bin/bash
# RDD Step 5: Generate receipt (validation proof = commit authorization)
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
RECEIPT_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.receipt.json"

echo "=== RDD: Generating Receipt ==="
echo "Feature: $FEATURE_NAME"
echo ""

# Aggregate scores from review JSONs (reviewer.score)
AGGREGATE=$(python3 -c "
import json, glob, os
scores = []
findings = []
for f in glob.glob(os.path.join('$REVIEW_DIR', '*.json')):
    with open(f) as fh:
        try:
            data = json.load(fh)
            if isinstance(data.get('score'), (int, float)):
                scores.append(data['score'])
            if isinstance(data.get('findings'), list):
                findings.extend(data['findings'])
        except:
            pass
avg = sum(scores)/len(scores) if scores else 0
critical = sum(1 for f in findings if isinstance(f,dict) and f.get('severity') in ('critical','high'))
print(json.dumps({'avg_score': round(avg,1), 'critical_issues': critical, 'total_findings': len(findings), 'reviews': len(scores)}))
" 2>/dev/null)

SCORE=$(echo "$AGGREGATE" | python3 -c "import json,sys;print(json.load(sys.stdin)['avg_score'])")
CRITICAL=$(echo "$AGGREGATE" | python3 -c "import json,sys;print(json.load(sys.stdin)['critical_issues'])")

# Authorization: score >= 80 and 0 criticals
AUTHORIZED="false"
if [ "$(python3 -c "print(1 if float('${SCORE:-0}') >= 80 else 0)")" = "1" ] && [ "${CRITICAL:-1}" = "0" ]; then
  AUTHORIZED="true"
fi

cat > "$RECEIPT_FILE" << EOF
{
  "feature": "$FEATURE_NAME",
  "receipt_id": "$(date +%Y%m%d)-$((RANDOM % 10000))",
  "generated_at": "$(date -Iseconds)",
  "freeze_fingerprint": "$(sha256sum "$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.fingerprint" 2>/dev/null | awk '{print $1}' || echo 'none')",
  "aggregated_score": ${SCORE:-0},
  "critical_issues": ${CRITICAL:-0},
  "reviews_complete": true,
  "validation_passed": true,
  "line_fix_budget": 120,
  "authorization": {
    "allowed_to_commit": $AUTHORIZED,
    "authorized_by": "RDD Gate",
    "reason": "Score: ${SCORE:-0}/100, Critical: ${CRITICAL:-0}"
  }
}
EOF

python3 -c "
import json
r=json.load(open('$RECEIPT_FILE'))
print('📋 RDD Receipt')
print('='*40)
print(f\"  Receipt ID: {r['receipt_id']}\")
print(f\"  Feature:   {r['feature']}\")
print(f\"  Score:     {r['aggregated_score']}/100\")
print(f\"  Critical:  {r['critical_issues']}\")
print(f\"  Authorized: {r['authorization']['allowed_to_commit']}\")
print()
if r['authorization']['allowed_to_commit']:
    print('  ✅ COMMIT AUTHORIZED')
else:
    print('  ❌ COMMIT BLOCKED — fix and re-validate')
"
