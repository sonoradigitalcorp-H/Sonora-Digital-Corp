#!/bin/bash
# AGENCY OS — GitHub Sync Automatizado
# Ejecuta: Después de cada commit manual, o automático en pipeline
# Frecuencia: Cada sesión de trabajo
set -euo pipefail

cd /home/mystic/sonora-digital-corp

echo "=== AGENCY OS — GitHub Sync ==="

# 1. Detectar remote
REMOTE=$(git remote -v 2>/dev/null | head -1 || echo "")
if [ -z "$REMOTE" ]; then
    echo "⚠️  No GitHub remote configurado."
    echo "   Para configurar:"
    echo "   gh repo create jarvis --private --source=/home/mystic/sonora-digital-corp --remote=origin --push"
    echo "   O manual: git remote add origin git@github.com:TU_USER/jarvis.git"
    exit 1
fi

# 2. Verificar que estamos en main
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "⚠️  En branch '$BRANCH', no 'main'. Switcheando..."
    git checkout main 2>/dev/null || true
fi

# 3. Status
STAGED=$(git diff --cached --stat 2>/dev/null | tail -1 || echo "0")
UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)
MODIFIED=$(git diff --stat 2>/dev/null | tail -1 || echo "0")

echo "   Staged: $STAGED"
echo "   Untracked: $UNTRACKED"
echo "   Modified: $MODIFIED"

# 4. Tests pasan?
echo "   Running tests..."
if ! python3 -m pytest tests/ -x -q 2>/dev/null; then
    echo "❌ TESTS FALLAN. No se pushea."
    exit 1
fi
echo "   ✅ Tests OK"

# 5. Pull antes de push (evitar conflictos)
echo "   Pulling latest..."
git pull origin main 2>/dev/null || echo "   No changes from remote"

# 6. Push
echo "   Pusheando a GitHub..."
git push origin main 2>&1
echo ""
echo "✅ Sync complete"
