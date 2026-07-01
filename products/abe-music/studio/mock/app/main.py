import json, time, uuid, threading
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MOCK_DELAY_MS = int(__import__('os').environ.get('MOCK_DELAY_MS', '3000'))
tasks = {}

def delayed_complete(task_id):
    time.sleep(MOCK_DELAY_MS / 1000)
    tasks[task_id] = {
        "id": task_id,
        "status": "completed",
        "created_at": int(time.time()),
        "model": "seedance-2-0",
        "billing_status": "charged",
        "credits": 60,
        "failed_reason": None,
        "data": {
            "results": [f"https://cdn.mock.seedance/{task_id}.mp4"],
            "video_expires_at": "2026-07-15T00:00:00Z",
            "last_frame_url": None,
            "processing_time": MOCK_DELAY_MS // 1000
        }
    }

@app.route('/v1/videos/generations', methods=['POST'])
def create_generation():
    task_id = f"mock_{uuid.uuid4().hex[:12]}"
    tasks[task_id] = {
        "id": task_id, "status": "queued",
        "created_at": int(time.time()),
        "model": "seedance-2-0", "billing_status": "reserved",
        "credits": 60, "failed_reason": None, "data": None
    }
    threading.Thread(target=delayed_complete, args=(task_id,), daemon=True).start()
    return jsonify({"taskId": task_id, "credits": 60}), 200

@app.route('/v1/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    t = tasks.get(task_id)
    if not t:
        return jsonify({"error": {"code": "not_found", "message": "Task not found"}}), 404
    return jsonify(t), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mock": True, "tasks": len(tasks)})

if __name__ == '__main__':
    port = int(__import__('os').environ.get('MOCK_PORT', '3099'))
    print(f"Seedance Mock running on :{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
