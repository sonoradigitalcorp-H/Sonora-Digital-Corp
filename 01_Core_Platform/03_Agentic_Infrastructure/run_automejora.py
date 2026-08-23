#!/usr/bin/env python3
"""
run_automejora.py — Loop de automejora de prompts (FASE 7 Skill nativa SDC).
Lee resultados de evals, los persiste en Postgres metrics_eval, detecta fallos
recurrentes por persona y genera propuestas de mejora de prompt.

Dos modos:
  - Modo observación (default): corre las evals y guarda en Postgres metrics_eval.
  - Modo propuesta: analiza fallos históricos y sugiere mejoras de prompt via LLM.

Uso:
  /opt/hermes/venv/bin/python3 /opt/hermes/scripts/run_automejora.py            # observación
  /opt/hermes/venv/bin/python3 /opt/hermes/scripts/run_automejora.py --suggest  # propuestas

Cron sugerido: cada hora (hora 3): observación. Semanal (domingo 5): --suggest.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
# El run_eval vive en 01_Core_Platform/09_CICD_Pipelines/prompt_registry/
REPO_ROOT = Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo")
RUN_EVAL = REPO_ROOT / "01_Core_Platform/09_CICD_Pipelines/prompt_registry/run_eval.py"

PG_PASSWORD = os.environ.get("METRICS_DB_PASSWORD", "changeme_secure_metrics_password")
PG_USER = os.environ.get("METRICS_PG_USER", "metrics")
PG_DB = os.environ.get("METRICS_PG_DB", "metrics")


def psql(cmd: str) -> str:
    """Ejecuta SQL en postgres-metrics via docker exec."""
    full = f"docker exec postgres-metrics psql -U {PG_USER} -d {PG_DB} -h localhost -c \"{cmd}\""
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
    return r.stdout + r.stderr


def get_openrouter_key() -> str:
    env_file = Path.home() / ".hermes" / ".env"
    for line in env_file.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    return os.environ.get("OPENROUTER_API_KEY", "")


def run_eval_and_capture() -> list[dict]:
    """Ejecuta run_eval.py, captura resultados de casos en una lista de registros."""
    # run_eval.py imprime a stdout con formato. Lo ejecutamos y parseamos líneas PASS/FAIL.
    key = get_openrouter_key()
    if not key:
        print("[automejora] sin OPENROUTER_API_KEY, skip", file=sys.stderr)
        return []
    # El run_eval lee la key de ~/.hermes/.env directamente.
    cmd = ["/opt/hermes/venv/bin/python3", str(RUN_EVAL)]
    # run_eval usa la key de ~/.hermes/.env, así que solo lo lanzamos.
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        output = r.stdout
    except Exception as e:
        print(f"[automejora] error ejecutando eval: {e}", file=sys.stderr)
        return []

    records = []
    for line in output.splitlines():
        if "[PASS]" in line or "[FAIL" in line:
            # Formato: [PASS|FAIL ...] id  model  time :: reply
            m = re.search(r"\[(PASS|FAIL[^\]]*)\]\s+(\S+)\s+(\S+)", line)
            if m:
                status = m.group(1)
                case_id = m.group(2)
                model = m.group(3)
                records.append({
                    "case_id": case_id, "model": model,
                    "passed": status == "PASS",
                    "reason": status if status != "PASS" else "",
                    "ts": datetime.now().isoformat(),
                })
    return records


def persist_evals(records: list[dict]):
    """Guarda cada resultado en metrics_eval de Postgres."""
    n = 0
    for rec in records:
        score = 1.0 if rec["passed"] else 0.0
        psql(
            f"INSERT INTO metrics_eval (persona, eval_type, score, passed, details) VALUES "
            f"('{rec.get('case_id','?').split('_')[0]}', 'prompt', {score}, "
            f"{'true' if rec['passed'] else 'false'}, "
            f"'{{\"case\": \"{rec['case_id']}\", \"model\": \"{rec['model']}\"}}');"
        )
        n += 1
    if n:
        print(f"[automejora] guardados {n} evals en metrics_eval")
    return n


def suggest_improvements() -> list[dict]:
    """Analiza fallos recientes por persona y genera propuestas de mejora de prompt."""
    key = get_openrouter_key()
    if not key:
        return []
    # Recolecta fallos de metrics_eval de las últimas 24h
    out = psql(
        "SELECT persona, COUNT(*) FROM metrics_eval WHERE passed=false "
        "AND timestamp > NOW() - INTERVAL '24 hours' GROUP BY persona;"
    )
    failures = {}
    for m in re.finditer(r"(\w+)\s*\|\s*(\d+)", out):
        failures[m.group(1)] = int(m.group(2))
    if not failures:
        print("[automejora] sin fallos recientes, no hay propuestas")
        return []

    persona = max(failures, key=failures.get)
    # Generamos un prompt de mejora para la persona con más fallos.
    body = json.dumps({
        "model": "deepseek/deepseek-v4-flash-0731",
        "messages": [
            {"role": "system", "content": (
                "Eres un especialista en prompt engineering para asistentes de voz "
                "y chat en español (México). Reglas duras: sin exclamaciones, sin "
                "palabras técnicas (IA/bot/modelo), vender beneficios, tono tranquilo, "
                "máximo 4 frases, cierre con CTA. Si la persona es tubandera: sin "
                "diagnóstico médico, derivar a humano/911 ante crisis, ofrecer "
                "diagnóstico gratis, cerrar con valoración/agendar/Roberto.")},
            {"role": "user", "content": (
                f"La persona '{persona}' está fallando {failures[persona]} evals hoy. "
                "Propón 3 mejoras concretas al system prompt para elevar el score. "
                "Regresa SOLO JSON: {\"mejoras\": [\"...3 textos...\"], "
                "\"raiz\": \"causa raíz probable en 20 palabras\"}")},
        ],
        "max_tokens": 500,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}",
                 "HTTP-Referer": "https://sonoradigitalcorp.com"})
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            d = json.loads(resp.read())
        content = d["choices"][0]["message"].get("content") or ""
        m = re.search(r"\{.*\}", content, re.S)
        return [{"persona": persona, "failures": failures[persona], **json.loads(m.group(0) if m else "{}")}]
    except Exception as e:
        print(f"[automejora] error propuesta: {e}", file=sys.stderr)
        return []


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "observe"
    if mode == "suggest":
        props = suggest_improvements()
        if props:
            print("[automejora] Propuestas:", json.dumps(props, ensure_ascii=False, indent=2))
        return
    # Modo observación
    records = run_eval_and_capture()
    if records:
        persist_evals(records)
        passed = sum(1 for r in records if r["passed"])
        print(f"[automejora] {passed}/{len(records)} PASS")
    else:
        # Si no corre eval (key no disponible), al menos registra un health pulse.
        psql("INSERT INTO metrics_health (service, status) VALUES ('automejora', 'no-op');")


if __name__ == "__main__":
    main()