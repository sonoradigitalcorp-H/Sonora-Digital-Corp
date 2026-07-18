#!/usr/bin/env python3
"""Evalúa prompts del Call Engine por nicho con DeepSeek V4 Flash.
Mide tiempo, tokens estimados y costo de cada interacción.

Uso:
  python3 scripts/eval_niches.py                         # todos los nichos, 3 workers
  python3 scripts/eval_niches.py --niche music            # solo music
  python3 scripts/eval_niches.py --niche agencies,real_estate
  python3 scripts/eval_niches.py --workers 6
  python3 scripts/eval_niches.py --fast                  # usa Ollama (más rápido, menos preciso)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NICHES_DIR = os.path.join(BASE, "promptfoo", "niches")

NICHES = {
    "music": "Industria Musical (ABE Music)",
    "agencies": "Agencias Creativas / Marketing",
    "real_estate": "Bienes Raíces",
    "ecommerce": "E-commerce",
    "prof_services": "Servicios Profesionales",
}

PROMPT_TYPES = {
    "call_agent": {
        "file": "call_agent.txt",
        "test_file": "call_agent.yaml",
        "system": "Eres un agente de ventas de Sonora Digital Corp. Actúa exactamente como lo haría el agente en una llamada real. Responde DIRECTAMENTE al lead.",
    },
    "objection_handler": {
        "file": "objection_handler.txt",
        "test_file": "objection.yaml",
        "system": "Eres un agente de ventas de Sonora Digital Corp manejando una objeción. Usa el método de 5 pasos de Brian Tracy. Responde DIRECTAMENTE al lead.",
    },
    "lead_scoring": {
        "file": "lead_scoring.txt",
        "test_file": "scoring.yaml",
        "system": "Eres un evaluador de leads de Sonora Digital Corp. Analiza la transcripción y responde SOLO con el JSON solicitado, sin explicaciones adicionales.",
    },
}


def ask_fast(prompt: str) -> tuple:
    """Ollama local (rápido ~2-5s, modelo más débil)"""
    api = os.environ.get("OLLAMA_API", "http://localhost:11434/api/generate")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
    body = json.dumps({
        "model": model, "prompt": prompt[:2000],
        "stream": False, "options": {"num_predict": 300, "temperature": 0.1}
    }).encode()
    t0 = time.time()
    try:
        r = urllib.request.urlopen(api, data=body, timeout=120)
        data = json.loads(r.read())
        elapsed = time.time() - t0
        resp = data.get("response", "[ERROR: empty]")
        tokens = data.get("eval_count", 0)
        cost = 0
        return resp, elapsed, tokens, cost
    except Exception as e:
        return f"[ERROR: {e}]", time.time() - t0, 0, 0


OPencode = os.environ.get("OPEncode_BIN", "opencode")

def ask_premium(prompt: str) -> tuple:
    """DeepSeek V4 Flash via opencode run (~30-60s, mejor modelo)"""
    t0 = time.time()
    try:
        r = subprocess.run(
            [OPencode, "run", prompt[:2000]],
            capture_output=True, text=True, timeout=180
        )
        elapsed = time.time() - t0
        resp = r.stdout.strip() or "[ERROR: empty]"
        tokens = max(1, len(resp) // 4)
        cost = tokens * 0.0000005
        return resp, elapsed, tokens, cost
    except subprocess.TimeoutExpired:
        return "[ERROR: timeout]", time.time() - t0, 0, 0
    except Exception as e:
        return f"[ERROR: {e}]", time.time() - t0, 0, 0


def load_prompt(niche: str, prompt_type: str) -> str:
    path = os.path.join(NICHES_DIR, niche, "prompts", PROMPT_TYPES[prompt_type]["file"])
    with open(path) as f:
        return f.read()


def load_tests(niche: str, prompt_type: str) -> list:
    test_file = PROMPT_TYPES[prompt_type]["test_file"]
    path = os.path.join(NICHES_DIR, niche, "tests", test_file)
    if not os.path.exists(path):
        return []
    import yaml
    return yaml.safe_load(open(path)) or []


def fill_template(template: str, vars: dict) -> str:
    filled = template
    for k, v in vars.items():
        filled = filled.replace("{{" + k + "}}", v)
    missing = re.findall(r"\{\{(\w+)\}\}", filled)
    if missing:
        filled += f"\n\n[NOTA: variables sin reemplazar: {missing}]"
    return filled


def run_single_test(niche: str, ptype: str, pconfig: dict, t: dict, fast: bool) -> dict:
    ask = ask_fast if fast else ask_premium
    template = load_prompt(niche, ptype)
    vars = t.get("vars", {})
    filled = fill_template(template, vars)
    prompt = f"{pconfig['system']}\n\n{filled}"

    resp, elapsed, tokens, cost = ask(prompt)

    result = {
        "name": f"{niche}/{ptype} - {vars.get('lead_name') or vars.get('objection', '')[:30] or 'scoring'}",
        "niche": niche, "type": ptype,
        "passed": True, "failures": [],
        "response": resp[:150], "time_s": round(elapsed, 1),
        "tokens": tokens, "cost_usd": round(cost, 6),
    }

    for assertion in t.get("assert", []):
        atype = assertion.get("type")
        value = assertion.get("value", "")

        if atype == "contains-all":
            for kw in value:
                if kw.lower() not in resp.lower():
                    result["passed"] = False
                    result["failures"].append(f"Falta: '{kw}'")

        elif atype == "contains":
            kw = value if isinstance(value, str) else value[0]
            if kw.lower() not in resp.lower():
                result["passed"] = False
                result["failures"].append(f"Falta: '{kw}'")

        elif atype == "not-contains":
            for kw in (value if isinstance(value, list) else [value]):
                if kw.lower() in resp.lower():
                    result["passed"] = False
                    result["failures"].append(f"Prohibido: '{kw}'")

        elif atype == "regex":
            if not re.search(value, resp):
                result["passed"] = False
                result["failures"].append(f"No cumple regex: {value}")

        elif atype == "is-json":
            cleaned = resp.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
            try:
                json.loads(cleaned)
            except json.JSONDecodeError:
                result["passed"] = False
                result["failures"].append("No es JSON válido")

        elif atype == "llm-rubric":
            rubric = value
            rp = f"Evalúa si cumple: {rubric}\n\nRespuesta:\n{resp}\n\nResponde SOLO: PASS o FAIL"
            eval_resp, _, _, _ = ask(rp)
            if "FAIL" in eval_resp.upper() and "PASS" not in eval_resp.upper():
                result["passed"] = False
                result["failures"].append(f"Rúbrica: {rubric[:60]}...")

    return result


def run_tests():
    parser = argparse.ArgumentParser(description="Evalúa prompts por nicho")
    parser.add_argument("--niche", help="Nichos (separados por coma)")
    parser.add_argument("--workers", type=int, default=3, help="Paralelismo")
    parser.add_argument("--fast", action="store_true", help="Usa Ollama (rápido) en vez de DeepSeek V4 Flash")
    args = parser.parse_args()

    selected = [n.strip() for n in args.niche.split(",") if n.strip() in NICHES] if args.niche else list(NICHES.keys())
    if not selected:
        print(f"No hay nichos. Opciones: {', '.join(NICHES.keys())}")
        sys.exit(1)

    try:
        import yaml
    except ImportError:
        print("pip install pyyaml")
        sys.exit(1)

    model_name = "Ollama (fast)" if args.fast else "DeepSeek V4 Flash"
    tasks = []
    for niche in selected:
        for ptype, pconfig in PROMPT_TYPES.items():
            for t in load_tests(niche, ptype):
                tasks.append((niche, ptype, pconfig, t, args.fast))

    print(f"\n📋 {len(tasks)} tests | {len(selected)} nichos | {args.workers} workers | {model_name}")
    print(f"{'='*60}\n")

    overall = {"passed": 0, "failed": 0, "time": 0, "tokens": 0, "cost": 0.0,
               "by_niche": {n: {"passed": 0, "failed": 0, "time": 0, "tokens": 0, "cost": 0.0} for n in selected}}
    completed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_single_test, *t) for t in tasks}

        for future in as_completed(futures):
            result = future.result()
            completed += 1
            niche = result["niche"]

            if result["passed"]:
                overall["passed"] += 1
                overall["by_niche"][niche]["passed"] += 1
                status = "✅ PASS"
            else:
                overall["failed"] += 1
                overall["by_niche"][niche]["failed"] += 1
                status = "❌ FAIL"

            overall["time"] += result["time_s"]
            overall["tokens"] += result["tokens"]
            overall["cost"] += result["cost_usd"]
            overall["by_niche"][niche]["time"] += result["time_s"]
            overall["by_niche"][niche]["tokens"] += result["tokens"]
            overall["by_niche"][niche]["cost"] += result["cost_usd"]

            pct = f"[{completed}/{len(tasks)}]"
            print(f"  {pct} {status} {result['name']}  ({result['time_s']}s, {result['tokens']}tok)")
            for f in result["failures"]:
                print(f"           ⚠️  {f}")

    print(f"\n{'='*60}")
    total = overall["passed"] + overall["failed"]
    print(f"  RESULTADO: {overall['passed']}/{total} passed, {overall['failed']} failed")
    print(f"  TIEMPO:    {overall['time']:.0f}s total, {overall['time']/max(total,1):.1f}s/test")
    print(f"  TOKENS:    {overall['tokens']} total")
    print(f"  COSTO:     ${overall['cost']:.6f} USD")
    print(f"{'='*60}")

    for niche in selected:
        r = overall["by_niche"][niche]
        nt = r["passed"] + r["failed"]
        if nt > 0:
            print(f"  {NICHES[niche]}: {r['passed']}/{nt} | {r['time']:.0f}s | {r['tokens']}tok | ${r['cost']:.6f}")

    sys.exit(0 if overall["failed"] == 0 else 1)


if __name__ == "__main__":
    run_tests()
