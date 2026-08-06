#!/usr/bin/env python3
"""Integrity tests OKF - ejecutables con python3 (sin dependencias)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
             "..", "..", "..", "03_Agentic_Infrastructure", "Hermes_Agent", "Tools"))
from okf_navigator import load_concepts, match, concept_context, retrieve_context

def test_schema():
    for c in load_concepts():
        for k in ("id", "tenant", "name", "aliases", "definition", "rules", "tables"):
            assert k in c, f"{c.get('id')} sin campo {k}"

def test_valor_exacto_sin_chunking():
    c = match("cuánto cuesta la instalación de antena comercial", "Aztrotech")
    assert c and "3200" in concept_context(c)

def test_aislamiento_tenant():
    ids = [c["id"] for c in load_concepts("Nathaly_Contabilidad")]
    assert "aztrotech.pricing" not in ids

def test_contrato_honestidad():
    r = retrieve_context("MRR de Nathaly en diciembre", "Nathaly_Contabilidad")
    assert r["corpus"] == "none" and "NO TENGO DATOS VERIFICADOS" in r["context"]

if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f(); print(f"✅ {f.__name__}")
    print(f"{len(fns)}/4 integrity tests PASSED")
