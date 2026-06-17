"""Tests for the Graph Builder (entity extraction + relationship linking)."""

import pytest
from src.core.graph_builder import (
    extract_entities_local, extract_relations_local,
    query_related, ENTITY_PATTERNS, RELATION_PATTERNS
)


class TestExtractEntitiesLocal:
    def test_extract_technology(self):
        text = "Estoy usando Python y Docker para el proyecto"
        entities = extract_entities_local(text)
        names = [e["name"].lower() for e in entities]
        assert "python" in names
        assert "docker" in names

    def test_extract_concept(self):
        text = "La arquitectura de microservicios con API REST"
        entities = extract_entities_local(text)
        names = [e["name"].lower() for e in entities]
        assert any("arquitectura" in n for n in names)

    def test_extract_person(self):
        text = "Hola @luis, como estas?"
        entities = extract_entities_local(text)
        names = [e["name"].lower() for e in entities]
        assert "@luis" in names

    def test_empty_text(self):
        entities = extract_entities_local("")
        assert entities == []

    def test_no_entities(self):
        entities = extract_entities_local("Hola, como estas?")
        assert entities == []

    def test_multiple_technologies(self):
        text = "React con TypeScript y Node.js"
        entities = extract_entities_local(text)
        names = [e["name"].lower() for e in entities]
        assert "react" in names
        assert "typescript" in names
        assert "node.js" in names or "node" in names

    def test_no_duplicates(self):
        text = "Python y Python otra vez"
        entities = extract_entities_local(text)
        count = sum(1 for e in entities if e["name"].lower() == "python")
        assert count == 1


class TestExtractRelationsLocal:
    def test_uses_relation(self):
        text = "La app usa Python para el backend"
        entities = [
            {"name": "app", "type": "project"},
            {"name": "Python", "type": "technology"},
        ]
        relations = extract_relations_local(text, entities)
        assert any(r["type"] == "USES" for r in relations)

    def test_depends_on_relation(self):
        text = "El modulo depende de Redis"
        entities = [
            {"name": "modulo", "type": "concept"},
            {"name": "Redis", "type": "technology"},
        ]
        relations = extract_relations_local(text, entities)
        assert any(r["type"] == "DEPENDS_ON" for r in relations)

    def test_communicates_with_relation(self):
        text = "El frontend se comunica con el backend via REST"
        entities = [
            {"name": "frontend", "type": "concept"},
            {"name": "backend", "type": "concept"},
        ]
        relations = extract_relations_local(text, entities)
        assert any(r["type"] == "COMMUNICATES_WITH" for r in relations)

    def test_no_entities_no_relations(self):
        relations = extract_relations_local("Hola mundo", [])
        assert relations == []


class TestQueryRelated:
    def test_no_neo4j(self):
        class MockStore:
            def get_driver(self):
                return None
        result = query_related("python", MockStore())
        assert result == []

    def test_empty_results(self):
        class MockDriver:
            def session(self):
                class MockSess:
                    def run(self, q, **p):
                        class MockRes:
                            def __iter__(self):
                                return iter([])
                        return MockRes()
                    def __enter__(self):
                        return self
                    def __exit__(self, *a):
                        pass
                return MockSess()
            def close(self):
                pass
        class MockStore:
            def get_driver(self):
                return MockDriver()
        result = query_related("python", MockStore())
        assert result == []
