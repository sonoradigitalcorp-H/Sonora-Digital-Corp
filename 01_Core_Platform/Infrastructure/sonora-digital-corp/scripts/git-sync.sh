#!/usr/bin/env bash
# git-sync.sh — Pre-session Git Sync Gate (GIT-006)
#
# Se corre ANTES de empezar a trabajar para asegurar que el repo
# está sincronizado con origin/main. Previene divergencias como
# la del 2026-07-08 (Luis Daniel + Noel en paralelo).
#
# Uso:
#   ./scripts/git-sync.sh          # Modo interactivo (pregunta si hay conflicto)
#   ./scripts/git-sync.sh --force  # Auto-merge sin preguntar
#   ./scripts/git-sync.sh --status # Solo mostrar estado, no hacer nada
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }

FORCE=false
STATUS_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)    FORCE=true; shift ;;
    --status)   STATUS_ONLY=true; shift ;;
    --help|-h)
      echo "Uso: ./scripts/git-sync.sh [--force|--status]"
      echo "  --force   Auto-merge sin preguntar"
      echo "  --status  Solo mostrar estado, no hacer nada"
      exit 0
      ;;
    *) err "Arg unknown: $1"; exit 1 ;;
  esac
done

echo ""
echo "══════════════════════════════════════════"
echo "  Git Sync Gate — Pre-Session Check"
echo "══════════════════════════════════════════"

# ─── 1. Check for stuck rebase ────────────────────────────────────────────────
info "1/5 — Checking for stuck rebase..."
if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
  err "REBASE IN PROGRESS (left from previous session)"
  echo ""
  echo "  This is what caused the Jul 8 incident. Resolve it:"
  echo "    git rebase --abort   # cancel rebase"
  echo "    git rebase --continue # finish rebase"
  echo ""
  if [ "$FORCE" = true ] || [ "$STATUS_ONLY" = true ]; then
    err "Rebase stuck. Run git rebase --abort manually."
    exit 1
  fi
  read -r -p "  Abort rebase? (Y/n): " yn
  if [[ ! "$yn" =~ ^[nN] ]]; then
    git rebase --abort && ok "Rebase aborted."
  else
    err "Cannot proceed with rebase in progress. Fix it first."
    exit 1
  fi
else
  ok "No stuck rebase."
fi

# ─── 2. Check for in-progress merge ───────────────────────────────────────────
info "2/5 — Checking for in-progress merge..."
if [ -f ".git/MERGE_HEAD" ]; then
  err "MERGE IN PROGRESS"
  echo "  Finish or abort the merge:"
  echo "    git merge --continue"
  echo "    git merge --abort"
  exit 1
else
  ok "No merge in progress."
fi

# ─── 3. Check for dirty files ────────────────────────────────────────────────
info "3/5 — Checking working tree..."
DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$DIRTY" -gt 0 ]; then
  warn "$DIRTY dirty file(s):"
  git status --short
  echo ""
  if [ "$STATUS_ONLY" = true ]; then
    warn "Dirty files exist."
  elif [ "$FORCE" = true ]; then
    info "Auto-stashing dirty files..."
    git stash push -m "auto-stash before git-sync $(date +%Y-%m-%d_%H%M%S)"
    ok "Stashed."
  else
    read -r -p "  Stash them and continue? (Y/n): " yn
    if [[ ! "$yn" =~ ^[nN] ]]; then
      git stash push -m "auto-stash before git-sync $(date +%Y-%m-%d_%H%M%S)"
      ok "Stashed."
    else
      warn "Proceeding with dirty files (not recommended)."
    fi
  fi
else
  ok "Working tree clean."
fi

# ─── 4. Fetch and check divergence ────────────────────────────────────────────
info "4/5 — Fetching origin..."
git fetch origin 2>/dev/null || { err "Cannot fetch origin. Check SSH/network."; exit 1; }

BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null)

echo ""
echo "  Local:  $(git rev-parse --short HEAD) ($(git log --oneline -1 --format=%s))"
echo "  Remote: $(git rev-parse --short origin/main) ($(git log --oneline -1 --format=%s origin/main))"
echo "  Ahead:  $AHEAD commits"
echo "  Behind: $BEHIND commits"
echo ""

if [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -eq 0 ]; then
  ok "In sync with origin/main. Ready to work."
elif [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -gt 0 ]; then
  # ─── DIVERGENCE ──────────────────────────────────────────────────────────
  warn "⚠️  DIVERGENCE DETECTED"
  echo "  You are ahead by $AHEAD commits AND behind by $BEHIND."
  echo "  This means you AND someone else (probably Noel) made commits."
  echo ""

  if [ "$STATUS_ONLY" = true ]; then
    err "Divergence detected. Run git-sync.sh without --status to resolve."
    exit 1
  fi

  echo "  Options:"
  echo "    1) Merge (recommended) — preserves both histories"
  echo "    2) Rebase — rewrites your commits on top of origin (risky)"
  echo "    3) Abort — do nothing, fix manually"
  echo ""

  if [ "$FORCE" = true ]; then
    info "Auto-merging (--force)..."
    git merge origin/main --no-edit || {
      err "Merge conflict! Resolve manually:"
      echo "  git merge --abort"
      echo "  git merge origin/main  # and fix conflicts"
      exit 1
    }
    ok "Merge successful."
  else
    read -r -p "  Choose (1/2/3) [1]: " choice
    choice="${choice:-1}"
    case "$choice" in
      1)
        info "Merging origin/main into local..."
        git merge origin/main --no-edit || {
          err "Merge conflict! Resolve manually."
          exit 1
        }
        ok "Merge successful."
        ;;
      2)
        warn "Rebase selected — this rewrites history!"
        read -r -p "  Are you sure? (y/N): " sure
        if [[ "$sure" =~ ^[yY] ]]; then
          git rebase origin/main || {
            err "Rebase conflict! Run: git rebase --abort"
            exit 1
          }
          ok "Rebase successful."
        else
          err "Aborted."
          exit 1
        fi
        ;;
      3)
        err "Aborted by user. Fix divergence manually."
        exit 1
        ;;
    esac
  fi
elif [ "$BEHIND" -gt 0 ]; then
  # ─── BEHIND ONLY ────────────────────────────────────────────────────────
  info "Behind by $BEHIND commits. Syncing..."
  if [ "$STATUS_ONLY" = true ]; then
    info "You are behind origin/main by $BEHIND commits."
    info "Run 'git pull' or 'git merge origin/main' to sync."
  else
    git merge origin/main --ff-only --no-edit 2>/dev/null || {
      warn "Fast-forward failed (divergent?). Trying merge..."
      git merge origin/main --no-edit
    }
    ok "Synced with origin/main."
  fi
elif [ "$AHEAD" -gt 0 ]; then
  # ─── AHEAD ONLY ─────────────────────────────────────────────────────────
  warn "Ahead by $AHEAD commits — they haven't been pushed yet."
  if [ "$STATUS_ONLY" = true ]; then
    info "You have $AHEAD unpushed commits. Push when ready via close-session.sh."
  else
    echo "  You can work, but remember to push at the end:"
    echo "    git push origin main"
    echo "  Or use: ./scripts/close-session.sh"
  fi
fi

# ─── 5. Pop stash if we stashed earlier ────────────────────────────────────────
if [ "$DIRTY" -gt 0 ] && [ "$STATUS_ONLY" = false ] && [ "$FORCE" = true ]; then
  STASH_COUNT=$(git stash list 2>/dev/null | wc -l)
  if [ "$STASH_COUNT" -gt 0 ]; then
    STASH_MSG=$(git stash list --format="%s" 2>/dev/null | head -1)
    if echo "$STASH_MSG" | grep -q "auto-stash before git-sync"; then
      info "Popping auto-stash..."
      git stash pop 2>/dev/null || warn "Stash pop failed (manual: git stash pop)."
    fi
  fi
fi

echo ""
echo "══════════════════════════════════════════"
if [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -eq 0 ]; then
  echo "  ✅ Git Sync Gate PASSED — Ready to work"
elif [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -eq 0 ]; then
  echo "  ⚠️  Git Sync Gate PASSED — You have unpushed commits"
else
  echo "  ✅ Git Sync Gate COMPLETE"
fi
echo "══════════════════════════════════════════"
echo ""
