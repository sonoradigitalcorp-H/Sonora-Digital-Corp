"""Tests para src/core/embeddings.py — chunk_text es puro, embed_text mockeado."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


import pytest
from src.core.embeddings import embed_text, embed_batch, chunk_text, EMBED_DIM


class TestChunkText:
    def test_chunk_small_text(self):
        text = "hola mundo"
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_large_text(self):
        words = ["word"] * 100
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=20, overlap=5)
        assert len(chunks) > 1

    def test_chunk_no_overlap(self):
        words = ["w"] * 30
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=10, overlap=0)
        assert len(chunks) == 3

    def test_chunk_empty_string(self):
        chunks = chunk_text("")
        assert chunks == []

    def test_chunk_single_word(self):
        chunks = chunk_text("solounapalabra")
        assert len(chunks) == 1
        assert chunks[0] == "solounapalabra"

    def test_embed_dim_constant(self):
        assert EMBED_DIM == 768


class TestEmbedText:
    @patch("src.core.embeddings.requests.post")
    def test_embed_text_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mock_post.return_value = mock_resp

        result = embed_text("test query")
        assert result == [0.1, 0.2, 0.3]
        mock_post.assert_called_once()

    @patch("src.core.embeddings.requests.post")
    def test_embed_text_failure_returns_none(self, mock_post):
        mock_post.side_effect = Exception("connection refused")

        result = embed_text("test query")
        assert result is None

    @patch("src.core.embeddings.requests.post")
    def test_embed_text_no_embedding_key(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_post.return_value = mock_resp

        result = embed_text("test")
        assert result is None


class TestEmbedBatch:
    @patch("src.core.embeddings.embed_text")
    def test_embed_batch(self, mock_embed):
        mock_embed.side_effect = [[0.1], [0.2], None]
        results = embed_batch(["a", "b", "c"])
        assert results == [[0.1], [0.2], None]
        assert mock_embed.call_count == 3
