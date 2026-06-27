#!/usr/bin/env bash
set -euo pipefail

# git-push-all.sh — Push a GitHub + respaldo local
#
# Uso:
#   bash scripts/git-push-all.sh
#
# Primera vez (configurar remote local):
#   git init --bare ~/sdc-repo-mirror.git
#   git remote add local ~/sdc-repo-mirror.git

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BRANCH="${1:-main}"
LOCAL_MIRROR="${HOME}/sdc-repo-mirror.git"

echo "🔐 Push a GitHub..."
git push origin "$BRANCH"

if [ -d "$LOCAL_MIRROR" ]; then
  echo "💾 Push a respaldo local..."
  # Verificar si el remote local existe, si no, agregarlo
  if ! git remote get-url local &>/dev/null; then
    git remote add local "$LOCAL_MIRROR"
  fi
  git push local "$BRANCH"
  echo "✅ Push completado a GitHub + local"
else
  echo "⚠️  Respaldo local no configurado."
  echo "   Para configurarlo:"
  echo "   git init --bare ~/sdc-repo-mirror.git"
  echo "   git remote add local ~/sdc-repo-mirror.git"
  echo ""
  echo "✅ Push completado a GitHub (solo)"
fi
