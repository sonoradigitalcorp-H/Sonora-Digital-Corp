#!/bin/bash
# JARVIS 24/7 Autonomous Agent System
# Ejecuta tareas de forma autónoma: ideas, tests, mejoras, reportes
# Correr vía cron: */15 * * * * /home/mystic/sonora-digital-corp/scripts/autonomous.sh

set -euo pipefail

LOG="/home/mystic/sonora-digital-corp/state/logs/autonomous.log"
LOCK="/tmp/jarvis-autonomous.lock"
JARVIS_HOME="/home/mystic/sonora-digital-corp"
ENGAM_DB="${JARVIS_HOME}/state/engram.db"
NOW=$(date '+%Y-%m-%d %H:%M:%S')

# Evitar ejecución simultánea
if [ -f "$LOCK" ] && [ -n "$(find "$LOCK" -mmin -5 2>/dev/null)" ]; then
    exit 0
fi
echo "$$" > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

mkdir -p "$(dirname "$LOG")"

echo "[$NOW] === Autónomo: Iniciando ciclo ===" >> "$LOG"

# ── Tarea 1: Healthcheck automático ────────
{
    echo "=== Healthcheck ==="
    # Probar servicios clave
    for svc in "http://localhost:5174/health" "http://localhost:8000/health" "http://localhost:18789/health"; do
        code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$svc" 2>/dev/null || echo "000")
        echo "  $svc → $code"
        if [ "$code" = "000" ] || [ "$code" = "000" ]; then
            echo "  ⚠️  Servicio caído: $svc"
        fi
    done
    
    # Verificar Docker
    docker ps --format "{{.Names}} {{.Status}}" 2>/dev/null | while read line; do
        echo "  🐳 $line"
    done
} >> "$LOG" 2>&1

# ── Tarea 2: Ideas pendientes en Engram ────
if [ -f "$ENGAM_DB" ]; then
    python3 -c "
import sqlite3
conn = sqlite3.connect('$ENGAM_DB')
c = conn.cursor()
# Buscar ideas sin procesar
c.execute(\"SELECT id, summary FROM memories WHERE tag='idea:pending' LIMIT 5\")
ideas = c.fetchall()
if ideas:
    for id, summary in ideas:
        print(f'💡 Idea pendiente: {summary[:80]}...')
        c.execute(\"UPDATE memories SET tag='idea:processing' WHERE id=?\", (id,))
        # Aquí se podría ejecutar el protocolo de ideas
conn.commit()
conn.close()
" 2>/dev/null >> "$LOG" || true
fi

# ── Tarea 3: Cleanup de logs antiguos ─────
find "$JARVIS_HOME/state/logs" -name "*.log" -mtime +7 -delete 2>/dev/null
find "$JARVIS_HOME/state/backups" -maxdepth 1 -type d -ctime +30 -exec rm -rf {} \; 2>/dev/null || true

# ── Tarea 4: Backup automático (diario) ────
HOUR=$(date +%H)
if [ "$HOUR" = "03" ]; then
    bash "$JARVIS_HOME/scripts/backup.sh" >> "$LOG" 2>&1
fi

# ── Tarea 5: Reporte de status ─────────────
{
    echo "=== Resumen ==="
    echo "  Brain: $(curl -s http://localhost:5174/api/brain/graph | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d[\"nodes\"]))' 2>/dev/null || echo '?') nodos"
    echo "  Productos en tienda: $(curl -s http://localhost:5174/api/store/products | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d[\"products\"]))' 2>/dev/null || echo '?')"
    echo "  GitHub commits hoy: $(git -C $JARVIS_HOME log --oneline --since=midnight 2>/dev/null | wc -l)"
} >> "$LOG" 2>&1

echo "[$NOW] ✅ Ciclo completado" >> "$LOG"
