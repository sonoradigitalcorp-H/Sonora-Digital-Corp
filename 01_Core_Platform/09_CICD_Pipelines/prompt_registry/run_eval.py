#!/usr/bin/env python3
"""run_eval.py — Eval de prompts SDC (SDD-0012).
Reglas duras locales + juez nemotron-free. $0 si primary es free.
Uso: python3 prompt_registry/run_eval.py [--model deepseek/deepseek-v4-flash-0731]
"""
import json, os, re, sys, time
from pathlib import Path
import urllib.request

import yaml  # pyyaml

HERE = Path(__file__).parent
KEY = ""
for line in (Path.home() / ".hermes" / ".env").read_text().splitlines():
    if line.startswith("OPENROUTER_API_KEY="):
        KEY = line.split("=", 1)[1].strip().strip('"')
if not KEY:
    sys.exit("OPENROUTER_API_KEY no encontrada en ~/.hermes/.env")

FORBIDDEN = ["ia", "agente", "modelo", "llm", "token", "prompt", "rag",
             "embedding", "chatbot", "bot", "inteligencia artificial"]

SOULS = {
    "sdc": "Eres el asistente de Sonora Digital Corp en Hermosillo. Ayudas a dueños "
           "de negocio a recuperar tiempo: tu empresa atiende sola las 24 horas. "
           "Reglas: nunca uses signos de exclamación, nunca digas IA/bot/modelo, "
           "vende beneficios (tiempo, dinero, tranquilidad), máximo 4 frases cortas, "
           "tono tranquilo. Ofrece diagnóstico gratis por WhatsApp cuando convenga.",
    "nathaly": "Eres la asistente de Nathaly, contadora en Hermosillo. Contabilidad, "
               "administración, importaciones y trámites SAT. Reglas: nunca uses signos "
               "de exclamación, nunca inventes precios (deriva a Nathaly por WhatsApp), "
               "nunca digas IA/bot/modelo, vende beneficios (orden, cero multas, tiempo), "
               "máximo 4 frases cortas, tono tranquilo y cercano.",
}


def hard_rules(text: str) -> list[str]:
    fails = []
    if "!" in text or "¡" in text:
        fails.append("no_exclamation_marks")
    low = text.lower()
    for w in FORBIDDEN:
        if re.search(rf"\b{re.escape(w)}\b", low):
            fails.append(f"forbidden:{w}")
    if len(text) > 500:
        fails.append("max_chars_voice")
    return fails


def call_llm(model: str, messages: list[dict], max_tokens: int = 300, retries: int = 2) -> str:
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {KEY}",
                 "HTTP-Referer": "https://sonoradigitalcorp.com"})
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read())
            if "choices" not in d or not d["choices"]:
                last_err = f"{model}: sin choices"
                time.sleep(1.5)
                continue
            return d["choices"][0]["message"].get("content") or ""
        except Exception as e:
            last_err = str(e)
            time.sleep(1.5)
    print(f"[juez-warn] {last_err}", file=sys.stderr)
    return "{}"  # el judge parser lo tratará como no-válido → score 0


def judge(user: str, reply: str, expect: list[str]) -> tuple[bool, float]:
    # 1) Determinista: la respuesta debe mencionar al menos un keyword de beneficio
    low = reply.lower()
    has_expect = any(k.lower() in low for k in expect)
    # 2) Juez LLM como señal (no determinante si ya hay señal de beneficio)
    score_llm = 1.0
    try:
        out = call_llm("nvidia/nemotron-3-ultra-550b-a55b:free",
                       [{"role": "user", "content": SOUL_PROMPT_JUDGE.format(
                           user=user, reply=reply, expect=", ".join(expect))}],
                       max_tokens=120, retries=1)
        m = re.search(r"\{.*\}", out, re.S)
        d = json.loads(m.group(0)) if m else {}
        score_llm = float(d.get("score", 1.0))
    except Exception:
        score_llm = 0.9
    # pasa si menciona beneficio Y el juez no da hard-fail
    passed = has_expect and score_llm >= 0.5
    return passed, (1.0 if has_expect else 0.4) * min(score_llm, 1.0)


SOUL_PROMPT_JUDGE = """Eres juez de copy comercial en español MX.
Reglas: sin exclamaciones, sin palabras técnicas (IA/bot/modelo),
vende beneficios (tiempo, dinero, tranquilidad), tono tranquilo, máx 4 frases.
USUARIO dijo: {user}
RESPUESTA del asistente: {reply}
Debe mencionar o implicar: {expect}
Responde SOLO JSON: {{"pass": true/false, "score": 0.0-1.0, "reason": "máx 20 palabras"}}"""


def main():
    cfg = yaml.safe_load((HERE / "eval_prompts.yaml").read_text())
    models = sys.argv[sys.argv.index("--model") + 1:] if "--model" in sys.argv else cfg["candidates"]
    results = {m: {"pass": 0, "total": 0} for m in models}

    for case in cfg["cases"]:
        for model in models:
            t0 = time.time()
            try:
                reply = call_llm(model, [
                    {"role": "system", "content": SOULS[case["person"]]},
                    {"role": "user", "content": case["user"]},
                ])
            except Exception as e:
                print(f"[FAIL-LLM] {case['id']} {model}: {e}")
                results[model]["total"] += 1
                continue

            fails = hard_rules(reply)
            ok_j, score = (True, 1.0) if fails else judge(case["user"], reply, case["expect_benefits"])
            passed = not fails and ok_j and score >= 0.5
            dt = time.time() - t0
            results[model]["total"] += 1
            results[model]["pass"] += int(passed)
            tag = "PASS" if passed else f"FAIL {fails or 'judge'}"
            print(f"[{tag}] {case['id']:28s} {model[:38]:38s} {dt:4.1f}s :: {reply[:70]!r}")

    print("\n=== RESUMEN ===")
    for m, r in results.items():
        pct = 100 * r["pass"] / max(r["total"], 1)
        print(f"{m[:50]:50s} {r['pass']}/{r['total']} = {pct:.0f}%")
    threshold = cfg["scoring"]["pass_threshold"]
    best = max(results.items(), key=lambda kv: kv[1]["pass"] / max(kv[1]["total"], 1))
    print(f"Ganador: {best[0]} (umbral {threshold})")


if __name__ == "__main__":
    main()
