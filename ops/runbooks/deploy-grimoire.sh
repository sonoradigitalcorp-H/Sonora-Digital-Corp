#!/bin/bash
# Deploy del Grimoire 3D Agentic OS al VPS
# Uso: bash ops/runbooks/deploy-grimoire.sh
set -e

GRIMOIRE_DIR="apps/grimoire"
VPS_DEST="ovh:/var/www/grimoire"
DOMAIN="grimorio.sonoradigitalcorp.com"

echo "✦ Deploy Grimoire 3D"
echo "━━━━━━━━━━━━━━━━━━"

# 1. Build
echo "📦 Building..."
cd "$GRIMOIRE_DIR"
npm run build 2>/dev/null || { echo "❌ Build failed"; exit 1; }
cd ../..

# 2. Deploy al VPS
echo "🚀 Deploying to $VPS_DEST..."
rsync -avz --delete "$GRIMOIRE_DIR/dist/" "$VPS_DEST/"

# 3. Verificar
echo "✅ Deploy completo"
echo "🌐 https://$DOMAIN"
echo ""
echo "📁 Archivos desplegados:"
ssh ovh "ls -lh /var/www/grimoire/"
