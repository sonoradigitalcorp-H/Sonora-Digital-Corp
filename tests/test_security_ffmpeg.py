"""Tests para FFmpeg Sanitizer — FR-09: Filter injection prevention"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from common.security.ffmpeg_sanitizer import sanitize_filter_arg, sanitize_watermark, validate_file_path


class TestWatermarkSanitizer:
    def test_allows_normal_text(self):
        result = sanitize_watermark("Sonora Digital Corp")
        assert result.safe
        assert result.sanitized == "Sonora Digital Corp"

    def test_allows_special_chars(self):
        result = sanitize_watermark("Mi Empresa ©2026 - Todos los derechos")
        assert result.safe

    def test_removes_single_quotes(self):
        result = sanitize_watermark("Cliente's video")
        assert "'" not in result.sanitized

    def test_removes_colons(self):
        result = sanitize_watermark("Video: final")
        assert ":" not in result.sanitized

    def test_removes_backslashes(self):
        result = sanitize_watermark("Test \\ path")
        assert "\\" not in result.sanitized

    def test_replaces_brackets(self):
        result = sanitize_watermark("[Promo] Video")
        assert "[" not in result.sanitized
        assert "]" not in result.sanitized

    def test_truncates_long_text(self):
        long_text = "A" * 200
        result = sanitize_watermark(long_text)
        assert len(result.sanitized) <= 100

    def test_handles_empty_text(self):
        result = sanitize_watermark("")
        assert result.safe
        assert result.sanitized == ""

    def test_blocks_textfile_directive(self):
        result = sanitize_watermark("textfile=/etc/passwd")
        assert not result.safe
        assert "textfile" in result.reason

    def test_blocks_fontfile_directive(self):
        result = sanitize_watermark("fontfile=malicious.ttf")
        assert not result.safe
        assert "fontfile" in result.reason


class TestFilterArgSanitizer:
    def test_sanitizes_normal_arg(self):
        result = sanitize_filter_arg("simple argument")
        assert result == "simple argument"

    def test_removes_shell_chars(self):
        result = sanitize_filter_arg("arg; rm -rf /")
        assert ";" not in result

    def test_removes_backticks(self):
        result = sanitize_filter_arg("`cat /etc/passwd`")
        assert "`" not in result

    def test_removes_dollar(self):
        result = sanitize_filter_arg("$(cat /etc/passwd)")
        assert "$" not in result


class TestFilePathValidator:
    def test_allows_tmp_path(self):
        assert validate_file_path("/tmp/video.mp4")

    def test_allows_relative_path(self):
        assert validate_file_path("./output/video.mp4")

    def test_rejects_etc_path(self):
        assert not validate_file_path("/etc/passwd")

    def test_rejects_home_path(self):
        assert not validate_file_path("/home/user/.env")

    def test_rejects_path_traversal(self):
        assert not validate_file_path("/tmp/../../etc/passwd")

    def test_rejects_special_chars_in_path(self):
        assert not validate_file_path("/tmp/video;rm.mp4")

    def test_rejects_empty_path(self):
        assert not validate_file_path("")
