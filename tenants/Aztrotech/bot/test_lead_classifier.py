#!/usr/bin/env python3
"""Test del Lead Classifier — cold/warm/hot sin servicios externos."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lead_classifier import LeadClassifier, LeadClassification

async def test_lead_classifier():
    classifier = LeadClassifier(use_llm=False)
    
    cases = [
        # COLD
        ("Hola", "cold"),
        ("Buenas tardes, ¿qué es Aztrotech?", "cold"),
        ("Solo estoy viendo, gracias", "cold"),
        ("Está muy caro, olvídalo", "cold"),
        ("No me interesa, gracias", "cold"),
        ("", "cold"),
        ("👍", "cold"),
        
        # WARM
        ("Me interesa el empleado digital", "warm"),
        ("¿Cuánto cuesta?", "warm"),
        ("Tengo una tienda de ropa en Hermosillo", "warm"),
        ("Ya uso otra herramienta pero quiero comparar", "warm"),
        ("Mis clientes se van porque no contesto a tiempo", "warm"),
        ("¿Cómo funciona el sistema de ventas?", "warm"),
        ("Tengo una clínica dental y necesito automatizar", "warm"),
        ("Soy dueño de un restaurante y pierdo pedidos por no contestar", "warm"),
        
        # HOT
        ("Quiero contratar YA", "hot"),
        ("Mi presupuesto es 15k al mes", "hot"),
        ("Empezamos el lunes", "hot"),
        ("Necesito algo ya, me urge", "hot"),
        ("Necesito contratar el empleado digital YA, tengo 20k de presupuesto", "hot"),
        ("Manden el contrato, estoy listo", "hot"),
        
        # ENGLISH
        ("Hello, what do you do?", "cold"),
        ("I'm interested in your automation service for my restaurant", "warm"),
        ("I need this now, my budget is ready", "hot"),
    ]
    
    passed = 0
    failed = 0
    total = len(cases)
    
    print("=" * 70)
    print("LEAD CLASSIFIER TEST — 24 casos cold/warm/hot")
    print("=" * 70)
    
    for msg, expected in cases:
        result = await classifier.classify([msg])
        ok = result.tipo == expected
        status = "PASS" if ok else "FAIL"
        
        if ok:
            passed += 1
        else:
            failed += 1
        
        emoji = {"cold": "🔵", "warm": "🟡", "hot": "🔴"}[result.tipo]
        print(f"  {status} {emoji} [{result.tipo:4s}] conf={result.confianza:.2f} | {msg[:50]}")
        if not ok:
            print(f"         esperado: {expected}")
    
    print("=" * 70)
    accuracy = (passed / total) * 100
    print(f"Resultado: {passed}/{total} passed ({accuracy:.1f}%)")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(test_lead_classifier())
    sys.exit(0 if success else 1)
