"""
Tests para src/core/verify.py — SDD structure verification.
"""
import sys, os
from pathlib import Path
from unittest.mock import patch

import pytest
from src.core.verify import Verifier, ConstraintViolation, main


class TestVerifierStructure:

    def test_valid_spec_structure(self, tmp_path):
        spec_dir = tmp_path / "001-test-spec"
        spec_dir.mkdir()
        for f in ["spec.md", "plan.md", "tasks.md", "checklist.md", "data-model.md"]:
            (spec_dir / f).write_text("content")
        contracts = spec_dir / "contracts"
        contracts.mkdir()
        (contracts / "README.md").write_text("contracts readme")
        (spec_dir / "checklist.md").write_text("- [ ] item 1\n- [ ] item 2\n- [ ] item 3")

        v = Verifier()
        v.verify_structure(str(spec_dir))

    def test_missing_spec_raises(self, tmp_path):
        spec_dir = tmp_path / "bad-spec"
        spec_dir.mkdir()
        v = Verifier()
        with pytest.raises(ConstraintViolation, match="Missing required file"):
            v.verify_structure(str(spec_dir))

    def test_spec_000_exception(self, tmp_path):
        spec_dir = tmp_path / "000-constitucion"
        spec_dir.mkdir()
        for f in ["constitution.md", "plan.md", "tasks.md", "checklist.md", "data-model.md"]:
            (spec_dir / f).write_text("content")
        contracts = spec_dir / "contracts"
        contracts.mkdir()
        (contracts / "README.md").write_text("readme")
        (spec_dir / "checklist.md").write_text("- [ ] item 1\n- [ ] item 2\n- [ ] item 3")

        v = Verifier()
        v.verify_structure(str(spec_dir))

    def test_checklist_too_short_raises(self, tmp_path):
        spec_dir = tmp_path / "bad-checklist"
        spec_dir.mkdir()
        for f in ["spec.md", "plan.md", "tasks.md", "checklist.md", "data-model.md"]:
            (spec_dir / f).write_text("content")
        contracts = spec_dir / "contracts"
        contracts.mkdir()
        (contracts / "README.md").write_text("readme")
        (spec_dir / "checklist.md").write_text("- [ ] only one item")

        v = Verifier()
        with pytest.raises(ConstraintViolation, match="Checklist incomplete"):
            v.verify_structure(str(spec_dir))


class TestTDDCompliance:

    def test_sufficient_tests(self):
        v = Verifier()
        result = v.verify_tdd_compliance("some-spec")
        assert result is None

    def test_verify_skill_coverage(self):
        v = Verifier()
        result = v.verify_skill_coverage("001-test")
        assert result is None


class TestMain:

    def test_main_runs_with_specs(self, tmp_path):
        spec_root = tmp_path / "specs"
        spec_root.mkdir()
        s = spec_root / "001-test"
        s.mkdir()
        for f in ["spec.md", "plan.md", "tasks.md", "checklist.md", "data-model.md"]:
            (s / f).write_text("content")
        c = s / "contracts"
        c.mkdir()
        (c / "README.md").write_text("readme")
        (s / "checklist.md").write_text("- [ ] item 1\n- [ ] item 2\n- [ ] item 3")

        main(specs_dir=str(spec_root))
