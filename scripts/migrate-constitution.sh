#!/usr/bin/env bash
# migrate-constitution.sh — Migrate truth/ → constitution/ (HAS-001)
# Idempotent. Safe to run multiple times.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*"; }

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

$DRY_RUN && info "DRY RUN — no files will be changed"

# ─── Step 1: Create constitution/ directory ────────────────────────────────────
if $DRY_RUN; then
  info "[dry] mkdir -p constitution/"
else
  mkdir -p constitution/
  info "Created constitution/"
fi

# ─── Step 2: Copy existing truth/ files with mapping ──────────────────────────
declare -A MAP=(
  ["00-index.yaml"]="00-index.yaml"
  ["10-principles.yaml"]="10-principles.yaml"
  ["20-architecture.yaml"]="30-architecture.yaml"
  ["30-security.yaml"]="40-security.yaml"
  ["40-infrastructure.yaml"]="30-architecture.yaml"
  ["45-execution.yaml"]="90-governance.yaml"
  ["50-coding.yaml"]="20-engineering.yaml"
  ["60-git.yaml"]="20-engineering.yaml"
  ["70-documentation.yaml"]="20-engineering.yaml"
  ["80-operations.yaml"]="90-governance.yaml"
  ["85-compliance.yaml"]="90-governance.yaml"
  ["90-learned.yaml"]="90-governance.yaml"
)

for src in "${!MAP[@]}"; do
  dst="${MAP[$src]}"
  if [ -f "truth/$src" ]; then
    if $DRY_RUN; then
      info "[dry] cp truth/$src → constitution/$dst (append)"
    else
      # Append content to target (merge, don't overwrite)
      echo "" >> "constitution/$dst" 2>/dev/null || true
      echo "# --- merged from truth/$src ---" >> "constitution/$dst"
      cat "truth/$src" >> "constitution/$dst"
      info "Merged truth/$src → constitution/$dst"
    fi
  fi
done

# ─── Step 3: Create new skeleton files ────────────────────────────────────────
NEW_DOMAINS=(
  "01-mission.yaml:1"
  "02-vision.yaml:1"
  "50-quality.yaml:2"
  "60-agents.yaml:2"
  "70-memory.yaml:3"
  "80-events.yaml:3"
  "100-cost.yaml:3"
  "110-brand.yaml:4"
  "120-ux.yaml:4"
  "130-ethics.yaml:4"
)

for entry in "${NEW_DOMAINS[@]}"; do
  file="${entry%%:*}"
  level="${entry##*:}"
  domain="${file#*-}"
  domain="${domain%.yaml}"

  if [ ! -f "constitution/$file" ]; then
    if $DRY_RUN; then
      info "[dry] create constitution/$file (domain=$domain, level=$level)"
    else
      cat > "constitution/$file" << EOF
version: 1
domain: $domain
updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
level: $level
rules: []
EOF
      info "Created constitution/$file"
    fi
  else
    info "constitution/$file already exists, skipping"
  fi
done

# ─── Step 4: Create backward-compat symlink ───────────────────────────────────
if [ ! -L "truth" ] && [ -d "truth" ]; then
  if $DRY_RUN; then
    info "[dry] mv truth/ truth.bak/ && ln -sf constitution/ truth/"
  else
    warn "Creating backup: truth.bak/"
    cp -r truth/ truth.bak/
    rm -rf truth/
    ln -sf constitution/ truth
    info "Symlink created: truth/ → constitution/"
    info "Backup saved: truth.bak/ (remove after 1 month of no errors)"
  fi
elif [ -L "truth" ]; then
  info "truth/ is already a symlink"
fi

# ─── Step 5: Update index ─────────────────────────────────────────────────────
if $DRY_RUN; then
  info "[dry] update constitution/00-index.yaml with new file list"
else
  cat > "constitution/00-index.yaml" << EOF
version: 1
domain: index
updated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
description: "Hermes Constitution — single source of organizational truth"
files:
  - file: "00-index.yaml"
    domain: index
    level: 0
    description: "Catalog and versioning of constitution files"
  - file: "01-mission.yaml"
    domain: mission
    level: 0
    description: "Mission statement, north star, purpose"
  - file: "02-vision.yaml"
    domain: vision
    level: 0
    description: "Long-term vision and success criteria"
  - file: "10-principles.yaml"
    domain: principles
    level: 0
    description: "Immutable principles — never change"
  - file: "20-engineering.yaml"
    domain: engineering
    level: 2
    description: "Engineering standards, methodology, code conventions"
  - file: "30-architecture.yaml"
    domain: architecture
    level: 1
    description: "Architectural decisions, patterns, network policies"
  - file: "40-security.yaml"
    domain: security
    level: 1
    description: "Secrets, encryption, access, compliance"
  - file: "50-quality.yaml"
    domain: quality
    level: 2
    description: "Quality standards, test coverage, linting"
  - file: "60-agents.yaml"
    domain: agents
    level: 2
    description: "Agent behavior rules, capability boundaries"
  - file: "70-memory.yaml"
    domain: memory
    level: 3
    description: "Memory policies, retention, privacy"
  - file: "80-events.yaml"
    domain: events
    level: 3
    description: "Event schemas, required fields, catalog"
  - file: "90-governance.yaml"
    domain: governance
    level: 1
    description: "Constitution Engine gates, policies, audits, lessons"
  - file: "100-cost.yaml"
    domain: cost
    level: 3
    description: "Cost policies, budgets, model routing"
  - file: "110-brand.yaml"
    domain: brand
    level: 4
    description: "Brand guidelines, tone, visual identity"
  - file: "120-ux.yaml"
    domain: ux
    level: 4
    description: "UX principles, Orb states, interaction rules"
  - file: "130-ethics.yaml"
    domain: ethics
    level: 4
    description: "Ethical boundaries, content policies"
EOF
  info "Updated constitution/00-index.yaml"
fi

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
if $DRY_RUN; then
  echo "  DRY RUN — no changes made"
else
  echo "  ✅ Constitution migration complete"
fi
echo "══════════════════════════════════════════"
echo ""
echo "  Files in constitution/: $(find constitution/ -name '*.yaml' -type f | wc -l)"
echo "  Backup: truth.bak/"
echo "  Symlink: truth/ → constitution/ (if no errors, run again to create)"
echo ""
echo "  Next steps:"
echo "    1. Review merged files in constitution/"
echo "    2. Run: python3 scripts/validate-constitution.py"
echo "    3. Remove truth.bak/ after 1 month"
