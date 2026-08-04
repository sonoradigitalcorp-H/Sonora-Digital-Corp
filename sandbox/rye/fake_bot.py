#!/usr/bin/env python3
"""Fake RYE bot — simulates the conductor for A/B baseline testing (no real LLM/Telegram).

Compares:
  A. baseline (no RAG)  — responde con prompt estático, sin contexto.
  B. rag (context-aware) — busca Qdrant + engram y construye prompt con contexto.

Usage:  python3 sandbox/rye/fake_bot.py
"""
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys_path = str(REPO)
import sys
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from apps.sonora_engine.rag_per_tenant import embed_text, ensure_collection, index_document, query_rag

TENANT = os.getenv("TENANT_ID", "rye")
FIXTURES = REPO / "sandbox" / "rye" / "fixtures" / "fanuc_knowledge.jsonl"

@dataclass
class FakeBot:
    use_rag: bool
    tenant: str = TENANT
    memory: dict = field(default_factory=dict)

    def seed(self):
        """Load fixtures into Qdrant collection kb_<tenant>."""
        ensure_collection(self.tenant)
        for line in FIXTURES.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            index_document(self.tenant, obj["doc_id"], obj["text"],
                           {"source": obj.get("source", ""), "tags": obj.get("tags", ""), "type": obj.get("type", "")})
        # brief wait for upsert propagation
        time.sleep(1)

    def _rag_context(self, query: str, limit: int = 3) -> str:
        hits = query_rag(self.tenant, query, limit=limit)
        if not hits:
            return ""
        parts = [f"[{h['source']}] {h['text']}" for h in hits]
        return "\n---\n".join(parts)

    def respond(self, query: str) -> str:
        if not self.use_rag:
            return "No tengo contexto. Consulta el manual FANUC oficial."
        ctx = self._rag_context(query)
        if not ctx:
            return "No encontré información relevante en mi conocimiento."
        return f"[Contexto RAG]\n{ctx}\n\n[Diagnóstico basado en contexto arriba]"

RESULTS = REPO / "sandbox" / "rye" / "evals" / "ab_baseline.jsonl"

def run_queries():
    queries = [
        "alarma SRVO-075 en celda de soldadura",
        "ciclo de la celda 3",
        "procedimiento de mantenimiento robot",
        "alarma SRVO-032 torque",
        "escalamiento cuando el downtime supera 15 minutos",
    ]
    bots = {
        "baseline": FakeBot(use_rag=False),
        "rag": FakeBot(use_rag=True),
    }
    for b in bots.values():
        b.seed()
    results = []
    for q in queries:
        for variant, bot in bots.items():
            t0 = time.time()
            resp = bot.respond(q)
            ms = round((time.time() - t0) * 1000, 1)
            ctx = bot._rag_context(q) if isinstance(bot, FakeBot) and bot.use_rag else ""
            results.append({
                "query": q,
                "variant": variant,
                "latency_ms": ms,
                "context_length": len(ctx),
                "response": resp[:200],
                "has_context": len(ctx) > 0,
            })
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return results

def report(results):
    print("=== A/B Baseline: RYE Fake Bot ===")
    rag = [r for r in results if r["variant"] == "rag"]
    base = [r for r in results if r["variant"] == "baseline"]
    rag_latency = sum(r["latency_ms"] for r in rag) / len(rag)
    base_latency = sum(r["latency_ms"] for r in base) / len(base)
    rag_ctx = sum(1 for r in rag if r["has_context"])
    print(f"Queries: {len(set(r['query'] for r in results))}")
    print(f"Baseline: {len(base)} respuestas sin contexto (latencia prom {base_latency:.1f}ms)")
    print(f"RAG:      {rag_ctx}/{len(rag)} con contexto (latencia prom {rag_latency:.1f}ms)")
    print(f"Archivo:  {RESULTS}")

if __name__ == "__main__":
    results = run_queries()
    report(results)
