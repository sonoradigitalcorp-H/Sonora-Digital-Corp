#!/usr/bin/env python3
"""RYE conversation engine — conductor unificado (2 capas según principios de Joaquín Ruiz).

Capa 1 — Conocimiento curado (índice): exacto y estable. Lee el índice y los conceptos
  por ruta canónica antes de tocar vectores. Da respuesta determinista y trazable.
Capa 2 — RAG (kb_rye): para "busca dónde se mencionó X" (tickets, logs, corpus grande).

Pipeline por mensaje:
  1. leer índice (saber qué existe → evita "ausencia" y respuestas falsas)
  2. si la consulta matchea un concepto curado → respuesta desde el concepto
  3. si no → rag_search en kb_rye (con metadata de fuente/score)
  4. construir prompt con contexto + regla de vigencia
  5. llm_chat (deepseek-v4-flash) → generar respuesta
  6. engram_save para memoria

Uso:
  python3 tenants/rye/bot/rye_engine.py "alarma SRVO-075 celda 2"
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

TENANT = os.getenv("TENANT_ID", "rye")
KNOWLEDGE = REPO / "tenants" / "rye" / "knowledge"
COLLECTION = "kb_rye"

# --- Capa 1: conocimiento curado ---

def _read_frontmatter_and_body(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = parts[2]
    return {"meta": meta, "body": body, "path": str(path.name)}


def load_index() -> dict:
    """Cargar rye-index.md: lista de conceptos con ruta + tags."""
    idx = _read_frontmatter_and_body(KNOWLEDGE / "rye-index.md")
    return idx


def find_concept(query: str) -> dict | None:
    """Buscar en el índice el concepto que pega con la consulta. Devuelve el archivo."""
    concepts = {
        "fanuc-srvo-alarms.md": ["srvo", "alarma", "fanuc", "servo", "colision", "torque", "srv"],
        "rye-cell-3-spec.md": ["celda 3", "celda3", "celda", "ciclo", "r-2000ic", "soldadura", "throughput", "downtime"],
        "rye-shift-report-format.md": ["reporte de turno", "turno", "reporte", "ciclo de turno", "downtime", "pendientes"],
    }
    q = query.lower()
    best = None
    best_hits = 0
    for fname, keywords in concepts.items():
        hits = sum(1 for kw in keywords if kw in q)
        if hits > best_hits:
            best_hits = hits
            best = fname
    if best and best_hits > 0:
        return _read_frontmatter_and_body(KNOWLEDGE / best)
    return None


# --- Capa 2: RAG ---

def rag_top(query: str, limit: int = 5):
    """Consultar kb_rye en Qdrant. Devuelve hits con fuente/score."""
    from apps.sonora_engine.rag_per_tenant import query_rag
    results = query_rag(TENANT, query, limit=limit)
    return results


# --- Pipeline combinado ---

def build_system_prompt() -> str:
    index = load_index()
    return (
        "Eres el asistente RYE de producción robótica (Iván, RYE Design, Claremore OK). "
        "Responde en español, directo y accionable.\n\n"
        "REGLAS:\n"
        "1. Si la consulta se refiere a un concepto curado del índice, usa LA DEFINICIÓN "
        "del concepto (es exacta y vigente). No la contradigas.\n"
        "2. Si no hay concepto curado, usa el contexto RAG (con su fuente).\n"
        "3. Vigencia: si el RAG contradice a un concepto curado, GANA el concepto curado.\n"
        "4. Si no hay información relevante (ni concepto ni RAG con score suficiente), "
        "dilo claramente y sugiere el manual FANUC oficial o escalar. NO inventes alarmas.\n"
        "5. Cita la fuente: nombre del concepto o del documento RAG.\n"
        "6. Seguridad: SRVO-105/107 y paros de seguridad → escalar y detener.\n\n"
        "CONCEPTOS CURADOS DISPONIBLES:\n" + index["body"]
    )


def answer(query: str, use_llm: bool = True) -> dict:
    result = {"query": query, "concept": None, "rag_hits": [], "response": "", "source": []}

    # Capa 1: concepto curado
    concept = find_concept(query)
    if concept:
        result["concept"] = concept["path"]
        result["source"].append(f"concept:{concept['path']}")
        context = f"[CONCEPTO CURADO {concept['path']}]\n{concept['body']}"
    else:
        context = ""

    # Capa 2: RAG fallback / complemento
    rag_hits = rag_top(query, limit=5)
    rag_ctx = ""
    if rag_hits:
        result["rag_hits"] = [{"source": h.get("source"), "score": round(h["score"], 3)} for h in rag_hits]
        parts = []
        for h in rag_hits:
            if context and h.get("source") == result.get("concept"):
                continue
            parts.append(f"[{h.get('source')} score={h['score']:.2f}]\n{h.get('text')}")
        if parts:
            rag_ctx = "\n---\n".join(parts)

    if not use_llm:
        # Modo sin LLM: devuelve el contexto (útil para verificar el RAG en sí)
        result["response"] = (context + "\n\n" + rag_ctx).strip()
        result["mode"] = "context"
        return result

    # LLM (cliente ligero, sin importar el paquete MCP pesado)
    from apps.sonora_engine.llm_client import llm_chat_sync
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": f"CONSULTA: {query}\n\nCONTEXTO:\n{context}\n\n{rag_ctx}".strip()},
    ]
    data = llm_chat_sync(messages)
    result["response"] = data.get("content", data.get("error", ""))
    result["mode"] = data.get("backend", "llm") if data.get("backend") else "llm"
    result["model"] = data.get("model", "")
    if "error" in data:
        result["mode"] = "error"
        result["rag_hits"] = result["rag_hits"] or ([{"error": data.get("error")}] if "error" in data else [])
    return result


# --- memoria engram ---

def save_memory(query: str, response: str) -> None:
    import sqlite3
    import time
    key = f"qa_{abs(hash(query)) % 1000000}"
    db = Path(os.getenv("ENGRAM_DIR", str(Path(__file__).resolve().parent.parent.parent.parent / "ops" / "state"))) / "engram_rye.db"
    try:
        conn = sqlite3.connect(db, timeout=5)
        conn.execute("""CREATE TABLE IF NOT EXISTS memories
            (key TEXT PRIMARY KEY, layer INTEGER DEFAULT 0, importance INTEGER DEFAULT 1,
             tags TEXT, value TEXT, updated_at REAL)""")
        conn.execute("INSERT OR REPLACE INTO memories (key, layer, importance, tags, value, updated_at) VALUES (?,?,?,?,?,?)",
                     (key, 0, 1, "rye,qa", f"Q: {query} | R: {response[:300]}", time.time()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[save_memory] {e}")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "alarma SRVO-075 celda de soldadura"
    res = answer(query, use_llm=False)
    print("=== RYE Engine (contexto) ===")
    print("Consulta:", res["query"])
    print("Concepto:", res["concept"])
    print("RAG hits:", json.dumps(res["rag_hits"], ensure_ascii=False, indent=2))
    print("Contexto:\n", res["response"][:800])
