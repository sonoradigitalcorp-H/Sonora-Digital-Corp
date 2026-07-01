#!/usr/bin/env python3
"""Test the ABE Studio mock server"""
import requests, time, json

BASE = "http://localhost:3099"

# 1. Health check
r = requests.get(f"{BASE}/health")
assert r.status_code == 200, f"Health failed: {r.status_code}"
print(f"✅ Health: {r.json()}")

# 2. Create generation task
r = requests.post(f"{BASE}/v1/videos/generations", json={
    "model": "seedance-2-0",
    "input": {"prompt": "a cat surfing", "generation_type": "text-to-video"}
})
assert r.status_code == 200, f"Create failed: {r.status_code}"
data = r.json()
task_id = data["taskId"]
print(f"✅ Created: taskId={task_id}, credits={data['credits']}")

# 3. Poll immediately (should be queued or generating)
r = requests.get(f"{BASE}/v1/tasks/{task_id}")
assert r.status_code == 200, f"Poll failed: {r.status_code}"
print(f"✅ Initial status: {r.json()['status']}")

# 4. Wait for completion
print("⏳ Waiting for mock delay...")
time.sleep(4)

# 5. Poll again (should be completed)
r = requests.get(f"{BASE}/v1/tasks/{task_id}")
assert r.status_code == 200
data = r.json()
assert data["status"] == "completed", f"Expected completed, got {data['status']}"
video_url = data["data"]["results"][0]
print(f"✅ Completed! Video URL: {video_url}")

print("\n🎉 All mock tests passed!")
