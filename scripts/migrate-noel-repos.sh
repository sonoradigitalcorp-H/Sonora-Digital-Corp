#!/bin/bash
# =============================================================================
# MIGRACIÓN NOEL → MONOREPO SDC
# =============================================================================
# Ejecutar desde la máquina de Noel o donde tenga acceso a GitHub.
# Requiere: git, jq (opcional)
#
# Uso:
#   chmod +x migrate-noel-repos.sh
#   ./migrate-noel-repos.sh
# =============================================================================

set -e

MONOREPO_URL="https://github.com/sonoradigitalcorp-H/Sonora-Digital-Corp.git"
NOEL_ACCOUNT="sonoradigitalcorp-H"
REPOS_TO_MIGRATE=(
  "abe-music"
  "productos"
  "productos-hector-rubio"
  "productos-javier-arvayo"
  "productos-jesus-urquijo"
  "reporte-ecosistema"
)

WORK_DIR="/tmp/sdc-migration-$(date +%s)"
LOG_FILE="$WORK_DIR/migration.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[$(date +%H:%M:%S)] WARN:${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[$(date +%H:%M:%S)] ERROR:${NC} $1" | tee -a "$LOG_FILE"; exit 1; }

# ── 1. Preparar directorio de trabajo ────────────────────────────────────────
log "📁 Creando directorio de trabajo: $WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# ── 2. Clonar monorepo principal ─────────────────────────────────────────────
log "📦 Clonando monorepo principal..."
git clone --depth 1 "$MONOREPO_URL" monorepo 2>/dev/null || error "No se pudo clonar el monorepo. ¿Tienes acceso?"
MONOREPO="$WORK_DIR/monorepo"

# ── 3. Clonar repos de Noel ──────────────────────────────────────────────────
log "📦 Clonando repos de Noel..."
for repo in "${REPOS_TO_MIGRATE[@]}"; do
  log "  → Clonando $repo..."
  git clone --depth 1 "https://github.com/$NOEL_ACCOUNT/$repo.git" "noel/$repo" 2>/dev/null || {
    warn "No se pudo clonar $repo (¿es privado?), saltando..."
    continue
  }
done

# ── 4. Migrar contenido ─────────────────────────────────────────────────────
log "🔄 Migrando contenido al monorepo..."

# abe-music → products/abe-music/
if [ -d "noel/abe-music" ]; then
  log "  → abe-music/ → products/abe-music/"
  cp -n noel/abe-music/*.html "$MONOREPO/products/abe-music/" 2>/dev/null || true
  cp -n noel/abe-music/*.css "$MONOREPO/products/abe-music/" 2>/dev/null || true
  cp -n noel/abe-music/*.js "$MONOREPO/products/abe-music/" 2>/dev/null || true
fi

# productos → products/
if [ -d "noel/productos" ]; then
  log "  → productos/ → products/"
  # Copiar directorios
  for dir in abe-music booking chatbot landing-artista; do
    if [ -d "noel/productos/$dir" ]; then
      mkdir -p "$MONOREPO/products/$dir"
      cp -rn "noel/productos/$dir/"* "$MONOREPO/products/$dir/" 2>/dev/null || true
    fi
  done
  # Copiar archivos sueltos
  cp -n noel/productos/*.html "$MONOREPO/products/" 2>/dev/null || true
  cp -n noel/productos/*.sh "$MONOREPO/products/" 2>/dev/null || true
  cp -n noel/productos/*.md "$MONOREPO/products/" 2>/dev/null || true
fi

# productos-{artista} → products/booking/{artista}/
for artist_repo in productos-hector-rubio productos-javier-arvayo productos-jesus-urquijo; do
  if [ -d "noel/$artist_repo" ]; then
    artist_name=$(echo "$artist_repo" | sed 's/productos-//')
    log "  → $artist_repo/ → products/booking/$artist_name/"
    mkdir -p "$MONOREPO/products/booking/$artist_name"
    cp -n "noel/$artist_repo/"* "$MONOREPO/products/booking/$artist_name/" 2>/dev/null || true
  fi
done

# reporte-ecosistema → products/
if [ -d "noel/reporte-ecosistema" ]; then
  log "  → reporte-ecosistema/ → products/"
  cp -n noel/reporte-ecosistema/*.html "$MONOREPO/products/" 2>/dev/null || true
fi

# ── 5. Resumen de cambios ────────────────────────────────────────────────────
log "📊 Resumen de cambios:"
cd "$MONOREPO"
CHANGES=$(git status --short | wc -l)
if [ "$CHANGES" -gt 0 ]; then
  git status --short | head -20
  if [ "$CHANGES" -gt 20 ]; then
    warn "... y $((CHANGES - 20)) archivos más"
  fi
  
  # ── 6. Commit y push ─────────────────────────────────────────────────────
  log "💾 Haciendo commit..."
  git add -A
  git commit -m "feat: migración Noel — productos, abe-music, artistas, reporte

Migrado desde repos separados de Noel:
- abe-music (landing pages artistas)
- productos (booking, chatbot, landing-artista)
- productos-hector-rubio (booking page)
- productos-javier-arvayo (booking page)
- productos-jesus-urquijo (booking page)
- reporte-ecosistema (reporte HTML)"
  
  log "🚀 Haciendo push a origin/main..."
  git push origin main
  
  log "✅ ¡Migración completada! $CHANGES archivos migrados."
else
  log "✅ No hay cambios — todo ya está en el monorepo."
fi

# ── 7. Cleanup ───────────────────────────────────────────────────────────────
log "🧹 Limpiando directorio temporal..."
cd /
rm -rf "$WORK_DIR"

log "📋 Log guardado en: $LOG_FILE"
log "🎉 ¡Listo! El monorepo está actualizado."
