"""FastEmbed Connector - Embeddings locales sin dependencia de Ollama."""

from dataclasses import dataclass
from typing import Optional
from fastembed import TextEmbedding


@dataclass
class FastEmbedConfig:
    """Configuración de FastEmbed."""
    model_name: str = "BAAI/bge-small-en-v1.5"  # ~130MB, multilingüe
    cache_dir: Optional[str] = None


class FastEmbedConnector:
    """
    FastEmbed Connector - Generación de embeddings locales.

    Usa modelos ONNX optimizados, no requiere GPU ni Ollama.
    Modelo por defecto: BAAI/bge-small-en-v1.5 (~130MB)
    """

    def __init__(self, config: Optional[FastEmbedConfig] = None):
        self.config = config or FastEmbedConfig()
        self._model: Optional[TextEmbedding] = None

    def _get_model(self) -> TextEmbedding:
        """Lazy load del modelo de embeddings."""
        if self._model is None:
            self._model = TextEmbedding(
                model_name=self.config.model_name,
                cache_dir=self.config.cache_dir,
            )
        return self._model

    def embed(self, text: str) -> list[float]:
        """
        Genera embedding para un texto.

        Args:
            text: Texto a procesar

        Returns:
            Lista de floats con el embedding
        """
        model = self._get_model()
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist() if hasattr(embeddings[0], "tolist") else list(embeddings[0])

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Genera embeddings para múltiples textos.

        Args:
            texts: Lista de textos

        Returns:
            Lista de embeddings
        """
        model = self._get_model()
        embeddings = list(model.embed(texts))
        return [
            e.tolist() if hasattr(e, "tolist") else list(e)
            for e in embeddings
        ]

    def health_check(self) -> dict:
        """Verifica que el modelo está cargado."""
        try:
            model = self._get_model()
            # Test embedding
            test_embedding = self.embed("test")
            return {
                "status": "healthy",
                "model": self.config.model_name,
                "embedding_dim": len(test_embedding),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_stats(self) -> dict:
        """Estadísticas del conector."""
        return {
            "model": self.config.model_name,
            "loaded": self._model is not None,
        }
