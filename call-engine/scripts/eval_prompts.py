#!/usr/bin/env python3
"""Evalúa los prompts del Call Engine contra OpenRouter.
Ejecuta cada test, verifica asserts, reporta resultados.
"""
import json
import os
import re
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ask_llm(system: str, user: str) -> str:
    prompt = f"{system}\n\n{user}"
    full_msg = prompt[:2000]
    try:
        r = subprocess.run(
            ["opencode", "run", full_msg],
            capture_output=True, text=True, timeout=180
        )
        out = r.stdout.strip()
        return out if out else "[ERROR: empty response]"
    except subprocess.TimeoutExpired:
        return "[ERROR: timeout]"
    except Exception as e:
        return f"[ERROR: {e}]"

def load_prompt(path: str) -> str:
    with open(os.path.join(BASE, "promptfoo", path)) as f:
        return f.read()

def run_tests():
    results = {"passed": 0, "failed": 0, "tests": []}

    tests = [
        {
            "name": "call_agent - Nathaly warm lead",
            "prompt": "prompts/call_agent.txt",
            "vars": {
                "lead_name": "Nathaly",
                "company": "Hermosillo",
                "objective": "Ofrecer servicios agenticos de SDC",
                "context": "Novia del CEO, contacto cálido, conoce la empresa",
                "tone": "cálido, profesional, directo",
                "history": "Sin llamadas previas",
            },
            "assert_contains": ["Sonora Digital Corp"],
            "assert_not_contains": ["pagar ahora", "solo hoy", "firma ya", "contrato"],
        },
        {
            "name": "call_agent - Carlos cold lead",
            "prompt": "prompts/call_agent.txt",
            "vars": {
                "lead_name": "Carlos",
                "company": "Agencia Creativa XYZ",
                "objective": "Vender pack de agente de atención al cliente",
                "context": "Lead frío, dueño de agencia, 10 empleados",
                "tone": "profesional",
                "history": "Sin llamadas previas",
            },
            "assert_not_contains": ["compra ahora", "solo por hoy", "descuento limitado"],
        },
        {
            "name": "objection - no tengo tiempo",
            "prompt": "prompts/objection_handler.txt",
            "vars": {
                "objection": "No tengo tiempo para esto",
                "context": "Dueño de negocio ocupado, 3 empleados",
                "relationship": "Lead frío",
                "attempt": "1",
            },
            "assert_not_contains": ["insisto", "obligado", "tienes que"],
        },
        {
            "name": "objection - ya tengo proveedor",
            "prompt": "prompts/objection_handler.txt",
            "vars": {
                "objection": "Ya tengo un proveedor",
                "context": "Agencia de marketing con 5 empleados",
                "relationship": "Lead caliente, referido",
                "attempt": "2",
            },
            "assert_contains": ["proveedor"],
        },
        {
            "name": "scoring - lead caliente",
            "prompt": "prompts/lead_scoring.txt",
            "vars": {
                "transcript": "Cliente: Me interesa mucho. ¿Cuándo podemos empezar? Agente: Podemos activar tu agente hoy mismo.",
                "duration": "5m",
                "objective": "Vender pack agente atención al cliente",
            },
            "assert_contains": ["hot"],
            "assert_json": True,
        },
        {
            "name": "scoring - lead tibio",
            "prompt": "prompts/lead_scoring.txt",
            "vars": {
                "transcript": "Cliente: Me interesa pero tengo que consultarlo con mi socio. ¿Me envías más info?",
                "duration": "4m",
                "objective": "Vender pack agente atención al cliente",
            },
            "assert_contains": ["warm"],
            "assert_json": True,
        },
    ]

    for t in tests:
        time.sleep(1)
        prompt_text = load_prompt(t["prompt"])
        filled = prompt_text
        for k, v in t["vars"].items():
            filled = filled.replace("{{" + k + "}}", v)
        if "{{" in filled:
            missing = re.findall(r"\{\{(\w+)\}\}", filled)
            filled += f"\n\n[NOTA: variables sin reemplazar: {missing}]"

        system = "Eres un agente de ventas de Sonora Digital Corp haciendo una llamada. Actúa exactamente como lo haría el agente en una llamada real. No mencio nes que eres un evaluador ni hables sobre prompts. Responde DIRECTAMENTE al lead."
        response = ask_llm(system, filled)

        test_result = {"name": t["name"], "passed": True, "failures": []}

        if t.get("assert_contains"):
            for keyword in t["assert_contains"]:
                if keyword.lower() not in response.lower():
                    test_result["passed"] = False
                    test_result["failures"].append(f"Falta: '{keyword}'")

        if t.get("assert_not_contains"):
            for keyword in t["assert_not_contains"]:
                if keyword.lower() in response.lower():
                    test_result["passed"] = False
                    test_result["failures"].append(f"Prohibido encontrado: '{keyword}'")

        if t.get("assert_regex"):
            if not re.search(t["assert_regex"], response):
                test_result["passed"] = False
                test_result["failures"].append(f"No cumple regex: {t['assert_regex']}")

        if t.get("assert_json"):
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
            try:
                parsed = json.loads(cleaned)
                for keyword in t.get("assert_contains", []):
                    val = json.dumps(parsed).lower()
                    if keyword.lower() not in val:
                        test_result["passed"] = False
                        test_result["failures"].append(f"JSON no contiene '{keyword}'")
            except json.JSONDecodeError:
                test_result["passed"] = False
                test_result["failures"].append("Respuesta no es JSON válido")

        if test_result["passed"]:
            results["passed"] += 1
            status = "✅ PASS"
        else:
            results["failed"] += 1
            status = "❌ FAIL"

        print(f"\n{'='*60}")
        print(f"{status} {t['name']}")
        print(f"{'='*60}")
        for f in test_result["failures"]:
            print(f"  ⚠️  {f}")
        print(f"  Response: {response[:200]}...")
        results["tests"].append(test_result)

    print(f"\n\n{'='*60}")
    print(f"RESULTADOS: {results['passed']} passed, {results['failed']} failed")
    print(f"{'='*60}")

    sys.exit(0 if results["failed"] == 0 else 1)

if __name__ == "__main__":
    run_tests()
