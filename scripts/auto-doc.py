#!/usr/bin/env python3
"""Auto-doc: genera documentacion de proceso segun templates y CONDUCT.md.

Uso:
  ./auto-doc.py --spec-id SPEC-20260703-003 --title "Mi Feature" --tier 2 --summary "..."

Modo interactivo:
  Responde preguntas para completar campos.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "process" / "templates"
COMPLETED = ROOT / "process" / "completed"
CATALOG = COMPLETED / "CATALOG.md"
AGENTS = ROOT / "AGENTS.md"

SCORE_METRICS = [
    ("Revenue Impact", "Impacto en ingresos directos o indirectos"),
    ("Scalability", "Capacidad de escalar sin friccion"),
    ("Reusability", "Reusabilidad del resultado en otros contextos"),
    ("Automation Impact", "Reduccion de intervencion manual"),
    ("Knowledge Impact", "Captura de conocimiento que antes era tribal"),
    ("Reliability", "Mejora en estabilidad y predictibilidad"),
    ("Founder Independence", "Reduccion de dependencia del fundador"),
    ("Operational Simplicity", "Simplificacion de operaciones diarias"),
    ("Customer Value", "Valor directo para clientes (ABE Music, etc.)"),
    ("FinOps Efficiency", "Eficiencia de costos de infraestructura"),
]


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def today_compact() -> str:
    return datetime.now().strftime("%Y%m%d")


def generate_spec(args: dict) -> str:
    title = args["title"]
    spec_id = args["spec_id"]
    tier = args.get("tier", "2")
    author = args.get("author", "OpenClaw")
    today_str = today()

    frs = args.get("frs", [f"Implementar {title}"])
    fr_lines = "\n".join(f"| FR{i+1} | {fr} |" for i, fr in enumerate(frs))

    scs = args.get("success_criteria", [])
    sc_lines = "\n".join(f"- [ ] {sc}" for sc in scs)

    edge_cases = args.get("edge_cases", [])
    ec_lines = "\n".join(f"- {ec}" for ec in edge_cases)

    value_driver = args.get("value_driver", SCORE_METRICS[0][0])
    objective = args.get("objective", f"Implementar {title}")
    approach = args.get("approach", "Por definir durante implementacion.")
    dependencies = args.get("dependencies", "- Por definir")
    events_table = args.get("events_table", "| Evento | Cuando |\n|--------|--------|\n| session.start | Inicio de implementacion |\n| spec.completed | Spec completada |")
    kill_criteria = args.get("kill_criteria", "Si el objetivo no es alcanzable en <4h de ejecucion, abortar y re-planificar.")
    scale_criteria = args.get("scale_criteria", "Cuando el impacto justifique automatizacion adicional o migracion a infra dedicada.")

    return f"""# SPEC — {title}

| Campo | Valor |
|-------|-------|
| **ID** | `{spec_id}` |
| **Fecha** | {today_str} |
| **Autor** | {author} |
| **Tier** | {tier} |
| **Estado** | completado |
| **Score requerido** | >=60 |

---

## 1. Objetivo

{objective}

---

## 2. Value Driver

{value_driver}

---

## 3. Functional Requirements

| FR# | Descripcion |
|-----|-------------|
{fr_lines}

---

## 4. Success Criteria

{sc_lines}

---

## 5. Gherkin Scenarios

Ver `gherkin/{spec_id}.feature`

---

## 6. Edge Cases

{ec_lines if ec_lines else "- Por definir"}

---

## 7. Technical Approach

{approach}

---

## 8. Dependencies

{dependencies}

---

## 9. Events to Emit

{events_table}

---

## 10. Kill Criteria

{kill_criteria}

---

## 11. Scale Criteria

{scale_criteria}
"""


def generate_score(args: dict) -> str:
    spec_id = args["spec_id"]
    scores = args.get("scores", {m[0]: 5 for m in SCORE_METRICS})
    reasons = args.get("score_reasons", {m[0]: "—" for m in SCORE_METRICS})

    rows = []
    for name, hint in SCORE_METRICS:
        s = scores.get(name, 5)
        r = reasons.get(name, "—")
        rows.append(f"| {name} | 1x | {s} | {r} |")

    total = sum(scores.get(m[0], 5) for m in SCORE_METRICS)
    passed = total >= 60
    separator = "\n"
    verdict = "PASA" if passed else "RECHAZADO"
    result = "aprobado" if passed else "rechazado"

    content = f"""# Score — {spec_id}

| Metrica | Peso | Score (0-10) | Justificacion |
|---------|------|--------------|---------------|
{separator.join(rows)}

**Total: {total}/100** => {verdict} (corte: >=60)

**Veredicto:** {result}
**Aprobado por:** score-sh
"""
    return content


def generate_adr(args: dict) -> str:
    spec_id = args["spec_id"]
    title = args.get("adr_title", args["title"])
    adr_num = args.get("adr_num", "001")
    today_str = today()
    today_compact_str = today_compact()

    adr_context = args.get("adr_context", "Contexto por definir.")
    adr_decision = args.get("adr_decision", "Decision por definir.")
    adr_options = args.get("adr_options", "| Opcion | Pros | Contras |\n|--------|------|---------|\n| A | — | — |\n| B | — | — |")
    adr_consequences = args.get("adr_consequences", "Consecuencias por definir.")
    adr_lessons = args.get("adr_lessons", "—")

    return f"""# ADR-{today_compact_str}-{adr_num} — {title}

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-{today_compact_str}-{adr_num}` |
| **Fecha** | {today_str} |
| **Spec** | `{spec_id}` |
| **Estado** | aceptado |

---

## Context

{adr_context}

---

## Decision

{adr_decision}

---

## Options Considered

{adr_options}

---

## Consequences

{adr_consequences}

---

## Lessons

{adr_lessons}

---

## Related

- Spec: `{spec_id}`
- Events: `session.start`, `spec.completed`
"""


def generate_leccion(args: dict) -> str:
    spec_id = args["spec_id"]
    went_well = args.get("went_well", [])
    went_wrong = args.get("went_wrong", [])
    different = args.get("different", [])

    ww_lines = "\n".join(f"- [x] {x}" for x in went_well) if went_well else "- [ ] —"
    wr_lines = "\n".join(f"- [x] {x}" for x in went_wrong) if went_wrong else "- [ ] —"
    df_lines = "\n".join(f"- {x}" for x in different) if different else "- —"

    return f"""# Leccion — {spec_id}

| Campo | Valor |
|-------|-------|
| **Spec** | `{spec_id}` |
| **Tier** | {args.get("tier", "2")} |
| **Fecha** | {today()} |

---

## Que paso?

{args.get("description", "Descripcion pendiente.")}

---

## Que salio bien?

{ww_lines}

---

## Que salio mal?

{wr_lines}

---

## Que hariamos diferente?

{df_lines}

---

## Engram Tags

{args.get("tags", "general")}
"""


def generate_events(args: dict) -> str:
    events = args.get("events", [
        {"name": "session.start", "desc": f"Inicio de {args['title']}"},
        {"name": "spec.created", "desc": f"Spec {args['spec_id']} creada"},
    ])
    lines = []
    for ev in events:
        evt = json.dumps({
            "event": ev["name"],
            "id": f"auto_{args['spec_id'].lower()}_{datetime.now().strftime('%H%M%S')}",
            "timestamp": datetime.now().isoformat() + "Z",
            "source": {"kernel": "documentation", "agent": "auto-doc"},
            "subject": {"type": "spec", "id": args["spec_id"]},
            "payload": {"desc": ev["desc"]},
        }, ensure_ascii=False)
        lines.append(evt)

        # Also emit to unified event bus if available
        try:
            import subprocess
            subprocess.run(
                ["python3", str(Path(__file__).parent / "emit-event.py"),
                 "--event", ev["name"],
                 "--kernel", "documentation",
                 "--agent", "auto-doc",
                 "--subject-type", "spec",
                 "--subject-id", args["spec_id"],
                 "--payload", json.dumps({"desc": ev["desc"]})],
                capture_output=True, timeout=5
            )
        except Exception:
            pass

    return "\n".join(lines) + "\n"


def generate_gherkin(args: dict) -> str:
    spec_id = args["spec_id"]
    scenarios = args.get("gherkin_scenarios", [
        {"title": "Happy path", "given": "context", "when": "action", "then": "expected result"},
    ])

    sc_lines = ""
    for sc in scenarios:
        sc_lines += f"""
  Scenario: {sc['title']}
    Given {sc.get('given', 'context')}
    When {sc.get('when', 'action')}
    Then {sc.get('then', 'expected')}
"""

    return f"""Feature: {args["title"]}
  As a {args.get("gherkin_role", "system")}
  I want {args.get("gherkin_goal", args.get("objective", f"implement {args['title']}"))}
  So that {args.get("gherkin_benefit", "value")}

  Background:
    Given system is in default state
{sc_lines}
"""


def make_docs(args: dict, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "gherkin").mkdir(exist_ok=True)

    docs = {
        "SPEC.md": generate_spec(args),
        "SCORE.md": generate_score(args),
        f"ADR-{today_compact()}-{args.get('adr_num', '001')}.md": generate_adr(args),
        "LECCION.md": generate_leccion(args),
        "events.jsonl": generate_events(args),
        f"gherkin/{args['spec_id']}.feature": generate_gherkin(args),
    }

    for filename, content in docs.items():
        filepath = output_dir / filename
        filepath.write_text(content)
        print(f"  CREATED {filepath.relative_to(ROOT)}")

    update_catalog(args)
    print(f"\n  => {output_dir.relative_to(ROOT)}/ complete")


def update_catalog(args: dict):
    if not CATALOG.exists():
        CATALOG.write_text("# CATALOG — Completed Initiatives\n\n| Fecha | ID | Titulo | Tier | Score | Estado | Leccion |\n|-------|-----|--------|------|-------|--------|---------|\n")

    text = CATALOG.read_text()
    spec_id = args["spec_id"]
    scores = args.get("scores", {m[0]: 5 for m in SCORE_METRICS})
    total = sum(scores.get(m[0], 5) for m in SCORE_METRICS)

    new_row = "| {} | {} | {} | {} | {} | completed | [link]({}/LECCION.md) |".format(
        today(), spec_id, args["title"],
        args.get("tier", "2"),
        total,
        args.get("dir_name", spec_id.lower().replace("spec-", "")),
    )

    if spec_id in text:
        text = re.sub(
            r"\|.*?\|.*?" + re.escape(spec_id) + r".*?\|.*?\|.*?\|.*?\|.*?\|.*?\|",
            new_row,
            text,
        )
    else:
        lines = text.split("\n")
        insert_idx = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith("|") and "Fecha" not in line and not line.strip().endswith("|-"):
                insert_idx = max(insert_idx, i + 1)
        lines.insert(insert_idx, new_row)
        text = "\n".join(lines)

    CATALOG.write_text(text)
    print(f"  UPDATED {CATALOG.relative_to(ROOT)}")


def autofill(args: dict):
    """Auto-fill common values from summary."""
    summary = args.get("summary", "")
    title = args.get("title", "Auto-generated Spec")

    # Infer FRs from summary bullet points
    bullets = re.findall(r"[-*]\s*(.+?)(?=[-*]|\Z)", summary, re.DOTALL)
    if not bullets:
        bullets = [summary[:100]] if summary else [f"Implementar {title}"]

    args.setdefault("frs", [b.strip()[:80] for b in bullets[:10]])
    args.setdefault("success_criteria", [f"[ ] {b.strip()[:60]}" for b in bullets[:5]])
    args.setdefault("edge_cases", bullets[3:6] if len(bullets) > 3 else ["Por identificar durante implementacion"])
    args.setdefault("went_well", bullets[:3] if bullets else ["—"])
    args.setdefault("went_wrong", bullets[1:4] if len(bullets) > 1 else ["—"])
    args.setdefault("different", ["Documentar mientras se construye, no al final"])
    args.setdefault("description", summary[:200] if summary else "Implementacion completada.")
    args.setdefault("events", [
        {"name": "session.start", "desc": f"Inicio de {title}"},
        {"name": "spec.created", "desc": "Spec creada"},
        {"name": "work.completed", "desc": "Implementacion completada"},
    ])
    args.setdefault("gherkin_scenarios", [
        {"title": "Implementacion exitosa", "given": "los requisitos estan definidos",
         "when": "se ejecuta la implementacion", "then": "todos los criterios de exito se cumplen"},
        {"title": "Rollback", "given": "la implementacion falla",
         "when": "se ejecuta rollback", "then": "el sistema vuelve a estado estable"},
    ])

    scores = {}
    score_reasons = {}
    for name, hint in SCORE_METRICS:
        scores[name] = args.get("scores", {}).get(name, 5)
        score_reasons[name] = args.get("score_reasons", {}).get(name, "—")

    args.setdefault("scores", scores)
    args.setdefault("score_reasons", score_reasons)

    return args


def interactive_fill(args: dict) -> dict:
    """Ask user for missing critical fields."""
    print("\n=== Completa campos faltantes ===")
    print(f"Spec ID: {args['spec_id']}")
    print(f"Titulo: {args['title']}")
    print(f"Tier: {args.get('tier', '2')}")
    print()

    if not args.get("frs") or args["frs"] == [f"Implementar {args['title']}"]:
        print("Funcional Requirements (enter=vacio, termina con .):")
        frs = []
        i = 1
        while True:
            fr = input(f"  FR{i}: ").strip()
            if not fr:
                break
            frs.append(fr)
            i += 1
        if frs:
            args["frs"] = frs

    if not args.get("went_well"):
        ww = input("Que salio bien? (breve): ").strip()
        if ww:
            args["went_well"] = [ww]

    if not args.get("went_wrong"):
        wr = input("Que salio mal? (breve): ").strip()
        if wr:
            args["went_wrong"] = [wr]

    return args


def auto_from_agents(args: dict) -> dict:
    """Auto-detect from AGENTS.md Progress section."""
    if not AGENTS.exists():
        print("AGENTS.md not found, skipping auto-detect")
        return args

    text = AGENTS.read_text()
    progress_match = re.search(r"## Progress\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not progress_match:
        return args

    progress = progress_match.group(1)
    args["summary"] = progress.strip()[:500]

    # Extract Done items
    done_items = re.findall(r"-\s*\*{0,2}(.*?)\*{0,2}:?\s*(.*?)(?=\n-\s*\*{0,2}|\n\s*\*{0,2}\[|$)", progress, re.DOTALL)
    if done_items:
        args["title"] = done_items[0][0].strip()[:60] if done_items[0][0].strip() else args["title"]
        bullets = [f"{d[0]}: {d[1][:60]}" for d in done_items if d[0].strip()]
        args["summary_bullets"] = bullets
        args.setdefault("frs", bullets[:8])
        args.setdefault("went_well", bullets[:3])
        args.setdefault("went_wrong", [b for b in bullets if "mal" in b.lower() or "error" in b.lower() or "fall" in b.lower()][:2] or ["—"])

    return args


def main():
    parser = argparse.ArgumentParser(description="Generate process documentation automatically")
    parser.add_argument("--spec-id", default=f"SPEC-{today_compact()}-001")
    parser.add_argument("--title", default="Auto-generated Spec")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3], default=2)
    parser.add_argument("--summary", default="", help="Session summary")
    parser.add_argument("--dir", help="Output directory name")
    parser.add_argument("--auto", action="store_true", help="Auto-fill from summary")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing dir")

    cmd_args = parser.parse_args()

    spec_id = cmd_args.spec_id
    dir_name = cmd_args.dir or spec_id.lower().replace("spec-", "")
    output_dir = COMPLETED / dir_name

    args = {
        "spec_id": spec_id,
        "title": cmd_args.title,
        "tier": cmd_args.tier,
        "summary": cmd_args.summary or cmd_args.title,
        "objective": f"Implementar {cmd_args.title}",
        "dir_name": dir_name,
        "adr_num": "001",
        "adr_title": cmd_args.title,
        "gherkin_role": "system",
        "gherkin_goal": f"implement {cmd_args.title}",
    }

    if cmd_args.auto:
        args = auto_from_agents(args)
        args = autofill(args)

    if cmd_args.interactive:
        args = interactive_fill(args)

    if output_dir.exists() and not cmd_args.force and not cmd_args.interactive:
        print(f"Directory {output_dir.relative_to(ROOT)} already exists.")
        print("Use --force to overwrite or -i for interactive mode.")
        sys.exit(1)
    elif output_dir.exists() and cmd_args.force:
        import shutil
        shutil.rmtree(output_dir)
        print(f"  REMOVED existing {output_dir.relative_to(ROOT)}")

    make_docs(args, output_dir)
    print("\nDone. Revisar y completar campos faltantes.")


if __name__ == "__main__":
    main()
