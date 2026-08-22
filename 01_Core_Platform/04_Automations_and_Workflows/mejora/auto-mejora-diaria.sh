#!/bin/bash
# auto-mejora-diaria.sh — Automejora DETERMINISTA, $0 LLM (no gasta OpenRouter)
# Analiza: proceso opencode/hermes/gateway/mcp pesados, guardián canónico, servicios VPS, disk, git.
export PATH="/home/mystic/.local/bin:/usr/bin:/bin:$PATH"
REPO="/home/mystic/Documentos/Sonora Digital Corp Nuevo"
LOG="/home/mystic/cron/logs"
mkdir -p "$LOG"
TS="$(date +%Y%m%d-%H%M)"
OUT="$LOG/auto-mejora-$TS.log"
{
  echo "=== AUTO-MEJORA $TS (determinista, \$0 LLM) ==="

  echo "--- 1. Guardián esqueleto canónico ---"
  ( cd "$REPO" && bash 00_Administration/guardians/structure_guard.sh ) || echo "⚠️ DERIVA detectada, acción manual"

  echo "--- 2. Procesos pesados (killer de duplicados, RAM <400MB alerta) ---"
  FREE_MB=$(free -m | awk 'NR==2{print $4}')
  echo "RAM libre: ${FREE_MB}MB"
  if [ "$FREE_MB" -lt 400 ]; then echo "⚠️ RAM CRÍTICA — matar accesorios"; fi
  # Duplicados de gateway (prohibido en local = solo 1)
  DUPS=$(pgrep -fc "hermes_cli.main gateway run")
  if [ "$DUPS" -gt 1 ]; then echo "⚠️ $DUPS gateways hermes — matar extras"; pkill -of "hermes_cli.main gateway run"; fi
  # Procesos MCP accesorios MÁXIMO 1 de cada uno
  for m in "mcp-server-fetch" "playwright" "mcp-server-filesystem"; do
    C=$(pgrep -fc "$m")
    [ "$C" -gt 1 ] && echo "⚠️ $m x$C — matar extras" && pkill -of "$m"
  done

  echo "--- 3. Servicios VPS (via SSH, no gasta LLM) ---"
  ssh -o ConnectTimeout=6 -o BatchMode=yes -o IdentitiesOnly=yes \
    ubuntu@149.56.46.173 -p 22 -i "$HOME/.ssh/id_ed25519_sdc" -o StrictHostKeyChecking=no \
    "for s in nginx cloudflared-tunnel vps-ai-server hermosillo-webhook hermes-gateway; do printf '%s ' \$(systemctl is-active \$s); done" \
    2>/dev/null || echo "⚠️ VPS no alcanzable"

  echo "--- 4. Disk ---"
  df -h / | awk 'NR==2 { if ($5+0 > 85) print "⚠️ DISK "$5; else print "Disk OK "$5 }'

  echo "--- 5. Git (rama next, sin push) ---"
  ( cd "$REPO" && git fetch origin next --quiet 2>/dev/null; git status --short | head -5; git lg -2 2>/dev/null || git log --oneline -2 )

  echo "--- 6. Estructura gobernancia (manifiestos presentes) ---"
  for m in AGENTS_MANIFEST.md SYSTEM_MANIFEST.md; do
    [ -f "$REPO/$m" ] && echo "OK $m" || echo "⚠️ falta $m"
  done

  echo "=== FIN ==="
} > "$OUT" 2>&1
echo "log: $OUT"
tail -3 "$OUT"
