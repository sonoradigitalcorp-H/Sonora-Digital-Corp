#!/bin/bash
# RDD (Receipt Driven Development) - Step 1: Freeze candidate with fingerprint
set -e

FEATURE_NAME="${1:-}"
if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name>"
  exit 1
fi

APP_DIR="${2:-sonora-digital-corp/apps/frontends/agentic-os}"
FREEZE_DIR="sonora-digital-corp/.rdd/freezes"
TODAY=$(date +%Y%m%d)
FREEZE_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}"

mkdir -p "$FREEZE_DIR"

echo "=== RDD: Freezing candidate ==="
echo "Feature: $FEATURE_NAME"
echo "App Dir: $APP_DIR"
echo ""

# 1. Create fingerprint (hash of all source files)
echo "1. Generating fingerprint..."
FINGERPRINT_FILE="$FREEZE_FILE.fingerprint"

# Hash all TypeScript/TSX files in the app
find "$APP_DIR/src" -name "*.ts" -o -name "*.tsx" | sort | xargs sha256sum > "$FINGERPRINT_FILE"

# Also hash package.json and key configs
echo "# Package manifest" >> "$FINGERPRINT_FILE"
sha256sum "$APP_DIR/package.json" >> "$FINGERPRINT_FILE" 2>/dev/null || true
sha256sum "$APP_DIR/vite.config.ts" >> "$FINGERPRINT_FILE" 2>/dev/null || true

echo "   Fingerprint saved: $FINGERPRINT_FILE"
echo "   Files hashed: $(wc -l < "$FINGERPRINT_FILE")"

# 2. Save git diff as the candidate
echo "2. Saving candidate diff..."
CANDIDATE_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.candidate.patch"
git -C "sonora-digital-corp" diff > "$CANDIDATE_FILE" 2>/dev/null || echo "No changes to diff" > "$CANDIDATE_FILE"
echo "   Candidate saved: $CANDIDATE_FILE"

# 3. Create manifest
echo "3. Creating manifest..."
MANIFEST_FILE="$FREEZE_FILE.manifest.json"
cat > "$MANIFEST_FILE" << EOF
{
  "feature": "$FEATURE_NAME",
  "fingerprint": "$(sha256sum "$FINGERPRINT_FILE" | awk '{print $1}')",
  "candidate_patch": "$CANDIDATE_FILE",
  "files_changed": $(find "$APP_DIR/src" -name "*.ts" -o -name "*.tsx" -newer "$FREEZE_DIR" | wc -l),
  "created_at": "$(date -Iseconds)",
  "status": "frozen",
  "reviews": [],
  "receipt": null
}
EOF
echo "   Manifest saved: $MANIFEST_FILE"

# 4. Initialize review status
echo "4. Initializing reviews..."
REVIEW_DIR="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}-reviews"
mkdir -p "$REVIEW_DIR"

cat > "$REVIEW_DIR/.status.json" << EOF
{
  "reviewers": {
    "sdd-engineer": {"status": "pending", "score": null, "report": null},
    "test-engineer": {"status": "pending", "score": null, "report": null},
    "frontend-architect": {"status": "pending", "score": null, "report": null},
    "backend-architect": {"status": "pending", "score": null, "report": null}
  },
  "aggregated_score": null,
  "passed": null,
  "fix_required": false
}
EOF

echo ""
echo "5. Frozen! Run reviews in parallel:"
echo "   opencode run rdd:review all '${FEATURE_NAME}'"
echo "   opencode run rdd:review sdd-engineer '${FEATURE_NAME}'"
echo "   opencode run rdd:review test-engineer '${FEATURE_NAME}'"
echo "   opencode run rdd:review frontend-architect '${FEATURE_NAME}'"
echo "   opencode run rdd:review backend-architect '${FEATURE_NAME}'"