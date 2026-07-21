#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════
# Ce-Son v3 — Deploy Script
# ═══════════════════════════════════════════════════════════════
REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$REPO/state/whatsapp/clients/r1"
LOG_DIR="$REPO/logs"

echo "🚀 Ce-Son v3 Deploy"
echo "━━━━━━━━━━━━━━━━━"

# 1. Create directories
mkdir -p "$STATE_DIR" "$LOG_DIR"

# 2. Setup wacli store
echo "📱 Checking wacli store..."
WACLI_STORE="${R1_WACLI_STORE:-$HOME/.config/wacli/r1-6623446953}"
if [ ! -f "$WACLI_STORE/config.json" ]; then
    echo "   Store not found at $WACLI_STORE"
    echo "   Run: wacli --store \"$WACLI_STORE\" link"
    echo "   Then scan QR code with the client's WhatsApp"
else
    echo "   ✅ Store exists at $WACLI_STORE"
fi

# 3. Install Python deps
echo "🐍 Installing dependencies..."
cd "$REPO"
pip install -q fastapi uvicorn pydantic httpx 2>/dev/null || true

# 4. Initialize DB
echo "🗄️  Initializing database..."
python3 -c "
import sys; sys.path.insert(0, '.')
from apps.whatsapp.order_store import get_db
conn = get_db()
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print(f'   ✅ {len(tables)} tables created: {[r[0] for r in tables]}')
conn.close()
"

# 5. Setup systemd services
echo "⚙️  Installing systemd services..."
USER_UNITS="$HOME/.config/systemd/user"
mkdir -p "$USER_UNITS"

for svc in whatsapp-r1-webhook whatsapp-r1-responder ce-son-api; do
    cp "$REPO/infra/systemd/${svc}.service" "$USER_UNITS/" 2>/dev/null && echo "   ✅ $svc.service" || echo "   ⚠️  $svc.service not found"
done

systemctl --user daemon-reload 2>/dev/null || true

# 6. Verify configs
echo "🔍 Verifying configuration..."
[ -f "$REPO/clients/r1/menu.json" ] && echo "   ✅ menu.json" || echo "   ⚠️  menu.json missing"
[ -f "$REPO/clients/r1/config.yaml" ] && echo "   ✅ config.yaml" || echo "   ⚠️  config.yaml missing"

# 7. Print summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Ce-Son v3 Deploy Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next steps:"
echo "   1. Link WhatsApp: wacli --store \"$WACLI_STORE\" link"
echo "   2. Set env vars in ~/.env.ce-son:"
echo "       export R1_WACLI_STORE=\"$WACLI_STORE\""
echo "       export R1_WACLI_PHONE=\"5216623446953\""
echo "       export R1_GROUP_JID=\"<grupo-repartidores>\""
echo "       export R1_OWNER_PHONE=\"<numero-dueno>\""
echo "       export OPENROUTER_API_KEY=\"<key>\""
echo "   3. Start services:"
echo "       systemctl --user start ce-son-api"
echo "       systemctl --user start whatsapp-r1-responder"
echo "       systemctl --user start whatsapp-r1-webhook"
echo "   4. Open dashboard: http://localhost:6400/frontends/ce-son/index.html"
echo ""
