"""Learning Kernel — extrae heurísticas desde LECCION.md y acumula en truth/90-learned.yaml [FR5-FR7]"""
import json
import os
import re
import sys
import yaml
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
COMPLETED = REPO / "process" / "completed"
TRUTH_LEARNED = REPO / "truth" / "90-learned.yaml"


def extract_heuristics():
    """Extrae heurísticas de todas las LECCION.md"""
    heuristics = []
    errors_seen = defaultdict(list)
    patterns_seen = defaultdict(list)

    for leccion_file in sorted(COMPLETED.rglob("LECCION.md")):
        spec_dir = leccion_file.parent.name
        text = leccion_file.read_text()

        # Extraer "Qué falló" section
        fallo_match = re.search(r"## Qué falló\s*\n(.*?)(?=##|\Z)", text, re.DOTALL)
        if fallo_match:
            items = re.findall(r"-\s*\*\*(.*?)\*\*", fallo_match.group(1))
            for item in items:
                errors_seen[item].append(spec_dir)

        # Extraer "Qué aprender" section
        learn_match = re.search(r"## Qué aprender para la próxima\s*\n(.*?)(?=##|\Z)", text, re.DOTALL)
        if learn_match:
            items = re.findall(r"\d+\.\s*(.*?)(?=\n\d+\.|\n\n|\Z)", learn_match.group(1), re.DOTALL)
            for item in items:
                item = item.strip()
                if item:
                    patterns_seen[item].append(spec_dir)

        # Extraer "Próximos pasos"
        next_match = re.search(r"## Próximos pasos\s*\n(.*?)(?=##|\Z)", text, re.DOTALL)
        if next_match:
            items = re.findall(r"-\s*\*?\*?(.*?)\*?", next_match.group(1))
            for item in items:
                item = item.strip()
                if item and len(item) > 10:
                    heuristics.append({"type": "next_step", "text": item, "source": spec_dir})

    # Convertir errores en heurísticas
    for error, sources in sorted(errors_seen.items(), key=lambda x: -len(x[1])):
        heuristics.append({
            "type": "error_pattern",
            "text": error,
            "count": len(sources),
            "sources": sources,
            "first_seen": sources[0],
            "last_seen": sources[-1]
        })

    for pattern, sources in sorted(patterns_seen.items(), key=lambda x: -len(x[1])):
        heuristics.append({
            "type": "lesson",
            "text": pattern[:200],
            "count": len(sources),
            "sources": sources,
        })

    return heuristics


def update_truth_learned(heuristics):
    """Actualiza truth/90-learned.yaml con heurísticas acumuladas"""
    if not TRUTH_LEARNED.exists():
        rules = []
    else:
        with open(TRUTH_LEARNED) as f:
            data = yaml.safe_load(f) or {}
        rules = data.get("rules", [])

    existing_ids = {r["id"] for r in rules if "id" in r}
    new_rules = []

    for h in heuristics:
        hid = f"LRN-{len(rules) + len(new_rules) + 1:03d}"
        if hid in existing_ids:
            continue

        rule = {
            "id": hid,
            "type": h["type"],
            "description": h["text"],
            "source": h.get("sources", [h.get("source", "unknown")])[-1],
            "count": h.get("count", 1),
            "learned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        new_rules.append(rule)

    if not new_rules:
        return {"status": "no_new", "total_rules": len(rules)}

    all_rules = rules + new_rules

    data = {
        "version": 1,
        "domain": "learned",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": "Heurísticas aprendidas — autogenerado desde LECCION.md. Siempre override por niveles superiores.",
        "rules": all_rules
    }

    with open(TRUTH_LEARNED, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return {"status": "updated", "new_rules": len(new_rules), "total_rules": len(all_rules)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Learning Kernel")
    parser.add_argument("--dry-run", action="store_true", help="Show heuristics without writing")
    args = parser.parse_args()

    print("Extracting heuristics from LECCION.md files...", file=sys.stderr)
    heuristics = extract_heuristics()
    print(f"Found {len(heuristics)} heuristics", file=sys.stderr)

    if args.dry_run:
        for h in heuristics:
            print(f"  [{h['type']}] {h['text'][:80]}... ({h.get('count', 1)}x)")
        return

    result = update_truth_learned(heuristics)
    print(json.dumps(result))

    # Emit event
    try:
        import subprocess
        subprocess.run(
            [sys.executable, str(REPO / "scripts" / "emit-event.py"),
             "--event", "knowledge.indexed",
             "--kernel", "learning",
             "--agent", "learning-kernel",
             "--subject-type", "knowledge",
             "--subject-id", "90-learned.yaml",
             "--payload", json.dumps(result)],
            capture_output=True, timeout=5
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
