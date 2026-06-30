"""
JARVIS Document Chunker — Semantic chunking pipeline for long documents.
Splits documents > 512 tokens into overlapping chunks for embedding storage.
"""

import logging
import re
from typing import Any

log = logging.getLogger("jarvis.chunker")

MAX_TOKENS = 512
CHUNK_OVERLAP = 64


def estimate_tokens(text: str) -> int:
    return len(text.split())


def chunk_document(
    text: str, max_tokens: int = MAX_TOKENS, overlap: int = CHUNK_OVERLAP
) -> list[dict[str, Any]]:
    if estimate_tokens(text) <= max_tokens:
        return [{"text": text, "index": 0, "total": 1}]
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current_chunk = []
    current_tokens = 0
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        if para_tokens > max_tokens:
            if current_chunk:
                chunks.append(_finalize_chunk(current_chunk))
                current_chunk = []
                current_tokens = 0
            sentences = re.split(r"(?<=[.!?])\s+", para)
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                if sent_tokens > max_tokens:
                    words = sentence.split()
                    for i in range(0, len(words), max_tokens - overlap):
                        word_chunk = words[i : i + max_tokens]
                        chunk_text = " ".join(word_chunk)
                        chunks.append({"text": chunk_text, "tokens": len(word_chunk)})
                    continue
                if current_tokens + sent_tokens > max_tokens and current_chunk:
                    chunks.append(_finalize_chunk(current_chunk, overlap))
                    current_chunk = _get_overlap_tail(chunks[-1]["text"], overlap)
                    current_tokens = estimate_tokens(" ".join(current_chunk))
                current_chunk.append(sentence)
                current_tokens += sent_tokens
        elif current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append(_finalize_chunk(current_chunk, overlap))
            current_chunk = _get_overlap_tail(chunks[-1]["text"], overlap)
            current_tokens = estimate_tokens(" ".join(current_chunk))
            current_chunk.append(para)
            current_tokens += para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    if current_chunk:
        chunks.append(_finalize_chunk(current_chunk))
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        chunk["index"] = i
        chunk["total"] = total
    return chunks


def _finalize_chunk(parts: list[str], overlap: int = 0) -> dict[str, Any]:
    text = "\n\n".join(parts)
    return {"text": text, "tokens": estimate_tokens(text)}


def _get_overlap_tail(text: str, overlap_tokens: int) -> list[str]:
    words = text.split()
    if len(words) <= overlap_tokens:
        return [" ".join(words)]
    tail = " ".join(words[-overlap_tokens:])
    return [tail]


def chunk_and_store(
    document: str, source: str, rag_engine, metadata: dict = None
) -> list[dict[str, Any]]:
    chunks = chunk_document(document)
    results = []
    for chunk in chunks:
        payload = {
            "text": chunk["text"],
            "source": source,
            "chunk_index": chunk["index"],
            "chunk_total": chunk["total"],
            "tokens": chunk["tokens"],
            **(metadata or {}),
        }
        result = rag_engine.store(text=chunk["text"], source=source, metadata=payload)
        results.append(
            {"chunk_index": chunk["index"], "status": "stored" if result else "failed"}
        )
    log.info(f"Stored {len(results)} chunks from {source}")
    return results
