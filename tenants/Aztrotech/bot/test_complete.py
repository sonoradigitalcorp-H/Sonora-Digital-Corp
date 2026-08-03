#!/usr/bin/env python3
"""Test completo del sistema AstroTech — Todos los componentes."""
import asyncio
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from lead_classifier import LeadClassifier
from router import ModelRouter
from rag_retriever import create_retriever
import yaml

async def run_all_tests():
    print("=" * 70)
    print("AZTROTECH AI — TEST COMPLETO DEL SISTEMA")
    print("=" * 70)
    
    results = {
        "lead_classifier": {"passed": 0, "failed": 0, "total": 0},
        "model_router": {"passed": 0, "failed": 0, "total": 0},
        "rag_retriever": {"passed": 0, "failed": 0, "total": 0},
        "tts_server": {"passed": 0, "failed": 0, "total": 0},
    }
    
    # ── LEAD CLASSIFIER ──────────────────────────────────────────
    print("\n1. LEAD CLASSIFIER")
    print("-" * 70)
    
    classifier = LeadClassifier(use_llm=False)
    test_cases = [
        ("Hola", "cold"),
        ("Me interesa el empleado digital", "warm"),
        ("Quiero contratar YA", "hot"),
        ("¿Cuánto cuesta?", "warm"),
        ("Necesito algo ya, me urge", "hot"),
        ("Solo estoy viendo", "cold"),
        ("Tengo una tienda y quiero automatizar", "warm"),
        ("Mi presupuesto es 15k al mes", "hot"),
    ]
    
    for msg, expected in test_cases:
        result = await classifier.classify([msg])
        ok = result.tipo == expected
        results["lead_classifier"]["total"] += 1
        if ok:
            results["lead_classifier"]["passed"] += 1
        else:
            results["lead_classifier"]["failed"] += 1
        status = "PASS" if ok else "FAIL"
        print(f"  {status} [{result.tipo:4s}] {msg[:50]}")
    
    # ── MODEL ROUTER ─────────────────────────────────────────────
    print("\n2. MODEL ROUTER")
    print("-" * 70)
    
    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml")) as f:
        config = yaml.safe_load(f)
    
    router = ModelRouter(config)
    router_cases = [
        ("Hola, ¿qué servicios ofrecen?", "deepseek/deepseek-v4-flash"),
        ("Analiza las ventajas de automatizar", "z-ai/glm-5.2"),
        ("Programa un sistema de inventario", "moonshotai/kimi-k2.7-code"),
    ]
    
    for msg, expected in router_cases:
        result = router.select_model(msg)
        ok = result == expected
        results["model_router"]["total"] += 1
        if ok:
            results["model_router"]["passed"] += 1
        else:
            results["model_router"]["failed"] += 1
        status = "PASS" if ok else "FAIL"
        print(f"  {status} {msg[:40]:40s} -> {result}")
    
    # ── RAG RETRIEVER ────────────────────────────────────────────
    print("\n3. RAG RETRIEVER")
    print("-" * 70)
    
    try:
        rag = create_retriever("aztrotech")
        health = rag.health()
        ok = health["ok"]
        results["rag_retriever"]["total"] += 1
        if ok:
            results["rag_retriever"]["passed"] += 1
        else:
            results["rag_retriever"]["failed"] += 1
        status = "PASS" if ok else "FAIL"
        print(f"  {status} Health: {health}")
        
        # Test search
        chunks = rag.search("¿Qué servicios ofrece Aztrotech?", top_k=3)
        ok = len(chunks) > 0
        results["rag_retriever"]["total"] += 1
        if ok:
            results["rag_retriever"]["passed"] += 1
        else:
            results["rag_retriever"]["failed"] += 1
        status = "PASS" if ok else "FAIL"
        print(f"  {status} Search: {len(chunks)} chunks found")
        
        for i, chunk in enumerate(chunks):
            print(f"    Chunk {i+1}: score={chunk.score:.3f} source={chunk.source}")
            
    except Exception as e:
        results["rag_retriever"]["total"] += 1
        results["rag_retriever"]["failed"] += 1
        print(f"  FAIL Error: {e}")
    
    # ── TTS SERVER ───────────────────────────────────────────────
    print("\n4. TTS SERVER")
    print("-" * 70)
    
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        # Health check
        try:
            resp = await client.get("http://localhost:8765/health")
            ok = resp.status_code == 200
            results["tts_server"]["total"] += 1
            if ok:
                results["tts_server"]["passed"] += 1
            else:
                results["tts_server"]["failed"] += 1
            status = "PASS" if ok else "FAIL"
            print(f"  {status} Health: {resp.json()}")
        except Exception as e:
            results["tts_server"]["total"] += 1
            results["tts_server"]["failed"] += 1
            print(f"  FAIL Health: {e}")
        
        # Generate audio
        try:
            resp = await client.post("http://localhost:8765/tts", json={
                "text": "Hola, bienvenido a Aztrotech",
                "voice": "cesar"
            })
            ok = resp.status_code == 200 and resp.json().get("size", 0) > 10000
            results["tts_server"]["total"] += 1
            if ok:
                results["tts_server"]["passed"] += 1
            else:
                results["tts_server"]["failed"] += 1
            status = "PASS" if ok else "FAIL"
            print(f"  {status} TTS generate: {resp.json().get('size', 0)} bytes")
        except Exception as e:
            results["tts_server"]["total"] += 1
            results["tts_server"]["failed"] += 1
            print(f"  FAIL TTS: {e}")
    
    # ── SUMMARY ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for component, r in results.items():
        total_passed += r["passed"]
        total_failed += r["failed"]
        total_tests += r["total"]
        status = "PASS" if r["failed"] == 0 else "FAIL"
        accuracy = (r["passed"] / r["total"] * 100) if r["total"] > 0 else 0
        print(f"  {status} {component:20s}: {r['passed']}/{r['total']} ({accuracy:.1f}%)")
    
    print("-" * 70)
    overall_accuracy = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"  TOTAL: {total_passed}/{total_tests} ({overall_accuracy:.1f}%)")
    print("=" * 70)
    
    return total_failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
