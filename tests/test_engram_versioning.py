"""Tests para Versionado Semántico de Observaciones Engram [FR-05]"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.engram_autocapture import format_version


class TestVersionFormat:
    def test_zero(self):
        assert format_version(0) == "v0.0.0"

    def test_one(self):
        assert format_version(1) == "v0.0.1"

    def test_ten(self):
        assert format_version(10) == "v0.1.0"

    def test_one_hundred(self):
        assert format_version(100) == "v1.0.0"

    def test_two_forty_seven(self):
        assert format_version(247) == "v2.4.7"

    def test_999(self):
        assert format_version(999) == "v9.9.9"

    def test_1000(self):
        assert format_version(1000) == "v10.0.0"


class TestVersionSequence:
    def test_multiple_observations_same_topic(self):
        from scripts.engram_autocapture import EngramVersionTracker
        tracker = EngramVersionTracker()
        v1 = tracker.next_version("architecture/auth-model")
        v2 = tracker.next_version("architecture/auth-model")
        assert v1 == "v0.0.1"
        assert v2 == "v0.0.2"

    def test_different_topics_independent(self):
        from scripts.engram_autocapture import EngramVersionTracker
        tracker = EngramVersionTracker()
        v1 = tracker.next_version("architecture/auth-model")
        v2 = tracker.next_version("git/20260718")
        assert v1 == "v0.0.1"
        assert v2 == "v0.0.1"

    def test_sequence_metadata(self):
        from scripts.engram_autocapture import EngramVersionTracker
        tracker = EngramVersionTracker()
        meta = tracker.next_version_meta("architecture/auth-model")
        assert meta["version"] == "v0.0.1"
        assert meta["sequence"] == 1
        assert meta["topic_key"] == "architecture/auth-model"
        assert "revision_count" in meta
