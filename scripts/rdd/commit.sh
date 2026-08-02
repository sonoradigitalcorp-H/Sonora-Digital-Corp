#!/bin/bash
# RDD: Commit with receipt validation
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

FREEZE_DIR="sonora-digital-corp/.rdd/freezes"
TODAY=$(date +%Y%m%d)
RECEIPT_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.receipt.json"

echo "=== RDD: Commit with Receipt ==="
echo "Feature: $FEATURE_NAME"
echo ""

if [ ! -f "$RECEIPT_FILE" ]; then
  echo "ERROR: No receipt found"
  echo "Generate receipt first: opencode run rdd:receipt '$FEATURE_NAME'"
  exit 1
fi

# Check receipt authorization
AUTHORIZED=$(python3 -c "
import json
with open('$RECEIPT_FILE') as f:
    r = json.load(f)
print(r['authorization']['allowed_to_commit'])
" 2>/dev/null)

if [ "$AUTHORIZED" != "True" ]; then
  echo "ERROR: Receipt does not authorize commit"
  echo "Reason: $(python3 -c "import json; print(json.load(open('$RECEIPT_FILE'))['authorization']['reason'])" 2>/dev/null)"
  echo "Fix issues and re-run: opencode run rdd:receipt '$FEATURE_NAME'"
  exit 1
fi

# Commit with receipt hash embedded in message
RECEIPT_HASH=$(python3 -c "
import json
with open('$RECEIPT_FILE') as f:
    r = json.load(f)
print(r['receipt_id'])
" 2>/dev/null)

echo "Receipt: $RECEIPT_HASH"
echo "Authorization: GRANTED"
echo ""

cd "sonora-digital-corp"
git add -A
git commit -m "feat: $FEATURE_NAME (RDD-${RECEIPT_HASH})" --allow-empty

echo ""
echo "✅ Commit created with RDD receipt"
echo "   git log --oneline -1"
git -C "sonora-digital-corp" log --oneline -1