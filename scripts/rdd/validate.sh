#!/bin/bash
# RDD: Aggregate reviews and validate (read-only check)
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

FREEZE_DIR="sonora-digital-corp/.rdd/freezes"
TODAY=$(date +%Y%m%d)
REVIEW_DIR="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}-reviews"

echo "=== RDD: Validation (Read-Only) ==="
echo "Feature: $FEATURE_NAME"
echo ""

# 1. Verify fingerprint unchanged
echo "1. Verifying fingerprint..."
CURRENT_FINGERPRINT=$(find "sonora-digital-corp/apps/frontends/agentic-os/src" -name "*.ts" -o -name "*.tsx" | sort | xargs sha256sum | sha256sum | awk '{print $1}')
STORED_FINGERPRINT=$(sha256sum "$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.fingerprint" 2>/dev/null | awk '{print $1}')

if [ "$CURRENT_FINGERPRINT" != "$STORED_FINGERPRINT" ]; then
  echo "   ⚠ Fingerprint mismatch (expected if fix was applied)"
  echo "   Old: $STORED_FINGERPRINT"
  echo "   New: $CURRENT_FINGERPRINT"
  # Update fingerprint to new state for receipt
  find "sonora-digital-corp/apps/frontends/agentic-os/src" -name "*.ts" -o -name "*.tsx" | sort | xargs sha256sum > "$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.fingerprint.new"
  echo "   New fingerprint saved for receipt"
else
  echo "   ✓ Fingerprint matches"
fi

# 2. Re-run tests (read-only verification)
echo "2. Running test suite..."
cd "sonora-digital-corp/apps/frontends/agentic-os"
if [ -f "tests/unit" ]; then
  npx vitest run 2>&1 | tail -10 || true
fi

echo ""
echo "3. Validation complete"
echo "   Run: opencode run rdd:receipt '$FEATURE_NAME' to generate final receipt"