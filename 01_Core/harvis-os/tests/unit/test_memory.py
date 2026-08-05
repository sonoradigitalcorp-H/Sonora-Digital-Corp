"""Unit tests for Memory System."""

import pytest
from src.memory.context import ContextManager
from src.memory.vector_store import VectorStore
from src.memory.graph_store import GraphStore


class TestContextManager:
    """Tests del Context Manager."""

    def setup_method(self):
        self.manager = ContextManager()

    def test_set_and_get(self):
        """Test guardar y obtener contexto."""
        entry_id = self.manager.set(
            key="user_preference",
            value="dark_mode",
            source="dispatcher",
        )
        assert entry_id is not None

        value = self.manager.get("user_preference")
        assert value == "dark_mode"

    def test_get_user_context(self):
        """Test obtener contexto de usuario."""
        self.manager.set("key1", "value1", "test", user_id="user1")
        self.manager.set("key2", "value2", "test", user_id="user1")
        self.manager.set("key3", "value3", "test", user_id="user2")

        context = self.manager.get_user_context("user1")
        assert len(context) == 2

    def test_search(self):
        """Test buscar contexto."""
        self.manager.set("theme", "dark", "test")
        self.manager.set("language", "es", "test")

        results = self.manager.search("dark")
        assert len(results) == 1
        assert results[0].value == "dark"

    def test_delete(self):
        """Test eliminar contexto."""
        entry_id = self.manager.set("key", "value", "test")
        result = self.manager.delete(entry_id)
        assert result is True
        assert self.manager.get("key") is None

    def test_clear_user_context(self):
        """Test limpiar contexto de usuario."""
        self.manager.set("key1", "value1", "test", user_id="user1")
        self.manager.set("key2", "value2", "test", user_id="user1")

        count = self.manager.clear_user_context("user1")
        assert count == 2
        assert len(self.manager.get_user_context("user1")) == 0

    def test_get_stats(self):
        """Test obtener estadísticas."""
        self.manager.set("key1", "value1", "test")
        stats = self.manager.get_stats()
        assert stats["total_entries"] == 1


class TestVectorStore:
    """Tests del Vector Store."""

    def setup_method(self):
        self.store = VectorStore()

    def test_add_and_search(self):
        """Test agregar y buscar vectores."""
        entry_id = self.store.add(
            content="这是一个测试",
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            collection="test",
        )
        assert entry_id is not None

        results = self.store.search(
            query_embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            collection="test",
        )
        assert len(results) == 1
        assert results[0]["score"] > 0.9

    def test_search_similar(self):
        """Test buscar vectores similares."""
        self.store.add("test1", [0.1, 0.2, 0.3], "test")
        self.store.add("test2", [0.1, 0.2, 0.4], "test")
        self.store.add("test3", [0.9, 0.8, 0.7], "test")

        results = self.store.search(
            query_embedding=[0.1, 0.2, 0.3],
            collection="test",
            limit=2,
        )
        assert len(results) == 2
        # Los primeros resultados deberían ser los más similares
        assert results[0]["score"] > results[1]["score"]

    def test_delete(self):
        """Test eliminar vector."""
        entry_id = self.store.add("test", [0.1, 0.2], "test")
        result = self.store.delete(entry_id)
        assert result is True

    def test_get_collection(self):
        """Test obtener colección."""
        self.store.add("test1", [0.1, 0.2], "collection1")
        self.store.add("test2", [0.3, 0.4], "collection1")
        self.store.add("test3", [0.5, 0.6], "collection2")

        entries = self.store.get_collection("collection1")
        assert len(entries) == 2

    def test_get_stats(self):
        """Test obtener estadísticas."""
        self.store.add("test", [0.1, 0.2], "test")
        stats = self.store.get_stats()
        assert stats["total_entries"] == 1
        assert "test" in stats["collections"]


class TestGraphStore:
    """Tests del Graph Store."""

    def setup_method(self):
        self.graph = GraphStore()

    def test_add_node(self):
        """Test agregar nodo."""
        node_id = self.graph.add_node("User", {"name": "Luis"})
        assert node_id is not None

    def test_add_edge(self):
        """Test agregar arista."""
        node1 = self.graph.add_node("User", {"name": "Luis"})
        node2 = self.graph.add_node("Task", {"title": "Test"})

        edge_id = self.graph.add_edge(node1, node2, "WORKS_ON")
        assert edge_id is not None

    def test_get_neighbors(self):
        """Test obtener vecinos."""
        node1 = self.graph.add_node("User", {"name": "Luis"})
        node2 = self.graph.add_node("Task", {"title": "Test"})
        self.graph.add_edge(node1, node2, "WORKS_ON")

        neighbors = self.graph.get_neighbors(node1)
        assert len(neighbors) == 1
        assert neighbors[0].label == "Task"

    def test_search_nodes(self):
        """Test buscar nodos."""
        self.graph.add_node("User", {"name": "Luis"})
        self.graph.add_node("User", {"name": "Pedro"})
        self.graph.add_node("Task", {"title": "Test"})

        users = self.graph.search(label="User")
        assert len(users) == 2

    def test_get_path(self):
        """Test obtener camino."""
        node1 = self.graph.add_node("A", {})
        node2 = self.graph.add_node("B", {})
        node3 = self.graph.add_node("C", {})

        self.graph.add_edge(node1, node2, "connects")
        self.graph.add_edge(node2, node3, "connects")

        path = self.graph.get_path(node1, node3)
        assert path is not None
        assert len(path) == 3

    def test_delete_node(self):
        """Test eliminar nodo."""
        node_id = self.graph.add_node("Test", {})
        result = self.graph.delete_node(node_id)
        assert result is True
        assert self.graph.get_node(node_id) is None

    def test_get_stats(self):
        """Test obtener estadísticas."""
        self.graph.add_node("A", {})
        self.graph.add_node("B", {})
        node1 = self.graph.add_node("C", {})
        node2 = self.graph.add_node("D", {})
        self.graph.add_edge(node1, node2, "connects")

        stats = self.graph.get_stats()
        assert stats["total_nodes"] == 4
        assert stats["total_edges"] == 1
