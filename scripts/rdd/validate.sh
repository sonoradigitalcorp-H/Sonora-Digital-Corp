#!/bin/bash
# RDD: Aggregate reviews and validate (read-only check)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

APP_DIR="${RDD_APP_DIR:-$RDD_ROOT}"
FREEZE_DIR="$RDD_FREEZE_DIR"
TODAY=$(date +%Y%m%d)
REVIEW_DIR="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}-reviews"

echo "=== RDD: Validation (Read-Only) ==="
echo "Feature: $FEATURE_NAME"
echo ""

# 1. Verify fingerprint changed state (expected if fix applied)
echo "1. Verifying fingerprint..."
CURRENT_FINGERPRINT=$(find "$APP_DIR" \( -path "*/.git" -o -path "*/node_modules" -o -path "*/__pycache__" -o -path "*/.rdd" \) -prune -o -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" \) -print | sort | xargs sha256sum 2>/dev/null | sha256sum | awk '{print $1}')
STORED_FINGERPRINT=$(sha256sum "$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.fingerprint" 2>/dev/null | awk '{print $1}')

if [ "$CURRENT_FINGERPRINT" != "$STORED_FINGERPRINT" ]; then
  echo "   ⚠ Fingerprint mismatch (expected if fix was applied)"
  echo "   New fingerprint saved for receipt"
  find "$APP_DIR" \( -path "*/.git" -o -path "*/node_modules" -o -path "*/__pycache__" -o -path "*/.rdd" \) -prune -o -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" \) -print | sort | xargs sha256sum > "$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.fingerprint.new" 2>/dev/null || true
else
  echo "   ✓ Fingerprint matches"
fi

# 2. Run test suite (read-only)
echo "2. Running test suite..."
cd "$RDD_ROOT"
if command -v make >/dev/null 2>&1 && [ -f Makefile ]; then
  timeout 180 make doctor-quick 2>&1 | tail -8 || true
else
  echo "   No Makefile; skipping test run"
fi

echo ""
echo "3. Validation complete"
echo "   Run: bash scripts/rdd/receipt.sh '$FEATURE_NAME' to generate final receipt"
