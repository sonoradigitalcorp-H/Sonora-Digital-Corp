#!/usr/bin/env bash
# end-session.sh — Cierra sesión: test gate + commit + PR + brain sync
#
# Uso:
#   ./scripts/end-session.sh --title "feat: arreglé onboarding"
#   ./scripts/end-session.sh
#   ./scripts/end-session.sh --no-pr
#   ./scripts/end-session.sh --no-tests
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }

TITLE=""; NO_PR=false; NO_TESTS=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="$2"; shift 2 ;;
    --no-pr) NO_PR=true; shift ;;
    --no-tests) NO_TESTS=true; shift ;;
    --help|-h) echo "Uso: $0 [--title '...'] [--no-pr] [--no-tests]"; exit 0 ;;
    *) err "Arg unknown: $1"; exit 1 ;;
  esac
done

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     🎬  END SESSION                      ║"
echo "║     Test gate → PR → Brain Sync          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
info "Branch: $BRANCH"

if [ "$BRANCH" = "main" ]; then
  err "Estás en main. Las sesiones deben usar un branch."
  echo "  Crea uno: git checkout -b session/$(date +%Y%m%d)-descripcion"
  exit 1
fi

# ─── 1. Test gate ────────────────────────────────────────────────────────
if [ "$NO_TESTS" = false ]; then
  info "Paso 1/5 — Test Gate..."
  CHANGED_PY=$(git diff --name-only origin/main..."$BRANCH" 2>/dev/null | grep '\.py$' || echo "")
  TEST_TARGETS=""

  if [ -n "$CHANGED_PY" ]; then
    while IFS= read -r f; do
      base=$(basename "$f" .py); dir=$(dirname "$f")
      if echo "$dir" | grep -q "scripts"; then
        [ -f "tests/test_${base}.py" ] && TEST_TARGETS="$TEST_TARGETS tests/test_${base}.py"
      fi
      if echo "$dir" | grep -q "tests"; then
        TEST_TARGETS="$TEST_TARGETS $f"
      fi
    done <<< "$CHANGED_PY"
  fi

  if [ -n "$TEST_TARGETS" ]; then
    info "Tests:$(echo "$TEST_TARGETS" | tr '\n' ' ')"
    python -m pytest $TEST_TARGETS -q --tb=short 2>&1 && ok "Tests ✅" || {
      err "Tests fallaron. Usa --no-tests para saltar."
      exit 1
    }
  else
    info "Corriendo suite general..."
    python -m pytest tests/ -q --tb=short 2>&1 | tail -3 && ok "Tests ✅" || {
      warn "Pueden ser fallos pre-existentes."
      read -r -p "  ¿Continuar? (y/N): " yn
      [[ "$yn" =~ ^[yY] ]] || { err "Abortado."; exit 1; }
    }
  fi
fi

# ─── 2. Título automático ────────────────────────────────────────────────
if [ -z "$TITLE" ]; then
  SPEC_FILE=$(ls -t process/active/SPEC-*.md 2>/dev/null | head -1 || echo "")
  if [ -n "$SPEC_FILE" ]; then
    TITLE="feat: $(basename "$SPEC_FILE" .md | sed 's/SPEC-[0-9]*-//' | tr '-' ' ')"
  else
    TITLE=$(git log -1 --pretty=%s 2>/dev/null || echo "feat: session $(date '+%Y-%m-%d')")
  fi
fi

# ─── 3. Commit todo ──────────────────────────────────────────────────────
info "Paso 2/5 — Committing..."
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "$TITLE" --no-verify 2>/dev/null && ok "Commited: $TITLE" || warn "Nada que commitear"
fi

# ─── 4. Push + PR ─────────────────────────────────────────────────────────
if [ "$NO_PR" = false ]; then
  info "Paso 3/5 — Push + PR..."
  git push origin "$BRANCH" 2>&1 || { err "Push falló"; exit 1; }
  ok "Push exitoso."

  if [ -f scripts/auto-pr.sh ]; then
    bash scripts/auto-pr.sh --title "$TITLE" --base main --head "$BRANCH" 2>&1
  else
    warn "auto-pr.sh no encontrado. PR manual:"
    echo "  gh pr create --title \"$TITLE\" --base main --head \"$BRANCH\""
  fi
else
  info "Paso 3/5 — PR saltado. Push manual: git push origin $BRANCH"
fi

# ─── 5. Brain sync ────────────────────────────────────────────────────────
info "Paso 4/5 — Brain sync..."
if [ -f scripts/sync-brain-vault.sh ]; then
  bash scripts/sync-brain-vault.sh 2>&1 | tail -3 && ok "Brain ✅" || warn "Brain sync falló"
fi

# ─── 6. Guardar metadata ─────────────────────────────────────────────────
info "Paso 5/5 — Guardando metadata..."
mkdir -p "$ROOT/state"
cat > "$ROOT/state/ultima-sesion.json" << EOF
{
  "branch": "$BRANCH",
  "titulo": "$TITLE",
  "fecha": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "cerrada": true
}
EOF
ok "Sesión cerrada."

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅  SESIÓN CERRADA                                 ║"
echo "║  Branch: $BRANCH"
echo "║  Code Review → GitHub → squash-merge a main         ║"
echo "║  Después: bash scripts/sync-to-vps.sh               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
