"""
Tests para Edge Client — lógica de configuración y archivos
(no requiere Windows — testea lógica pura)
"""

import json
import os
import tempfile
from pathlib import Path

from apps.openclaw_edge.edge_client import (
    _deep_merge,
    _safe_rename,
    _write_error_log,
    file_hash,
    load_config,
    setup_directories,
)


class TestConfig:
    def test_load_default_config(self):
        cfg = load_config("/nonexistent/config.yaml")
        assert cfg["vps"]["url"] == "https://vps.sonoradigitalcorp.com"
        assert cfg["device"]["id"] == "nathaly-laptop"

    def test_deep_merge(self):
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"b": 99}}
        _deep_merge(base, override)
        assert base["a"]["b"] == 99
        assert base["a"]["c"] == 2
        assert base["d"] == 3


class TestDirectories:
    def test_setup_creates_all_subdirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs = setup_directories(tmp)
            for sub in ["Inbox", "Procesados", "Pendientes", "Errores", "Exportaciones", "Logs"]:
                assert sub in dirs
                assert dirs[sub].exists()
                assert dirs[sub].is_dir()

    def test_idempotent_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs1 = setup_directories(tmp)
            dirs2 = setup_directories(tmp)
            assert dirs1.keys() == dirs2.keys()


class TestFileHash:
    def test_same_content_same_hash(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello")
            path = f.name
        try:
            h1 = file_hash(Path(path))
            h2 = file_hash(Path(path))
            assert h1 == h2
            assert len(h1) == 64
        finally:
            os.unlink(path)

    def test_different_content_different_hash(self):
        with tempfile.NamedTemporaryFile(delete=False) as f1:
            f1.write(b"hello")
            p1 = f1.name
        with tempfile.NamedTemporaryFile(delete=False) as f2:
            f2.write(b"world")
            p2 = f2.name
        try:
            assert file_hash(Path(p1)) != file_hash(Path(p2))
        finally:
            os.unlink(p1)
            os.unlink(p2)


class TestSafeRename:
    def test_rename_no_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.txt"
            dst = Path(tmp) / "dst.txt"
            src.write_text("content")
            _safe_rename(src, dst)
            assert not src.exists()
            assert dst.exists()
            assert dst.read_text() == "content"

    def test_rename_with_collision_adds_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.txt"
            existing = Path(tmp) / "dst.txt"
            src.write_text("new")
            existing.write_text("old")
            _safe_rename(src, existing)
            assert not src.exists()
            assert existing.exists()
            files = list(Path(tmp).glob("dst_*.txt"))
            assert len(files) >= 1


class TestErrorLog:
    def test_write_error_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors_dir = Path(tmp)
            _write_error_log(errors_dir, "test.xml", "RFC invalido")
            log_path = errors_dir / "error_log.jsonl"
            assert log_path.exists()
            lines = log_path.read_text().strip().split("\n")
            assert len(lines) == 1
            entry = json.loads(lines[0])
            assert entry["file"] == "test.xml"
            assert "RFC" in entry["error"]

    def test_multiple_errors_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors_dir = Path(tmp)
            _write_error_log(errors_dir, "a.xml", "error 1")
            _write_error_log(errors_dir, "b.xml", "error 2")
            log_path = errors_dir / "error_log.jsonl"
            lines = log_path.read_text().strip().split("\n")
            assert len(lines) == 2
