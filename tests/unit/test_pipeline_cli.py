"""Tests for process-pipeline.sh CLI."""

import subprocess
import os
import tempfile
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).parent.parent.parent
PIPELINE_SCRIPT = BASE_DIR / "scripts" / "process-pipeline.sh"


class TestPipelineCLI:
    def test_help_returns_usage(self):
        result = subprocess.run(["bash", str(PIPELINE_SCRIPT), "help"],
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        assert "Pipeline Commands:" in result.stdout

    def test_status_returns_info(self):
        result = subprocess.run(["bash", str(PIPELINE_SCRIPT), "status"],
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        assert "Pipeline Status" in result.stdout

    @pytest.fixture
    def temp_process_dir(self, tmp_path):
        """Create a temporary process/ structure for testing."""
        p = tmp_path / "process"
        (p / "templates").mkdir(parents=True)
        (p / "active").mkdir()
        (p / "completed").mkdir()
        # Copy templates
        for t in ["SPEC.md", "SCORE.md", "EVENT.md", "ADR.md", "LECCION.md", "GHERKIN.md"]:
            src = BASE_DIR / "process" / "templates" / t
            if src.exists():
                with open(src) as f:
                    content = f.read()
                (p / "templates" / t).write_text(content)
        return p

    @pytest.mark.skip(reason="CLI test creates artifacts in process/active/")
    def test_spec_new_creates_file(self, temp_process_dir):
        result = subprocess.run(
            ["bash", str(PIPELINE_SCRIPT), "spec-new", "Test Spec Creation"],
            capture_output=True, text=True, timeout=10,
            cwd=temp_process_dir.parent,
        )
        assert result.returncode == 0
        assert "Created" in result.stdout

    @pytest.mark.skip(reason="Requires enterprise-score.sh dependencies")
    def test_score_runs(self):
        result = subprocess.run(["bash", str(PIPELINE_SCRIPT), "score"],
                                capture_output=True, text=True, timeout=10)
        assert result.returncode == 0

    def test_event_emits_without_crashing(self):
        result = subprocess.run(
            ["bash", str(PIPELINE_SCRIPT), "event", "test_event", '{"test": true}'],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "Event logged" in result.stdout
