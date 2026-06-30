#!/bin/bash
# git-push-all.sh — Push unificado para Sonora Digital Corp
set -e

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="main"
MSG="${1:-chore: auto-sync $(date '+%Y-%m-%d %H:%M')}"

echo "=== git-push-all: $REPO ==="
cd "$REPO"
git add -A
if git diff --cached --quiet; then
  echo "→ No hay cambios nuevos"
else
  git commit -m "$MSG"
  git push origin "$BRANCH"
  echo "✅ Pusheado: $MSG"
fi
