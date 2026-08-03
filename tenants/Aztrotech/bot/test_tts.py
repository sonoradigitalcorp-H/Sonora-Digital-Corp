#!/usr/bin/env python3
"""Test del pipeline TTS — genera audio y verifica calidad."""
import asyncio
import os
import sys
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

import httpx

TTS_URL = "http://localhost:8765"

async def test_tts():
    print("=" * 70)
    print("TTS PIPELINE TEST")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # Test 1: Health check
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TTS_URL}/health")
        ok = resp.status_code == 200 and resp.json().get("status") == "ok"
        status = "PASS" if ok else "FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status} Health check: {resp.json()}")
    
    # Test 2: Generate TTS audio (using /tts endpoint)
    test_texts = [
        "Hola, bienvenido a Aztrotech",
        "¿Cómo estás? ¡Muy bien! El precio es $1,500 MXN",
        "Hola bienvenido a Aztrotech",
    ]
    
    for text in test_texts:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{TTS_URL}/tts", json={
                "text": text,
                "voice": "cesar"
            })
            
            if resp.status_code == 200:
                data = resp.json()
                size = data.get("size", 0)
                output = data.get("output", "")
                ok = size > 10000  # At least 10KB
                status = "PASS" if ok else "FAIL"
                if ok: passed += 1
                else: failed += 1
                print(f"  {status} TTS '{text[:40]}...' -> {size} bytes ({output})")
            else:
                failed += 1
                print(f"  FAIL TTS '{text[:40]}...' -> HTTP {resp.status_code}")
    
    # Test 3: Check available voices
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TTS_URL}/voices")
        if resp.status_code == 200:
            data = resp.json()
            voices = data.get("voices", [])
            ok = len(voices) > 0
            status = "PASS" if ok else "FAIL"
            if ok: passed += 1
            else: failed += 1
            print(f"  {status} Available voices: {voices}")
        else:
            print(f"  SKIP Voices endpoint: HTTP {resp.status_code}")
    
    print("=" * 70)
    total = passed + failed
    accuracy = (passed / total) * 100 if total > 0 else 0
    print(f"Resultado: {passed}/{total} passed ({accuracy:.1f}%)")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(test_tts())
    sys.exit(0 if success else 1)
