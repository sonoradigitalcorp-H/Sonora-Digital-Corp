#!/usr/bin/env python3
"""
Qdrant Collections Initialization for JARVIS
Crear las colecciones necesarias para la memoria vectorial
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import sys

def initialize_collections():
    """Inicializar colecciones en Qdrant"""
    
    # Conectar a Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    print("Conectando a Qdrant...")
    
    # Obtener colecciones existentes
    collections = client.get_collections().collections
    existing_names = [c.name for c in collections]
    
    print(f"Colecciones existentes: {existing_names}")
    
    # Definir colecciones a crear
    collections_to_create = [
        {
            "name": "conversations",
            "description": "Embeddings de conversaciones",
            "vector_size": 768,  # nomic-embed-text (Ollama local)
            "distance": Distance.COSINE
        },
        {
            "name": "documents",
            "description": "Embeddings de documentos",
            "vector_size": 768,
            "distance": Distance.COSINE
        },
        {
            "name": "tasks",
            "description": "Embeddings de tareas",
            "vector_size": 768,
            "distance": Distance.COSINE
        },
        {
            "name": "jarvis_knowledge",
            "description": "Base de conocimiento general (RAG pipeline real)",
            "vector_size": 768,
            "distance": Distance.COSINE
        }
    ]
    
    # Crear colecciones
    for coll_config in collections_to_create:
        name = coll_config["name"]
        
        if name in existing_names:
            print(f"✓ Colección '{name}' ya existe")
            continue
        
        print(f"Creando colección '{name}'...")
        
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=coll_config["vector_size"],
                distance=coll_config["distance"]
            )
        )
        
        print(f"✓ Colección '{name}' creada")
    
    # Crear payload indexes para búsqueda rápida
    print("\nCreando índices...")
    
    # Índice para conversaciones
    client.create_payload_index(
        collection_name="conversations",
        field_name="timestamp",
        field_schema="datetime"
    )
    
    client.create_payload_index(
        collection_name="conversations",
        field_name="user",
        field_schema="keyword"
    )
    
    client.create_payload_index(
        collection_name="conversations",
        field_name="topic",
        field_schema="keyword"
    )
    
    # Índice para documentos
    client.create_payload_index(
        collection_name="documents",
        field_name="type",
        field_schema="keyword"
    )
    
    client.create_payload_index(
        collection_name="documents",
        field_name="created_at",
        field_schema="datetime"
    )
    
    print("✓ Índices creados")
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("RESUMEN DE COLECCIONES")
    print("="*50)
    
    collections = client.get_collections().collections
    for coll in collections:
        info = client.get_collection(coll.name)
        print(f"\n{coll.name}:")
        print(f"  - Vectores: {info.points_count}")
        print(f"  - Tamaño vector: {info.config.params.vectors.size}")
        print(f"  - Distancia: {info.config.params.vectors.distance}")
    
    print("\n" + "="*50)
    print("✓ Inicialización completada")
    print("="*50)

if __name__ == "__main__":
    try:
        initialize_collections()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
