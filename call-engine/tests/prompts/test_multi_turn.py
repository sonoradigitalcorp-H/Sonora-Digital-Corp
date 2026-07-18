#!/usr/bin/env python3
"""Eval: multi-turn conversation — el agente mantiene contexto entre turnos."""
import json, os, sys, time, urllib.request, urllib.error

SYSTEM = """Eres un agente de ventas de Sonora Digital Corp.
LLAMAS a: Nathaly
OBJETIVO: Ofrecer servicios agenticos
TONO: Cálido, profesional

Reglas:
- Escucha más de lo que hablas
- Responde en español
- Mantén el contexto de la conversación
- Refiérete a lo que el lead dijo antes
- Siempre avanza hacia el objetivo de la llamada"""

TURNS = [
    {"role": "lead", "text": "¿Hola? ¿Quién habla?"},
    {"role": "lead", "text": "Ah sí, conoczco SDC. ¿Qué me ofrecen?"},
    {"role": "lead", "text": "Suena interesante. ¿Cuánto cuesta?"},
]

def ask(text: str) -> str:
    import subprocess
    try:
        r = subprocess.run(["ollama", "run", "llama3.2:3b"], input=text, capture_output=True, text=True, timeout=120)
        return r.stdout.strip() or "[ERROR: empty]"
    except subprocess.TimeoutExpired: return "[ERROR: timeout]"
    except Exception as e: return f"[ERROR: {e}]"
def main():
    messages = [{"role": "system", "content": SYSTEM}]
    passed = failed = 0

    for i, turn in enumerate(TURNS):
        messages.append({"role": "user", "content": turn["text"]})
        resp = ask(messages)
        messages.append({"role": "assistant", "content": resp})

        turn_num = i + 1
        has_error = resp.startswith("[ERROR")
        is_spanish = any(c in resp for c in "áéíóúñ") or "que" in resp.lower() or "lo" in resp.lower()
        failures = []
        if has_error:
            failures.append("LLM error")
        if not is_spanish:
            failures.append("No responde en español")

        if failures:
            failed += 1
            print(f"❌ Turno {turn_num}: {', '.join(failures)}")
        else:
            passed += 1
            print(f"✅ Turno {turn_num}: {resp[:120]}...")

        time.sleep(1)

    print(f"\nResultados: {passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
