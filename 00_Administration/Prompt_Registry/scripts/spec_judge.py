#!/usr/bin/env python3
"""Spec Judge — evalúa un prompt contra su spec y features Gherkin.
Uso:
  python3 spec_judge.py --prompt <PROMPT.md> --spec <SPEC.md> --feature <FILE.feature>
Devuelve score 0-100 por criterio + veredicto PASS/FAIL.
Usa OpenRouter (deepseek-v4-flash-0731). NUNCA LLM local pesado.
"""
import argparse, json, os, re, sys, urllib.request

def _load_env_key(name):
    p = os.path.expanduser("~/.hermes/.env")
    with open(p) as f:
        for line in f:
            if line.startswith(f"{name}="):
                return line.strip().split("=", 1)[1].strip()
    return ""

OPENROUTER_KEY = _load_env_key("OPENROUTER_API_KEY")  # SIEMPRE del .env canónico; el env del shell puede estar stale
MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash-0731")

def _llm(system, user, max_tokens=1200):
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_tokens": max_tokens}).encode()
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body, headers={
        "Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data["choices"][0]["message"]["content"]

def _parse_scenario_lines(feature_text):
    steps = []
    for line in feature_text.splitlines():
        line = line.strip()
        for kw in ("Given ", "When ", "Then ", "And "):
            if line.startswith(kw):
                steps.append(line[len(kw):].strip())
    return steps

def judge(prompt_text, spec_text, feature_text):
    criteria = [
        ("spec_alignment", "El prompt cumple TODOS los criterios de aceptación de la spec."),
        ("feature_coverage", "El prompt satisface cada paso Given/When/Then del feature Gherkin."),
        ("cost_compliance", "El prompt respeta topes de costo: $0.50 por operación, num_frames<=64, num_images<=1."),
        ("clarity", "El prompt es específico, sin ambigüedad, con directivas de composición/estilo."),
        ("platform_fit", "El prompt genera salida apta para la plataforma destino (IG 9:16, reel, etc.)."),
    ]
    steps = _parse_scenario_lines(feature_text)
    system = ("Eres un LLM judge de prompts de creación de contenido. Evalúas OBJETIVAMENTE "
              "cada criterio con un score 0-100. Devuelve SOLO JSON: "
              '{"scores": {"<criterio>": 0-100, ...}, "veredicto": "PASS|FAIL", "razon": "..."}')
    user = (f"# SPEC\n{spec_text}\n\n# FEATURE (GHERKIN)\n{feature_text}\n\n"
            f"# PROMPT A EVALUAR\n{prompt_text}\n\n"
            f"# CRITERIOS A EVALUAR\n" + "\n".join(f"- {k}: {v}" for k, v in criteria))
    raw = None
    for attempt in range(3):
        try:
            raw = _llm(system, user)
            if raw:
                break
        except Exception:
            raw = None
        import time; time.sleep(3 * (attempt + 1))
    if not raw:
        return {"scores": {}, "veredicto": "FAIL", "razon": "API sin respuesta tras 3 intentos"}, criteria
    try:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        result = json.loads(m.group(0) if m else raw)
    except Exception:
        result = {"scores": {}, "veredicto": "FAIL", "razon": raw[:200]}
    return result, criteria

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--feature", required=True)
    ap.add_argument("--min-score", type=int, default=80)
    args = ap.parse_args()
    with open(args.prompt) as f: prompt_text = f.read()
    with open(args.spec) as f: spec_text = f.read()
    with open(args.feature) as f: feature_text = f.read()
    result, criteria = judge(prompt_text, spec_text, feature_text)
    avg = sum(result.get("scores", {}).values()) / max(len(result.get("scores", {})), 1)
    veredicto = "PASS" if result.get("veredicto") == "PASS" and avg >= args.min_score else "FAIL"
    out = {"veredicto": veredicto, "score_promedio": round(avg, 1),
           "scores": result.get("scores", {}), "razon": result.get("razon", ""),
           "modelo": MODEL, "min_aprobacion": args.min_score}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    sys.exit(0 if veredicto == "PASS" else 1)

if __name__ == "__main__":
    main()
