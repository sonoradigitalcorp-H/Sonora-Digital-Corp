#!/bin/bash
# SDD: Implement from specification
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

SPEC_FILE="sonora-digital-corp/docs/specs/${FEATURE_NAME}.md"
if [ ! -f "$SPEC_FILE" ]; then
  echo "Specification not found: $SPEC_FILE"
  echo "Run: opencode run sdd:spec $FEATURE_NAME"
  exit 1
fi

echo "Implementing from spec: $SPEC_FILE"
echo "This will create:"
echo "  - Backend API in sonora-digital-corp/apps/core/"
echo "  - Frontend components in sonora-digital-corp/apps/frontends/"
echo "  - Tests in sonora-digital-corp/tests/"
echo ""
echo "Run the implementation agent:"
echo "  opencode agent sdd-engineer \"Implement $FEATURE_NAME from spec at $SPEC_FILE\""