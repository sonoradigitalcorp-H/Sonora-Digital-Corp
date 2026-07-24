import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _model = None


def embed(texts: list[str]) -> list[list[float]]:
    if _model is None:
        raise RuntimeError("sentence-transformers not available")
    vecs = _model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return vecs.tolist() if isinstance(vecs, np.ndarray) else [v.tolist() for v in vecs]


def embed_query(text: str) -> list[float]:
    return embed([text])[0]


DIMENSION = 384
