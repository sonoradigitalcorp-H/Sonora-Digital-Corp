#!/usr/bin/env python3
"""OKF Navigator - capa de conocimiento EXACTO de Sonora Digital Corp.
Navega conceptos estructurados completos. Cero chunking, cero similitud."""
import os, sys, json

OKF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "Databases", "OKF_Knowledge", "concepts")

def _norm(t): return (t or "").lower().replace(" ", "_")

def load_concepts(tenant=None):
    out = []
    if not os.path.isdir(OKF_DIR): return out
    for f in sorted(os.listdir(OKF_DIR)):
        if f.endswith(".json"):
            with open(os.path.join(OKF_DIR, f)) as fh:
                c = json.load(fh)
            if c and (tenant is None or _norm(c.get("tenant")) == _norm(tenant)):
                out.append(c)
    return out

def get_concept(concept_id):
    for c in load_concepts():
        if c.get("id") == concept_id: return c
    return None

def match(question, tenant=None, min_score=1):
    q = question.lower()
    best, best_score = None, 0
    for c in load_concepts(tenant):
        score = sum(1 for a in c.get("aliases", []) if a.lower() in q)
        if score > best_score: best, best_score = c, score
    return best if best_score >= min_score else None

def concept_context(c): return json.dumps(c, ensure_ascii=False, indent=2)

def _relevant(question, rag_text):
    """Puerta de relevancia: la memoria RAG solo es contexto si comparte términos
    con la pregunta. Sin solapamiento => irrelevante => no daño (honestidad)."""
    qw = set(w for w in question.lower().split() if any(ch.isalnum() for ch in w))
    rw = set(w for w in rag_text.lower().split() if any(ch.isalnum() for ch in w))
    return len(qw & rw) >= 1

def retrieve_context(question, tenant):
    """Enrutamiento Corpus: okf (exacto) -> rag (experiencial, si relevante) -> none (honesto)."""
    c = match(question, tenant)
    if c:
        return {"corpus": "okf", "concept_id": c["id"], "context": concept_context(c)}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from engram_memory import query_memory
        rag = query_memory(question, tenant)
        if rag and not rag.startswith(("No hay memoria", "Sin resultados")) and _relevant(question, rag):
            return {"corpus": "rag", "concept_id": None,
                    "context": rag + " [fuente experiencial: aproximada, verificar]"}
    except Exception:
        pass
    return {"corpus": "none", "concept_id": None,
            "context": "NO TENGO DATOS VERIFICADOS. Prohibido inventar cálculos."}
