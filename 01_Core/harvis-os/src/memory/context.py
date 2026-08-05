"""Context Manager - Gestión de contexto entre sesiones."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class ContextEntry:
    """Entrada de contexto."""
    id: str
    key: str
    value: str
    source: str  # componente que creó el contexto
    metadata: dict = field(default_factory=dict)
    created_at: str = None
    expires_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


class ContextManager:
    """
    Context Manager - Gestión de contexto compartido.

    Almacena y recupera contexto entre sesiones y componentes.
    """

    def __init__(self):
        self.contexts: dict[str, ContextEntry] = {}
        self.user_contexts: dict[str, list[str]] = {}  # user_id -> [context_ids]

    def set(
        self,
        key: str,
        value: str,
        source: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        ttl: Optional[int] = None,  # segundos
    ) -> str:
        """
        Guarda un valor en el contexto.

        Args:
            key: Clave del contexto
            value: Valor a almacenar
            source: Componente que crea el contexto
            user_id: ID del usuario (opcional)
            metadata: Metadatos adicionales
            ttl: Time to live en segundos

        Returns:
            ID de la entrada creada
        """
        entry_id = str(uuid4())

        entry = ContextEntry(
            id=entry_id,
            key=key,
            value=value,
            source=source,
            metadata=metadata or {},
        )

        self.contexts[entry_id] = entry

        # Asociar a usuario si se especifica
        if user_id:
            if user_id not in self.user_contexts:
                self.user_contexts[user_id] = []
            self.user_contexts[user_id].append(entry_id)

        return entry_id

    def get(self, key: str, user_id: Optional[str] = None) -> Optional[str]:
        """
        Obtiene un valor del contexto.

        Args:
            key: Clave a buscar
            user_id: Filtrar por usuario

        Returns:
            Valor o None si no existe
        """
        for entry in self.contexts.values():
            if entry.key == key:
                if user_id and user_id not in self.user_contexts:
                    continue
                if user_id and entry.id not in self.user_contexts.get(user_id, []):
                    continue
                return entry.value
        return None

    def get_by_id(self, entry_id: str) -> Optional[ContextEntry]:
        """Obtiene una entrada por ID."""
        return self.contexts.get(entry_id)

    def get_user_context(self, user_id: str) -> list[ContextEntry]:
        """Obtiene todo el contexto de un usuario."""
        entry_ids = self.user_contexts.get(user_id, [])
        return [self.contexts[eid] for eid in entry_ids if eid in self.contexts]

    def search(self, query: str, limit: int = 10) -> list[ContextEntry]:
        """Busca contexto por texto."""
        results = []
        query_lower = query.lower()

        for entry in self.contexts.values():
            if query_lower in entry.key.lower() or query_lower in entry.value.lower():
                results.append(entry)

        return results[:limit]

    def delete(self, entry_id: str) -> bool:
        """Elimina una entrada de contexto."""
        if entry_id in self.contexts:
            entry = self.contexts[entry_id]
            del self.contexts[entry_id]

            # Eliminar de usuario
            for user_id, entry_ids in self.user_contexts.items():
                if entry_id in entry_ids:
                    entry_ids.remove(entry_id)

            return True
        return False

    def clear_user_context(self, user_id: str) -> int:
        """Limpia todo el contexto de un usuario."""
        entry_ids = self.user_contexts.get(user_id, [])
        count = 0

        for entry_id in entry_ids:
            if entry_id in self.contexts:
                del self.contexts[entry_id]
                count += 1

        self.user_contexts[user_id] = []
        return count

    def get_stats(self) -> dict:
        """Obtiene estadísticas del contexto."""
        return {
            "total_entries": len(self.contexts),
            "total_users": len(self.user_contexts),
            "entries_by_source": self._count_by_source(),
        }

    def _count_by_source(self) -> dict:
        counts = {}
        for entry in self.contexts.values():
            counts[entry.source] = counts.get(entry.source, 0) + 1
        return counts
