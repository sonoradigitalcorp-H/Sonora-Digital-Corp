#!/usr/bin/env python3
"""Anonimizador de conversaciones — Elimina PII de mensajes reales.

Reemplaza:
  - Nombres propios → [NOMBRE]
  - Teléfonos → [TEL]
  - Emails → [EMAIL]
  - URLs → [URL]
  - Empresas referenciadas → [EMPRESA]
  - Números de tarjeta → [TARJETA]

Determinista: el mismo valor se reemplaza con el mismo placeholder en todo el dataset,
para permitir evaluaciones consistentes.
"""

import json
import os
import re
import sys
from pathlib import Path

# Mapeo determinista valor → placeholder
_NAME_MAP = {}
_PHONE_MAP = {}
_EMAIL_MAP = {}

# Patrones
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[ -]?)?(?:\(\d{2,4}\)[ -]?)?\d{7,10}(?:[ -]\d{2,4})?")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[^\s]+|www\.[^\s]+")
# Nombres: secuencias de palabras capitalizadas (2+ palabras) precedidas por "me llamo|soy|mi nombre es"
NAME_RE = re.compile(r"(?:\b(?:me llamo|soy|mi nombre es|hablo con|atiende)\s+)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,2})")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")


def _next_tag(mapping, value, prefix, counter):
    key = value.lower()
    if key not in mapping:
        counter[0] += 1
        mapping[key] = f"[{prefix}{counter[0]}]"
    return mapping[key]


def anonymize_text(text: str, counters: dict) -> str:
    if not text:
        return text
    out = text

    # Emails
    def repl_email(m):
        return _next_tag(_EMAIL_MAP, m.group(0), "EMAIL", counters["email"])
    out = EMAIL_RE.sub(repl_email, out)

    # URLs
    def repl_url(m):
        return "[URL]"
    out = URL_RE.sub(repl_url, out)

    # Tarjetas (antes que teléfonos para no confundir)
    out = CARD_RE.sub("[TARJETA]", out)

    # Teléfonos
    def repl_phone(m):
        v = m.group(0).strip()
        if len(v) < 7:
            return m.group(0)
        return _next_tag(_PHONE_MAP, v, "TEL", counters["phone"])
    out = PHONE_RE.sub(repl_phone, out)

    # Nombres
    def repl_name(m):
        return _next_tag(_NAME_MAP, m.group(1), "NOMBRE", counters["name"])
    out = NAME_RE.sub(repl_name, out)

    return out


def anonymize_conversation(turns: list) -> list:
    """Anonimiza lista de turns [{role, content}, ...]."""
    counters = {"email": 0, "phone": 0, "name": 0}
    result = []
    for turn in turns:
        result.append({
            "role": turn.get("role", "user"),
            "content": anonymize_text(turn.get("content", ""), counters),
        })
    return result


def anonymize_jsonl(input_path: Path, output_path: Path):
    """Anonimiza un archivo JSONL de conversaciones (una por línea)."""
    out_lines = []
    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if "turns" in item:
                item["turns"] = anonymize_conversation(item["turns"])
            elif "content" in item:
                item["content"] = anonymize_text(item["content"], {"email": 0, "phone": 0, "name": 0})
            out_lines.append(json.dumps(item, ensure_ascii=False))
    output_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"Anonimizado: {input_path} → {output_path} ({len(out_lines)} líneas)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 anonymize_conversations.py <input.jsonl> <output.jsonl>")
        sys.exit(1)
    anonymize_jsonl(Path(sys.argv[1]), Path(sys.argv[2]))