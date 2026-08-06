"""Graph Store - Almacenamiento de grafos para relaciones."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class Node:
    """Nodo en el grafo."""
    id: str
    label: str
    properties: dict = field(default_factory=dict)


@dataclass
class Edge:
    """Arista en el grafo."""
    id: str
    source: str
    target: str
    relationship: str
    properties: dict = field(default_factory=dict)


class GraphStore:
    """
    Graph Store - Almacenamiento de grafos.

    En producción, esto se conectaría a Neo4j.
    Por ahora, es una implementación en memoria para desarrollo.
    """

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.adjacency: dict[str, list[str]] = {}  # node_id -> [edge_ids]

    def add_node(
        self,
        label: str,
        properties: Optional[dict] = None,
    ) -> str:
        """
        Agrega un nodo al grafo.

        Args:
            label: Etiqueta del nodo
            properties: Propiedades del nodo

        Returns:
            ID del nodo creado
        """
        node_id = str(uuid4())

        node = Node(
            id=node_id,
            label=label,
            properties=properties or {},
        )

        self.nodes[node_id] = node
        return node_id

    def add_edge(
        self,
        source: str,
        target: str,
        relationship: str,
        properties: Optional[dict] = None,
    ) -> str:
        """
        Agrega una arista al grafo.

        Args:
            source: ID del nodo origen
            target: ID del nodo destino
            relationship: Tipo de relación
            properties: Propiedades de la relación

        Returns:
            ID de la arista creada
        """
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Source or target node not found")

        edge_id = str(uuid4())

        edge = Edge(
            id=edge_id,
            source=source,
            target=target,
            relationship=relationship,
            properties=properties or {},
        )

        self.edges[edge_id] = edge

        # Actualizar adyacencia
        if source not in self.adjacency:
            self.adjacency[source] = []
        self.adjacency[source].append(edge_id)

        return edge_id

    def get_node(self, node_id: str) -> Optional[Node]:
        """Obtiene un nodo por ID."""
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Obtiene una arista por ID."""
        return self.edges.get(edge_id)

    def get_neighbors(self, node_id: str, relationship: Optional[str] = None) -> list[Node]:
        """
        Obtiene los vecinos de un nodo.

        Args:
            node_id: ID del nodo
            relationship: Filtrar por tipo de relación

        Returns:
            Lista de nodos vecinos
        """
        neighbors = []
        edge_ids = self.adjacency.get(node_id, [])

        for edge_id in edge_ids:
            edge = self.edges.get(edge_id)
            if edge:
                if relationship is None or edge.relationship == relationship:
                    neighbor = self.nodes.get(edge.target)
                    if neighbor:
                        neighbors.append(neighbor)

        return neighbors

    def search(
        self,
        label: Optional[str] = None,
        properties: Optional[dict] = None,
        limit: int = 10,
    ) -> list[Node]:
        """
        Busca nodos por etiqueta o propiedades.

        Args:
            label: Filtrar por etiqueta
            properties: Filtrar por propiedades
            limit: Número máximo de resultados

        Returns:
            Lista de nodos que coinciden
        """
        results = []

        for node in self.nodes.values():
            if label and node.label != label:
                continue

            if properties:
                match = all(
                    node.properties.get(k) == v
                    for k, v in properties.items()
                )
                if not match:
                    continue

            results.append(node)

            if len(results) >= limit:
                break

        return results

    def delete_node(self, node_id: str) -> bool:
        """Elimina un nodo y sus aristas."""
        if node_id not in self.nodes:
            return False

        # Eliminar aristas asociadas
        edge_ids = self.adjacency.get(node_id, [])
        for edge_id in edge_ids:
            if edge_id in self.edges:
                del self.edges[edge_id]

        del self.nodes[node_id]
        if node_id in self.adjacency:
            del self.adjacency[node_id]

        return True

    def get_path(
        self,
        start: str,
        end: str,
        max_depth: int = 5,
    ) -> Optional[list[Node]]:
        """
        Encuentra un camino entre dos nodos.

        Args:
            start: ID del nodo inicio
            end: ID del nodo fin
            max_depth: Profundidad máxima

        Returns:
            Lista de nodos en el camino o None
        """
        if start not in self.nodes or end not in self.nodes:
            return None

        # BFS simplificado
        visited = set()
        queue = [[start]]

        while queue:
            path = queue.pop(0)
            node_id = path[-1]

            if node_id == end:
                return [self.nodes[nid] for nid in path]

            if len(path) > max_depth:
                continue

            if node_id in visited:
                continue

            visited.add(node_id)

            for neighbor in self.get_neighbors(node_id):
                if neighbor.id not in visited:
                    queue.append(path + [neighbor.id])

        return None

    def get_stats(self) -> dict:
        """Obtiene estadísticas del grafo."""
        relationships = {}
        for edge in self.edges.values():
            relationships[edge.relationship] = relationships.get(edge.relationship, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "relationships": relationships,
        }
