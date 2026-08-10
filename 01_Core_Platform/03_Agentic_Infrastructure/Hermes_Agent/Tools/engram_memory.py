# Wrapper para Memoria Vectorial (Qdrant) - Sonora Digital Corp
import subprocess
import sys
import os
import json
import urllib.request

# Auto-instalación de dependencias si no existen (DevOps trick)
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("Instalando dependencias faltantes...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qdrant-client"])
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

# Embeddings via Ollama (all-minilm, 384-dim) — sin sentence-transformers
# Ollama corre en VPS OVH (docker) — ver ~/.hermes/.env OLLAMA_ENDPOINT
OLLAMA_URL = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434") + "/api/embeddings"
OLLAMA_MODEL = "all-minilm"

def _embed(text):
    req = urllib.request.Request(OLLAMA_URL,
        data=json.dumps({"model": OLLAMA_MODEL, "prompt": text}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["embedding"]

def _get_qdrant():
    return QdrantClient(host="localhost", port=6333, timeout=5)

def get_collection_name(client_name):
    return f"tenant_{client_name.lower().replace(' ', '_')}"

def _collection_exists(collection_name):
    """Verifica si una colección existe usando get_collections (API estable)."""
    try:
        collections = _get_qdrant().get_collections()
        return any(c.name == collection_name for c in collections.collections)
    except Exception:
        return False

def save_memory(data, client_name):
    """Guarda un recuerdo en el espacio vectorial aislado del cliente."""
    collection = get_collection_name(client_name)
    
    # Crear colección si no existe (Aislamiento Multitenant)
    if not _collection_exists(collection):
        _get_qdrant().create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"[Engram Tool] Colección creada para el tenant: {client_name}")
    
    vector = _embed(data)
    point_id = abs(hash(data)) % (10**10) # ID simple basado en el texto
    
    _get_qdrant().upsert(
        collection_name=collection,
        points=[PointStruct(id=point_id, vector=vector, payload={"text": data})]
    )
    return f"Memoria guardada para {client_name} en Qdrant."

def query_memory(query, client_name):
    """Busca memories semánticamente relevantes para el cliente."""
    collection = get_collection_name(client_name)
    
    if not _collection_exists(collection):
        return f"No hay memoria previa para {client_name}."
    
    vector = _embed(query)
    results = _get_qdrant().search(
        collection_name=collection,
        query_vector=vector,
        limit=1
    )
    
    if results:
        return results[0].payload.get("text", "Sin resultados")
    return "Sin resultados en la memoria vectorial."

if __name__ == "__main__":
    # Test rápido
    print("--- Test de Memoria Multitenant ---")
    print(save_memory("Aztrotech quiere reservar el día 15 de agosto a las 4pm.", "Aztrotech"))
    print(query_memory("¿cuándo quiere reservar aztrotech?", "Aztrotech"))
    
    # Test de aislamiento (Nathaly no debe ver la memoria de Aztrotech)
    print(query_memory("reserva agosto", "Nathaly_Contabilidad"))