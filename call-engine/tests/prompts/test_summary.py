#!/usr/bin/env python3
"""Eval: summary prompt — extrae puntos clave de transcripción."""
import json, os, sys, urllib.request, urllib.error

PROMPT = """Resume la siguiente llamada de ventas en JSON.

TRANSCRIPCIÓN:
{transcript}

DURACIÓN: {duration}

Responde SOLO con JSON:
{{
  "outcome": "resumen de 1 línea",
  "objections": ["objeción 1", "objeción 2"],
  "next_step": "qué hacer después",
  "score": "cold|warm|hot"
}}
"""

TESTS = [
    {
        "name": "summary - llamada con objeción resuelta",
        "vars": {
            "transcript": "Agente: Hola, somos SDC. Lead: No me interesa. Agente: ¿Puedo preguntar por qué? Lead: Tengo proveedor. Agente: Entiendo, ¿qué valora de su proveedor? Lead: El precio. Agente: Nosotros ofrecemos 20% menos. Lead: Suena bien, mándenme info.",
            "duration": "4:30",
        },
        "assert_fields": ["outcome", "objections", "next_step", "score"],
        "assert_json": True,
    },
    {
        "name": "summary - llamada corta sin interés",
        "vars": {
            "transcript": "Agente: Hola, soy de SDC. Lead: No me interesa, gracias. Agente: Gracias, buen día.",
            "duration": "0:45",
        },
        "assert_fields": ["outcome", "objections", "next_step", "score"],
        "assert_json": True,
    },
]

def ask(text: str) -> str:
    import subprocess
    try:
        r = subprocess.run(["ollama", "run", "llama3.2:3b"], input=text, capture_output=True, text=True, timeout=120)
        return r.stdout.strip() or "[ERROR: empty]"
    except subprocess.TimeoutExpired: return "[ERROR: timeout]"
    except Exception as e: return f"[ERROR: {e}]"
def main():
    passed = failed = 0
    for t in TESTS:
        resp = ask(PROMPT.format(**t["vars"]))
        cleaned = resp.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        ok = True
        try:
            parsed = json.loads(cleaned)
            for field in t["assert_fields"]:
                if field not in parsed:
                    ok = False
                    print(f"❌ {t['name']}: falta campo '{field}'")
            if ok:
                passed += 1
                print(f"✅ {t['name']}")
        except json.JSONDecodeError:
            failed += 1
            print(f"❌ {t['name']}: JSON inválido")
        print(f"   {resp[:200]}...\n")

    print(f"\nResultados: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
