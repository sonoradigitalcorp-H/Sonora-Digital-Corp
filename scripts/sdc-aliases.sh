# sdc-status — Verifica que estás en el repo correcto
sdc-status() {
  local pwd=$(pwd)
  if [ "$pwd" != "/home/mystic/sonora-digital-corp" ]; then
    echo "❌ FUERA DEL REPO: $pwd"
    echo "→ cd /home/mystic/sonora-digital-corp"
    return 1
  fi
  local remote=$(git remote get-url origin 2>/dev/null)
  local branch=$(git branch --show-current 2>/dev/null)
  local ahead=$(git rev-list --count origin/main...HEAD 2>/dev/null || echo 0)
  local behind=$(git rev-list --count HEAD...origin/main 2>/dev/null || echo 0)
  echo "✅ REPO CORRECTO"
  echo "   Remote: $remote"
  echo "   Branch: $branch"
  echo "   Ahead (sin push): $ahead"
  echo "   Behind (sin pull): $behind"
  local dirty=$(git status --porcelain 2>/dev/null | wc -l)
  [ "$dirty" -gt 0 ] && echo "⚠️  Archivos sin commit: $dirty" || echo "✅ Working tree limpio"
}

# Detectar si estamos en el repo equivocado
detect_wrong_repo() {
  local dir=$(pwd 2>/dev/null)
  if echo "$dir" | grep -qE "archive-sonora|SonoraDigitalCorp-Yami"; then
    echo "╔══════════════════════════════════════════════╗"
    echo "║  ❌  ESTÁS EN UN REPO OBSOLETO              ║"
    echo "║  Trabaja SOLO en:                           ║"
    echo "║  /home/mystic/sonora-digital-corp           ║"
    echo "╚══════════════════════════════════════════════╝"
  fi
}
detect_wrong_repo

# ── Clone Service Quantum Aliases ──
alias clone-quantum="xdg-open /tmp/clone-service-quantum.html 2>/dev/null &"
alias clone-test="cd /home/mystic/sonora-digital-corp && PYTHONPATH=. python3 -m pytest tests/test_clone_*.py -q"
alias clone-ls="ls -la /home/mystic/sonora-digital-corp/gherkin/clone-*.feature /home/mystic/sonora-digital-corp/tests/test_clone_*.py /home/mystic/sonora-digital-corp/mcp/servers/*clone*.py /home/mystic/sonora-digital-corp/mcp/servers/generate_mcp.py /home/mystic/sonora-digital-corp/mcp/servers/credit_mcp.py /home/mystic/sonora-digital-corp/scripts/clone_pipeline.py"
alias clone-spec="cd /home/mystic/sonora-digital-corp && (bat process/active/SPEC-20260718-CLONE-SERVICE.md 2>/dev/null || cat process/active/SPEC-20260718-CLONE-SERVICE.md)"
alias clone-help="echo '┌─ CLONE SERVICE ─────────────────────────────┐'
echo '│ clone-quantum  → Abre presentación cuántica   │'
echo '│ clone-status X → Estado del cliente X         │'
echo '│ clone-test     → Corre 82 tests cuánticos     │'
echo '│ clone-ls       → Lista todos los archivos     │'
echo '│ clone-spec     → Lee la SPEC del servicio     │'
echo '└──────────────────────────────────────────────┘'
echo ''
echo 'PIPELINE CLI (en sonora-digital-corp):'
echo '  python3 scripts/clone_pipeline.py --client-id X --action create-pack --pack-type basic'
echo '  python3 scripts/clone_pipeline.py --client-id X --action status'"

alias clone-flow="bash /home/mystic/sonora-digital-corp/scripts/test_clone_flow.sh"
clone-status() {
  cd /home/mystic/sonora-digital-corp
  PYTHONPATH=. python3 scripts/clone_pipeline.py --client-id "$1" --action status 2>/dev/null
}

# ── Digital Brain Aliases ──
alias brain-sync="bash /home/mystic/sonora-digital-corp/scripts/sync-brain-vault.sh"
alias brain-open="nohup /home/mystic/Applications/Obsidian.AppImage --no-sandbox /home/mystic/Documents/sdc-brain-vault > /dev/null 2>&1 & disown"
alias brain-status="echo '🧠 CEREBRO DIGITAL — Luis Daniel Guerrero Enciso'
echo '  Vault: ~/Documents/sdc-brain-vault'
ls /home/mystic/Documents/sdc-brain-vault/Observations/ 2>/dev/null | wc -l | xargs -I{} echo '  Observaciones: {}'
ls /home/mystic/Documents/sdc-brain-vault/People/ 2>/dev/null | wc -l | xargs -I{} echo '  Personas: {}'
ls /home/mystic/Documents/sdc-brain-vault/Decisions/ 2>/dev/null | wc -l | xargs -I{} echo '  Decisiones: {}'
ls /home/mystic/Documents/sdc-brain-vault/Projects/ 2>/dev/null | wc -l | xargs -I{} echo '  Proyectos: {}'
echo '  Engram DB: ~/.engram/engram.db ($(du -h ~/.engram/engram.db 2>/dev/null | cut -f1))'
echo '  Conecta con: Qdrant (vectores) + Neo4j (grafos)'"
