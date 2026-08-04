#!/usr/bin/env python3
"""Verify the full LLM + RAG + Engram stack end-to-end for a tenant.

Checks, in order:
  1. Qdrant reachable (:6333)
  2. Engram CLI present
  3. Embeddings: FastEmbed model loads and produces 384-dim vectors
  4. RAG index: index_document() writes a chunk to kb_<tenant>
  5. RAG query: query_rag() retrieves the chunk with semantic similarity
  6. Engram memory: engram save + search round-trip

Usage:
  python3 scripts/verify_rag_stack.py [tenant_id]
  TENANT_ID=rye python3 scripts/verify_rag_stack.py
"""

import json
import os
import shutil
import sys
import time

TENANT_ID = os.getenv("TENANT_ID", sys.argv[1] if len(sys.argv) > 1 else "rye")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-minilm")
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "ollama")
EMBED_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

# Asegurar que el repo está en sys.path (imports de apps.sonora_engine.*, skills.mcp.*)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

PASS, FAIL = "✅", "❌"
fails = []


def check(name, ok, detail=""):
    status = PASS if ok else FAIL
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)
    return ok


def main():
    print(f"=== Verify RAG stack — tenant: {TENANT_ID} ===")
    print(f"Qdrant: {QDRANT_URL}")
    print(f"Embed model: {EMBED_MODEL}")
    print()

    # 1. Qdrant reachable
    print("1. Vector store (Qdrant)")
    try:
        import httpx
        r = httpx.get(f"{QDRANT_URL}/healthz", timeout=5)
        check("Qdrant healthz", r.status_code == 200, r.text.strip()[:40])
    except Exception as e:
        check("Qdrant healthz", False, str(e))

    # 1b. Embedding backend reachable (Ollama local o FastEmbed)
    print("\n1b. Embedding backend (local)")
    try:
        import httpx
        r = httpx.post(f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/embeddings",
                       json={"model": EMBED_MODEL, "prompt": "test"}, timeout=15)
        v = r.json().get("embedding", [])
        check("embeddings backend responds", r.status_code == 200 and len(v) > 0,
              f"model={EMBED_MODEL}, dims={len(v)}")
    except Exception as e:
        check("embeddings backend responds", False, str(e))

    # 2. Engram CLI
    print("\n2. Memory (Engram)")
    engram_bin = shutil.which("engram")
    check("engram CLI present", engram_bin is not None, engram_bin or "")

    # 3. Embeddings
    print("\n3. Embeddings (local)")
    from apps.sonora_engine.rag_per_tenant import (
        embed_text,
        ensure_collection,
        index_document,
        query_rag,
    )
    try:
        vec = embed_text("alarma SRVO-075 en celda de soldadura")
        check("embed_text produces {} dims".format(EMBED_DIM), len(vec) == EMBED_DIM, f"dims={len(vec)}")
    except Exception as e:
        check("embed_text produces {} dims".format(EMBED_DIM), False, str(e))

    # 4. RAG index + query
    print("\n4. RAG index/query (Qdrant kb_{tenant})")
    ok_ensure = ensure_collection(TENANT_ID)
    check("collection kb_{} ready".format(TENANT_ID.replace("-", "_")), True,
          "created" if ok_ensure else "exists")

    doc_id = "verify-fixed-doc"  # fixed id -> idempotent upsert, no polluting kb_rye
    sample = (
        "SRVO-075 es una alarma de FANUC de colisión o sobrecarga del servo. "
        "Verificar la zona de trabajo, revisar collision detect y reiniciar con Reset "
        "después de liberar el robot. Aplicable a los robots R-2000iC en las celdas "
        "de soldadura de RYE para líneas automotrices BMW y Rivian."
    )
    ok_index = index_document(TENANT_ID, doc_id, sample, {"source": "verify_rag_stack"})
    check("index_document()", ok_index)

    time.sleep(1)
    # Robust check: query with the exact indexed text tokens + high limit so the
    # freshly-indexed doc reliably appears even alongside the loaded corpus.
    results = query_rag(TENANT_ID, "SRVO-075 sobrecarga servo R-2000iC reset collision", limit=20)
    hit = any(r.get("doc_id") == doc_id for r in results)
    check("query_rag() retrieves indexed doc", hit,
          f"{len(results)} hits, top score={results[0]['score'] if results else 'n/a'}")

    # 5. Engram round-trip (per-tenant SQLite, same path the agents use)
    print("\n5. Engram memory round-trip")
    try:
        from skills.mcp.servers.sdc_mcp_stdio import engram_get, engram_save, engram_search
        import json as _json

        key = f"verify_{TENANT_ID}_{int(time.time())}"
        save_out = _json.loads(engram_save(TENANT_ID, key, "alarma SRVO-075 diagnostico de prueba", tags="verify"))
        check("engram_save", save_out.get("saved") is True, f"id={save_out.get('id')}")

        get_out = _json.loads(engram_get(TENANT_ID, key))
        check("engram_get", get_out.get("found") is True, f"value={get_out.get('value', '')[:40]}")

        search_out = _json.loads(engram_search(TENANT_ID, "SRVO-075", limit=5))
        hit = any(m.get("key") == key for m in search_out.get("results", []))
        check("engram_search finds memory", hit, f"{len(search_out.get('results', []))} results")
    except Exception as e:
        check("engram round-trip", False, str(e))

    print()
    if fails:
        print(f"❌ VERIFY FAILED — {len(fails)} checks failed: {', '.join(fails)}")
        sys.exit(1)
    print("✅ VERIFY PASSED — stack LLM+RAG+engram funcional para tenant '{}'".format(TENANT_ID))
    print("   (llm_chat no se prueba aquí; usa sdc-mcp-local o OpenRouter directo)")


if __name__ == "__main__":
    main()
