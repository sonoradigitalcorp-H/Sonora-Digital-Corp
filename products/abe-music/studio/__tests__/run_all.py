#!/usr/bin/env python3
"""ABE Studio — Test Runner (start servers, run tests, cleanup)"""
import subprocess, time, requests, sys, os

STUDIO_DIR = "/home/mystic/sonora-digital-corp/products/abe-music/studio"
API_DIR = f"{STUDIO_DIR}/api"
os.environ["STUDIO_SEEDANCE_BASE_URL"] = "http://localhost:3099"
os.environ["STUDIO_WEBHOOK_BASE_URL"] = "http://localhost:3021"
os.environ["STUDIO_STORAGE_PATH"] = "/tmp/studio_videos"
os.environ["STUDIO_DB_PATH"] = "/tmp/studio_test_run.db"
os.environ["STUDIO_SCHEMA_PATH"] = f"{STUDIO_DIR}/schema.sql"
os.environ["STUDIO_MOCK_MODE"] = "true"

procs = []

try:
    # Start mock
    mock = subprocess.Popen(
        ["python3", "app/main.py"],
        cwd=f"{STUDIO_DIR}/mock",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    procs.append(mock)

    # Start API
    api = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3020"],
        cwd=API_DIR,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    procs.append(api)

    time.sleep(3)

    # Verify both are up
    assert requests.get("http://localhost:3099/health").status_code == 200
    assert requests.get("http://localhost:3020/health").status_code == 200
    print("✅ Servers up")

    # Run integration tests
    status = subprocess.call(
        ["python3", f"{STUDIO_DIR}/__tests__/test_integration.py"],
        env={**os.environ, "STUDIO_API_URL": "http://localhost:3020", "STUDIO_MOCK_URL": "http://localhost:3099"}
    )

    # Test tier system
    print("\n🧪 Tier Tests:")
    
    r = requests.get("http://localhost:3020/studio/tiers")
    assert r.status_code == 200
    tiers = r.json()
    assert "free" in tiers["tiers"]
    print(f"  ✅ Tiers disponibles: {', '.join(tiers['tiers'])}")

    r = requests.get("http://localhost:3020/studio/usage", headers={"X-Tier": "free", "X-User-Id": "1"})
    assert r.status_code == 200
    data = r.json()
    assert data["tier"] == "free"
    print(f"  ✅ Límite free: {data['remaining']} reels restantes")

    r = requests.post("http://localhost:3020/studio/generate", 
        json={"model": "seedance-2-0", "input": {"prompt": "test tier", "generation_type": "text-to-video"}},
        headers={"X-Tier": "free", "X-User-Id": "1"})
    assert r.status_code == 200
    print(f"  ✅ Generate con tier free: taskId={r.json()['taskId']}")

    print(f"\n{'='*40}")
    if status == 0:
        print("🎉 Todos los tests pasaron!")
    else:
        print(f"❌ Algunos tests fallaron (exit code: {status})")
        sys.exit(status)

finally:
    for p in procs:
        p.terminate()
    time.sleep(0.5)
    for p in procs:
        p.kill()
