#!/bin/bash
# JARVIS — One-Command GitHub Setup
# bash scripts/setup-github.sh
set -euo pipefail

JARVIS_DIR="/home/mystic/sonora-digital-corp"
cd "$JARVIS_DIR"

echo "⚡ JARVIS — GitHub Auto-Setup"
echo "============================="
echo ""

# 1. Verificar SSH key
if ssh -T -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 git@github.com 2>&1 | grep -q "successfully"; then
    echo "✅ SSH key funciona"
else
    echo "❌ SSH key no funciona"
    exit 1
fi

# 2. Autenticar GitHub CLI
if gh auth status &>/dev/null; then
    echo "✅ GitHub CLI autenticado"
else
    echo "ℹ️  Autenticando GitHub CLI..."
    echo "   Código: $(gh auth login --hostname github.com --scopes 'repo,workflow' --web 2>&1 | grep -oP '[A-Z0-9]+-[A-Z0-9]+' | head -1)"
    echo "   Ve a https://github.com/login/device e ingresa el código"
    echo ""
    echo "⏳ Esperando autenticación..."
    sleep 30
fi

# 3. Crear repo (si no existe)
if ! gh repo view perrykingla69-cyber/jarvis &>/dev/null; then
    echo "📦 Creando repositorio..."
    gh repo create jarvis --public \
        --description "JARVIS AI Assistant — SDD specs, FastAPI, AgentOrchestrator, Voice, Neo4j" \
        --remote origin --source=. 2>&1 || true
fi

# 4. Push
echo "📤 Pusheando código..."
export GIT_SSH_COMMAND='ssh -i /home/mystic/.ssh/id_ed25519'
git remote set-url origin git@github.com:perrykingla69-cyber/jarvis.git 2>/dev/null || true
git push -u origin main --force 2>&1 || echo "   (primero crea el repo en GitHub)"

# 5. Tags
git tag -f v2.0.0 2>/dev/null
git push origin --tags -f 2>&1 || true

echo ""
echo "✅ Listo!"
echo "   https://github.com/perrykingla69-cyber/jarvis"
echo ""
echo "📊 GitHub Actions:"
echo "   CI:   $(gh run list --limit 1 2>/dev/null || echo 'pendiente')"
echo "   Deploy: automático con tags v*"
