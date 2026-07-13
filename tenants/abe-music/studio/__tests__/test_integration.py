#!/usr/bin/env python3
"""ABE Studio — Integration Test
Prueba el flujo completo: API → Mock → Worker → Webhook
Uso: python3 __tests__/test_integration.py
"""
import requests, time, json, sys, os

API = os.environ.get("STUDIO_API_URL", "http://localhost:3020")
MOCK = os.environ.get("STUDIO_MOCK_URL", "http://localhost:3099")

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅ {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        failed += 1

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)

print("\n🧪 ABE Studio — Integration Tests\n")

# ── 1. Health ──
test("Health: API responde", lambda:
    check(requests.get(f"{API}/health").status_code == 200, "API health failed"))

test("Health: Mock responde", lambda:
    check(requests.get(f"{MOCK}/health").status_code == 200, "Mock health failed"))

# ── 2. Generación ──
test("POST /studio/generate crea tarea", lambda:
    check(requests.post(f"{API}/studio/generate", json={
        "model": "seedance-2-0",
        "input": {
            "prompt": "test cat surfing",
            "generation_type": "text-to-video",
            "duration": 5,
            "aspect_ratio": "9:16",
            "resolution": "720p"
        }
    }).status_code == 200, "Create failed"))

# ── 3. Task status ──
r = requests.post(f"{API}/studio/generate", json={
    "model": "seedance-2-0",
    "input": {"prompt": "cinematic sunset", "generation_type": "text-to-video"}
})
task_id = r.json()["taskId"]

test("GET /studio/tasks/:id returns task", lambda:
    check(requests.get(f"{API}/studio/tasks/{task_id}").status_code == 200, "Get task failed"))

# ── 4. Poll ──
test("POST /studio/poll runs without error", lambda:
    check(requests.post(f"{API}/studio/poll").status_code == 200, "Poll failed"))

# ── 5. Webhook ──
test("POST /studio/webhook accepts callback", lambda:
    check(requests.post(f"{API}/studio/webhook", json={
        "id": task_id,
        "status": "completed",
        "data": {"results": ["https://cdn.test/video.mp4"], "processing_time": 3}
    }).status_code == 200, "Webhook failed"))

# ── 6. 404 ──
test("GET /studio/tasks/:id returns 404 for unknown", lambda:
    check(requests.get(f"{API}/studio/tasks/nonexistent").status_code == 404, "Expected 404"))

# ── Resumen ──
total = passed + failed
print(f"\n{'='*40}")
print(f"Resultados: {passed}/{total} pasaron")
if failed:
    print(f"Fallaron: {failed}")
    sys.exit(1)
else:
    print("🎉 Todos los tests pasaron!")
