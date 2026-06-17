"""Tests for the document chunking pipeline."""

import pytest
from src.core.chunker import (
    estimate_tokens, chunk_document, chunk_and_store,
    MAX_TOKENS, CHUNK_OVERLAP
)


class TestEstimateTokens:
    def test_empty(self):
        assert estimate_tokens("") == 0

    def test_simple(self):
        assert estimate_tokens("hello world") == 2

    def test_spanish(self):
        assert estimate_tokens("Hola mundo, esto es una prueba") == 6


class TestChunkDocument:
    def test_short_text_no_chunking(self):
        text = "Texto corto."
        chunks = chunk_document(text, max_tokens=100)
        assert len(chunks) == 1
        assert chunks[0]["text"] == text

    def test_single_long_paragraph(self):
        text = "word " * 600
        chunks = chunk_document(text, max_tokens=512)
        assert len(chunks) >= 2

    def test_multiple_paragraphs(self):
        para1 = "word " * 300
        para2 = "test " * 300
        text = f"{para1}\n\n{para2}"
        chunks = chunk_document(text, max_tokens=512)
        assert len(chunks) >= 2

    def test_chunk_metadata(self):
        text = "word " * 600
        chunks = chunk_document(text, max_tokens=512)
        for i, chunk in enumerate(chunks):
            assert "text" in chunk
            assert "index" in chunk
            assert "total" in chunk
            assert chunk["index"] == i

    def test_exact_boundary(self):
        text = "word " * 512
        chunks = chunk_document(text, max_tokens=512)
        assert len(chunks) == 1

    def test_overlap_content(self):
        text = "word " * 600
        chunks = chunk_document(text, max_tokens=512, overlap=20)
        if len(chunks) > 1:
            first_end = chunks[0]["text"].split()[-20:]
            second_start = chunks[1]["text"].split()[:20]
            assert any(w in second_start for w in first_end)

    def test_sentences(self):
        sentences = "Esta es la primera oración. " * 30 + "Esta es otra oración. " * 30
        chunks = chunk_document(sentences, max_tokens=100)
        assert len(chunks) >= 2


class TestChunkAndStore:
    def test_with_mock_rag(self):
        stored = []

        class MockRag:
            def store(self, text, source, metadata=None):
                stored.append({"text": text, "source": source, "metadata": metadata})
                return True

        rag = MockRag()
        text = "word " * 600
        results = chunk_and_store(text, "test.txt", rag, {"author": "test"})
        assert len(results) >= 2
        assert len(stored) >= 2
        for s in stored:
            assert s["source"] == "test.txt"
            assert s["metadata"]["author"] == "test"
