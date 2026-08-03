#!/usr/bin/env python3
"""Test del ModelRouter — selección de modelos y rate limits."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import yaml
from router import ModelRouter

def test_router():
    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml")) as f:
        config = yaml.safe_load(f)
    
    router = ModelRouter(config)
    
    print("=" * 70)
    print("MODEL ROUTER TEST")
    print("=" * 70)
    
    # Test model selection
    cases = [
        ("Hola, ¿qué servicios ofrecen?", "deepseek/deepseek-v4-flash"),
        ("Analiza las ventajas de automatizar", "z-ai/glm-5.2"),
        ("Programa un sistema de inventario", "moonshotai/kimi-k2.7-code"),
        ("¿Cuánto cuesta?", "deepseek/deepseek-v4-flash"),
        ("Compara los planes", "z-ai/glm-5.2"),
        ("Desarrolla una API REST", "moonshotai/kimi-k2.7-code"),
    ]
    
    passed = 0
    failed = 0
    
    for msg, expected in cases:
        result = router.select_model(msg)
        ok = result == expected
        status = "PASS" if ok else "FAIL"
        
        if ok:
            passed += 1
        else:
            failed += 1
        
        print(f"  {status} {msg[:40]:40s} -> {result}")
        if not ok:
            print(f"         esperado: {expected}")
    
    # Test rate limits
    print("\n  Rate Limits:")
    for pkg in ["despertar", "elevar", "soberano"]:
        limits = router.get_rate_limits(pkg)
        print(f"    {pkg}: {limits['calls_per_month']}/mes, {limits['calls_per_day']}/día, {limits['concurrent_calls']} concurrentes")
    
    # Test rate limit check
    result = router.check_rate_limit("despertar", {"monthly": 99, "daily": 4})
    print(f"\n  Rate limit check (99/100 monthly): allowed={result['allowed']}")
    
    result = router.check_rate_limit("despertar", {"monthly": 100, "daily": 5})
    print(f"  Rate limit check (100/100 monthly): allowed={result['allowed']}")
    
    print("=" * 70)
    accuracy = (passed / len(cases)) * 100
    print(f"Resultado: {passed}/{len(cases)} passed ({accuracy:.1f}%)")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = test_router()
    sys.exit(0 if success else 1)
