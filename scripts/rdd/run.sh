#!/bin/bash
# RDD: Full workflow - Freeze, Review, Fix, Validate, Receipt, Commit
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name> [action]"
  echo "Actions: freeze, review, fix, validate, receipt, commit"
  echo "Default: run full workflow"
  exit 1
fi

ACTION="${2:-full}"

case $ACTION in
  freeze)
    bash scripts/rdd/freeze.sh "$FEATURE_NAME"
    ;;
  review)
    bash scripts/rdd/review.sh all "$FEATURE_NAME"
    ;;
  fix)
    bash scripts/rdd/fix.sh "$FEATURE_NAME"
    ;;
  validate)
    bash scripts/rdd/validate.sh "$FEATURE_NAME"
    ;;
  receipt)
    bash scripts/rdd/receipt.sh "$FEATURE_NAME"
    ;;
  commit)
    bash scripts/rdd/commit.sh "$FEATURE_NAME"
    ;;
  full)
    echo "=== RDD Full Workflow ==="
    echo "Feature: $FEATURE_NAME"
    echo ""
    
    echo "Step 1: FREEZE"
    bash scripts/rdd/freeze.sh "$FEATURE_NAME"
    echo ""
    
    echo "Step 2: REVIEW (4 parallel lenses)"
    bash scripts/rdd/review.sh all "$FEATURE_NAME"
    echo ""
    
    echo "Step 3: FIX (bounded)"
    bash scripts/rdd/fix.sh "$FEATURE_NAME"
    echo ""
    
    echo "Step 4: VALIDATE"
    bash scripts/rdd/validate.sh "$FEATURE_NAME"
    echo ""
    
    echo "Step 5: RECEIPT"
    bash scripts/rdd/receipt.sh "$FEATURE_NAME"
    echo ""
    
    echo "Step 6: COMMIT"
    bash scripts/rdd/commit.sh "$FEATURE_NAME"
    echo ""
    
    echo "✅ RDD Complete for $FEATURE_NAME"
    ;;
  *)
    echo "Unknown action: $ACTION"
    exit 1
    ;;
esac