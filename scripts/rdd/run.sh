#!/bin/bash
# RDD: Full workflow - Freeze, Review, Fix, Validate, Receipt, Commit
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name> [action]"
  echo "Actions: freeze, review, fix, validate, receipt, commit"
  echo "Default: run full workflow"
  exit 1
fi

ACTION="${2:-full}"

case $ACTION in
  freeze)   bash "$SCRIPT_DIR/freeze.sh" "$FEATURE_NAME" ;;
  review)   bash "$SCRIPT_DIR/review.sh" all "$FEATURE_NAME" ;;
  fix)      bash "$SCRIPT_DIR/fix.sh" "$FEATURE_NAME" ;;
  validate) bash "$SCRIPT_DIR/validate.sh" "$FEATURE_NAME" ;;
  receipt)  bash "$SCRIPT_DIR/receipt.sh" "$FEATURE_NAME" ;;
  commit)   bash "$SCRIPT_DIR/commit.sh" "$FEATURE_NAME" ;;
  gate)     rdd_require_gate "$FEATURE_NAME" ;;
  full)
    echo "=== RDD Full Workflow ==="
    echo "Feature: $FEATURE_NAME"
    echo "Step 1: FREEZE";   bash "$SCRIPT_DIR/freeze.sh" "$FEATURE_NAME"
    echo "Step 2: REVIEW";   bash "$SCRIPT_DIR/review.sh" all "$FEATURE_NAME"
    echo "Step 3: FIX";      bash "$SCRIPT_DIR/fix.sh" "$FEATURE_NAME"
    echo "Step 4: VALIDATE"; bash "$SCRIPT_DIR/validate.sh" "$FEATURE_NAME"
    echo "Step 5: RECEIPT";  bash "$SCRIPT_DIR/receipt.sh" "$FEATURE_NAME"
    echo "Step 6: COMMIT";   bash "$SCRIPT_DIR/commit.sh" "$FEATURE_NAME"
    echo "✅ RDD Complete for $FEATURE_NAME"
    ;;
  *) echo "Unknown action: $ACTION"; exit 1 ;;
esac
