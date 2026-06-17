"""
Tests para src/core/tools.py — funciones deterministas sin LLM.
"""

import os
import sys
import tempfile
from pathlib import Path


import pytest
from src.core.tools import (
    execute_command,
    read_file,
    write_file,
    list_files,
    search_code,
    search_semantic,
    rag_store,
    TOOL_DEFINITIONS,
    AVAILABLE_TOOLS,
)


class TestToolDefinitions:
    def test_all_tools_have_definitions(self):
        names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        for tool_name in AVAILABLE_TOOLS:
            assert tool_name in names, f"{tool_name} no tiene definición"

    def test_tool_count(self):
        assert len(AVAILABLE_TOOLS) >= 8

    def test_definitions_have_required(self):
        for t in TOOL_DEFINITIONS:
            f = t["function"]
            assert "name" in f
            assert "description" in f
            assert "parameters" in f


class TestExecuteCommand:
    def test_ls_works(self):
        result = execute_command("ls")
        assert result["status"] == "success"

    def test_disallowed_command(self):
        result = execute_command("rm -rf /")
        assert result["status"] == "error"

    def test_pwd_works(self):
        result = execute_command("pwd")
        assert result["status"] == "success"
        assert "/" in result["output"]


class TestReadFile:
    def test_read_existing(self):
        result = read_file("apps/jarvis/src/core/tools/router.py", max_lines=5)
        assert result["status"] == "success"
        assert result["total_lines"] > 0

    def test_read_nonexistent(self):
        result = read_file("no-existe-12345.py")
        assert result["status"] == "error"

    def test_read_respects_max_lines(self):
        result = read_file("apps/jarvis/src/core/tools/router.py", max_lines=3)
        assert result["status"] == "success"
        assert result["lines_shown"] <= 3


class TestWriteFile:
    def test_write_and_cleanup(self):
        path = "_test_write_temp.txt"
        try:
            result = write_file(path, "hello world")
            assert result["status"] == "success"
            assert result["bytes_written"] == 11
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_write_outside_project(self):
        result = write_file("/etc/passwd", "hack")
        assert result["status"] == "error"


class TestListFiles:
    def test_list_root(self):
        result = list_files(".")
        assert result["status"] == "success"
        assert result["count"] > 0

    def test_list_nonexistent(self):
        result = list_files("/no-existe-12345")
        assert result["status"] == "error"


class TestSearchSemantic:
    def test_search_semantic_fails_gracefully(self):
        result = search_semantic("test", limit=1)
        assert "status" in result


class TestRagStore:
    def test_rag_store_fails_gracefully(self):
        result = rag_store("test text", source="test")
        assert "status" in result


class TestSearchCode:
    def test_search_existing_pattern(self):
        result = search_code("def execute_command", path="src/core", include="*.py")
        assert result["status"] == "success"

    def test_search_empty_pattern(self):
        result = search_code("__no_way_this_exists__xyz123", path="src/core")
        assert result["status"] == "success"
