#!/bin/bash
# Daily Content Pipeline — SDC Agent OS
# Runs every day at 6:00 AM
# Generates content for all active artists

set -e
MCP="http://127.0.0.1:8180/mcp/execute"
DATE=$(date +%Y-%m-%d)
LOG="/home/ubuntu/sonora-digital-corp/core/state/logs/content-pipeline-${DATE}.log"
mkdir -p "$(dirname "$LOG")"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
tool() {
  local result
  result=$(curl -s "$MCP" -X POST -H "Content-Type: application/json" -d "$1" --max-time 120)
  echo "$result" >> "$LOG"
  echo "$result"
}

log "=== Daily Content Pipeline — $DATE ==="

# Step 1: Sync Hasura stats to RAG
log "[1/6] Syncing Hasura stats to Qdrant..."
tool '{"tool":"hasura_query","args":{"query":"query { artists { id name streams revenue followers } }"}}' > /tmp/artists.json
ARTISTS=$(python3 -c "
import json
with open('/tmp/artists.json') as f:
    d = json.load(f)
r = d.get('result', {})
for a in r.get('data', {}).get('artists', []):
    print(f\"{a['name']}|{a['id']}|{a['streams']}|{a['revenue']}|{a['followers']}\")
")
echo "$ARTISTS" | while IFS='|' read -r name id streams revenue followers; do
  log "  Syncing stats for $name..."
  tool "$(python3 -c "
import json
print(json.dumps({'tool':'rag_index','args':{
    'tenant_id':'abe_music',
    'document_id': 'stats_${id}_${DATE}',
    'content': f'$name tiene {streams} streams, \${revenue} revenue, {followers} seguidores. Fecha: $DATE',
    'metadata': {'artist_id': '$id', 'date': '$DATE', 'type': 'stats'}
}}))
")" > /dev/null
done

# Step 2: Ingest news/trends via RAG context
log "[2/6] Checking RAG context..."
tool '{"tool":"rag_context_for_script","args":{"tenant_id":"abe_music"}}' > /dev/null 2>&1 || true

# Step 3-6: For each artist, generate content
log "[3/6] Generating content per artist..."
SUCCESS=0
FAIL=0
echo "$ARTISTS" | while IFS='|' read -r name id streams revenue followers; do
  artist_slug=$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
  log "  Processing: $name..."

  # Get yesterday's content to avoid duplicates
  YESTERDAY=$(python3 -c "from datetime import date,timedelta;print((date.today()-timedelta(1)).isoformat())")
  PREV=$(tool "$(python3 -c "
import json
print(json.dumps({'tool':'engram_get','args':{'tenant_id':'abe-music','key':f'content_${artist_slug}_${YESTERDAY}'}}))
")" | python3 -c "
import json,sys
d=json.load(sys.stdin)
r=d.get('result',{})
if r.get('found'):
    print(r['value'][:100])
" 2>/dev/null || echo "")

  # Generate script via LLM with context
  log "    Generating script..."
  SCRIPT=$(tool "$(python3 -c "
import json
print(json.dumps({'tool':'llm_chat','args':{
    'system': f'Eres el content agent de ABE Music. Genera un script de 60 segundos para $name. Contexto: {streams} streams, \${revenue} revenue, {followers} seguidores. Contenido de ayer: {PREV}. Idioma: español.',
    'message': 'Genera el script para hoy'
}}))
")" | python3 -c "
import json,sys
d=json.load(sys.stdin)
r=d.get('result',{})
if isinstance(r, dict):
    print(r.get('content',''))
" 2>/dev/null || echo "Script para $name del $DATE")

  log "    Script generated (${#SCRIPT} chars)"

  # Generate video via FAL
  log "    Generating video..."
  VIDEO_RESULT=$(tool "$(python3 -c "
import json
print(json.dumps({'tool':'generate_video','args':{
    'artist_name':'$name',
    'prompt': f'$name hablando a cámara, estilo TikTok',
    'script_text': '$SCRIPT',
    'content_type': 'clase'
}}))
")")

  VIDEO_URL=$(echo "$VIDEO_RESULT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
r=d.get('result',{})
if isinstance(r, dict):
    print(r.get('video_url',''))
" 2>/dev/null)

  if [ -n "$VIDEO_URL" ]; then
    log "    Video generated: $VIDEO_URL"

    # Export to 4 formats
    log "    Exporting to 4 formats..."
    EXPORT_RESULT=$(tool "$(python3 -c "
import json
print(json.dumps({'tool':'ffmpeg_multiformat','args':{
    'video_url':'$VIDEO_URL',
    'artist_name':'$name'
}}))
")")
    log "    Export result: $(echo "$EXPORT_RESULT" | head -c 200)"

    # Save to Engram
    tool "$(python3 -c "
import json
print(json.dumps({'tool':'engram_save','args':{
    'tenant_id':'abe-music',
    'key': f'content_${artist_slug}_${DATE}',
    'value': f'Script: ${SCRIPT::100}... Video: ${VIDEO_URL}',
    'tags': 'content daily'
}}))
")" > /dev/null

    SUCCESS=$((SUCCESS + 1))
    log "  ✅ $name done"
  else
    log "  ❌ $name video failed"
    FAIL=$((FAIL + 1))
    tool "$(python3 -c "
import json
print(json.dumps({'tool':'engram_save','args':{
    'tenant_id':'abe-music',
    'key': f'content_fail_${artist_slug}_${DATE}',
    'value': f'Failed to generate video for $name. ${VIDEO_RESULT}'
}}))
")" > /dev/null
  fi
done

# Final notification
log "=== Pipeline Complete: $SUCCESS success, $FAIL failures ==="
python3 -c "
import json, subprocess
msg = f'🎬 Pipeline diario completado:\n✅ {SUCCESS} artistas generados\n❌ {FAIL} fallos'
subprocess.run(['/usr/bin/curl', '-s', '-X', 'POST',
    'https://api.telegram.org/bot$ABE_TELEGRAM_TOKEN/sendMessage',
    '-d', f'chat_id=$ABE_TELEGRAM_CHAT&text={msg}'], timeout=10)
" 2>/dev/null || true

exit $FAIL
