#!/usr/bin/env python3
"""Eval de 3 columnas (como el vídeo): RAG-only / OKF-only / Híbrido."""
import os, sys, json
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "..", "..", "03_Agentic_Infrastructure", "Hermes_Agent", "Tools"))
import okf_navigator as okf
try:
    import engram_memory as engram
except Exception:
    engram = None

suite = json.load(open(os.path.join(BASE, "okf_eval_suite.json")))
scores = {"rag": 0, "okf": 0, "hybrid": 0}
lines = []
for e in suite:
    q, t, want = e["question"], e["tenant"], e
    rag_c = ""
    if engram:
        try: rag_c = engram.query_memory(q, t)
        except Exception: rag_c = ""
    c = okf.match(q, t)
    okf_c = okf.concept_context(c) if c else ""
    hy = okf.retrieve_context(q, t)
    pr = want["contains"] in rag_c
    po = want["contains"] in okf_c
    ph = (want["contains"] in hy["context"]) or (want["expected_corpus"] == "none" and hy["corpus"] == "none")
    scores["rag"] += pr; scores["okf"] += po; scores["hybrid"] += ph
    lines.append(f"{q[:45]:47s} | RAG {'PASS' if pr else 'FAIL'} | OKF {'PASS' if po else 'FAIL'} | HYBRID {'PASS' if ph else 'FAIL'} (corpus={hy['corpus']})")

out = "\n".join(lines) + f"\n\nTOTAL: RAG {scores['rag']}/6 · OKF {scores['okf']}/6 · RAG+OKF {scores['hybrid']}/6"
print(out)
open(os.path.join(BASE, "resultados.txt"), "w").write(out + "\n")
