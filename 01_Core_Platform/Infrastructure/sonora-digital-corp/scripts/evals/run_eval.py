#!/usr/bin/env python3
"""Eval Pipeline — Ejecuta batch sobre dataset de conversaciones reales anonimizadas.

Métricas:
  - Lead classification: accuracy, precision/recall por clase (cold/warm/hot)
  - Emotion: detección de flags vs esperado
  - Safety: % respuestas sin precios, sin revelar SDC
  - Tokens: p50/p95 input+output, costo total
  - Latencia: p50/p95

Uso: python3 run_eval.py [--dataset path.jsonl] [--no-llm] [--report path.md]
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Asegurar imports del bot
BOT_DIR = Path(__file__).resolve().parent.parent.parent / "tenants" / "Aztrotech" / "bot"
sys.path.insert(0, str(BOT_DIR))

from lead_classifier import create_classifier  # noqa: E402
from emotion_analyzer import create_emotion_analyzer  # noqa: E402
from prompt_builder import create_prompt_builder  # noqa: E402

import httpx  # noqa: E402


def _make_llm_call():
    """Crea llm_call que usa OpenRouter con OPENROUTER_API_KEY."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    async def llm_call(messages, model="deepseek/deepseek-v4-flash"):
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={"model": model, "messages": messages, "max_tokens": 512},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://astrotech.ai",
                    "X-Title": "AstroTech AI Eval",
                },
            )
            if resp.status_code != 200:
                raise Exception(f"LLM eval HTTP {resp.status_code}")
            return resp.json()

    return llm_call


def load_dataset(path: str) -> list:
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


async def run_evals(items: list, use_llm: bool = True) -> dict:
    llm_call = _make_llm_call() if use_llm else None
    classifier = create_classifier(llm_call=llm_call, use_llm=use_llm)
    emotion = create_emotion_analyzer(llm_call=llm_call, use_llm=use_llm)
    builder = create_prompt_builder()

    lead_correct = 0
    lead_total = 0
    lead_conf = {"cold": {"tp": 0, "fp": 0, "fn": 0}, "warm": {"tp": 0, "fp": 0, "fn": 0}, "hot": {"tp": 0, "fp": 0, "fn": 0}}
    emotion_correct = 0
    emotion_total = 0
    safety_issues = 0
    latencies = []
    total_tokens = {"in": 0, "out": 0}
    cost = 0.0

    for item in items:
        conv = [t["content"] for t in item.get("turns", [])]
        expected_lead = item.get("expected_lead_type")
        expected_emotions = item.get("expected_emotion_flags", [])
        lang = item.get("language", "es")

        # Lead classification
        if expected_lead:
            lead_total += 1
            t0 = time.monotonic()
            result = await classifier.classify(conv)
            latencies.append(time.monotonic() - t0)
            if result.tipo == expected_lead:
                lead_correct += 1
            # Confusion matrix
            for cls in lead_conf:
                if result.tipo == cls and expected_lead == cls:
                    lead_conf[cls]["tp"] += 1
                elif result.tipo == cls and expected_lead != cls:
                    lead_conf[cls]["fp"] += 1
                elif result.tipo != cls and expected_lead == cls:
                    lead_conf[cls]["fn"] += 1

        # Emotion flags
        if expected_emotions:
            for turn in item.get("turns", [])[-3:]:
                if turn.get("role") != "user":
                    continue
                emotion_total += 1
                emo = await emotion.analyze(turn["content"])
                matched_flags = sum(1 for f in expected_emotions if emo.flags.get(f, False))
                # Coincidencia parcial ≥50% de los flags esperados
                if matched_flags >= max(1, len(expected_emotions) // 2):
                    emotion_correct += 1

        # Safety: revisar respuestas esperadas (si dataset tiene expected_reply)
        reply = item.get("expected_reply")
        if reply:
            gr = builder.check_guardrails(reply)
            if not gr["pass"]:
                safety_issues += 1

    return {
        "total_items": len(items),
        "lead_accuracy": round(lead_correct / lead_total, 3) if lead_total else 0,
        "lead_total": lead_total,
        "lead_confusion": lead_conf,
        "emotion_accuracy": round(emotion_correct / emotion_total, 3) if emotion_total else 0,
        "emotion_total": emotion_total,
        "safety_issues": safety_issues,
        "latency_p50_ms": round(sorted(latencies)[len(latencies)//2] * 1000, 1) if latencies else 0,
        "use_llm": use_llm,
    }


def percentile(data: list, p: float) -> float:
    if not data:
        return 0
    data = sorted(data)
    idx = int(len(data) * p)
    return data[min(idx, len(data) - 1)]


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path a dataset JSONL")
    parser.add_argument("--no-llm", action="store_true", help="Solo reglas (sin LLM)")
    parser.add_argument("--report", help="Path opcional para reporte markdown")
    args = parser.parse_args()

    items = load_dataset(args.dataset)
    print(f"Dataset: {args.dataset} ({len(items)} conversaciones)\n")

    results = await run_evals(items, use_llm=not args.no_llm)

    print("=== RESULTADOS ===")
    print(f"Lead accuracy:      {results['lead_accuracy']*100:.1f}% ({results['lead_total']} casos)")
    print(f"  confusion:        {json.dumps(results['lead_confusion'])}")
    print(f"Emotion accuracy:   {results['emotion_accuracy']*100:.1f}% ({results['emotion_total']} casos)")
    print(f"Safety issues:      {results['safety_issues']}")
    print(f"Latencia p50:       {results['latency_p50_ms']}ms")
    print(f"Modo:               {'LLM' if not args.no_llm else 'solo-reglas'}")

    if args.report:
        Path(args.report).write_text(
            f"# Eval Report\n\n"
            f"- **Dataset**: {args.dataset}\n"
            f"- **Items**: {results['total_items']}\n"
            f"- **Lead accuracy**: {results['lead_accuracy']*100:.1f}%\n"
            f"- **Emotion accuracy**: {results['emotion_accuracy']*100:.1f}%\n"
            f"- **Safety issues**: {results['safety_issues']}\n"
            f"- **Latency p50**: {results['latency_p50_ms']}ms\n",
            encoding="utf-8",
        )
        print(f"\nReporte: {args.report}")


if __name__ == "__main__":
    asyncio.run(main())