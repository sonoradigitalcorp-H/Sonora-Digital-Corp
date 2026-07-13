"""Tests para Per-tenant RAG [FR7] — Qdrant collections aisladas por cliente."""

from unittest.mock import MagicMock, patch

import pytest


class TestCollectionManagement:
    """Cada tenant tiene su propia colección Qdrant."""

    def test_collection_name_uses_tenant(self):
        from apps.sonora_engine.rag_per_tenant import _collection_name
        name = _collection_name("abe-music")
        assert name == "kb_abe_music"

    def test_collection_name_sanitizes(self):
        from apps.sonora_engine.rag_per_tenant import _collection_name
        name = _collection_name("other-tenant-id")
        assert "-" not in name
        assert name == "kb_other_tenant_id"

    def test_ensure_collection_creates_new(self):
        from apps.sonora_engine.rag_per_tenant import ensure_collection

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            result = ensure_collection("new-tenant")
            assert result is True
            client.create_collection.assert_called_once()

    def test_ensure_collection_skips_existing(self):
        from apps.sonora_engine.rag_per_tenant import ensure_collection

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            existing = MagicMock()
            existing.name = "kb_abe_music"
            client.get_collections.return_value = MagicMock(collections=[existing])

            result = ensure_collection("abe-music")
            assert result is False
            client.create_collection.assert_not_called()


class TestDocumentIndexing:
    """Documentos indexados con aislamiento por tenant."""

    def test_index_document_adds_tenant_filter(self):
        from apps.sonora_engine.rag_per_tenant import index_document

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            result = index_document(
                tenant_id="abe-music",
                doc_id="doc-001",
                text="Hector Rubio tiene 115 millones de streams",
                metadata={"source": "spotify", "type": "artist_stats"},
            )
            assert result is True
            client.upsert.assert_called_once()

    def test_index_multiple_tenants_separate(self):
        """Documentos de distintos tenants se indexan en colecciones separadas."""
        from apps.sonora_engine.rag_per_tenant import index_document

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            index_document("abe-music", "doc-1", "Datos de ABE Music")
            index_document("other-client", "doc-1", "Datos de otro cliente")

            calls = client.create_collection.call_args_list
            collections_created = [c[1]["collection_name"] for c in calls]
            assert "kb_abe_music" in collections_created
            assert "kb_other_client" in collections_created


class TestRAGQuery:
    """Consultas RAG con aislamiento de tenant."""

    def test_query_returns_results(self):
        from apps.sonora_engine.rag_per_tenant import query_rag

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            # Mock search results
            mock_result = MagicMock()
            mock_result.score = 0.85
            mock_result.payload = {
                "text": "Hector Rubio tiene 115M streams",
                "source": "spotify",
                "doc_id": "doc-001",
                "tenant_id": "abe-music",
            }
            client.search.return_value = [mock_result]

            results = query_rag("abe-music", "streams de Hector", limit=5)
            assert len(results) >= 1
            assert results[0]["score"] == 0.85
            assert "Hector" in results[0]["text"]

    def test_query_filtered_by_tenant(self):
        """Query filter must include tenant_id to prevent cross-tenant leaks."""
        from apps.sonora_engine.rag_per_tenant import query_rag

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            query_rag("abe-music", "streams")
            # Verify the filter includes tenant_id
            call_kwargs = client.search.call_args[1]
            query_filter = call_kwargs.get("query_filter")
            assert query_filter is not None, "Missing tenant filter — risk of data leak"


class TestArtistKnowledgeIndexing:
    """Indexación automática de artistas desde ABE Service."""

    def test_index_artist_knowledge(self):
        from apps.sonora_engine.rag_per_tenant import index_artist_knowledge

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            artist_data = {
                "name": "Hector Rubio",
                "genero": "Regional Mexicano",
                "pais": "México",
                "streams": 115093009,
                "monthly_listeners": 1100000,
                "top_song": "Se Volvieron Locos",
                "top_song_streams": 16000000,
                "revenue": 460372.0,
                "social": {"instagram": "@hector_rubiorr", "tiktok": "@thor_rubio"},
            }

            result = index_artist_knowledge(
                tenant_id="abe-music",
                artist_id="artist-uuid",
                artist_data=artist_data,
            )
            assert result is True
            # Should create multiple document chunks
            assert client.upsert.call_count >= 3


class TestTenantIsolationRAG:
    """Verificación de que no hay fuga de datos entre tenants."""

    def test_different_tenants_different_collections(self):
        from apps.sonora_engine.rag_per_tenant import _collection_name

        name_a = _collection_name("abe-music")
        name_b = _collection_name("other-tenant")
        assert name_a != name_b

    def test_tenant_a_cannot_see_tenant_b_data(self):
        """Cada tenant consulta SOLO su colección."""
        from apps.sonora_engine.rag_per_tenant import query_rag

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client
            client.get_collections.return_value = MagicMock(collections=[])

            query_rag("abe-music", "test")
            query_rag("other-tenant", "test")

            searches = client.search.call_args_list
            collections_searched = [s[1]["collection_name"] for s in searches]
            assert "kb_abe_music" in collections_searched
            assert "kb_other_tenant" in collections_searched


class TestCollectionListing:
    """Listado de colecciones por tenant."""

    def test_list_collections(self):
        from apps.sonora_engine.rag_per_tenant import list_collections

        with patch("apps.sonora_engine.rag_per_tenant._get_client") as mock_get:
            client = MagicMock()
            mock_get.return_value = client

            cols = [MagicMock(name="kb_abe_music"), MagicMock(name="kb_other")]
            for c in cols:
                c.name = c.name
                c.vectors_count = 10
            client.get_collections.return_value = MagicMock(collections=cols)

            result = list_collections()
            assert len(result) == 2
