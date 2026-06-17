#!/bin/bash
# close-session.sh — Guarda TODO antes de cerrar sesion
# Ejecutar: bash /home/mystic/sonora-digital-corp/scripts/close-session.sh

cd /home/mystic/sonora-digital-corp
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG="state/logs/session-close-$TIMESTAMP.log"
mkdir -p state/logs

echo "[$(date)] === CLOSING SESSION ===" | tee -a "$LOG"

# 1. Guardar estado del sistema
echo "[1/6] Guardando estado..." | tee -a "$LOG"
python3 scripts/automation/memory-save.py >> "$LOG" 2>&1

# 2. Alimentar Neo4j con ultimas decisiones
echo "[2/6] Alimentando Neo4j..." | tee -a "$LOG"
python3 -c "
import sys; sys.path.insert(0, '.')
from src.core import neo4j_store
import subprocess
state = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True)
containers = state.stdout.strip().split('\n')
neo4j_store.save_memory('session:close:' + '$TIMESTAMP', f'Containers: {len(containers)} - {containers}')
print('Saved')
" 2>&1 | tee -a "$LOG"

# 3. Sincronizar Qdrant
echo "[3/6] Sincronizando Qdrant..." | tee -a "$LOG"
python3 -c "
import sys; sys.path.insert(0, '.')
from src.core.rag import rag
from src.core import neo4j_store
memories = neo4j_store.search_memory('', limit=200)
count = 0
for m in memories:
    text = f\"{m['key']}: {m['value']}\"
    if len(text) > 20:
        try: rag.store(text, metadata={'source': 'session-close', 'type': 'memory'}); count += 1
        except: pass
print(f'Synced {count} memories to Qdrant')
" 2>&1 | tee -a "$LOG"

# 4. Verificar servicios core
echo "[4/6] Verificando servicios..." | tee -a "$LOG"
for svc in jarvis-neo4j hermes_qdrant hermes_frontend hermes_api hermes_n8n; do
    if docker ps --format '{{.Names}}' | grep -q "$svc"; then
        echo "  ✅ $svc" | tee -a "$LOG"
    else
        echo "  ❌ $svc" | tee -a "$LOG"
    fi
done

# 5. Resumen de tokens y recursos
echo "[5/6] Recursos..." | tee -a "$LOG"
free -h | tee -a "$LOG"

# 6. Crear punto de restauracion
echo "[6/6] Punto de restauracion creado" | tee -a "$LOG"
date '+%s' > /home/mystic/sonora-digital-corp/state/last-session-epoch.txt

echo "[$(date)] === SESSION CLOSED ===" | tee -a "$LOG"
echo "Log: $LOG"
