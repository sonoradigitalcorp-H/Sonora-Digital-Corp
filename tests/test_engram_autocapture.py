"""Tests para Engram Auto-Capture — Bash commands, env snapshots, git status, process snapshots [FR-01–FR-04]"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.engram_autocapture import (
    capture_env_snapshot,
    capture_git_snapshot,
    capture_process_snapshot,
    classify_command,
    classify_type_by_keywords,
    format_version,
    rate_limiter,
    sanitize_secrets,
    should_capture,
)


class TestShouldCapture:
    def test_captures_git_commit(self):
        assert should_capture("git commit -m 'fix'") is True

    def test_captures_npm_build(self):
        assert should_capture("npm run build") is True

    def test_captures_docker(self):
        assert should_capture("docker compose up -d") is True

    def test_captures_python_script(self):
        assert should_capture("python3 scripts/deploy.py") is True

    def test_skips_ls(self):
        assert should_capture("ls -la") is False

    def test_skips_cat(self):
        assert should_capture("cat README.md") is False

    def test_skips_grep(self):
        assert should_capture("grep 'TODO' *.py") is False

    def test_skips_pwd(self):
        assert should_capture("pwd") is False

    def test_skips_cd(self):
        assert should_capture("cd /tmp") is False

    def test_skips_echo(self):
        assert should_capture("echo hello") is False


class TestSanitizeSecrets:
    def test_filters_api_key(self):
        result = sanitize_secrets("export API_KEY=sk-12345")
        assert "sk-12345" not in result
        assert "[FILTERED]" in result

    def test_filters_multiple_secrets(self):
        result = sanitize_secrets("TOKEN=abc PASS=123")
        assert "[FILTERED]" in result

    def test_keeps_clean_text(self):
        text = "git commit -m 'fix bug'"
        assert sanitize_secrets(text) == text


class TestClassifyCommand:
    def test_git_is_code_change(self):
        assert classify_command("git add .") == "code_change"

    def test_npm_is_build(self):
        assert classify_command("npm run build") == "build"

    def test_docker_is_deploy(self):
        assert classify_command("docker compose up") == "deploy"

    def test_ssh_is_remote(self):
        assert classify_command("ssh ubuntu@vps") == "remote"

    def test_default_is_other(self):
        assert classify_command("terraform plan") == "other"


class TestCaptureEnvSnapshot:
    def test_captures_relevant_vars(self, monkeypatch):
        monkeypatch.setenv("SDC_PROJECT", "test")
        monkeypatch.setenv("NEO4J_URI", "bolt://localhost")
        monkeypatch.setenv("HOME", "/home/user")
        snapshot = capture_env_snapshot()
        assert "SDC_PROJECT" in snapshot
        assert "NEO4J_URI" in snapshot
        assert "HOME" not in snapshot


class TestCaptureGitSnapshot:
    def test_returns_dict_with_keys(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        result = capture_git_snapshot()
        assert "status" in result
        assert "commits" in result


class TestCaptureProcessSnapshot:
    def test_filters_relevant_processes(self):
        processes = capture_process_snapshot()
        assert isinstance(processes, list)


class TestRateLimiter:
    def test_allows_within_limit(self):
        rl = rate_limiter(max_per_minute=30)
        for _ in range(30):
            assert rl.allow("test-session") is True

    def test_blocks_over_limit(self):
        rl = rate_limiter(max_per_minute=5)
        for _ in range(5):
            rl.allow("test-session")
        assert rl.allow("test-session") is False

    def test_resets_after_minute(self):
        rl = rate_limiter(max_per_minute=1, window_seconds=0)
        rl.allow("test-session")
        assert rl.allow("test-session") is True


class TestFormatVersion:
    def test_v0_0_0(self):
        assert format_version(0) == "v0.0.0"

    def test_v0_0_1(self):
        assert format_version(1) == "v0.0.1"

    def test_v0_1_0(self):
        assert format_version(10) == "v0.1.0"

    def test_v1_0_0(self):
        assert format_version(100) == "v1.0.0"

    def test_v2_4_7(self):
        assert format_version(247) == "v2.4.7"


class TestClassifyTypeByKeywords:
    def test_bugfix(self):
        assert classify_type_by_keywords("fix error in parser") == "bugfix"

    def test_decision(self):
        assert classify_type_by_keywords("decidi usar FastAPI") == "decision"

    def test_config(self):
        assert classify_type_by_keywords("config yaml file") == "config"

    def test_pattern(self):
        assert classify_type_by_keywords("patron repository pattern") == "pattern"

    def test_learning(self):
        assert classify_type_by_keywords("aprendi que Whisper") == "learning"

    def test_architecture(self):
        assert classify_type_by_keywords("arquitectura microservicios") == "architecture"

    def test_default_discovery(self):
        assert classify_type_by_keywords("anything else here") == "discovery"
