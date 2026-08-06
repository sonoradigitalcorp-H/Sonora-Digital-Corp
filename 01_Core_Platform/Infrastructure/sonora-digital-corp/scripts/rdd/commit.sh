#!/bin/bash
# RDD Step 6: Commit with RDD gate (authorization required unless kill switch)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name> [git-args...]"
  exit 1
fi
shift

FREEZE_DIR="$RDD_FREEZE_DIR"
TODAY=$(date +%Y%m%d)

# Gate check (respect kill switch)
if rdd_gate_enabled; then
  if ! rdd_require_gate "$FEATURE_NAME"; then
    echo "❌ Commit blocked by RDD gate."
    exit 1
  fi
else
  echo "⚠  Kill switch active — bypassing gate (document emergency)."
fi

RECEIPT_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.receipt.json"
RECEIPT_ID=$(python3 -c "import json;print(json.load(open('$RECEIPT_FILE')).get('receipt_id','unknown'))" 2>/dev/null || echo "unknown")

cd "$RDD_ROOT"
git add -A
git commit -m "$FEATURE_NAME (RDD:${RECEIPT_ID})" "$@"
echo "✅ Commit done with RDD receipt: $RECEIPT_ID"
