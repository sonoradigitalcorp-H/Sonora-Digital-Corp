import json
import os
import httpx

ENGRAM_URL = os.getenv("ENGRAM_URL", "http://localhost:7437")


async def save_memory(tenant_id, key, data):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{ENGRAM_URL}/memory/{tenant_id}",
                json={"key": key, "data": data},
            )
            return resp.status_code == 200
    except Exception:
        _local_save(tenant_id, key, data)
        return False


async def get_memory(tenant_id, key=None):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            url = f"{ENGRAM_URL}/memory/{tenant_id}"
            if key:
                url += f"/{key}"
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return _local_load(tenant_id, key)


def _local_path(tenant_id):
    path = os.path.join(os.path.dirname(__file__), "..", "data", "memory")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{tenant_id}.json")


def _local_save(tenant_id, key, data):
    path = _local_path(tenant_id)
    store = {}
    if os.path.exists(path):
        with open(path) as f:
            store = json.load(f)
    store[key] = data
    with open(path, "w") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def _local_load(tenant_id, key=None):
    path = _local_path(tenant_id)
    if not os.path.exists(path):
        return {} if key else {}
    with open(path) as f:
        store = json.load(f)
    if key:
        return store.get(key, {})
    return store


async def get_context(tenant_id, limit=5):
    memories = await get_memory(tenant_id)
    summaries = memories.get("call_summaries", []) if memories else []
    recent = summaries[-limit:] if len(summaries) > limit else summaries
    return recent


async def save_call_summary(tenant_id, summary):
    memories = await get_memory(tenant_id)
    summaries = memories.get("call_summaries", []) if memories else []
    summaries.append(summary)
    if len(summaries) > 50:
        summaries = summaries[-50:]
    await save_memory(tenant_id, "call_summaries", summaries)
