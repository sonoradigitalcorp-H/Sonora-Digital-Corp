#!/usr/bin/env bash
# skill-creator — Genera un nuevo skill desde SKILL-TEMPLATE.md
# Usage: skill-creator <name> <category> [description]
set -euo pipefail

NAME="${1:?Usage: skill-creator <name> <category> [description]}"
CATEGORY="${2:-general}"
DESCRIPTION="${3:-}"

SDC_HOME="${SDC_HOME:-$HOME/sonora-digital-corp}"
SKILL_DIR="$SDC_HOME/skills/$NAME"

if [ -d "$SKILL_DIR" ]; then
    echo "Error: Skill '$NAME' already exists at $SKILL_DIR"
    exit 1
fi

TEMPLATE="$SDC_HOME/skills/SKILL-TEMPLATE.md"
if [ ! -f "$TEMPLATE" ]; then
    echo "Error: SKILL-TEMPLATE.md not found at $TEMPLATE"
    exit 1
fi

mkdir -p "$SKILL_DIR"

DATE=$(date +%Y-%m-%d)

cat > "$SKILL_DIR/SKILL.md" << SKILLEOF
# Skill: $NAME

**Version**: 1.0.0
**Created**: $DATE
**Category**: $CATEGORY

## Business Objective

${DESCRIPTION:-To be defined.}

## Inputs

- Input 1: ...

## Outputs

- Output 1: ...

## Events

- \`$NAME.started\`
- \`$NAME.completed\`
- \`$NAME.failed\`

## Dependencies

- ...

## Tools

- ...

## Policies

- ...

## Success Metrics

- ...

## Failure Conditions

- ...

## Recovery Procedure

- ...

## Business Value

${DESCRIPTION:+$CATEGORY automation}${DESCRIPTION:-To be quantified.}

## Parent OS

sdc

---

## Validation Checklist

- [ ] Business Objective defined
- [ ] Inputs defined
- [ ] Outputs defined
- [ ] Events defined
- [ ] Dependencies documented
- [ ] Policies defined
SKILLEOF

# Register in meta-registry
if command -v sdc &>/dev/null; then
    cd "$SDC_HOME" && python3 scripts/sync-registry.py > /dev/null 2>&1 || true
fi

echo "✅ Skill '$NAME' created at $SKILL_DIR/SKILL.md"
echo "   Category: $CATEGORY"
echo "   Run 'sdc skill list' to verify"
