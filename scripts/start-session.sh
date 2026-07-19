#!/usr/bin/env bash
# start-session.sh — Inicia sesión con branch aislado + sync
#
# Crea una rama por sesión para evitar conflicto entre sesiones paralelas.
# Cada sesión tiene su propio branch aislado → PR → code review → merge.
#
# Uso:
#   ./scripts/start-session.sh --desc "arreglar onboarding tests"
#   ./scripts/start-session.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }

DESC=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --desc) DESC="$2"; shift 2 ;;
    --help|-h) echo "Uso: $0 --desc 'breve descripción'"; exit 0 ;;
    *) err "Arg unknown: $1"; exit 1 ;;
  esac
done

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     🚀  START SESSION                    ║"
echo "║     Branch aislado + sync automático     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

# ─── 1. Pedir descripción si no viene ──────────────────────────────────
if [ -z "$DESC" ]; then
  if [ "$CURRENT_BRANCH" != "main" ]; then
    warn "Ya estás en la rama '$CURRENT_BRANCH'"
    read -r -p "  ¿Usar esta rama? (Y/n): " yn
    if [[ ! "$yn" =~ ^[nN] ]]; then
      info "Continuando en rama actual: $CURRENT_BRANCH"
      bash scripts/session-status.sh
      exit 0
    fi
  fi
  read -r -p "  Describe esta sesión (ej: arreglar onboarding tests): " DESC
  [ -z "$DESC" ] && DESC="sin-descripcion-$(date +%H%M%S)"
fi

# ─── 2. Sync con origin/main ────────────────────────────────────────────
info "Paso 1/3 — Sincronizando con origin/main..."
if [ -f "$ROOT/scripts/git-sync.sh" ]; then
  bash scripts/git-sync.sh --force 2>&1 || warn "Sync tuvo problemas, continuando..."
else
  warn "git-sync.sh no encontrado, haciendo git pull..."
  git pull origin main --ff-only 2>/dev/null || git pull origin main 2>/dev/null || true
fi
ok "Repo sincronizado."

# ─── 3. Crear branch de sesión ──────────────────────────────────────────
DATE=$(date +%Y%m%d)
SAFE_DESC=$(echo "$DESC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50)
BRANCH="session/${DATE}-${SAFE_DESC}"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

if git rev-parse --verify "$BRANCH" 2>/dev/null; then
  [ "$CURRENT_BRANCH" != "$BRANCH" ] && git checkout "$BRANCH"
  ok "Switched a: $BRANCH"
else
  git checkout -b "$BRANCH"
  ok "Rama creada: $BRANCH"
  if [ -n "$(git status --porcelain)" ]; then
    info "Committing cambios pendientes en la rama..."
    git add -A
    git commit -m "wip: checkpoint $(date +%Y%m%d-%H%M)" --no-verify 2>/dev/null || true
  fi
fi

echo ""
info "Paso 2/3 — Mostrando estado..."
bash scripts/session-status.sh

echo ""
info "Paso 3/3 — Guardando metadata..."
mkdir -p "$ROOT/state"
cat > "$ROOT/state/ultima-sesion.json" << EOF
{
  "branch": "$BRANCH",
  "descripcion": "$DESC",
  "fecha": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
EOF
ok "Sesión iniciada."

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅  SESIÓN LISTA                        ║"
echo "║  Branch: $BRANCH"
echo "║  Al cerrar: bash scripts/end-session.sh  ║"
echo "╚══════════════════════════════════════════╝"
echo ""
