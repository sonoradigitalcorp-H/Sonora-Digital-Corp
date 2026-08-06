#!/bin/bash
# RDD (Receipt Driven Development) - Step 1: Freeze candidate with fingerprint
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
FREEZE_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}"

mkdir -p "$FREEZE_DIR"

echo "=== RDD: Freezing candidate ==="
echo "Feature: $FEATURE_NAME"
echo "Repo Root: $RDD_ROOT"
echo "App Dir: $APP_DIR"
echo ""

# 1. Create fingerprint (hash of source + config files)
echo "1. Generating fingerprint..."
FINGERPRINT_FILE="$FREEZE_FILE.fingerprint"

# Hash source files under RDD_APP_DIR
find "$APP_DIR" \( -path "*/.git" -o -path "*/node_modules" -o -path "*/__pycache__" -o -path "*/.rdd" \) -prune -o -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" -o -name "*.yml" \) -print | sort | xargs sha256sum > "$FINGERPRINT_FILE" 2>/dev/null || true

# Also hash key configs
echo "# Package manifest" >> "$FINGERPRINT_FILE"
sha256sum "$APP_DIR/package.json" >> "$FINGERPRINT_FILE" 2>/dev/null || true
sha256sum "$APP_DIR/pyproject.toml" >> "$FINGERPRINT_FILE" 2>/dev/null || true

echo "   Fingerprint saved: $FINGERPRINT_FILE"
echo "   Files hashed: $(wc -l < "$FINGERPRINT_FILE")"

# 2. Save git diff as the candidate
echo "2. Saving candidate diff..."
CANDIDATE_FILE="$FREEZE_DIR/${TODAY}-${FEATURE_NAME}.candidate.patch"
git -C "$RDD_ROOT" diff > "$CANDIDATE_FILE" 2>/dev/null || echo "No changes to diff" > "$CANDIDATE_FILE"
echo "   Candidate saved: $CANDIDATE_FILE"

# 3. Create manifest
echo "3. Creating manifest..."
MANIFEST_FILE="$FREEZE_FILE.manifest.json"
cat > "$MANIFEST_FILE" << EOF
{
  "feature": "$FEATURE_NAME",
  "app_dir": "$APP_DIR",
  "repo_root": "$RDD_ROOT",
  "fingerprint": "$(sha256sum "$FINGERPRINT_FILE" | awk '{print $1}')",
  "candidate_patch": "$CANDIDATE_FILE",
  "files_changed": $(wc -l < "$FINGERPRINT_FILE"),
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
echo "   bash scripts/rdd/review.sh all '${FEATURE_NAME}'"
echo "   bash scripts/rdd/review.sh sdd-engineer '${FEATURE_NAME}'"
echo "   bash scripts/rdd/review.sh test-engineer '${FEATURE_NAME}'"
echo "   bash scripts/rdd/review.sh frontend-architect '${FEATURE_NAME}'"
echo "   bash scripts/rdd/review.sh backend-architect '${FEATURE_NAME}'"
