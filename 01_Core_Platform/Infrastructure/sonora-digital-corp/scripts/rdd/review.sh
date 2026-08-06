#!/bin/bash
# RDD Step 2: Review with 4 parallel lenses
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

REVIEWER="${1:-}"
FEATURE_NAME="${2:-}"
if [ -z "$REVIEWER" ] || [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <reviewer-name> <feature-name>"
  echo "Reviewers: sdd-engineer, test-engineer, frontend-architect, backend-architect, all"
  exit 1
fi

FREEZE_DIR="$RDD_FREEZE_DIR"
TODAY=$(date +%Y%m%d)
REVIEW_DIR="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}-reviews"

# Get the agent prompt based on reviewer type
case $REVIEWER in
  sdd-engineer)
    AGENT="sdd-engineer"
    PROMPT="You are an SDD specification expert reviewing code changes. Check if the implementation matches the spec, requirements are met, API contracts are correct, edge cases are handled. Score 0-100. Focus: specification compliance."
    ;;
  test-engineer)
    AGENT="test-engineer"
    PROMPT="You are a test engineering expert reviewing code changes. Check test coverage, test quality, edge cases, unit/integration/e2e test adequacy. Score 0-100. Focus: testing quality."
    ;;
  frontend-architect)
    AGENT="frontend-architect"
    PROMPT="You are a frontend architect reviewing code changes. Check patterns, component design, state management, accessibility. Score 0-100. Focus: frontend quality."
    ;;
  backend-architect)
    AGENT="backend-architect"
    PROMPT="You are a backend architect reviewing code changes. Check API design, data flow, error handling, security, scalability. Score 0-100. Focus: backend quality."
    ;;
  all)
    echo "Running all 4 reviews in parallel..."
    bash "$SCRIPT_DIR/review.sh" sdd-engineer "$FEATURE_NAME" &
    bash "$SCRIPT_DIR/review.sh" test-engineer "$FEATURE_NAME" &
    bash "$SCRIPT_DIR/review.sh" frontend-architect "$FEATURE_NAME" &
    bash "$SCRIPT_DIR/review.sh" backend-architect "$FEATURE_NAME" &
    wait
    echo "All reviews complete. Run: bash scripts/rdd/receipt.sh '$FEATURE_NAME'"
    exit 0
    ;;
  *)
    echo "Unknown reviewer: $REVIEWER"
    exit 1
    ;;
esac

echo "=== RDD Review: $REVIEWER ==="
echo "Feature: $FEATURE_NAME"
echo ""

# Create review report
REPORT_FILE="$REVIEW_DIR/${REVIEWER}.json"
mkdir -p "$REVIEW_DIR"

# Run as subagent via opencode if available; else record with given score
SCORE="${3:-}"
FINDINGS_JSON="${4:-[]}"

if [ -n "$SCORE" ]; then
  cat > "$REPORT_FILE" << EOF
{
  "reviewer": "$REVIEWER",
  "feature": "$FEATURE_NAME",
  "timestamp": "$(date -Iseconds)",
  "score": $SCORE,
  "findings": $FINDINGS_JSON,
  "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
  "status": "complete"
}
EOF
  echo "Review recorded: $REVIEWER score=$SCORE"
else
  cat > "$REPORT_FILE" << EOF
{
  "reviewer": "$REVIEWER",
  "feature": "$FEATURE_NAME",
  "timestamp": "$(date -Iseconds)",
  "score": null,
  "findings": [],
  "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
  "status": "pending"
}
EOF
  echo "Reviews dir initialized: $REVIEW_DIR"
  echo "Submit scores: bash scripts/rdd/review.sh $REVIEWER '$FEATURE_NAME' <score> '<findings-json>'"
fi
