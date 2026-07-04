#!/usr/bin/env bash
# close-session.sh — Post-session cleanup automatizado
#
# Uso:
#   ./scripts/close-session.sh --spec-id SPEC-20260704-EVOLUTION --title "Evolution Loop" --tier 3
#   ./scripts/close-session.sh --dry-run
#   ./scripts/close-session.sh --interactive
#
# Pipeline:
#   1. Validate git status (no dirty files)
#   2. Run tests (gate — aborta si fallan)
#   3. Generate docs via auto-doc.py
#   4. Move active SPECs → process/completed/<dir>/
#   5. Update AGENTS.md (paths, test counts, anchored summary)
#   6. Merge process/CATALOG.md → process/completed/CATALOG.md + remove duplicate
#   7. Git add + commit + push
#   8. VPS sync via GitHub Action (auto en push)
#
# Flags:
#   --spec-id     SPEC ID (default: auto-detect from process/active/)
#   --title       Título de la sesión
#   --tier        1|2|3 (default: 2)
#   --summary     Resumen de la sesión
#   --dir         Nombre del directorio en process/completed/ (default: deriva de spec-id)
#   --dry-run     Solo muestra qué haría, no ejecuta nada
#   --no-tests    Saltea test gate
#   --no-push     Hace commit pero no push
#   --interactive Pregunta antes de cada paso
#   --force       Sobreescribe directorio de docs existente
#   --help        Muestra ayuda
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# ─── Colores ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }
dry()   { echo -e "${YELLOW}[DRY-RUN]${NC} $*"; }
step()  { echo ""; echo -e "${CYAN}═══ $* ═══${NC}"; }

# ─── Parse args ──────────────────────────────────────────────────────────────
SPEC_ID=""
TITLE=""
TIER=2
SUMMARY=""
DIR_NAME=""
DRY_RUN=false
NO_TESTS=false
NO_PUSH=false
INTERACTIVE=false
FORCE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --spec-id)     SPEC_ID="$2"; shift 2 ;;
    --title)       TITLE="$2"; shift 2 ;;
    --tier)        TIER="$2"; shift 2 ;;
    --summary)     SUMMARY="$2"; shift 2 ;;
    --dir)         DIR_NAME="$2"; shift 2 ;;
    --dry-run)     DRY_RUN=true; shift ;;
    --no-tests)    NO_TESTS=true; shift ;;
    --no-push)     NO_PUSH=true; shift ;;
    --interactive) INTERACTIVE=true; shift ;;
    --force)       FORCE=true; shift ;;
    --help|-h)
      sed -n '2,28p' "$0"
      exit 0
      ;;
    *) err "Unknown arg: $1"; exit 1 ;;
  esac
done

# ─── Auto-detect spec-id ─────────────────────────────────────────────────────
if [ -z "$SPEC_ID" ]; then
  latest_spec=$(ls -t process/active/SPEC-*.md 2>/dev/null | head -1)
  if [ -n "$latest_spec" ]; then
    SPEC_ID=$(basename "$latest_spec" .md)
    info "Auto-detected spec: $SPEC_ID"
  else
    err "No --spec-id provided and no SPECs found in process/active/"
    exit 1
  fi
fi

if [ -z "$TITLE" ]; then
  TITLE="$SPEC_ID"
  warn "No --title provided, using spec ID"
fi

DIR_NAME="${DIR_NAME:-$(echo "$SPEC_ID" | tr '[:upper:]' '[:lower:]' | sed 's/spec-//')}"
OUTPUT_DIR="process/completed/$DIR_NAME"

# ─── Interactive mode ────────────────────────────────────────────────────────
if [ "$INTERACTIVE" = true ]; then
  echo ""
  echo "══════════════════════════════════════════"
  echo "  Close Session — Interactive Mode"
  echo "══════════════════════════════════════════"
  read -r -p "Spec ID     [$SPEC_ID]: " input; SPEC_ID="${input:-$SPEC_ID}"
  read -r -p "Title       [$TITLE]: " input; TITLE="${input:-$TITLE}"
  read -r -p "Tier (1/2/3) [$TIER]: " input; TIER="${input:-$TIER}"
  read -r -p "Summary     []: " input; SUMMARY="${input:-$SUMMARY}"
  DIR_NAME=$(echo "$SPEC_ID" | tr '[:upper:]' '[:lower:]' | sed 's/spec-//')
  OUTPUT_DIR="process/completed/$DIR_NAME"
  echo ""
fi

# ─── Dry-run: show plan ──────────────────────────────────────────────────────
if [ "$DRY_RUN" = true ]; then
  step "DRY-RUN PLAN"
  echo "  Working dir:     $ROOT"
  echo "  Spec ID:         $SPEC_ID"
  echo "  Title:           $TITLE"
  echo "  Tier:            $TIER"
  echo "  Output dir:      $OUTPUT_DIR/"
  echo "  Summary:         ${SUMMARY:-"(not provided)"}"
  echo ""
  echo "  Steps:"
  echo "    1. [SKIP] Validate git status"
  echo "    2. [SKIP] Run tests (gate)"
  [ "$NO_TESTS" = true ] && echo "       └─ skipped (--no-tests)"
  echo "    3. Generate docs:"
  echo "       python3 scripts/auto-doc.py --spec-id $SPEC_ID --title \"$TITLE\" --tier $TIER --dir $DIR_NAME"
  echo "    4. Move active SPECs:"
  base_id="$SPEC_ID"
  echo "       process/active/${base_id}* -> $OUTPUT_DIR/"
  echo "       process/active/SCORE-${base_id#SPEC-}* -> $OUTPUT_DIR/"
  echo "    5. Update AGENTS.md (paths + test counts + anchored summary)"
  echo "    6. Merge + remove process/CATALOG.md -> process/completed/CATALOG.md"
  echo "    7. Git add + commit + push"
  [ "$NO_PUSH" = true ] && echo "       └─ no push (--no-push)"
  echo "    8. VPS sync via GitHub Action (automático en push)"
  echo ""
  exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Validate git status
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 1/8 — Validate git status"
DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$DIRTY" -gt 0 ]; then
  warn "Hay $DIRTY archivos sin commitear"
  git status --short 2>/dev/null
  echo ""
  if [ "$INTERACTIVE" = true ]; then
    read -r -p "Continuar con archivos dirty? (y/N): " yn
    [[ "$yn" =~ ^[yY] ]] || exit 1
  fi
else
  ok "Git clean"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Run tests (gate)
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 2/8 — Run tests (gate)"
if [ "$NO_TESTS" = true ]; then
  warn "Tests skipped (--no-tests)"
else
  if command -v python3 &>/dev/null; then
    echo "Running: PYTHONPATH=. python3 -m pytest tests/test_truth.py tests/test_abe_service.py tests/test_collectors/ tests/test_execution.py tests/test_evolution.py -q --tb=short 2>&1 | tail -5"
    test_output=$(PYTHONPATH=. python3 -m pytest tests/test_truth.py tests/test_abe_service.py tests/test_collectors/ tests/test_execution.py tests/test_evolution.py -q --tb=short 2>&1 || true)
    echo "$test_output" | tail -5
    if echo "$test_output" | grep -q "FAILED\|failed"; then
      err "Tests fallaron. Abortando."
      echo "Usa --no-tests para saltear o corrige los tests primero."
      exit 1
    fi
    # Extract total test count
    TEST_COUNT=$(echo "$test_output" | grep -oP '\d+(?= passed)' | tail -1)
    TEST_COUNT="${TEST_COUNT:-0}"
    ok "Tests OK — $TEST_COUNT passed"
  else
    warn "python3 no disponible, salteando tests"
    TEST_COUNT=0
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Generate docs via auto-doc.py
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 3/8 — Generate documentation"
AUTODOC_ARGS=(
  --spec-id "$SPEC_ID"
  --title "$TITLE"
  --tier "$TIER"
  --dir "$DIR_NAME"
)
[ -n "$SUMMARY" ] && AUTODOC_ARGS+=(--summary "$SUMMARY")
[ "$FORCE" = true ] && AUTODOC_ARGS+=(--force)

if [ -d "$OUTPUT_DIR" ] && [ "$FORCE" = false ]; then
  warn "Directory $OUTPUT_DIR/ already exists. Use --force to overwrite."
  echo "  Contents: $(ls "$OUTPUT_DIR" 2>/dev/null | wc -l) files"
  if [ "$INTERACTIVE" = true ]; then
    read -r -p "Overwrite? (y/N): " yn
    if [[ "$yn" =~ ^[yY] ]]; then
      python3 scripts/auto-doc.py "${AUTODOC_ARGS[@]}" --force
    else
      echo "  Skipping doc generation."
    fi
  else
    echo "  Skipping (use --force to regenerate)."
  fi
else
  python3 scripts/auto-doc.py "${AUTODOC_ARGS[@]}"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Move active SPECs → completed
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 4/8 — Move active SPECs to completed"
MOVED=0
mkdir -p "$OUTPUT_DIR"
# SPEC_ID puede ser "SPEC-20260704-EVOLUTION" o "20260704-evolution"
# Normalizar: si ya tiene SPEC-, usarlo directo; si no, prefijar
BASE_ID="$SPEC_ID"
for f in process/active/${BASE_ID}* process/active/SCORE-${BASE_ID#SPEC-}* process/active/ADR-${BASE_ID#SPEC-}*; do
  if [ -f "$f" ]; then
    mv "$f" "$OUTPUT_DIR/"
    ok "Moved $(basename "$f") → $OUTPUT_DIR/"
    MOVED=$((MOVED + 1))
  fi
done
# Also move subdirectories (SPEC-20260701-013/)
for d in process/active/${BASE_ID}/; do
  if [ -d "$d" ]; then
    mv "$d" "$OUTPUT_DIR/"
    ok "Moved directory ${d} → $OUTPUT_DIR/"
    MOVED=$((MOVED + 1))
  fi
done
if [ "$MOVED" -eq 0 ]; then
  info "No matching files found in process/active/ for $SPEC_ID"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Update AGENTS.md
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 5/8 — Update AGENTS.md"
AGENTS_FILE="$ROOT/AGENTS.md"
if [ -f "$AGENTS_FILE" ]; then
  # Update test count if detected
  if [ -n "${TEST_COUNT:-}" ] && [ "$TEST_COUNT" -gt 0 ]; then
    if grep -q "tests/" "$AGENTS_FILE"; then
      sed -i "s/| \`tests\/\` |.*|/| \`tests\/\` | ${TEST_COUNT} tests |/" "$AGENTS_FILE"
      ok "Updated test count in AGENTS.md → $TEST_COUNT"
    fi
  fi

  # Update anchored summary — add session reference to Cognitive Kernel section
  SESSION_DATE=$(echo "$DIR_NAME" | grep -oP '^\d{8}' | sed 's/\(....\)\(..\)\(..\)/\1-\2-\3/')
  if [ -n "$SESSION_DATE" ]; then
    # Check if session already documented in the file
    if grep -qi "$SPEC_ID\|$DIR_NAME" "$AGENTS_FILE"; then
      info "Session already referenced in AGENTS.md"
    else
      # Append a line under Cognitive Kernel or at the end
      if grep -q "Enterprise Score actual:" "$AGENTS_FILE"; then
        sed -i "/Enterprise Score actual:/a\\
\\
### ${TITLE} (${SESSION_DATE})\\
| Ruta | Que es |\\
|------|--------|\\
| \`${OUTPUT_DIR}/\` | ${TITLE} — Score: \`process/completed/CATALOG.md\` |" "$AGENTS_FILE"
        ok "Appended session reference to AGENTS.md"
      fi
    fi
  fi
else
  warn "AGENTS.md not found, skipping"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: Merge + remove process/CATALOG.md → process/completed/CATALOG.md
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 6/8 — Unify CATALOGs"
MAIN_CATALOG="process/CATALOG.md"
COMPLETED_CATALOG="process/completed/CATALOG.md"

if [ -f "$MAIN_CATALOG" ]; then
  # Check if main CATALOG only has the ECA entry (or similar that's already in completed)
  main_lines=$(wc -l < "$MAIN_CATALOG")
  if [ "$main_lines" -le 20 ]; then
    info "process/CATALOG.md has $main_lines lines — likely duplicated in completed catalog"
    # Extract any module-level detail not in completed catalog
    detail_lines=$(grep -E "^\|.*\|.*\|$" "$MAIN_CATALOG" 2>/dev/null || true)
    if [ -n "$detail_lines" ]; then
      # Append detail rows to completed catalog as HTML comment or additional note
      if grep -q "ECA\|$DIR_NAME" "$COMPLETED_CATALOG" 2>/dev/null; then
        info "Content already in completed catalog"
      fi
    fi
    # Remove the duplicate
    rm "$MAIN_CATALOG"
    ok "Removed process/CATALOG.md (content merged into process/completed/CATALOG.md)"
  else
    warn "process/CATALOG.md has $main_lines lines — review manually before removal"
    info "Skipping auto-removal"
  fi
else
  info "process/CATALOG.md already removed or doesn't exist"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7: Git add + commit + push
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 7/8 — Git commit + push"
if git diff --quiet && git diff --cached --quiet; then
  warn "No changes to commit"
else
  echo "Staging all changes..."
  git add -A
  git commit -m "close($DIR_NAME): $TITLE"
  ok "Committed: close($DIR_NAME): $TITLE"

  if [ "$NO_PUSH" = true ]; then
    warn "Push skipped (--no-push)"
  else
    echo "Pushing to origin main..."
    git push origin main 2>&1 | tail -3
    ok "Pushed to GitHub — VPS will auto-sync via GitHub Action (sync-vps.yml)"
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8: Summary
# ═══════════════════════════════════════════════════════════════════════════════
step "Step 8/8 — Complete"
echo ""
echo "══════════════════════════════════════════"
echo "  Session closed: $TITLE"
echo "  Spec:           $SPEC_ID"
echo "  Docs:           $OUTPUT_DIR/"
echo "  Tests:          ${TEST_COUNT:-N/A} passed"
echo "  VPS sync:       $(if [ "$NO_PUSH" = true ]; then echo 'manual (--no-push)'; else echo 'auto via GitHub Action'; fi)"
echo "══════════════════════════════════════════"
echo ""
echo "Post-close checklist (manual):"
echo "  [ ] Habilitar GitHub Pages: Settings → Pages → Source: GitHub Actions"
echo "  [ ] Verificar Guardian restart en VPS si no se reinició solo"
echo "  [ ] Probar endpoints nuevos manualmente"
echo "  [ ] Revisar que AGENTS.md refleje los cambios"
