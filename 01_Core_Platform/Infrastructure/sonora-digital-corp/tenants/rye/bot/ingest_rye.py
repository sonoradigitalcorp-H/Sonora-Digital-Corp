#!/usr/bin/env python3
"""Ingestión de RYE: indexa knowledge (conceptos curados) + manuals en kb_rye.

Reutiliza el chunking/embeddings de rag_per_tenant. Idempotente (uuid5 por
doc_id+chunk). Carga:
  - tenants/rye/knowledge/**   (conceptos curados, type=concept)
  - tenants/rye/manuals/**     (manuales, type=manual)

Uso:
  EMBED_BACKEND=ollama EMBED_MODEL=all-minilm python3 tenants/rye/bot/ingest_rye.py
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps.sonora_engine.rag_per_tenant import ensure_collection, index_document

TENANT = os.getenv("TENANT_ID", "rye")
DIRS = {
    "concept": REPO / "tenants" / "rye" / "knowledge",
    "manual": REPO / "tenants" / "rye" / "manuals",
}


def read_doc(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # strip frontmatter for indexing (keep body only? keep all, embedding handles it)
    return text


def main():
    ensure_collection(TENANT)
    total = 0
    for kind, directory in DIRS.items():
        if not directory.exists():
            print(f"skip {kind}: {directory} no existe")
            continue
        files = sorted(p for p in directory.glob("*.md") if p.is_file())
        for f in files:
            if f.name.startswith("rye-index") or f.name.startswith("index"):
                continue  # índice no se indexa como fragmento
            text = read_doc(f)
            doc_id = f"{kind}:{f.stem}"
            ok = index_document(TENANT, doc_id, text,
                                {"source": str(f.relative_to(REPO)), "type": kind})
            if ok:
                total += 1
                print(f"  ✓ {kind}: {f.name}")
            else:
                print(f"  ✗ {kind}: {f.name}")
    print(f"\nTotal documentos indexados en kb_rye: {total}")


if __name__ == "__main__":
    main()
