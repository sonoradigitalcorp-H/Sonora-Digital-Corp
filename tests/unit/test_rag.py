"""Tests para src/core/rag.py — Qdrant mockeado."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock


import pytest
from src.core.rag import RagEngine, rag


class TestRagEngine:
    @patch("src.core.rag.QdrantClient")
    def test_client_unavailable(self, mock_qdrant):
        mock_qdrant.side_effect = Exception("no connection")
        engine = RagEngine()
        assert engine.client is None

    @patch("src.core.rag.QdrantClient")
    def test_store_no_client(self, mock_qdrant):
        mock_qdrant.side_effect = Exception("no connection")
        engine = RagEngine()
        result = engine.store("test text")
        assert result["status"] == "error"

    @patch("src.core.rag.QdrantClient")
    def test_search_no_client(self, mock_qdrant):
        mock_qdrant.side_effect = Exception("no connection")
        engine = RagEngine()
        result = engine.search("test query")
        assert result["status"] == "error"
        assert result["results"] == []

    @patch("src.core.rag.QdrantClient")
    def test_get_context_empty_when_no_client(self, mock_qdrant):
        mock_qdrant.side_effect = Exception("no connection")
        engine = RagEngine()
        result = engine.get_context("test")
        assert result == ""

    @patch("src.core.rag.QdrantClient")
    def test_ensure_collection_creates_if_missing(self, mock_qdrant):
        mock_instance = MagicMock()
        mock_qdrant.return_value = mock_instance
        from qdrant_client.http.exceptions import UnexpectedResponse
        mock_instance.get_collection.side_effect = UnexpectedResponse(
            status_code=404, content=None, headers=None, reason_phrase="Not Found"
        )
        mock_instance.create_collection.return_value = None

        engine = RagEngine()
        result = engine.ensure_collection()
        assert result is True
        mock_instance.create_collection.assert_called_once()

    @patch("src.core.rag.QdrantClient")
    def test_store_success(self, mock_qdrant):
        mock_instance = MagicMock()
        mock_qdrant.return_value = mock_instance
        mock_instance.get_collection.return_value = MagicMock()
        mock_instance.upsert.return_value = None

        engine = RagEngine()
        with patch("src.core.rag.embed_text") as mock_embed:
            mock_embed.return_value = [0.1] * 768
            result = engine.store("test content", {"source": "test"})

        assert result["status"] == "success"
        mock_instance.upsert.assert_called_once()

    @patch("src.core.rag.QdrantClient")
    def test_search_with_results(self, mock_qdrant):
        mock_instance = MagicMock()
        mock_qdrant.return_value = mock_instance

        mock_hit = MagicMock()
        mock_hit.id = 123
        mock_hit.score = 0.85
        mock_hit.payload = {"text": "result text", "metadata": {}, "timestamp": "2026-01-01"}
        mock_instance.search.return_value = [mock_hit]

        engine = RagEngine()
        with patch("src.core.rag.embed_text") as mock_embed:
            mock_embed.return_value = [0.1] * 768
            result = engine.search("test query", limit=1)

        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["results"][0]["score"] == 0.85
        assert result["results"][0]["text"] == "result text"

    @patch("src.core.rag.QdrantClient")
    def test_get_context_returns_string(self, mock_qdrant):
        mock_instance = MagicMock()
        mock_qdrant.return_value = mock_instance

        mock_hit = MagicMock()
        mock_hit.id = 1
        mock_hit.score = 0.9
        mock_hit.payload = {"text": "some context", "metadata": {}, "timestamp": "2026-01-01"}
        mock_instance.search.return_value = [mock_hit]

        engine = RagEngine()
        with patch("src.core.rag.embed_text") as mock_embed:
            mock_embed.return_value = [0.1] * 768
            context = engine.get_context("test query")

        assert "[0.90]" in context
        assert "some context" in context


class TestRagSingleton:
    def test_rag_is_instance(self):
        from src.core.rag import RagEngine
        assert isinstance(rag, RagEngine)
