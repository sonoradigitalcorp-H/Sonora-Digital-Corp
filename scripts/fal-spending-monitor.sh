#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# FAL Spending Monitor — Vigila el gasto en fal.ai y alerta si hay anomalías
# ──────────────────────────────────────────────────────────────────────────────
# Uso:
#   ./scripts/fal-spending-monitor.sh                # Resumen de todos los tenants
#   ./scripts/fal-spending-monitor.sh abe-music      # Reporte detallado de un tenant
#   ./scripts/fal-spending-monitor.sh --watch        # Loop de monitoreo cada 5 min
#   ./scripts/fal-spending-monitor.sh --alert-only   # Solo si hay alertas activas
# ──────────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")/.."
SDC_HOME=$(pwd)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STATE_DIR="$SDC_HOME/state"
REPORT_FILE="$STATE_DIR/fal-spending-report.json"
LOCK_FILE="$STATE_DIR/fal-monitor.lock"
DB_PATH="$STATE_DIR/budget.db"

ensure_state_dir() {
    mkdir -p "$STATE_DIR"
}

check_db() {
    if [ ! -f "$DB_PATH" ]; then
        echo -e "${YELLOW}⚠️  No hay DB de gastos todavía. Ejecutá alguna operación FAL primero.${NC}"
        # Intentar crearla
        python3 -c "
from policy.fal_guard import FalGuard
FalGuard()
print('DB creada')
" 2>/dev/null && echo -e "${GREEN}✅ DB creada${NC}" || true
    fi
}

list_tenants() {
    python3 -c "
import sqlite3, json
from pathlib import Path
db = Path('$DB_PATH')
if db.exists():
    conn = sqlite3.connect(str(db))
    try:
        rows = conn.execute('SELECT DISTINCT tenant FROM fal_usage ORDER BY tenant').fetchall()
        if rows:
            print('\n'.join(r[0] for r in rows))
        else:
            print('__no_data__')
    finally:
        conn.close()
else:
    print('__no_db__')
"
}

print_summary() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║        📊  FAL SPENDING MONITOR — $(date '+%Y-%m-%d %H:%M')        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local tenants=$(list_tenants)
    
    if [ "$tenants" = "__no_db__" ] || [ "$tenants" = "__no_data__" ]; then
        echo -e "${GREEN}✅ No hay actividad FAL registrada.${NC}"
        echo -e "   Los límites de gasto están configurados en:"
        echo -e "   - ${BLUE}FAL_DAILY_LIMIT${NC}=${FAL_DAILY_LIMIT:-\$10} (default)"
        echo -e "   - ${BLUE}FAL_MAX_PER_CALL${NC}=${FAL_MAX_PER_CALL:-\$1} (default)"
        echo ""
        return
    fi
    
    local total_daily=0
    local total_limits=0
    local has_alerts=false
    local alert_count=0
    
    for tenant in $tenants; do
        local report=$(python3 -c "
from policy.fal_guard import FalGuard
import json
g = FalGuard()
print(json.dumps(g.report('$tenant')))
")
        local daily=$(echo "$report" | python3 -c "import sys,json;print(json.load(sys.stdin)['daily_used'])")
        local limit=$(echo "$report" | python3 -c "import sys,json;print(json.load(sys.stdin)['daily_limit'])")
        local pct=$(echo "$report" | python3 -c "import sys,json;print(json.load(sys.stdin)['daily_pct'])")
        local alerts=$(echo "$report" | python3 -c "import sys,json;print(json.load(sys.stdin)['active_alerts'])")
        local calls=$(echo "$report" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(d['recent_calls']))")
        local total_hist=$(echo "$report" | python3 -c "import sys,json;print(json.load(sys.stdin)['total_historical'])")
        
        total_daily=$(echo "$total_daily + $daily" | bc 2>/dev/null || echo "0")
        total_limits=$(echo "$total_limits + $limit" | bc 2>/dev/null || echo "0")
        
        if [ "$alerts" -gt 0 ]; then
            has_alerts=true
            alert_count=$((alert_count + alerts))
        fi
        
        # Color por porcentaje de uso
        if (( $(echo "$pct > 80" | bc -l) )); then
            echo -e "  ${RED}🔴${NC} ${tenant}: \$${daily}/\$${limit} (${pct}%) — ${alerts} alertas — ${calls} calls hoy — total hist: \$${total_hist}"
        elif (( $(echo "$pct > 50" | bc -l) )); then
            echo -e "  ${YELLOW}🟡${NC} ${tenant}: \$${daily}/\$${limit} (${pct}%) — ${alerts} alertas — ${calls} calls hoy — total hist: \$${total_hist}"
        else
            echo -e "  ${GREEN}🟢${NC} ${tenant}: \$${daily}/\$${limit} (${pct}%) — ${alerts} alertas — ${calls} calls hoy — total hist: \$${total_hist}"
        fi
    done
    
    echo ""
    echo -e "  Total gasto hoy: \$${total_daily} / \$${total_limits}"
    
    if [ "$has_alerts" = true ]; then
        echo -e "  ${RED}⚠️  ${alert_count} alerta(s) activa(s) — revisá con --watch o por tenant${NC}"
    else
        echo -e "  ${GREEN}✅ Sin alertas activas${NC}"
    fi
    echo ""
    
    # Guardar reporte
    python3 -c "
from policy.fal_guard import FalGuard
import json
g = FalGuard()
tenants = $(python3 -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
rows = conn.execute('SELECT DISTINCT tenant FROM fal_usage').fetchall()
conn.close()
print(json.dumps([r[0] for r in rows]))
")
report = {t: g.report(t) for t in tenants}
with open('$REPORT_FILE', 'w') as f:
    json.dump(report, f, indent=2)
" 2>/dev/null || true
}

print_detailed() {
    local tenant="$1"
    python3 -c "
from policy.fal_guard import print_report
print_report('$tenant')
"
}

watch_loop() {
    local interval="${1:-300}"
    echo -e "${BLUE}👀 Monitoreando FAL spending cada ${interval}s...${NC}"
    echo -e "${YELLOW}   Presioná Ctrl+C para salir${NC}"
    echo ""
    
    while true; do
        clear 2>/dev/null || true
        print_summary
        
        # Mostrar alertas no leídas
        local alerts=$(python3 -c "
from policy.fal_guard import FalGuard
import json, sqlite3
from pathlib import Path
db = Path('$DB_PATH')
if db.exists():
    conn = sqlite3.connect(str(db))
    rows = conn.execute('SELECT tenant, severity, message FROM fal_alerts WHERE acknowledged=0 ORDER BY id DESC LIMIT 10').fetchall()
    conn.close()
    for r in rows:
        print(f'[{r[0]}] {r[1]}: {r[2][:100]}')
")
        if [ -n "$alerts" ]; then
            echo -e "${RED}⚠️  ALERTAS ACTIVAS:${NC}"
            echo "$alerts" | while IFS= read -r line; do
                echo -e "  ${RED}•${NC} $line"
            done
            echo ""
        fi
        
        sleep "$interval"
    done
}

# ─── Main ────────────────────────────────────────────────────────────

ensure_state_dir
check_db

case "${1:-}" in
    --watch|-w)
        watch_loop "${2:-300}"
        ;;
    --alert-only|-a)
        local alerts=$(python3 -c "
from policy.fal_guard import FalGuard
import sqlite3
from pathlib import Path
db = Path('$DB_PATH')
if db.exists():
    conn = sqlite3.connect(str(db))
    count = conn.execute('SELECT COUNT(*) FROM fal_alerts WHERE acknowledged=0').fetchone()[0]
    conn.close()
    print(count)
" 2>/dev/null || echo "0")
        if [ "$alerts" -gt 0 ]; then
            print_summary
        else
            echo -e "${GREEN}✅ Sin alertas activas${NC}"
        fi
        ;;
    --help|-h)
        echo "Uso: $0 [tenant|--watch|--alert-only|--help]"
        echo ""
        echo "  <tenant>       Reporte detallado de un tenant específico"
        echo "  --watch        Loop de monitoreo cada 5 minutos"
        echo "  --alert-only   Mostrar solo si hay alertas"
        echo "  --help         Esta ayuda"
        ;;
    *)
        if [ -n "${1:-}" ]; then
            print_detailed "$1"
        else
            print_summary
        fi
        ;;
esac
