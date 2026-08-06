"""Vector Store - Almacenamiento vectorial para búsqueda semántica."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class VectorEntry:
    """Entrada vectorial."""
    id: str
    content: str
    embedding: list[float]
    metadata: dict = field(default_factory=dict)
    collection: str = "default"


class VectorStore:
    """
    Vector Store - Almacenamiento vectorial.

    En producción, esto se conectaría a Qdrant.
    Por ahora, es una implementación en memoria para desarrollo.
    """

    def __init__(self, embedding_connector=None):
        self.entries: dict[str, VectorEntry] = {}
        self.collections: dict[str, list[str]] = {}  # collection -> [entry_ids]
        self._embedding = embedding_connector

    def add(
        self,
        content: str,
        embedding: list[float],
        collection: str = "default",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Agrega un vector al almacén.

        Args:
            content: Texto original
            embedding: Vector de embeddings
            collection: Colección a la que pertenece
            metadata: Metadatos adicionales

        Returns:
            ID de la entrada creada
        """
        entry_id = str(uuid4())

        entry = VectorEntry(
            id=entry_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            collection=collection,
        )

        self.entries[entry_id] = entry

        # Agregar a colección
        if collection not in self.collections:
            self.collections[collection] = []
        self.collections[collection].append(entry_id)

        return entry_id

    def add_text(
        self,
        content: str,
        collection: str = "default",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Agrega texto generando embedding automáticamente.

        Requiere que el VectorStore haya sido inicializado
        con un embedding_connector (FastEmbedConnector).

        Args:
            content: Texto a almacenar
            collection: Colección a la que pertenece
            metadata: Metadatos adicionales

        Returns:
            ID de la entrada creada
        """
        if self._embedding is None:
            raise RuntimeError(
                "VectorStore no tiene embedding_connector. "
                "Inicializa con VectorStore(embedding_connector=fastembed)"
            )
        embedding = self._embedding.embed(content)
        return self.add(content, embedding, collection, metadata)

    def search(
        self,
        query_embedding: list[float],
        collection: str = "default",
        limit: int = 5,
        min_score: float = 0.5,
    ) -> list[dict]:
        """
        Busca vectors similares.

        Args:
            query_embedding: Vector de consulta
            collection: Colección a buscar
            limit: Número máximo de resultados
            min_score: Score mínimo de similitud

        Returns:
            Lista de resultados con score
        """
        collection_ids = self.collections.get(collection, [])
        results = []

        for entry_id in collection_ids:
            entry = self.entries.get(entry_id)
            if entry:
                # Calcular similitud coseno (simplificada)
                score = self._cosine_similarity(query_embedding, entry.embedding)
                if score >= min_score:
                    results.append({
                        "id": entry_id,
                        "content": entry.content,
                        "score": score,
                        "metadata": entry.metadata,
                    })

        # Ordenar por score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def search_text(
        self,
        query: str,
        collection: str = "default",
        limit: int = 5,
        min_score: float = 0.5,
    ) -> list[dict]:
        """
        Busca por texto, generando embedding automáticamente.

        Requiere que el VectorStore haya sido inicializado
        con un embedding_connector.

        Args:
            query: Texto de consulta
            collection: Colección a buscar
            limit: Número máximo de resultados
            min_score: Score mínimo de similitud

        Returns:
            Lista de resultados con score
        """
        if self._embedding is None:
            raise RuntimeError(
                "VectorStore no tiene embedding_connector. "
                "Inicializa con VectorStore(embedding_connector=fastembed)"
            )
        query_embedding = self._embedding.embed(query)
        return self.search(query_embedding, collection, limit, min_score)

    def get(self, entry_id: str) -> Optional[VectorEntry]:
        """Obtiene una entrada por ID."""
        return self.entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        """Elimina una entrada."""
        if entry_id in self.entries:
            entry = self.entries[entry_id]
            del self.entries[entry_id]

            # Eliminar de colección
            if entry.collection in self.collections:
                self.collections[entry.collection] = [
                    eid for eid in self.collections[entry.collection]
                    if eid != entry_id
                ]

            return True
        return False

    def get_collection(self, collection: str) -> list[VectorEntry]:
        """Obtiene todas las entradas de una colección."""
        entry_ids = self.collections.get(collection, [])
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calcula similitud coseno entre dos vectores."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get_stats(self) -> dict:
        """Obtiene estadísticas del vector store."""
        return {
            "total_entries": len(self.entries),
            "collections": {c: len(ids) for c, ids in self.collections.items()},
            "embedding_model": self._embedding.config.model_name if self._embedding else None,
            "embedding_loaded": self._embedding is not None,
        }
