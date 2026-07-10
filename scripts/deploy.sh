#!/bin/bash
# Deploy productos para un cliente
# Uso: bash deploy.sh "Nombre Artista" "whatsapp" "email"
set -euo pipefail

ARTISTA="${1:-Artista}"
WHATSAPP="${2:-526621234567}"
EMAIL="${3:-artista@email.com}"
REPO="productos-$(echo "$ARTISTA" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

echo "=== Deploy para: $ARTISTA ==="

# 1. Crear landing personalizada
echo "📄 Creando landing page..."
mkdir -p "/tmp/$REPO"
cp -r /home/mystic/products/landing-artista/* "/tmp/$REPO/"
cp /home/mystic/products/booking/index.html "/tmp/$REPO/booking.html"

# 2. Reemplazar placeholders
sed -i "s/Nombre del\\? Artista/$ARTISTA/g" "/tmp/$REPO/index.html"
sed -i "s/Nombre del\\? Artista/$ARTISTA/g" "/tmp/$REPO/booking.html"
sed -i "s/526621234567/$WHATSAPP/g" "/tmp/$REPO/index.html"
sed -i "s/526621234567/$WHATSAPP/g" "/tmp/$REPO/booking.html"

# 3. Crear repo y subir
echo "📤 Subiendo a GitHub Pages..."
cd "/tmp/$REPO"
git init
git checkout -b main
git add -A
git commit -m "feat: landing + booking para $ARTISTA"
gh repo create "sonoradigitalcorp-H/$REPO" --public --push --source=. --remote origin 2>/dev/null || {
    git remote add origin "https://github.com/sonoradigitalcorp-H/$REPO.git"
    git push -u origin main --force
}

# 4. Habilitar GitHub Pages
sleep 2
gh api "repos/sonoradigitalcorp-H/$REPO/pages" -X POST \
  --input <(echo '{"source":{"branch":"main","path":"/"}}') 2>/dev/null || true

# 5. URL
echo ""
echo "✅ Landing publicada en:"
echo "   https://sonoradigitalcorp-H.github.io/$REPO/"
echo "   https://sonoradigitalcorp-H.github.io/$REPO/booking.html"
echo ""
echo "📱 WhatsApp del artista: wa.me/$WHATSAPP"
echo ""
echo "=== LISTO ==="
