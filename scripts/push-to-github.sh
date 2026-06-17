#!/bin/bash
# JARVIS — Push to GitHub
# Ejecutar: bash scripts/push-to-github.sh
set -euo pipefail

echo "⚡ JARVIS — Push to GitHub"
echo "=========================="

# 1. Configurar SSH
export GIT_SSH_COMMAND='ssh -i /home/mystic/.ssh/id_ed25519'

cd /home/mystic/sonora-digital-corp

# 2. Verificar que exista el repo en GitHub
if ! git ls-remote git@github.com:perrykingla69-cyber/jarvis.git &>/dev/null; then
    echo "❌ Repo no encontrado en GitHub."
    echo ""
    echo "Para crearlo manualmente:"
    echo "  1. Ir a https://github.com/new"
    echo "  2. Nombre: jarvis"
    echo "  3. Descripción: JARVIS AI Assistant"
    echo "  4. Público"
    echo "  5. NO marcar nada más"
    echo "  6. Click: Create repository"
    echo ""
    echo "Luego ejecuta este script de nuevo."
    echo ""
    echo "O crealo desde CLI con:"
    echo "  gh repo create jarvis --public --source=/home/mystic/sonora-digital-corp --remote=origin --push"
    exit 1
fi

# 3. Push
echo "📤 Pusheando a GitHub..."
git push -u origin main 2>&1
echo ""

# 4. Push tags
echo "🏷️  Pusheando tags..."
git tag -f v2.0.0 2>/dev/null
git push origin --tags -f 2>&1

echo ""
echo "✅ JARVIS está en GitHub:"
echo "   https://github.com/perrykingla69-cyber/jarvis"
echo ""
echo "📊 GitHub Actions se activarán automáticamente:"
echo "   - CI: lint + test + docker + specs en cada push"
echo "   - Deploy: con tags v*"
