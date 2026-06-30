#!/bin/bash
# Process Pipeline — Automates lifecycle for specs, scores, events, ADRs, lecciones
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROCESS_DIR="$BASE_DIR/process"
TEMPLATES="$PROCESS_DIR/templates"

cmd="${1:-help}"

case "$cmd" in
  spec-new)
    # Creates a new spec from template
    title="$2"
    if [ -z "$title" ]; then
      echo "Usage: $0 spec-new \"Title of the spec\""
      exit 1
    fi
    id="SPEC-$(date +%Y%m%d)-$(ls "$PROCESS_DIR/active" 2>/dev/null | wc -l | xargs printf '%03d')"
    slug="$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
    cat "$TEMPLATES/SPEC.md" \
      | sed "s/{title}/$title/g" \
      | sed "s/{SPEC-ID}/$id/g" \
      | sed "s/{YYYY-MM-DD}/$(date +%Y-%m-%d)/g" \
      | sed "s/{autor}/OpenClaw/g" \
      > "$PROCESS_DIR/active/$id-$slug.md"
    mkdir -p "$PROCESS_DIR/active/gherkin"
    cp "$TEMPLATES/GHERKIN.md" "$PROCESS_DIR/active/gherkin/$id.feature"
    echo "Created: $PROCESS_DIR/active/$id-$slug.md"
    echo "Created: $PROCESS_DIR/active/gherkin/$id.feature"
    ;;

  score)
    # Calculates enterprise score and compares against spec requirement
    spec_file="$2"
    if [ -z "$spec_file" ]; then
      "$BASE_DIR/scripts/enterprise-score.sh"
      exit 0
    fi
    "$BASE_DIR/scripts/enterprise-score.sh"
    score=$("$BASE_DIR/scripts/enterprise-score.sh" 2>/dev/null | grep "Enterprise Score:" | grep -oE '[0-9]+' | head -1)
    echo "Score: $score/100 (threshold: 60)"
    if [ "$score" -ge 60 ] 2>/dev/null; then
      echo "✓ PASS — Score meets threshold"
    else
      echo "✗ FAIL — Score below 60. Rejected or human override required."
      exit 1
    fi
    ;;

  complete)
    # Moves active spec to completed with all artifacts
    spec_file="$2"
    if [ -z "$spec_file" ]; then
      echo "Usage: $0 complete <spec-file>"
      exit 1
    fi
    spec_name="$(basename "$spec_file" .md)"
    completed_dir="$PROCESS_DIR/completed/$(date +%Y%m%d)-$spec_name"
    mkdir -p "$completed_dir"
    cp "$spec_file" "$completed_dir/SPEC.md"
    if [ -f "$PROCESS_DIR/active/SCORE.md" ]; then
      cp "$PROCESS_DIR/active/SCORE.md" "$completed_dir/"
    fi
    if [ -f "$PROCESS_DIR/active/ADR.md" ]; then
      cp "$PROCESS_DIR/active/ADR.md" "$completed_dir/"
    fi
    if [ -f "$PROCESS_DIR/active/LECCION.md" ]; then
      cp "$PROCESS_DIR/active/LECCION.md" "$completed_dir/"
    fi
    # Emit completion event
    "$BASE_DIR/scripts/process-pipeline.sh" event "spec_completed" "{\"spec\":\"$spec_name\"}"
    echo "Completed spec moved to: $completed_dir"
    ;;

  event)
    # Logs an enterprise event
    event_name="$2"
    payload="$3"
    events_dir="$BASE_DIR/state/logs"
    mkdir -p "$events_dir"
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "{\"event\":\"$event_name\",\"timestamp\":\"$ts\",\"payload\":$payload}" >> "$events_dir/events.jsonl"
    echo "Event logged: $event_name"
    ;;

  adr-new)
    # Creates a new ADR from template
    title="$2"
    spec_id="$3"
    if [ -z "$title" ]; then
      echo "Usage: $0 adr-new \"Title\" SPEC-XXX"
      exit 1
    fi
    id="ADR-$(date +%Y%m%d)-$(ls "$PROCESS_DIR/active" 2>/dev/null | wc -l | xargs printf '%03d')"
    cat "$TEMPLATES/ADR.md" \
      | sed "s/{title}/$title/g" \
      | sed "s/{SPEC-ID}/$spec_id/g" \
      | sed "s/ADR-{YYYYMMDD}-{NNN}/$id/g" \
      | sed "s/{YYYY-MM-DD}/$(date +%Y-%m-%d)/g" \
      > "$PROCESS_DIR/active/$id.md"
    echo "Created: $PROCESS_DIR/active/$id.md"
    ;;

  leccion-new)
    # Creates a leccion from template
    spec_id="$2"
    if [ -z "$spec_id" ]; then
      echo "Usage: $0 leccion-new SPEC-XXX"
      exit 1
    fi
    cat "$TEMPLATES/LECCION.md" \
      | sed "s/{SPEC-ID}/$spec_id/g" \
      | sed "s/{YYYY-MM-DD}/$(date +%Y-%m-%d)/g" \
      > "$PROCESS_DIR/active/LECCION-$spec_id.md"
    echo "Created: $PROCESS_DIR/active/LECCION-$spec_id.md"
    ;;

  gherkin-new)
    # Creates gherkin stub
    spec_id="$2"
    if [ -z "$spec_id" ]; then
      echo "Usage: $0 gherkin-new SPEC-XXX"
      exit 1
    fi
    mkdir -p "$PROCESS_DIR/active/gherkin"
    cp "$TEMPLATES/GHERKIN.md" "$PROCESS_DIR/active/gherkin/$spec_id.feature"
    echo "Created: $PROCESS_DIR/active/gherkin/$spec_id.feature"
    ;;

  status)
    echo "=== Pipeline Status ==="
    echo "Active specs:"
    ls "$PROCESS_DIR/active/"*.md 2>/dev/null | head -5 || echo "  (none)"
    echo ""
    echo "Completed specs:"
    ls -d "$PROCESS_DIR/completed/"*/ 2>/dev/null | head -5 || echo "  (none)"
    echo ""
    echo "Events logged:"
    wc -l "$BASE_DIR/state/logs/events.jsonl" 2>/dev/null | awk '{print "  " $1 " events"}'
    echo ""
    "$BASE_DIR/scripts/enterprise-score.sh" 2>/dev/null | head -1 || echo "  Score: N/A"
    ;;

  help|*)
    echo "Pipeline Commands:"
    echo "  spec-new <title>         — Create a new spec from template"
    echo "  score [spec-file]        — Calculate enterprise score"
    echo "  complete <spec-file>     — Move spec to completed with all artifacts"
    echo "  event <name> <json>      — Log an enterprise event"
    echo "  adr-new <title> <spec>   — Create a new ADR from template"
    echo "  leccion-new <spec>       — Create lecciones template"
    echo "  gherkin-new <spec>       — Create Gherkin feature file"
    echo "  status                   — Show pipeline state"
    ;;
esac
