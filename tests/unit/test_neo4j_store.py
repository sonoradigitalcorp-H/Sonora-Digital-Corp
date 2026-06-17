"""
Tests para src/core/neo4j_store.py — con mocks (no requiere Neo4j corriendo).
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.core.neo4j_store import (
    create_session,
    get_session,
    list_sessions,
    search_sessions,
    toggle_pin,
    delete_session,
    add_message,
)


class TestNeo4jStore:

    def test_get_session_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = get_session("any")
            assert result is None

    def test_list_sessions_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = list_sessions()
            assert result == []

    def test_search_sessions_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = search_sessions("test")
            assert result == []

    def test_create_session_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = create_session("test-title")
            assert result is None

    def test_toggle_pin_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = toggle_pin("any")
            assert result is None

    def test_delete_session_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = delete_session("any")
            assert result is False

    def test_add_message_no_driver(self):
        with patch("src.core.neo4j_store.get_driver", return_value=None):
            result = add_message("any", "user", "hello")
            assert result is None
