#!/bin/bash
# Instalar cron jobs para el sistema autónomo 24/7
# Ejecutar: bash scripts/install-cron.sh

CRON_FILE="/tmp/jarvis-cron"
cat > "$CRON_FILE" << 'EOF'
# ── JARVIS Autonomous System ──────────────────────
# Healthcheck + tareas menores cada 15 minutos
*/15 * * * * /home/mystic/jarvis/scripts/autonomous.sh > /dev/null 2>&1

# Protocolo de ideas (cada hora)
0 * * * * cd /home/mystic/jarvis && python3 -c "
import sqlite3
conn = sqlite3.connect('engram.db')
c = conn.cursor()
c.execute(\"SELECT id, summary FROM memories WHERE tag='idea:pending' LIMIT 3\")
for id, summary in c.fetchall():
    print(f'Procesando idea {id}: {summary[:80]}')
    c.execute(\"UPDATE memories SET tag='idea:scheduled' WHERE id=?\", (id,))
conn.commit()
conn.close()
" >> /home/mystic/jarvis/logs/ideas.log 2>&1

# Backup diario a las 3 AM
0 3 * * * bash /home/mystic/jarvis/scripts/backup.sh > /dev/null 2>&1

# Reporte semanal los lunes 9 AM
0 9 * * 1 cd /home/mystic/jarvis && python3 scripts/weekly-report.py >> logs/report.log 2>&1

# Cleanup logs viejos cada noche
0 2 * * * find /home/mystic/jarvis/logs -name "*.log" -mtime +14 -delete
EOF

crontab "$CRON_FILE"
rm "$CRON_FILE"
echo "✅ Cron jobs instalados:"
crontab -l
