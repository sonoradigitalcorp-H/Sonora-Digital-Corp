#!/usr/bin/env bash
set -euo pipefail

# ABE Music — Artist Onboarding Pipeline
# Usage: ./onboard-artist.sh [artist_name] [spotify_id] [genre] [instagram] [tiktok]
# Example: ./onboard-artist.sh "Nuevo Artista" "abc123def" "Regional Mexicano" "@ig" "@tt"

NAME="${1:-}"
SPOTIFY_ID="${2:-}"
GENRE="${3:-}"
INSTAGRAM="${4:-}"
TIKTOK="${5:-}"

if [ -z "$NAME" ]; then
    echo "Usage: $0 \"Artist Name\" spotify_id genre [instagram] [tiktok]"
    exit 1
fi

echo "🎵 Onboarding artist: $NAME"

DATA_FILE="../data/abe-music.json"
API_URL="http://localhost:8080"
DOMAIN="https://sonoradigitalcorp.com"

# 1. Get Spotify info via public API
echo "🔍 Looking up Spotify data..."
SPOTIFY_URL="https://open.spotify.com/artist/$SPOTIFY_ID"

SPOTIFY_DATA=$(curl -s "https://api.spotify.com/v1/artists/$SPOTIFY_ID" 2>/dev/null || echo '{}')

# Note: requires Spotify API token. For now we prompt for manual data.
echo ""
echo "⚠️  Spotify API requires an access token."
echo "   Enter estimated stats (or 0 to skip):"
read -p "   Monthly listeners: " MONTHLY
read -p "   Total streams: " STREAMS
read -p "   Top song: " TOP_SONG
read -p "   Top song streams: " TOP_SONG_STREAMS

# Generate UUID-like id
ARTIST_ID=$(python3 -c "import uuid; print(uuid.uuid4().hex[:8])")
NOW=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")

# 2. Create JSON entry
echo "📝 Creating data entry..."
python3 << PYEOF
import json, os

path = os.path.expanduser("$DATA_FILE")
with open(path) as f:
    data = json.load(f)

artist = {
    "id": "$ARTIST_ID",
    "nombre": "$NAME",
    "genero": "$GENRE",
    "pais": "México",
    "status": "signed",
    "email": "",
    "telefono": "",
    "created_at": "$NOW",
    "streams": ${STREAMS:-0},
    "revenue": ${STREAMS:-0},
    "releases_count": 0,
    "monthly_listeners": ${MONTHLY:-0},
    "top_song": "$TOP_SONG",
    "top_song_streams": ${TOP_SONG_STREAMS:-0},
    "instagram": "$INSTAGRAM",
    "tiktok": "$TIKTOK",
    "spotify_url": "$SPOTIFY_URL",
    "label": "ABE Music"
}

data["artists"][artist["id"]] = artist

with open(path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Artist $NAME added with ID $ARTIST_ID")
PYEOF

# 3. Create GitHub Pages landing page
echo "🌐 Creating landing page..."
mkdir -p "../landing-artista"
LANDING_FILE="../landing-artista/productos-$NAME.html"

cat > "$LANDING_FILE" << HTMLEOF
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$NAME · ABE Music</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:#0a0a0f;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:linear-gradient(135deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.06);border-radius:20px;padding:40px;max-width:500px;text-align:center}
.avatar{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#c8a87c,#8a6d44);margin:0 auto 20px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;color:#060608}
h1{font-size:24px;color:#fff;margin-bottom:8px}
.genre{color:#c8a87c;font-size:12px;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:20px}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}
.stat .num{font-size:22px;font-weight:700;color:#fff}
.stat .lab{font-size:11px;color:#666}
.btn{display:inline-block;padding:10px 24px;border-radius:10px;background:rgba(200,168,124,0.12);color:#c8a87c;text-decoration:none;font-weight:600;margin-top:16px}
.btn:hover{background:rgba(200,168,124,0.2)}
</style>
</head>
<body>
<div class="card">
<div class="avatar">${NAME:0:1}</div>
<h1>$NAME</h1>
<div class="genre">$GENRE · ABE Music</div>
<div class="stats">
<div class="stat"><div class="num">${STREAMS:,}</div><div class="lab">Streams</div></div>
<div class="stat"><div class="num">${MONTHLY:,}</div><div class="lab">Oyentes/mes</div></div>
</div>
<a class="btn" href="$SPOTIFY_URL" target="_blank">Escuchar en Spotify</a>
</div>
</body>
</html>
HTMLEOF

echo "✅ Landing page created: $LANDING_FILE"

# 4. Deploy to server
echo "🚀 Deploying to production..."
scp -i ~/.ssh/id_ed25519_sdc "$DATA_FILE" ubuntu@149.56.46.173:~/sdc/data/
ssh -i ~/.ssh/id_ed25519_sdc ubuntu@149.56.46.173 "sudo systemctl restart abe-server.service"

# 5. Notify via Telegram
echo "📱 Sending Telegram notification..."
TOKEN=$(grep ABE_TELEGRAM_TOKEN ~/sdc/.env 2>/dev/null | cut -d= -f2 || echo "")
CHAT=$(grep ABE_TELEGRAM_CHAT ~/sdc/.env 2>/dev/null | cut -d= -f2 || echo "5738935134")
if [ -n "$TOKEN" ]; then
    MSG="🎤 Nuevo artista onboarded: $NAME\n📊 Streams: ${STREAMS:-0:,}\n🎵 $SPOTIFY_URL\n🌐 $DOMAIN"
    curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
        -d "chat_id=$CHAT" -d "text=$MSG" -d "disable_web_page_preview=true" > /dev/null
fi

echo ""
echo "✅ Done! $NAME is now live on $DOMAIN"
