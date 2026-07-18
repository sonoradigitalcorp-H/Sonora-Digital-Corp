#!/usr/bin/env python3
"""Motor único de generación desde templates — reemplaza escritura manual de docs [FR17]"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO / "process" / "templates"


def list_templates():
    """Lista templates disponibles"""
    templates = {}
    for f in sorted(TEMPLATES_DIR.glob("*.md")):
        name = f.stem
        # Extract number prefix (e.g., "01-SPEC" -> "SPEC")
        base = re.sub(r"^\d+-", "", name)
        templates[base.lower()] = {
            "file": f.name,
            "path": str(f.relative_to(REPO))
        }
    return templates


def get_placeholders(template_content):
    """Extrae todos los placeholders {{NAME}} del template"""
    return set(re.findall(r"\{\{(\w+)\}\}", template_content))


def generate(template_name, values, output_path=None):
    """Genera un documento desde template"""
    templates = list_templates()
    key = template_name.lower().replace(".md", "")

    if key not in templates:
        print(f"ERROR: Template '{template_name}' not found", file=sys.stderr)
        print(f"Available: {list(templates.keys())}", file=sys.stderr)
        sys.exit(1)

    template_file = TEMPLATES_DIR / templates[key]["file"]
    content = template_file.read_text()

    # Replace placeholders
    placeholders = get_placeholders(content)
    missing = []
    for ph in placeholders:
        if ph in values:
            content = content.replace("{{" + ph + "}}", str(values[ph]))
        else:
            missing.append(ph)

    # Auto-fill missing placeholders with defaults
    defaults = {
        "DATE": datetime.now().strftime("%Y-%m-%d"),
        "ID": datetime.now().strftime("%Y%m%d%H%M"),
    }
    for ph in placeholders:
        if ph in defaults and ph not in values:
            content = content.replace("{{" + ph + "}}", defaults[ph])

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"Generated: {output_path}", file=sys.stderr)
    else:
        print(content)

    return {"template": template_name, "output": str(output_path) if output_path else "stdout",
            "placeholders_filled": len(placeholders) - len(missing)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate document from template")
    parser.add_argument("template", help="Template name (e.g., SPEC, ADR, PLAYBOOK)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--values", "-v", help="JSON string with placeholder values")
    parser.add_argument("--values-file", help="JSON file with placeholder values")
    parser.add_argument("--list", action="store_true", help="List available templates")
    args = parser.parse_args()

    if args.list:
        templates = list_templates()
        print("Available templates:")
        for name, info in sorted(templates.items()):
            print(f"  {name:20s} → {info['file']}")
        return

    values = {}
    if args.values:
        values.update(json.loads(args.values))
    if args.values_file:
        with open(args.values_file) as f:
            values.update(json.load(f))

    result = generate(args.template, values, args.output)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
