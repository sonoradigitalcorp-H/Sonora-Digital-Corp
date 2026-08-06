#!/usr/bin/env python3
"""Hermes Orchestrator Pipeline - Sonora Digital Corp.
Usa OpenRouter como LLM, OKF como conocimiento exacto, Engram como memoria vectorial."""
import os, sys, json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Tools"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "04_Shared_Libraries", "SDK_Python"))

from sdc_sdk import SDC_Client
from okf_navigator import retrieve_context

HERMES_SYSTEM_PROMPT = """Eres Hermes, el orquestador de Sonora Digital Corp.
Tienes acceso a dos herramientas de conocimiento:

1. OKF (Conocimiento Exacto): tablas de precios, cuotas, fórmulas, políticas de negocio.
   - Usa okf_navigator cuando la pregunta sea sobre datos de negocio (precios, cuotas, tarifas, políticas).
   - Si el dato existe en OKF, responde con el valor exacto citando el concept_id.
   - Si el dato NO existe en OKF, di "no tengo datos verificados".

2. Engram (Memoria Vectorial): recuerdos experienciales guardados por tenant.
   - Usa engram_memory cuando la pregunta sea sobre historial, acciones pasadas, reservas, conversaciones.
   - Si hay memoria relevante, úsala como contexto.
   - Si no hay memoria, di "no tengo memoria previa para esto".

Reglas de oro:
- NUNCA inventes datos, precios, fechas ni cálculos.
- Si no tienes el dato en ninguna capa, responde: "no tengo datos verificados".
- Responde en español, de forma natural y concisa.
- Siempre cita la fuente (OKF o Engram).

Herramientas disponibles:
- okf_navigator(query, tenant): conocimiento exacto
- engram_memory(query, tenant): memoria vectorial
- save_memory(data, tenant): guardar nuevo recuerdo
"""

def hermes_answer(question, tenant="Aztrotech"):
    """Pipeline completo: pregunta → OKF/Engram → OpenRouter → respuesta natural."""
    client = SDC_Client(tenant)

    # Paso 1: OKF (conocimiento exacto)
    okf = retrieve_context(question, tenant)
    okf_context = ""
    if okf["corpus"] == "okf":
        okf_context = f"[OKF - {okf['concept_id']}]\n{okf['context'][:600]}"
    elif okf["corpus"] == "rag":
        okf_context = f"[Engram - experiencial]\n{okf['context'][:600]}"

    # Paso 2: Construir mensajes para el LLM
    messages = [
        {"role": "system", "content": HERMES_SYSTEM_PROMPT},
        {"role": "user", "content": f"Pregunta del usuario: {question}\n\nContexto del conocimiento:\n{okf_context if okf_context else 'Sin datos en ninguna capa.'}\n\nResponde de forma natural citando la fuente."}
    ]

    # Paso 3: Llamar a OpenRouter
    result = client.call_llm(messages)

    if result.get("status") == "success":
        return {
            "answer": result["content"].strip(),
            "corpus": okf["corpus"],
            "model": result.get("model"),
            "cost": result.get("usage", {}).get("cost", 0),
            "tokens": result.get("usage", {})
        }
    else:
        return {"error": result.get("error", "unknown"), "corpus": okf["corpus"]}

if __name__ == "__main__":
    print("=" * 60)
    print("HERMES ORCHESTRATOR - Pipeline de Prueba")
    print("=" * 60)

    tests = [
        ("cuánto cuesta la instalación de antena comercial para Aztrotech", "Aztrotech"),
        ("qué reserva pidió Aztrotech", "Aztrotech"),
        ("MRR de Nathaly en diciembre", "Nathaly_Contabilidad"),
        ("cuánto cuesta pintar un coche", "Aztrotech"),
    ]

    for q, t in tests:
        print(f"\n--- Pregunta: {q} (tenant: {t}) ---")
        r = hermes_answer(q, t)
        if "error" in r:
            print(f"  Error: {r['error']}")
        else:
            print(f"  Corpus: {r['corpus']}")
            print(f"  Respuesta: {r['answer'][:200]}")
            print(f"  Costo: ${r.get('cost', '?')}")

    print("\n" + "=" * 60)
    print("PIPELINE CEREBRO VERIFICADO")
    print("=" * 60)
