import logging
from pathlib import Path
from typing import Any

from products.mystik.config import config

logger = logging.getLogger(__name__)

# Fallback knowledge base (productos SDC)
FALLBACK_KB = {
    "content-studio": "Content Studio: genera imágenes, TTS, talking heads, OCR, edición. MCP server en :8765.",
    "omnivoice": "OmniVoice: clonación de voz AI. API en :3900. Clona cualquier voz con 10s de audio.",
    "open-notebook": "Open Notebook: RAG sobre documentos. Alternativa a NotebookLM. UI en :8502.",
    "abe-music": "ABE Music OS: gestión de artistas musicales. Revenue, contratos, CRM.",
    "mystik": "Mystik AI: asistente de ventas inteligente con voz y texto. Mobile-first.",
}


class MystikRAG:
    def __init__(self):
        self.chroma = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self.chroma = chromadb.HttpClient(host=config.chroma_host, port=config.chroma_port)
            self.collection = self.chroma.get_or_create_collection("mystik_products")
            logger.info("ChromaDB connected")
        except Exception as e:
            logger.warning("ChromaDB not available (%s), using fallback KB", e)
            self.chroma = None

    def _load_docs_to_chroma(self):
        if not self.chroma or not self.collection:
            return
        docs_dir = Path("products")
        docs = []
        ids = []
        for product_dir in docs_dir.iterdir():
            if not product_dir.is_dir():
                continue
            readme = product_dir / "README.md"
            api_doc = product_dir / "API.md"
            content = ""
            if readme.exists():
                content += readme.read_text()[:1000]
            if api_doc.exists():
                content += "\n" + api_doc.read_text()[:1000]
            if content:
                docs.append(content)
                ids.append(product_dir.name)
        if docs and self.collection:
            try:
                self.collection.add(documents=docs, ids=ids)
                logger.info("Loaded %d product docs to ChromaDB", len(docs))
            except Exception as e:
                logger.warning("Failed to load docs to ChromaDB: %s", e)

    def search(self, query: str, tenant: str = "sonora") -> str:
        if self.chroma and self.collection:
            try:
                results = self.collection.query(query_texts=[query], n_results=3)
                if results.get("documents"):
                    return "\n".join(results["documents"][0])
            except Exception as e:
                logger.warning("Chroma query failed: %s", e)
        for key, text in FALLBACK_KB.items():
            if any(w in query.lower() for w in key.split("-")):
                return text
        return "Sonora Digital Corp ofrece soluciones AI para empresas: Content Studio, OmniVoice, Open Notebook, ABE Music OS, y Mystik AI."
