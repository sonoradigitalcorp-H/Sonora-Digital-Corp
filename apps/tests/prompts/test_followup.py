#!/usr/bin/env python3
"""Eval: followup prompt — genera mensaje de seguimiento post-llamada."""
import json
import os
import sys

PROMPT = """Eres un asistente de Sonora Digital Corp generando un mensaje de seguimiento.

DATOS DE LA LLAMADA:
Lead: {lead_name}
Score: {score}
Resumen: {summary}
Objetivo de llamada: {objective}
Objeciones: {objections}

Genera un mensaje de WhatsApp de seguimiento para este lead.
Debe ser:
- Personalizado (menciona la conversación anterior)
- Con un próximo paso claro
- Con branding de Sonora Digital Corp
- Máximo 200 palabras
"""

TESTS = [
    {
        "name": "followup - warm lead con interés",
        "vars": {
            "lead_name": "Carlos",
            "score": "warm",
            "summary": "Cliente interesado en pack de agente, pidió más información",
            "objective": "Vender pack agente atención al cliente",
            "objections": "Ninguna, solo quiere ver pricing",
        },
        "assert_contains": ["Carlos", "Sonora Digital Corp"],
    },
    {
        "name": "followup - cold lead con objeción",
        "vars": {
            "lead_name": "María",
            "score": "cold",
            "summary": "Cliente dijo que ya tiene proveedor y no quiere cambiar",
            "objective": "Vender pack agente atención al cliente",
            "objections": "Ya tengo proveedor, estoy satisfecho",
        },
        "assert_contains": ["María", "Sonora Digital Corp"],
        "assert_not_contains": ["presionar", "obligado", "descuento exclusivo"],
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
    passed = 0
    failed = 0
    for t in TESTS:
        filled = PROMPT.format(**t["vars"])
        resp = ask(filled)
        ok = True
        failures = []
        for kw in t.get("assert_contains", []):
            if kw.lower() not in resp.lower():
                ok = False
                failures.append(f"Falta: '{kw}'")
        for kw in t.get("assert_not_contains", []):
            if kw.lower() in resp.lower():
                ok = False
                failures.append(f"Prohibido: '{kw}'")
        if ok:
            passed += 1
            print(f"✅ {t['name']}")
        else:
            failed += 1
            print(f"❌ {t['name']}")
            for f in failures:
                print(f"   ⚠️  {f}")
        print(f"   {resp[:150]}...\n")

    print(f"\nResultados: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
