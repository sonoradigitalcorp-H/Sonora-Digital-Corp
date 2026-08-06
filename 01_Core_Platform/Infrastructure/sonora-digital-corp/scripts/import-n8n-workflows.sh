#!/bin/bash
# Import zero-token n8n workflows
cd "$(dirname "$0")/.."
N8N_URL="http://localhost:5678"
DIR="config/n8n-zero-token"
LOG="logs/n8n-import.log"

echo "[$(date)] === Importing n8n workflows ===" | tee -a $LOG

for f in $DIR/*.json; do
  NAME=$(basename "$f" .json)
  echo "[$(date)] Importing: $NAME" | tee -a $LOG
  
  # Try to import via n8n API
  WORKFLOW=$(cat "$f")
  RESPONSE=$(curl -s -X POST "$N8N_URL/rest/workflows" \
    -H "Content-Type: application/json" \
    -d "$WORKFLOW" 2>/dev/null)
  
  if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('name',''))" 2>/dev/null; then
    echo "  ✅ Imported: $NAME" | tee -a $LOG
  else
    echo "  ⚠️  API might need auth. Saving for manual import." | tee -a $LOG
  fi
done

echo "[$(date)] === Import complete ===" | tee -a $LOG
