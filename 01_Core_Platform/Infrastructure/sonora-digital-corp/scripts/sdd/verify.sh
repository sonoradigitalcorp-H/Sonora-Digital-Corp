#!/bin/bash
# SDD: Verify implementation against specification
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

SPEC_FILE="sonora-digital-corp/docs/specs/${FEATURE_NAME}.md"
if [ ! -f "$SPEC_FILE" ]; then
  echo "Specification not found: $SPEC_FILE"
  exit 1
fi

echo "Verifying implementation against spec: $SPEC_FILE"
echo ""
echo "Running verification checks..."

# Run tests
echo "=== Unit Tests ==="
cd sonora-digital-corp && python -m pytest tests/unit -k "$FEATURE_NAME" -v || true

echo "=== Integration Tests ==="
cd sonora-digital-corp && python -m pytest tests/integration -k "$FEATURE_NAME" -v || true

echo "=== E2E Tests ==="
cd sonora-digital-corp && python -m pytest tests/e2e -k "$FEATURE_NAME" -v || true

echo "=== Quality Gates ==="
bash scripts/quality-gate.sh

echo ""
echo "Verification complete. Check test results above."